"""Tests for method_signature."""

import inspect
import unittest

from vertexai.generative_models import GenerativeModel

from sdk_schema_tests import common_contract
from sdk_schema_tests import vertex_ai_only_contract as specific_contract

_SDK_NAME = "VertexAI"


class TestGenerativeModelMethodSignatures(unittest.TestCase):
    def test_generate_content_signature(self):
        generate_content_signature = inspect.signature(GenerativeModel.generate_content)
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
