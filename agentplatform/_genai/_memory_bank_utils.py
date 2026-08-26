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
"""Utility functions for memory banks."""

import asyncio
import json
import re
import time
from typing import (
    Any,
    Protocol,
    Union,
)

from . import types as genai_types


MemoryBankOperation = Union[
    genai_types.MemoryBankOperation,
    genai_types.MemoryOperation,
    genai_types.GenerateMemoriesOperation,
]


class GetOperationFunction(Protocol):
    def __call__(self, *, operation_name: str, **kwargs: Any) -> MemoryBankOperation:
        pass


class GetAsyncOperationFunction(Protocol):
    async def __call__(
        self, *, operation_name: str, **kwargs: Any
    ) -> MemoryBankOperation:
        pass


def _get_memory_bank_id(operation_name: str = "", resource_name: str = "") -> str:
    """Returns Memory Bank ID from operation name or resource name."""
    if not resource_name and not operation_name:
        raise ValueError("Resource name or operation name cannot be empty.")

    if resource_name:
        match = re.match(
            r"^projects/[^/]+/locations/[^/]+/reasoningEngines/([^/]+)$",
            resource_name,
        )
        if match:
            return match.group(1)
        match = re.match(
            r"^projects/[^/]+/locations/[^/]+/memoryBanks/([^/]+)$",
            resource_name,
        )
        if match:
            return match.group(1)
        raise ValueError(
            "Failed to parse Memory Bank ID from resource name: " f"`{resource_name}`"
        )

    if not operation_name:
        raise ValueError("Operation name cannot be empty.")

    match = re.match(
        r"^projects/[^/]+/locations/[^/]+/reasoningEngines/([^/]+)/operations/[^/]+$",
        operation_name,
    )
    if match:
        return match.group(1)

    match = re.match(
        r"^projects/[^/]+/locations/[^/]+/memoryBanks/([^/]+)/operations/[^/]+$",
        operation_name,
    )
    raise ValueError(
        "Failed to parse Memory Bank ID from operation name: " f"`{operation_name}`"
    )


def _await_operation(
    *,
    operation_name: str,
    get_operation_fn: GetOperationFunction,
    poll_interval_seconds: float = 1,
) -> Any:
    """Waits for the operation to complete.

    Args:
        operation_name (str):
            Required. The name of the operation.
        poll_interval_seconds (float):
            The number of seconds to wait between each poll.
        get_operation_fn (Callable[[str], Any]):
            Optional. The function to use for getting the operation. If not
            provided, `self._get_memory_bank_operation` will be used.

    Returns:
        The operation that has completed (i.e. `operation.done==True`).
    """
    operation = get_operation_fn(operation_name=operation_name)
    while not operation.done:
        time.sleep(poll_interval_seconds)
        operation = get_operation_fn(operation_name=operation.name)

    return operation


async def _await_async_operation(
    *,
    operation_name: str,
    get_operation_fn: GetAsyncOperationFunction,
    poll_interval_seconds: float = 1,
) -> Any:
    """Waits for the operation to complete.

    Args:
        operation_name (str):
            Required. The name of the operation.
        poll_interval_seconds (float):
            The number of seconds to wait between each poll.
        get_operation_fn (Callable[[str], Awaitable[Any]]):
            Optional. The async function to use for getting the operation. If not
            provided, `self._get_memory_bank_operation` will be used.

    Returns:
        The operation that has completed (i.e. `operation.done==True`).
    """
    operation = await get_operation_fn(operation_name=operation_name)
    while not operation.done:
        await asyncio.sleep(poll_interval_seconds)
        operation = await get_operation_fn(operation_name=operation.name)

    return operation


def _managed_semantic_memory_config_to_memory_bank_config(
    semantic_memory_config: genai_types.ManagedSemanticMemoryConfigOrDict,
) -> genai_types.ReasoningEngineContextSpecMemoryBankConfigDict:
    """Converts ManagedSemanticMemoryConfig to MemoryBankConfig."""
    if semantic_memory_config is None:
        semantic_memory_config = {}
    if isinstance(semantic_memory_config, dict):
        semantic_memory_config = genai_types.ManagedSemanticMemoryConfig.model_validate(
            semantic_memory_config
        )
    elif not isinstance(
        semantic_memory_config, genai_types.ManagedSemanticMemoryConfig
    ):
        raise TypeError(
            "managed_semantic_memory_config must be a dict or "
            "ManagedSemanticMemoryConfig, "
            f"but got {type(semantic_memory_config)}."
        )

    memory_bank_config = json.loads(semantic_memory_config.model_dump_json())
    if "unstructured_memory_configs" in memory_bank_config:
        memory_bank_config["customization_configs"] = memory_bank_config.pop(
            "unstructured_memory_configs"
        )
    return memory_bank_config


def _memory_bank_config_to_managed_semantic_memories_config(
    memory_bank_config: genai_types.ReasoningEngineContextSpecMemoryBankConfig,
) -> genai_types.ManagedSemanticMemoryConfigDict:
    """Converts MemoryBankConfig to ManagedSemanticMemoriesConfig."""
    memory_bank_config = json.loads(memory_bank_config.model_dump_json())
    if "customization_configs" in memory_bank_config:
        memory_bank_config["unstructured_memory_configs"] = memory_bank_config.pop(
            "customization_configs"
        )
    return memory_bank_config


def _reasoning_engine_to_memory_bank(
    reasoning_engine: genai_types.ReasoningEngine,
) -> genai_types.MemoryBank:
    """Converts ReasoningEngine to MemoryBank."""
    if reasoning_engine.context_spec is not None:
        semantic_memory_config = (
            _memory_bank_config_to_managed_semantic_memories_config(
                reasoning_engine.context_spec.memory_bank_config
            )
        )
    else:
        semantic_memory_config = {}
    memory_bank = genai_types.MemoryBank(
        name=reasoning_engine.name,
        create_time=reasoning_engine.create_time,
        update_time=reasoning_engine.update_time,
        display_name=reasoning_engine.display_name,
        description=reasoning_engine.description,
        encryption_spec=reasoning_engine.encryption_spec,
        managed_semantic_memory_config=semantic_memory_config,
    )
    return memory_bank
