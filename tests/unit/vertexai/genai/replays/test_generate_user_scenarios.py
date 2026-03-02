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
from vertexai import types
import pytest


def test_gen_user_scenarios(client):
    """Tests that generate_user_scenarios() correctly calls the API and parses the response."""
    eval_dataset = client.evals.generate_user_scenarios(
        agents={
            "booking-agent": types.evals.AgentConfig(
                agent_id="booking-agent",
                agent_type="service_agent",
                description="An agent capable of booking flights and hotels.",
                instruction="You are a helpful travel assistant. Use tools to find flights.",
                tools=[
                    {
                        "function_declarations": [
                            {
                                "name": "search_flights",
                                "description": "Search for available flights.",
                            }
                        ]
                    }
                ],
            )
        },
        user_scenario_generation_config=types.evals.UserScenarioGenerationConfig(
            user_scenario_count=2,
            simulation_instruction=(
                "Generate scenarios where the user tries to book a flight but"
                " changes their mind about the destination."
            ),
            environment_data="Today is Monday. Flights to Paris are available.",
            model_name="gemini-2.5-flash",
        ),
        root_agent_id="booking-agent",
    )
    assert isinstance(eval_dataset, types.EvaluationDataset)
    assert len(eval_dataset.eval_cases) == 2
    assert (
        eval_dataset.eval_cases[0].user_scenario.starting_prompt
        == "I want to find a flight from New York to London."
    )
    assert (
        eval_dataset.eval_cases[0].user_scenario.conversation_plan
        == "Actually, I meant Paris, not London. Please search for flights to Paris."
    )


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_gen_user_scenarios_async(client):
    """Tests that generate_user_scenarios() async correctly calls the API and parses the response."""
    eval_dataset = await client.aio.evals.generate_user_scenarios(
        agents={
            "booking-agent": types.evals.AgentConfig(
                agent_id="booking-agent",
                agent_type="service_agent",
                description="An agent capable of booking flights and hotels.",
                instruction="You are a helpful travel assistant. Use tools to find flights.",
                tools=[
                    {
                        "function_declarations": [
                            {
                                "name": "search_flights",
                                "description": "Search for available flights.",
                            }
                        ]
                    }
                ],
            )
        },
        user_scenario_generation_config=types.evals.UserScenarioGenerationConfig(
            user_scenario_count=2,
            simulation_instruction=(
                "Generate scenarios where the user tries to book a flight but"
                " changes their mind about the destination."
            ),
            environment_data="Today is Monday. Flights to Paris are available.",
            model_name="gemini-2.5-flash",
        ),
        root_agent_id="booking-agent",
    )
    assert isinstance(eval_dataset, types.EvaluationDataset)
    assert len(eval_dataset.eval_cases) == 2
    assert (
        eval_dataset.eval_cases[1].user_scenario.starting_prompt
        == "Find me a flight from Boston to Rome for next month."
    )
    assert (
        eval_dataset.eval_cases[1].user_scenario.conversation_plan
        == "Wait, change of plans. I need to go to Milan instead, and it needs to be a round trip, returning two weeks after departure."
    )


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.generate_user_scenarios",
)
