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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring

import asyncio
import time

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform import types
import pytest


# The Harbor import is served on autopush.
_AUTOPUSH_BASE_URL = "https://us-central1-autopush-aiplatform.sandbox.googleapis.com/"
_HARBOR_DATASET_GCS_URI = (
    "gs://agent-eval-fishfood/harbor-swebench-verified-mini/import/"
    "swebench-verified-mini"
)
# An existing EvaluationSet of Harbor tasks from the dataset above.
_HARBOR_EVAL_SET_NAME = (
    "projects/977012026409/locations/us-central1/evaluationSets/62296129806532608"
)
_POLL_INTERVAL_SECONDS = 5
_MAX_POLLS = 60


def _wait_for_import(client, operation, is_replay_mode):
    for _ in range(_MAX_POLLS):
        if operation.done:
            return operation
        if not is_replay_mode:
            time.sleep(_POLL_INTERVAL_SECONDS)
        operation = client.evals.get_import_evaluation_set_operation(
            operation_name=operation.name
        )
    raise TimeoutError(f"Import operation {operation.name} is not done.")


async def _async_wait_for_import(client, operation, is_replay_mode):
    for _ in range(_MAX_POLLS):
        if operation.done:
            return operation
        if not is_replay_mode:
            await asyncio.sleep(_POLL_INTERVAL_SECONDS)
        operation = await client.aio.evals.get_import_evaluation_set_operation(
            operation_name=operation.name
        )
    raise TimeoutError(f"Import operation {operation.name} is not done.")


def test_get_import_eval_set_operation_overwrite_harbor_dataset(client, is_replay_mode):
    """Polls an import that overwrites an EvaluationSet of Harbor tasks."""
    client._api_client._http_options.base_url = _AUTOPUSH_BASE_URL

    operation = _wait_for_import(
        client,
        client.evals.import_evaluation_set(
            evaluation_set=types.EvaluationSet(name=_HARBOR_EVAL_SET_NAME),
            harbor_dataset=types.HarborDataset(gcs_uri=_HARBOR_DATASET_GCS_URI),
            import_mode=types.ImportMode.OVERWRITE,
        ),
        is_replay_mode,
    )

    assert isinstance(operation, types.ImportEvaluationSetOperation)
    assert operation.error is None
    assert operation.response.evaluation_set == _HARBOR_EVAL_SET_NAME


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_get_import_eval_set_operation_async(client, is_replay_mode):
    """Polls a Harbor import on the async client."""
    client._api_client._http_options.base_url = _AUTOPUSH_BASE_URL

    operation = await _async_wait_for_import(
        client,
        await client.aio.evals.import_evaluation_set(
            evaluation_set=types.EvaluationSet(display_name="replay-test-harbor-set"),
            harbor_dataset=types.HarborDataset(gcs_uri=_HARBOR_DATASET_GCS_URI),
        ),
        is_replay_mode,
    )

    assert isinstance(operation, types.ImportEvaluationSetOperation)
    assert operation.error is None
    assert "/evaluationSets/" in operation.response.evaluation_set


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.get_import_evaluation_set_operation",
)
