# -*- coding: utf-8 -*-

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
"""Unit tests for `vertexai.types` resolving against `agentplatform.types`."""

import agentplatform
import vertexai
from agentplatform._genai import types as agentplatform_types
from vertexai._genai import types as legacy_types

import sys

import pytest

# Both modules resolve these out of `_evals_metric_loaders` on first access, so
# they are checked on their own rather than in the bulk comparisons below.
_LAZY_NAMES = frozenset({"PrebuiltMetric", "RubricMetric"})

_SHARED_NAMES = sorted(
    (set(agentplatform_types.__all__) & set(legacy_types.__all__)) - _LAZY_NAMES
)
_LEGACY_ONLY_NAMES = sorted(
    set(legacy_types.__all__) - set(agentplatform_types.__all__)
)
_AGENT_PLATFORM_ONLY_NAMES = sorted(
    set(agentplatform_types.__all__) - set(legacy_types.__all__)
)


def test_vertexai_types_is_the_alias_module():
    assert sys.modules[vertexai.types.__name__] is vertexai.types
    assert vertexai.types is not legacy_types
    assert vertexai.types is not agentplatform_types


def test_shared_names_are_the_agentplatform_objects():
    """The point of the alias: one class per message rather than two."""
    assert _SHARED_NAMES, "expected the two modules to share generated types"
    mismatched = [
        name
        for name in _SHARED_NAMES
        if getattr(vertexai.types, name) is not getattr(agentplatform_types, name)
    ]
    assert not mismatched


def test_memory_profile_survives_an_isinstance_check():
    """Regression: an agentplatform object checked against the vertexai name."""
    profile = agentplatform_types.MemoryProfile(schema_id="user-profile", profile={})
    assert isinstance(profile, vertexai.types.MemoryProfile)


def test_shared_types_still_nest_inside_a_legacy_only_model():
    """The two halves have to interoperate, not just coexist.

    `GenerateAgentEngineMemoriesConfig` stays a `vertexai` class because
    agentplatform renamed it, but its `metadata` values are now agentplatform
    objects. Pydantic accepts them because both models derive from the genai
    `BaseModel`, which sets `from_attributes=True`.
    """
    config = vertexai.types.GenerateAgentEngineMemoriesConfig(
        metadata={"record": vertexai.types.MemoryMetadataValue(string_value="123")}
    )
    assert type(config) is legacy_types.GenerateAgentEngineMemoriesConfig
    assert config.metadata["record"].string_value == "123"


def test_legacy_only_names_still_resolve():
    """The `AgentEngine*` surface agentplatform renamed is not taken away."""
    assert "AgentEngine" in _LEGACY_ONLY_NAMES
    mismatched = [
        name
        for name in _LEGACY_ONLY_NAMES
        if getattr(vertexai.types, name) is not getattr(legacy_types, name)
    ]
    assert not mismatched


def test_agentplatform_only_names_are_reachable():
    assert "Runtime" in _AGENT_PLATFORM_ONLY_NAMES
    mismatched = [
        name
        for name in _AGENT_PLATFORM_ONLY_NAMES
        if getattr(vertexai.types, name) is not getattr(agentplatform_types, name)
    ]
    assert not mismatched


@pytest.mark.parametrize("name", sorted(_LAZY_NAMES))
def test_lazily_loaded_metric_names_resolve_to_agentplatform(name):
    assert getattr(vertexai.types, name) is getattr(agentplatform_types, name)


def test_all_is_the_union_of_both_modules():
    expected = set(agentplatform_types.__all__) | set(legacy_types.__all__)
    assert set(vertexai.types.__all__) == expected
    assert set(dir(vertexai.types)) == expected


def test_unknown_name_still_raises_attribute_error():
    with pytest.raises(AttributeError):
        _ = vertexai.types.NoSuchTypeName


def test_agentplatform_registers_its_own_types_alias():
    """`agentplatform.types` must no longer claim the `vertexai.types` key."""
    assert agentplatform.types is agentplatform_types
    assert sys.modules[f"{agentplatform.__name__}.types"] is agentplatform_types
    assert sys.modules[f"{vertexai.__name__}.types"] is not agentplatform_types
