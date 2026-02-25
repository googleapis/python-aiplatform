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


def test_list_simple_a2a_task_events(client):
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
        a2a_task_id="task999",
        config=types.CreateAgentEngineTaskConfig(context_id="context999"),
    )
    assert isinstance(task, types.A2aTask)

    events = list(
        client.agent_engines.a2a_tasks.events.list(
            name=task.name,
        )
    )
    assert len(events) == 1
    assert events[0].event_data.state_change.new_state == "SUBMITTED"

    client.agent_engines.a2a_tasks.events.append(
        name=task.name,
        task_events=[
            types.TaskEvent(
                event_data=types.TaskEventData(
                    metadata_change=types.TaskMetadataChange(
                        new_metadata={"key1": "value1"}
                    )
                ),
                event_sequence_number=1,
            ),
            types.TaskEvent(
                event_data=types.TaskEventData(
                    metadata_change=types.TaskMetadataChange(
                        new_metadata={"key2": "value2"}
                    )
                ),
                event_sequence_number=2,
            ),
        ],
    )

    result = list(
        client.agent_engines.a2a_tasks.events.list(
            name=task.name,
            config=types.ListAgentEngineTaskEventsConfig(
                order_by="create_time desc",
            ),
        )
    )

    assert len(result) == 3
    assert result[0].event_sequence_number == 2
    assert result[0].event_data.metadata_change.new_metadata == {"key2": "value2"}
    assert result[1].event_sequence_number == 1
    assert result[1].event_data.metadata_change.new_metadata == {"key1": "value1"}
    assert result[2].event_data.state_change.new_state == "SUBMITTED"

    # Clean up resources.
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)
