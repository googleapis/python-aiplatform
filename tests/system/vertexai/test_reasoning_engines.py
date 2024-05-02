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
"""System tests for reasoning engines."""
import pytest
from google import auth
from google.api_core import exceptions
import vertexai
from tests.system.aiplatform import e2e_base
from vertexai.preview import reasoning_engines


class CapitalizeEngine:
    """A sample Reasoning Engine."""

    def set_up(self):
        pass

    def query(self, input: str) -> str:
        """Capitalizes the input."""
        return input.upper()


@pytest.mark.usefixtures(
    "prepare_staging_bucket", "delete_staging_bucket", "tear_down_resources"
)
class TestReasoningEngines(e2e_base.TestEndToEnd):
    """System tests for reasoning engines."""

    _temp_prefix = "test-reasoning-engine"

    def test_langchain_template(self, shared_state):
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        vertexai.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
            credentials=credentials,
        )
        created_app = reasoning_engines.ReasoningEngine.create(
            reasoning_engines.LangchainAgent(model="gemini-1.0-pro"),
            requirements=["google-cloud-aiplatform[reasoningengine,langchain]"],
        )
        shared_state.setdefault("resources", [])
        shared_state["resources"].append(created_app)  # Deletion at teardown.
        try:
            response = created_app.query(input="hello")
            assert response.get("input") == "hello"
            assert isinstance(created_app.resource_name, str)
            got_app = reasoning_engines.ReasoningEngine(created_app.resource_name)
            assert got_app.resource_name == created_app.resource_name
            assert got_app.operation_schemas() == created_app.operation_schemas()
            response = got_app.query(input="hello")
            assert response.get("input") == "hello"
        except exceptions.FailedPrecondition as e:
            print(e)

    def test_create_reasoning_engine_gcs_dir_name(self, shared_state):
        # https://github.com/googleapis/python-aiplatform/issues/3650
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        vertexai.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
            credentials=credentials,
        )
        created_app = reasoning_engines.ReasoningEngine.create(
            reasoning_engine=CapitalizeEngine(),
            gcs_dir_name="test-gcs-dir-name",
        )
        shared_state.setdefault("resources", [])
        shared_state["resources"].append(created_app)  # Deletion at teardown.
        assert created_app.query(input="hello") == "HELLO"

    def test_create_reasoning_engine_resource_attributes(self, shared_state):
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        vertexai.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
            credentials=credentials,
        )
        created_app = reasoning_engines.ReasoningEngine.create(
            reasoning_engine=CapitalizeEngine(),
            reasoning_engine_name="test-reasoning-engine-name",
            display_name="test-display-name",
            description="test-description",
        )
        shared_state.setdefault("resources", [])
        shared_state["resources"].append(created_app)  # Deletion at teardown.
        assert created_app.gca_resource.name == "test-reasoning-engine-name"
        assert created_app.gca_resource.display_name == "test-display-name"
        assert created_app.gca_resource.description == "test-description"

    def test_create_reasoning_engine_operation_schemas(self, shared_state):
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        vertexai.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
            credentials=credentials,
        )
        created_app = reasoning_engines.ReasoningEngine.create(
            reasoning_engine=CapitalizeEngine(),
        )
        shared_state.setdefault("resources", [])
        shared_state["resources"].append(created_app)  # Deletion at teardown.
        assert created_app.operation_schemas() == []
