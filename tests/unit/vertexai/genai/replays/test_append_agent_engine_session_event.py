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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring

import datetime

from tests.unit.vertexai.genai.replays import pytest_helper


def test_append_session_event(client):
    agent_engine = client.agent_engines.create()
    operation = client.agent_engines.create_session(
        name=agent_engine.api_resource.name,
        user_id="test-user-123",
    )
    session = operation.response
    client.agent_engines.append_session_event(
        name=session.name,
        author="test-user-123",
        invocation_id="test-invocation-id",
        timestamp=datetime.datetime.fromtimestamp(1234567890, tz=datetime.timezone.utc),
        config={
            "content": {
                "parts": [
                    {
                        "text": "Hello World",
                    },
                ],
            },
            "error_code": "test-error-code",
            "error_message": "test-error-message",
        },
    )


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.append_session_event",
)
