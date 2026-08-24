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
from google.genai import types as genai_types


def test_private_get_generate_memories_operation(client):
    memory_bank = client.memory_banks.create()
    try:
        generate_memories_operation = client.memory_banks.memories.generate(
            name=memory_bank.name,
            scope={"user_id": "123"},
            direct_contents_source=types.GenerateMemoriesRequestDirectContentsSource(
                events=[
                    types.GenerateMemoriesRequestDirectContentsSourceEvent(
                        content=genai_types.Content(
                            role="model",
                            parts=[genai_types.Part(text="I am writing tests.")],
                        )
                    )
                ]
            ),
        )
        memory_operation = (
            client.memory_banks.memories._get_generate_memories_operation(
                operation_name=generate_memories_operation.name
            )
        )
        assert isinstance(memory_operation, types.GenerateMemoriesOperation)
    finally:
        client.memory_banks.delete(name=memory_bank.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="memory_banks.memories._get_generate_memories_operation",
)
