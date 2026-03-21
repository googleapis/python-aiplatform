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
from vertexai._genai import types


def test_append_session_event(client):
    session_event = client.agent_engines.sessions.events.append(
        name="reasoningEngines/2886612747586371584/sessions/6922431337672474624",
        author="test-user-123",
        invocation_id="test-invocation-id",
        timestamp=datetime.datetime.fromtimestamp(1234567860, tz=datetime.timezone.utc),
    )
    assert isinstance(session_event, types.AppendAgentEngineSessionEventResponse)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.sessions.events.append",
)
