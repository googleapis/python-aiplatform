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

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types


def test_create_memory_with_ttl(client):
    memory_bank = client.memory_banks.create()
    try:
        assert isinstance(memory_bank, types.MemoryBank)

        metadata = {
            "my_string_key": types.MemoryMetadataValue(string_value="my_string_value"),
            "my_double_key": types.MemoryMetadataValue(double_value=123.456),
            "my_boolean_key": types.MemoryMetadataValue(bool_value=True),
            "my_timestamp_key": types.MemoryMetadataValue(
                timestamp_value=datetime.datetime(
                    2027, 1, 1, 12, 30, 00, tzinfo=datetime.timezone.utc
                )
            ),
        }

        operation = client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact",
            scope={"user_id": "123"},
            config=types.MemoryConfig(
                display_name="my_memory_fact",
                ttl="120s",
                metadata=metadata,
            ),
        )
        assert isinstance(operation, types.MemoryOperation)
        assert operation.response.fact == "memory_fact"
        assert operation.response.scope == {"user_id": "123"}
        assert operation.response.name.startswith(memory_bank.name)
        # Expire time is calculated by the server, so we only check that it is
        # within a reasonable range to avoid flakiness.
        assert (
            operation.response.create_time + datetime.timedelta(seconds=119.5)
            <= operation.response.expire_time
            <= operation.response.create_time + datetime.timedelta(seconds=120.5)
        )
        assert operation.response.metadata == metadata
    finally:
        # Clean up resources.
        client.memory_banks.delete(name=memory_bank.name, force=True)


def test_create_memory_with_expire_time(client):
    memory_bank = client.memory_banks.create()
    try:
        assert isinstance(memory_bank, types.MemoryBank)
        expire_time = datetime.datetime(
            2027, 1, 1, 12, 30, 00, tzinfo=datetime.timezone.utc
        )

        operation = client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact",
            scope={"user_id": "123"},
            config=types.MemoryConfig(
                display_name="my_memory_fact", expire_time=expire_time
            ),
        )
        assert isinstance(operation, types.MemoryOperation)
        assert operation.response.fact == "memory_fact"
        assert operation.response.scope == {"user_id": "123"}
        assert operation.response.name.startswith(memory_bank.name)
        assert operation.response.expire_time == expire_time
    finally:
        # Clean up resources.
        client.memory_banks.delete(name=memory_bank.name, force=True)


def test_create_memory_with_custom_memory_id(client):
    memory_bank = client.memory_banks.create()
    try:
        assert isinstance(memory_bank, types.MemoryBank)

        operation = client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact",
            scope={"user_id": "123"},
            config=types.MemoryConfig(
                display_name="my_memory_fact", memory_id="my-memory-id"
            ),
        )
        assert isinstance(operation, types.MemoryOperation)
        assert operation.response.fact == "memory_fact"
        assert operation.response.scope == {"user_id": "123"}
        assert operation.response.name == f"{memory_bank.name}/memories/my-memory-id"
    finally:
        # Clean up resources.
        client.memory_banks.delete(name=memory_bank.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="memory_banks.memories.create",
)
