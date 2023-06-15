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

import pytest
from importlib import reload
from unittest import mock

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
import constants as test_constants

from google.cloud.aiplatform.compat.services import (
    model_garden_service_client_v1,
)

from google.cloud.aiplatform.compat.types import (
    publisher_model as gca_publisher_model,
)

from vertexai._model_garden import _model_garden_models

_TEXT_BISON_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/text-bison",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "launch_stage": gca_publisher_model.PublisherModel.LaunchStage.PUBLIC_PREVIEW,
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/text-bison@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/text_generation_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/text_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/text_generation_1.0.0.yaml",
    },
}


@pytest.mark.usefixtures("google_auth_mock")
class TestModelGardenModels:
    """Unit tests for the _ModelGardenModel base class."""

    class FakeModelGardenModel(_model_garden_models._ModelGardenModel):

        _LAUNCH_STAGE = _model_garden_models._SDK_PUBLIC_PREVIEW_LAUNCH_STAGE

        _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/text_generation_1.0.0.yaml"

    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_model_garden_model_with_from_pretrained(self):
        """Tests the text generation model."""
        aiplatform.init(
            project=test_constants.ProjectConstants._TEST_PROJECT,
            location=test_constants.ProjectConstants._TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client_v1.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            self.FakeModelGardenModel.from_pretrained("text-bison@001")

            mock_get_publisher_model.assert_called_once_with(
                name="publishers/google/models/text-bison@001",
                retry=base._DEFAULT_RETRY,
            )

    def test_init_preview_model_raises_with_ga_launch_stage_set(self):
        """Tests the text generation model."""
        aiplatform.init(
            project=test_constants.ProjectConstants._TEST_PROJECT,
            location=test_constants.ProjectConstants._TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client_v1.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ):
            self.FakeModelGardenModel._LAUNCH_STAGE = (
                _model_garden_models._SDK_GA_LAUNCH_STAGE
            )

            with pytest.raises(ValueError):
                self.FakeModelGardenModel.from_pretrained("text-bison@001")
