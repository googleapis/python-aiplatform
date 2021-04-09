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
    Dataset,
    TabularDataset,
    ImageDataset,
    TextDataset,
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
set_experiment = metadata.metadata_service.set_experiment
get_experiment = metadata.metadata_service.get_experiment
set_run = metadata.metadata_service.set_run
get_pipeline = metadata.metadata_service.get_pipeline


__all__ = (
    "explain",
    "gapic",
    "init",
    "log_params",
    "log_metrics",
    "get_experiment",
    "set_experiment",
    "set_run",
    "get_pipeline",
    "AutoMLImageTrainingJob",
    "AutoMLTabularTrainingJob",
    "AutoMLTextTrainingJob",
    "AutoMLVideoTrainingJob",
    "BatchPredictionJob",
    "CustomTrainingJob",
    "CustomContainerTrainingJob",
    "CustomPythonPackageTrainingJob",
    "Dataset",
    "Endpoint",
    "ImageDataset",
    "Model",
    "TabularDataset",
    "TextDataset",
    "VideoDataset",
)
