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
import datetime
import pytest


def test_get_eval_set(client):
    """Tests that get_evaluation_set() returns a correctly structured EvaluationSet."""
    evaluation_set_name = (
        "projects/503583131166/locations/us-central1/evaluationSets/102386522778501120"
    )
    evaluation_set = client.evals.get_evaluation_set(name=evaluation_set_name)
    assert isinstance(evaluation_set, types.EvaluationSet)
    check_set_102386522778501120(evaluation_set, evaluation_set_name)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_get_eval_set_async(client):
    """Tests that get_evaluation_set() returns a correctly structured EvaluationSet."""
    eval_set_id = "102386522778501120"
    evaluation_set_name = (
        f"projects/503583131166/locations/us-central1/evaluationSets/{eval_set_id}"
    )
    evaluation_set = await client.aio.evals.get_evaluation_set(name=eval_set_id)
    check_set_102386522778501120(evaluation_set, evaluation_set_name)


def check_set_102386522778501120(
    evaluation_set: types.EvaluationSet, evaluation_set_name: str
):
    assert evaluation_set.name == evaluation_set_name
    assert (
        evaluation_set.display_name
        == "Results Set for EvaluationRun 1957799200510967808"
    )
    assert evaluation_set.evaluation_items == [
        "projects/503583131166/locations/us-central1/evaluationItems/2748216119486578688",
        "projects/503583131166/locations/us-central1/evaluationItems/1486082323915997184",
        "projects/503583131166/locations/us-central1/evaluationItems/2219043163270545408",
        "projects/503583131166/locations/us-central1/evaluationItems/8570244537769787392",
        "projects/503583131166/locations/us-central1/evaluationItems/2112082672120496128",
        "projects/503583131166/locations/us-central1/evaluationItems/8192505119024087040",
        "projects/503583131166/locations/us-central1/evaluationItems/1383625432393318400",
        "projects/503583131166/locations/us-central1/evaluationItems/5832267070561058816",
        "projects/503583131166/locations/us-central1/evaluationItems/1733991409653907456",
        "projects/503583131166/locations/us-central1/evaluationItems/2549142942207967232",
        "projects/503583131166/locations/us-central1/evaluationItems/8565740938142416896",
        "projects/503583131166/locations/us-central1/evaluationItems/6069620844672319488",
        "projects/503583131166/locations/us-central1/evaluationItems/7777822109585113088",
        "projects/503583131166/locations/us-central1/evaluationItems/5656415578861076480",
        "projects/503583131166/locations/us-central1/evaluationItems/5926842662735839232",
        "projects/503583131166/locations/us-central1/evaluationItems/648623899457617920",
        "projects/503583131166/locations/us-central1/evaluationItems/4349245787016790016",
        "projects/503583131166/locations/us-central1/evaluationItems/1119038954285301760",
        "projects/503583131166/locations/us-central1/evaluationItems/5741983971781115904",
    ]
    assert evaluation_set.create_time == datetime.datetime(
        2025, 9, 8, 20, 55, 46, 413954, tzinfo=datetime.timezone.utc
    )
    assert evaluation_set.update_time == datetime.datetime(
        2025, 9, 8, 20, 55, 46, 413954, tzinfo=datetime.timezone.utc
    )
    assert evaluation_set.metadata is None


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.get_evaluation_set",
)
