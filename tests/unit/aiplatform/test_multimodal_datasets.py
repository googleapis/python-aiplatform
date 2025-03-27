"""Unit tests for the MultimodalDataset class."""

import importlib
from unittest import mock

from google import auth
from google.api_core import operation
from google.auth import credentials as auth_credentials
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
_TEST_ID = "1028944691210842416"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/datasets/{_TEST_ID}"
_TEST_DISPLAY_NAME = "my_dataset_1234"
_TEST_LABELS = {"my_key": "my_value"}
_TEST_DESCRIPTION = "test description"
_TEST_PROMPT_RESOURCE_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/datasets/987"
)

_TEST_SOURCE_URI_BQ = "bq://my-project.my-dataset.table"
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
    bigframes_module = type(sys)("bigframes")
    bigframes_module.pandas = bpd_module
    sys.modules["bigframes"] = bigframes_module

    yield bigframes_module, bpd_module

    del sys.modules["bigframes"]
    del sys.modules["bigframes.pandas"]


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
            bigquery_uri=_TEST_SOURCE_URI_BQ,
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

    @pytest.mark.skip(reason="flaky with other tests mocking bigframes")
    @pytest.mark.usefixtures("get_dataset_mock")
    def test_create_dataset_from_pandas(
        self, create_dataset_mock, bigframes_import_mock
    ):
        _, bpd_module = bigframes_import_mock
        bigframes_mock = mock.Mock()
        bpd_module.read_pandas = lambda x: bigframes_mock
        aiplatform.init(project=_TEST_PROJECT)
        dataframe = pandas.DataFrame(
            {
                "question": ["question"],
                "answer": ["answer"],
            }
        )
        bq_table = "my-project.my-dataset.my-table"
        ummd.MultimodalDataset.from_pandas(
            dataframe=dataframe,
            target_table_id=bq_table,
            display_name=_TEST_DISPLAY_NAME,
        )
        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_MULTIMODAL,
            metadata={"inputConfig": {"bigquerySource": {"uri": f"bq://{bq_table}"}}},
        )
        create_dataset_mock.assert_called_once_with(
            dataset=expected_dataset,
            parent=_TEST_PARENT,
            timeout=None,
        )
        bigframes_mock.to_gbq.assert_called_once_with(
            destination_table=bq_table,
            if_exists="replace",
        )

    @pytest.mark.skip(reason="flaky with other tests mocking bigframes")
    @pytest.mark.usefixtures("bigframes_import_mock")
    @pytest.mark.usefixtures("get_dataset_mock")
    def test_create_dataset_from_bigframes(self, create_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT)
        bigframes_df = mock.Mock()
        bq_table = "my-project.my-dataset.my-table"
        ummd.MultimodalDataset.from_bigframes(
            dataframe=bigframes_df,
            target_table_id=bq_table,
            display_name=_TEST_DISPLAY_NAME,
        )

        bigframes_df.to_gbq.assert_called_once_with(
            destination_table=bq_table,
            if_exists="replace",
        )
        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_MULTIMODAL,
            metadata={"inputConfig": {"bigquerySource": {"uri": f"bq://{bq_table}"}}},
        )
        create_dataset_mock.assert_called_once_with(
            dataset=expected_dataset,
            parent=_TEST_PARENT,
            timeout=None,
        )

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
                gemini_template_config=template_config._raw_gemini_template_config,
            ),
            timeout=None,
        )
        assert result == ummd.TuningResourceUsageAssessmentResult(
            token_count=100, billable_character_count=200
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
                gemini_template_config=template_config._raw_gemini_template_config,
            ),
            timeout=None,
        )
        assert result == ummd.TuningValidationAssessmentResult(errors=["error message"])

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
