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

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types
from google.genai import types as genai_types

pytest.importorskip(
    "google.adk", reason="google-adk not installed, skipping ADK agent tests"
)
from google.adk.agents import (  # noqa: E402
    LlmAgent,
)  # pylint: disable=g-import-not-at-top,g-bad-import-order


def test_inference_with_eval_cases_multi_turn_agent_data(client):
    """Tests run_inference with multi-turn agent_data in eval_cases.

    Verifies that run_inference() accepts an EvaluationDataset with
    eval_cases containing agent_data (no eval_dataset_df). The agent_data
    has 2 turns: turn 0 is a completed user+agent exchange (history),
    turn 1 is a new user query. The agent should see the history and
    respond to the final query in context.
    """
    agent = LlmAgent(
        name="test_agent",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant. Answer questions concisely.",
    )

    eval_case = types.EvalCase(
        agent_data=types.evals.AgentData(
            turns=[
                types.evals.ConversationTurn(
                    turn_index=0,
                    events=[
                        types.evals.AgentEvent(
                            author="user",
                            content=genai_types.Content(
                                role="user",
                                parts=[genai_types.Part(text="My name is Alice.")],
                            ),
                        ),
                        types.evals.AgentEvent(
                            author="test_agent",
                            content=genai_types.Content(
                                role="model",
                                parts=[
                                    genai_types.Part(
                                        text="Hello Alice! How can I help you?"
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
                                parts=[genai_types.Part(text="What is my name?")],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )
    eval_dataset = types.EvaluationDataset(eval_cases=[eval_case])

    inference_result = client.evals.run_inference(
        agent=agent,
        src=eval_dataset,
    )
    assert isinstance(inference_result, types.EvaluationDataset)
    assert inference_result.eval_dataset_df is not None
    assert "agent_data" in inference_result.eval_dataset_df.columns


def test_inference_with_eval_cases_agent_engine_agent_data(client):
    """Tests N+1 inference with agent_data via remote Agent Engine."""
    agent_engine = client.agent_engines.get(
        name="projects/977012026409/locations/us-central1"
        "/reasoningEngines/7188347537655332864"
    )

    eval_case = types.EvalCase(
        agent_data=types.evals.AgentData(
            turns=[
                types.evals.ConversationTurn(
                    turn_index=0,
                    events=[
                        types.evals.AgentEvent(
                            author="user",
                            content=genai_types.Content(
                                role="user",
                                parts=[genai_types.Part(text="My name is Bob.")],
                            ),
                        ),
                        types.evals.AgentEvent(
                            author="model",
                            content=genai_types.Content(
                                role="model",
                                parts=[
                                    genai_types.Part(text="Hi Bob! Nice to meet you.")
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
                                parts=[genai_types.Part(text="What is my name?")],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )
    eval_dataset = types.EvaluationDataset(eval_cases=[eval_case])

    inference_result = client.evals.run_inference(
        agent=agent_engine,
        src=eval_dataset,
    )
    assert isinstance(inference_result, types.EvaluationDataset)
    assert inference_result.eval_dataset_df is not None
    assert "agent_data" in inference_result.eval_dataset_df.columns


def test_inference_with_prompt_column_local_agent(client):
    """Tests run_inference with a prompt column and a local ADK agent.

    Verifies the existing prompt-based inference path: a DataFrame with
    a 'prompt' column is passed alongside a local LlmAgent.  The agent
    should respond to the prompt normally.
    """
    import pandas as pd

    agent = LlmAgent(
        name="prompt_agent",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant. Answer questions concisely.",
    )

    prompt_df = pd.DataFrame(
        {
            "prompt": ["What is the capital of France?"],
        }
    )
    eval_dataset = types.EvaluationDataset(eval_dataset_df=prompt_df)

    inference_result = client.evals.run_inference(
        agent=agent,
        src=eval_dataset,
    )
    assert isinstance(inference_result, types.EvaluationDataset)
    result_df = inference_result.eval_dataset_df
    assert result_df is not None
    assert "response" in result_df.columns
    # The response should be a non-empty string (actual model answer).
    response_val = result_df["response"].iloc[0]
    assert response_val is not None
    assert isinstance(response_val, str)
    assert len(response_val) > 0


def test_inference_with_completed_and_incomplete_agent_data(client):
    """Tests run_inference with a mix of completed and N+1 agent traces.

    Provides two eval_cases:
    - Row 0: completed trace (last event from agent) — BYOD, no inference.
    - Row 1: incomplete trace (last event from user) — N+1 inference.

    The completed row should return the existing agent response without
    making any API calls.  The N+1 row should run inference normally.
    """
    agent = LlmAgent(
        name="mixed_agent",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant. Answer questions concisely.",
    )

    # Row 0: Completed trace — last event is from the agent.
    completed_case = types.EvalCase(
        agent_data=types.evals.AgentData(
            turns=[
                types.evals.ConversationTurn(
                    turn_index=0,
                    events=[
                        types.evals.AgentEvent(
                            author="user",
                            content=genai_types.Content(
                                role="user",
                                parts=[genai_types.Part(text="What color is the sky?")],
                            ),
                        ),
                        types.evals.AgentEvent(
                            author="mixed_agent",
                            content=genai_types.Content(
                                role="model",
                                parts=[genai_types.Part(text="The sky is blue.")],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    # Row 1: N+1 trace — last event is from the user.
    n_plus_1_case = types.EvalCase(
        agent_data=types.evals.AgentData(
            turns=[
                types.evals.ConversationTurn(
                    turn_index=0,
                    events=[
                        types.evals.AgentEvent(
                            author="user",
                            content=genai_types.Content(
                                role="user",
                                parts=[
                                    genai_types.Part(text="My favorite number is 7.")
                                ],
                            ),
                        ),
                        types.evals.AgentEvent(
                            author="mixed_agent",
                            content=genai_types.Content(
                                role="model",
                                parts=[genai_types.Part(text="Got it, 7!")],
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
                                    genai_types.Part(text="What is my favorite number?")
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    eval_dataset = types.EvaluationDataset(eval_cases=[completed_case, n_plus_1_case])

    inference_result = client.evals.run_inference(
        agent=agent,
        src=eval_dataset,
    )
    assert isinstance(inference_result, types.EvaluationDataset)
    result_df = inference_result.eval_dataset_df
    assert result_df is not None
    assert len(result_df) == 2

    # Row 0 (completed trace): response should contain the existing
    # agent answer — "The sky is blue."
    row0_response = result_df["response"].iloc[0]
    assert row0_response is not None
    assert "blue" in row0_response.lower()

    # Row 1 (N+1 inference): response should be a non-empty string
    # from the model (actual inference).
    row1_response = result_df["response"].iloc[1]
    assert row1_response is not None
    assert isinstance(row1_response, str)
    assert len(row1_response) > 0


def test_inference_with_gemini_agent(client):
    """Tests run_inference() against a Gemini Agents API agent.

    Drives the Interactions API client-side (one interaction per prompt) and
    returns an EvaluationDataset with prompt/response/interaction_id/agent_data.
    """
    import pandas as pd

    prompts_df = pd.DataFrame({"prompt": ["What is Taylor Swift's most recent album?"]})

    eval_dataset = client.evals.run_inference(
        src=prompts_df,
        agent="projects/model-evaluation-dev/locations/global/agents/test-agent-eval",
    )

    assert isinstance(eval_dataset, types.EvaluationDataset)
    result_df = eval_dataset.eval_dataset_df
    assert result_df is not None
    assert set(["prompt", "response", "interaction_id", "agent_data"]).issubset(
        set(result_df.columns)
    )
    assert len(result_df) == 1
    assert result_df["interaction_id"].iloc[0]


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.run_inference",
)
