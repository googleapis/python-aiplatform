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

import pytest

from unittest import mock
from unittest.mock import patch
from importlib import reload

from google.api_core import operation

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import tensorboard
from google.cloud.aiplatform import utils

from google.cloud.aiplatform.compat.services import (
    tensorboard_service_client,
)

from google.cloud.aiplatform.compat.types import (
    encryption_spec as gca_encryption_spec,
    tensorboard as gca_tensorboard,
    tensorboard_data as gca_tensorboard_data,
    tensorboard_experiment as gca_tensorboard_experiment,
    tensorboard_run as gca_tensorboard_run,
    tensorboard_service as gca_tensorboard_service,
    tensorboard_time_series as gca_tensorboard_time_series,
)

from google.protobuf import field_mask_pb2

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_ALT_PROJECT = "test-project_alt"

_TEST_ALT_LOCATION = "europe-west4"
_TEST_INVALID_LOCATION = "us-central2"

# tensorboard
_TEST_ID = "1028944691210842416"
_TEST_DISPLAY_NAME = "my_tensorboard_1234"
_TEST_DISPLAY_NAME_UPDATE = "my_tensorboard_1234_update"

_TEST_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/tensorboards/{_TEST_ID}"
)
_TEST_ALT_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_ALT_LOCATION}/tensorboards/{_TEST_ID}"
)
_TEST_INVALID_NAME = f"prj/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/{_TEST_ID}"

_TEST_TENSORBOARD_EXPERIMENT_ID = "test-experiment"
_TEST_TENSORBOARD_EXPERIMENT_NAME = (
    f"{_TEST_NAME}/experiments/{_TEST_TENSORBOARD_EXPERIMENT_ID}"
)

_TEST_TENSORBOARD_RUN_ID = "test-run"
_TEST_TENSORBOARD_RUN_NAME = (
    f"{_TEST_TENSORBOARD_EXPERIMENT_NAME}/runs/{_TEST_TENSORBOARD_RUN_ID}"
)

_TEST_TENSORBOARD_TIME_SERIES_ID = "test-time-series"
_TEST_TENSORBOARD_TIME_SERIES_NAME = (
    f"{_TEST_TENSORBOARD_RUN_NAME}/timeSeries/{_TEST_TENSORBOARD_TIME_SERIES_ID}"
)

# request_metadata
_TEST_REQUEST_METADATA = ()

# CMEK encryption
_TEST_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_ENCRYPTION_KEY_NAME
)

_TEST_TIME_SERIES_DISPLAY_NAME = "accuracy"


@pytest.fixture
def get_tensorboard_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient, "get_tensorboard"
    ) as get_tensorboard_mock:
        get_tensorboard_mock.return_value = gca_tensorboard.Tensorboard(
            name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_tensorboard_mock


@pytest.fixture
def create_tensorboard_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient, "create_tensorboard"
    ) as create_tensorboard_mock:
        create_tensorboard_lro_mock = mock.Mock(operation.Operation)
        create_tensorboard_lro_mock.result.return_value = gca_tensorboard.Tensorboard(
            name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_tensorboard_mock.return_value = create_tensorboard_lro_mock
        yield create_tensorboard_mock


@pytest.fixture
def update_tensorboard_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient, "update_tensorboard"
    ) as update_tensorboard_mock:
        update_tensorboard_lro_mock = mock.Mock(operation.Operation)
        update_tensorboard_lro_mock.result.return_value = gca_tensorboard.Tensorboard(
            name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        update_tensorboard_mock.return_value = update_tensorboard_lro_mock
        yield update_tensorboard_mock


@pytest.fixture
def delete_tensorboard_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient, "delete_tensorboard"
    ) as delete_tensorboard_mock:
        delete_tensorboard_lro_mock = mock.Mock(operation.Operation)
        delete_tensorboard_lro_mock.result.return_value = (
            gca_tensorboard_service.DeleteTensorboardRequest(
                name=_TEST_NAME,
            )
        )
        delete_tensorboard_mock.return_value = delete_tensorboard_lro_mock
        yield delete_tensorboard_mock


_TEST_TENSORBOARD_EXPERIMENT = gca_tensorboard_experiment.TensorboardExperiment(
    name=_TEST_TENSORBOARD_EXPERIMENT_NAME,
    display_name=_TEST_DISPLAY_NAME,
)


@pytest.fixture
def get_tensorboard_experiment_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "get_tensorboard_experiment",
    ) as get_tensorboard_experiment__mock:
        get_tensorboard_experiment__mock.return_value = _TEST_TENSORBOARD_EXPERIMENT
        yield get_tensorboard_experiment__mock


@pytest.fixture
def create_tensorboard_experiment_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "create_tensorboard_experiment",
    ) as create_tensorboard_experiment_mock:
        create_tensorboard_experiment_mock.return_value = _TEST_TENSORBOARD_EXPERIMENT
        yield create_tensorboard_experiment_mock


@pytest.fixture
def delete_tensorboard_experiment_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "delete_tensorboard_experiment",
    ) as delete_tensorboard_experiment_mock:
        delete_tensorboard_lro_experiment_mock = mock.Mock(operation.Operation)
        delete_tensorboard_lro_experiment_mock.result.return_value = (
            gca_tensorboard_service.DeleteTensorboardExperimentRequest(
                name=_TEST_TENSORBOARD_EXPERIMENT_NAME,
            )
        )
        delete_tensorboard_experiment_mock.return_value = (
            delete_tensorboard_lro_experiment_mock
        )
        yield delete_tensorboard_experiment_mock


@pytest.fixture
def list_tensorboard_experiment_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "list_tensorboard_experiments",
    ) as list_tensorboard_experiment_mock:
        list_tensorboard_experiment_mock.return_value = [_TEST_TENSORBOARD_EXPERIMENT]
        yield list_tensorboard_experiment_mock


_TEST_TENSORBOARD_RUN = gca_tensorboard_run.TensorboardRun(
    name=_TEST_TENSORBOARD_RUN_NAME,
    display_name=_TEST_DISPLAY_NAME,
)


@pytest.fixture
def get_tensorboard_run_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "get_tensorboard_run",
    ) as get_tensorboard_run_mock:
        get_tensorboard_run_mock.return_value = _TEST_TENSORBOARD_RUN
        yield get_tensorboard_run_mock


@pytest.fixture
def create_tensorboard_run_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "create_tensorboard_run",
    ) as create_tensorboard_run_mock:
        create_tensorboard_run_mock.return_value = _TEST_TENSORBOARD_RUN
        yield create_tensorboard_run_mock


@pytest.fixture
def delete_tensorboard_run_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "delete_tensorboard_run",
    ) as delete_tensorboard_run_mock:
        delete_tensorboard_lro_run_mock = mock.Mock(operation.Operation)
        delete_tensorboard_lro_run_mock.result.return_value = (
            gca_tensorboard_service.DeleteTensorboardRunRequest(
                name=_TEST_TENSORBOARD_RUN_NAME,
            )
        )
        delete_tensorboard_run_mock.return_value = delete_tensorboard_lro_run_mock
        yield delete_tensorboard_run_mock


@pytest.fixture
def list_tensorboard_run_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "list_tensorboard_runs",
    ) as list_tensorboard_run_mock:
        list_tensorboard_run_mock.return_value = [
            gca_tensorboard_run.TensorboardRun(
                name=_TEST_TENSORBOARD_RUN_NAME,
                display_name=_TEST_DISPLAY_NAME,
            )
        ]
        yield list_tensorboard_run_mock


@pytest.fixture
def write_tensorboard_run_data_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "write_tensorboard_run_data",
    ) as write_tensorboard_run_data_mock:
        yield write_tensorboard_run_data_mock


_TEST_TENSORBOARD_TIME_SERIES = gca_tensorboard_time_series.TensorboardTimeSeries(
    name=_TEST_TENSORBOARD_TIME_SERIES_NAME,
    display_name=_TEST_TIME_SERIES_DISPLAY_NAME,
    value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
)


@pytest.fixture
def get_tensorboard_time_series_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "get_tensorboard_time_series",
    ) as get_tensorboard_time_series_mock:
        get_tensorboard_time_series_mock.return_value = _TEST_TENSORBOARD_TIME_SERIES
        yield get_tensorboard_time_series_mock


@pytest.fixture
def create_tensorboard_time_series_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "create_tensorboard_time_series",
    ) as create_tensorboard_time_series_mock:
        create_tensorboard_time_series_mock.return_value = _TEST_TENSORBOARD_TIME_SERIES
        yield create_tensorboard_time_series_mock


@pytest.fixture
def delete_tensorboard_time_series_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "delete_tensorboard_time_series",
    ) as delete_tensorboard_time_series_mock:
        delete_tensorboard_lro_time_series_mock = mock.Mock(operation.Operation)
        delete_tensorboard_lro_time_series_mock.result.return_value = (
            gca_tensorboard_service.DeleteTensorboardTimeSeriesRequest(
                name=_TEST_TENSORBOARD_TIME_SERIES_NAME,
            )
        )
        delete_tensorboard_time_series_mock.return_value = (
            delete_tensorboard_lro_time_series_mock
        )
        yield delete_tensorboard_time_series_mock


@pytest.fixture
def list_tensorboard_time_series_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "list_tensorboard_time_series",
    ) as list_tensorboard_time_series_mock:
        list_tensorboard_time_series_mock.return_value = [_TEST_TENSORBOARD_TIME_SERIES]
        yield list_tensorboard_time_series_mock


_TEST_TENSORBOARD_TIME_SERIES_DATA = gca_tensorboard_data.TimeSeriesData(
    tensorboard_time_series_id=_TEST_TENSORBOARD_TIME_SERIES_ID,
    value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
    values=[
        gca_tensorboard_data.TimeSeriesDataPoint(
            scalar=gca_tensorboard_data.Scalar(value=1.0),
            step=1,
            wall_time=utils.get_timestamp_proto(),
        )
    ],
)


@pytest.fixture
def batch_read_tensorboard_time_series_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "batch_read_tensorboard_time_series_data",
    ) as batch_read_tensorboard_time_series_data_mock:
        batch_read_tensorboard_time_series_data_mock.return_value = (
            gca_tensorboard_service.BatchReadTensorboardTimeSeriesDataResponse(
                time_series_data=[_TEST_TENSORBOARD_TIME_SERIES_DATA]
            )
        )
        yield batch_read_tensorboard_time_series_data_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestTensorboard:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_tensorboard(self, get_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.Tensorboard(tensorboard_name=_TEST_NAME)
        get_tensorboard_mock.assert_called_once_with(
            name=_TEST_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_tensorboard_with_id_only_with_project_and_location(
        self, get_tensorboard_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.Tensorboard(
            tensorboard_name=_TEST_ID, project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        get_tensorboard_mock.assert_called_once_with(
            name=_TEST_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_tensorboard_with_project_and_location(self, get_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.Tensorboard(
            tensorboard_name=_TEST_NAME, project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        get_tensorboard_mock.assert_called_once_with(
            name=_TEST_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_tensorboard_with_alt_project_and_location(self, get_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.Tensorboard(
            tensorboard_name=_TEST_NAME,
            project=_TEST_ALT_PROJECT,
            location=_TEST_LOCATION,
        )
        get_tensorboard_mock.assert_called_once_with(
            name=_TEST_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_tensorboard_with_alt_location(self, get_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_ALT_LOCATION)
        tensorboard.Tensorboard(
            tensorboard_name=_TEST_NAME,
        )
        get_tensorboard_mock.assert_called_once_with(
            name=_TEST_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_tensorboard_with_project_and_alt_location(self):
        aiplatform.init(project=_TEST_PROJECT)
        with pytest.raises(RuntimeError):
            tensorboard.Tensorboard(
                tensorboard_name=_TEST_NAME,
                project=_TEST_PROJECT,
                location=_TEST_ALT_LOCATION,
            )

    def test_init_tensorboard_with_location_override(self, get_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        tensorboard.Tensorboard(tensorboard_name=_TEST_ID, location=_TEST_ALT_LOCATION)
        get_tensorboard_mock.assert_called_once_with(
            name=_TEST_ALT_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_init_tensorboard_with_invalid_name(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            tensorboard.Tensorboard(tensorboard_name=_TEST_INVALID_NAME)

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_create_tensorboard_with_default_encryption_key(
        self, create_tensorboard_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        tensorboard.Tensorboard.create(
            display_name=_TEST_DISPLAY_NAME,
            create_request_timeout=None,
        )

        expected_tensorboard = gca_tensorboard.Tensorboard(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_tensorboard_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_create_tensorboard(self, create_tensorboard_mock):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.Tensorboard.create(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            create_request_timeout=None,
        )

        expected_tensorboard = gca_tensorboard.Tensorboard(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_tensorboard_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_create_tensorboard_with_timeout(self, create_tensorboard_mock):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.Tensorboard.create(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            create_request_timeout=180.0,
        )

        expected_tensorboard = gca_tensorboard.Tensorboard(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_tensorboard_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
            timeout=180.0,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_create_tensorboard_with_timeout_not_explicitly_set(
        self, create_tensorboard_mock
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.Tensorboard.create(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        expected_tensorboard = gca_tensorboard.Tensorboard(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_tensorboard_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_create_tensorboard_is_default_true(self, create_tensorboard_mock):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.Tensorboard.create(
            display_name=_TEST_DISPLAY_NAME,
            is_default=True,
        )

        expected_tensorboard = gca_tensorboard.Tensorboard(
            display_name=_TEST_DISPLAY_NAME, is_default=True
        )

        create_tensorboard_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_create_tensorboard_is_default_false(self, create_tensorboard_mock):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.Tensorboard.create(
            display_name=_TEST_DISPLAY_NAME,
            is_default=False,
        )

        expected_tensorboard = gca_tensorboard.Tensorboard(
            display_name=_TEST_DISPLAY_NAME, is_default=False
        )

        create_tensorboard_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_delete_tensorboard(self, delete_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_tensorboard = tensorboard.Tensorboard(tensorboard_name=_TEST_NAME)

        my_tensorboard.delete()

        delete_tensorboard_mock.assert_called_once_with(
            name=my_tensorboard.resource_name
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_update_tensorboard_display_name(self, update_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_tensorboard = tensorboard.Tensorboard(tensorboard_name=_TEST_NAME)
        my_tensorboard.update(display_name=_TEST_DISPLAY_NAME_UPDATE)

        expected_tensorboard = gca_tensorboard.Tensorboard(
            name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME_UPDATE,
        )
        update_tensorboard_mock.assert_called_once_with(
            update_mask=field_mask_pb2.FieldMask(paths=["display_name"]),
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_update_tensorboard_encryption_spec(self, update_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_tensorboard = tensorboard.Tensorboard(tensorboard_name=_TEST_NAME)
        my_tensorboard.update(encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME)

        expected_tensorboard = gca_tensorboard.Tensorboard(
            name=_TEST_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        update_tensorboard_mock.assert_called_once_with(
            update_mask=field_mask_pb2.FieldMask(paths=["encryption_spec"]),
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_update_tensorboard_is_default_true(self, update_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_tensorboard = tensorboard.Tensorboard(tensorboard_name=_TEST_NAME)
        my_tensorboard.update(is_default=True)

        expected_tensorboard = gca_tensorboard.Tensorboard(
            name=_TEST_NAME,
            is_default=True,
        )
        update_tensorboard_mock.assert_called_once_with(
            update_mask=field_mask_pb2.FieldMask(paths=["is_default"]),
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_update_tensorboard_is_default_false(self, update_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_tensorboard = tensorboard.Tensorboard(tensorboard_name=_TEST_NAME)
        my_tensorboard.update(is_default=False)

        expected_tensorboard = gca_tensorboard.Tensorboard(
            name=_TEST_NAME,
            is_default=False,
        )
        update_tensorboard_mock.assert_called_once_with(
            update_mask=field_mask_pb2.FieldMask(paths=["is_default"]),
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
        )


@pytest.mark.usefixtures("google_auth_mock")
class TestTensorboardExperiment:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_tensorboard_experiment(self, get_tensorboard_experiment_mock):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.TensorboardExperiment(
            tensorboard_experiment_name=_TEST_TENSORBOARD_EXPERIMENT_NAME
        )
        get_tensorboard_experiment_mock.assert_called_once_with(
            name=_TEST_TENSORBOARD_EXPERIMENT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_tensorboard_experiment_with_tensorboard(
        self, get_tensorboard_experiment_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.TensorboardExperiment(
            tensorboard_experiment_name=_TEST_TENSORBOARD_EXPERIMENT_ID,
            tensorboard_id=_TEST_ID,
        )
        get_tensorboard_experiment_mock.assert_called_once_with(
            name=_TEST_TENSORBOARD_EXPERIMENT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_tensorboard_experiment_with_id_only_with_project_and_location(
        self, get_tensorboard_experiment_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.TensorboardExperiment(
            tensorboard_experiment_name=_TEST_TENSORBOARD_EXPERIMENT_ID,
            tensorboard_id=_TEST_ID,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        get_tensorboard_experiment_mock.assert_called_once_with(
            name=_TEST_TENSORBOARD_EXPERIMENT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_create_tensorboard_experiment(
        self, create_tensorboard_experiment_mock, get_tensorboard_experiment_mock
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.TensorboardExperiment.create(
            tensorboard_experiment_id=_TEST_TENSORBOARD_EXPERIMENT_ID,
            tensorboard_name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME,
            create_request_timeout=None,
        )

        expected_tensorboard_experiment = (
            gca_tensorboard_experiment.TensorboardExperiment(
                display_name=_TEST_DISPLAY_NAME,
            )
        )

        create_tensorboard_experiment_mock.assert_called_once_with(
            parent=_TEST_NAME,
            tensorboard_experiment=expected_tensorboard_experiment,
            tensorboard_experiment_id=_TEST_TENSORBOARD_EXPERIMENT_ID,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

        get_tensorboard_experiment_mock.assert_called_once_with(
            name=_TEST_TENSORBOARD_EXPERIMENT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_create_tensorboard_experiment_with_timeout(
        self, create_tensorboard_experiment_mock, get_tensorboard_experiment_mock
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.TensorboardExperiment.create(
            tensorboard_experiment_id=_TEST_TENSORBOARD_EXPERIMENT_ID,
            tensorboard_name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME,
            create_request_timeout=180.0,
        )

        expected_tensorboard_experiment = (
            gca_tensorboard_experiment.TensorboardExperiment(
                display_name=_TEST_DISPLAY_NAME,
            )
        )

        create_tensorboard_experiment_mock.assert_called_once_with(
            parent=_TEST_NAME,
            tensorboard_experiment=expected_tensorboard_experiment,
            tensorboard_experiment_id=_TEST_TENSORBOARD_EXPERIMENT_ID,
            metadata=_TEST_REQUEST_METADATA,
            timeout=180.0,
        )

    def test_create_tensorboard_experiment_with_timeout_not_explicitly_set(
        self, create_tensorboard_experiment_mock, get_tensorboard_experiment_mock
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.TensorboardExperiment.create(
            tensorboard_experiment_id=_TEST_TENSORBOARD_EXPERIMENT_ID,
            tensorboard_name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME,
        )

        expected_tensorboard_experiment = (
            gca_tensorboard_experiment.TensorboardExperiment(
                display_name=_TEST_DISPLAY_NAME,
            )
        )

        create_tensorboard_experiment_mock.assert_called_once_with(
            parent=_TEST_NAME,
            tensorboard_experiment=expected_tensorboard_experiment,
            tensorboard_experiment_id=_TEST_TENSORBOARD_EXPERIMENT_ID,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_tensorboard_experiment_mock")
    def test_delete_tensorboard_experiement(self, delete_tensorboard_experiment_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_tensorboard_experiment = tensorboard.TensorboardExperiment(
            tensorboard_experiment_name=_TEST_TENSORBOARD_EXPERIMENT_NAME
        )

        my_tensorboard_experiment.delete()

        delete_tensorboard_experiment_mock.assert_called_once_with(
            name=my_tensorboard_experiment.resource_name
        )

    def test_list_tensorboard_experiments(self, list_tensorboard_experiment_mock):
        aiplatform.init(project=_TEST_PROJECT)

        tensorboard.TensorboardExperiment.list(tensorboard_name=_TEST_NAME)

        list_tensorboard_experiment_mock.assert_called_once_with(
            request={"parent": _TEST_NAME}
        )


@pytest.mark.usefixtures("google_auth_mock")
class TestTensorboardRun:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("list_tensorboard_time_series_mock")
    def test_init_tensorboard_run(self, get_tensorboard_run_mock):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.TensorboardRun(tensorboard_run_name=_TEST_TENSORBOARD_RUN_NAME)
        get_tensorboard_run_mock.assert_called_once_with(
            name=_TEST_TENSORBOARD_RUN_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("list_tensorboard_time_series_mock")
    def test_init_tensorboard_run_with_tensorboard_and_experiment(
        self, get_tensorboard_run_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.TensorboardRun(
            tensorboard_run_name=_TEST_TENSORBOARD_RUN_ID,
            tensorboard_experiment_id=_TEST_TENSORBOARD_EXPERIMENT_ID,
            tensorboard_id=_TEST_ID,
        )
        get_tensorboard_run_mock.assert_called_once_with(
            name=_TEST_TENSORBOARD_RUN_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_tensorboard_run_with_id_only_with_project_and_location(
        self, get_tensorboard_run_mock, list_tensorboard_time_series_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.TensorboardRun(
            tensorboard_run_name=_TEST_TENSORBOARD_RUN_ID,
            tensorboard_experiment_id=_TEST_TENSORBOARD_EXPERIMENT_ID,
            tensorboard_id=_TEST_ID,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        get_tensorboard_run_mock.assert_called_once_with(
            name=_TEST_TENSORBOARD_RUN_NAME, retry=base._DEFAULT_RETRY
        )
        list_tensorboard_time_series_mock.assert_called_once_with(
            request={"parent": _TEST_TENSORBOARD_RUN_NAME}
        )

    @pytest.mark.usefixtures("list_tensorboard_time_series_mock")
    def test_create_tensorboard_run(
        self,
        create_tensorboard_run_mock,
        get_tensorboard_run_mock,
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.TensorboardRun.create(
            tensorboard_run_id=_TEST_TENSORBOARD_RUN_ID,
            tensorboard_experiment_name=_TEST_TENSORBOARD_EXPERIMENT_NAME,
            create_request_timeout=None,
        )

        expected_tensorboard_run = gca_tensorboard_run.TensorboardRun(
            display_name=_TEST_TENSORBOARD_RUN_ID,
        )

        create_tensorboard_run_mock.assert_called_once_with(
            parent=_TEST_TENSORBOARD_EXPERIMENT_NAME,
            tensorboard_run=expected_tensorboard_run,
            tensorboard_run_id=_TEST_TENSORBOARD_RUN_ID,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

        get_tensorboard_run_mock.assert_called_once_with(
            name=_TEST_TENSORBOARD_RUN_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("list_tensorboard_time_series_mock")
    def test_create_tensorboard_run_with_timeout(
        self, create_tensorboard_run_mock, get_tensorboard_run_mock
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.TensorboardRun.create(
            tensorboard_run_id=_TEST_TENSORBOARD_RUN_ID,
            tensorboard_experiment_name=_TEST_TENSORBOARD_EXPERIMENT_NAME,
            create_request_timeout=180.0,
        )

        expected_tensorboard_run = gca_tensorboard_run.TensorboardRun(
            display_name=_TEST_TENSORBOARD_RUN_ID,
        )

        create_tensorboard_run_mock.assert_called_once_with(
            parent=_TEST_TENSORBOARD_EXPERIMENT_NAME,
            tensorboard_run=expected_tensorboard_run,
            tensorboard_run_id=_TEST_TENSORBOARD_RUN_ID,
            metadata=_TEST_REQUEST_METADATA,
            timeout=180.0,
        )

    @pytest.mark.usefixtures("list_tensorboard_time_series_mock")
    def test_create_tensorboard_run_with_timeout_not_explicitly_set(
        self, create_tensorboard_run_mock, get_tensorboard_run_mock
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.TensorboardRun.create(
            tensorboard_run_id=_TEST_TENSORBOARD_RUN_ID,
            tensorboard_experiment_name=_TEST_TENSORBOARD_EXPERIMENT_NAME,
        )

        expected_tensorboard_run = gca_tensorboard_run.TensorboardRun(
            display_name=_TEST_TENSORBOARD_RUN_ID,
        )

        create_tensorboard_run_mock.assert_called_once_with(
            parent=_TEST_TENSORBOARD_EXPERIMENT_NAME,
            tensorboard_run=expected_tensorboard_run,
            tensorboard_run_id=_TEST_TENSORBOARD_RUN_ID,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_tensorboard_run_mock", "list_tensorboard_time_series_mock"
    )
    def test_delete_tensorboard_run(self, delete_tensorboard_run_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_tensorboard_run = tensorboard.TensorboardRun(
            tensorboard_run_name=_TEST_TENSORBOARD_RUN_NAME
        )

        my_tensorboard_run.delete()

        delete_tensorboard_run_mock.assert_called_once_with(
            name=my_tensorboard_run.resource_name
        )

    def test_list_tensorboard_runs(
        self, list_tensorboard_run_mock, list_tensorboard_time_series_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        tensorboard.TensorboardRun.list(
            tensorboard_experiment_name=_TEST_TENSORBOARD_EXPERIMENT_NAME
        )

        list_tensorboard_run_mock.assert_called_once_with(
            request={"parent": _TEST_TENSORBOARD_EXPERIMENT_NAME}
        )

        list_tensorboard_time_series_mock.assert_called_once_with(
            request={"parent": _TEST_TENSORBOARD_RUN_NAME}
        )

    @pytest.mark.usefixtures(
        "get_tensorboard_run_mock", "list_tensorboard_time_series_mock"
    )
    def test_write_tensorboard_run_data(self, write_tensorboard_run_data_mock):
        aiplatform.init(project=_TEST_PROJECT)

        tb_run = tensorboard.TensorboardRun(
            tensorboard_run_name=_TEST_TENSORBOARD_RUN_NAME
        )

        timestamp = utils.get_timestamp_proto()
        tb_run.write_tensorboard_scalar_data(
            time_series_data={"accuracy": 0.9}, step=1, wall_time=timestamp
        )

        expected_time_series_data = [
            gca_tensorboard_data.TimeSeriesData(
                tensorboard_time_series_id=_TEST_TENSORBOARD_TIME_SERIES_ID,
                value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
                values=[
                    gca_tensorboard_data.TimeSeriesDataPoint(
                        scalar=gca_tensorboard_data.Scalar(value=0.9),
                        wall_time=timestamp,
                        step=1,
                    )
                ],
            ),
        ]

        write_tensorboard_run_data_mock.assert_called_once_with(
            tensorboard_run=_TEST_TENSORBOARD_RUN_NAME,
            time_series_data=expected_time_series_data,
        )

    @pytest.mark.usefixtures(
        "get_tensorboard_run_mock", "list_tensorboard_time_series_mock"
    )
    def test_read_tensorboard_time_series(
        self, batch_read_tensorboard_time_series_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        tb_run = tensorboard.TensorboardRun(
            tensorboard_run_name=_TEST_TENSORBOARD_RUN_NAME
        )

        ts_data = tb_run.read_time_series_data()

        true_ts_data = {
            _TEST_TIME_SERIES_DISPLAY_NAME: _TEST_TENSORBOARD_TIME_SERIES_DATA
        }

        batch_read_tensorboard_time_series_mock.assert_called_once_with(
            request=gca_tensorboard_service.BatchReadTensorboardTimeSeriesDataRequest(
                tensorboard=_TEST_NAME,
                time_series=[_TEST_TENSORBOARD_TIME_SERIES_NAME],
            )
        )

        assert ts_data == true_ts_data


@pytest.mark.usefixtures("google_auth_mock")
class TestTensorboardTimeSeries:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_tensorboard_time_series(self, get_tensorboard_time_series_mock):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.TensorboardTimeSeries(
            tensorboard_time_series_name=_TEST_TENSORBOARD_TIME_SERIES_NAME
        )
        get_tensorboard_time_series_mock.assert_called_once_with(
            name=_TEST_TENSORBOARD_TIME_SERIES_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_tensorboard_time_series_with_tensorboard_and_experiment_and_run(
        self, get_tensorboard_time_series_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.TensorboardTimeSeries(
            tensorboard_time_series_name=_TEST_TENSORBOARD_TIME_SERIES_ID,
            tensorboard_run_id=_TEST_TENSORBOARD_RUN_ID,
            tensorboard_experiment_id=_TEST_TENSORBOARD_EXPERIMENT_ID,
            tensorboard_id=_TEST_ID,
        )
        get_tensorboard_time_series_mock.assert_called_once_with(
            name=_TEST_TENSORBOARD_TIME_SERIES_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_tensorboard_time_series_with_id_only_with_project_and_location(
        self, get_tensorboard_time_series_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.TensorboardTimeSeries(
            tensorboard_time_series_name=_TEST_TENSORBOARD_TIME_SERIES_ID,
            tensorboard_run_id=_TEST_TENSORBOARD_RUN_ID,
            tensorboard_experiment_id=_TEST_TENSORBOARD_EXPERIMENT_ID,
            tensorboard_id=_TEST_ID,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        get_tensorboard_time_series_mock.assert_called_once_with(
            name=_TEST_TENSORBOARD_TIME_SERIES_NAME, retry=base._DEFAULT_RETRY
        )

    def test_create_tensorboard_time_series(
        self,
        create_tensorboard_time_series_mock,
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
        )

        tensorboard.TensorboardTimeSeries.create(
            display_name=_TEST_TIME_SERIES_DISPLAY_NAME,
            tensorboard_run_name=_TEST_TENSORBOARD_RUN_NAME,
        )

        expected_tensorboard_time_series = gca_tensorboard_time_series.TensorboardTimeSeries(
            display_name=_TEST_TIME_SERIES_DISPLAY_NAME,
            value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
            plugin_name="scalars",
        )

        create_tensorboard_time_series_mock.assert_called_once_with(
            parent=_TEST_TENSORBOARD_RUN_NAME,
            tensorboard_time_series=expected_tensorboard_time_series,
        )

    @pytest.mark.usefixtures("get_tensorboard_time_series_mock")
    def test_delete_tensorboard_time_series(self, delete_tensorboard_time_series_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_tensorboard_time_series = tensorboard.TensorboardTimeSeries(
            tensorboard_time_series_name=_TEST_TENSORBOARD_TIME_SERIES_NAME
        )

        my_tensorboard_time_series.delete()

        delete_tensorboard_time_series_mock.assert_called_once_with(
            name=my_tensorboard_time_series.resource_name
        )

    def test_list_tensorboard_time_series(self, list_tensorboard_time_series_mock):
        aiplatform.init(project=_TEST_PROJECT)

        tensorboard.TensorboardTimeSeries.list(
            tensorboard_run_name=_TEST_TENSORBOARD_RUN_NAME
        )

        list_tensorboard_time_series_mock.assert_called_once_with(
            request={"parent": _TEST_TENSORBOARD_RUN_NAME}
        )
