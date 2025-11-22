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

GCS_URI = (
    "gs://lakeyk-limited-bucket/agora_eval_080525/request_4813679498589372416.json"
)
DISPLAY_NAME = "test_eval_item"


def test_create_eval_item(client):
    """Tests that create_evaluation_item() returns a correctly structured EvaluationItem."""
    evaluation_item = client.evals.create_evaluation_item(
        evaluation_item_type=types.EvaluationItemType.REQUEST,
        gcs_uri=GCS_URI,
        display_name=DISPLAY_NAME,
    )
    # Retrieve the evaluation item to check that it was created correctly.
    retrieved_evaluation_item = client.evals.get_evaluation_item(
        name=evaluation_item.name
    )
    check_evaluation_item(
        evaluation_item,
        retrieved_evaluation_item,
    )


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_create_eval_item_async(client):
    """Tests that create_evaluation_item() returns a correctly structured EvaluationItem."""
    evaluation_item = await client.aio.evals.create_evaluation_item(
        evaluation_item_type=types.EvaluationItemType.REQUEST,
        gcs_uri=GCS_URI,
        display_name=DISPLAY_NAME,
    )
    # Retrieve the evaluation item to check that it was created correctly.
    retrieved_evaluation_item = await client.aio.evals.get_evaluation_item(
        name=evaluation_item.name
    )
    check_evaluation_item(
        evaluation_item,
        retrieved_evaluation_item,
    )


def check_evaluation_item(
    evaluation_item: types.EvaluationItem,
    retrieved_evaluation_item: types.EvaluationItem,
):
    assert isinstance(evaluation_item, types.EvaluationItem)
    assert evaluation_item.gcs_uri == GCS_URI
    assert evaluation_item.evaluation_item_type == types.EvaluationItemType.REQUEST
    assert evaluation_item.display_name == DISPLAY_NAME
    assert retrieved_evaluation_item.gcs_uri == GCS_URI
    assert (
        retrieved_evaluation_item.evaluation_item_type
        == types.EvaluationItemType.REQUEST
    )
    assert retrieved_evaluation_item.display_name == DISPLAY_NAME
    # Check the request data.
    request = retrieved_evaluation_item.evaluation_request
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
    test_method="evals.create_evaluation_item",
)
