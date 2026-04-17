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

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types
import pytest


def _make_eval_result():
    """Creates an EvaluationResult with rubric verdicts for loss analysis."""
    return types.EvaluationResult(
        eval_case_results=[
            types.EvalCaseResult(
                eval_case_index=0,
                response_candidate_results=[
                    types.ResponseCandidateResult(
                        response_index=0,
                        metric_results={
                            "multi_turn_task_success_v1": types.EvalCaseMetricResult(
                                score=0.0,
                                explanation="Failed tool invocation",
                                rubric_verdicts=[
                                    types.evals.RubricVerdict(
                                        evaluated_rubric=types.evals.Rubric(
                                            rubric_id="tool_invocation",
                                            content=types.evals.RubricContent(
                                                property=types.evals.RubricContentProperty(
                                                    description="The agent should invoke the find_flights tool with the correct parameters.",
                                                )
                                            ),
                                        ),
                                        verdict=False,
                                    )
                                ],
                            )
                        },
                    )
                ],
            )
        ],
        evaluation_dataset=[
            types.EvaluationDataset(
                eval_cases=[
                    types.EvalCase(
                        agent_data=types.evals.AgentData(
                            agents={
                                "travel-agent": types.evals.AgentConfig(
                                    agent_id="travel-agent",
                                    agent_type="ToolUseAgent",
                                    description="A travel agent that can book flights.",
                                )
                            },
                            turns=[
                                types.evals.ConversationTurn(
                                    turn_index=0,
                                    events=[
                                        types.evals.AgentEvent(
                                            author="user",
                                            content={
                                                "parts": [
                                                    {"text": "Book a flight to Paris."}
                                                ]
                                            },
                                        ),
                                        types.evals.AgentEvent(
                                            author="travel-agent",
                                            content={
                                                "parts": [
                                                    {"text": "I can help with that."}
                                                ]
                                            },
                                        ),
                                    ],
                                )
                            ],
                        )
                    )
                ]
            )
        ],
        metadata=types.EvaluationRunMetadata(candidate_names=["travel-agent"]),
    )


def test_gen_loss_clusters(client):
    """Tests that generate_loss_clusters() returns GenerateLossClustersResponse."""
    eval_result = _make_eval_result()
    response = client.evals.generate_loss_clusters(
        eval_result=eval_result,
        config=types.LossAnalysisConfig(
            metric="multi_turn_task_success_v1",
            candidate="travel-agent",
        ),
    )
    assert isinstance(response, types.GenerateLossClustersResponse)
    assert len(response.results) >= 1
    result = response.results[0]
    assert result.config.metric == "multi_turn_task_success_v1"
    assert result.config.candidate == "travel-agent"
    assert len(result.clusters) >= 1
    for cluster in result.clusters:
        assert cluster.cluster_id is not None
        assert cluster.taxonomy_entry is not None
        assert cluster.taxonomy_entry.l1_category is not None


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_gen_loss_clusters_async(client):
    """Tests that generate_loss_clusters() async returns GenerateLossClustersResponse."""
    eval_result = _make_eval_result()
    response = await client.aio.evals.generate_loss_clusters(
        eval_result=eval_result,
        config=types.LossAnalysisConfig(
            metric="multi_turn_task_success_v1",
            candidate="travel-agent",
        ),
    )
    assert isinstance(response, types.GenerateLossClustersResponse)
    assert len(response.results) >= 1
    result = response.results[0]
    assert result.config.metric == "multi_turn_task_success_v1"
    assert len(result.clusters) >= 1


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.generate_loss_clusters",
)
