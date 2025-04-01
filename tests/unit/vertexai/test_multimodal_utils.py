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
"""Unit tests for multimodal utils."""

from google.cloud.aiplatform_v1beta1.types import content
from google.cloud.aiplatform_v1beta1.types import (
    evaluation_service as gapic_eval_service_types,
)
from vertexai.preview.evaluation import (
    multimodal_utils,
)


ContentMap = gapic_eval_service_types.ContentMap
Content = content.Content
Part = content.Part

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

_MODEL_BASED_METRIC_INSTANCE_INPUT = {
    "prompt": "test prompt",
    "response": (
        '{"contents": [{"parts": [{"file_data": {"mime_type": "image/png",'
        ' "file_uri": "gs://test-bucket/image1.png"}}]}]}'
    ),
    "baseline_response": (
        '{"contents": [{"parts": [{"file_data": {"mime_type": "image/jepg",'
        ' "file_uri": "gs://test-bucket/image2.png"}}]}]}'
    ),
}
_INVALID_MODEL_BASED_METRIC_INSTANCE_INPUT = {
    "prompt": "test prompt",
    "invalid_response_format": (
        '{"contents": [{{{{"parts": [{"file_data": {"mime_type": "image/png",'
        ' "file_uri": "gs://test-bucket/image1.png"}}]}]}'
    ),
    "baseline_response": "test image",
}


class TestMultimodalUtils:
    """Unit tests for multimodal utils."""

    def test_is_multimodal_instance(self):
        assert multimodal_utils.is_multimodal_instance(
            _MODEL_BASED_METRIC_INSTANCE_INPUT
        )

    def test_not_multimodal_instance(self):
        assert not multimodal_utils.is_multimodal_instance(
            _INVALID_MODEL_BASED_METRIC_INSTANCE_INPUT
        )

    def test_convert_multimodal_response_to_content_map(self):
        """Test convert_multimodal_response_to_content_map."""
        content_map = multimodal_utils.convert_multimodal_response_to_content_map(
            _MODEL_BASED_METRIC_INSTANCE_INPUT
        )
        assert content_map.values["prompt"] == ContentMap.Contents(
            contents=[Content(parts=[Part(text="test prompt")])]
        )
        assert content_map.values["response"] == ContentMap.Contents(
            contents=[
                Content(
                    parts=[
                        Part(
                            file_data={
                                "mime_type": "image/png",
                                "file_uri": "gs://test-bucket/image1.png",
                            }
                        )
                    ]
                )
            ]
        )
        assert content_map.values["baseline_response"] == ContentMap.Contents(
            contents=[
                Content(
                    parts=[
                        Part(
                            file_data={
                                "mime_type": "image/jepg",
                                "file_uri": "gs://test-bucket/image2.png",
                            }
                        )
                    ]
                )
            ]
        )

    def test_split_metric_prompt_template(self):
        metric_prompt_template = "This prompt uses {prompt} and {response}."
        placeholders = ["prompt", "response", "baseline_response"]
        split_metric_prompt_template = multimodal_utils._split_metric_prompt_template(
            metric_prompt_template, placeholders
        )
        assert split_metric_prompt_template == [
            "This prompt uses ",
            "{prompt}",
            " and ",
            "{response}",
            ".",
        ]

    def test_assemble_multi_modal_prompt_gemini_format(self):
        prompt_template = """This {prompt} uses the {response}."""
        prompt = multimodal_utils._assemble_multi_modal_prompt(
            prompt_template,
            _MODEL_BASED_METRIC_INSTANCE_INPUT,
            1,
            ["response", "prompt"],
        )
        assert prompt[0] == "This "
        assert prompt[1] == "test prompt"
        assert prompt[2] == " uses the "
        assert prompt[3].file_data.file_uri == "gs://test-bucket/image1.png"
        assert prompt[4] == "."
