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


def test_get_eval_item_response(client):
    """Tests that get_evaluation_item() returns a correctly structured EvaluationItem."""
    evaluation_item_name = "projects/503583131166/locations/us-central1/evaluationItems/1486082323915997184"
    evaluation_item = client.evals.get_evaluation_item(name=evaluation_item_name)
    assert isinstance(evaluation_item, types.EvaluationItem)
    check_item_1486082323915997184(evaluation_item, evaluation_item_name)


def test_get_eval_item_request(client):
    """Tests that get_evaluation_item() returns a correctly structured EvaluationItem with request."""
    evaluation_item_name = "projects/503583131166/locations/us-central1/evaluationItems/4813679498589372416"
    evaluation_item = client.evals.get_evaluation_item(name=evaluation_item_name)
    assert isinstance(evaluation_item, types.EvaluationItem)
    check_item_4813679498589372416(evaluation_item, evaluation_item_name)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_get_eval_item_response_async(client):
    """Tests that get_evaluation_item() returns a correctly structured EvaluationItem."""
    eval_item_id = "1486082323915997184"
    evaluation_item_name = (
        f"projects/503583131166/locations/us-central1/evaluationItems/{eval_item_id}"
    )
    evaluation_item = await client.aio.evals.get_evaluation_item(name=eval_item_id)
    check_item_1486082323915997184(evaluation_item, evaluation_item_name)


@pytest.mark.asyncio
async def test_get_eval_item_request_async(client):
    """Tests that get_evaluation_item() returns a correctly structured EvaluationItem with request."""
    eval_item_id = "4813679498589372416"
    evaluation_item_name = (
        f"projects/503583131166/locations/us-central1/evaluationItems/{eval_item_id}"
    )
    evaluation_item = await client.aio.evals.get_evaluation_item(name=eval_item_id)
    check_item_4813679498589372416(evaluation_item, evaluation_item_name)


def check_item_1486082323915997184(
    evaluation_item: types.EvaluationItem, evaluation_item_name: str
):
    assert evaluation_item.name == evaluation_item_name
    assert evaluation_item.display_name == "universal result for 7119522507803066368"
    assert evaluation_item.evaluation_item_type == types.EvaluationItemType.RESULT
    assert (
        evaluation_item.gcs_uri
        == "gs://lakeyk-limited-bucket/agora_eval_080525/result_1486082323915997184.json"
    )
    assert evaluation_item.create_time == datetime.datetime(
        2025, 9, 8, 20, 55, 46, 713792, tzinfo=datetime.timezone.utc
    )
    assert isinstance(evaluation_item.evaluation_response, types.EvaluationItemResult)
    assert (
        evaluation_item.evaluation_response.evaluation_request
        == "projects/503583131166/locations/us-central1/evaluationItems/7119522507803066368"
    )
    assert (
        evaluation_item.evaluation_response.evaluation_run
        == "projects/503583131166/locations/us-central1/evaluationRuns/1957799200510967808"
    )
    # Check the first candidate result.
    candidate_result = evaluation_item.evaluation_response.candidate_results[0]
    assert candidate_result.candidate == "gemini-2.0-flash-001@default"
    assert candidate_result.metric == "universal"
    assert candidate_result.score == 0.2857143
    # Check the first rubric verdict.
    rubric_verdict = candidate_result.rubric_verdicts[0]
    assert rubric_verdict.verdict
    assert (
        rubric_verdict.reasoning
        == "The entire response is written in the English language."
    )
    assert rubric_verdict.evaluated_rubric.type == "LANGUAGE:PRIMARY_RESPONSE_LANGUAGE"
    assert rubric_verdict.evaluated_rubric.importance == "HIGH"
    assert (
        rubric_verdict.evaluated_rubric.content.property.description
        == "The response is in English."
    )
    # Check the request.
    request = evaluation_item.evaluation_response.request
    assert (
        "There is a wide range of potato varieties to choose from"
        in request.prompt.text
    )
    assert request.candidate_responses[0].candidate == "gemini-2.0-flash-001@default"
    assert "Pick out your potato variety" in request.candidate_responses[0].text


def check_item_4813679498589372416(
    evaluation_item: types.EvaluationItem, evaluation_item_name: str
):
    assert evaluation_item.name == evaluation_item_name
    assert evaluation_item.display_name == "4813679498589372416"
    assert evaluation_item.evaluation_item_type == types.EvaluationItemType.REQUEST
    assert (
        evaluation_item.gcs_uri
        == "gs://lakeyk-limited-bucket/agora_eval_080525/request_4813679498589372416.json"
    )
    assert evaluation_item.create_time == datetime.datetime(
        2025, 9, 8, 20, 55, 46, 338353, tzinfo=datetime.timezone.utc
    )
    assert isinstance(evaluation_item.evaluation_request, types.EvaluationItemRequest)
    # Check the request.
    request = evaluation_item.evaluation_request
    assert (
        "If your ball is curving during flight from left to right"
        in request.prompt.text
    )
    # Check the first candidate response.
    assert request.candidate_responses[0].candidate == "gemini-2.0-flash-001@default"
    assert (
        "Keep your knees bent during the backswing"
        in request.candidate_responses[0].text
    )


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.get_evaluation_item",
)
