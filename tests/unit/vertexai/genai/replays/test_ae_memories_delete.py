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

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types


def test_delete_memory(client):
    ae_memory_operation = client.agent_engines.memories.delete(
        name="projects/964831358985/locations/us-central1/reasoningEngines/2886612747586371584/memories/5605466683931099136",
    )
    assert isinstance(ae_memory_operation, types.DeleteAgentEngineMemoryOperation)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.memories.delete",
)
