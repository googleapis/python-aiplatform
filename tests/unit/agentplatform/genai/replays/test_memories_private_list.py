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

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types


def test_private_list_memory(client):
    memory_bank = client.memory_banks.create()
    try:
        _ = client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact",
            scope={"user_id": "123"},
        )
        memory_list = client.memory_banks.memories._list(name=memory_bank.name)
        assert isinstance(memory_list, types.ListMemoriesResponse)
        assert isinstance(memory_list.memories[0], types.Memory)
    finally:
        client.memory_banks.delete(name=memory_bank.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="memory_banks.memories._list",
)
