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
from vertexai._genai import types


def test_optimize_prompt(client):
    """Tests the optimize request parameters method."""

    test_prompt = "Generate system instructions for analyzing medical articles"
    response = client.prompt_optimizer.optimize_prompt(prompt=test_prompt)
    assert isinstance(response, types.OptimizeResponse)
    assert response.raw_text_response


# def test_optimize_prompt_w_optimization_target(client):
#     """Tests the optimize request parameters method with optimization target."""
#     from google.genai import types as genai_types
#     test_prompt = "Generate system instructions for analyzing medical articles"
#     response = client.prompt_optimizer.optimize_prompt(
#         prompt=test_prompt,
#         config=types.OptimizeConfig(
#             optimization_target=types.OptimizeTarget.OPTIMIZATION_TARGET_GEMINI_NANO,
#         ),
#     )
#     assert isinstance(response, types.OptimizeResponse)
#     assert response.raw_text_response


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="prompt_optimizer.optimize_prompt",
)
