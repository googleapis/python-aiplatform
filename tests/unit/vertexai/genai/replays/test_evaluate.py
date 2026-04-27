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
import re
from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types
from google.genai import types as genai_types
import pandas as pd


def test_evaluation_result(client):
    """Tests that evaluate() produces a correctly structured EvaluationResult."""
    prompts_df = pd.DataFrame({"prompt": ["What is Taylor Swift's most recent album?"]})

    eval_dataset = client.evals.run_inference(
        model="gemini-2.5-flash",
        src=prompts_df,
    )

    metrics_to_run = [
        types.RubricMetric.TEXT_QUALITY,
    ]

    evaluation_result = client.evals.evaluate(
        dataset=eval_dataset,
        metrics=metrics_to_run,
    )

    assert isinstance(evaluation_result, types.EvaluationResult)

    assert evaluation_result.summary_metrics is not None
    assert len(evaluation_result.summary_metrics) > 0
    for summary in evaluation_result.summary_metrics:
        assert isinstance(summary, types.AggregatedMetricResult)
        assert summary.metric_name is not None
        assert summary.mean_score is not None

    assert evaluation_result.eval_case_results is not None
    assert len(evaluation_result.eval_case_results) > 0
    for case_result in evaluation_result.eval_case_results:
        assert isinstance(case_result, types.EvalCaseResult)
        assert case_result.eval_case_index is not None
        assert case_result.response_candidate_results is not None


def test_evaluation_byor(client):
    """Tests that evaluate() with BYOR (Bring-Your-Own Response) produces a correctly structured EvaluationResult."""
    byor_df = pd.DataFrame(
        {
            "prompt": [
                "Write a simple story about a dinosaur",
                "Generate a poem about Vertex AI",
            ],
            "response": [
                "Once upon a time, there was a T-Rex named Rexy.",
                "In clouds of code, a mind of silicon born...",
            ],
        }
    )

    metrics_to_run = [
        types.RubricMetric.GENERAL_QUALITY,
    ]

    evaluation_result = client.evals.evaluate(
        dataset=byor_df,
        metrics=metrics_to_run,
    )

    assert isinstance(evaluation_result, types.EvaluationResult)

    assert evaluation_result.summary_metrics is not None
    assert len(evaluation_result.summary_metrics) > 0
    for summary in evaluation_result.summary_metrics:
        assert isinstance(summary, types.AggregatedMetricResult)
        assert summary.metric_name is not None
        assert summary.mean_score is not None
        assert summary.pass_rate is not None

    assert evaluation_result.eval_case_results is not None
    assert len(evaluation_result.eval_case_results) > 0
    for case_result in evaluation_result.eval_case_results:
        assert isinstance(case_result, types.EvalCaseResult)
        assert case_result.eval_case_index is not None
        assert case_result.response_candidate_results is not None


def test_evaluation_agent_data(client):
    """Tests evaluate method with AgentData."""
    client._api_client._http_options.api_version = "v1beta1"

    agent_data = types.evals.AgentData(
        agents={
            "coordinator": types.evals.AgentConfig(
                agent_id="coordinator",
                agent_type="RouterAgent",
                description="Root agent that delegates to specialists.",
                instruction=(
                    "You are a travel coordinator. Delegate flight tasks to"
                    " 'flight_bot' and hotel tasks to 'hotel_bot'."
                ),
                sub_agents=["flight_bot", "hotel_bot"],
                tools=[
                    genai_types.Tool(
                        function_declarations=[
                            genai_types.FunctionDeclaration(
                                name="delegate_to_agent",
                                description=("Delegates conversation to a sub-agent."),
                            )
                        ]
                    )
                ],
            ),
            "flight_bot": types.evals.AgentConfig(
                agent_id="flight_bot",
                agent_type="SpecialistAgent",
                description="Handles flight searches.",
                instruction="Search for flights using the available tools.",
                tools=[
                    genai_types.Tool(
                        function_declarations=[
                            genai_types.FunctionDeclaration(
                                name="search_flights",
                                description=(
                                    "Finds flights based on origin and" " destination."
                                ),
                            )
                        ]
                    )
                ],
            ),
            "hotel_bot": types.evals.AgentConfig(
                agent_id="hotel_bot",
                agent_type="SpecialistAgent",
                description="Handles hotel searches.",
                instruction="Search for hotels using the available tools.",
                tools=[
                    genai_types.Tool(
                        function_declarations=[
                            genai_types.FunctionDeclaration(
                                name="search_hotels",
                                description="Finds hotels in a given location.",
                            )
                        ]
                    )
                ],
            ),
        },
        turns=[
            types.evals.ConversationTurn(
                turn_index=0,
                events=[
                    types.evals.AgentEvent(
                        author="user",
                        content=genai_types.Content(
                            role="user",
                            parts=[
                                genai_types.Part(
                                    text=(
                                        "I need to book a flight to NYC for next"
                                        " Monday."
                                    )
                                )
                            ],
                        ),
                    ),
                    types.evals.AgentEvent(
                        author="coordinator",
                        content=genai_types.Content(
                            role="model",
                            parts=[
                                genai_types.Part(
                                    function_call=genai_types.FunctionCall(
                                        name="delegate_to_agent",
                                        args={"agent_name": "flight_bot"},
                                    )
                                )
                            ],
                        ),
                    ),
                    types.evals.AgentEvent(
                        author="flight_bot",
                        content=genai_types.Content(
                            role="model",
                            parts=[
                                genai_types.Part(
                                    function_call=genai_types.FunctionCall(
                                        name="search_flights",
                                        args={
                                            "destination": "NYC",
                                            "date": "next Monday",
                                        },
                                    )
                                )
                            ],
                        ),
                    ),
                    types.evals.AgentEvent(
                        author="flight_bot",
                        content=genai_types.Content(
                            role="tool",
                            parts=[
                                genai_types.Part(
                                    function_response=genai_types.FunctionResponse(
                                        name="search_flights",
                                        response={
                                            "flights": [
                                                {
                                                    "id": "UA100",
                                                    "price": "$300",
                                                }
                                            ]
                                        },
                                    )
                                )
                            ],
                        ),
                    ),
                    types.evals.AgentEvent(
                        author="flight_bot",
                        content=genai_types.Content(
                            role="model",
                            parts=[
                                genai_types.Part(
                                    text="I found flight UA100 to NYC for $300."
                                )
                            ],
                        ),
                    ),
                ],
            ),
            types.evals.ConversationTurn(
                turn_index=1,
                events=[
                    types.evals.AgentEvent(
                        author="user",
                        content=genai_types.Content(
                            role="user",
                            parts=[
                                genai_types.Part(
                                    text=(
                                        "Great, book that. I also need a hotel"
                                        " there."
                                    )
                                )
                            ],
                        ),
                    ),
                    types.evals.AgentEvent(
                        author="coordinator",
                        content=genai_types.Content(
                            role="model",
                            parts=[
                                genai_types.Part(
                                    function_call=genai_types.FunctionCall(
                                        name="delegate_to_agent",
                                        args={"agent_name": "hotel_bot"},
                                    )
                                )
                            ],
                        ),
                    ),
                    types.evals.AgentEvent(
                        author="hotel_bot",
                        content=genai_types.Content(
                            role="model",
                            parts=[
                                genai_types.Part(
                                    function_call=genai_types.FunctionCall(
                                        name="search_hotels",
                                        args={"location": "NYC"},
                                    )
                                )
                            ],
                        ),
                    ),
                    types.evals.AgentEvent(
                        author="hotel_bot",
                        content=genai_types.Content(
                            role="tool",
                            parts=[
                                genai_types.Part(
                                    function_response=genai_types.FunctionResponse(
                                        name="search_hotels",
                                        response={
                                            "hotels": [
                                                {
                                                    "name": "Central Park Hotel",
                                                    "rating": 4.5,
                                                }
                                            ]
                                        },
                                    )
                                )
                            ],
                        ),
                    ),
                    types.evals.AgentEvent(
                        author="hotel_bot",
                        content=genai_types.Content(
                            role="model",
                            parts=[
                                genai_types.Part(
                                    text="I recommend the Central Park Hotel."
                                )
                            ],
                        ),
                    ),
                ],
            ),
        ],
    )

    # Create the EvalCase and wrap it in an EvaluationDataset
    eval_case = types.EvalCase(agent_data=agent_data)
    eval_dataset = types.EvaluationDataset(eval_cases=[eval_case])

    metrics = [
        types.RubricMetric.MULTI_TURN_TRAJECTORY_QUALITY,
    ]

    evaluation_result = client.evals.evaluate(dataset=eval_dataset, metrics=metrics)

    assert isinstance(evaluation_result, types.EvaluationResult)

    assert evaluation_result.summary_metrics is not None
    assert len(evaluation_result.summary_metrics) > 0
    for summary in evaluation_result.summary_metrics:
        assert isinstance(summary, types.AggregatedMetricResult)
        assert summary.metric_name is not None
        assert summary.mean_score is not None

    assert evaluation_result.eval_case_results is not None
    assert len(evaluation_result.eval_case_results) > 0
    for case_result in evaluation_result.eval_case_results:
        assert isinstance(case_result, types.EvalCaseResult)
        assert case_result.eval_case_index is not None
        assert case_result.response_candidate_results is not None


def test_evaluation_metric_resource_name(client):
    """Tests with a metric resource name in types.Metric."""
    client._api_client._http_options.api_version = "v1beta1"
    tone_check_metric = types.LLMMetric(
        name="tone_check",
        prompt_template="""Analyze the tone of the response based on these two criteria:\n
          1. Professionalism: The response should use appropriate language and maintain a business-like demeanor.\n
          2. Empathy: The response should acknowledge the user's feelings and show understanding.\n\n
          Prompt: {agent_data.turns[0].events[0]}
          Response: {agent_data.turns[0].events[1]}
          Return ONLY a JSON list of objects for these two properties:
          [{"property": "Professionalism", "verdict": true, "reasoning": "..."},
          {"property": "Empathy", "verdict": true, "reasoning": "..."}]
        """,
        result_parsing_function="""
import json, re
def parse_results(responses):
    text = responses[0]
    # Use robust regex to find the JSON list block
    match = re.search("[\\[].*[]]", text, re.DOTALL)
    if not match: return {"score": 0.0, "explanation": "No valid JSON found"}

    try:
        data = json.loads(match.group(0))
        # Calculate an overall score (e.g., average of verdicts)
        passed_count = sum(1 for r in data if r.get("verdict", False))
        total_count = len(data)
        score = passed_count / total_count if total_count > 0 else 0.0

        # Consolidate reasoning into a single explanation string
        explanation = "\\n".join([f"{r.get('property')}: {r.get('reasoning')}" for r in data])

        # IMPORTANT: Return a dictionary, not a list
        return {
            "score": float(score),
            "explanation": explanation
        }
    except Exception as e:
        return {"score": 0.0, "explanation": f"Parsing failed: {str(e)}"}
""",
    )
    metric_resource_name = client.evals.create_evaluation_metric(
        metric=tone_check_metric,
    )
    assert isinstance(metric_resource_name, str)
    assert re.match(
        r"^projects/[^/]+/locations/[^/]+/evaluationMetrics/[^/]+$",
        metric_resource_name,
    )
    agent_data = types.evals.AgentData(
        turns=[
            types.evals.ConversationTurn(
                turn_index=0,
                events=[
                    types.evals.AgentEvent(
                        author="user",
                        content=genai_types.Content(
                            role="user",
                            parts=[
                                genai_types.Part(
                                    text=("Write a simple story about a dinosaur")
                                )
                            ],
                        ),
                    ),
                    types.evals.AgentEvent(
                        author="model",
                        content=genai_types.Content(
                            role="model",
                            parts=[
                                genai_types.Part(
                                    text="Once upon a time, there was a T-Rex named Rexy."
                                )
                            ],
                        ),
                    ),
                ],
            ),
        ],
    )
    byor_df = pd.DataFrame(
        {
            "agent_data": [agent_data],
        }
    )
    metric = types.Metric(
        name="my_custom_metric", metric_resource_name=metric_resource_name
    )
    evaluation_result = client.evals.evaluate(
        dataset=byor_df,
        metrics=[metric],
    )
    assert isinstance(evaluation_result, types.EvaluationResult)
    assert evaluation_result.eval_case_results is not None
    assert len(evaluation_result.eval_case_results) == 1
    assert evaluation_result.summary_metrics[0].metric_name == "my_custom_metric"
    assert evaluation_result.summary_metrics[0].mean_score is not None
    assert evaluation_result.summary_metrics[0].num_cases_valid == 1
    assert evaluation_result.summary_metrics[0].num_cases_error == 0

    case_result = evaluation_result.eval_case_results[0]
    assert case_result.response_candidate_results is not None
    assert len(case_result.response_candidate_results) == 1

    metric_result = case_result.response_candidate_results[0].metric_results[
        "my_custom_metric"
    ]
    assert metric_result.score is not None
    assert metric_result.score >= 0.0
    assert metric_result.error_message is None


def test_evaluation_single_turn_agent_data(client):
    """Tests single-turn AgentData eval with agent quality metrics."""
    client._api_client._http_options.api_version = "v1beta1"

    weather_agent = {
        "weather_bot": types.evals.AgentConfig(
            agent_id="weather_bot",
            agent_type="SpecialistAgent",
            description="Handles weather queries.",
            instruction=(
                "You are a weather assistant. Use the get_weather tool to"
                " answer weather questions."
            ),
            tools=[
                genai_types.Tool(
                    function_declarations=[
                        genai_types.FunctionDeclaration(
                            name="get_weather",
                            description=(
                                "Gets the current weather for a given location."
                            ),
                        )
                    ]
                )
            ],
        ),
    }

    eval_case = types.EvalCase(
        eval_case_id="successful-tool-use",
        agent_data=types.evals.AgentData(
            agents=weather_agent,
            turns=[
                types.evals.ConversationTurn(
                    turn_index=0,
                    events=[
                        types.evals.AgentEvent(
                            author="user",
                            content=genai_types.Content(
                                role="user",
                                parts=[
                                    genai_types.Part(
                                        text="What is the weather in Tokyo?"
                                    )
                                ],
                            ),
                        ),
                        types.evals.AgentEvent(
                            author="weather_bot",
                            content=genai_types.Content(
                                role="model",
                                parts=[
                                    genai_types.Part(
                                        function_call=genai_types.FunctionCall(
                                            id="tool_call_0",
                                            name="get_weather",
                                            args={"location": "Tokyo"},
                                        )
                                    )
                                ],
                            ),
                        ),
                        types.evals.AgentEvent(
                            author="weather_bot",
                            content=genai_types.Content(
                                role="tool",
                                parts=[
                                    genai_types.Part(
                                        function_response=genai_types.FunctionResponse(
                                            id="tool_call_0",
                                            name="get_weather",
                                            response={"weather": "75F and sunny"},
                                        )
                                    )
                                ],
                            ),
                        ),
                        types.evals.AgentEvent(
                            author="weather_bot",
                            content=genai_types.Content(
                                role="model",
                                parts=[
                                    genai_types.Part(
                                        text=(
                                            "It is currently 75F and sunny in" " Tokyo."
                                        )
                                    )
                                ],
                            ),
                        ),
                    ],
                )
            ],
        ),
    )

    eval_dataset = types.EvaluationDataset(eval_cases=[eval_case])

    metrics = [
        types.RubricMetric.FINAL_RESPONSE_QUALITY,
        types.RubricMetric.TOOL_USE_QUALITY,
        types.RubricMetric.HALLUCINATION,
        types.RubricMetric.SAFETY,
        types.RubricMetric.GENERAL_QUALITY,
        types.RubricMetric.TEXT_QUALITY,
    ]

    evaluation_result = client.evals.evaluate(dataset=eval_dataset, metrics=metrics)

    assert isinstance(evaluation_result, types.EvaluationResult)
    assert evaluation_result.summary_metrics is not None
    assert len(evaluation_result.summary_metrics) > 0
    for summary in evaluation_result.summary_metrics:
        assert isinstance(summary, types.AggregatedMetricResult)
        assert summary.metric_name is not None

    assert evaluation_result.eval_case_results is not None
    assert len(evaluation_result.eval_case_results) == 1


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.evaluate",
)
