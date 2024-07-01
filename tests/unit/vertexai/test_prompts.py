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
"""Unit tests for generative model prompts."""
# pylint: disable=protected-access,bad-continuation

from vertexai.generative_models._prompts import Prompt
from vertexai.generative_models import Content, Part

import pytest

from typing import Any, List


def _is_list_type(obj: Any, T: Any) -> bool:
    return isinstance(obj, list) and all(isinstance(s, T) for s in obj)


def compare_prompt_contents(
    prompt_contents: List[Content],
    expected_prompt_contents: List[Content],
) -> None:
    assert len(prompt_contents) == len(expected_prompt_contents)
    for i in range(len(prompt_contents)):
        assert prompt_contents[i].role == expected_prompt_contents[i].role
        assert len(prompt_contents[i].parts) == len(expected_prompt_contents[i].parts)
        for j in range(len(prompt_contents[i].parts)):
            assert (
                prompt_contents[i].parts[j]._raw_part.text
                == expected_prompt_contents[i].parts[j]._raw_part.text
            )


@pytest.mark.usefixtures("google_auth_mock")
class TestPrompt:
    """Unit tests for generative model prompts."""

    def test_string_prompt_constructor(self):
        # Create string prompt with string only variable values
        prompt = Prompt(
            prompt_data="Rate the movie {movie1}",
            variables={
                "movie1": "The Avengers",
            },
        )
        # String prompt data should remain as string before compilation
        assert prompt.prompt_data == "Rate the movie {movie1}"
        # Variables values should be converted to List[Part]
        assert _is_list_type(prompt.variables["movie1"], Part)

        # Create string prompt with List[Part] variable values
        prompt = Prompt(
            prompt_data="Rate the movie {movie1}",
            variables={
                "movie1": [Part.from_text("The Avengers")],
            },
        )
        # Variables values should be converted to List[Part]
        assert _is_list_type(prompt.variables["movie1"], Part)

        # String prompt variables must either be string or List[Part]
        with pytest.raises(ValueError):
            Prompt(
                prompt_data="Rate the movie {movie1}",
                variables={
                    "movie1": Part.from_text("The Avengers"),
                },
            )

    def test_string_prompt_to_contents(self):
        prompt = Prompt(
            prompt_data="Which movie is better, {movie1} or {movie2}?",
            variables={
                "movie1": "The Avengers",
                "movie2": "Frozen",
            },
        )
        unassembled_prompt_content = prompt.to_contents()
        expected_content = [
            Content(
                parts=[
                    Part.from_text("Which movie is better, {movie1} or {movie2}?"),
                ],
                role="user",
            )
        ]
        compare_prompt_contents(unassembled_prompt_content, expected_content)

        # Check assembled prompt content
        prompt.assemble()
        assembled_prompt_content = prompt.to_contents()
        expected_content = [
            Content(
                parts=[
                    Part.from_text("Which movie is better, The Avengers or Frozen?"),
                ],
                role="user",
            )
        ]
        compare_prompt_contents(assembled_prompt_content, expected_content)

    def test_string_prompt_assemble(self):
        prompt = Prompt(
            prompt_data="Which movie is better, {movie1} or {movie2}?",
            variables={
                "movie1": "The Avengers",
            },
        )

        # Check partially assembled prompt content
        prompt.assemble()
        assembled1_prompt_content = prompt.to_contents()
        expected1_content = [
            Content(
                parts=[
                    Part.from_text("Which movie is better, The Avengers or {movie2}?"),
                ],
                role="user",
            )
        ]
        compare_prompt_contents(assembled1_prompt_content, expected1_content)

        # Check assembled prompt content
        prompt.assemble(movie2="Frozen")
        assembled2_prompt_content = prompt.to_contents()
        expected2_content = [
            Content(
                parts=[
                    Part.from_text("Which movie is better, The Avengers or Frozen?"),
                ],
                role="user",
            )
        ]
        compare_prompt_contents(assembled2_prompt_content, expected2_content)

        # Check assembled prompt content with override
        prompt.assemble(movie1="Inception")
        assembled3_prompt_content = prompt.to_contents()
        expected3_content = [
            Content(
                parts=[
                    Part.from_text("Which movie is better, Inception or Frozen?"),
                ],
                role="user",
            )
        ]
        compare_prompt_contents(assembled3_prompt_content, expected3_content)
