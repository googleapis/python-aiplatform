# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
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

# pylint: disable=protected-access,bad-continuation

import json
import pytest
from importlib import reload
from unittest import mock
from urllib import request as urllib_request
from typing import Tuple

import pandas as pd
from google.cloud import storage

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.utils import gcs_utils
import constants as test_constants

from google.cloud.aiplatform.compat.services import (
    model_garden_service_client_v1beta1,
    endpoint_service_client,
    model_service_client,
    pipeline_service_client,
)
from google.cloud.aiplatform.compat.services import prediction_service_client
from google.cloud.aiplatform.compat.types import (
    prediction_service as gca_prediction_service,
    context as gca_context,
    endpoint as gca_endpoint,
    pipeline_job as gca_pipeline_job,
    pipeline_state as gca_pipeline_state,
    deployed_model_ref_v1beta1,
)
from google.cloud.aiplatform_v1beta1.types import (
    publisher_model as gca_publisher_model,
    model as gca_model,
)

from vertexai.preview import language_models
from google.cloud.aiplatform_v1 import Execution as GapicExecution

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

_TEXT_BISON_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/text-bison",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/text-bison@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/text_generation_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/text_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/text_generation_1.0.0.yaml",
    },
}

_CHAT_BISON_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/chat-bison",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/chat-bison@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/chat_generation_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/chat_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/chat_generation_1.0.0.yaml",
    },
}

_TEXT_EMBEDDING_GECKO_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/textembedding-gecko",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/chat-bison@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/text_embedding_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/text_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/text_embedding_1.0.0.yaml",
    },
}

_TEST_TEXT_GENERATION_PREDICTION = {
    "safetyAttributes": {
        "categories": ["Violent"],
        "blocked": False,
        "scores": [0.10000000149011612],
    },
    "content": """
Ingredients:
* 3 cups all-purpose flour

Instructions:
1. Preheat oven to 350 degrees F (175 degrees C).""",
}

_TEST_CHAT_GENERATION_PREDICTION1 = {
    "safetyAttributes": {
        "scores": [],
        "blocked": False,
        "categories": [],
    },
    "candidates": [
        {
            "author": "1",
            "content": "Chat response 1",
        }
    ],
}
_TEST_CHAT_GENERATION_PREDICTION2 = {
    "safetyAttributes": {
        "scores": [],
        "blocked": False,
        "categories": [],
    },
    "candidates": [
        {
            "author": "1",
            "content": "Chat response 2",
        }
    ],
}

_TEXT_EMBEDDING_VECTOR_LENGTH = 768
_TEST_TEXT_EMBEDDING_PREDICTION = {
    "embeddings": {
        "values": list([1.0] * _TEXT_EMBEDDING_VECTOR_LENGTH),
    }
}


_TEST_TEXT_BISON_TRAINING_DF = pd.DataFrame(
    {
        "input_text": [
            "Basketball teams in the Midwest.",
            "How to bake gluten-free bread?",
            "Want to buy a new phone.",
        ],
        "output_text": [
            "There are several basketball teams located in the Midwest region of the United States. Here are some of them:",
            "Baking gluten-free bread can be a bit challenging because gluten is the protein that gives bread its structure and elasticity.",
            "Great! There are many factors to consider when buying a new phone, including your budget, preferred operating system, desired features, and more. Here are some general steps to follow to help you make an informed decision:",
        ],
    },
)

_TEST_PIPELINE_SPEC = {
    "components": {},
    "pipelineInfo": {"name": "evaluation-llm-text-generation-pipeline"},
    "root": {
        "dag": {"tasks": {}},
        "inputDefinitions": {
            "parameters": {
                "project": {"parameterType": "STRING"},
                "location": {
                    "parameterType": "STRING",
                },
                "large_model_reference": {
                    "parameterType": "STRING",
                },
                "model_display_name": {
                    "parameterType": "STRING",
                },
                "train_steps": {
                    "parameterType": "NUMBER_INTEGER",
                },
                "dataset_uri": {"parameterType": "STRING"},
                "dataset_name": {"parameterType": "STRING"},
            }
        },
    },
    "schemaVersion": "2.1.0",
    "sdkVersion": "kfp-2.0.0-beta.14",
}


_TEST_PIPELINE_SPEC_JSON = json.dumps(
    _TEST_PIPELINE_SPEC,
)

_TEST_PIPELINE_JOB = json.dumps(
    {
        "runtimeConfig": {"parameterValues": {}},
        "pipelineSpec": json.loads(_TEST_PIPELINE_SPEC_JSON),
    }
)


@pytest.fixture
def mock_pipeline_bucket_exists():
    def mock_create_gcs_bucket_for_pipeline_artifacts_if_it_does_not_exist(
        output_artifacts_gcs_dir=None,
        service_account=None,
        project=None,
        location=None,
        credentials=None,
    ):
        output_artifacts_gcs_dir = (
            output_artifacts_gcs_dir
            or gcs_utils.generate_gcs_directory_for_pipeline_artifacts(
                project=project,
                location=location,
            )
        )
        return output_artifacts_gcs_dir

    with mock.patch(
        "google.cloud.aiplatform.utils.gcs_utils.create_gcs_bucket_for_pipeline_artifacts_if_it_does_not_exist",
        wraps=mock_create_gcs_bucket_for_pipeline_artifacts_if_it_does_not_exist,
    ) as mock_context:
        yield mock_context


def make_pipeline_job(state):
    return gca_pipeline_job.PipelineJob(
        name=test_constants.PipelineJobConstants._TEST_PIPELINE_JOB_NAME,
        state=state,
        create_time=test_constants.PipelineJobConstants._TEST_PIPELINE_CREATE_TIME,
        service_account=test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT,
        network=test_constants.TrainingJobConstants._TEST_NETWORK,
        job_detail=gca_pipeline_job.PipelineJobDetail(
            pipeline_run_context=gca_context.Context(
                name=test_constants.PipelineJobConstants._TEST_PIPELINE_JOB_NAME,
            ),
            task_details=[
                gca_pipeline_job.PipelineTaskDetail(
                    task_id=456,
                    task_name="upload-llm-model",
                    execution=GapicExecution(
                        name="test-execution-name",
                        display_name="evaluation_metrics",
                        metadata={
                            "output:model_resource_name": "projects/123/locations/us-central1/models/456"
                        },
                    ),
                ),
            ],
        ),
    )


@pytest.fixture
def mock_pipeline_service_create():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_pipeline_job"
    ) as mock_create_pipeline_job:
        mock_create_pipeline_job.return_value = make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        yield mock_create_pipeline_job


@pytest.fixture
def mock_pipeline_job_get():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_job:
        mock_get_pipeline_job.side_effect = [
            make_pipeline_job(gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
        ]

        yield mock_get_pipeline_job


@pytest.fixture
def mock_load_yaml_and_json(job_spec):
    with mock.patch.object(
        storage.Blob, "download_as_bytes"
    ) as mock_load_yaml_and_json:
        mock_load_yaml_and_json.return_value = job_spec.encode()
        yield mock_load_yaml_and_json


@pytest.fixture
def mock_gcs_from_string():
    with mock.patch.object(storage.Blob, "from_string") as mock_from_string:
        yield mock_from_string


@pytest.fixture
def mock_gcs_upload():
    with mock.patch.object(storage.Blob, "upload_from_filename") as mock_from_filename:
        yield mock_from_filename


@pytest.fixture
def mock_request_urlopen(request: str) -> Tuple[str, mock.MagicMock]:
    data = _TEST_PIPELINE_SPEC
    with mock.patch.object(urllib_request, "urlopen") as mock_urlopen:
        mock_read_response = mock.MagicMock()
        mock_decode_response = mock.MagicMock()
        mock_decode_response.return_value = json.dumps(data)
        mock_read_response.return_value.decode = mock_decode_response
        mock_urlopen.return_value.read = mock_read_response
        yield request.param, mock_urlopen


@pytest.fixture
def get_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name="test-display-name",
            name=test_constants.EndpointConstants._TEST_ENDPOINT_NAME,
        )
        yield get_endpoint_mock


@pytest.fixture
def mock_get_tuned_model(get_endpoint_mock):
    with mock.patch.object(
        language_models.TextGenerationModel, "get_tuned_model"
    ) as mock_text_generation_model:
        mock_text_generation_model._model_id = (
            test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
        )
        mock_text_generation_model._endpoint_name = (
            test_constants.EndpointConstants._TEST_ENDPOINT_NAME
        )
        mock_text_generation_model._endpoint = get_endpoint_mock
        yield mock_text_generation_model


@pytest.fixture
def get_model_with_tuned_version_label_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=test_constants.ModelConstants._TEST_MODEL_NAME,
            name=test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME,
            labels={"google-vertex-llm-tuning-base-model-id": "text-bison-001"},
            deployed_models=[
                deployed_model_ref_v1beta1.DeployedModelRef(
                    endpoint=test_constants.EndpointConstants._TEST_ENDPOINT_NAME,
                    deployed_model_id=test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME,
                )
            ],
        )
        yield get_model_mock


@pytest.fixture
def get_endpoint_with_models_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_models_mock:
        get_endpoint_models_mock.return_value = gca_endpoint.Endpoint(
            display_name=test_constants.EndpointConstants._TEST_DISPLAY_NAME,
            name=test_constants.EndpointConstants._TEST_ENDPOINT_NAME,
            deployed_models=[
                gca_endpoint.DeployedModel(
                    id=test_constants.ModelConstants._TEST_ID,
                    display_name=test_constants.ModelConstants._TEST_MODEL_NAME,
                    model=test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME,
                ),
            ],
            traffic_split=test_constants.EndpointConstants._TEST_TRAFFIC_SPLIT,
        )
        yield get_endpoint_models_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestLanguageModels:
    """Unit tests for the language models."""

    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_text_generation(self):
        """Tests the text generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client_v1beta1.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.TextGenerationModel.from_pretrained(
                "google/text-bison@001"
            )

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/text-bison@001", retry=base._DEFAULT_RETRY
        )

        assert (
            model._model_resource_name
            == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/publishers/google/models/text-bison@001"
        )

        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.append(_TEST_TEXT_GENERATION_PREDICTION)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            response = model.predict(
                "What is the best recipe for banana bread? Recipe:",
                max_output_tokens=128,
                temperature=0,
                top_p=1,
                top_k=5,
            )

        assert response.text == _TEST_TEXT_GENERATION_PREDICTION["content"]

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize(
        "mock_request_urlopen",
        ["https://us-central1-kfp.pkg.dev/proj/repo/pack/latest"],
        indirect=True,
    )
    def test_tune_model(
        self,
        mock_pipeline_service_create,
        mock_pipeline_job_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
        mock_gcs_from_string,
        mock_gcs_upload,
        mock_request_urlopen,
        mock_get_tuned_model,
    ):
        """Tests tuning the text generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client_v1beta1.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "google/text-bison@001"
            )

            model.tune_model(
                training_data=_TEST_TEXT_BISON_TRAINING_DF,
                tuning_job_location="europe-west4",
                tuned_model_location="us-central1",
            )

    @pytest.mark.usefixtures(
        "get_model_with_tuned_version_label_mock",
        "get_endpoint_with_models_mock",
    )
    def test_get_tuned_model(
        self,
    ):
        """Tests getting a tuned model"""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        with mock.patch.object(
            target=model_garden_service_client_v1beta1.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):

            tuned_model = language_models.TextGenerationModel.get_tuned_model(
                test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
            )

            assert (
                tuned_model._model_resource_name
                == test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
            )

    def test_chat(self):
        """Tests the chat generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client_v1beta1.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.ChatModel.from_pretrained("google/chat-bison@001")

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/chat-bison@001", retry=base._DEFAULT_RETRY
        )

        chat = model.start_chat(
            context="""
            My name is Ned.
            You are my personal assistant.
            My favorite movies are Lord of the Rings and Hobbit.
            """,
            examples=[
                language_models.InputOutputTextPair(
                    input_text="Who do you work for?",
                    output_text="I work for Ned.",
                ),
                language_models.InputOutputTextPair(
                    input_text="What do I like?",
                    output_text="Ned likes watching movies.",
                ),
            ],
            temperature=0.2, max_output_tokens=777
        )

        gca_predict_response1 = gca_prediction_service.PredictResponse()
        gca_predict_response1.predictions.append(_TEST_CHAT_GENERATION_PREDICTION1)

        default_top_k, default_top_p = (
                language_models.TextGenerationModel._DEFAULT_TOP_K, 
                language_models.TextGenerationModel._DEFAULT_TOP_P)
        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response1,
        ) as mock_predict:
            response = chat.send_message(
                "Are my favorite movies based on a book series?",
                max_output_tokens=888
            )
            assert (
                response.text
                == _TEST_CHAT_GENERATION_PREDICTION1["candidates"][0]["content"]
            )
            assert len(chat._history) == 1
            mock_predict.assert_called_once()
            call_params = mock_predict.call_args.kwargs["parameters"]
            assert call_params["temperature"] == 0.2
            assert call_params["maxDecodeSteps"] == 888
            assert call_params["topK"] == default_top_k
            assert call_params["topP"] == default_top_p

        gca_predict_response2 = gca_prediction_service.PredictResponse()
        gca_predict_response2.predictions.append(_TEST_CHAT_GENERATION_PREDICTION2)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response2,
        ) as mock_predict:
            response = chat.send_message(
                "When where these books published?",
                temperature=0.1, top_p=0.55
            )
            assert (
                response.text
                == _TEST_CHAT_GENERATION_PREDICTION2["candidates"][0]["content"]
            )
            assert len(chat._history) == 2
            mock_predict.assert_called_once()
            call_params = mock_predict.call_args.kwargs["parameters"]
            assert call_params["temperature"] == 0.1
            assert call_params["maxDecodeSteps"] == 777
            assert call_params["topK"] == default_top_k
            assert call_params["topP"] == 0.55

    def test_text_embedding(self):
        """Tests the text embedding model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client_v1beta1.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_EMBEDDING_GECKO_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.TextEmbeddingModel.from_pretrained(
                "google/textembedding-gecko@001"
            )

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/textembedding-gecko@001",
            retry=base._DEFAULT_RETRY,
        )

        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.append(_TEST_TEXT_EMBEDDING_PREDICTION)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            embeddings = model.get_embeddings(["What is life?"])
            assert embeddings
            for embedding in embeddings:
                vector = embedding.values
                assert len(vector) == _TEXT_EMBEDDING_VECTOR_LENGTH
                assert vector == _TEST_TEXT_EMBEDDING_PREDICTION["embeddings"]["values"]
