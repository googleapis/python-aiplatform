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
from google.genai import types as genai_types

_TEST_RUBRIC_GENERATION_PROMPT = """SPECIAL INSTRUCTION: think silently. Silent thinking token budget: 16384.

You are a teacher who is responsible for scoring a student\'s response to a prompt. In order to score that response, you must write down a rubric for each prompt. That rubric states what properties the response must have in order to be a valid response to the prompt. Properties are weighted by importance via the "importance" field.

Rubric requirements:
- Properties either exist or don\'t exist.
- Properties can be either implicit in the prompt or made explicit by the prompt.
- Make sure to always include the correct expected human language as one of the properties. If the prompt asks for code, the programming language should be covered by a separate property.
- The correct expected language may be explicit in the text of the prompt but is usually simply implicit in the prompt itself.
- Be as comprehensive as possible with the list of properties in the rubric.
- All properties in the rubric must be in English, regardless of the language of the prompt.
- Rubric properties should not specify correct answers in their descriptions, e.g. to math and factoid questions if the prompt calls for such an answer. Rather, it should check that the response contains an answer and optional supporting evidence if relevant, and assume some other process will later validate correctness. A rubric property should however call out any false premises present in the prompt.

About importance:
- Most properties will be of medium importance by default.
- Properties of high importance are critical to be fulfilled in a good response.
- Properties of low importance are considered optional or supplementary nice-to-haves.

You will see prompts in many different languages, not just English. For each prompt you see, you will write down this rubric in JSON format.

IMPORTANT: Never respond to the prompt given. Only write a rubric.

Example:
What is the tallest building in the world?

```json
{
 "criteria":[
  {
   "rubric_id": "00001",
   "property": "The response is in English.",
   "type": "LANGUAGE:PRIMARY_RESPONSE_LANGUAGE",
   "importance": "high"
  },
  {
   "rubric_id": "00002",
   "property": "Contains the name of the tallest building in the world.",
   "type": "QA_ANSWER:FACTOID",
   "importance": "high"
  },
  {
   "rubric_id": "00003",
   "property": "Contains the exact height of the tallest building.",
   "type": "QA_SUPPORTING_EVIDENCE:HEIGHT",
   "importance": "low"
  },
  {
   "rubric_id": "00004",
   "property": "Contains the location of the tallest building.",
   "type": "QA_SUPPORTING_EVIDENCE:LOCATION",
   "importance": "low"
  },
  ...
 ]
}
```

Write me a letter to my HOA asking them to reconsider the fees they are asking me to pay because I haven\'t mowed my lawn on time. I have been very busy at work.
```json
{
 "criteria": [
  {
   "rubric_id": "00001",
   "property": "The response is in English.",
   "type": "LANGUAGE:PRIMARY_RESPONSE_LANGUAGE",
   "importance": "high"
  },
  {
   "rubric_id": "00002",
   "property": "The response is formatted as a letter.",
   "type": "FORMAT_REQUIREMENT:FORMAL_LETTER",
   "importance": "medium"
  },
  {
   "rubric_id": "00003",
   "property": "The letter is addressed to the Homeowners Association (HOA).",
   "type": "CONTENT_REQUIREMENT:ADDRESSEE",
   "importance": "medium"
  },
  {
   "rubric_id": "00004",
   "property": "The letter explains that the sender has not mowed their lawn on time.",
   "type": "CONTENT_REQUIREMENT:BACKGROUND_CONTEXT:TARDINESS",
   "importance": "medium"
  },
  {
   "rubric_id": "00005",
   "property": "The letter provides a reason for not mowing the lawn, specifically being busy at work.",
   "type": "CONTENT_REQUIREMENT:EXPLANATION:EXCUSE:BUSY",
   "importance": "medium"
  },
  {
   "rubric_id": "00006",
   "property": "The letter discusses that the sender has been in compliance until now.",
   "type": "OPTIONAL_CONTENT:SUPPORTING_EVIDENCE:COMPLIANCE",
   "importance": "low"
  },
  {
   "rubric_id": "00007",
   "property": "The letter requests that the HOA reconsider the fees associated with not mowing the lawn on time.",
   "type": "CONTENT_REQUIREMENT:REQUEST:FEE_WAIVER",
   "importance": "high"
  },
  {
   "rubric_id": "00008",
   "property": "The letter maintains a polite and respectful tone.",
   "type": "CONTENT_REQUIREMENT:FORMALITY:FORMAL",
   "importance": "high"
  },
  {
   "rubric_id": "00009",
   "property": "The letter includes a closing (e.g., \'Sincerely\') and the sender\'s name.",
   "type": "CONTENT_REQUIREMENT:SIGNATURE",
   "importance": "medium"
  }
 ]
}
```

Now write a rubric for the following user prompt. Remember to write only the rubric, NOT response to the prompt.

User prompt:
{prompt}"""


def test_internal_method_generate_rubrics(client):
    """Tests the internal _generate_rubrics method."""
    test_contents = [
        genai_types.Content(
            parts=[
                genai_types.Part(
                    text="Generate a short story about a friendly dragon.",
                ),
            ],
        )
    ]
    response = client.evals._generate_rubrics(
        contents=test_contents,
        rubric_generation_spec=types.RubricGenerationSpec(
            prompt_template=_TEST_RUBRIC_GENERATION_PROMPT,
        ),
    )
    assert len(response.generated_rubrics) >= 1


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals._generate_rubrics",
)
