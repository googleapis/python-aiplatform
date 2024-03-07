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

import importlib
import uuid

import pytest

from google import auth
from google.cloud import storage

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from tests.system.aiplatform import e2e_base

from google.cloud.aiplatform.compat.types import (
    pipeline_state as gca_pipeline_state,
)

_TEST_MODEL_EVAL_CLASS_LABELS = ["0", "1", "2"]
_TEST_TARGET_FIELD_NAME = "species"

_TEST_PROJECT = e2e_base._PROJECT
_TEST_LOCATION = e2e_base._LOCATION
_EVAL_METRICS_KEYS_CLASSIFICATION = [
    "auPrc",
    "auRoc",
    "logLoss",
    "confidenceMetrics",
    "confusionMatrix",
]


_TEST_XGB_CLASSIFICATION_MODEL_ID = "6336857145803276288"
_TEST_EVAL_DATA_URI = (
    "gs://cloud-samples-data-us-central1/vertex-ai/model-evaluation/iris_training.csv"
)
_TEST_PERMANENT_CUSTOM_MODEL_CLASSIFICATION_RESOURCE_NAME = f"projects/{_TEST_PROJECT}/locations/us-central1/models/{_TEST_XGB_CLASSIFICATION_MODEL_ID}"

_LOGGER = base.Logger(__name__)


@pytest.mark.usefixtures(
    "prepare_staging_bucket",
    "delete_staging_bucket",
    "tear_down_resources",
)
class TestModelEvaluationJob(e2e_base.TestEndToEnd):
    _temp_prefix = "temp_vertex_sdk_model_evaluation_test"

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    @pytest.fixture()
    def storage_client(self):
        yield storage.Client(project=_TEST_PROJECT)

    @pytest.fixture()
    def staging_bucket(self, storage_client):
        new_staging_bucket = f"temp-sdk-integration-{uuid.uuid4()}"
        bucket = storage_client.create_bucket(
            new_staging_bucket, location="us-central1"
        )

        yield bucket

    def test_model_evaluate_custom_tabular_model(self, staging_bucket, shared_state):
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=credentials,
        )

        custom_model = aiplatform.Model(
            model_name=_TEST_PERMANENT_CUSTOM_MODEL_CLASSIFICATION_RESOURCE_NAME
        )

        eval_job = custom_model.evaluate(
            gcs_source_uris=[_TEST_EVAL_DATA_URI],
            prediction_type="classification",
            class_labels=_TEST_MODEL_EVAL_CLASS_LABELS,
            target_field_name=_TEST_TARGET_FIELD_NAME,
            staging_bucket=f"gs://{staging_bucket.name}",
        )

        shared_state["resources"] = [eval_job.backing_pipeline_job]

        _LOGGER.info("%s, state before completion", eval_job.backing_pipeline_job.state)

        eval_job.wait()

        _LOGGER.info("%s, state after completion", eval_job.backing_pipeline_job.state)

        assert (
            eval_job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        assert eval_job.state == eval_job.backing_pipeline_job.state

        assert eval_job.resource_name == eval_job.backing_pipeline_job.resource_name

        model_eval = eval_job.get_model_evaluation()

        # ModelEvaluation.delete() has not been implemented yet
        # shared_state["resources"].append(model_eval)

        eval_metrics_dict = dict(model_eval.metrics)

        for metric_name in _EVAL_METRICS_KEYS_CLASSIFICATION:
            assert metric_name in eval_metrics_dict
