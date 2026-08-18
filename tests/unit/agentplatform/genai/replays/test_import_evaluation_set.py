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
from agentplatform import types
from google.genai import types as genai_types
import pytest


_GCS_OUTPUT_PREFIX = "gs://agent-eval-datasets/eval-import-replay/output/"


def test_import_eval_set(client):
    """Tests import_evaluation_set() from a Cloud Trace source."""
    operation = client.evals.import_evaluation_set(
        evaluation_set=types.EvaluationSet(display_name="replay-test-import-set"),
        gcs_destination=genai_types.GcsDestination(
            output_uri_prefix=_GCS_OUTPUT_PREFIX
        ),
        cloud_trace_source=types.EvaluationSetCloudTraceSource(
            project_id="vertex-sdk-dev",
            session_ids=["replay-session-1"],
        ),
    )
    assert isinstance(operation, types.ImportEvaluationSetOperation)
    assert operation.name is not None
    assert "/operations/" in operation.name


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_import_eval_set_async(client):
    """Tests import_evaluation_set() on the async client."""
    operation = await client.aio.evals.import_evaluation_set(
        evaluation_set=types.EvaluationSet(display_name="replay-test-import-set"),
        gcs_destination=genai_types.GcsDestination(
            output_uri_prefix=_GCS_OUTPUT_PREFIX
        ),
        cloud_trace_source=types.EvaluationSetCloudTraceSource(
            project_id="vertex-sdk-dev",
            session_ids=["replay-session-1"],
        ),
    )
    assert isinstance(operation, types.ImportEvaluationSetOperation)
    assert operation.name is not None
    assert "/operations/" in operation.name


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.import_evaluation_set",
)
