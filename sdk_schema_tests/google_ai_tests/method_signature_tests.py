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

from inspect import signature
import unittest

from google.generativeai import GenerativeModel
from sdk_schema_tests import common_contract
from sdk_schema_tests import google_ai_only_contract as specific_contract

_SDK_NAME = "GoogleAI"


class TestGenerativeModelMethodSignatures(unittest.TestCase):
    def test_generate_content_signature(self):
        generate_content_signature = signature(GenerativeModel.generate_content)
        actual_method_arg_keys = generate_content_signature.parameters.keys()
        actual_return_annotation = generate_content_signature.return_annotation

        for expected_key in common_contract.expected_generate_content_common_arg_keys:
            self.assertIn(
                member=expected_key,
                container=actual_method_arg_keys,
                msg=(
                    f"[{_SDK_NAME}]: expected common key {expected_key} not found in"
                    f" actual keys: {actual_method_arg_keys}"
                ),
            )

        self.assertEqual(
            actual_return_annotation,
            specific_contract.expected_generate_content_return_annotation,
            msg=(
                f"[{_SDK_NAME}]: expected return annotation"
                f" {specific_contract.expected_generate_content_return_annotation}"
                f" not equal to actual return annotation {actual_return_annotation}"
            ),
        )
