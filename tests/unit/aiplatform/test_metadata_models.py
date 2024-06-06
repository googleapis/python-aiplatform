# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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
import os
import pickle
from importlib import reload
from unittest import mock
from unittest.mock import patch
import uuid

from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata import metadata
from google.cloud.aiplatform.metadata import _models
from google.cloud.aiplatform.models import Model
from google.cloud.aiplatform_v1 import Artifact as GapicArtifact
from google.cloud.aiplatform_v1 import MetadataStore as GapicMetadataStore
from google.cloud.aiplatform_v1 import MetadataServiceClient
import numpy as np
import pytest
import sklearn
from sklearn.datasets import make_classification
from sklearn.linear_model import LinearRegression
import tensorflow as tf
import xgboost as xgb


# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_BUCKET_NAME = "gs://test-bucket"
_TEST_PARENT = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)
_TEST_CREDENTIALS = mock.Mock(
    spec=auth_credentials.AnonymousCredentials(),
    universe_domain="googleapis.com",
)


# artifact
_TEST_ARTIFACT_ID = "test-model-id"
_TEST_URI = "gs://test-uri"
_TEST_DISPLAY_NAME = "test-model-display-name"

_TEST_ARTIFACT_ID = "test-model-id"
_TEST_ARTIFACT_NAME = f"{_TEST_PARENT}/artifacts/{_TEST_ARTIFACT_ID}"

_TEST_TIMESTAMP = "2022-11-30-00-00-00"
_TEST_DATETIME = datetime.datetime.strptime(_TEST_TIMESTAMP, "%Y-%m-%d-%H-%M-%S")

_TEST_UUID = uuid.UUID("fa2db23f-1b13-412d-beea-94602448e4ce")

_TEST_INPUT_EXAMPLE = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])

_TEST_MODEL_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_ARTIFACT_ID}"
)


@pytest.fixture
def mock_datetime_now(monkeypatch):
    class DateTime(datetime.datetime):
        @classmethod
        def now(cls):
            return _TEST_DATETIME

    monkeypatch.setattr(datetime, "datetime", DateTime)


@pytest.fixture
def mock_uuid():
    with patch.object(uuid, "uuid4", return_value=_TEST_UUID) as mock_uuid:
        yield mock_uuid


@pytest.fixture
def mock_keras_save_model():
    with patch.object(tf.keras.models.Sequential, "save") as mock_keras_save_model:
        yield mock_keras_save_model


@pytest.fixture
def mock_tf_save_model():
    with patch("tensorflow.saved_model.save") as mock_tf_save_model:
        yield mock_tf_save_model


@pytest.fixture
def mock_storage_blob_upload_from_filename():
    with patch(
        "google.cloud.storage.Blob.upload_from_filename"
    ) as mock_blob_upload_from_filename, patch(
        "google.cloud.storage.Bucket.exists", return_value=True
    ):
        yield mock_blob_upload_from_filename


@pytest.fixture
def mock_storage_blob_download_sklearn_model_file():
    def create_model_file(filename):
        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.dot(train_x, np.array([1, 2])) + 3
        model = LinearRegression()
        model.fit(train_x, train_y)
        with open(filename, "wb") as model_file:
            pickle.dump(model, model_file)

    with patch(
        "google.cloud.storage.Blob.download_to_filename", wraps=create_model_file
    ) as mock_blob_download_to_filename, patch(
        "google.cloud.storage.Bucket.exists", return_value=True
    ):
        yield mock_blob_download_to_filename


@pytest.fixture
def mock_storage_blob_download_xgboost_booster_file():
    def create_model_file(filename):
        x, y = make_classification()
        dtrain = xgb.DMatrix(data=x, label=y)
        booster = xgb.train(
            params={"num_parallel_tree": 4, "subsample": 0.5, "num_class": 2},
            dtrain=dtrain,
        )
        booster.save_model(filename)

    with patch(
        "google.cloud.storage.Blob.download_to_filename", wraps=create_model_file
    ) as mock_blob_download_to_filename, patch(
        "google.cloud.storage.Bucket.exists", return_value=True
    ):
        yield mock_blob_download_to_filename


@pytest.fixture
def mock_storage_blob_download_xgboost_xgbmodel_file():
    def create_model_file(filename):
        x, y = make_classification()
        model = xgb.XGBClassifier()
        model.fit(x, y)
        model.save_model(filename)

    with patch(
        "google.cloud.storage.Blob.download_to_filename", wraps=create_model_file
    ) as mock_blob_download_to_filename, patch(
        "google.cloud.storage.Bucket.exists", return_value=True
    ):
        yield mock_blob_download_to_filename


@pytest.fixture
def mock_storage_blob_download_input_example():
    def create_input_example_file(filename):
        filepath, _ = os.path.split(filename)
        _models._save_input_example(_TEST_INPUT_EXAMPLE, filepath)

    with patch(
        "google.cloud.storage.Blob.download_to_filename",
        wraps=create_input_example_file,
    ) as mock_blob_download_to_filename, patch(
        "google.cloud.storage.Bucket.exists", return_value=True
    ):
        yield mock_blob_download_to_filename


@pytest.fixture
def mock_load_tensorflow_keras_model():
    with patch("tensorflow.keras.models.load_model") as load_tensorflow_keras_model:
        yield load_tensorflow_keras_model


@pytest.fixture
def mock_load_tensorflow_module_model():
    with patch("tensorflow.saved_model.load") as load_tensorflow_keras_model:
        yield load_tensorflow_keras_model


_TEST_SKLEARN_MODEL_ARTIFACT = GapicArtifact(
    name=_TEST_ARTIFACT_NAME,
    uri=_TEST_URI,
    display_name=_TEST_DISPLAY_NAME,
    schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
    schema_version=constants._DEFAULT_SCHEMA_VERSION,
    state=GapicArtifact.State.LIVE,
    metadata={
        "frameworkName": "sklearn",
        "frameworkVersion": "1.0",
        "modelFile": "model.pkl",
        "modelClass": "sklearn.linear_model._base.LinearRegression",
    },
)


@pytest.fixture
def create_experiment_model_artifact_mock():
    with patch.object(MetadataServiceClient, "create_artifact") as create_artifact_mock:
        create_artifact_mock.return_value = _TEST_SKLEARN_MODEL_ARTIFACT
        yield create_artifact_mock


@pytest.fixture
def get_sklearn_model_artifact_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.return_value = _TEST_SKLEARN_MODEL_ARTIFACT
        yield get_artifact_mock


_TEST_XGBOOST_BOOSTER_ARTIFACT = GapicArtifact(
    name=_TEST_ARTIFACT_NAME,
    uri=_TEST_URI,
    display_name=_TEST_DISPLAY_NAME,
    schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
    schema_version=constants._DEFAULT_SCHEMA_VERSION,
    state=GapicArtifact.State.LIVE,
    metadata={
        "frameworkName": "xgboost",
        "frameworkVersion": "1.5",
        "modelFile": "model.bst",
        "modelClass": "xgboost.core.Booster",
    },
)


@pytest.fixture
def get_xgboost_booster_artifact_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.return_value = _TEST_XGBOOST_BOOSTER_ARTIFACT
        yield get_artifact_mock


_TEST_XGBOOST_XGBMODEL_ARTIFACT = GapicArtifact(
    name=_TEST_ARTIFACT_NAME,
    uri=_TEST_URI,
    display_name=_TEST_DISPLAY_NAME,
    schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
    schema_version=constants._DEFAULT_SCHEMA_VERSION,
    state=GapicArtifact.State.LIVE,
    metadata={
        "frameworkName": "xgboost",
        "frameworkVersion": "1.5",
        "modelFile": "model.bst",
        "modelClass": "xgboost.sklearn.XGBClassifier",
    },
)


@pytest.fixture
def get_xgboost_xgbmodel_artifact_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.return_value = _TEST_XGBOOST_XGBMODEL_ARTIFACT
        yield get_artifact_mock


_TEST_TENSORFLOW_KERAS_ARTIFACT = GapicArtifact(
    name=_TEST_ARTIFACT_NAME,
    uri=_TEST_URI,
    display_name=_TEST_DISPLAY_NAME,
    schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
    schema_version=constants._DEFAULT_SCHEMA_VERSION,
    state=GapicArtifact.State.LIVE,
    metadata={
        "frameworkName": "tensorflow",
        "frameworkVersion": "2.8",
        "modelFile": "saved_model",
        "modelClass": "tensorflow.keras.Model",
    },
)


@pytest.fixture
def get_tensorflow_keras_artifact_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.return_value = _TEST_TENSORFLOW_KERAS_ARTIFACT
        yield get_artifact_mock


_TEST_TENSORFLOW_MODULE_ARTIFACT = GapicArtifact(
    name=_TEST_ARTIFACT_NAME,
    uri=_TEST_URI,
    display_name=_TEST_DISPLAY_NAME,
    schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
    schema_version=constants._DEFAULT_SCHEMA_VERSION,
    state=GapicArtifact.State.LIVE,
    metadata={
        "frameworkName": "tensorflow",
        "frameworkVersion": "2.8",
        "modelFile": "saved_model",
        "modelClass": "tensorflow.Module",
    },
)


@pytest.fixture
def get_tensorflow_module_artifact_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.return_value = _TEST_TENSORFLOW_MODULE_ARTIFACT
        yield get_artifact_mock


@pytest.fixture
def model_upload_mock():
    with patch.object(Model, "upload") as upload_model_mock:
        yield upload_model_mock


@pytest.fixture
def get_metadata_store_mock():
    with patch.object(
        MetadataServiceClient, "get_metadata_store"
    ) as get_metadata_store_mock:
        get_metadata_store_mock.return_value = GapicMetadataStore(name=_TEST_PARENT)
        yield get_metadata_store_mock


class TestModels:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures(
        "mock_datetime_now",
        "mock_uuid",
        "get_metadata_store_mock",
    )
    def test_save_model_sklearn(
        self,
        mock_storage_blob_upload_from_filename,
        create_experiment_model_artifact_mock,
        get_sklearn_model_artifact_mock,
    ):
        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.dot(train_x, np.array([1, 2])) + 3
        model = LinearRegression()
        model.fit(train_x, train_y)

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        aiplatform.save_model(model, _TEST_ARTIFACT_ID)

        # Verify that the model file is correctly uploaded to gcs
        upload_file_path = mock_storage_blob_upload_from_filename.call_args[1][
            "filename"
        ]
        assert upload_file_path.endswith("model.pkl")

        # Verify the model artifact is created correctly
        expected_artifact = GapicArtifact(
            uri=f"{_TEST_BUCKET_NAME}/{_TEST_TIMESTAMP}-{_TEST_UUID.hex[:5]}-sklearn-model",
            schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
            schema_version=constants._DEFAULT_SCHEMA_VERSION,
            metadata={
                "frameworkName": "sklearn",
                "frameworkVersion": sklearn.__version__,
                "modelFile": "model.pkl",
                "modelClass": "sklearn.linear_model._base.LinearRegression",
            },
            state=GapicArtifact.State.LIVE,
        )
        create_experiment_model_artifact_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            artifact=expected_artifact,
            artifact_id=_TEST_ARTIFACT_ID,
        )

        get_sklearn_model_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures(
        "mock_storage_blob_upload_from_filename",
        "get_sklearn_model_artifact_mock",
        "get_metadata_store_mock",
    )
    def test_save_model_with_all_args(
        self,
        create_experiment_model_artifact_mock,
    ):
        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.dot(train_x, np.array([1, 2])) + 3
        model = LinearRegression()
        model.fit(train_x, train_y)

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        aiplatform.save_model(
            model=model,
            artifact_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            input_example=_TEST_INPUT_EXAMPLE,
        )

        # Verify the model artifact is created correctly
        expected_artifact = GapicArtifact(
            display_name=_TEST_DISPLAY_NAME,
            uri=_TEST_URI,
            schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
            schema_version=constants._DEFAULT_SCHEMA_VERSION,
            metadata={
                "frameworkName": "sklearn",
                "frameworkVersion": sklearn.__version__,
                "modelFile": "model.pkl",
                "modelClass": "sklearn.linear_model._base.LinearRegression",
                "predictSchemata": {"instanceSchemaUri": f"{_TEST_URI}/instance.yaml"},
            },
            state=GapicArtifact.State.LIVE,
        )
        create_experiment_model_artifact_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            artifact=expected_artifact,
            artifact_id=_TEST_ARTIFACT_ID,
        )

    @pytest.mark.usefixtures(
        "mock_datetime_now",
        "mock_uuid",
        "get_metadata_store_mock",
    )
    def test_save_model_xgboost_booster(
        self,
        mock_storage_blob_upload_from_filename,
        create_experiment_model_artifact_mock,
        get_xgboost_booster_artifact_mock,
    ):
        # Fix the bug that xgb.__version__ in third_party returns a byte not string
        xgb.__version__ = "1.5.1"

        x, y = make_classification()
        dtrain = xgb.DMatrix(data=x, label=y)
        booster = xgb.train(
            params={"num_parallel_tree": 4, "subsample": 0.5, "num_class": 2},
            dtrain=dtrain,
        )

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        aiplatform.save_model(booster, _TEST_ARTIFACT_ID)

        # Verify that the model file is correctly uploaded to gcs
        upload_file_path = mock_storage_blob_upload_from_filename.call_args[1][
            "filename"
        ]
        assert upload_file_path.endswith("model.bst")

        # Verify the model artifact is created correctly
        expected_artifact = GapicArtifact(
            uri=f"{_TEST_BUCKET_NAME}/{_TEST_TIMESTAMP}-{_TEST_UUID.hex[:5]}-xgboost-model",
            schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
            schema_version=constants._DEFAULT_SCHEMA_VERSION,
            metadata={
                "frameworkName": "xgboost",
                "frameworkVersion": xgb.__version__,
                "modelFile": "model.bst",
                "modelClass": "xgboost.core.Booster",
            },
            state=GapicArtifact.State.LIVE,
        )
        create_experiment_model_artifact_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            artifact=expected_artifact,
            artifact_id=_TEST_ARTIFACT_ID,
        )

        get_xgboost_booster_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures(
        "mock_datetime_now",
        "mock_uuid",
        "get_metadata_store_mock",
    )
    def test_save_model_xgboost_xgbmodel(
        self,
        mock_storage_blob_upload_from_filename,
        create_experiment_model_artifact_mock,
        get_xgboost_xgbmodel_artifact_mock,
    ):
        # Fix the bug that xgb.__version__ in third_party returns a byte not string
        xgb.__version__ = "1.5.1"

        x, y = make_classification()
        xgb_model = xgb.XGBClassifier()
        xgb_model.fit(x, y)

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        aiplatform.save_model(xgb_model, _TEST_ARTIFACT_ID)

        # Verify that the model file is correctly uploaded to gcs
        upload_file_path = mock_storage_blob_upload_from_filename.call_args[1][
            "filename"
        ]
        assert upload_file_path.endswith("model.bst")

        # Verify the model artifact is created correctly
        expected_artifact = GapicArtifact(
            uri=f"{_TEST_BUCKET_NAME}/{_TEST_TIMESTAMP}-{_TEST_UUID.hex[:5]}-xgboost-model",
            schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
            schema_version=constants._DEFAULT_SCHEMA_VERSION,
            metadata={
                "frameworkName": "xgboost",
                "frameworkVersion": xgb.__version__,
                "modelFile": "model.bst",
                "modelClass": "xgboost.sklearn.XGBClassifier",
            },
            state=GapicArtifact.State.LIVE,
        )
        create_experiment_model_artifact_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            artifact=expected_artifact,
            artifact_id=_TEST_ARTIFACT_ID,
        )

        get_xgboost_xgbmodel_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures(
        "mock_datetime_now",
        "mock_uuid",
        "get_metadata_store_mock",
    )
    def test_save_model_tensorflow_keras(
        self,
        mock_keras_save_model,
        create_experiment_model_artifact_mock,
        get_tensorflow_keras_artifact_mock,
    ):
        x = np.random.random((100, 3))
        y = np.random.random((100, 1))
        model = tf.keras.Sequential(
            [tf.keras.layers.Dense(5, input_shape=(3,)), tf.keras.layers.Softmax()]
        )
        model.compile(optimizer="adam", loss="mean_squared_error")
        model.fit(x, y)

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        aiplatform.save_model(model, _TEST_ARTIFACT_ID)

        mock_keras_save_model.assert_called_once_with(
            f"{_TEST_BUCKET_NAME}/{_TEST_TIMESTAMP}-{_TEST_UUID.hex[:5]}"
            + "-tensorflow-model/saved_model",
        )

        # Verify the model artifact is created correctly
        expected_artifact = GapicArtifact(
            uri=f"{_TEST_BUCKET_NAME}/{_TEST_TIMESTAMP}-{_TEST_UUID.hex[:5]}-tensorflow-model",
            schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
            schema_version=constants._DEFAULT_SCHEMA_VERSION,
            metadata={
                "frameworkName": "tensorflow",
                "frameworkVersion": tf.__version__,
                "modelFile": "saved_model",
                "modelClass": "tensorflow.keras.Model",
            },
            state=GapicArtifact.State.LIVE,
        )
        create_experiment_model_artifact_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            artifact=expected_artifact,
            artifact_id=_TEST_ARTIFACT_ID,
        )

        get_tensorflow_keras_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures(
        "mock_datetime_now",
        "mock_uuid",
        "get_metadata_store_mock",
    )
    def test_save_model_tensorflow_module(
        self,
        mock_tf_save_model,
        create_experiment_model_artifact_mock,
        get_tensorflow_module_artifact_mock,
    ):
        class Adder(tf.Module):
            @tf.function(input_signature=[tf.TensorSpec(shape=[], dtype=tf.float32)])
            def add(self, x):
                return x + x

        model = Adder()

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        aiplatform.save_model(model, _TEST_ARTIFACT_ID)

        mock_tf_save_model.assert_called_once_with(
            model,
            f"{_TEST_BUCKET_NAME}/{_TEST_TIMESTAMP}-{_TEST_UUID.hex[:5]}"
            + "-tensorflow-model/saved_model",
        )

        # Verify the model artifact is created correctly
        expected_artifact = GapicArtifact(
            uri=f"{_TEST_BUCKET_NAME}/{_TEST_TIMESTAMP}-{_TEST_UUID.hex[:5]}-tensorflow-model",
            schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
            schema_version=constants._DEFAULT_SCHEMA_VERSION,
            metadata={
                "frameworkName": "tensorflow",
                "frameworkVersion": tf.__version__,
                "modelFile": "saved_model",
                "modelClass": "tensorflow.Module",
            },
            state=GapicArtifact.State.LIVE,
        )
        create_experiment_model_artifact_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            artifact=expected_artifact,
            artifact_id=_TEST_ARTIFACT_ID,
        )

        get_tensorflow_module_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_load_model_sklearn(
        self,
        mock_storage_blob_download_sklearn_model_file,
        get_sklearn_model_artifact_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        experiment_model = aiplatform.get_experiment_model(_TEST_ARTIFACT_ID)
        model = experiment_model.load_model()

        # Verify that the correct model artifact is retrieved by its ID
        get_sklearn_model_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

        # Verify that the model file is downloaded correctly
        download_file_path = mock_storage_blob_download_sklearn_model_file.call_args[1][
            "filename"
        ]
        assert download_file_path.endswith("model.pkl")

        # Verify the loaded model
        assert model.__class__.__name__ == "LinearRegression"

    def test_load_model_xgboost_booster(
        self,
        mock_storage_blob_download_xgboost_booster_file,
        get_xgboost_booster_artifact_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        # Fix the bug that xgb.__version__ in third_party returns a byte not string
        xgb.__version__ = "1.5.1"

        experiment_model = aiplatform.get_experiment_model(_TEST_ARTIFACT_ID)
        model = experiment_model.load_model()

        # Verify that the correct model artifact is retrieved by its ID
        get_xgboost_booster_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

        # Verify that the model file is downloaded correctly
        download_file_path = mock_storage_blob_download_xgboost_booster_file.call_args[
            1
        ]["filename"]
        assert download_file_path.endswith("model.bst")

        # Verify the loaded model
        assert model.__class__.__name__ == "Booster"

    def test_load_model_xgboost_xgbmodel(
        self,
        mock_storage_blob_download_xgboost_xgbmodel_file,
        get_xgboost_xgbmodel_artifact_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        # Fix the bug that xgb.__version__ in third_party returns a byte not string
        xgb.__version__ = "1.5.1"

        experiment_model = aiplatform.get_experiment_model(_TEST_ARTIFACT_ID)
        model = experiment_model.load_model()

        # Verify that the correct model artifact is retrieved by its ID
        get_xgboost_xgbmodel_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

        # Verify that the model file is downloaded correctly
        download_file_path = mock_storage_blob_download_xgboost_xgbmodel_file.call_args[
            1
        ]["filename"]
        assert download_file_path.endswith("model.bst")

        # Verify the loaded model
        assert model.__class__.__name__ == "XGBClassifier"

    def test_load_model_tensorflow_keras(
        self,
        mock_load_tensorflow_keras_model,
        get_tensorflow_keras_artifact_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        experiment_model = aiplatform.get_experiment_model(_TEST_ARTIFACT_ID)
        experiment_model.load_model()

        # Verify that the correct model artifact is retrieved by its ID
        get_tensorflow_keras_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

        # Verify that the model file is loaded correctly
        mock_load_tensorflow_keras_model.assert_called_once_with(
            f"{_TEST_URI}/saved_model",
        )

    def test_load_model_tensorflow_module(
        self,
        mock_load_tensorflow_module_model,
        get_tensorflow_module_artifact_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )
        experiment_model = aiplatform.get_experiment_model(_TEST_ARTIFACT_ID)
        experiment_model.load_model()

        # Verify that the correct model artifact is retrieved by its ID
        get_tensorflow_module_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

        # Verify that the model file is loaded correctly
        mock_load_tensorflow_module_model.assert_called_once_with(
            f"{_TEST_URI}/saved_model",
        )

    def test_register_model_sklearn(
        self, model_upload_mock, get_sklearn_model_artifact_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        experiment_model = aiplatform.get_experiment_model(_TEST_ARTIFACT_ID)
        experiment_model.register_model(display_name=_TEST_DISPLAY_NAME)

        # Verify that the correct model artifact is retrieved by its ID
        get_sklearn_model_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )
        # register_model API calls Model.upload internally to register the model
        # Since Model.upload is tested in "test_models.py", here we only need to
        # make sure register_model is sending the right args to Model.upload
        model_upload_mock.assert_called_once_with(
            serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest",
            artifact_uri=_TEST_URI,
            model_id=None,
            parent_model=None,
            is_default_version=True,
            version_aliases=None,
            version_description=None,
            display_name=_TEST_DISPLAY_NAME,
            description=None,
            labels=None,
            serving_container_predict_route=None,
            serving_container_health_route=None,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables=None,
            serving_container_ports=None,
            instance_schema_uri=None,
            parameters_schema_uri=None,
            prediction_schema_uri=None,
            explanation_metadata=None,
            explanation_parameters=None,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            encryption_spec_key_name=None,
            staging_bucket=None,
            sync=True,
            upload_request_timeout=None,
        )

    @pytest.mark.usefixtures(
        "mock_storage_blob_download_input_example",
        "get_sklearn_model_artifact_mock",
    )
    def test_get_experiment_model_info(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )
        experiment_model = aiplatform.get_experiment_model(_TEST_ARTIFACT_ID)
        model_info = experiment_model.get_model_info()

        expected_model_info = {
            "model_class": "sklearn.linear_model._base.LinearRegression",
            "framework_name": "sklearn",
            "framework_version": "1.0",
            "input_example": {
                "type": "numpy.ndarray",
                "data": _TEST_INPUT_EXAMPLE.tolist(),
            },
        }
        assert model_info == expected_model_info
