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
import pytest


EVAL_ITEMS = [
    "projects/964831358985/locations/us-central1/evaluationItems/7028087120837214208",
    "projects/964831358985/locations/us-central1/evaluationItems/4820901090960605184",
]


def test_delete_eval_set(client):
    """Tests that delete_evaluation_set() deletes a created EvaluationSet."""
    evaluation_set = client.evals.create_evaluation_set(
        evaluation_items=EVAL_ITEMS, display_name="test_delete_eval_set"
    )
    assert isinstance(evaluation_set, types.EvaluationSet)

    # delete_evaluation_set is fire-and-forget and returns None.
    assert client.evals.delete_evaluation_set(name=evaluation_set.name) is None


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_delete_eval_set_async(client):
    """Tests that delete_evaluation_set() deletes a created EvaluationSet."""
    evaluation_set = await client.aio.evals.create_evaluation_set(
        evaluation_items=EVAL_ITEMS, display_name="test_delete_eval_set"
    )
    assert isinstance(evaluation_set, types.EvaluationSet)

    assert (
        await client.aio.evals.delete_evaluation_set(name=evaluation_set.name)
    ) is None


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.delete_evaluation_set",
)
