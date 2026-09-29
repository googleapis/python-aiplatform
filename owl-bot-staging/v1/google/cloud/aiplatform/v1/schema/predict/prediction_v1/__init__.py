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
from google.cloud.aiplatform.v1.schema.predict.prediction_v1 import gapic_version as package_version

import google.api_core as api_core

__version__ = package_version.__version__

# PEP 0810: Explicit Lazy Imports
# Python 3.15+ natively intercepts and defers these imports.
# Developers can disable this behavior and force eager imports.
# For more information, see:
# https://docs.python.org/3.15/library/sys.html#sys.set_lazy_imports_filter
# Older Python versions safely ignore this variable.
__lazy_modules__ = {
"google.cloud.aiplatform.v1.schema.predict.prediction_v1.types.classification",
"google.cloud.aiplatform.v1.schema.predict.prediction_v1.types.image_object_detection",
"google.cloud.aiplatform.v1.schema.predict.prediction_v1.types.image_segmentation",
"google.cloud.aiplatform.v1.schema.predict.prediction_v1.types.tabular_classification",
"google.cloud.aiplatform.v1.schema.predict.prediction_v1.types.tabular_regression",
"google.cloud.aiplatform.v1.schema.predict.prediction_v1.types.text_extraction",
"google.cloud.aiplatform.v1.schema.predict.prediction_v1.types.text_sentiment",
"google.cloud.aiplatform.v1.schema.predict.prediction_v1.types.video_action_recognition",
"google.cloud.aiplatform.v1.schema.predict.prediction_v1.types.video_classification",
"google.cloud.aiplatform.v1.schema.predict.prediction_v1.types.video_object_tracking",
}



from .types.classification import ClassificationPredictionResult
from .types.image_object_detection import ImageObjectDetectionPredictionResult
from .types.image_segmentation import ImageSegmentationPredictionResult
from .types.tabular_classification import TabularClassificationPredictionResult
from .types.tabular_regression import TabularRegressionPredictionResult
from .types.text_extraction import TextExtractionPredictionResult
from .types.text_sentiment import TextSentimentPredictionResult
from .types.video_action_recognition import VideoActionRecognitionPredictionResult
from .types.video_classification import VideoClassificationPredictionResult
from .types.video_object_tracking import VideoObjectTrackingPredictionResult

__all__ = (
'ClassificationPredictionResult',
'ImageObjectDetectionPredictionResult',
'ImageSegmentationPredictionResult',
'TabularClassificationPredictionResult',
'TabularRegressionPredictionResult',
'TextExtractionPredictionResult',
'TextSentimentPredictionResult',
'VideoActionRecognitionPredictionResult',
'VideoClassificationPredictionResult',
'VideoObjectTrackingPredictionResult',
)

api_core.check_python_version("google.cloud.aiplatform.v1.schema.predict.prediction_v1")
api_core.check_dependency_versions("google.cloud.aiplatform.v1.schema.predict.prediction_v1")
