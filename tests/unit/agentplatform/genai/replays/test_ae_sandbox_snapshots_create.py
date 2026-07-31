"""Tests for Sandbox Snapshot create operation."""

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


def test_create_sandbox_snapshot(client):
    snapshot = client.sandboxes.snapshots._create(
        source_sandbox_environment_name="projects/802583348448/locations/us-central1/reasoningEngines/6130241318758121472/sandboxEnvironments/525190525100228608",
        config={
            "display_name": "test_snapshot",
            "ttl": "3600s",
            "owner": "test_owner",
        },
    )

    assert isinstance(snapshot, types.RuntimeSandboxSnapshotOperation)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="sandboxes.snapshots._create",
)
