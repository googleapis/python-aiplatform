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

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai import types
import pytest


EVAL_ITEMS = [
    "projects/503583131166/locations/us-central1/evaluationItems/4411504533427978240",
    "projects/503583131166/locations/us-central1/evaluationItems/8621947972554326016",
]
DISPLAY_NAME = "test_eval_set"


def test_create_eval_set(client):
    """Tests that create_evaluation_set() returns a correctly structured EvaluationSet."""
    evaluation_set = client.evals.create_evaluation_set(
        evaluation_items=EVAL_ITEMS, display_name=DISPLAY_NAME
    )
    assert isinstance(evaluation_set, types.EvaluationSet)
    assert evaluation_set.display_name == DISPLAY_NAME
    assert evaluation_set.evaluation_items == EVAL_ITEMS


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_create_eval_set_async(client):
    """Tests that create_evaluation_set() returns a correctly structured EvaluationSet."""
    evaluation_set = await client.aio.evals.create_evaluation_set(
        evaluation_items=EVAL_ITEMS,
        display_name=DISPLAY_NAME,
    )
    assert isinstance(evaluation_set, types.EvaluationSet)
    assert evaluation_set.display_name == DISPLAY_NAME
    assert evaluation_set.evaluation_items == EVAL_ITEMS


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.create_evaluation_set",
)
