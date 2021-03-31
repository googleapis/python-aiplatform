# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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

from google.cloud.aiplatform_v1beta1.types.explanation_metadata import (
    ExplanationMetadata,
)
from google.cloud.aiplatform_v1beta1.types.explanation import ExplanationParameters

from google.cloud.aiplatform_v1beta1.types.explanation import FeatureNoiseSigma

# Classes used by ExplanationParameters
from google.cloud.aiplatform_v1beta1.types.explanation import (
    IntegratedGradientsAttribution,
)
from google.cloud.aiplatform_v1beta1.types.explanation import SampledShapleyAttribution
from google.cloud.aiplatform_v1beta1.types.explanation import SmoothGradConfig
from google.cloud.aiplatform_v1beta1.types.explanation import XraiAttribution

# ExplanationMetadata subclasses
InputMetadata = ExplanationMetadata.InputMetadata
OutputMetadata = ExplanationMetadata.OutputMetadata

# InputMetadata subclasses
Encoding = ExplanationMetadata.InputMetadata.Encoding
FeatureValueDomain = ExplanationMetadata.InputMetadata.FeatureValueDomain
Visualization = ExplanationMetadata.InputMetadata.Visualization

__all__ = (
    "Encoding",
    "ExplanationMetadata",
    "ExplanationParameters",
    "FeatureNoiseSigma",
    "FeatureValueDomain",
    "InputMetadata",
    "IntegratedGradientsAttribution",
    "OutputMetadata",
    "SampledShapleyAttribution",
    "SmoothGradConfig",
    "Visualization",
    "XraiAttribution",
)
