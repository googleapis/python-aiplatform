# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
import functools
import pytest
import tempfile
import torch

from torch.utils.data import DataLoader
from torch.utils.data import Dataset

import numpy as np
import pandas as pd
import unittest.mock as mock
from unittest.mock import patch

from google.cloud import aiplatform
from google.cloud import storage

from google.cloud.aiplatform.experimental.vertex_model import base
from google.cloud.aiplatform.experimental.vertex_model.serializers import pytorch
from google.cloud.aiplatform.experimental.vertex_model.serializers import model
from google.cloud.aiplatform.experimental.vertex_model.serializers import pandas


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

_TEST_BUCKET_NAME = "test-bucket"
_TEST_STAGING_BUCKET = "gs://test-staging-bucket"

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_default"


@pytest.fixture
def mock_pd_read_csv():
    with patch.object(pd, "read_csv") as mock:
        mock.return_value = pd.DataFrame(
            np.random.random(size=(100, 3)), columns=["feat_1", "feat_2", "target"]
        )
        yield mock


@pytest.fixture
def mock_torch_load():
    with patch.object(torch, "load") as mock:
        mock.return_value = DataLoader(NumbersDataset(), batch_size=64)
        yield mock


@pytest.fixture
def mock_torch_jit_load():
    with patch.object(torch.jit, "load") as mock:
        mock.return_value = LinearRegression(2, 1)
        yield mock


@pytest.fixture
def mock_client_bucket():
    with patch.object(storage.Client, "bucket") as mock_client_bucket:

        def blob_side_effect(name, mock_blob, bucket):
            mock_blob.name = name
            mock_blob.bucket = bucket
            return mock_blob

        MockBucket = mock.Mock(autospec=storage.Bucket)
        MockBucket.name = _TEST_BUCKET_NAME
        MockBlob = mock.Mock(autospec=storage.Blob)
        MockBucket.blob.side_effect = functools.partial(
            blob_side_effect, mock_blob=MockBlob, bucket=MockBucket
        )
        mock_client_bucket.return_value = MockBucket

        yield mock_client_bucket, MockBlob


class LinearRegression(base.VertexModel, torch.nn.Module):
    def __init__(self, input_size: int, output_size: int):
        base.VertexModel.__init__(self, input_size=input_size, output_size=output_size)
        torch.nn.Module.__init__(self)
        self.linear = torch.nn.Linear(input_size, output_size)

    def forward(self, x):
        return self.linear(x)

    def train_loop(self, dataloader, loss_fn, optimizer):
        for batch, (X, y) in enumerate(dataloader):
            pred = self.predict(X.float())
            loss = loss_fn(pred.float(), y.float())

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    def fit(
        self, data: pd.DataFrame, target_column: str, epochs: int, learning_rate: float
    ):
        feature_columns = list(data.columns)
        feature_columns.remove(target_column)

        features = torch.tensor(data[feature_columns].values)
        target = torch.tensor(data[target_column].values)

        dataloader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(features, target),
            batch_size=10,
            shuffle=True,
        )

        loss_fn = torch.nn.MSELoss()
        optimizer = torch.optim.SGD(self.parameters(), lr=learning_rate)

        for t in range(epochs):
            self.train_loop(dataloader, loss_fn, optimizer)

    def predict(self, data):
        return self.forward(data)

    # Implementation of predict_payload_to_predict_input(), which converts a predict_payload object to predict() inputs
    def predict_payload_to_predict_input(self, instances):
        feature_columns = ["feat_1", "feat_2"]
        data = pd.DataFrame(instances, columns=feature_columns)
        torch_tensor = torch.tensor(data[feature_columns].values).type(
            torch.FloatTensor
        )
        return torch_tensor

    # Implementation of predict_input_to_predict_payload(), which converts predict() inputs to a predict_payload object
    def predict_input_to_predict_payload(self, parameter):
        return parameter.tolist()

    # Implementation of predict_output_to_predict_payload(), which converts the predict() output to a predict_payload object
    def predict_output_to_predict_payload(self, output):
        return output.tolist()

    # Implementation of predict_payload_to_predict_output, which takes a predict_payload object containing predictions and
    # converts it to the type of output expected by the user-written class.
    def predict_payload_to_predict_output(self, predictions):
        data = pd.DataFrame(predictions)
        torch_tensor = torch.tensor(data.values).type(torch.FloatTensor)
        return torch_tensor


class NumbersDataset(Dataset):
    def __init__(self):
        self.samples = list(range(1, 1001))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


class TestModelSerialization:
    def test_local_serialization_works(self, mock_client_bucket):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        # Create model object
        my_model = LinearRegression(2, 1)
        my_model.remote = True

        # Serialize and deserialize locally
        with tempfile.TemporaryDirectory() as tmpdirname:
            model_uri = model._serialize_local_model(tmpdirname, my_model, "test")
            deserialized_model = model._deserialize_remote_model(model_uri)

            for key_item_1, key_item_2 in zip(
                my_model.state_dict().items(), deserialized_model.state_dict().items()
            ):
                assert torch.equal(key_item_1[1], key_item_2[1])

    def test_remote_serialization_works(self, mock_client_bucket, mock_torch_jit_load):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        # Create model object
        my_model = LinearRegression(2, 1)

        staging_bucket = aiplatform.initializer.global_config.staging_bucket
        if staging_bucket is None:
            raise RuntimeError(
                "Staging bucket must be set to run training in cloud mode: `aiplatform.init(staging_bucket='gs://my/staging/bucket')`"
            )

        timestamp = datetime.datetime.now().isoformat(sep="-", timespec="milliseconds")
        vertex_model_root_folder = "/".join(
            [staging_bucket, f"vertex_model_run_{timestamp}"]
        )
        vertex_model_model_folder = "/".join(
            [vertex_model_root_folder, "serialized_model"]
        )

        model_uri = model._serialize_local_model(
            vertex_model_model_folder, my_model, "local"
        )

        assert len(model_uri) > 0

        deserialized_model = model._deserialize_remote_model(model_uri)

        assert issubclass(type(deserialized_model), torch.nn.Module)


class TestDataLoaderSerialization:
    def test_local_serialization_works(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            dataset = NumbersDataset()
            root = getattr(dataset, "root", None)
            print(root)

            dataloader = DataLoader(dataset, batch_size=64)

            timestamp = datetime.datetime.now().isoformat(
                sep="-", timespec="milliseconds"
            )
            dataloader_root_folder = "/".join([tmpdirname, f"dataloader_{timestamp}"])

            # Locally serialize and deserialize
            obj_path = pytorch._serialize_dataloader(
                dataloader_root_folder, dataloader, "local"
            )
            deserialized_dataloader = pytorch._deserialize_dataloader(obj_path)

            original_tensor = next(iter(dataloader))
            new_tensor = next(iter(deserialized_dataloader))

            assert torch.all(original_tensor.eq(new_tensor))

    def test_remote_serialization_works(self, mock_client_bucket, mock_torch_load):
        dataset = NumbersDataset()
        dataloader = DataLoader(dataset, batch_size=64)

        timestamp = datetime.datetime.now().isoformat(sep="-", timespec="milliseconds")
        dataloader_root_folder = "/".join(
            [_TEST_STAGING_BUCKET, f"dataloader_{timestamp}"]
        )

        obj_path = pytorch._serialize_dataloader(
            dataloader_root_folder, dataloader, "local"
        )

        remote_obj_path = pytorch._serialize_remote_dataloader(
            dataloader_root_folder, dataloader, "remote"
        )

        assert len(obj_path) > 0
        assert len(remote_obj_path) > 0

        deserialized_dataloader = pytorch._deserialize_dataloader(obj_path)

        assert type(deserialized_dataloader) is DataLoader


class TestDataFrameSerialization:
    def test_local_serialization_works(self):
        df = pd.DataFrame(
            np.random.random(size=(100, 3)), columns=["feat_1", "feat_2", "target"]
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            df_path = pandas._serialize_dataframe(tmpdirname, df, "test")
            new_df = pandas._deserialize_dataframe(df_path)

            pd.testing.assert_frame_equal(df, new_df, check_dtype=True)

    def test_remote_serialization_works(self, mock_client_bucket, mock_pd_read_csv):
        df = pd.DataFrame(
            np.random.random(size=(100, 3)), columns=["feat_1", "feat_2", "target"]
        )

        df_path = pandas._serialize_dataframe(_TEST_STAGING_BUCKET, df, "test")

        assert len(df_path) > 0

        deserialized_dataframe = pandas._deserialize_dataframe(df_path)

        assert type(deserialized_dataframe) is pd.DataFrame
