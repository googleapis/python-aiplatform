"""Tests for method_signature."""

from inspect import signature
import unittest

from vertexai.generative_models import GenerativeModel as VertexAIGenerativeModel
from google.generativeai import GenerativeModel as GoogleAIGenerativeModel
from sdk_schema_tests import common_contract


_VERTEX_AI_SDK_NAME = "Vertex AI SDK"
_GOOGLE_AI_SDK_NAME = "Google AI SDK"


class TestGenerativeModelMethodSignatures(unittest.TestCase):
    """Tests for method signatures of GenerativeModel."""

    def _test_method_argument_key_in_both_sdks(
        self,
        method_under_test,
        expected_method_arg_keys,
        sdk_name
    ):
        method_signature = signature(method_under_test)
        actual_method_arg_keys = method_signature.parameters.keys()
        for expected_arg_key in expected_method_arg_keys:
            self.assertIn(
                member=expected_arg_key,
                container=actual_method_arg_keys,
                msg=(
                    f"[{sdk_name}][method {method_under_test.__name__}]: expected"
                    f" common arugment {expected_arg_key} not found in actual arugment"
                    f" list: {actual_method_arg_keys}"
                ),
            )

    def test_generate_content_method_signature(self):
        expected_common_arg_keys = (
            common_contract.expected_generate_content_common_arg_keys
        )
        test_arguments = [
            {
                "method_under_test": VertexAIGenerativeModel.generate_content,
                "expected_method_arg_keys": expected_common_arg_keys,
                "sdk_name": _VERTEX_AI_SDK_NAME,
            },
            {
                "method_under_test": GoogleAIGenerativeModel.generate_content,
                "expected_method_arg_keys": expected_common_arg_keys,
                "sdk_name": _GOOGLE_AI_SDK_NAME,
            },
        ]
        for test_argument in test_arguments:
            self._test_method_argument_key_in_both_sdks(**test_argument)
