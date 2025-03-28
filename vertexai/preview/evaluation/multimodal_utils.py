"""Utility functions for multimodal evaluation."""

import logging
from typing import Dict

from google.cloud.aiplatform_v1beta1.types import content
from google.cloud.aiplatform_v1beta1.types import (
    evaluation_service as gapic_eval_service_types,
)
from google.protobuf import json_format


ContentMap = gapic_eval_service_types.ContentMap
Content = content.Content
Part = content.Part
_CONTENTS_DETECTOR = "contents {"
_PARTS_DETECTOR = "parts {"


def _string_to_content_list(input_str: str) -> ContentMap.Contents:
    """Converts a string to a list if possible, otherwise returns None."""
    try:
        return json_format.Parse(
            input_str,
            ContentMap.Contents.pb(ContentMap.Contents()),
        )
    except json_format.ParseError as e:
        if _CONTENTS_DETECTOR in input_str and _PARTS_DETECTOR in input_str:
            logging.warning(
                "Failed to parse %s to ContentMap.Contents: %s", input_str, e
            )
        return None


def _is_multimodal_response(response: str) -> bool:
    """Checks if the model response contains multimodal input."""
    content_list = _string_to_content_list(response)
    if content_list is None:
        if _CONTENTS_DETECTOR in response and _PARTS_DETECTOR in response:
            logging.warning(
                "Response contains multimodal input: %s. Please check whether"
                " the response format conforms to ContentMap type.",
                response,
            )
        return False
    else:
        return True


def is_multimodal_instance(
    model_based_metric_instance_input: Dict[str, str],
) -> bool:
    """Checks if the evaluation instance contains multimodal input."""
    for placeholder in model_based_metric_instance_input:
        if _is_multimodal_response(model_based_metric_instance_input[placeholder]):
            return True
    return False


def convert_multimodal_response_to_content_map(
    model_based_metric_instance_input: Dict[str, str],
) -> ContentMap:
    """Converts a multimodal model response to a ContentMap."""
    content_map = ContentMap()
    for placeholder in model_based_metric_instance_input.keys():
        content_list = _string_to_content_list(
            model_based_metric_instance_input[placeholder]
        )
        if content_list is None:
            content_map.values[placeholder] = ContentMap.Contents(
                contents=[
                    Content(
                        parts=[
                            Part(text=model_based_metric_instance_input[placeholder])
                        ]
                    )
                ]
            )
        else:
            content_map.values[placeholder] = content_list

    return content_map
