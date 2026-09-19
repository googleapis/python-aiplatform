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
"""`vertexai.types` resolved against `agentplatform.types`.

Agent Platform re-generated the Gen AI types under `agentplatform` rather than
moving them, so `vertexai.types.Memory` and `agentplatform.types.Memory` were
two distinct classes carrying identical definitions. Code that hands an
`agentplatform` object to a caller written against the `vertexai` name fails
`isinstance`, even though both describe the same message.

This module removes the split. Every name `agentplatform.types` defines
resolves here to the `agentplatform` class, so the two spellings are one
object. The names that only ever existed under `vertexai` -- the `AgentEngine*`
surface Agent Platform renamed to `Runtime*` and `MemoryBank*` -- keep
resolving to their `vertexai._genai.types` classes, so nothing is taken away
from callers that have not migrated.

The unification is a runtime one. Names resolve through `__getattr__`, so a
type checker still reads `vertexai.types.X` as `Any`, exactly as it did while
this name was a lazy alias for `vertexai._genai.types`. Re-exporting both
modules under `typing.TYPE_CHECKING` would make them resolve statically too,
but it also makes the checker read the generated `Optional` fields for the
first time, which turns long-standing unguarded accesses in downstream callers
into new type errors. Static resolution is being rolled out separately, once
those callers are fixed.

The dependency runs one way: `vertexai` reaches into `agentplatform`, never the
reverse. `google-cloud-agentplatform` ships `agentplatform` without `vertexai`
and without the generated clients, and nothing here changes that.

Resolution stays lazy at each step. `vertexai.__getattr__` defers importing
this module until `vertexai.types` is touched; `vertexai._genai.types` is
imported only if a name is not found in `agentplatform`; and neither module's
`PrebuiltMetric`/`RubricMetric` is resolved until asked for, so the evaluation
dependencies are still not pulled in by a bare import.
"""

from __future__ import annotations

import importlib as _importlib
import types as _module_types
import typing as _typing

from agentplatform._genai import types as _agentplatform_types

_legacy_types: _module_types.ModuleType | None = None


def _get_legacy_types() -> _module_types.ModuleType:
    """Imports `vertexai._genai.types` on first use."""
    global _legacy_types
    if _legacy_types is None:
        _legacy_types = _importlib.import_module("._genai.types", __package__)
    return _legacy_types


def __getattr__(name: str) -> _typing.Any:
    # See https://peps.python.org/pep-0562/
    if name == "__all__":
        return __dir__()
    try:
        return getattr(_agentplatform_types, name)
    except AttributeError:
        pass
    try:
        return getattr(_get_legacy_types(), name)
    except AttributeError:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'") from None


def __dir__() -> list[str]:
    return sorted(set(_agentplatform_types.__all__) | set(_get_legacy_types().__all__))
