# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

from google.cloud.aiplatform import gapic
from google.cloud.aiplatform import explain

from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.datasets import (
    ImageDataset,
    TabularDataset,
    TextDataset,
    TimeSeriesDataset,
    VideoDataset,
)
from google.cloud.aiplatform.models import Endpoint
from google.cloud.aiplatform.models import Model
from google.cloud.aiplatform.jobs import BatchPredictionJob
from google.cloud.aiplatform.training_jobs import (
    CustomTrainingJob,
    CustomContainerTrainingJob,
    CustomPythonPackageTrainingJob,
    AutoMLTabularTrainingJob,
    AutoMLForecastingTrainingJob,
    AutoMLImageTrainingJob,
    AutoMLTextTrainingJob,
    AutoMLVideoTrainingJob,
)
from google.cloud.aiplatform.metadata import metadata

"""
Usage:
from google.cloud import aiplatform

aiplatform.init(project='my_project')
"""
init = initializer.global_config.init

log_params = metadata.metadata_service.log_params
log_metrics = metadata.metadata_service.log_metrics
get_experiment_df = metadata.metadata_service.get_experiment_df
get_pipeline_df = metadata.metadata_service.get_pipeline_df
start_run = metadata.metadata_service.start_run


__all__ = (
    "explain",
    "gapic",
    "init",
    "log_params",
    "log_metrics",
    "get_experiment_df",
    "get_pipeline_df",
    "start_run",
    "AutoMLImageTrainingJob",
    "AutoMLTabularTrainingJob",
    "AutoMLForecastingTrainingJob",
    "AutoMLTextTrainingJob",
    "AutoMLVideoTrainingJob",
    "BatchPredictionJob",
    "CustomTrainingJob",
    "CustomContainerTrainingJob",
    "CustomPythonPackageTrainingJob",
    "Endpoint",
    "ImageDataset",
    "Model",
    "TabularDataset",
    "TextDataset",
    "TimeSeriesDataset",
    "VideoDataset",
)
