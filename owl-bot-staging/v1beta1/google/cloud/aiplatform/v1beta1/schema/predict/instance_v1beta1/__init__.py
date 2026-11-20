# -*- coding: utf-8 -*-
# Copyright 2026 Google LLC
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
from google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1 import gapic_version as package_version

import google.api_core as api_core

__version__ = package_version.__version__

# PEP 0810: Explicit Lazy Imports
# Python 3.15+ natively intercepts and defers these imports.
# Developers can disable this behavior and force eager imports.
# For more information, see:
# https://docs.python.org/3.15/library/sys.html#sys.set_lazy_imports_filter
# Older Python versions safely ignore this variable.
__lazy_modules__ = {
"google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1.types.image_classification",
"google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1.types.image_object_detection",
"google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1.types.image_segmentation",
"google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1.types.text_classification",
"google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1.types.text_extraction",
"google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1.types.text_sentiment",
"google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1.types.video_action_recognition",
"google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1.types.video_classification",
"google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1.types.video_object_tracking",
}



from .types.image_classification import ImageClassificationPredictionInstance
from .types.image_object_detection import ImageObjectDetectionPredictionInstance
from .types.image_segmentation import ImageSegmentationPredictionInstance
from .types.text_classification import TextClassificationPredictionInstance
from .types.text_extraction import TextExtractionPredictionInstance
from .types.text_sentiment import TextSentimentPredictionInstance
from .types.video_action_recognition import VideoActionRecognitionPredictionInstance
from .types.video_classification import VideoClassificationPredictionInstance
from .types.video_object_tracking import VideoObjectTrackingPredictionInstance

__all__ = (
'ImageClassificationPredictionInstance',
'ImageObjectDetectionPredictionInstance',
'ImageSegmentationPredictionInstance',
'TextClassificationPredictionInstance',
'TextExtractionPredictionInstance',
'TextSentimentPredictionInstance',
'VideoActionRecognitionPredictionInstance',
'VideoClassificationPredictionInstance',
'VideoObjectTrackingPredictionInstance',
)

api_core.check_python_version("google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1")
api_core.check_dependency_versions("google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1")
