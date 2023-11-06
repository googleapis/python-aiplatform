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
import dataclasses
import json
import pytest
from importlib import reload
from unittest import mock
from urllib import request as urllib_request
from typing import Tuple

import pandas as pd
from google.cloud import storage

from google.cloud import aiplatform
from google.cloud.aiplatform import _streaming_prediction
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.utils import gcs_utils
import constants as test_constants

from google.cloud.aiplatform.compat.services import (
    model_garden_service_client,
    endpoint_service_client,
    model_service_client,
    pipeline_service_client,
)
from google.cloud.aiplatform.compat.services import (
    prediction_service_client,
    prediction_service_async_client,
)
from google.cloud.aiplatform.compat.types import (
    artifact as gca_artifact,
    prediction_service as gca_prediction_service,
    context as gca_context,
    endpoint_v1 as gca_endpoint,
    pipeline_job as gca_pipeline_job,
    pipeline_state as gca_pipeline_state,
    deployed_model_ref_v1,
)
from google.cloud.aiplatform.compat.types import (
    publisher_model as gca_publisher_model,
    model as gca_model,
)

from google.cloud.aiplatform_v1beta1.services.prediction_service import (
    client as prediction_service_client_v1beta1,
)
from google.cloud.aiplatform_v1beta1.types import (
    prediction_service as gca_prediction_service_v1beta1,
)

import vertexai
from vertexai.preview import (
    language_models as preview_language_models,
)
from vertexai import language_models
from vertexai.language_models import _language_models
from vertexai.language_models import (
    _evaluatable_language_models,
)
from vertexai.language_models import GroundingSource
from google.cloud.aiplatform_v1 import Execution as GapicExecution
from google.cloud.aiplatform.compat.types import (
    encryption_spec as gca_encryption_spec,
)

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

# CMEK encryption
_TEST_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_ENCRYPTION_KEY_NAME
)

_TEXT_BISON_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/text-bison",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "launch_stage": gca_publisher_model.PublisherModel.LaunchStage.GA,
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
    "launch_stage": gca_publisher_model.PublisherModel.LaunchStage.GA,
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/chat-bison@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/chat_generation_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/chat_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/chat_generation_1.0.0.yaml",
    },
}

_CODECHAT_BISON_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/codechat-bison",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "launch_stage": gca_publisher_model.PublisherModel.LaunchStage.GA,
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/codechat-bison@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/codechat_generation_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/codechat_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/codechat_generation_1.0.0.yaml",
    },
}

_CODE_GENERATION_BISON_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/code-bison",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "launch_stage": gca_publisher_model.PublisherModel.LaunchStage.GA,
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/code-bison@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/code_generation_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/code_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/code_generation_1.0.0.yaml",
    },
}

_CODE_COMPLETION_BISON_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/code-gecko",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "launch_stage": gca_publisher_model.PublisherModel.LaunchStage.GA,
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/code-gecko@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/code_generation_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/code_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/code_generation_1.0.0.yaml",
    },
}

_TEXT_EMBEDDING_GECKO_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/textembedding-gecko",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "launch_stage": gca_publisher_model.PublisherModel.LaunchStage.GA,
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/textembedding-gecko@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/text_embedding_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/text_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/text_embedding_1.0.0.yaml",
    },
}

_TEST_GROUNDING_WEB_SEARCH = GroundingSource.WebSearch()

_TEST_GROUNDING_VERTEX_AI_SEARCH_DATASTORE = GroundingSource.VertexAISearch(
    data_store_id="test_datastore", location="global"
)

_TEST_TEXT_GENERATION_PREDICTION_GROUNDING = {
    "safetyAttributes": {
        "categories": ["Violent"],
        "blocked": False,
        "scores": [0.10000000149011612],
    },
    "groundingMetadata": {
        "citations": [
            {"url": "url1", "startIndex": 1, "endIndex": 2},
            {"url": "url2", "startIndex": 3, "endIndex": 4},
        ]
    },
    "content": """
Ingredients:
* 3 cups all-purpose flour

Instructions:
1. Preheat oven to 350 degrees F (175 degrees C).""",
}

_EXPECTED_PARSED_GROUNDING_METADATA = {
    "citations": [
        {
            "url": "url1",
            "start_index": 1,
            "end_index": 2,
            "title": None,
            "license": None,
            "publication_date": None,
        },
        {
            "url": "url2",
            "start_index": 3,
            "end_index": 4,
            "title": None,
            "license": None,
            "publication_date": None,
        },
    ]
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

_TEST_TEXT_GENERATION_PREDICTION_STREAMING = [
    {
        "content": "1. 2. 3. 4. 5. 6. 7. 8. 9. 10. 11. 12. 13. 14. 15. 16. 17.",
    },
    {
        "content": " 18. 19. 20. 21. 22. 23. 24. 25. 26. 27. 28. 29. 30. 31.",
        "safetyAttributes": {"blocked": False, "categories": None, "scores": None},
    },
    {
        "content": " 32. 33. 34. 35. 36. 37. 38. 39. 40. 41. 42. 43. 44. 45.",
        "citationMetadata": {
            "citations": [
                {
                    "title": "THEATRUM ARITHMETICO-GEOMETRICUM",
                    "publicationDate": "1727",
                    "endIndex": 181,
                    "startIndex": 12,
                }
            ]
        },
        "safetyAttributes": {
            "blocked": True,
            "categories": ["Finance"],
            "scores": [0.1],
        },
    },
]

_TEST_CHAT_GENERATION_PREDICTION1 = {
    "safetyAttributes": [
        {
            "scores": [],
            "blocked": False,
            "categories": [],
        }
    ],
    "candidates": [
        {
            "author": "1",
            "content": "Chat response 1",
        }
    ],
}
_TEST_CHAT_GENERATION_PREDICTION2 = {
    "safetyAttributes": [
        {
            "scores": [],
            "blocked": False,
            "categories": [],
        }
    ],
    "candidates": [
        {
            "author": "1",
            "content": "Chat response 2",
        }
    ],
}
_TEST_CHAT_GENERATION_MULTI_CANDIDATE_PREDICTION = {
    "safetyAttributes": [
        {
            "scores": [],
            "categories": [],
            "blocked": False,
        },
        {
            "scores": [0.1],
            "categories": ["Finance"],
            "blocked": True,
        },
    ],
    "candidates": [
        {
            "author": "1",
            "content": "Chat response 2",
        },
        {
            "author": "1",
            "content": "",
        },
    ],
}

_TEST_CHAT_PREDICTION_STREAMING = [
    {
        "candidates": [
            {
                "author": "1",
                "content": "1. 2. 3. 4. 5. 6. 7. 8. 9. 10. 11. 12. 13. 14. 15.",
            }
        ],
        "safetyAttributes": [{"blocked": False, "categories": None, "scores": None}],
    },
    {
        "candidates": [
            {
                "author": "1",
                "content": " 16. 17. 18. 19. 20. 21. 22. 23. 24. 25. 26. 27.",
            }
        ],
        "safetyAttributes": [
            {
                "blocked": True,
                "categories": ["Finance"],
                "scores": [0.1],
            }
        ],
    },
]

_TEST_CODE_GENERATION_PREDICTION = {
    "safetyAttributes": {
        "blocked": True,
        "categories": ["Finance"],
        "scores": [0.1],
    },
    "content": """
```python
def is_leap_year(year):
  \"\"\"
  Returns True if the given year is a leap year, False otherwise.

  Args:
    year: The year to check.

  Returns:
    True if the year is a leap year, False otherwise.
  \"\"\"

  # A year is a leap year if it is divisible by 4, but not divisible by 100,
  # unless it is also divisible by 400.

  return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
```""",
}

_TEST_CODE_COMPLETION_PREDICTION = {
    "safetyAttributes": {
        "categories": [],
        "blocked": False,
        "scores": [],
    },
    "content": """
    return s[::-1]


def reverse_string_2(s):""",
}

_TEXT_EMBEDDING_VECTOR_LENGTH = 768
_TEST_TEXT_EMBEDDING_PREDICTION = {
    "embeddings": {
        "values": list([1.0] * _TEXT_EMBEDDING_VECTOR_LENGTH),
        "statistics": {"truncated": False, "token_count": 4.0},
    }
}

_TEST_COUNT_TOKENS_RESPONSE = {
    "total_tokens": 5,
    "total_billable_characters": 25,
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
                "accelerator_type": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "api_endpoint": {
                    "defaultValue": "aiplatform.googleapis.com/ui",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "dataset_name": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "dataset_uri": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "default_context": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "enable_early_stopping": {
                    "defaultValue": True,
                    "isOptional": True,
                    "parameterType": "BOOLEAN",
                },
                "encryption_spec_key_name": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "evaluation_data_uri": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "evaluation_interval": {
                    "defaultValue": 20,
                    "isOptional": True,
                    "parameterType": "NUMBER_INTEGER",
                },
                "evaluation_output_root_dir": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "large_model_reference": {
                    "defaultValue": "text-bison@001",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "learning_rate": {
                    "defaultValue": -1,
                    "isOptional": True,
                    "parameterType": "NUMBER_DOUBLE",
                },
                "learning_rate_multiplier": {
                    "defaultValue": 1,
                    "isOptional": True,
                    "parameterType": "NUMBER_DOUBLE",
                },
                "location": {"parameterType": "STRING"},
                "model_display_name": {"parameterType": "STRING"},
                "project": {"parameterType": "STRING"},
                "tensorboard_resource_id": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "tpu_training_skip_cmek": {
                    "defaultValue": False,
                    "isOptional": True,
                    "parameterType": "BOOLEAN",
                },
                "train_steps": {
                    "defaultValue": 300,
                    "isOptional": True,
                    "parameterType": "NUMBER_INTEGER",
                },
                "tuning_method": {
                    "defaultValue": "tune_v2",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
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

_TEST_TEXT_GENERATION_METRICS = {
    "bleu": 3.9311041439597427,
    "rougeLSum": 19.014677479620463,
}


_TEST_TEXT_CLASSIFICATION_METRICS = {"auPrc": 0.9, "auRoc": 0.8, "logLoss": 0.5}

_TEST_EVAL_DATA = [
    {
        "prompt": "Basketball teams in the Midwest.",
        "ground_truth": "There are several basketball teams located in the Midwest region of the United States. Here are some of them:",
    },
    {
        "prompt": "How to bake gluten-free bread?",
        "ground_truth": "Baking gluten-free bread can be a bit challenging because gluten is the protein that gives bread its structure and elasticity.",
    },
]

_TEST_EVAL_DATA_DF = pd.DataFrame(_TEST_EVAL_DATA)

_TEST_ARTIFACT_ID = "123456"
_TEST_ARTIFACT_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default/artifacts/{_TEST_ARTIFACT_ID}"

_TEST_EVAL_PIPELINE_SPEC = {
    "components": {},
    "pipelineInfo": {"name": "evaluation-llm-text-generation-pipeline"},
    "root": {
        "dag": {"tasks": {}},
        "inputDefinitions": {
            "parameters": {
                "batch_predict_accelerator_count": {
                    "defaultValue": 0.0,
                    "isOptional": True,
                    "parameterType": "NUMBER_INTEGER",
                },
                "batch_predict_accelerator_type": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "batch_predict_gcs_source_uris": {
                    "defaultValue": [],
                    "isOptional": True,
                    "parameterType": "LIST",
                },
                "batch_predict_gcs_destination_output_uri": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "batch_predict_predictions_format": {
                    "defaultValue": "jsonl",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "enable_web_access": {
                    "defaultValue": True,
                    "isOptional": True,
                    "parameterType": "BOOLEAN",
                },
                "encryption_spec_key_name": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "evaluation_display_name": {
                    "defaultValue": "evaluation-text-generation",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "location": {
                    "defaultValue": "us-central1",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "machine_type": {
                    "defaultValue": "e2-highmem-16",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "model_name": {"parameterType": "STRING"},
                "evaluation_task": {"parameterType": "STRING"},
                "network": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "nlp_task": {
                    "defaultValue": "text-generation",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "predictions_format": {
                    "defaultValue": "jsonl",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "predictions_gcs_source": {
                    "defaultValue": [],
                    "isOptional": True,
                    "parameterType": "LIST",
                },
                "project": {"parameterType": "STRING"},
                "root_dir": {"parameterType": "STRING"},
                "service_account": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
            }
        },
    },
    "schemaVersion": "2.1.0",
    "sdkVersion": "kfp-2.0.0-beta.14",
}


_TEST_EVAL_PIPELINE_SPEC_JSON = json.dumps(
    _TEST_EVAL_PIPELINE_SPEC,
)

_TEST_EVAL_PIPELINE_JOB = json.dumps(
    {
        "runtimeConfig": {"parameterValues": {}},
        "pipelineSpec": json.loads(_TEST_EVAL_PIPELINE_SPEC_JSON),
    }
)

# Eval classification spec

_TEST_EVAL_CLASSIFICATION_PIPELINE_SPEC = {
    "components": {},
    "pipelineInfo": {"name": "evaluation-llm-text-generation-pipeline"},
    "root": {
        "dag": {"tasks": {}},
        "inputDefinitions": {
            "parameters": {
                "batch_predict_accelerator_count": {
                    "defaultValue": 0.0,
                    "isOptional": True,
                    "parameterType": "NUMBER_INTEGER",
                },
                "batch_predict_accelerator_type": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "batch_predict_gcs_source_uris": {
                    "defaultValue": [],
                    "isOptional": True,
                    "parameterType": "LIST",
                },
                "batch_predict_gcs_destination_output_uri": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "batch_predict_predictions_format": {
                    "defaultValue": "jsonl",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "enable_web_access": {
                    "defaultValue": True,
                    "isOptional": True,
                    "parameterType": "BOOLEAN",
                },
                "encryption_spec_key_name": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "evaluation_display_name": {
                    "defaultValue": "evaluation-text-generation",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "location": {
                    "defaultValue": "us-central1",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "machine_type": {
                    "defaultValue": "e2-highmem-16",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "model_name": {"parameterType": "STRING"},
                "evaluation_task": {"parameterType": "STRING"},
                "network": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "nlp_task": {
                    "defaultValue": "text-generation",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "predictions_format": {
                    "defaultValue": "jsonl",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "predictions_gcs_source": {
                    "defaultValue": [],
                    "isOptional": True,
                    "parameterType": "LIST",
                },
                "evaluation_class_labels": {
                    "defaultValue": [],
                    "isOptional": True,
                    "parameterType": "LIST",
                },
                "target_field_name": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
                "project": {"parameterType": "STRING"},
                "root_dir": {"parameterType": "STRING"},
                "service_account": {
                    "defaultValue": "",
                    "isOptional": True,
                    "parameterType": "STRING",
                },
            }
        },
    },
    "schemaVersion": "2.1.0",
    "sdkVersion": "kfp-2.0.0-beta.14",
}

_TEST_EVAL_CLASSIFICATION_PIPELINE_SPEC_JSON = json.dumps(
    _TEST_EVAL_CLASSIFICATION_PIPELINE_SPEC,
)

_TEST_EVAL_CLASSIFICATION_PIPELINE_JOB = json.dumps(
    {
        "runtimeConfig": {"parameterValues": {}},
        "pipelineSpec": json.loads(_TEST_EVAL_PIPELINE_SPEC_JSON),
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
                    task_name="tune-large-model-20230724214903",
                    execution=GapicExecution(
                        name="projects/123/locations/europe-west4/metadataStores/default/executions/...",
                        display_name="tune-large-model-20230724214903",
                        schema_title="system.Run",
                        metadata={
                            "output:model_resource_name": "projects/123/locations/us-central1/models/456",
                            "output:endpoint_resource_name": "projects/123/locations/us-central1/endpoints/456",
                        },
                    ),
                ),
            ],
        ),
    )


def make_eval_pipeline_job(state):
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
                    task_name=test_constants.PipelineJobConstants._TEST_PIPELINE_JOB_ID,
                    outputs={
                        "evaluation_metrics": gca_pipeline_job.PipelineTaskDetail.ArtifactList(
                            artifacts=[
                                gca_artifact.Artifact(
                                    name="test-metric-artifact",
                                    metadata=_TEST_TEXT_GENERATION_METRICS,
                                ),
                            ],
                        )
                    },
                ),
                gca_pipeline_job.PipelineTaskDetail(
                    task_id=789,
                    task_name=test_constants.PipelineJobConstants._TEST_PIPELINE_JOB_ID,
                    outputs={
                        "evaluation_metrics": gca_pipeline_job.PipelineTaskDetail.ArtifactList(
                            artifacts=[
                                gca_artifact.Artifact(
                                    display_name="evaluation_metrics",
                                    uri="gs://test-bucket/evaluation_metrics",
                                ),
                            ]
                        )
                    },
                ),
            ],
        ),
    )


def make_eval_classification_pipeline_job(state):
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
                    task_name=test_constants.PipelineJobConstants._TEST_PIPELINE_JOB_ID,
                    outputs={
                        "evaluation_metrics": gca_pipeline_job.PipelineTaskDetail.ArtifactList(
                            artifacts=[
                                gca_artifact.Artifact(
                                    name="test-metric-artifact",
                                    metadata=_TEST_TEXT_CLASSIFICATION_METRICS,
                                ),
                            ],
                        )
                    },
                ),
                gca_pipeline_job.PipelineTaskDetail(
                    task_id=789,
                    task_name=test_constants.PipelineJobConstants._TEST_PIPELINE_JOB_ID,
                    outputs={
                        "evaluation_metrics": gca_pipeline_job.PipelineTaskDetail.ArtifactList(
                            artifacts=[
                                gca_artifact.Artifact(
                                    display_name="evaluation_metrics",
                                    uri="gs://test-bucket/evaluation_metrics",
                                ),
                            ]
                        )
                    },
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
def mock_pipeline_service_create_eval():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_pipeline_job"
    ) as mock_create_pipeline_job:
        mock_create_pipeline_job.return_value = make_eval_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        yield mock_create_pipeline_job


@pytest.fixture
def mock_pipeline_service_create_eval_classification():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_pipeline_job"
    ) as mock_create_pipeline_job:
        mock_create_pipeline_job.return_value = make_eval_classification_pipeline_job(
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
def mock_pipeline_job_get_eval():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_job:
        mock_get_pipeline_job.side_effect = [
            make_eval_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING
            ),
            make_eval_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
        ]

        yield mock_get_pipeline_job


@pytest.fixture
def mock_pipeline_job_get_eval_classification():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_job:
        mock_get_pipeline_job.side_effect = [
            make_eval_classification_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING
            ),
            make_eval_classification_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_classification_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_classification_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_classification_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_classification_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_classification_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_classification_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_eval_classification_pipeline_job(
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
def mock_request_urlopen_eval(request: str) -> Tuple[str, mock.MagicMock]:
    data = _TEST_EVAL_PIPELINE_SPEC
    with mock.patch.object(urllib_request, "urlopen") as mock_urlopen:
        mock_read_response = mock.MagicMock()
        mock_decode_response = mock.MagicMock()
        mock_decode_response.return_value = json.dumps(data)
        mock_read_response.return_value.decode = mock_decode_response
        mock_urlopen.return_value.read = mock_read_response
        yield request.param, mock_urlopen


@pytest.fixture
def mock_request_urlopen_eval_classification(
    request: str,
) -> Tuple[str, mock.MagicMock]:
    data = _TEST_EVAL_CLASSIFICATION_PIPELINE_SPEC
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
            deployed_models=[
                gca_endpoint.DeployedModel(
                    model=test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
                ),
            ],
        )
        yield get_endpoint_mock


@pytest.fixture
def mock_get_tuned_model(get_endpoint_mock):
    with mock.patch.object(
        _language_models._TunableModelMixin, "get_tuned_model"
    ) as mock_text_generation_model:
        mock_text_generation_model.return_value._model_id = (
            test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
        )
        mock_text_generation_model.return_value._endpoint_name = (
            test_constants.EndpointConstants._TEST_ENDPOINT_NAME
        )
        mock_text_generation_model.return_value._endpoint = get_endpoint_mock
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
                deployed_model_ref_v1.DeployedModelRef(
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


# Model Evaluation fixtures
@pytest.fixture
def mock_model_evaluate():
    with mock.patch.object(
        _evaluatable_language_models._EvaluatableLanguageModel, "evaluate"
    ) as mock_model_evaluate:
        mock_model_evaluate.return_value = _TEST_TEXT_GENERATION_METRICS
        yield mock_model_evaluate


@pytest.fixture
def mock_successfully_completed_eval_job():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_model_eval_job:
        mock_get_model_eval_job.return_value = make_eval_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        yield mock_get_model_eval_job


@pytest.fixture
def mock_successfully_completed_eval_classification_job():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_model_eval_job:
        mock_get_model_eval_job.return_value = make_eval_classification_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        yield mock_get_model_eval_job


@pytest.fixture
def mock_storage_blob_upload_from_filename():
    with mock.patch(
        "google.cloud.storage.Blob.upload_from_filename"
    ) as mock_blob_upload_from_filename, mock.patch(
        "google.cloud.storage.Bucket.exists", return_value=True
    ):
        yield mock_blob_upload_from_filename


@pytest.mark.usefixtures("google_auth_mock")
class TestLanguageModels:
    """Unit tests for the language models."""

    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_text_generation(self):
        """Tests the text generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = preview_language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
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
                temperature=0.0,
                top_p=1.0,
                top_k=5,
            )

        assert response.text == _TEST_TEXT_GENERATION_PREDICTION["content"]
        assert (
            response.raw_prediction_response.predictions[0]
            == _TEST_TEXT_GENERATION_PREDICTION
        )
        assert (
            response.safety_attributes["Violent"]
            == _TEST_TEXT_GENERATION_PREDICTION["safetyAttributes"]["scores"][0]
        )

    def test_text_generation_preview_count_tokens(self):
        """Tests the text generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = preview_language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

        gca_count_tokens_response = gca_prediction_service_v1beta1.CountTokensResponse(
            total_tokens=_TEST_COUNT_TOKENS_RESPONSE["total_tokens"],
            total_billable_characters=_TEST_COUNT_TOKENS_RESPONSE[
                "total_billable_characters"
            ],
        )

        with mock.patch.object(
            target=prediction_service_client_v1beta1.PredictionServiceClient,
            attribute="count_tokens",
            return_value=gca_count_tokens_response,
        ):
            response = model.count_tokens(["What is the best recipe for banana bread?"])

            assert response.total_tokens == _TEST_COUNT_TOKENS_RESPONSE["total_tokens"]
            assert (
                response.total_billable_characters
                == _TEST_COUNT_TOKENS_RESPONSE["total_billable_characters"]
            )

    def test_text_generation_ga(self):
        """Tests the text generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
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
        ) as mock_predict:
            response = model.predict(
                "What is the best recipe for banana bread? Recipe:",
                max_output_tokens=128,
                temperature=0.0,
                top_p=1.0,
                top_k=5,
                stop_sequences=["\n"],
            )

        prediction_parameters = mock_predict.call_args[1]["parameters"]
        assert prediction_parameters["maxDecodeSteps"] == 128
        assert prediction_parameters["temperature"] == 0.0
        assert prediction_parameters["topP"] == 1.0
        assert prediction_parameters["topK"] == 5
        assert prediction_parameters["stopSequences"] == ["\n"]
        assert response.text == _TEST_TEXT_GENERATION_PREDICTION["content"]

        # Validating that unspecified parameters are not passed to the model
        # (except `max_output_tokens`).
        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ) as mock_predict:
            model.predict(
                "What is the best recipe for banana bread? Recipe:",
            )

        prediction_parameters = mock_predict.call_args[1]["parameters"]
        assert (
            prediction_parameters["maxDecodeSteps"]
            == language_models.TextGenerationModel._DEFAULT_MAX_OUTPUT_TOKENS
        )
        assert "temperature" not in prediction_parameters
        assert "topP" not in prediction_parameters
        assert "topK" not in prediction_parameters

    def test_text_generation_multiple_candidates(self):
        """Tests the text generation model with multiple candidates."""
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

        gca_predict_response = gca_prediction_service.PredictResponse()
        # Discrepancy between the number of `instances` and the number of `predictions`
        # is a violation of the prediction service invariant, but the service does this.
        gca_predict_response.predictions.append(_TEST_TEXT_GENERATION_PREDICTION)
        gca_predict_response.predictions.append(_TEST_TEXT_GENERATION_PREDICTION)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ) as mock_predict:
            response = model.predict(
                "What is the best recipe for banana bread? Recipe:",
                candidate_count=2,
            )
        prediction_parameters = mock_predict.call_args[1]["parameters"]
        assert prediction_parameters["candidateCount"] == 2

        assert response.text == _TEST_TEXT_GENERATION_PREDICTION["content"]
        assert len(response.candidates) == 2
        assert (
            response.candidates[0].text == _TEST_TEXT_GENERATION_PREDICTION["content"]
        )

    def test_text_generation_multiple_candidates_grounding(self):
        """Tests the text generation model with multiple candidates with web grounding."""
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

        gca_predict_response = gca_prediction_service.PredictResponse()
        # Discrepancy between the number of `instances` and the number of `predictions`
        # is a violation of the prediction service invariant, but the service does this.
        gca_predict_response.predictions.append(
            _TEST_TEXT_GENERATION_PREDICTION_GROUNDING
        )
        gca_predict_response.predictions.append(
            _TEST_TEXT_GENERATION_PREDICTION_GROUNDING
        )

        test_grounding_sources = [
            _TEST_GROUNDING_WEB_SEARCH,
            _TEST_GROUNDING_VERTEX_AI_SEARCH_DATASTORE,
        ]
        datastore_path = (
            "projects/test-project/locations/global/"
            "collections/default_collection/dataStores/test_datastore"
        )
        expected_grounding_sources = [
            {"sources": [{"type": "WEB"}]},
            {
                "sources": [
                    {
                        "type": "ENTERPRISE",
                        "enterpriseDatastore": datastore_path,
                    }
                ]
            },
        ]

        for test_grounding_source, expected_grounding_source in zip(
            test_grounding_sources, expected_grounding_sources
        ):
            with mock.patch.object(
                target=prediction_service_client.PredictionServiceClient,
                attribute="predict",
                return_value=gca_predict_response,
            ) as mock_predict:
                response = model.predict(
                    "What is the best recipe for banana bread? Recipe:",
                    candidate_count=2,
                    grounding_source=test_grounding_source,
                )
            prediction_parameters = mock_predict.call_args[1]["parameters"]
            assert prediction_parameters["candidateCount"] == 2
            assert prediction_parameters["groundingConfig"] == expected_grounding_source
            assert (
                response.text == _TEST_TEXT_GENERATION_PREDICTION_GROUNDING["content"]
            )
            assert len(response.candidates) == 2
            assert (
                response.candidates[0].text
                == _TEST_TEXT_GENERATION_PREDICTION_GROUNDING["content"]
            )
            assert (
                dataclasses.asdict(response.candidates[0].grounding_metadata)
                == _EXPECTED_PARSED_GROUNDING_METADATA
            )

    @pytest.mark.asyncio
    async def test_text_generation_async(self):
        """Tests the text generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.append(_TEST_TEXT_GENERATION_PREDICTION)

        with mock.patch.object(
            target=prediction_service_async_client.PredictionServiceAsyncClient,
            attribute="predict",
            return_value=gca_predict_response,
        ) as mock_predict:
            response = await model.predict_async(
                "What is the best recipe for banana bread? Recipe:",
                max_output_tokens=128,
                temperature=0.0,
                top_p=1.0,
                top_k=5,
                stop_sequences=["\n"],
            )

        prediction_parameters = mock_predict.call_args[1]["parameters"]
        assert prediction_parameters["maxDecodeSteps"] == 128
        assert prediction_parameters["temperature"] == 0.0
        assert prediction_parameters["topP"] == 1.0
        assert prediction_parameters["topK"] == 5
        assert prediction_parameters["stopSequences"] == ["\n"]
        assert response.text == _TEST_TEXT_GENERATION_PREDICTION["content"]

    @pytest.mark.asyncio
    async def test_text_generation_multiple_candidates_grounding_async(self):
        """Tests the text generation model with multiple candidates async with web grounding."""
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

        gca_predict_response = gca_prediction_service.PredictResponse()
        # Discrepancy between the number of `instances` and the number of `predictions`
        # is a violation of the prediction service invariant, but the service does this.
        gca_predict_response.predictions.append(
            _TEST_TEXT_GENERATION_PREDICTION_GROUNDING
        )

        test_grounding_sources = [
            _TEST_GROUNDING_WEB_SEARCH,
            _TEST_GROUNDING_VERTEX_AI_SEARCH_DATASTORE,
        ]
        datastore_path = (
            "projects/test-project/locations/global/"
            "collections/default_collection/dataStores/test_datastore"
        )
        expected_grounding_sources = [
            {"sources": [{"type": "WEB"}]},
            {
                "sources": [
                    {
                        "type": "ENTERPRISE",
                        "enterpriseDatastore": datastore_path,
                    }
                ]
            },
        ]

        for test_grounding_source, expected_grounding_source in zip(
            test_grounding_sources, expected_grounding_sources
        ):
            with mock.patch.object(
                target=prediction_service_async_client.PredictionServiceAsyncClient,
                attribute="predict",
                return_value=gca_predict_response,
            ) as mock_predict:
                response = await model.predict_async(
                    "What is the best recipe for banana bread? Recipe:",
                    max_output_tokens=128,
                    temperature=0.0,
                    top_p=1.0,
                    top_k=5,
                    stop_sequences=["\n"],
                    grounding_source=test_grounding_source,
                )
            prediction_parameters = mock_predict.call_args[1]["parameters"]
            assert prediction_parameters["maxDecodeSteps"] == 128
            assert prediction_parameters["temperature"] == 0.0
            assert prediction_parameters["topP"] == 1.0
            assert prediction_parameters["topK"] == 5
            assert prediction_parameters["stopSequences"] == ["\n"]
            assert prediction_parameters["groundingConfig"] == expected_grounding_source
            assert (
                response.text == _TEST_TEXT_GENERATION_PREDICTION_GROUNDING["content"]
            )
            assert (
                dataclasses.asdict(response.grounding_metadata)
                == _EXPECTED_PARSED_GROUNDING_METADATA
            )

    def test_text_generation_model_predict_streaming(self):
        """Tests the TextGenerationModel.predict_streaming method."""
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

        response_generator = (
            gca_prediction_service.StreamingPredictResponse(
                outputs=[_streaming_prediction.value_to_tensor(response_dict)]
            )
            for response_dict in _TEST_TEXT_GENERATION_PREDICTION_STREAMING
        )

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="server_streaming_predict",
            return_value=response_generator,
        ):
            for response in model.predict_streaming(
                "Count to 50",
                max_output_tokens=1000,
                temperature=0.0,
                top_p=1.0,
                top_k=5,
                stop_sequences=["# %%"],
            ):
                assert len(response.text) > 10

    @pytest.mark.asyncio
    async def test_text_generation_model_predict_streaming_async(self):
        """Tests the TextGenerationModel.predict_streaming_async method."""
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

        async def mock_server_streaming_predict_async_iter(*args, **kwargs):
            for response_dict in _TEST_TEXT_GENERATION_PREDICTION_STREAMING:
                yield gca_prediction_service.StreamingPredictResponse(
                    outputs=[_streaming_prediction.value_to_tensor(response_dict)]
                )

        async def mock_server_streaming_predict_async(*args, **kwargs):
            return mock_server_streaming_predict_async_iter(*args, **kwargs)

        with mock.patch.object(
            target=prediction_service_async_client.PredictionServiceAsyncClient,
            attribute="server_streaming_predict",
            new=mock_server_streaming_predict_async,
        ):
            async for response in model.predict_streaming_async(
                "Count to 50",
                max_output_tokens=1000,
                temperature=0.0,
                top_p=1.0,
                top_k=5,
                stop_sequences=["# %%"],
            ):
                assert len(response.text) > 10

    def test_text_generation_response_repr(self):
        response = language_models.TextGenerationResponse(
            text="",
            is_blocked=True,
            safety_attributes={"Violent": 0.1},
            _prediction_response=None,
        )
        response_repr = repr(response)
        assert "blocked" in response_repr
        assert "Violent" in response_repr

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize(
        "mock_request_urlopen",
        ["https://us-central1-kfp.pkg.dev/proj/repo/pack/latest"],
        indirect=True,
    )
    def test_tune_text_generation_model(
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
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = preview_language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

            tuning_job_location = "europe-west4"
            evaluation_data_uri = "gs://bucket/eval.jsonl"
            evaluation_interval = 37
            enable_early_stopping = True
            tensorboard_name = f"projects/{_TEST_PROJECT}/locations/{tuning_job_location}/tensorboards/123"

            tuning_job = model.tune_model(
                training_data=_TEST_TEXT_BISON_TRAINING_DF,
                tuning_job_location=tuning_job_location,
                tuned_model_location="us-central1",
                learning_rate=0.1,
                learning_rate_multiplier=2.0,
                train_steps=10,
                tuning_evaluation_spec=preview_language_models.TuningEvaluationSpec(
                    evaluation_data=evaluation_data_uri,
                    evaluation_interval=evaluation_interval,
                    enable_early_stopping=enable_early_stopping,
                    tensorboard=tensorboard_name,
                ),
                accelerator_type="TPU",
            )
            call_kwargs = mock_pipeline_service_create.call_args[1]
            pipeline_arguments = call_kwargs[
                "pipeline_job"
            ].runtime_config.parameter_values
            assert pipeline_arguments["learning_rate"] == 0.1
            assert pipeline_arguments["learning_rate_multiplier"] == 2.0
            assert pipeline_arguments["train_steps"] == 10
            assert pipeline_arguments["evaluation_data_uri"] == evaluation_data_uri
            assert pipeline_arguments["evaluation_interval"] == evaluation_interval
            assert pipeline_arguments["enable_early_stopping"] == enable_early_stopping
            assert pipeline_arguments["tensorboard_resource_id"] == tensorboard_name
            assert pipeline_arguments["large_model_reference"] == "text-bison@001"
            assert pipeline_arguments["accelerator_type"] == "TPU"
            assert (
                call_kwargs["pipeline_job"].encryption_spec.kms_key_name
                == _TEST_ENCRYPTION_KEY_NAME
            )

            # Testing the tuned model
            tuned_model = tuning_job.get_tuned_model()
            assert (
                tuned_model._endpoint_name
                == test_constants.EndpointConstants._TEST_ENDPOINT_NAME
            )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize(
        "mock_request_urlopen",
        ["https://us-central1-kfp.pkg.dev/proj/repo/pack/latest"],
        indirect=True,
    )
    def test_tune_text_generation_model_ga(
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
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

            tuning_job_location = "europe-west4"
            evaluation_data_uri = "gs://bucket/eval.jsonl"
            evaluation_interval = 37
            enable_early_stopping = True
            tensorboard_name = f"projects/{_TEST_PROJECT}/locations/{tuning_job_location}/tensorboards/123"

            tuning_job = model.tune_model(
                training_data=_TEST_TEXT_BISON_TRAINING_DF,
                tuning_job_location=tuning_job_location,
                tuned_model_location="us-central1",
                learning_rate_multiplier=2.0,
                train_steps=10,
                tuning_evaluation_spec=preview_language_models.TuningEvaluationSpec(
                    evaluation_data=evaluation_data_uri,
                    evaluation_interval=evaluation_interval,
                    enable_early_stopping=enable_early_stopping,
                    tensorboard=tensorboard_name,
                ),
                accelerator_type="TPU",
            )
            call_kwargs = mock_pipeline_service_create.call_args[1]
            pipeline_arguments = call_kwargs[
                "pipeline_job"
            ].runtime_config.parameter_values
            assert pipeline_arguments["learning_rate_multiplier"] == 2.0
            assert pipeline_arguments["train_steps"] == 10
            assert pipeline_arguments["evaluation_data_uri"] == evaluation_data_uri
            assert pipeline_arguments["evaluation_interval"] == evaluation_interval
            assert pipeline_arguments["enable_early_stopping"] == enable_early_stopping
            assert pipeline_arguments["tensorboard_resource_id"] == tensorboard_name
            assert pipeline_arguments["large_model_reference"] == "text-bison@001"
            assert pipeline_arguments["accelerator_type"] == "TPU"
            assert (
                call_kwargs["pipeline_job"].encryption_spec.kms_key_name
                == _TEST_ENCRYPTION_KEY_NAME
            )

            # Testing the tuned model
            tuned_model = tuning_job.get_tuned_model()
            assert (
                tuned_model._endpoint_name
                == test_constants.EndpointConstants._TEST_ENDPOINT_NAME
            )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON],
    )
    @pytest.mark.parametrize(
        "mock_request_urlopen",
        ["https://us-central1-kfp.pkg.dev/proj/repo/pack/latest"],
        indirect=True,
    )
    def test_tune_text_generation_model_evaluation_with_only_tensorboard(
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
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

            tuning_job_location = "europe-west4"
            tensorboard_name = f"projects/{_TEST_PROJECT}/locations/{tuning_job_location}/tensorboards/123"

            model.tune_model(
                training_data=_TEST_TEXT_BISON_TRAINING_DF,
                tuning_job_location=tuning_job_location,
                tuned_model_location="us-central1",
                tuning_evaluation_spec=preview_language_models.TuningEvaluationSpec(
                    tensorboard=tensorboard_name,
                ),
            )
            call_kwargs = mock_pipeline_service_create.call_args[1]
            pipeline_arguments = call_kwargs[
                "pipeline_job"
            ].runtime_config.parameter_values
            assert pipeline_arguments["tensorboard_resource_id"] == tensorboard_name

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON],
    )
    @pytest.mark.parametrize(
        "mock_request_urlopen",
        ["https://us-central1-kfp.pkg.dev/proj/repo/pack/latest"],
        indirect=True,
    )
    def test_tune_text_generation_model_staging_bucket(
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
        """Tests that tune_model respects staging_bucket."""
        TEST_STAGING_BUCKET = "gs://test_staging_bucket/path/"
        aiplatform.init(staging_bucket=TEST_STAGING_BUCKET)

        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

            model.tune_model(
                training_data=_TEST_TEXT_BISON_TRAINING_DF,
                tuning_job_location="europe-west4",
                tuned_model_location="us-central1",
            )
            call_kwargs = mock_pipeline_service_create.call_args[1]
            pipeline_arguments = call_kwargs[
                "pipeline_job"
            ].runtime_config.parameter_values
            assert pipeline_arguments["dataset_uri"].startswith(TEST_STAGING_BUCKET)

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON],
    )
    @pytest.mark.parametrize(
        "mock_request_urlopen",
        ["https://us-central1-kfp.pkg.dev/proj/repo/pack/latest"],
        indirect=True,
    )
    def test_tune_chat_model(
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
        """Tests tuning a chat model."""
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.ChatModel.from_pretrained("chat-bison@001")

            default_context = "Default context"
            tuning_job = model.tune_model(
                training_data=_TEST_TEXT_BISON_TRAINING_DF,
                tuning_job_location="europe-west4",
                tuned_model_location="us-central1",
                default_context=default_context,
                accelerator_type="TPU",
            )
            call_kwargs = mock_pipeline_service_create.call_args[1]
            pipeline_arguments = call_kwargs[
                "pipeline_job"
            ].runtime_config.parameter_values
            assert pipeline_arguments["large_model_reference"] == "chat-bison@001"
            assert pipeline_arguments["default_context"] == default_context
            assert pipeline_arguments["accelerator_type"] == "TPU"

            # Testing the tuned model
            tuned_model = tuning_job.get_tuned_model()
            assert (
                tuned_model._endpoint_name
                == test_constants.EndpointConstants._TEST_ENDPOINT_NAME
            )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON],
    )
    @pytest.mark.parametrize(
        "mock_request_urlopen",
        ["https://us-central1-kfp.pkg.dev/proj/repo/pack/latest"],
        indirect=True,
    )
    def test_tune_code_generation_model(
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
        """Tests tuning a code generation model."""
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CODE_GENERATION_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = preview_language_models.CodeGenerationModel.from_pretrained(
                "code-bison@001"
            )
            # The tune_model call needs to be inside the PublisherModel mock
            # since it gets a new PublisherModel when tuning completes.
            model.tune_model(
                training_data=_TEST_TEXT_BISON_TRAINING_DF,
                tuning_job_location="europe-west4",
                tuned_model_location="us-central1",
                accelerator_type="TPU",
            )
            call_kwargs = mock_pipeline_service_create.call_args[1]
            pipeline_arguments = call_kwargs[
                "pipeline_job"
            ].runtime_config.parameter_values
            assert pipeline_arguments["large_model_reference"] == "code-bison@001"
            assert pipeline_arguments["accelerator_type"] == "TPU"

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON],
    )
    @pytest.mark.parametrize(
        "mock_request_urlopen",
        ["https://us-central1-kfp.pkg.dev/proj/repo/pack/latest"],
        indirect=True,
    )
    def test_tune_code_chat_model(
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
        """Tests tuning a code chat model."""
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CODECHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.CodeChatModel.from_pretrained("codechat-bison@001")

            # The tune_model call needs to be inside the PublisherModel mock
            # since it gets a new PublisherModel when tuning completes.
            model.tune_model(
                training_data=_TEST_TEXT_BISON_TRAINING_DF,
                tuning_job_location="europe-west4",
                tuned_model_location="us-central1",
                accelerator_type="TPU",
            )
            call_kwargs = mock_pipeline_service_create.call_args[1]
            pipeline_arguments = call_kwargs[
                "pipeline_job"
            ].runtime_config.parameter_values
            assert pipeline_arguments["large_model_reference"] == "codechat-bison@001"
            assert pipeline_arguments["accelerator_type"] == "TPU"

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
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            tuned_model = preview_language_models.TextGenerationModel.get_tuned_model(
                test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
            )

            assert (
                tuned_model._model_resource_name
                == test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
            )

    @pytest.mark.usefixtures(
        "get_model_mock",
    )
    def get_tuned_model_raises_if_not_called_with_mg_model(self):
        """Tests getting a tuned model raises if not called with a Model trained from Model Garden."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        with pytest.raises(ValueError):
            preview_language_models.TextGenerationModel.get_tuned_model(
                test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
            )

    def test_chat(self):
        """Tests the chat generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = preview_language_models.ChatModel.from_pretrained("chat-bison@001")

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
                preview_language_models.InputOutputTextPair(
                    input_text="Who do you work for?",
                    output_text="I work for Ned.",
                ),
                preview_language_models.InputOutputTextPair(
                    input_text="What do I like?",
                    output_text="Ned likes watching movies.",
                ),
            ],
            message_history=[
                preview_language_models.ChatMessage(
                    author=preview_language_models.ChatSession.USER_AUTHOR,
                    content="Question 1?",
                ),
                preview_language_models.ChatMessage(
                    author=preview_language_models.ChatSession.MODEL_AUTHOR,
                    content="Answer 1.",
                ),
            ],
            temperature=0.0,
        )

        gca_predict_response1 = gca_prediction_service.PredictResponse()
        gca_predict_response1.predictions.append(_TEST_CHAT_GENERATION_PREDICTION1)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response1,
        ):
            message_text1 = "Are my favorite movies based on a book series?"
            expected_response1 = _TEST_CHAT_GENERATION_PREDICTION1["candidates"][0][
                "content"
            ]
            response = chat.send_message(message_text1)
            assert response.text == expected_response1
            assert len(chat.message_history) == 4
            assert chat.message_history[2].author == chat.USER_AUTHOR
            assert chat.message_history[2].content == message_text1
            assert chat.message_history[3].author == chat.MODEL_AUTHOR
            assert chat.message_history[3].content == expected_response1

        gca_predict_response2 = gca_prediction_service.PredictResponse()
        gca_predict_response2.predictions.append(_TEST_CHAT_GENERATION_PREDICTION2)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response2,
        ):
            message_text2 = "When were these books published?"
            expected_response2 = _TEST_CHAT_GENERATION_PREDICTION2["candidates"][0][
                "content"
            ]
            response = chat.send_message(message_text2, temperature=0.1)
            assert response.text == expected_response2
            assert len(chat.message_history) == 6
            assert chat.message_history[4].author == chat.USER_AUTHOR
            assert chat.message_history[4].content == message_text2
            assert chat.message_history[5].author == chat.MODEL_AUTHOR
            assert chat.message_history[5].content == expected_response2

        # Validating the parameters
        chat_temperature = 0.1
        chat_max_output_tokens = 100
        chat_top_k = 1
        chat_top_p = 0.1
        message_temperature = 0.2
        message_max_output_tokens = 200
        message_top_k = 2
        message_top_p = 0.2

        chat2 = model.start_chat(
            temperature=chat_temperature,
            max_output_tokens=chat_max_output_tokens,
            top_k=chat_top_k,
            top_p=chat_top_p,
        )

        gca_predict_response3 = gca_prediction_service.PredictResponse()
        gca_predict_response3.predictions.append(_TEST_CHAT_GENERATION_PREDICTION1)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response3,
        ) as mock_predict3:
            chat2.send_message("Are my favorite movies based on a book series?")
            prediction_parameters = mock_predict3.call_args[1]["parameters"]
            assert prediction_parameters["temperature"] == chat_temperature
            assert prediction_parameters["maxDecodeSteps"] == chat_max_output_tokens
            assert prediction_parameters["topK"] == chat_top_k
            assert prediction_parameters["topP"] == chat_top_p

            chat2.send_message(
                "Are my favorite movies based on a book series?",
                temperature=message_temperature,
                max_output_tokens=message_max_output_tokens,
                top_k=message_top_k,
                top_p=message_top_p,
            )
            prediction_parameters = mock_predict3.call_args[1]["parameters"]
            assert prediction_parameters["temperature"] == message_temperature
            assert prediction_parameters["maxDecodeSteps"] == message_max_output_tokens
            assert prediction_parameters["topK"] == message_top_k
            assert prediction_parameters["topP"] == message_top_p

    def test_chat_ga(self):
        """Tests the chat generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.ChatModel.from_pretrained("chat-bison@001")

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
            message_history=[
                language_models.ChatMessage(
                    author=preview_language_models.ChatSession.USER_AUTHOR,
                    content="Question 1?",
                ),
                language_models.ChatMessage(
                    author=preview_language_models.ChatSession.MODEL_AUTHOR,
                    content="Answer 1.",
                ),
            ],
            temperature=0.0,
        )

        gca_predict_response1 = gca_prediction_service.PredictResponse()
        gca_predict_response1.predictions.append(_TEST_CHAT_GENERATION_PREDICTION1)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response1,
        ):
            message_text1 = "Are my favorite movies based on a book series?"
            expected_response1 = _TEST_CHAT_GENERATION_PREDICTION1["candidates"][0][
                "content"
            ]
            response = chat.send_message(message_text1)
            assert response.text == expected_response1
            assert len(chat.message_history) == 4
            assert chat.message_history[2].author == chat.USER_AUTHOR
            assert chat.message_history[2].content == message_text1
            assert chat.message_history[3].author == chat.MODEL_AUTHOR
            assert chat.message_history[3].content == expected_response1

        gca_predict_response2 = gca_prediction_service.PredictResponse()
        gca_predict_response2.predictions.append(_TEST_CHAT_GENERATION_PREDICTION2)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response2,
        ):
            message_text2 = "When were these books published?"
            expected_response2 = _TEST_CHAT_GENERATION_PREDICTION2["candidates"][0][
                "content"
            ]
            response = chat.send_message(message_text2, temperature=0.1)
            assert response.text == expected_response2
            assert len(chat.message_history) == 6
            assert chat.message_history[4].author == chat.USER_AUTHOR
            assert chat.message_history[4].content == message_text2
            assert chat.message_history[5].author == chat.MODEL_AUTHOR
            assert chat.message_history[5].content == expected_response2

        # Validating the parameters
        chat_temperature = 0.1
        chat_max_output_tokens = 100
        chat_top_k = 1
        chat_top_p = 0.1
        stop_sequences = ["\n"]
        message_temperature = 0.2
        message_max_output_tokens = 200
        message_top_k = 2
        message_top_p = 0.2
        message_stop_sequences = ["# %%"]

        chat2 = model.start_chat(
            temperature=chat_temperature,
            max_output_tokens=chat_max_output_tokens,
            top_k=chat_top_k,
            top_p=chat_top_p,
            stop_sequences=stop_sequences,
        )

        gca_predict_response3 = gca_prediction_service.PredictResponse()
        gca_predict_response3.predictions.append(_TEST_CHAT_GENERATION_PREDICTION1)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response3,
        ) as mock_predict3:
            chat2.send_message("Are my favorite movies based on a book series?")
            prediction_parameters = mock_predict3.call_args[1]["parameters"]
            assert prediction_parameters["temperature"] == chat_temperature
            assert prediction_parameters["maxDecodeSteps"] == chat_max_output_tokens
            assert prediction_parameters["topK"] == chat_top_k
            assert prediction_parameters["topP"] == chat_top_p
            assert prediction_parameters["stopSequences"] == stop_sequences

            chat2.send_message(
                "Are my favorite movies based on a book series?",
                temperature=message_temperature,
                max_output_tokens=message_max_output_tokens,
                top_k=message_top_k,
                top_p=message_top_p,
                stop_sequences=message_stop_sequences,
            )
            prediction_parameters = mock_predict3.call_args[1]["parameters"]
            assert prediction_parameters["temperature"] == message_temperature
            assert prediction_parameters["maxDecodeSteps"] == message_max_output_tokens
            assert prediction_parameters["topK"] == message_top_k
            assert prediction_parameters["topP"] == message_top_p
            assert prediction_parameters["stopSequences"] == message_stop_sequences

    def test_chat_model_send_message_with_multiple_candidates(self):
        """Tests the chat generation model with multiple candidates."""

        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.ChatModel.from_pretrained("chat-bison@001")

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/chat-bison@001", retry=base._DEFAULT_RETRY
        )

        chat = model.start_chat()

        gca_predict_response1 = gca_prediction_service.PredictResponse()
        gca_predict_response1.predictions.append(
            _TEST_CHAT_GENERATION_MULTI_CANDIDATE_PREDICTION
        )

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response1,
        ):
            message_text1 = "Are my favorite movies based on a book series?"
            expected_response_candidates = (
                _TEST_CHAT_GENERATION_MULTI_CANDIDATE_PREDICTION["candidates"]
            )
            expected_candidate_0 = expected_response_candidates[0]["content"]
            expected_candidate_1 = expected_response_candidates[1]["content"]

            response = chat.send_message(message_text1, candidate_count=2)
            assert response.text == expected_candidate_0
            assert len(response.candidates) == 2
            assert response.candidates[0].text == expected_candidate_0
            assert response.candidates[1].text == expected_candidate_1

            assert len(chat.message_history) == 2
            assert chat.message_history[0].author == chat.USER_AUTHOR
            assert chat.message_history[0].content == message_text1
            assert chat.message_history[1].author == chat.MODEL_AUTHOR
            assert chat.message_history[1].content == expected_candidate_0

    def test_chat_model_send_message_streaming(self):
        """Tests the chat generation model."""
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.ChatModel.from_pretrained("chat-bison@001")

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
            message_history=[
                language_models.ChatMessage(
                    author=preview_language_models.ChatSession.USER_AUTHOR,
                    content="Question 1?",
                ),
                language_models.ChatMessage(
                    author=preview_language_models.ChatSession.MODEL_AUTHOR,
                    content="Answer 1.",
                ),
            ],
            temperature=0.0,
            stop_sequences=["\n"],
        )

        # Using list instead of a generator so that it can be reused.
        response_generator = [
            gca_prediction_service.StreamingPredictResponse(
                outputs=[_streaming_prediction.value_to_tensor(response_dict)]
            )
            for response_dict in _TEST_CHAT_PREDICTION_STREAMING
        ]

        message_temperature = 0.2
        message_max_output_tokens = 200
        message_top_k = 2
        message_top_p = 0.2
        message_stop_sequences = ["# %%"]

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="server_streaming_predict",
            return_value=response_generator,
        ):
            message_text1 = "Are my favorite movies based on a book series?"

            for idx, response in enumerate(
                chat.send_message_streaming(
                    message=message_text1,
                    max_output_tokens=message_max_output_tokens,
                    temperature=message_temperature,
                    top_k=message_top_k,
                    top_p=message_top_p,
                    stop_sequences=message_stop_sequences,
                )
            ):
                assert len(response.text) > 10
                # New messages are not added until the response is fully read
                if idx + 1 < len(response_generator):
                    assert len(chat.message_history) == 2

        # New messages are only added after the response is fully read
        assert len(chat.message_history) == 4
        assert chat.message_history[2].author == chat.USER_AUTHOR
        assert chat.message_history[2].content == message_text1
        assert chat.message_history[3].author == chat.MODEL_AUTHOR

    def test_chat_model_preview_count_tokens(self):
        """Tests the text generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = preview_language_models.ChatModel.from_pretrained("chat-bison@001")

            chat = model.start_chat()
            assert isinstance(chat, preview_language_models.ChatSession)

        gca_count_tokens_response = gca_prediction_service_v1beta1.CountTokensResponse(
            total_tokens=_TEST_COUNT_TOKENS_RESPONSE["total_tokens"],
            total_billable_characters=_TEST_COUNT_TOKENS_RESPONSE[
                "total_billable_characters"
            ],
        )

        with mock.patch.object(
            target=prediction_service_client_v1beta1.PredictionServiceClient,
            attribute="count_tokens",
            return_value=gca_count_tokens_response,
        ):
            response = chat.count_tokens("What is the best recipe for banana bread?")

            assert response.total_tokens == _TEST_COUNT_TOKENS_RESPONSE["total_tokens"]
            assert (
                response.total_billable_characters
                == _TEST_COUNT_TOKENS_RESPONSE["total_billable_characters"]
            )

    def test_code_chat(self):
        """Tests the code chat model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CODECHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.CodeChatModel.from_pretrained(
                "google/codechat-bison@001"
            )

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/codechat-bison@001",
            retry=base._DEFAULT_RETRY,
        )

        code_chat = model.start_chat(
            context="We're working on large-scale production system.",
            max_output_tokens=128,
            temperature=0.2,
            stop_sequences=["\n"],
        )

        gca_predict_response1 = gca_prediction_service.PredictResponse()
        gca_predict_response1.predictions.append(_TEST_CHAT_GENERATION_PREDICTION1)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response1,
        ):
            response = code_chat.send_message("Hi, how are you?")
            assert (
                response.text
                == _TEST_CHAT_GENERATION_PREDICTION1["candidates"][0]["content"]
            )
            assert len(code_chat.message_history) == 2

        gca_predict_response2 = gca_prediction_service.PredictResponse()
        gca_predict_response2.predictions.append(_TEST_CHAT_GENERATION_PREDICTION2)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response2,
        ):
            response = code_chat.send_message(
                "Please help write a function to calculate the min of two numbers",
                temperature=0.2,
                max_output_tokens=256,
            )
            assert (
                response.text
                == _TEST_CHAT_GENERATION_PREDICTION2["candidates"][0]["content"]
            )
            assert len(code_chat.message_history) == 4

        # Validating the parameters
        chat_temperature = 0.1
        chat_max_output_tokens = 100
        chat_stop_sequences = ["\n"]
        message_temperature = 0.2
        message_max_output_tokens = 200
        message_stop_sequences = ["# %%"]

        code_chat2 = model.start_chat(
            temperature=chat_temperature,
            max_output_tokens=chat_max_output_tokens,
            stop_sequences=chat_stop_sequences,
        )

        gca_predict_response3 = gca_prediction_service.PredictResponse()
        gca_predict_response3.predictions.append(_TEST_CHAT_GENERATION_PREDICTION1)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response3,
        ) as mock_predict:
            code_chat2.send_message(
                "Please help write a function to calculate the min of two numbers"
            )
            prediction_parameters = mock_predict.call_args[1]["parameters"]
            assert prediction_parameters["temperature"] == chat_temperature
            assert prediction_parameters["maxDecodeSteps"] == chat_max_output_tokens
            assert prediction_parameters["stopSequences"] == chat_stop_sequences

            code_chat2.send_message(
                "Please help write a function to calculate the min of two numbers",
                temperature=message_temperature,
                max_output_tokens=message_max_output_tokens,
                stop_sequences=message_stop_sequences,
            )
            prediction_parameters = mock_predict.call_args[1]["parameters"]
            assert prediction_parameters["temperature"] == message_temperature
            assert prediction_parameters["maxDecodeSteps"] == message_max_output_tokens
            assert prediction_parameters["stopSequences"] == message_stop_sequences

    def test_code_chat_model_send_message_with_multiple_candidates(self):
        """Tests the code chat model with multiple candidates."""
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CODECHAT_BISON_PUBLISHER_MODEL_DICT
            ),
            autospec=True,
        ):
            model = language_models.CodeChatModel.from_pretrained(
                "google/codechat-bison@001"
            )

        chat = model.start_chat()

        gca_predict_response1 = gca_prediction_service.PredictResponse()
        gca_predict_response1.predictions.append(
            _TEST_CHAT_GENERATION_MULTI_CANDIDATE_PREDICTION
        )

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response1,
            autospec=True,
        ):
            message_text1 = "Are my favorite movies based on a book series?"
            expected_response_candidates = (
                _TEST_CHAT_GENERATION_MULTI_CANDIDATE_PREDICTION["candidates"]
            )
            expected_candidate_0 = expected_response_candidates[0]["content"]
            expected_candidate_1 = expected_response_candidates[1]["content"]

            response = chat.send_message(
                message=message_text1,
                # candidate_count acts as a maximum number, not exact number.
                candidate_count=7,
            )
            # The service can return a different number of candidates.
            assert response.text == expected_candidate_0
            assert len(response.candidates) == 2
            assert response.candidates[0].text == expected_candidate_0
            assert response.candidates[1].text == expected_candidate_1

            assert len(chat.message_history) == 2
            assert chat.message_history[0].author == chat.USER_AUTHOR
            assert chat.message_history[0].content == message_text1
            assert chat.message_history[1].author == chat.MODEL_AUTHOR
            assert chat.message_history[1].content == expected_candidate_0

    def test_code_chat_model_send_message_streaming(self):
        """Tests the chat generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CODECHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.CodeChatModel.from_pretrained("codechat-bison@001")

        chat = model.start_chat(temperature=0.0, stop_sequences=["\n"])

        # Using list instead of a generator so that it can be reused.
        response_generator = [
            gca_prediction_service.StreamingPredictResponse(
                outputs=[_streaming_prediction.value_to_tensor(response_dict)]
            )
            for response_dict in _TEST_CHAT_PREDICTION_STREAMING
        ]

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="server_streaming_predict",
            return_value=response_generator,
        ):
            message_text1 = (
                "Please help write a function to calculate the max of two numbers"
            )
            # New messages are not added until the response is fully read
            assert not chat.message_history
            for response in chat.send_message_streaming(message_text1):
                assert len(response.text) > 10
            # New messages are only added after the response is fully read
            assert chat.message_history

        assert len(chat.message_history) == 2
        assert chat.message_history[0].author == chat.USER_AUTHOR
        assert chat.message_history[0].content == message_text1
        assert chat.message_history[1].author == chat.MODEL_AUTHOR

    def test_code_chat_model_preview_count_tokens(self):
        """Tests the text generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CODECHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = preview_language_models.CodeChatModel.from_pretrained(
                "codechat-bison@001"
            )

            chat = model.start_chat()
            assert isinstance(chat, preview_language_models.CodeChatSession)

        gca_count_tokens_response = gca_prediction_service_v1beta1.CountTokensResponse(
            total_tokens=_TEST_COUNT_TOKENS_RESPONSE["total_tokens"],
            total_billable_characters=_TEST_COUNT_TOKENS_RESPONSE[
                "total_billable_characters"
            ],
        )

        with mock.patch.object(
            target=prediction_service_client_v1beta1.PredictionServiceClient,
            attribute="count_tokens",
            return_value=gca_count_tokens_response,
        ):
            response = chat.count_tokens("What is the best recipe for banana bread?")

            assert response.total_tokens == _TEST_COUNT_TOKENS_RESPONSE["total_tokens"]
            assert (
                response.total_billable_characters
                == _TEST_COUNT_TOKENS_RESPONSE["total_billable_characters"]
            )

    def test_code_generation(self):
        """Tests code generation with the code generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CODE_GENERATION_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.CodeGenerationModel.from_pretrained(
                "google/code-bison@001"
            )

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/code-bison@001",
            retry=base._DEFAULT_RETRY,
        )

        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.append(_TEST_CODE_GENERATION_PREDICTION)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            response = model.predict(
                prefix="Write a function that checks if a year is a leap year.",
                max_output_tokens=256,
                temperature=0.2,
            )
            assert response.text == _TEST_CODE_GENERATION_PREDICTION["content"]
            expected_safety_attributes_raw = _TEST_CODE_GENERATION_PREDICTION[
                "safetyAttributes"
            ]
            expected_safety_attributes = dict(
                zip(
                    expected_safety_attributes_raw["categories"],
                    expected_safety_attributes_raw["scores"],
                )
            )
            assert response.safety_attributes == expected_safety_attributes
            assert response.is_blocked == expected_safety_attributes_raw["blocked"]

        # Validating the parameters
        predict_temperature = 0.1
        predict_max_output_tokens = 100
        stop_sequences = ["\n"]

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ) as mock_predict:
            model.predict(
                prefix="Write a function that checks if a year is a leap year.",
                max_output_tokens=predict_max_output_tokens,
                temperature=predict_temperature,
                stop_sequences=stop_sequences,
            )
            prediction_parameters = mock_predict.call_args[1]["parameters"]
            assert prediction_parameters["temperature"] == predict_temperature
            assert prediction_parameters["maxOutputTokens"] == predict_max_output_tokens
            assert prediction_parameters["stopSequences"] == stop_sequences

            model.predict(
                prefix="Write a function that checks if a year is a leap year.",
            )
            prediction_parameters = mock_predict.call_args[1]["parameters"]
            assert "temperature" not in prediction_parameters
            assert "maxOutputTokens" not in prediction_parameters

    def test_code_generation_multiple_candidates(self):
        """Tests the code generation model with multiple candidates."""
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CODE_GENERATION_BISON_PUBLISHER_MODEL_DICT
            ),
            autospec=True,
        ):
            model = language_models.CodeGenerationModel.from_pretrained(
                "code-bison@001"
            )

        gca_predict_response = gca_prediction_service.PredictResponse()
        # Discrepancy between the number of `instances` and the number of `predictions`
        # is a violation of the prediction service invariant, but the service does this.
        gca_predict_response.predictions.append(_TEST_CODE_GENERATION_PREDICTION)
        gca_predict_response.predictions.append(_TEST_CODE_GENERATION_PREDICTION)
        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
            autospec=True,
        ) as mock_predict:
            response = model.predict(
                prefix="Write a function that checks if a year is a leap year.",
                # candidate_count acts as a maximum number, not exact number.
                candidate_count=7,
            )
        prediction_parameters = mock_predict.call_args[1]["parameters"]
        assert prediction_parameters["candidateCount"] == 7

        assert response.text == _TEST_CODE_GENERATION_PREDICTION["content"]
        # The service can return a different number of candidates.
        assert len(response.candidates) == 2
        assert (
            response.candidates[0].text == _TEST_CODE_GENERATION_PREDICTION["content"]
        )

    def test_code_generation_preview_count_tokens(self):
        """Tests the count_tokens method in CodeGenerationModel."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CODE_COMPLETION_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = preview_language_models.CodeGenerationModel.from_pretrained(
                "code-gecko@001"
            )

        gca_count_tokens_response = gca_prediction_service_v1beta1.CountTokensResponse(
            total_tokens=_TEST_COUNT_TOKENS_RESPONSE["total_tokens"],
            total_billable_characters=_TEST_COUNT_TOKENS_RESPONSE[
                "total_billable_characters"
            ],
        )

        with mock.patch.object(
            target=prediction_service_client_v1beta1.PredictionServiceClient,
            attribute="count_tokens",
            return_value=gca_count_tokens_response,
        ):
            response = model.count_tokens("def reverse_string(s):")

            assert response.total_tokens == _TEST_COUNT_TOKENS_RESPONSE["total_tokens"]
            assert (
                response.total_billable_characters
                == _TEST_COUNT_TOKENS_RESPONSE["total_billable_characters"]
            )

    def test_code_completion(self):
        """Tests code completion with the code generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CODE_COMPLETION_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.CodeGenerationModel.from_pretrained(
                "google/code-gecko@001"
            )

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/code-gecko@001",
            retry=base._DEFAULT_RETRY,
        )

        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.append(_TEST_CODE_COMPLETION_PREDICTION)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            response = model.predict(
                prefix="def reverse_string(s):",
                max_output_tokens=128,
                temperature=0.2,
            )
            assert response.text == _TEST_CODE_COMPLETION_PREDICTION["content"]

        # Validating the parameters
        predict_temperature = 0.1
        predict_max_output_tokens = 100

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ) as mock_predict:
            model.predict(
                prefix="def reverse_string(s):",
                max_output_tokens=predict_max_output_tokens,
                temperature=predict_temperature,
            )
            prediction_parameters = mock_predict.call_args[1]["parameters"]
            assert prediction_parameters["temperature"] == predict_temperature
            assert prediction_parameters["maxOutputTokens"] == predict_max_output_tokens

            model.predict(
                prefix="def reverse_string(s):",
            )
            prediction_parameters = mock_predict.call_args[1]["parameters"]
            assert "temperature" not in prediction_parameters
            assert "maxOutputTokens" not in prediction_parameters

    def test_code_generation_model_predict_streaming(self):
        """Tests the TextGenerationModel.predict_streaming method."""
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CODE_GENERATION_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.CodeGenerationModel.from_pretrained(
                "code-bison@001"
            )

        response_generator = (
            gca_prediction_service.StreamingPredictResponse(
                outputs=[_streaming_prediction.value_to_tensor(response_dict)]
            )
            for response_dict in _TEST_TEXT_GENERATION_PREDICTION_STREAMING
        )

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="server_streaming_predict",
            return_value=response_generator,
        ):
            for response in model.predict_streaming(
                prefix="def reverse_string(s):",
                suffix="    return s",
                max_output_tokens=1000,
                temperature=0.0,
            ):
                assert len(response.text) > 10

    def test_text_embedding(self):
        """Tests the text embedding model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_EMBEDDING_GECKO_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = preview_language_models.TextEmbeddingModel.from_pretrained(
                "textembedding-gecko@001"
            )

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/textembedding-gecko@001",
            retry=base._DEFAULT_RETRY,
        )

        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.append(_TEST_TEXT_EMBEDDING_PREDICTION)
        gca_predict_response.predictions.append(_TEST_TEXT_EMBEDDING_PREDICTION)

        expected_embedding = _TEST_TEXT_EMBEDDING_PREDICTION["embeddings"]
        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ) as mock_predict:
            embeddings = model.get_embeddings(
                [
                    "What is life?",
                    language_models.TextEmbeddingInput(
                        text="Foo",
                        task_type="RETRIEVAL_DOCUMENT",
                        title="Bar",
                    ),
                    language_models.TextEmbeddingInput(
                        text="Baz",
                        task_type="CLASSIFICATION",
                    ),
                ],
                auto_truncate=False,
            )
            prediction_instances = mock_predict.call_args[1]["instances"]
            assert prediction_instances == [
                {"content": "What is life?"},
                {
                    "content": "Foo",
                    "task_type": "RETRIEVAL_DOCUMENT",
                    "title": "Bar",
                },
                {
                    "content": "Baz",
                    "task_type": "CLASSIFICATION",
                },
            ]
            prediction_parameters = mock_predict.call_args[1]["parameters"]
            assert not prediction_parameters["autoTruncate"]
            assert embeddings
            for embedding in embeddings:
                vector = embedding.values
                assert len(vector) == _TEXT_EMBEDDING_VECTOR_LENGTH
                assert vector == expected_embedding["values"]
                assert (
                    embedding.statistics.token_count
                    == expected_embedding["statistics"]["token_count"]
                )
                assert (
                    embedding.statistics.truncated
                    == expected_embedding["statistics"]["truncated"]
                )

    def test_text_embedding_preview_count_tokens(self):
        """Tests the text embedding model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_EMBEDDING_GECKO_PUBLISHER_MODEL_DICT
            ),
        ):
            model = preview_language_models.TextEmbeddingModel.from_pretrained(
                "textembedding-gecko@001"
            )

            gca_count_tokens_response = (
                gca_prediction_service_v1beta1.CountTokensResponse(
                    total_tokens=_TEST_COUNT_TOKENS_RESPONSE["total_tokens"],
                    total_billable_characters=_TEST_COUNT_TOKENS_RESPONSE[
                        "total_billable_characters"
                    ],
                )
            )

            with mock.patch.object(
                target=prediction_service_client_v1beta1.PredictionServiceClient,
                attribute="count_tokens",
                return_value=gca_count_tokens_response,
            ):
                response = model.count_tokens(["What is life?"])

                assert (
                    response.total_tokens == _TEST_COUNT_TOKENS_RESPONSE["total_tokens"]
                )
                assert (
                    response.total_billable_characters
                    == _TEST_COUNT_TOKENS_RESPONSE["total_billable_characters"]
                )

    def test_text_embedding_ga(self):
        """Tests the text embedding model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_EMBEDDING_GECKO_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.TextEmbeddingModel.from_pretrained(
                "textembedding-gecko@001"
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

    def test_batch_prediction(
        self,
        get_endpoint_mock,
    ):
        """Tests batch prediction."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

        with mock.patch.object(
            target=aiplatform.BatchPredictionJob,
            attribute="create",
        ) as mock_create:
            model.batch_predict(
                dataset="gs://test-bucket/test_table.jsonl",
                destination_uri_prefix="gs://test-bucket/results/",
                model_parameters={"temperature": 0.1},
            )
            mock_create.assert_called_once_with(
                model_name=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/publishers/google/models/text-bison@001",
                job_display_name=None,
                gcs_source="gs://test-bucket/test_table.jsonl",
                gcs_destination_prefix="gs://test-bucket/results/",
                model_parameters={"temperature": 0.1},
            )

        # Testing tuned model batch prediction
        tuned_model = language_models.TextGenerationModel(
            model_id=model._model_id,
            endpoint_name=test_constants.EndpointConstants._TEST_ENDPOINT_NAME,
        )
        with mock.patch.object(
            target=aiplatform.BatchPredictionJob,
            attribute="create",
        ) as mock_create:
            tuned_model.batch_predict(
                dataset="gs://test-bucket/test_table.jsonl",
                destination_uri_prefix="gs://test-bucket/results/",
                model_parameters={"temperature": 0.1},
            )
            mock_create.assert_called_once_with(
                model_name=test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME,
                job_display_name=None,
                gcs_source="gs://test-bucket/test_table.jsonl",
                gcs_destination_prefix="gs://test-bucket/results/",
                model_parameters={"temperature": 0.1},
            )

    def test_batch_prediction_for_text_embedding(self):
        """Tests batch prediction."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_EMBEDDING_GECKO_PUBLISHER_MODEL_DICT
            ),
        ):
            model = preview_language_models.TextEmbeddingModel.from_pretrained(
                "textembedding-gecko@001"
            )

        with mock.patch.object(
            target=aiplatform.BatchPredictionJob,
            attribute="create",
        ) as mock_create:
            model.batch_predict(
                dataset="gs://test-bucket/test_table.jsonl",
                destination_uri_prefix="gs://test-bucket/results/",
                model_parameters={},
            )
            mock_create.assert_called_once_with(
                model_name=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/publishers/google/models/textembedding-gecko@001",
                job_display_name=None,
                gcs_source="gs://test-bucket/test_table.jsonl",
                gcs_destination_prefix="gs://test-bucket/results/",
                model_parameters={},
            )

    def test_text_generation_top_level_from_pretrained_preview(self):
        """Tests the text generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = vertexai.preview.from_pretrained(
                foundation_model_name="text-bison@001"
            )

            assert isinstance(model, preview_language_models.TextGenerationModel)

        mock_get_publisher_model.assert_called_with(
            name="publishers/google/models/text-bison@001", retry=base._DEFAULT_RETRY
        )
        assert mock_get_publisher_model.call_count == 1

        assert (
            model._model_resource_name
            == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/publishers/google/models/text-bison@001"
        )

        # Test that methods on TextGenerationModel still work as expected
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
                temperature=0.0,
                top_p=1.0,
                top_k=5,
            )

        assert response.text == _TEST_TEXT_GENERATION_PREDICTION["content"]
        assert (
            response.raw_prediction_response.predictions[0]
            == _TEST_TEXT_GENERATION_PREDICTION
        )
        assert (
            response.safety_attributes["Violent"]
            == _TEST_TEXT_GENERATION_PREDICTION["safetyAttributes"]["scores"][0]
        )

    def test_text_embedding_top_level_from_pretrained_preview(self):
        """Tests the text embedding model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_EMBEDDING_GECKO_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = vertexai.preview.from_pretrained(
                foundation_model_name="textembedding-gecko@001"
            )

            assert isinstance(model, preview_language_models.TextEmbeddingModel)

            assert (
                model._endpoint_name
                == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/publishers/google/models/textembedding-gecko@001"
            )

        mock_get_publisher_model.assert_called_with(
            name="publishers/google/models/textembedding-gecko@001",
            retry=base._DEFAULT_RETRY,
        )

        assert mock_get_publisher_model.call_count == 1


# TODO (b/285946649): add more test coverage before public preview release
@pytest.mark.usefixtures("google_auth_mock")
class TestLanguageModelEvaluation:
    @pytest.mark.usefixtures(
        "get_model_with_tuned_version_label_mock",
        "get_endpoint_with_models_mock",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_EVAL_PIPELINE_SPEC_JSON, _TEST_EVAL_PIPELINE_JOB],
    )
    @pytest.mark.parametrize(
        "mock_request_urlopen_eval",
        ["https://us-kfp.pkg.dev/proj/repo/pack/latest"],
        indirect=True,
    )
    def test_model_evaluation_text_generation_task_with_gcs_input(
        self,
        job_spec,
        mock_pipeline_service_create_eval,
        mock_pipeline_job_get_eval,
        mock_successfully_completed_eval_job,
        mock_pipeline_bucket_exists,
        mock_load_yaml_and_json,
        mock_request_urlopen_eval,
    ):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):

            my_model = preview_language_models.TextGenerationModel.get_tuned_model(
                test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
            )

            eval_metrics = my_model.evaluate(
                task_spec=preview_language_models.EvaluationTextGenerationSpec(
                    ground_truth_data="gs://my-bucket/ground-truth.jsonl",
                ),
            )

            assert isinstance(eval_metrics, preview_language_models.EvaluationMetric)
            assert eval_metrics.bleu == _TEST_TEXT_GENERATION_METRICS["bleu"]

    @pytest.mark.usefixtures(
        "get_model_with_tuned_version_label_mock",
        "get_endpoint_with_models_mock",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_EVAL_PIPELINE_SPEC_JSON, _TEST_EVAL_PIPELINE_JOB],
    )
    def test_populate_eval_template_params(
        self,
        job_spec,
        mock_pipeline_service_create,
        mock_model_evaluate,
        mock_pipeline_job_get,
        mock_successfully_completed_eval_job,
        mock_pipeline_bucket_exists,
        mock_load_yaml_and_json,
    ):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):

            my_model = preview_language_models.TextGenerationModel.get_tuned_model(
                test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
            )

            task_spec = preview_language_models.EvaluationTextGenerationSpec(
                ground_truth_data="gs://my-bucket/ground-truth.jsonl",
            )

            formatted_template_params = (
                _evaluatable_language_models._populate_eval_template_params(
                    task_spec=task_spec, model_name=my_model._model_resource_name
                )
            )

            assert (
                "batch_predict_gcs_destination_output_uri" in formatted_template_params
            )
            assert "model_name" in formatted_template_params
            assert "evaluation_task" in formatted_template_params

            # This should only be in the classification task pipeline template
            assert "evaluation_class_labels" not in formatted_template_params
            assert "target_column_name" not in formatted_template_params

    @pytest.mark.usefixtures(
        "get_model_with_tuned_version_label_mock",
        "get_endpoint_with_models_mock",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_EVAL_PIPELINE_SPEC_JSON, _TEST_EVAL_PIPELINE_JOB],
    )
    def test_populate_template_params_for_classification_task(
        self,
        job_spec,
        mock_pipeline_service_create,
        mock_model_evaluate,
        mock_pipeline_job_get,
        mock_successfully_completed_eval_job,
        mock_pipeline_bucket_exists,
        mock_load_yaml_and_json,
    ):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):

            my_model = preview_language_models.TextGenerationModel.get_tuned_model(
                test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
            )

            task_spec = preview_language_models.EvaluationTextClassificationSpec(
                ground_truth_data="gs://my-bucket/ground-truth.jsonl",
                target_column_name="test_targ_name",
                class_names=["test_class_name_1", "test_class_name_2"],
            )

            formatted_template_params = (
                _evaluatable_language_models._populate_eval_template_params(
                    task_spec=task_spec, model_name=my_model._model_resource_name
                )
            )

            assert "evaluation_class_labels" in formatted_template_params
            assert "target_field_name" in formatted_template_params

    @pytest.mark.usefixtures(
        "get_model_with_tuned_version_label_mock",
        "get_endpoint_with_models_mock",
        "mock_storage_blob_upload_from_filename",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_EVAL_PIPELINE_SPEC_JSON, _TEST_EVAL_PIPELINE_JOB],
    )
    def test_populate_template_params_with_dataframe_input(
        self,
        job_spec,
        mock_pipeline_service_create,
        mock_pipeline_job_get,
        mock_successfully_completed_eval_job,
        mock_pipeline_bucket_exists,
        mock_load_yaml_and_json,
    ):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):

            my_model = preview_language_models.TextGenerationModel.get_tuned_model(
                test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
            )

            task_spec = preview_language_models.EvaluationTextGenerationSpec(
                ground_truth_data=_TEST_EVAL_DATA_DF,
            )

            formatted_template_params = (
                _evaluatable_language_models._populate_eval_template_params(
                    task_spec=task_spec, model_name=my_model._model_resource_name
                )
            )

            # The utility method should not modify task_spec
            assert isinstance(task_spec.ground_truth_data, pd.DataFrame)

            assert (
                "batch_predict_gcs_destination_output_uri" in formatted_template_params
            )
            assert "model_name" in formatted_template_params
            assert "evaluation_task" in formatted_template_params

            # This should only be in the classification task pipeline template
            assert "evaluation_class_labels" not in formatted_template_params
            assert "target_column_name" not in formatted_template_params

    def test_evaluate_raises_on_ga_language_model(
        self,
    ):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            model = language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

            with pytest.raises(AttributeError):
                model.evaluate()

    @pytest.mark.usefixtures(
        "get_endpoint_with_models_mock",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_EVAL_PIPELINE_SPEC_JSON, _TEST_EVAL_PIPELINE_JOB],
    )
    @pytest.mark.parametrize(
        "mock_request_urlopen_eval",
        ["https://us-kfp.pkg.dev/proj/repo/pack/latest"],
        indirect=True,
    )
    def test_model_evaluation_text_generation_task_on_base_model(
        self,
        job_spec,
        mock_pipeline_service_create_eval,
        mock_pipeline_job_get_eval,
        mock_successfully_completed_eval_job,
        mock_pipeline_bucket_exists,
        mock_load_yaml_and_json,
        mock_request_urlopen_eval,
    ):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):

            my_model = preview_language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

            eval_metrics = my_model.evaluate(
                task_spec=preview_language_models.EvaluationTextGenerationSpec(
                    ground_truth_data="gs://my-bucket/ground-truth.jsonl",
                ),
            )

            assert isinstance(eval_metrics, preview_language_models.EvaluationMetric)

    @pytest.mark.usefixtures(
        "get_endpoint_with_models_mock",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_EVAL_CLASSIFICATION_PIPELINE_SPEC_JSON,
            _TEST_EVAL_CLASSIFICATION_PIPELINE_JOB,
        ],
    )
    @pytest.mark.parametrize(
        "mock_request_urlopen_eval_classification",
        ["https://us-central1-kfp.pkg.dev/proj/repo/pack/latest"],
        indirect=True,
    )
    def test_model_evaluation_text_classification_base_model_only_summary_metrics(
        self,
        job_spec,
        mock_pipeline_service_create_eval_classification,
        mock_pipeline_job_get_eval_classification,
        mock_successfully_completed_eval_classification_job,
        mock_pipeline_bucket_exists,
        mock_load_yaml_and_json,
        mock_request_urlopen_eval_classification,
    ):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            my_model = preview_language_models.TextGenerationModel.from_pretrained(
                "text-bison@001"
            )

            eval_metrics = my_model.evaluate(
                task_spec=preview_language_models.EvaluationTextClassificationSpec(
                    ground_truth_data="gs://my-bucket/ground-truth.jsonl",
                    target_column_name="test_targ_name",
                    class_names=["test_class_name_1", "test_class_name_2"],
                )
            )

            assert isinstance(
                eval_metrics,
                preview_language_models.EvaluationClassificationMetric,
            )
            assert eval_metrics.confidenceMetrics is None
            assert eval_metrics.auPrc == _TEST_TEXT_CLASSIFICATION_METRICS["auPrc"]
