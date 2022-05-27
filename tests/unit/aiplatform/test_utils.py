# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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
import importlib
import json
import os
import textwrap
from typing import Callable, Dict, Optional
from unittest import mock
from unittest.mock import patch

import pytest
import yaml
from google.api_core import client_options, gapic_v1
from google.cloud import aiplatform
from google.cloud import storage
from google.cloud.aiplatform import compat, utils
from google.cloud.aiplatform.utils import (
    pipeline_utils,
    prediction_utils,
    tensorboard_utils,
    yaml_utils,
)
from google.cloud.aiplatform_v1.services.model_service import (
    client as model_service_client_v1,
)
from google.cloud.aiplatform_v1beta1.services.model_service import (
    client as model_service_client_v1beta1,
)
from google.protobuf import timestamp_pb2

model_service_client_default = model_service_client_v1


@pytest.fixture
def mock_storage_client():
    with patch.object(storage, "Client") as mock_storage_client:
        bucket = mock.Mock()
        bucket.list_blobs.return_value = mock.Mock()
        mock_storage_client.get_bucket.return_value = bucket
        yield mock_storage_client


def test_invalid_region_raises_with_invalid_region():
    with pytest.raises(ValueError):
        aiplatform.utils.validate_region(region="us-west3")


def test_invalid_region_does_not_raise_with_valid_region():
    aiplatform.utils.validate_region(region="us-central1")


@pytest.fixture
def copy_tree_mock():
    with mock.patch("distutils.dir_util.copy_tree") as copy_tree_mock:
        yield copy_tree_mock


@pytest.mark.parametrize(
    "resource_noun, project, parse_resource_name_method, format_resource_name_method, parent_resource_name_fields, location, full_name",
    [
        (
            "datasets",
            "123456",
            aiplatform.TabularDataset._parse_resource_name,
            aiplatform.TabularDataset._format_resource_name,
            None,
            "us-central1",
            "projects/123456/locations/us-central1/datasets/987654",
        ),
        (
            "trainingPipelines",
            "857392",
            aiplatform.CustomTrainingJob._parse_resource_name,
            aiplatform.CustomTrainingJob._format_resource_name,
            None,
            "us-west20",
            "projects/857392/locations/us-central1/trainingPipelines/347292",
        ),
        (
            "contexts",
            "123456",
            aiplatform.metadata._Context._parse_resource_name,
            aiplatform.metadata._Context._format_resource_name,
            {aiplatform.metadata._MetadataStore._resource_noun: "default"},
            "europe-west4",
            "projects/857392/locations/us-central1/metadataStores/default/contexts/123",
        ),
        (
            "timeSeries",
            "857392",
            aiplatform.gapic.TensorboardServiceClient.parse_tensorboard_time_series_path,
            aiplatform.gapic.TensorboardServiceClient.tensorboard_time_series_path,
            {
                aiplatform.Tensorboard._resource_noun: "123",
                "experiments": "456",
                "runs": "789",
            },
            "us-central1",
            "projects/857392/locations/us-central1/tensorboards/123/experiments/456/runs/789/timeSeries/1",
        ),
    ],
)
def test_full_resource_name_with_full_name(
    resource_noun: str,
    project: str,
    parse_resource_name_method: Callable[[str], Dict[str, str]],
    format_resource_name_method: Callable[..., str],
    parent_resource_name_fields: Optional[Dict[str, str]],
    location: str,
    full_name: str,
):
    # should ignore issues with other arguments as resource_name is full_name
    assert (
        aiplatform.utils.full_resource_name(
            resource_name=full_name,
            resource_noun=resource_noun,
            parse_resource_name_method=parse_resource_name_method,
            format_resource_name_method=format_resource_name_method,
            parent_resource_name_fields=parent_resource_name_fields,
            project=project,
            location=location,
        )
        == full_name
    )


@pytest.mark.parametrize(
    "partial_name, resource_noun, parse_resource_name_method, format_resource_name_method, parent_resource_name_fields, project, location, full_name",
    [
        (
            "987654",
            "datasets",
            aiplatform.TabularDataset._parse_resource_name,
            aiplatform.TabularDataset._format_resource_name,
            None,
            "123456",
            "us-central1",
            "projects/123456/locations/us-central1/datasets/987654",
        ),
        (
            "347292",
            "trainingPipelines",
            aiplatform.CustomTrainingJob._parse_resource_name,
            aiplatform.CustomTrainingJob._format_resource_name,
            None,
            "857392",
            "us-central1",
            "projects/857392/locations/us-central1/trainingPipelines/347292",
        ),
        (
            "123",
            "contexts",
            aiplatform.metadata._Context._parse_resource_name,
            aiplatform.metadata._Context._format_resource_name,
            {aiplatform.metadata._MetadataStore._resource_noun: "default"},
            "857392",
            "us-central1",
            "projects/857392/locations/us-central1/metadataStores/default/contexts/123",
        ),
        (
            "1",
            "timeSeries",
            aiplatform.gapic.TensorboardServiceClient.parse_tensorboard_time_series_path,
            aiplatform.gapic.TensorboardServiceClient.tensorboard_time_series_path,
            {
                aiplatform.Tensorboard._resource_noun: "123",
                "experiments": "456",
                "runs": "789",
            },
            "857392",
            "us-central1",
            "projects/857392/locations/us-central1/tensorboards/123/experiments/456/runs/789/timeSeries/1",
        ),
    ],
)
def test_full_resource_name_with_partial_name(
    partial_name: str,
    resource_noun: str,
    parse_resource_name_method: Callable[[str], Dict[str, str]],
    format_resource_name_method: Callable[..., str],
    parent_resource_name_fields: Optional[Dict[str, str]],
    project: str,
    location: str,
    full_name: str,
):
    assert (
        aiplatform.utils.full_resource_name(
            resource_name=partial_name,
            resource_noun=resource_noun,
            parse_resource_name_method=parse_resource_name_method,
            format_resource_name_method=format_resource_name_method,
            parent_resource_name_fields=parent_resource_name_fields,
            project=project,
            location=location,
        )
        == full_name
    )


@pytest.mark.parametrize(
    "partial_name, resource_noun, project, location",
    [("347292", "trainingPipelines", "857392", "us-west2020")],
)
def test_full_resource_name_raises_value_error(
    partial_name: str,
    resource_noun: str,
    project: str,
    location: str,
):
    with pytest.raises(ValueError):
        aiplatform.utils.full_resource_name(
            resource_name=partial_name,
            resource_noun=resource_noun,
            parse_resource_name_method=aiplatform.CustomTrainingJob._parse_resource_name,
            format_resource_name_method=aiplatform.CustomTrainingJob._format_resource_name,
            project=project,
            location=location,
        )


def test_validate_display_name_raises_length():
    with pytest.raises(ValueError):
        aiplatform.utils.validate_display_name(
            "slanflksdnlikh;likhq290u90rflkasndfkljashndfkl;jhowq2342;iehoiwerhowqihjer34564356o;iqwjr;oijsdalfjasl;kfjas;ldifhja;slkdfsdlkfhj"
        )


def test_validate_display_name():
    aiplatform.utils.validate_display_name("my_model_abc")


def test_validate_labels_raises_value_not_str():
    with pytest.raises(ValueError):
        aiplatform.utils.validate_labels({"my_key1": 1, "my_key2": 2})


def test_validate_labels_raises_key_not_str():
    with pytest.raises(ValueError):
        aiplatform.utils.validate_labels({1: "my_value1", 2: "my_value2"})


def test_validate_labels():
    aiplatform.utils.validate_labels({"my_key1": "my_value1", "my_key2": "my_value2"})


@pytest.mark.parametrize(
    "accelerator_type, expected",
    [
        ("NVIDIA_TESLA_K80", True),
        ("ACCELERATOR_TYPE_UNSPECIFIED", True),
        ("NONEXISTENT_GPU", False),
        ("NVIDIA_GALAXY_R7", False),
        ("", False),
        (None, False),
    ],
)
def test_validate_accelerator_type(accelerator_type: str, expected: bool):
    # Invalid type raises specific ValueError
    if not expected:
        with pytest.raises(ValueError) as e:
            utils.validate_accelerator_type(accelerator_type)
        assert e.match(regexp=r"Given accelerator_type")
    # Valid type returns True
    else:
        assert utils.validate_accelerator_type(accelerator_type)


@pytest.mark.parametrize(
    "gcs_path, expected",
    [
        ("gs://example-bucket/path/to/folder", ("example-bucket", "path/to/folder")),
        ("example-bucket/path/to/folder/", ("example-bucket", "path/to/folder")),
        ("gs://example-bucket", ("example-bucket", None)),
        ("gs://example-bucket/", ("example-bucket", None)),
        ("gs://example-bucket/path", ("example-bucket", "path")),
    ],
)
def test_extract_bucket_and_prefix_from_gcs_path(gcs_path: str, expected: tuple):
    # Given a GCS path, ensure correct bucket and prefix are extracted
    assert expected == utils.extract_bucket_and_prefix_from_gcs_path(gcs_path)


@pytest.mark.usefixtures("google_auth_mock")
def test_wrapped_client():
    test_client_info = gapic_v1.client_info.ClientInfo()
    test_client_options = client_options.ClientOptions()

    wrapped_client = utils.ClientWithOverride.WrappedClient(
        client_class=model_service_client_default.ModelServiceClient,
        client_options=test_client_options,
        client_info=test_client_info,
    )

    assert isinstance(
        wrapped_client.get_model.__self__,
        model_service_client_default.ModelServiceClient,
    )


def test_client_w_override_default_version():

    test_client_info = gapic_v1.client_info.ClientInfo()
    test_client_options = client_options.ClientOptions()

    client_w_override = utils.ModelClientWithOverride(
        client_options=test_client_options,
        client_info=test_client_info,
    )
    assert isinstance(
        client_w_override._clients[
            client_w_override._default_version
        ].get_model.__self__,
        model_service_client_default.ModelServiceClient,
    )


def test_client_w_override_select_version():

    test_client_info = gapic_v1.client_info.ClientInfo()
    test_client_options = client_options.ClientOptions()

    client_w_override = utils.ModelClientWithOverride(
        client_options=test_client_options,
        client_info=test_client_info,
    )

    assert isinstance(
        client_w_override.select_version(compat.V1BETA1).get_model.__self__,
        model_service_client_v1beta1.ModelServiceClient,
    )
    assert isinstance(
        client_w_override.select_version(compat.V1).get_model.__self__,
        model_service_client_v1.ModelServiceClient,
    )


@pytest.mark.parametrize(
    "year,month,day,hour,minute,second,microsecond,expected_seconds,expected_nanos",
    [
        (
            2021,
            12,
            23,
            23,
            59,
            59,
            999999,
            1640303999,
            999000000,
        ),
        (
            2013,
            1,
            1,
            1,
            1,
            1,
            199999,
            1357002061,
            199000000,
        ),
    ],
)
def test_get_timestamp_proto(
    year,
    month,
    day,
    hour,
    minute,
    second,
    microsecond,
    expected_seconds,
    expected_nanos,
):
    time = datetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond,
    )
    true_timestamp_proto = timestamp_pb2.Timestamp(
        seconds=expected_seconds, nanos=expected_nanos
    )
    assert true_timestamp_proto == utils.get_timestamp_proto(time)


class TestPipelineUtils:
    SAMPLE_JOB_SPEC = {
        "pipelineSpec": {
            "root": {
                "inputDefinitions": {
                    "parameters": {
                        "string_param": {"type": "STRING"},
                        "int_param": {"type": "INT"},
                        "float_param": {"type": "DOUBLE"},
                        "new_param": {"type": "STRING"},
                        "bool_param": {"type": "STRING"},
                        "dict_param": {"type": "STRING"},
                        "list_param": {"type": "STRING"},
                    }
                }
            },
            "schemaVersion": "2.0.0",
        },
        "runtimeConfig": {
            "gcsOutputDirectory": "path/to/my/root",
            "parameters": {
                "string_param": {"stringValue": "test-string"},
                "int_param": {"intValue": 42},
                "float_param": {"doubleValue": 3.14},
            },
        },
    }

    def test_pipeline_utils_runtime_config_builder_from_values(self):
        my_builder = pipeline_utils.PipelineRuntimeConfigBuilder(
            pipeline_root="path/to/my/root",
            schema_version="2.0.0",
            parameter_types={
                "string_param": "STRING",
                "int_param": "INT",
                "float_param": "DOUBLE",
            },
            parameter_values={
                "string_param": "test-string",
                "int_param": 42,
                "float_param": 3.14,
            },
        )
        actual_runtime_config = my_builder.build()
        assert True

        expected_runtime_config = self.SAMPLE_JOB_SPEC["runtimeConfig"]
        assert expected_runtime_config == actual_runtime_config

    def test_pipeline_utils_runtime_config_builder_from_json(self):
        my_builder = pipeline_utils.PipelineRuntimeConfigBuilder.from_job_spec_json(
            self.SAMPLE_JOB_SPEC
        )
        actual_runtime_config = my_builder.build()

        expected_runtime_config = self.SAMPLE_JOB_SPEC["runtimeConfig"]
        assert expected_runtime_config == actual_runtime_config

    def test_pipeline_utils_runtime_config_builder_with_no_op_updates(self):
        my_builder = pipeline_utils.PipelineRuntimeConfigBuilder.from_job_spec_json(
            self.SAMPLE_JOB_SPEC
        )
        my_builder.update_pipeline_root(None)
        my_builder.update_runtime_parameters(None)
        actual_runtime_config = my_builder.build()

        expected_runtime_config = self.SAMPLE_JOB_SPEC["runtimeConfig"]
        assert expected_runtime_config == actual_runtime_config

    def test_pipeline_utils_runtime_config_builder_with_merge_updates(self):
        my_builder = pipeline_utils.PipelineRuntimeConfigBuilder.from_job_spec_json(
            self.SAMPLE_JOB_SPEC
        )
        my_builder.update_pipeline_root("path/to/my/new/root")
        my_builder.update_runtime_parameters(
            {
                "int_param": 888,
                "new_param": "new-string",
                "dict_param": {"a": 1},
                "list_param": [1, 2, 3],
                "bool_param": True,
            }
        )
        actual_runtime_config = my_builder.build()

        expected_runtime_config = {
            "gcsOutputDirectory": "path/to/my/new/root",
            "parameters": {
                "string_param": {"stringValue": "test-string"},
                "int_param": {"intValue": 888},
                "float_param": {"doubleValue": 3.14},
                "new_param": {"stringValue": "new-string"},
                "dict_param": {"stringValue": '{"a": 1}'},
                "list_param": {"stringValue": "[1, 2, 3]"},
                "bool_param": {"stringValue": "true"},
            },
        }
        assert expected_runtime_config == actual_runtime_config

    def test_pipeline_utils_runtime_config_builder_parameter_not_found(self):
        my_builder = pipeline_utils.PipelineRuntimeConfigBuilder.from_job_spec_json(
            self.SAMPLE_JOB_SPEC
        )
        my_builder.update_pipeline_root("path/to/my/new/root")
        my_builder.update_runtime_parameters({"no_such_param": "new-string"})
        with pytest.raises(ValueError) as e:
            my_builder.build()

        assert e.match(regexp=r"The pipeline parameter no_such_param is not found")


class TestTensorboardUtils:
    def test_tensorboard_get_experiment_url(self):
        actual = tensorboard_utils.get_experiment_url(
            "projects/123/locations/asia-east1/tensorboards/456/experiments/exp1"
        )
        assert actual == (
            "https://asia-east1.tensorboard."
            + "googleusercontent.com/experiment/projects+123+locations+asia-east1+tensorboards+456+experiments+exp1"
        )

    def test_get_experiments_url_bad_experiment_name(self):
        with pytest.raises(ValueError, match="Invalid experiment name: foo-bar."):
            tensorboard_utils.get_experiment_url("foo-bar")

    def test_tensorboard_get_experiments_compare_url(self):
        actual = tensorboard_utils.get_experiments_compare_url(
            (
                "projects/123/locations/asia-east1/tensorboards/456/experiments/exp1",
                "projects/123/locations/asia-east1/tensorboards/456/experiments/exp2",
            )
        )
        assert actual == (
            "https://asia-east1.tensorboard."
            + "googleusercontent.com/compare/1-exp1:123+asia-east1+456+exp1,"
            + "2-exp2:123+asia-east1+456+exp2"
        )

    def test_tensorboard_get_experiments_compare_url_fail_just_one_exp(self):
        with pytest.raises(
            ValueError, match="At least two experiment_names are required."
        ):
            tensorboard_utils.get_experiments_compare_url(
                ("projects/123/locations/asia-east1/tensorboards/456/experiments/exp1",)
            )

    def test_tensorboard_get_experiments_compare_url_fail_diff_region(self):
        with pytest.raises(
            ValueError,
            match="Got experiments from different locations: asia-east.",
        ):
            tensorboard_utils.get_experiments_compare_url(
                (
                    "projects/123/locations/asia-east1/tensorboards/456/experiments/exp1",
                    "projects/123/locations/asia-east2/tensorboards/456/experiments/exp2",
                )
            )

    def test_get_experiments_compare_url_bad_experiment_name(self):
        with pytest.raises(ValueError, match="Invalid experiment name: foo-bar."):
            tensorboard_utils.get_experiments_compare_url(("foo-bar", "foo-bar1"))


class TestPredictionUtils:
    SRC_DIR = "user_code"
    ENTRYPOINT_FILE = "entrypoint.py"
    PREDICTOR_FILE = "predictor.py"
    HANDLER_FILE = "custom_handler.py"

    def _load_module(self, name, location):
        spec = importlib.util.spec_from_file_location(name, location)
        return importlib.util.module_from_spec(spec)

    def test_populate_entrypoint_if_not_exists(self, tmp_path):
        src_dir = tmp_path / self.SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / self.PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class MyPredictor(Predictor):
                pass
            """
            )
        )
        my_predictor = self._load_module("MyPredictor", str(predictor))

        prediction_utils.populate_entrypoint_if_not_exists(
            str(src_dir),
            self.ENTRYPOINT_FILE,
            predictor=my_predictor,
        )

        entrypoint = src_dir / self.ENTRYPOINT_FILE

        assert "from predictor import MyPredictor" in entrypoint.read_text()
        assert "predictor_class=MyPredictor" in entrypoint.read_text()

    def test_populate_entrypoint_if_not_exists_invalid_src_dir(self):
        with pytest.raises(ValueError) as exception:
            prediction_utils.populate_entrypoint_if_not_exists(
                self.SRC_DIR,
                self.ENTRYPOINT_FILE,
                predictor=None,
            )

        assert "is not a valid path to a directory." in str(exception.value)

    def test_populate_entrypoint_if_not_exists_entrypoint_exists(self, tmp_path):
        src_dir = tmp_path / self.SRC_DIR
        src_dir.mkdir()
        entrypoint = src_dir / self.ENTRYPOINT_FILE
        entrypoint.write_text("")

        prediction_utils.populate_entrypoint_if_not_exists(
            str(src_dir),
            self.ENTRYPOINT_FILE,
            predictor=None,
        )

        assert (
            "from google.cloud.aiplatform import prediction"
            not in entrypoint.read_text()
        )

    def test_populate_entrypoint_if_not_exists_predictor_not_in_src_dir(self, tmp_path):
        src_dir = tmp_path / self.SRC_DIR
        src_dir.mkdir()
        predictor = tmp_path / self.PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class MyPredictor(Predictor):
                pass
            """
            )
        )
        my_predictor = self._load_module("MyPredictor", str(predictor))

        with pytest.raises(ValueError) as exception:
            prediction_utils.populate_entrypoint_if_not_exists(
                str(src_dir),
                self.ENTRYPOINT_FILE,
                predictor=my_predictor,
            )

        assert 'The file implementing "MyPredictor" must be' in str(exception.value)

    def test_populate_entrypoint_if_not_exists_predictor_is_none(self, tmp_path):
        src_dir = tmp_path / self.SRC_DIR
        src_dir.mkdir()
        handler = src_dir / self.HANDLER_FILE
        handler.write_text(
            textwrap.dedent(
                """
            class CustomHandler(Handler):
                pass
            """
            )
        )
        custom_handler = self._load_module("CustomHandler", str(handler))

        prediction_utils.populate_entrypoint_if_not_exists(
            str(src_dir),
            self.ENTRYPOINT_FILE,
            predictor=None,
            handler=custom_handler,
        )

        entrypoint = src_dir / self.ENTRYPOINT_FILE

        assert "predictor_class=None" in entrypoint.read_text()

    def test_populate_entrypoint_if_not_exists_handler_is_none(self, tmp_path):
        src_dir = tmp_path / self.SRC_DIR
        src_dir.mkdir()
        expected_message = "A handler must be provided but handler is None."

        with pytest.raises(ValueError) as exception:
            prediction_utils.populate_entrypoint_if_not_exists(
                str(src_dir),
                self.ENTRYPOINT_FILE,
                predictor=None,
                handler=None,
            )

        assert str(exception.value) == expected_message

    def test_populate_entrypoint_if_not_exists_predictionhandler_predictor_is_none(
        self, tmp_path
    ):
        src_dir = tmp_path / self.SRC_DIR
        src_dir.mkdir()
        expected_message = (
            "PredictionHandler must have a predictor class but predictor is None."
        )

        with pytest.raises(ValueError) as exception:
            prediction_utils.populate_entrypoint_if_not_exists(
                str(src_dir),
                self.ENTRYPOINT_FILE,
                predictor=None,
            )

        assert str(exception.value) == expected_message

    def test_populate_entrypoint_if_not_exists_with_custom_handler(self, tmp_path):
        src_dir = tmp_path / self.SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / self.PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class MyPredictor(Predictor):
                pass
            """
            )
        )
        my_predictor = self._load_module("MyPredictor", str(predictor))
        handler = src_dir / self.HANDLER_FILE
        handler.write_text(
            textwrap.dedent(
                """
            class CustomHandler(Handler):
                pass
            """
            )
        )
        custom_handler = self._load_module("CustomHandler", str(handler))

        prediction_utils.populate_entrypoint_if_not_exists(
            str(src_dir),
            self.ENTRYPOINT_FILE,
            predictor=my_predictor,
            handler=custom_handler,
        )

        entrypoint = src_dir / self.ENTRYPOINT_FILE

        assert "from predictor import MyPredictor" in entrypoint.read_text()
        assert "from custom_handler import CustomHandler" in entrypoint.read_text()
        assert "predictor_class=MyPredictor" in entrypoint.read_text()
        assert "handler_class=CustomHandler" in entrypoint.read_text()

    def test_populate_entrypoint_if_not_exists_with_custom_handler_and_predictor_is_none(
        self, tmp_path
    ):
        src_dir = tmp_path / self.SRC_DIR
        src_dir.mkdir()
        handler = src_dir / self.HANDLER_FILE
        handler.write_text(
            textwrap.dedent(
                """
            class CustomHandler(Handler):
                pass
            """
            )
        )
        custom_handler = self._load_module("CustomHandler", str(handler))

        prediction_utils.populate_entrypoint_if_not_exists(
            str(src_dir),
            self.ENTRYPOINT_FILE,
            predictor=None,
            handler=custom_handler,
        )

        entrypoint = src_dir / self.ENTRYPOINT_FILE

        assert "from custom_handler import CustomHandler" in entrypoint.read_text()
        assert "predictor_class=None" in entrypoint.read_text()
        assert "handler_class=CustomHandler" in entrypoint.read_text()

    def test_populate_entrypoint_if_not_exists_custom_handler_not_in_src_dir(
        self, tmp_path
    ):
        src_dir = tmp_path / self.SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / self.PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class MyPredictor(Predictor):
                pass
            """
            )
        )
        my_predictor = self._load_module("MyPredictor", str(predictor))
        handler = tmp_path / self.HANDLER_FILE
        handler.write_text(
            textwrap.dedent(
                """
            class CustomHandler(Handler):
                pass
            """
            )
        )
        custom_handler = self._load_module("CustomHandler", str(handler))

        with pytest.raises(ValueError) as exception:
            prediction_utils.populate_entrypoint_if_not_exists(
                str(src_dir),
                self.ENTRYPOINT_FILE,
                predictor=my_predictor,
                handler=custom_handler,
            )

        assert 'The file implementing "CustomHandler" must be' in str(exception.value)

    @pytest.mark.parametrize(
        "image_uri, expected",
        [
            ("gcr.io/myproject/myimage", True),
            ("us.gcr.io/myproject/myimage", True),
            ("us-docker.pkg.dev/myproject/myimage", True),
            ("us-central1-docker.pkg.dev/myproject/myimage", True),
            ("myproject/myimage", False),
            ("random.host/myproject/myimage", False),
        ],
    )
    def test_is_registry_uri(self, image_uri, expected):
        result = prediction_utils.is_registry_uri(image_uri)

        assert result == expected

    def test_get_prediction_aip_http_port(self):
        ports = [1000, 2000, 3000]

        http_port = prediction_utils.get_prediction_aip_http_port(ports)

        assert http_port == ports[0]

    def test_get_prediction_aip_http_port_default(self):
        http_port = prediction_utils.get_prediction_aip_http_port(None)

        assert http_port == 8080

    def test_download_model_artifacts(self, mock_storage_client):
        bucket = "a_fake_bucket"
        prefix = "a/fake/prefix"
        prediction_utils.download_model_artifacts(f"gs://{bucket}/{prefix}")

        assert mock_storage_client.called
        mock_storage_client().get_bucket.assert_called_once_with(bucket)
        mock_storage_client().get_bucket().list_blobs.assert_called_once_with(
            prefix=prefix
        )

    def test_download_model_artifacts_not_gcs_uri(
        self, mock_storage_client, tmp_path, copy_tree_mock
    ):
        model_dir_name = "/tmp/models"

        prediction_utils.download_model_artifacts(model_dir_name)

        assert not mock_storage_client.called
        copy_tree_mock.assert_called_once_with(model_dir_name, ".")


@pytest.fixture(scope="function")
def yaml_file(tmp_path):
    data = {"key": "val", "list": ["1", 2, 3.0]}
    yaml_file_path = os.path.join(tmp_path, "test.yaml")
    with open(yaml_file_path, "w") as f:
        yaml.dump(data, f)
    yield yaml_file_path


@pytest.fixture(scope="function")
def json_file(tmp_path):
    data = {"key": "val", "list": ["1", 2, 3.0]}
    json_file_path = os.path.join(tmp_path, "test.json")
    with open(json_file_path, "w") as f:
        json.dump(data, f)
    yield json_file_path


class TestYamlUtils:
    def test_load_yaml_from_local_file__with_json(self, yaml_file):
        actual = yaml_utils.load_yaml(yaml_file)
        expected = {"key": "val", "list": ["1", 2, 3.0]}
        assert actual == expected

    def test_load_yaml_from_local_file__with_yaml(self, json_file):
        actual = yaml_utils.load_yaml(json_file)
        expected = {"key": "val", "list": ["1", 2, 3.0]}
        assert actual == expected
