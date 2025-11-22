# -*- coding: utf-8 -*-

# Copyright 2025 Google LLC
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

import importlib
import functools
from unittest import mock
import uuid

from google import auth
from google.api_core import operation
from google.auth import credentials as auth_credentials
from google.cloud import bigquery
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.compat.types import (
    dataset_v1beta1 as gca_dataset,
    dataset_service_v1beta1 as gca_dataset_service,
)
from google.cloud.aiplatform.compat.services import (
    dataset_service_client_v1beta1 as dataset_service,
)
from google.cloud.aiplatform.preview import datasets as ummd
from vertexai import generative_models
from vertexai.preview import prompts
import pandas
import pytest

from google.protobuf import field_mask_pb2


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_ALTERNATE_LOCATION = "europe-west6"
_TEST_ID = "1028944691210842416"
_TEST_UUID = "1234567890"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/datasets/{_TEST_ID}"
_TEST_DISPLAY_NAME = "my_dataset_1234"
_TEST_LABELS = {"my_key": "my_value"}
_TEST_DESCRIPTION = "test description"
_TEST_PROMPT_RESOURCE_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/datasets/987"
)
_TEST_JSONL_CONTENT = """
json_line_1
json_line_2
"""
_TEST_BUCKET_NAME = "test-bucket"

_TEST_SOURCE_URI_BQ = "bq://my-project.my-dataset.table"
_TEST_TARGET_BQ_DATASET = f"{_TEST_PROJECT}.target-dataset"
_TEST_TARGET_BQ_TABLE = f"{_TEST_TARGET_BQ_DATASET}.target-table"
_TEST_DISPLAY_NAME = "my_dataset_1234"
_TEST_METADATA_SCHEMA_URI_MULTIMODAL = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/multimodal_1.0.0.yaml"
)
_TEST_METADATA_MULTIMODAL = {
    "inputConfig": {"bigquerySource": {"uri": _TEST_SOURCE_URI_BQ}}
}
_TEST_METADATA_MULTIMODAL_WITH_TEMPLATE_CONFIG = {
    "inputConfig": {"bigquerySource": {"uri": _TEST_SOURCE_URI_BQ}},
    "geminiTemplateConfigSource": {
        "geminiTemplateConfig": {
            # TODO(b/402399640): Make sure that field renaming (camel case/snake
            # case) is working as expected.
            "field_mapping": {"question": "questionColumn"},
        },
    },
}

_TEST_METADATA_MULTIMODAL_WITH_PROMPT_RESOURCE = {
    "inputConfig": {"bigquerySource": {"uri": _TEST_SOURCE_URI_BQ}},
    "geminiTemplateConfigSource": {"promptUri": _TEST_PROMPT_RESOURCE_NAME},
}

_TEST_ASSEMBLE_DATA_BIGQUERY_DESTINATION = "bq://my-project.my-dataset.table_assembled"


@pytest.fixture
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_default_mock:
        google_auth_default_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_default_mock


@pytest.fixture
def get_dataset_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_MULTIMODAL,
            name=_TEST_NAME,
            metadata=_TEST_METADATA_MULTIMODAL,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_template_config_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_MULTIMODAL,
            name=_TEST_NAME,
            metadata=_TEST_METADATA_MULTIMODAL_WITH_TEMPLATE_CONFIG,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_request_column_name_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        metadata = {
            "inputConfig": {"bigquerySource": {"uri": _TEST_SOURCE_URI_BQ}},
            "geminiTemplateConfigSource": {"requestColumnName": "requests"},
        }
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_MULTIMODAL,
            name=_TEST_NAME,
            metadata=metadata,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_with_prompt_resource_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_MULTIMODAL,
            name=_TEST_NAME,
            metadata=_TEST_METADATA_MULTIMODAL_WITH_PROMPT_RESOURCE,
        )
        yield get_dataset_mock


@pytest.fixture
def update_dataset_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "update_dataset"
    ) as update_dataset_mock:
        update_dataset_mock.return_value = gca_dataset.Dataset(
            name=_TEST_NAME,
            display_name=f"update_{_TEST_DISPLAY_NAME}",
            labels=_TEST_LABELS,
            description=_TEST_DESCRIPTION,
        )
        yield update_dataset_mock


@pytest.fixture
def create_dataset_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "create_dataset"
    ) as create_dataset_mock:
        create_dataset_lro_mock = mock.Mock(operation.Operation)
        create_dataset_lro_mock.result.return_value = gca_dataset.Dataset(
            name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_MULTIMODAL,
            metadata=_TEST_METADATA_MULTIMODAL,
        )
        create_dataset_mock.return_value = create_dataset_lro_mock
        yield create_dataset_mock


@pytest.fixture
def prompts_get_mock():
    with mock.patch.object(prompts, "get") as prompts_get_mock:
        prompts_get_mock.return_value = prompts.Prompt(prompt_data="hello world")
        yield prompts_get_mock


@pytest.fixture
def bigframes_import_mock():
    import sys

    bpd_module = type(sys)("bigframes.pandas")
    sys.modules["bigframes.pandas"] = bpd_module
    bbq_module = type(sys)("bigframes.bigquery")
    sys.modules["bigframes.bigquery"] = bbq_module
    bigframes_module = type(sys)("bigframes")
    bigframes_module.pandas = bpd_module
    bigframes_module.bigquery = bbq_module
    sys.modules["bigframes"] = bigframes_module

    bigframes_module.BigQueryOptions = mock.MagicMock()
    bigframes_module.connect = mock.MagicMock()

    yield bigframes_module, bpd_module, bbq_module

    del sys.modules["bigframes"]
    del sys.modules["bigframes.pandas"]
    del sys.modules["bigframes.bigquery"]


@pytest.fixture
def bq_client_mock():
    with mock.patch.object(bigquery, "Client", autospec=True) as bq_client_mock:
        bq_dataset = mock.Mock()
        bq_dataset.location = _TEST_LOCATION
        bq_client_mock.return_value.get_dataset.return_value = bq_dataset
        bq_client_mock.return_value.create_dataset = mock.Mock()
        yield bq_client_mock


@pytest.fixture
def uuid_mock():
    with mock.patch.object(uuid, "uuid4") as uuid_mock:
        uuid_mock.return_value = _TEST_UUID
        yield uuid_mock


@pytest.fixture
def update_dataset_with_template_config_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "update_dataset"
    ) as update_dataset_mock:
        update_dataset_mock.return_value = gca_dataset.Dataset(
            name=_TEST_NAME,
            display_name=f"update_{_TEST_DISPLAY_NAME}",
            metadata=_TEST_METADATA_MULTIMODAL_WITH_TEMPLATE_CONFIG,
        )
        yield update_dataset_mock


@pytest.fixture
def assess_data_tuning_resources_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "assess_data"
    ) as assess_data_mock:
        assess_data_lro_mock = mock.Mock(operation.Operation)
        assess_data_lro_mock.result.return_value = gca_dataset_service.AssessDataResponse(
            tuning_resource_usage_assessment_result=gca_dataset_service.AssessDataResponse.TuningResourceUsageAssessmentResult(
                token_count=100, billable_character_count=200
            )
        )
        assess_data_mock.return_value = assess_data_lro_mock
        yield assess_data_mock


@pytest.fixture
def assess_data_tuning_validation_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "assess_data"
    ) as assess_data_mock:
        assess_data_lro_mock = mock.Mock(operation.Operation)
        assess_data_lro_mock.result.return_value = gca_dataset_service.AssessDataResponse(
            tuning_validation_assessment_result=gca_dataset_service.AssessDataResponse.TuningValidationAssessmentResult(
                errors=["error message"],
            )
        )
        assess_data_mock.return_value = assess_data_lro_mock
        yield assess_data_mock


@pytest.fixture
def assess_data_batch_prediction_resources_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "assess_data"
    ) as assess_data_mock:
        assess_data_lro_mock = mock.Mock(operation.Operation)
        assess_data_lro_mock.result.return_value = gca_dataset_service.AssessDataResponse(
            batch_prediction_resource_usage_assessment_result=gca_dataset_service.AssessDataResponse.BatchPredictionResourceUsageAssessmentResult(
                token_count=100, audio_token_count=200
            )
        )
        assess_data_mock.return_value = assess_data_lro_mock
        yield assess_data_mock


@pytest.fixture
def assess_data_batch_prediction_validation_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "assess_data"
    ) as assess_data_mock:
        assess_data_lro_mock = mock.Mock(operation.Operation)
        assess_data_lro_mock.result.return_value = gca_dataset_service.AssessDataResponse(
            batch_prediction_validation_assessment_result=gca_dataset_service.AssessDataResponse.BatchPredictionValidationAssessmentResult()
        )
        assess_data_mock.return_value = assess_data_lro_mock
        yield assess_data_mock


@pytest.fixture
def assemble_data_mock():
    with mock.patch.object(
        dataset_service.DatasetServiceClient, "assemble_data"
    ) as assemble_data_mock:
        assemble_data_lro_mock = mock.Mock(operation.Operation)
        assemble_data_lro_mock.result.return_value = (
            gca_dataset_service.AssembleDataResponse(
                bigquery_destination=_TEST_ASSEMBLE_DATA_BIGQUERY_DESTINATION
            )
        )
        assemble_data_mock.return_value = assemble_data_lro_mock
        yield assemble_data_mock


@pytest.fixture
def mock_storage_client_bucket():
    with mock.patch.object(storage.Client, "bucket") as mock_storage_client_bucket:

        def blob_side_effect(name, mock_blob, bucket):
            mock_blob.name = name
            mock_blob.bucket = bucket
            return mock_blob

        mock_bucket = mock.Mock(autospec=storage.Bucket)
        mock_bucket.name = _TEST_BUCKET_NAME
        mock_blob = mock.Mock(autospec=storage.Blob)
        mock_bucket.blob.side_effect = functools.partial(
            blob_side_effect, mock_blob=mock_blob, bucket=mock_bucket
        )
        mock_blob.download_as_text.return_value = _TEST_JSONL_CONTENT
        mock_storage_client_bucket.return_value = mock_bucket

        yield mock_storage_client_bucket, mock_bucket, mock_blob


def test_construct_single_turn_template():
    tools = [
        generative_models.Tool(
            function_declarations=[
                generative_models.FunctionDeclaration(name="function", parameters={})
            ],
        )
    ]
    tool_config = generative_models.ToolConfig(
        function_calling_config=generative_models.ToolConfig.FunctionCallingConfig(
            mode=generative_models.ToolConfig.FunctionCallingConfig.Mode.ANY,
            allowed_function_names=["get_current_weather"],
        )
    )
    safety_settings = [
        generative_models.SafetySetting(
            category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
        )
    ]
    generation_config = generative_models.GenerationConfig(max_output_tokens=100)
    field_mapping = [{"input": "prompt", "output": "response"}]
    template_config = ummd.construct_single_turn_template(
        prompt="prompt",
        response="response",
        system_instruction="system_instruction",
        model="gemini-1.5-flash-002",
        cached_content="cached_content",
        tools=tools,
        tool_config=tool_config,
        safety_settings=safety_settings,
        generation_config=generation_config,
        field_mapping=field_mapping,
    )
    expected_gemini_example = ummd.GeminiExample(
        model="gemini-1.5-flash-002",
        contents=[
            ummd.GeminiExample.Content(
                role="user", parts=[generative_models.Part.from_text("prompt")]
            ),
            ummd.GeminiExample.Content(
                role="model",
                parts=[generative_models.Part.from_text("response")],
            ),
        ],
        system_instruction=generative_models.Content(
            parts=[
                generative_models.Part.from_text("system_instruction"),
            ]
        ),
        cached_content="cached_content",
        tools=tools,
        tool_config=tool_config,
        safety_settings=safety_settings,
        generation_config=generation_config,
    )
    expected_gemini_template_config = ummd.GeminiTemplateConfig(
        gemini_example=expected_gemini_example,
        field_mapping=[{"input": "prompt", "output": "response"}],
    )
    assert str(template_config) == str(expected_gemini_template_config)


@pytest.mark.usefixtures("google_auth_mock")
class TestMultimodalDataset:
    """Tests for the MultimodalDataset class."""

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_dataset(self, get_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT)
        ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        get_dataset_mock.assert_called_once_with(
            name=_TEST_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_dataset_bigquery_table(self):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        assert dataset.bigquery_table == _TEST_SOURCE_URI_BQ

    @pytest.mark.usefixtures("get_dataset_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_dataset_from_bigquery(self, create_dataset_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)
        new_dataset = ummd.MultimodalDataset.from_bigquery(
            bigquery_source=_TEST_SOURCE_URI_BQ,
            display_name=_TEST_DISPLAY_NAME,
            sync=sync,
        )
        if not sync:
            new_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_MULTIMODAL,
            metadata=_TEST_METADATA_MULTIMODAL,
        )
        create_dataset_mock.assert_called_once_with(
            dataset=expected_dataset,
            parent=_TEST_PARENT,
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "bigframes_import_mock",
        "get_dataset_mock",
    )
    def test_create_dataset_from_bigframes(self, create_dataset_mock, bq_client_mock):
        aiplatform.init(project=_TEST_PROJECT)
        bigframes_df = mock.Mock()
        ummd.MultimodalDataset.from_bigframes(
            dataframe=bigframes_df,
            target_table_id=_TEST_TARGET_BQ_TABLE,
            display_name=_TEST_DISPLAY_NAME,
        )

        bq_client_mock.return_value.copy_table.assert_called_once_with(
            sources=mock.ANY,
            destination=_TEST_TARGET_BQ_TABLE,
        )
        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_MULTIMODAL,
            metadata={
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{_TEST_TARGET_BQ_TABLE}"}
                }
            },
        )
        create_dataset_mock.assert_called_once_with(
            dataset=expected_dataset,
            parent=_TEST_PARENT,
            timeout=None,
        )

    @pytest.mark.usefixtures("bigframes_import_mock")
    def test_create_dataset_from_bigframes_different_project_throws_error(self):
        aiplatform.init(project=_TEST_PROJECT)
        bigframes_df = mock.Mock()
        with pytest.raises(ValueError):
            ummd.MultimodalDataset.from_bigframes(
                dataframe=bigframes_df,
                target_table_id="another_project.dataset.table",
                display_name=_TEST_DISPLAY_NAME,
            )

    @pytest.mark.usefixtures(
        "bigframes_import_mock",
    )
    def test_create_dataset_from_bigframes_different_location_throws_error(
        self, bq_client_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        bq_client_mock.return_value.get_dataset.return_value.location = (
            _TEST_ALTERNATE_LOCATION
        )
        bigframes_df = mock.Mock()
        with pytest.raises(ValueError):
            ummd.MultimodalDataset.from_bigframes(
                dataframe=bigframes_df,
                target_table_id=_TEST_TARGET_BQ_TABLE,
                display_name=_TEST_DISPLAY_NAME,
            )

    @pytest.mark.usefixtures("bigframes_import_mock")
    def test_create_dataset_from_bigframes_invalid_target_table_id_throws_error(self):
        aiplatform.init(project=_TEST_PROJECT)
        bigframes_df = mock.Mock()
        with pytest.raises(ValueError):
            ummd.MultimodalDataset.from_bigframes(
                dataframe=bigframes_df,
                target_table_id="invalid-table",
                display_name=_TEST_DISPLAY_NAME,
            )

    @pytest.mark.usefixtures(
        "bigframes_import_mock", "create_dataset_mock", "get_dataset_mock", "uuid_mock"
    )
    def test_create_dataset_from_bigframes_without_target_table_id(
        self, bq_client_mock
    ):
        test_location = "europe-west1"
        aiplatform.init(project=_TEST_PROJECT, location=test_location)
        bigframes_df = mock.Mock()

        ummd.MultimodalDataset.from_bigframes(dataframe=bigframes_df)

        bq_dataset_name = f"vertex_datasets_{test_location.replace('-', '_')}"
        create_dataset_args = bq_client_mock.return_value.create_dataset.call_args.args
        assert create_dataset_args[0].reference == bigquery.DatasetReference(
            dataset_id=bq_dataset_name, project=_TEST_PROJECT
        )
        assert create_dataset_args[0].location == test_location

        copy_table_kwargs = bq_client_mock.return_value.copy_table.call_args.kwargs
        assert (
            copy_table_kwargs["destination"]
            == f"{_TEST_PROJECT}.{bq_dataset_name}.multimodal_dataset_{_TEST_UUID}"
        )

    @pytest.mark.usefixtures(
        "get_dataset_request_column_name_mock",
    )
    def test_create_dataset_from_gemini_request_jsonl(
        self,
        create_dataset_mock,
        mock_storage_client_bucket,
        bigframes_import_mock,
        bq_client_mock,
    ):
        bf_module, bpd_module, bbq_module = bigframes_import_mock

        bpd_module.Series = pandas.Series
        bpd_module.read_pandas = mock.MagicMock()
        bbq_module.parse_json = lambda x: x

        session_mock = mock.MagicMock()
        bf_module.connect.return_value.__enter__.return_value = session_mock

        aiplatform.init(project=_TEST_PROJECT)
        bq_table = "test-project.test-dataset.test-table"
        ummd.MultimodalDataset.from_gemini_request_jsonl(
            gcs_uri=f"gs://{_TEST_BUCKET_NAME}/test-file.jsonl",
            target_table_id=bq_table,
            display_name=_TEST_DISPLAY_NAME,
        )
        mock_storage_client_bucket, mock_bucket, mock_blob = mock_storage_client_bucket
        mock_storage_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_bucket.blob.assert_called_once_with("test-file.jsonl")
        mock_blob.download_as_text.assert_called_once()

        session_mock.read_json.assert_called_once()
        assert (
            session_mock.read_json.call_args[0][0].getvalue()
            == '{"requests": ["json_line_1", "json_line_2"]}'
        )
        bq_client_mock.return_value.copy_table.assert_called_once_with(
            sources=mock.ANY,
            destination=bq_table,
        )
        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_MULTIMODAL,
            metadata={
                "inputConfig": {"bigquerySource": {"uri": f"bq://{bq_table}"}},
                "geminiTemplateConfigSource": {"requestColumnName": "requests"},
            },
        )
        create_dataset_mock.assert_called_once_with(
            dataset=expected_dataset,
            parent=_TEST_PARENT,
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_dataset_request_column_name_mock",
        "uuid_mock",
    )
    def test_create_dataset_from_gemini_request_jsonl_without_target_table_id(
        self,
        create_dataset_mock,
        mock_storage_client_bucket,
        bigframes_import_mock,
        bq_client_mock,
    ):
        bf_module, bpd_module, bbq_module = bigframes_import_mock

        bpd_module.Series = pandas.Series
        bpd_module.read_pandas = mock.MagicMock()
        bbq_module.parse_json = lambda x: x

        session_mock = mock.MagicMock()
        bf_module.connect.return_value.__enter__.return_value = session_mock

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        ummd.MultimodalDataset.from_gemini_request_jsonl(
            gcs_uri=f"gs://{_TEST_BUCKET_NAME}/test-file.jsonl",
            display_name=_TEST_DISPLAY_NAME,
        )
        mock_storage_client_bucket, mock_bucket, mock_blob = mock_storage_client_bucket
        mock_storage_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_bucket.blob.assert_called_once_with("test-file.jsonl")
        mock_blob.download_as_text.assert_called_once()

        session_mock.read_json.assert_called_once()
        assert (
            session_mock.read_json.call_args[0][0].getvalue()
            == '{"requests": ["json_line_1", "json_line_2"]}'
        )

        # Assert that the default BQ dataset is created
        location_str = _TEST_LOCATION.replace("-", "_")
        bq_dataset_name = f"vertex_datasets_{location_str}"
        bq_client_mock.return_value.create_dataset.assert_called_once()
        create_dataset_args = bq_client_mock.return_value.create_dataset.call_args.args
        assert create_dataset_args[0].reference == bigquery.DatasetReference(
            dataset_id=bq_dataset_name, project=_TEST_PROJECT
        )
        assert create_dataset_args[0].location == _TEST_LOCATION
        # Assert that the data is copied to the generated table
        expected_bq_table = (
            f"{_TEST_PROJECT}.{bq_dataset_name}.multimodal_dataset_{_TEST_UUID}"
        )
        bq_client_mock.return_value.copy_table.assert_called_once_with(
            sources=mock.ANY,
            destination=expected_bq_table,
        )
        # Assert that the Vertex AI Dataset is created with the correct metadata
        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_MULTIMODAL,
            metadata={
                "inputConfig": {"bigquerySource": {"uri": f"bq://{expected_bq_table}"}},
                "geminiTemplateConfigSource": {"requestColumnName": "requests"},
            },
        )
        create_dataset_mock.assert_called_once_with(
            dataset=expected_dataset,
            parent=_TEST_PARENT,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_dataset_request_column_name_mock")
    def test_request_column_name_returns_correct_value(self):
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        assert dataset.request_column_name == "requests"
        assert dataset.template_config is None

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_update_dataset(self, update_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)

        my_dataset.update(
            display_name=f"update_{_TEST_DISPLAY_NAME}",
            labels=_TEST_LABELS,
            description=_TEST_DESCRIPTION,
            update_request_timeout=None,
        )

        expected_dataset = gca_dataset.Dataset(
            name=_TEST_NAME,
            display_name=f"update_{_TEST_DISPLAY_NAME}",
            labels=_TEST_LABELS,
            description=_TEST_DESCRIPTION,
        )

        expected_mask = field_mask_pb2.FieldMask(
            paths=["display_name", "labels", "description"]
        )

        update_dataset_mock.assert_called_once_with(
            dataset=expected_dataset,
            update_mask=expected_mask,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_attach_template_config(self, update_dataset_with_template_config_mock):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        template_config = ummd.GeminiTemplateConfig(
            field_mapping={"question": "questionColumn"},
        )
        updated_dataset = dataset.attach_template_config(
            template_config=template_config
        )
        update_dataset_with_template_config_mock.assert_called_once_with(
            dataset=gca_dataset.Dataset(
                name=_TEST_NAME,
                metadata=_TEST_METADATA_MULTIMODAL_WITH_TEMPLATE_CONFIG,
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["metadata"]),
            timeout=None,
        )
        # TODO(b/402399640): Implement equality check for GeminiTemplateConfig.
        assert str(template_config) == str(updated_dataset.template_config)
        assert dataset.request_column_name is None

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_attach_template_config_with_prompt(
        self, update_dataset_with_template_config_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        prompt = prompts.Prompt()
        prompt._dataset = gca_dataset.Dataset(name=_TEST_PROMPT_RESOURCE_NAME)
        dataset.attach_template_config(prompt=prompt)
        update_dataset_with_template_config_mock.assert_called_once_with(
            dataset=gca_dataset.Dataset(
                name=_TEST_NAME,
                metadata=_TEST_METADATA_MULTIMODAL_WITH_PROMPT_RESOURCE,
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["metadata"]),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_has_template_config(self, update_dataset_with_template_config_mock):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        template_config = ummd.GeminiTemplateConfig(
            field_mapping={"question": "questionColumn"},
        )
        assert dataset.has_template_config() is False
        # Attach a template config to the dataset.
        dataset.attach_template_config(template_config=template_config)
        assert dataset.has_template_config() is True

    @pytest.mark.usefixtures(
        "get_dataset_with_prompt_resource_mock", "prompts_get_mock"
    )
    def test_template_config_from_prompt(self):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        template_config = dataset.template_config
        assert str(template_config.gemini_example.contents) == str(
            [
                ummd.GeminiExample.Content(
                    role="user",
                    parts=[
                        ummd.GeminiExample.Part.from_text("hello world"),
                    ],
                )
            ]
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_assess_tuning_resources(self, assess_data_tuning_resources_mock):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        template_config = ummd.GeminiTemplateConfig(
            field_mapping={"question": "questionColumn"},
        )
        result = dataset.assess_tuning_resources(
            model_name="gemini-1.5-flash-exp",
            template_config=template_config,
        )
        assess_data_tuning_resources_mock.assert_called_once_with(
            request=gca_dataset_service.AssessDataRequest(
                name=_TEST_NAME,
                tuning_resource_usage_assessment_config=gca_dataset_service.AssessDataRequest.TuningResourceUsageAssessmentConfig(
                    model_name="gemini-1.5-flash-exp"
                ),
                gemini_request_read_config=gca_dataset_service.GeminiRequestReadConfig(
                    template_config=template_config._raw_gemini_template_config
                ),
            ),
            timeout=None,
        )
        assert result == ummd.TuningResourceUsageAssessmentResult(
            token_count=100, billable_character_count=200
        )

    @pytest.mark.usefixtures("get_dataset_request_column_name_mock")
    def test_assess_tuning_resources_request_column_name(
        self, assess_data_tuning_resources_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        dataset.assess_tuning_resources(model_name="gemini-1.5-flash-exp")
        assess_data_tuning_resources_mock.assert_called_once_with(
            request=gca_dataset_service.AssessDataRequest(
                name=_TEST_NAME,
                tuning_resource_usage_assessment_config=gca_dataset_service.AssessDataRequest.TuningResourceUsageAssessmentConfig(
                    model_name="gemini-1.5-flash-exp"
                ),
                gemini_request_read_config=gca_dataset_service.GeminiRequestReadConfig(
                    assembled_request_column_name="requests"
                ),
            ),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_assess_tuning_validity(self, assess_data_tuning_validation_mock):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        template_config = ummd.GeminiTemplateConfig(
            field_mapping={"question": "questionColumn"},
        )
        result = dataset.assess_tuning_validity(
            model_name="gemini-1.5-flash-exp",
            dataset_usage="SFT_TRAINING",
            template_config=template_config,
        )
        assess_data_tuning_validation_mock.assert_called_once_with(
            request=gca_dataset_service.AssessDataRequest(
                name=_TEST_NAME,
                tuning_validation_assessment_config=gca_dataset_service.AssessDataRequest.TuningValidationAssessmentConfig(
                    model_name="gemini-1.5-flash-exp",
                    dataset_usage=gca_dataset_service.AssessDataRequest.TuningValidationAssessmentConfig.DatasetUsage.SFT_TRAINING,
                ),
                gemini_request_read_config=gca_dataset_service.GeminiRequestReadConfig(
                    template_config=template_config._raw_gemini_template_config
                ),
            ),
            timeout=None,
        )
        assert result == ummd.TuningValidationAssessmentResult(errors=["error message"])

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_assess_batch_prediction_resources(
        self, assess_data_batch_prediction_resources_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        template_config = ummd.GeminiTemplateConfig(
            field_mapping={"question": "questionColumn"},
        )
        result = dataset.assess_batch_prediction_resources(
            model_name="gemini-1.5-flash-exp",
            template_config=template_config,
        )
        assess_data_batch_prediction_resources_mock.assert_called_once_with(
            request=gca_dataset_service.AssessDataRequest(
                name=_TEST_NAME,
                batch_prediction_resource_usage_assessment_config=gca_dataset_service.AssessDataRequest.BatchPredictionResourceUsageAssessmentConfig(
                    model_name="gemini-1.5-flash-exp"
                ),
                gemini_request_read_config=gca_dataset_service.GeminiRequestReadConfig(
                    template_config=template_config._raw_gemini_template_config
                ),
            ),
            timeout=None,
        )
        assert result == ummd.BatchPredictionResourceUsageAssessmentResult(
            token_count=100, audio_token_count=200
        )

    @pytest.mark.usefixtures("get_dataset_request_column_name_mock")
    def test_assess_batch_prediction_resources_request_column_name(
        self, assess_data_batch_prediction_resources_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        dataset.assess_batch_prediction_resources(model_name="gemini-1.5-flash-exp")
        assess_data_batch_prediction_resources_mock.assert_called_once_with(
            request=gca_dataset_service.AssessDataRequest(
                name=_TEST_NAME,
                batch_prediction_resource_usage_assessment_config=gca_dataset_service.AssessDataRequest.BatchPredictionResourceUsageAssessmentConfig(
                    model_name="gemini-1.5-flash-exp"
                ),
                gemini_request_read_config=gca_dataset_service.GeminiRequestReadConfig(
                    assembled_request_column_name="requests"
                ),
            ),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_assess_batch_prediction_validity(
        self, assess_data_batch_prediction_validation_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        template_config = ummd.GeminiTemplateConfig(
            field_mapping={"question": "questionColumn"},
        )
        result = dataset.assess_batch_prediction_validity(
            model_name="gemini-1.5-flash-exp",
            template_config=template_config,
        )
        assess_data_batch_prediction_validation_mock.assert_called_once_with(
            request=gca_dataset_service.AssessDataRequest(
                name=_TEST_NAME,
                batch_prediction_validation_assessment_config=gca_dataset_service.AssessDataRequest.BatchPredictionValidationAssessmentConfig(
                    model_name="gemini-1.5-flash-exp",
                ),
                gemini_request_read_config=gca_dataset_service.GeminiRequestReadConfig(
                    template_config=template_config._raw_gemini_template_config
                ),
            ),
            timeout=None,
        )
        assert result is None

    @pytest.mark.usefixtures("get_dataset_request_column_name_mock")
    def test_assess_tuning_validity_request_column_name(
        self, assess_data_tuning_validation_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        dataset.assess_tuning_validity(
            model_name="gemini-1.5-flash-exp",
            dataset_usage="SFT_TRAINING",
        )
        assess_data_tuning_validation_mock.assert_called_once_with(
            request=gca_dataset_service.AssessDataRequest(
                name=_TEST_NAME,
                tuning_validation_assessment_config=gca_dataset_service.AssessDataRequest.TuningValidationAssessmentConfig(
                    model_name="gemini-1.5-flash-exp",
                    dataset_usage=gca_dataset_service.AssessDataRequest.TuningValidationAssessmentConfig.DatasetUsage.SFT_TRAINING,
                ),
                gemini_request_read_config=gca_dataset_service.GeminiRequestReadConfig(
                    assembled_request_column_name="requests"
                ),
            ),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_dataset_template_config_mock")
    def test_assess_tuning_validity_uses_attached_template_config(
        self, assess_data_tuning_validation_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        dataset.assess_tuning_validity(
            model_name="gemini-1.5-flash-exp",
            dataset_usage="SFT_TRAINING",
        )
        assess_data_tuning_validation_mock.assert_called_once_with(
            request=gca_dataset_service.AssessDataRequest(
                name=_TEST_NAME,
                tuning_validation_assessment_config=gca_dataset_service.AssessDataRequest.TuningValidationAssessmentConfig(
                    model_name="gemini-1.5-flash-exp",
                    dataset_usage=gca_dataset_service.AssessDataRequest.TuningValidationAssessmentConfig.DatasetUsage.SFT_TRAINING,
                ),
                gemini_request_read_config=gca_dataset_service.GeminiRequestReadConfig(
                    template_config=_TEST_METADATA_MULTIMODAL_WITH_TEMPLATE_CONFIG[
                        "geminiTemplateConfigSource"
                    ]["geminiTemplateConfig"]
                ),
            ),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_dataset_request_column_name_mock")
    def test_assess_tuning_validity_request_column_name_overridden_by_template_config(
        self, assess_data_tuning_validation_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        template_config = ummd.GeminiTemplateConfig(
            field_mapping={"question": "questionColumn"},
        )
        dataset.assess_tuning_validity(
            model_name="gemini-1.5-flash-exp",
            dataset_usage="SFT_TRAINING",
            template_config=template_config,
        )
        assess_data_tuning_validation_mock.assert_called_once_with(
            request=gca_dataset_service.AssessDataRequest(
                name=_TEST_NAME,
                tuning_validation_assessment_config=gca_dataset_service.AssessDataRequest.TuningValidationAssessmentConfig(
                    model_name="gemini-1.5-flash-exp",
                    dataset_usage=gca_dataset_service.AssessDataRequest.TuningValidationAssessmentConfig.DatasetUsage.SFT_TRAINING,
                ),
                gemini_request_read_config=gca_dataset_service.GeminiRequestReadConfig(
                    template_config=template_config._raw_gemini_template_config
                ),
            ),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_assess_tuning_validity_invalid_dataset_usage_throws_error(
        self, assess_data_tuning_validation_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        template_config = ummd.GeminiTemplateConfig(
            field_mapping={"question": "questionColumn"},
        )
        with pytest.raises(ValueError) as excinfo:
            dataset.assess_tuning_validity(
                model_name="gemini-1.5-flash-exp",
                # FOO is not in the DatasetUsage enum.
                dataset_usage="FOO",
                template_config=template_config,
            )
        assert (
            "Argument 'dataset_usage' must be one of the following: "
            "SFT_TRAINING, SFT_VALIDATION." == str(excinfo.value)
        )

    @pytest.mark.usefixtures("bigframes_import_mock", "get_dataset_mock")
    def test_assemble(self, assemble_data_mock):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        template_config = ummd.GeminiTemplateConfig(
            field_mapping={"question": "questionColumn"},
        )
        result_table_id, _ = dataset.assemble(
            template_config=template_config,
            load_dataframe=False,
        )
        assemble_data_mock.assert_called_once_with(
            request=gca_dataset_service.AssembleDataRequest(
                name=_TEST_NAME,
                gemini_request_read_config=gca_dataset_service.GeminiRequestReadConfig(
                    template_config=template_config._raw_gemini_template_config
                ),
            ),
            timeout=None,
        )
        assert result_table_id == _TEST_ASSEMBLE_DATA_BIGQUERY_DESTINATION[5:]

    @pytest.mark.usefixtures(
        "bigframes_import_mock",
        "get_dataset_request_column_name_mock",
    )
    def test_assemble_request_column_name(self, assemble_data_mock):
        aiplatform.init(project=_TEST_PROJECT)
        dataset = ummd.MultimodalDataset(dataset_name=_TEST_NAME)
        result_table_id, _ = dataset.assemble(
            load_dataframe=False,
        )
        assemble_data_mock.assert_called_once_with(
            request=gca_dataset_service.AssembleDataRequest(
                name=_TEST_NAME,
                gemini_request_read_config=gca_dataset_service.GeminiRequestReadConfig(
                    assembled_request_column_name="requests"
                ),
            ),
            timeout=None,
        )
        assert result_table_id == _TEST_ASSEMBLE_DATA_BIGQUERY_DESTINATION[5:]

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_create_dataset_from_pandas_multiregion_target_table_allowed(
        self, create_dataset_mock, bigframes_import_mock, bq_client_mock
    ):
        bq_client_mock.return_value.get_dataset.return_value.location = "us"

        _, bpd_module, _ = bigframes_import_mock

        bpd_module.read_pandas = lambda x: mock.Mock()
        aiplatform.init(project=_TEST_PROJECT)
        dataframe = pandas.DataFrame(
            {
                "question": ["question"],
                "answer": ["answer"],
            }
        )
        ummd.MultimodalDataset.from_pandas(
            dataframe=dataframe,
            target_table_id=_TEST_TARGET_BQ_TABLE,
            display_name=_TEST_DISPLAY_NAME,
            location="us-central1",
        )
        create_dataset_mock.assert_called_once()

    def test_create_dataset_from_pandas_multiregion_target_table_location_mismatch_throws_error(
        self, bigframes_import_mock, bq_client_mock
    ):
        bq_client_mock.return_value.get_dataset.return_value.location = "eu"

        _, bpd_module, _ = bigframes_import_mock

        bpd_module.read_pandas = lambda x: mock.Mock()
        aiplatform.init(project=_TEST_PROJECT)
        dataframe = pandas.DataFrame(
            {
                "question": ["question"],
                "answer": ["answer"],
            }
        )
        with pytest.raises(ValueError):
            ummd.MultimodalDataset.from_pandas(
                dataframe=dataframe,
                target_table_id=_TEST_TARGET_BQ_TABLE,
                display_name=_TEST_DISPLAY_NAME,
                location="us-central1",
            )


class TestGeminiExample:
    """Tests for the GeminiExample class."""

    def test_init_gemini_example_model(self):
        example = ummd.GeminiExample(model="gemini-1.5-flash-exp")
        assert example.model == "gemini-1.5-flash-exp"

    def test_init_gemini_example_contents(self):
        contents = [
            ummd.GeminiExample.Content(
                role="user",
                parts=[
                    ummd.GeminiExample.Part.from_text("Hello"),
                ],
            )
        ]
        example = ummd.GeminiExample(contents=contents)
        assert str(example.contents) == str(contents)

    def test_init_gemini_example_system_instruction(self):
        system_instruction = ummd.GeminiExample.Content(
            role="system",
            parts=[
                ummd.GeminiExample.Part.from_text("Hello"),
            ],
        )
        example = ummd.GeminiExample(system_instruction=system_instruction)
        assert str(example.system_instruction) == str(system_instruction)

    def test_init_gemini_example_cached_content(self):
        example = ummd.GeminiExample(cached_content="cached_content")
        assert example.cached_content == "cached_content"

    def test_init_gemini_example_tools(self):
        function_declaration = generative_models.FunctionDeclaration(
            name="function", parameters={}
        )
        tools = [
            generative_models.Tool(
                function_declarations=[function_declaration],
            )
        ]
        example = ummd.GeminiExample(tools=tools)
        assert str(example.tools) == str(tools)

    def test_init_gemini_example_tool_config(self):
        tool_config = ummd.GeminiExample.ToolConfig(
            function_calling_config=ummd.GeminiExample.ToolConfig.FunctionCallingConfig(
                mode=ummd.GeminiExample.ToolConfig.FunctionCallingConfig.Mode.ANY,
                allowed_function_names=["get_current_weather_func"],
            )
        )

        example = ummd.GeminiExample(tool_config=tool_config)
        assert str(example.tool_config) == str(tool_config)

    def test_init_gemini_example_safety_settings(self):
        safety_settings = [
            generative_models.SafetySetting(
                category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
            )
        ]
        example = ummd.GeminiExample(safety_settings=safety_settings)
        assert str(example.safety_settings) == str(safety_settings)

    def test_init_gemini_example_generation_config(self):
        generation_config = generative_models.GenerationConfig(
            max_output_tokens=1024,
            temperature=0.5,
            top_p=0.9,
            top_k=40,
        )
        example = ummd.GeminiExample(generation_config=generation_config)
        assert str(example.generation_config) == str(generation_config)

    def test_gemini_example_from_prompt(self):
        prompt = prompts.Prompt(
            prompt_data="Compare the movies {movie1} and {movie2}.",
            model_name="gemini-1.5-pro-002",
            system_instruction="You are a movie critic. Answer in a short sentence.",
            safety_settings=[
                generative_models.SafetySetting(
                    category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
                )
            ],
            generation_config=generative_models.GenerationConfig(
                max_output_tokens=1024,
                temperature=0.5,
                top_p=0.9,
                top_k=40,
            ),
        )
        gemini_example = ummd.GeminiExample.from_prompt(prompt)
        assert (
            gemini_example.model
            == "projects/test-project/locations/us-central1/publishers/google/models/gemini-1.5-pro-002"
        )
        assert str(gemini_example.contents) == str(
            [
                ummd.GeminiExample.Content(
                    role="user",
                    parts=[
                        ummd.GeminiExample.Part.from_text(
                            "Compare the movies {movie1} and {movie2}."
                        ),
                    ],
                )
            ]
        )
        assert str(gemini_example.system_instruction) == str(
            ummd.GeminiExample.Content(
                role="user",
                parts=[
                    ummd.GeminiExample.Part.from_text(
                        "You are a movie critic. Answer in a short sentence."
                    ),
                ],
            )
        )
        assert str(gemini_example.safety_settings) == str(
            [
                generative_models.SafetySetting(
                    category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
                )
            ]
        )
        assert str(gemini_example.generation_config) == str(
            generative_models.GenerationConfig(
                max_output_tokens=1024,
                temperature=0.5,
                top_p=0.9,
                top_k=40,
            )
        )
