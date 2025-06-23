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

import os

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types
import pytest


IS_KOKORO = os.getenv("KOKORO_BUILD_NUMBER") is not None


@pytest.mark.skipif(IS_KOKORO, reason="This test is only run in google3 env.")
class TestEvaluateInstances:
    """Tests for evaluate instances."""

    def test_bleu_metric(self, client):
        test_bleu_input = types.BleuInput(
            instances=[
                types.BleuInstance(
                    reference="The quick brown fox jumps over the lazy dog.",
                    prediction="A fast brown fox leaps over a lazy dog.",
                )
            ],
            metric_spec=types.BleuSpec(),
        )
        response = client.evals._evaluate_instances(bleu_input=test_bleu_input)
        assert len(response.bleu_results.bleu_metric_values) == 1


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.evaluate",
)
