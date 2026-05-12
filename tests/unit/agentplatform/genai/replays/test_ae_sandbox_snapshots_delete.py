"""Tests for Sandbox Snapshot delete operation."""

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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring,bad-indentation

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types


def test_delete_sandbox_snapshot(client):
    result = client.agent_engines.sandboxes.snapshots._delete(
        name="projects/802583348448/locations/us-central1/reasoningEngines/6130241318758121472/sandboxEnvironmentSnapshots/421086565159141376",
    )

    assert isinstance(result, types.DeleteSandboxEnvironmentSnapshotOperation)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.sandboxes.snapshots._delete",
)
