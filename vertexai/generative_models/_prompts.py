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

from vertexai.generative_models import Content, Part
from vertexai.generative_models._generative_models import (
    PartsType,
    Image,
    _to_content,
)

import re
from typing import (
    Any,
    Dict,
    List,
    Union,
)


VARIABLE_NAME_REGEX = r"(\{[^\W0-9]\w*\})"


class Prompt:
    """A prompt which may be a template with variables.

    The `Prompt` class allows users to define a template string with
    variables represented in curly braces `{variable}`. The variable
    name must be a valid Python variable name (no spaces, must start with a
    letter). These placeholders can be replaced with specific values using the
    `assemble` method, providing flexibility in generating dynamic prompts.

    Usage:

        ```
        prompt = Prompt(
            prompt_data="Hello, {name}! Today is {day}. How are you?",
            variables={"name": "Alice", "day": "Monday"}
        )
        prompt.assemble()
        prompt.to_content()
        ```
    """

    def __init__(
        self,
        prompt_data: PartsType,
        variables: Dict[str, Union[str, List[Part]]],
    ):
        """Initializes the Prompt with a given prompt, and variables.

        Args:
            prompt: A PartsType prompt which may be a template with variables or a prompt with no variables.
            variables: A dictionary containing the variable names and values.
        """
        self._check_valid_prompt_data(prompt_data)
        self.prompt_data = prompt_data
        self.variables = self._format_variables(variables)
        self._assembled_prompt = None

    def set_prompt(self, prompt_data: Union[str, List[Part]]) -> None:
        """Overwrites the existing prompt_data.

        Args:
            prompt_data: A string or List[Part] prompt.
        """
        self._check_valid_prompt_data(prompt_data)
        self.prompt_data = prompt_data
        self._assembled_prompt = None

    def set_variables(self, variables: Dict[str, Union[str, List[Part]]]) -> None:
        """Overwrites the existing variables dictionary.

        Args:
            variables: A dictionary containing the variable names and values.
        """
        self.variables = self._format_variables(variables)
        self._assembled_prompt = None

    def _format_variables(
        self, variables: Dict[str, Union[str, List[Part]]]
    ) -> Dict[str, List[Part]]:
        """Formats the variables values to be List[Part]."""
        self._check_valid_variables(variables)
        for key in variables.keys():
            if isinstance(variables[key], str):
                variables[key] = [Part.from_text(variables[key])]
        return variables

    def _is_list_type(self, obj: Any, T: Any) -> bool:
        return isinstance(obj, list) and all(isinstance(s, T) for s in obj)

    def _check_valid_prompt_data(self, prompt_data: Any) -> None:
        if (
            self._is_list_type(prompt_data, str)
            or self._is_list_type(prompt_data, Image)
            or self._is_list_type(prompt_data, Part)
        ):
            return
        elif (
            isinstance(prompt_data, str)
            or isinstance(prompt_data, Image)
            or isinstance(prompt_data, Part)
        ):
            return
        raise ValueError("Prompt data must be a PartsType object.")

    def _check_valid_variables(self, variables: Any) -> None:
        """Dict must be a Dict[str, Union[str, List[Part]]."""
        valid = True
        if isinstance(variables, dict):
            for key, value in variables.items():
                if not isinstance(key, str):
                    valid = False
                if not (isinstance(value, str) or self._is_list_type(value, Part)):
                    valid = False
        else:
            valid = False
        if not valid:
            raise ValueError(
                "Variable values must be a string or a list of Part objects."
            )

    def assemble(self, **kwargs) -> None:
        """Replaces only the provided variables in the template with specific values.

        Args:
            **kwargs: Keyword arguments where keys are placeholder names and values
              are the replacements.

        Returns:
            A new PromptTemplate instance with the updated template string.

        Usage:
            ```
            prompt = Prompt(
                prompt_data="Hello, {name}! Today is {day}. How are you?",
                variables={"name": "Alice"}
            )
            prompt.assemble()
            prompt.to_contents()
            # Returns "Hello, Alice! Today is {day}. How are you?" as List[Content]
            prompt.assemble(day="Monday")
            prompt.to_contents()
            # Returns "Hello, Alice! Today is Monday. How are you?" as List[Content]
            prompt.assemble(name="Bob")
            prompt.to_contents()
            # Returns "Hello, Bob! Today is Monday. How are you?" as List[Content]
            ```
        """
        # Python Dict update will overwrite existing key values.
        self.variables.update(kwargs)

        # Step 1) Convert the variables values to List[Part].
        formatted_variables = self._format_variables(self.variables)

        # Step 2) Assemble the prompt
        assembled_prompt = []
        if self._is_list_type(self.prompt_data, Union[str, Image, Part]):
            # User inputted a List of Parts as prompt_data.
            for part in self.prompt_data:
                assembled_prompt.extend(
                    self._assemble_singular_part(part, formatted_variables)
                )
        elif isinstance(self.prompt_data, PartsType):
            # User inputted a single str, Image, or Part as prompt_data.
            assembled_prompt.extend(
                self._assemble_singular_part(self.prompt_data, formatted_variables)
            )
        else:
            raise ValueError("Prompt data must be PartsType.")

        # Step 3) Simplify adjacent string Parts
        simplified_assembled_prompt = [assembled_prompt[0]]
        for i in range(1, len(assembled_prompt)):
            # If the previous Part and current Part is a string, concatenate them.
            try:
                prev_text = simplified_assembled_prompt[-1].text
                curr_text = assembled_prompt[i].text
                if prev_text and curr_text:
                    simplified_assembled_prompt[-1] = Part.from_text(
                        prev_text + curr_text
                    )
                else:
                    simplified_assembled_prompt.append(assembled_prompt[i])
            except AttributeError:
                simplified_assembled_prompt.append(assembled_prompt[i])
                continue

        # Step 4) Wrap List[Part] as a single Content object.
        self._assembled_prompt = [
            Content(
                parts=simplified_assembled_prompt,
                role="user",
            )
        ]

    def _assemble_singular_part(
        self,
        prompt_data_part: Union[str, Image, Part],
        formatted_variables: Dict[str, List[Part]],
    ) -> List[Part]:
        """Assemble a str, Image, or Part."""
        if isinstance(prompt_data_part, Image):
            # Templating is not supported for Image prompt_data.
            return [Part.from_image(prompt_data_part)]
        elif isinstance(prompt_data_part, str):
            # Assemble a single string
            return self._assemble_single_str(prompt_data_part, formatted_variables)
        elif isinstance(prompt_data_part, Part):
            # If the Part is a text Part, assemble it.
            try:
                return self._assemble_single_str(
                    prompt_data_part.text, formatted_variables
                )
            except AttributeError:
                return [prompt_data_part]

    def _assemble_single_str(
        self,
        prompt_data_str: str,
        formatted_variables: Dict[str, List[Part]],
    ) -> List[Part]:
        """Assemble a single string with 0 or more variables within the string."""
        # Step 1) Find and isolate variables as their own string.
        prompt_data_str_split = re.split(VARIABLE_NAME_REGEX, prompt_data_str)

        assembled_data = []
        # Step 2) Assemble variables with their values, creating a list of Parts.
        for s in prompt_data_str_split:
            if not s:
                continue
            variable_name = s[1:-1]
            if (
                re.match(VARIABLE_NAME_REGEX, s)
                and variable_name in formatted_variables
            ):
                assembled_data.extend(formatted_variables[variable_name])
            else:
                assembled_data.append(Part.from_text(s))

        return assembled_data

    def to_contents(self) -> List[Content]:
        """Returns the prompt data, assembled if prompt.assemble() was called.
        Can be ingested into model.generate_content to make API calls.

        Returns:
            A List[Content] prompt.
        Usage:
            ```
            prompt = Prompt(
                prompt_data="Hello, {name}! Today is {day}. How are you?",
                variables={"name": "Alice", "day": "Monday"}
            )
            prompt.assemble(day="Monday")
            model.generate_content(
                contents=prompt.to_contents()
            )
            ```
        """
        if self._assembled_prompt:
            return self._assembled_prompt
        return [Content._from_gapic(_to_content(value=self.prompt_data))]

    def get_unassembled_prompt(self) -> PartsType:
        """Returns the prompt data, without any variables replaced."""
        return self.prompt_data

    def __str__(self) -> str:
        """Returns the prompt data, assembled if prompt.assemble() was called."""
        return str(self._assembled_prompt) or str(self.prompt_data)

    def __repr__(self) -> str:
        """Returns a string representation of the unassembled prompt."""
        return f"Prompt(prompt_data='{self.prompt_data}', variables={self.variables})"
