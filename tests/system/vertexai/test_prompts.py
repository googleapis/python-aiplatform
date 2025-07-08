# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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
# pylint: disable=protected-access, g-multiple-import
"""System tests for GenAI prompts."""

from google.cloud import aiplatform
from vertexai import generative_models
from vertexai.generative_models import (
    GenerationConfig,
    SafetySetting,
    ToolConfig,
)
from vertexai.preview import prompts
from vertexai.preview.prompts import Prompt

from tests.system.aiplatform import e2e_base
from google import auth

_REQUEST_FUNCTION_PARAMETER_SCHEMA_STRUCT = {
    "type": "object",
    "properties": {
        "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA",
        },
        "unit": {
            "type": "string",
            "enum": [
                "celsius",
                "fahrenheit",
            ],
        },
    },
    "required": ["location"],
}


class TestPrompts(e2e_base.TestEndToEnd):
    """System tests for prompts."""

    _temp_prefix = "temp_prompts_test_"

    def setup_method(self):
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            credentials=credentials,
        )

    def test_create_prompt_with_variables(self):
        # Create local Prompt
        prompt = Prompt(
            prompt_data="Hello, {name}! Today is {day}. How are you?",
            variables=[
                {"name": "Alice", "day": "Monday"},
                {"name": "Bob", "day": "Tuesday"},
            ],
            generation_config=GenerationConfig(temperature=0.1),
            model_name="gemini-1.5-pro-002",
            safety_settings=[
                SafetySetting(
                    category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    method=SafetySetting.HarmBlockMethod.SEVERITY,
                )
            ],
            system_instruction="Please answer in a short sentence.",
        )

        # Generate content using the assembled prompt for each variable set.
        for i in range(len(prompt.variables)):
            prompt.generate_content(
                contents=prompt.assemble_contents(**prompt.variables[i])
            )

        # Save Prompt to online resource. Returns a new Prompt object associated with the online resource
        prompt1 = prompts.create_version(prompt=prompt)

        # Only new prompt should be associated with a prompt resource
        assert prompt1.prompt_id
        assert not prompt.prompt_id

        # Update prompt and save a new version
        prompt1.prompt_data = "Hi, {name}! How are you? Today is {day}."
        prompt2 = prompts.create_version(prompt=prompt1, version_name="v2")
        assert prompt2.prompt_id == prompt1.prompt_id
        assert prompt2.version_id != prompt1.version_id

        # Restore previous version
        metadata = prompts.restore_version(
            prompt_id=prompt2.prompt_id, version_id=prompt1.version_id
        )
        assert metadata.prompt_id == prompt2.prompt_id
        assert metadata.version_id != prompt2.version_id

        # List prompt versions
        versions_metadata = prompts.list_versions(prompt_id=metadata.prompt_id)
        assert len(versions_metadata) == 3

        # Delete the prompt resource
        prompts.delete(prompt_id=prompt2.prompt_id)

    def test_create_prompt_with_function_calling(self):
        # Create local Prompt
        get_current_weather_func = generative_models.FunctionDeclaration(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters=_REQUEST_FUNCTION_PARAMETER_SCHEMA_STRUCT,
        )
        weather_tool = generative_models.Tool(
            function_declarations=[get_current_weather_func],
        )

        tool_config = ToolConfig(
            function_calling_config=ToolConfig.FunctionCallingConfig(
                mode=ToolConfig.FunctionCallingConfig.Mode.ANY,
                allowed_function_names=["get_current_weather"],
            )
        )

        prompt = Prompt(
            prompt_data="What is the weather like in Boston?",
            tools=[weather_tool],
            tool_config=tool_config,
            model_name="gemini-1.5-pro-002",
        )

        # (Optional) Create a separate prompt resource to save the version to
        prompt_temp = Prompt(model_name="gemini-1.5-pro-002")
        prompt_temp1 = prompts.create_version(prompt=prompt_temp, version_name="empty")

        # Create a new version to an existing prompt
        prompt1 = prompts.create_version(
            prompt=prompt, prompt_id=prompt_temp1.prompt_id, version_name="fc"
        )

        # Delete the prompt resource
        prompts.delete(prompt_id=prompt1.prompt_id)

    def test_get_prompt_with_variables(self):
        # List prompts
        prompts_list = prompts.list()
        assert prompts_list

        # Get prompt created in UI
        prompt_id = "3217694940163211264"
        prompt = prompts.get(prompt_id=prompt_id)
        assert prompt.prompt_id == prompt_id
        assert prompt.prompt_data
        assert prompt.generation_config
        assert prompt.system_instruction
        # UI has a bug where safety settings are not saved
        # assert prompt.safety_settings

        # Generate content using the assembled prompt for each variable set.
        for i in range(len(prompt.variables)):
            response = prompt.generate_content(
                contents=prompt.assemble_contents(**prompt.variables[i])
            )
            assert response.text

    def test_get_prompt_with_function_calling(self):
        # List prompts
        prompts_list = prompts.list()
        assert prompts_list

        # Get prompt created in UI
        prompt_id = "1173060709337006080"
        prompt = prompts.get(prompt_id=prompt_id)
        assert prompt.prompt_id == prompt_id
        assert prompt.tools

        # Generate content using the prompt
        response = prompt.generate_content(
            model_name="gemini-1.5-pro-002", contents=prompt.assemble_contents()
        )
        assert response
