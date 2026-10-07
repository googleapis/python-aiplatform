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
from google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1 import (
    gapic_version as package_version,
)

import google.api_core as api_core

__version__ = package_version.__version__

# PEP 0810: Explicit Lazy Imports
# Python 3.15+ natively intercepts and defers these imports.
# Developers can disable this behavior and force eager imports.
# For more information, see:
# https://docs.python.org/3.15/library/sys.html#sys.set_lazy_imports_filter
# Older Python versions safely ignore this variable.
__lazy_modules__ = {
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.automl_image_classification",
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.automl_image_object_detection",
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.automl_image_segmentation",
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.automl_tables",
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.automl_text_classification",
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.automl_text_extraction",
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.automl_text_sentiment",
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.automl_time_series_forecasting",
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.automl_video_action_recognition",
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.automl_video_classification",
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.automl_video_object_tracking",
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.export_evaluated_data_items_config",
}


from .types.automl_image_classification import AutoMlImageClassification
from .types.automl_image_classification import AutoMlImageClassificationInputs
from .types.automl_image_classification import AutoMlImageClassificationMetadata
from .types.automl_image_object_detection import AutoMlImageObjectDetection
from .types.automl_image_object_detection import AutoMlImageObjectDetectionInputs
from .types.automl_image_object_detection import AutoMlImageObjectDetectionMetadata
from .types.automl_image_segmentation import AutoMlImageSegmentation
from .types.automl_image_segmentation import AutoMlImageSegmentationInputs
from .types.automl_image_segmentation import AutoMlImageSegmentationMetadata
from .types.automl_tables import AutoMlTables
from .types.automl_tables import AutoMlTablesInputs
from .types.automl_tables import AutoMlTablesMetadata
from .types.automl_text_classification import AutoMlTextClassification
from .types.automl_text_classification import AutoMlTextClassificationInputs
from .types.automl_text_extraction import AutoMlTextExtraction
from .types.automl_text_extraction import AutoMlTextExtractionInputs
from .types.automl_text_sentiment import AutoMlTextSentiment
from .types.automl_text_sentiment import AutoMlTextSentimentInputs
from .types.automl_time_series_forecasting import AutoMlForecasting
from .types.automl_time_series_forecasting import AutoMlForecastingInputs
from .types.automl_time_series_forecasting import AutoMlForecastingMetadata
from .types.automl_video_action_recognition import AutoMlVideoActionRecognition
from .types.automl_video_action_recognition import AutoMlVideoActionRecognitionInputs
from .types.automl_video_classification import AutoMlVideoClassification
from .types.automl_video_classification import AutoMlVideoClassificationInputs
from .types.automl_video_object_tracking import AutoMlVideoObjectTracking
from .types.automl_video_object_tracking import AutoMlVideoObjectTrackingInputs
from .types.export_evaluated_data_items_config import ExportEvaluatedDataItemsConfig

__all__ = (
    "AutoMlForecasting",
    "AutoMlForecastingInputs",
    "AutoMlForecastingMetadata",
    "AutoMlImageClassification",
    "AutoMlImageClassificationInputs",
    "AutoMlImageClassificationMetadata",
    "AutoMlImageObjectDetection",
    "AutoMlImageObjectDetectionInputs",
    "AutoMlImageObjectDetectionMetadata",
    "AutoMlImageSegmentation",
    "AutoMlImageSegmentationInputs",
    "AutoMlImageSegmentationMetadata",
    "AutoMlTables",
    "AutoMlTablesInputs",
    "AutoMlTablesMetadata",
    "AutoMlTextClassification",
    "AutoMlTextClassificationInputs",
    "AutoMlTextExtraction",
    "AutoMlTextExtractionInputs",
    "AutoMlTextSentiment",
    "AutoMlTextSentimentInputs",
    "AutoMlVideoActionRecognition",
    "AutoMlVideoActionRecognitionInputs",
    "AutoMlVideoClassification",
    "AutoMlVideoClassificationInputs",
    "AutoMlVideoObjectTracking",
    "AutoMlVideoObjectTrackingInputs",
    "ExportEvaluatedDataItemsConfig",
)

api_core.check_python_version(
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1"
)
api_core.check_dependency_versions(
    "google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1"
)
