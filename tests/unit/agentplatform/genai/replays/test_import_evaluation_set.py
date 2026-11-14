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
# The Harbor tests are recorded against autopush, which serves the Harbor import.
_AUTOPUSH_BASE_URL = "https://us-central1-autopush-aiplatform.sandbox.googleapis.com/"
_HARBOR_DATASET_GCS_URI = (
    "gs://agent-eval-fishfood/harbor-swebench-verified-mini/import/"
    "swebench-verified-mini"
)


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


def test_import_eval_set_from_harbor_dataset(client):
    """Tests import_evaluation_set(wait=True) from a Harbor dataset."""
    client._api_client._http_options.base_url = _AUTOPUSH_BASE_URL

    operation = client.evals.import_evaluation_set(
        evaluation_set=types.EvaluationSet(display_name="replay-test-harbor-set"),
        harbor_dataset=types.HarborDataset(gcs_uri=_HARBOR_DATASET_GCS_URI),
        wait=True,
    )
    evaluation_set = client.evals.get_evaluation_set(
        name=operation.response.evaluation_set
    )

    assert isinstance(operation, types.ImportEvaluationSetOperation)
    assert operation.done
    assert "/evaluationSets/" in evaluation_set.name
    assert evaluation_set.display_name == "replay-test-harbor-set"
    assert evaluation_set.harbor_dataset.gcs_uri == _HARBOR_DATASET_GCS_URI


def test_import_eval_set_overwrite_harbor_dataset(client):
    """Tests import_evaluation_set() with ImportMode.OVERWRITE."""
    client._api_client._http_options.base_url = _AUTOPUSH_BASE_URL
    harbor_dataset = types.HarborDataset(gcs_uri=_HARBOR_DATASET_GCS_URI)
    operation = client.evals.import_evaluation_set(
        evaluation_set=types.EvaluationSet(
            display_name="replay-test-harbor-overwrite-set"
        ),
        harbor_dataset=harbor_dataset,
        wait=True,
    )
    evaluation_set = client.evals.get_evaluation_set(
        name=operation.response.evaluation_set
    )

    overwrite_operation = client.evals.import_evaluation_set(
        evaluation_set=types.EvaluationSet(name=evaluation_set.name),
        harbor_dataset=harbor_dataset,
        import_mode=types.ImportMode.OVERWRITE,
        wait=True,
    )
    overwritten_set = client.evals.get_evaluation_set(
        name=overwrite_operation.response.evaluation_set
    )

    assert overwrite_operation.response.evaluation_set == evaluation_set.name
    assert overwritten_set.harbor_dataset.gcs_uri == _HARBOR_DATASET_GCS_URI


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


@pytest.mark.asyncio
async def test_import_eval_set_from_harbor_dataset_async(client):
    """Tests import_evaluation_set(wait=True) on the async client."""
    client._api_client._http_options.base_url = _AUTOPUSH_BASE_URL

    operation = await client.aio.evals.import_evaluation_set(
        evaluation_set=types.EvaluationSet(display_name="replay-test-harbor-set"),
        harbor_dataset=types.HarborDataset(gcs_uri=_HARBOR_DATASET_GCS_URI),
        wait=True,
    )
    evaluation_set = await client.aio.evals.get_evaluation_set(
        name=operation.response.evaluation_set
    )

    assert isinstance(operation, types.ImportEvaluationSetOperation)
    assert operation.done
    assert "/evaluationSets/" in evaluation_set.name
    assert evaluation_set.display_name == "replay-test-harbor-set"
    assert evaluation_set.harbor_dataset.gcs_uri == _HARBOR_DATASET_GCS_URI


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.import_evaluation_set",
)
