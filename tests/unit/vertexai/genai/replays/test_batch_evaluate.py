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

import pytest

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types


def test_batch_eval(client):
    eval_dataset = types.EvaluationDataset(
        gcs_source=types.GcsSource(
            uris=["gs://genai-eval-sdk-replay-test/test_data/inference_results.jsonl"]
        )
    )

    batch_eval_operation = client.evals.batch_evaluate(
        dataset=eval_dataset,
        metrics=[
            types.RubricMetric.TEXT_QUALITY,
        ],
        dest="gs://genai-eval-sdk-replay-test/test_data/batch_eval_output",
    )
    assert "operations" in batch_eval_operation.name
    assert "EvaluateDatasetOperationMetadata" in batch_eval_operation.metadata.get(
        "@type"
    )


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.batch_evaluate",
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_batch_eval_async(client):
    eval_dataset = types.EvaluationDataset(
        gcs_source=types.GcsSource(
            uris=["gs://genai-eval-sdk-replay-test/test_data/inference_results.jsonl"]
        )
    )

    response = await client.aio.evals.batch_evaluate(
        dataset=eval_dataset,
        metrics=[
            types.RubricMetric.TEXT_QUALITY,
        ],
        dest="gs://genai-eval-sdk-replay-test/test_data/batch_eval_output",
    )
    assert "operations" in response.name
    assert "EvaluateDatasetOperationMetadata" in response.metadata.get("@type")
