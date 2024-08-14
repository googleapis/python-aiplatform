# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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

from google import auth

from google.cloud import aiplatform
from google.cloud.aiplatform import telemetry
from tests.system.aiplatform import e2e_base

from vertexai.generative_models import GenerativeModel

GEMINI_MODEL_NAME = "gemini-1.0-pro-002"


class TestTelemetry(e2e_base.TestEndToEnd):
    """Tests the telemetry tool context manager."""

    _temp_prefix = "test_telemetry_"

    def setup_method(self):
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            credentials=credentials,
        )

    def test_single_context_manager(self):
        with telemetry.tool_context_manager("context"):
            model = GenerativeModel(GEMINI_MODEL_NAME)

            model.generate_content("Why is the sky blue?")

    def test_nested_context_manager(self):
        with telemetry.tool_context_manager("outer"):
            with telemetry.tool_context_manager("inner"):
                model = GenerativeModel(GEMINI_MODEL_NAME)

                model.generate_content("Why is the sky blue?")
