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

import json

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types


def test_private_execute_code(client):

    code = """
with open("test.txt", "r") as input:
    with open("output.txt", "w") as output_txt:
        for line in input:
            output_txt.write(line)
"""
    # Transform the input data into chunks as expected by _execute_code
    input_chunks = [
        types.Chunk(
            mime_type="application/json",
            data=json.dumps({"code": code}).encode("utf-8"),
        ),
        types.Chunk(
            mime_type="text/plain",
            data=b"Hello, world!",
            metadata={"attributes": {"file_name": b"test.txt"}},
        ),
    ]

    execute_code_response = client.agent_engines.sandboxes._execute_code(
        name=(
            "reasoningEngines/2886612747586371584/sandboxEnvironments/6068475153556176896"
        ),
        inputs=input_chunks,
    )
    assert isinstance(
        execute_code_response,
        types.ExecuteSandboxEnvironmentResponse,
    )
    assert isinstance(execute_code_response.outputs, list)
    assert isinstance(execute_code_response.outputs[0], types.Chunk)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.sandboxes._execute_code",
)
