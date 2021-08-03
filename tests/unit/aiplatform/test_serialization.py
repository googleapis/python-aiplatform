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
from unittest.mock import MagicMock

from google.cloud import aiplatform
from google.cloud import storage

from google.cloud.aiplatform.experimental.vertex_model import base
from google.cloud.aiplatform.experimental.vertex_model.serializers import dataloaders
from google.cloud.aiplatform.experimental.vertex_model.serializers import model


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

_TEST_BUCKET_NAME = "test-bucket"
_TEST_STAGING_BUCKET = "gs://test-staging-bucket"

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_default"


@pytest.fixture
def mock_custom_training_job():
    mock = MagicMock(aiplatform.training_jobs.CustomTrainingJob)
    yield mock


@pytest.fixture
def mock_get_custom_training_job(mock_custom_training_job):
    with patch.object(aiplatform, "CustomTrainingJob") as mock:
        mock.return_value = mock_custom_training_job
        yield mock


@pytest.fixture
def mock_run_custom_training_job(mock_custom_training_job):
    with patch.object(mock_custom_training_job, "run") as mock:
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
        my_model.training_mode = "cloud"

        # Serialize and deserialize locally
        with tempfile.TemporaryDirectory() as tmpdirname:
            timestamp = datetime.datetime.now().isoformat(
                sep="-", timespec="milliseconds"
            )
            model_root_folder = "/".join([tmpdirname, f"model_{timestamp}"])

            model_uri = model._serialize_local_model(model_root_folder, my_model, "test")
            deserialized_model = model._deserialize_remote_model(model_uri)

            assert my_model.state_dict() == deserialized_model.state_dict()


class TestDataLoaderSerialization:
    def test_local_serialization_works(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Create DataLoader from random data
            random_df = pd.DataFrame(
                np.random.random(size=(100, 3)), columns=["feat_1", "feat_2", "target"]
            )

            source_path = tmpdirname + "/my_dataset.csv"
            random_df.to_csv(source_path)

            dataset = NumbersDataset()
            dataloader = DataLoader(dataset, batch_size=64)

            timestamp = datetime.datetime.now().isoformat(
                sep="-", timespec="milliseconds"
            )
            dataloader_root_folder = "/".join([tmpdirname, f"dataloader_{timestamp}"])

            # Locally serialize and deserialize
            obj_path, data_path = dataloaders._serialize_dataloader(
                dataloader_root_folder, dataloader, "local"
            )
            deserialized_dataloader = dataloaders._deserialize_dataloader(obj_path)

            original_tensor = next(iter(dataloader))
            new_tensor = next(iter(deserialized_dataloader))
            assert torch.all(original_tensor.eq(new_tensor))
            
