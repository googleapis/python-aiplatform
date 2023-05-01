# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
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
from google.cloud.aiplatform_v1beta1.types import (
    explanation as explanation_v1beta1,
)
from google.cloud.aiplatform_v1beta1.types import (
    explanation_metadata as explanation_metadata_v1beta1,
)


# Preview Explanation clases for Vertex AI.
ExplanationMetadata = explanation_metadata_v1beta1.ExplanationMetadata

# ExplanationMetadata subclasses
InputMetadata = ExplanationMetadata.InputMetadata
OutputMetadata = ExplanationMetadata.OutputMetadata

# InputMetadata subclasses
Encoding = InputMetadata.Encoding
FeatureValueDomain = InputMetadata.FeatureValueDomain
Visualization = InputMetadata.Visualization


ExplanationParameters = explanation_v1beta1.ExplanationParameters
FeatureNoiseSigma = explanation_v1beta1.FeatureNoiseSigma

ExplanationSpec = explanation_v1beta1.ExplanationSpec

# Classes used by ExplanationParameters
Examples = explanation_v1beta1.Examples


__all__ = (
    "ExplanationMetadata",
    "InputMetadata",
    "OutputMetadata",
    "Encoding",
    "FeatureValueDomain",
    "Visualization",
    "ExplanationParameters",
    "FeatureNoiseSigma",
    "ExplanationSpec",
    "Examples",
)
