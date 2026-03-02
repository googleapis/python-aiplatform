# Copyright 2026 Google LLC
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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types


def test_create_simple_a2a_task(client):
    # Use the autopush environment.
    client._api_client._http_options.base_url = (
        "https://us-central1-autopush-aiplatform.sandbox.googleapis.com/"
    )
    agent_engine = client.agent_engines.create()
    assert isinstance(agent_engine, types.AgentEngine)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)
    # Use the internal API version for internal API access.
    client._api_client._http_options.api_version = "internal"

    task = client.agent_engines.a2a_tasks.create(
        name=agent_engine.api_resource.name,
        a2a_task_id="task123",
        config=types.CreateAgentEngineTaskConfig(
            context_id="context123",
            metadata={
                "key": "value",
                "key2": [{"key3": "value3", "key4": "value4"}],
            },
            state=types.A2aTaskState.STATE_UNSPECIFIED,
            status_details=types.TaskStatusDetails(
                task_message=types.TaskMessage(
                    role="user",
                    message_id="message123",
                    parts=[
                        types.Part(
                            text="hello123",
                        )
                    ],
                    metadata={
                        "key42": "value42",
                    },
                ),
            ),
            output=types.TaskOutput(
                artifacts=[
                    types.TaskArtifact(
                        artifact_id="artifact123",
                        display_name="display_name123",
                        description="description123",
                        parts=[
                            types.Part(
                                text="hello456",
                            )
                        ],
                    )
                ],
            ),
        ),
    )

    assert isinstance(task, types.A2aTask)
    assert task.name == f"{agent_engine.api_resource.name}/a2aTasks/task123"
    assert task.context_id == "context123"
    assert task.state == types.State.SUBMITTED
    assert task.status_details.task_message.role == "user"
    assert task.status_details.task_message.message_id == "message123"
    assert task.status_details.task_message.parts[0].text == "hello123"
    assert task.status_details.task_message.metadata["key42"] == "value42"
    assert task.output.artifacts[0].artifact_id == "artifact123"
    assert task.output.artifacts[0].display_name == "display_name123"
    assert task.output.artifacts[0].description == "description123"
    assert task.output.artifacts[0].parts[0].text == "hello456"
    assert task.metadata == {
        "key": "value",
        "key2": [{"key3": "value3", "key4": "value4"}],
    }

    # Clean up resources.
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)
