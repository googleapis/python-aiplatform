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

import functools
import importlib
import os
import pathlib
import py_compile
import pytest
import tempfile
import torch

import numpy as np
import pandas as pd
import unittest.mock as mock
from unittest.mock import patch
from unittest.mock import MagicMock

from google.cloud.aiplatform import initializer
from google.cloud import aiplatform
from google.cloud import storage

from google.cloud.aiplatform.experimental.vertex_model import base
from google.cloud.aiplatform.experimental.vertex_model.utils import source_utils
from google.cloud.aiplatform.experimental.vertex_model.serializers import (
    model as model_serializers,
)

from google.cloud.aiplatform_v1.services.model_service import (
    client as model_service_client,
)
from google.cloud.aiplatform_v1.types import Model as gca_Model


try:
    # Available in a colab environment.
    from google.colab import _message  # pylint: disable=g-import-not-at-top

    MOCK_NOTEBOOK = _message.blocking_request("get_ipynb", request="", timeout_sec=200)

except ImportError:
    _message = None
    MOCK_NOTEBOOK = None


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_ID = "1028944691210842416"
_TEST_DISPLAY_NAME = "test-display-name"

_TEST_BUCKET_NAME = "test-bucket"
_TEST_STAGING_BUCKET = "gs://test-staging-bucket"

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_default"

_TEST_MODEL_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_ID}"
)
_TEST_MODEL_RESOURCE_NAME = model_service_client.ModelServiceClient.model_path(
    _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
)


class TorchModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = torch.nn.Linear(2, 1)

    def forward(self, x):
        return self.linear(x)


@pytest.fixture
def mock_get_notebook():
    if _message is not None:
        with patch.object(_message, "blocking_request") as mock:
            mock.return_value = MOCK_NOTEBOOK
            yield mock
    else:
        yield None


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
def mock_model():
    mock_model = MagicMock(aiplatform.models.Model)
    mock_model.artifact_uri = "gs://fake-bucket/my_model.pth"
    mock_model._gca_resource = gca_Model(
        artifact_uri="gs://fake-bucket/my_model.pth", name=_TEST_MODEL_RESOURCE_NAME
    )
    yield mock_model


@pytest.fixture
def mock_deserialize_model():
    with patch.object(model_serializers, "_deserialize_remote_model") as mock:
        mock.return_value = TorchModel()
        yield mock


@pytest.fixture
def mock_serialize_model(mock_model):
    with patch.object(model_serializers, "_serialize_local_model") as mock:
        mock.return_value = mock_model
        yield mock


@pytest.fixture
def mock_run_custom_training_job(mock_custom_training_job, mock_model):
    with patch.object(mock_custom_training_job, "run") as mock:
        mock.return_value = mock_model
        yield mock


@pytest.fixture
def mock_model_upload(mock_model):
    with patch.object(aiplatform.models.Model, "upload") as mock:
        mock.return_value = mock_model
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


class TestCloudVertexModelClass:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def test_create_vertex_model_cloud_class(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        my_model = LinearRegression(2, 1)
        my_model.remote = True

        assert my_model is not None

    def test_custom_job_call_from_vertex_model(
        self,
        mock_get_custom_training_job,
        mock_run_custom_training_job,
        mock_client_bucket,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        my_model = LinearRegression(2, 1)
        my_model.remote = True

        df = pd.DataFrame(
            np.random.random(size=(100, 3)), columns=["feat_1", "feat_2", "target"]
        )
        my_model.fit(df, "target", 1, 0.1)

        call_args = mock_get_custom_training_job.call_args

        expected = {
            "display_name": "my_training_job",
            "requirements": [
                "pandas>=1.3",
                "torch>=1.7",
                "google-cloud-aiplatform @ git+https://github.com/googleapis/python-aiplatform@refs/pull/628/head#egg=google-cloud-aiplatform",
            ],
            "container_uri": "us-docker.pkg.dev/vertex-ai/training/scikit-learn-cpu.0-23:latest",
            "model_serving_container_image_uri": "gcr.io/google-appengine/python",
        }

        for key, value in expected.items():
            print(key)
            assert call_args[1][key] == value

        assert call_args[1]["script_path"].endswith("/training_script.py")
        assert sorted(list(call_args[1].keys())) == sorted(
            list(expected.keys())
            + ["script_path"]
            + ["model_serving_container_command"]
        )

        mock_get_custom_training_job.assert_called_once()
        assert len(call_args[0]) == 0

        mock_run_custom_training_job.assert_called_once_with(
            model_display_name="my_model", replica_count=1,
        )

    def test_remote_train_remote_predict(
        self,
        mock_get_custom_training_job,
        mock_run_custom_training_job,
        mock_model,
        mock_client_bucket,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        my_model = LinearRegression(2, 1)
        my_model.remote = True

        df = pd.DataFrame(
            np.random.random(size=(100, 3)), columns=["feat_1", "feat_2", "target"]
        )
        my_model.fit(df, "target", 1, 0.1)

        # Predict remotely
        my_model.remote = True
        data = pd.DataFrame(
            np.random.random(size=(100, 3)), columns=["feat_1", "feat_2", "target"]
        )

        feature_columns = list(data.columns)
        feature_columns.remove("target")
        torch_tensor = torch.tensor(data[feature_columns].values).type(
            torch.FloatTensor
        )

        my_model.predict(torch_tensor)

        # Check that endpoint is deployed
        mock_model.deploy.assert_called_once_with(machine_type="n1-standard-4")

    @pytest.mark.usefixtures("mock_deserialize_model")
    def test_remote_train_local_predict(
        self,
        mock_get_custom_training_job,
        mock_run_custom_training_job,
        mock_client_bucket,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        # Remote training
        my_model = LinearRegression(2, 1)
        my_model.remote = True

        df = pd.DataFrame(
            np.random.random(size=(100, 3)), columns=["feat_1", "feat_2", "target"]
        )
        my_model.fit(df, "target", 1, 0.1)
        mock_run_custom_training_job.assert_called_once()

        # Local prediction: check that the model is available
        my_model.remote = False
        data = pd.DataFrame(
            np.random.random(size=(100, 3)), columns=["feat_1", "feat_2", "target"]
        )

        feature_columns = list(data.columns)
        feature_columns.remove("target")
        torch_tensor = torch.tensor(data[feature_columns].values).type(
            torch.FloatTensor
        )

        my_model.predict(torch_tensor)

        assert mock_run_custom_training_job.return_value is not None

    @pytest.mark.usefixtures("mock_serialize_model")
    def test_local_train_remote_predict(
        self,
        mock_get_custom_training_job,
        mock_run_custom_training_job,
        mock_client_bucket,
        mock_model_upload,
        mock_model,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        # Train locally
        my_model = LinearRegression(2, 1)
        my_model.remote = False

        df = pd.DataFrame(
            np.random.random(size=(100, 3)), columns=["feat_1", "feat_2", "target"]
        )

        my_model.fit(df, "target", 1, 0.1)

        # Predict remotely
        my_model.remote = True
        data = pd.DataFrame(
            np.random.random(size=(100, 3)), columns=["feat_1", "feat_2", "target"]
        )

        feature_columns = list(data.columns)
        feature_columns.remove("target")
        torch_tensor = torch.tensor(data[feature_columns].values).type(
            torch.FloatTensor
        )

        os.environ["AIP_STORAGE_URI"] = _TEST_STAGING_BUCKET

        my_model.predict(torch_tensor)

        # Make assertions
        mock_model_upload.assert_called_once()
        mock_model.deploy.assert_called_once_with(machine_type="n1-standard-4")

    def test_jupyter_source_retrieval(self, mock_get_notebook):
        if _message is not None and MOCK_NOTEBOOK is not None:
            output_file = source_utils.jupyter_notebook_to_file()

            with open(output_file, "w"):
                module_ok = True

                try:
                    py_compile.compile(output_file, doraise=True)
                except py_compile.PyCompileError as e:
                    print(e.exc_value)
                    module_ok = False

                assert module_ok

    def test_source_script_compiles(
        self, mock_client_bucket,
    ):
        my_model = LinearRegression(input_size=10, output_size=10)
        cls_name = my_model.__class__.__name__

        training_source = source_utils._make_class_source(my_model)

        with tempfile.TemporaryDirectory() as tmpdirname:
            script_path = pathlib.Path(tmpdirname) / "training_script.py"

            source = source_utils._make_source(
                cls_source=training_source,
                cls_name=cls_name,
                instance_method=None,
                pass_through_params=None,
                param_name_to_serialized_info=None,
                obj=my_model,
            )

            with open(script_path, "w") as f:
                f.write(source)
                print(source)

                module_ok = True

                try:
                    py_compile.compile(script_path, doraise=True)
                except py_compile.PyCompileError as e:
                    print(e.exc_value)
                    module_ok = False

                assert module_ok


class TestLocalVertexModelClass:
    def test_create_local_vertex_model_class(self):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_STAGING_BUCKET)

        model = LinearRegression(2, 1)
        assert model is not None
