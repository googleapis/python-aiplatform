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

from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper
from google.genai import types as genai_types

PREPROCESS_CODE = """
def preprocess(agent_data):
    turns = []
    for turn in agent_data.get("turns", []):
        events = [
            e for e in turn.get("events", [])
            if e.get("author") in ("user", "coordinator")
        ]
        turns.append({**turn, "events": events})
    return {"agents": agent_data.get("agents", {}), "turns": turns}
"""

PARSE_CODE = """
def parse_results(responses):
    scores = []
    for response in responses:
        digits = [c for c in response if c.isdigit()]
        if digits:
            scores.append(float(digits[-1]))
    return sum(scores) / len(scores)
"""


def _event(author, role, text):
    return types.evals.AgentEvent(
        author=author,
        content=genai_types.Content(role=role, parts=[genai_types.Part(text=text)]),
    )


def _eval_dataset():
    agent_data = types.evals.AgentData(
        agents={
            "coordinator": types.evals.AgentConfig(
                agent_id="coordinator",
                instruction=(
                    "Delegate flights to flight_agent and hotels to hotel_agent."
                ),
                sub_agents=["flight_agent", "hotel_agent"],
            ),
            "flight_agent": types.evals.AgentConfig(
                agent_id="flight_agent", instruction="Book flights."
            ),
            "hotel_agent": types.evals.AgentConfig(
                agent_id="hotel_agent",
                instruction="Book hotels within the user's budget.",
            ),
        },
        turns=[
            types.evals.ConversationTurn(
                turn_index=0,
                events=[
                    _event(
                        "user",
                        "user",
                        "Book a flight to Paris and a hotel under $200 a night.",
                    ),
                    _event(
                        "coordinator",
                        "model",
                        "Asking flight_agent for the flight and hotel_agent for"
                        " the hotel.",
                    ),
                    _event("flight_agent", "model", "Booked flight AF123 to Paris."),
                    _event(
                        "hotel_agent",
                        "model",
                        "Booked Hotel Lumiere at $250 a night.",
                    ),
                    _event(
                        "coordinator",
                        "model",
                        "Your flight AF123 and Hotel Lumiere ($250 a night) are"
                        " booked.",
                    ),
                ],
            )
        ],
    )
    return types.EvaluationDataset(
        eval_cases=[types.EvalCase(eval_case_id="paris-trip", agent_data=agent_data)]
    )


def _assert_result(evaluation_result, metric_name):
    assert isinstance(evaluation_result, types.EvaluationResult)
    assert evaluation_result.summary_metrics[0].metric_name == metric_name
    assert len(evaluation_result.eval_case_results) == 1
    metric_result = (
        evaluation_result.eval_case_results[0]
        .response_candidate_results[0]
        .metric_results[metric_name]
    )
    assert metric_result.error_message is None
    assert metric_result.score is not None


def test_filter_preprocessor(client):
    """Tests a two-step metric over a filtered agent trace."""
    client._api_client._http_options.api_version = "v1beta1"
    metric = types.StepBasedLLMMetric(
        name="budget_adherence",
        preprocessor=types.AgentDataPreprocessor(
            filter_config=types.FilterPreprocessorConfig(
                trace_compression_config=types.TraceCompressionConfig(
                    thoughts_filtered=True, max_turn_count=1
                )
            )
        ),
        steps=[
            types.StepBasedLLMMetricStep(
                step_id="constraints",
                prompt_template=(
                    "List the user's constraints in this trace as a JSON array"
                    " of strings.\n{agent_eval_data}"
                ),
            ),
            types.StepBasedLLMMetricStep(
                step_id="score",
                prompt_template=(
                    "Constraints: {step.constraints.output}\nTrace:"
                    " {agent_eval_data}\nRate from 1 to 5 how well the final"
                    ' bookings meet the constraints. Return JSON {"score":'
                    ' <int>, "explanation": <str>}.'
                ),
            ),
        ],
    )

    evaluation_result = client.evals.evaluate(dataset=_eval_dataset(), metrics=[metric])

    _assert_result(evaluation_result, "budget_adherence")


def test_code_preprocessor_and_parser(client):
    """Tests a coordinator-only metric with a code preprocessor and parser."""
    client._api_client._http_options.api_version = "v1beta1"
    metric = types.StepBasedLLMMetric(
        name="coordinator_relay",
        preprocessor=types.AgentDataPreprocessor(
            code_config=types.CodePreprocessorConfig(code=PREPROCESS_CODE)
        ),
        steps=[
            types.StepBasedLLMMetricStep(
                step_id="relay",
                prompt_template=(
                    "This trace shows only the user and the coordinator.\n"
                    "{agent_eval_data}\nRate from 1 to 5 how accurately the"
                    " coordinator relayed the bookings. End with the digit."
                ),
                autorater_config=genai_types.AutoraterConfig(sampling_count=2),
                response_parser_config=types.ResponseParserConfig(
                    custom_code_parser_config=types.CustomCodeParserConfig(
                        parsing_function=PARSE_CODE
                    )
                ),
            )
        ],
    )

    evaluation_result = client.evals.evaluate(dataset=_eval_dataset(), metrics=[metric])

    _assert_result(evaluation_result, "coordinator_relay")


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.evaluate",
)
