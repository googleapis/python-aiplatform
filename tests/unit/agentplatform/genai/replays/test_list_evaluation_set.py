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


def test_list_eval_sets(client):
    """Tests that list_evaluation_sets() returns a page of EvaluationSets."""
    response = client.evals.list_evaluation_sets(config={"page_size": 5})
    assert isinstance(response, types.ListEvaluationSetsResponse)
    assert response.evaluation_sets is not None
    assert len(response.evaluation_sets) == 5
    assert response.next_page_token
    for evaluation_set in response.evaluation_sets:
        assert isinstance(evaluation_set, types.EvaluationSet)
        assert (
            evaluation_set.name.startswith("projects/")
            and "/evaluationSets/" in evaluation_set.name
        )


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_list_eval_sets_async(client):
    """Tests that list_evaluation_sets() works on the async client."""
    response = await client.aio.evals.list_evaluation_sets(config={"page_size": 5})
    assert isinstance(response, types.ListEvaluationSetsResponse)
    assert response.evaluation_sets is not None
    assert len(response.evaluation_sets) == 5
    for evaluation_set in response.evaluation_sets:
        assert isinstance(evaluation_set, types.EvaluationSet)
        assert (
            evaluation_set.name.startswith("projects/")
            and "/evaluationSets/" in evaluation_set.name
        )


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.list_evaluation_sets",
)
