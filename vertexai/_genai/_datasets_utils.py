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
"""Utility functions for multimodal dataset."""

from typing import Any, TypeVar, Type
from vertexai._genai.types import common
from pydantic import BaseModel

METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/multimodal_1.0.0.yaml"
)

T = TypeVar("T", bound=BaseModel)


def create_from_response(model_type: Type[T], response: dict[str, Any]) -> T:
    """Creates a model from a response."""
    model_field_names = model_type.model_fields.keys()
    filtered_response = {}
    for key, value in response.items():
        snake_key = common.camel_to_snake(key)
        if snake_key in model_field_names:
            filtered_response[snake_key] = value
    return model_type(**filtered_response)
