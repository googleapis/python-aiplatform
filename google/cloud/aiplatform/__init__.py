# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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


from google.cloud.aiplatform import version as aiplatform_version

__version__ = aiplatform_version.__version__


from google.cloud.aiplatform import initializer

from google.cloud.aiplatform.datasets import (
    ImageDataset,
    TabularDataset,
    TextDataset,
    TimeSeriesDataset,
    VideoDataset,
)
from google.cloud.aiplatform import explain
from google.cloud.aiplatform import gapic
from google.cloud.aiplatform import hyperparameter_tuning
from google.cloud.aiplatform.featurestore import (
    EntityType,
    Feature,
    Featurestore,
)
from google.cloud.aiplatform.matching_engine import (
    MatchingEngineIndex,
    MatchingEngineIndexEndpoint,
)
from google.cloud.aiplatform import metadata
from google.cloud.aiplatform.models import Endpoint
from google.cloud.aiplatform.models import PrivateEndpoint
from google.cloud.aiplatform.models import Model
from google.cloud.aiplatform.models import ModelRegistry
from google.cloud.aiplatform.model_evaluation import ModelEvaluation
from google.cloud.aiplatform.jobs import (
    BatchPredictionJob,
    CustomJob,
    HyperparameterTuningJob,
    ModelDeploymentMonitoringJob,
)
from google.cloud.aiplatform.pipeline_jobs import PipelineJob
from google.cloud.aiplatform.tensorboard import (
    Tensorboard,
    TensorboardExperiment,
    TensorboardRun,
    TensorboardTimeSeries,
)
from google.cloud.aiplatform.training_jobs import (
    CustomTrainingJob,
    CustomContainerTrainingJob,
    CustomPythonPackageTrainingJob,
    AutoMLTabularTrainingJob,
    AutoMLForecastingTrainingJob,
    SequenceToSequencePlusForecastingTrainingJob,
    AutoMLImageTrainingJob,
    AutoMLTextTrainingJob,
    AutoMLVideoTrainingJob,
)

from google.cloud.aiplatform import helpers

"""
Usage:
from google.cloud import aiplatform

aiplatform.init(project='my_project')
"""
init = initializer.global_config.init

get_pipeline_df = metadata.metadata._LegacyExperimentService.get_pipeline_df

log_params = metadata.metadata._experiment_tracker.log_params
log_metrics = metadata.metadata._experiment_tracker.log_metrics
log_classification_metrics = (
    metadata.metadata._experiment_tracker.log_classification_metrics
)
get_experiment_df = metadata.metadata._experiment_tracker.get_experiment_df
start_run = metadata.metadata._experiment_tracker.start_run
start_execution = metadata.metadata._experiment_tracker.start_execution
log = metadata.metadata._experiment_tracker.log
log_time_series_metrics = metadata.metadata._experiment_tracker.log_time_series_metrics
end_run = metadata.metadata._experiment_tracker.end_run

Experiment = metadata.experiment_resources.Experiment
ExperimentRun = metadata.experiment_run_resource.ExperimentRun
Artifact = metadata.artifact.Artifact
Execution = metadata.execution.Execution
Context = metadata.context.Context


__all__ = (
    "end_run",
    "explain",
    "gapic",
    "init",
    "helpers",
    "hyperparameter_tuning",
    "log",
    "log_params",
    "log_metrics",
    "log_classification_metrics",
    "log_time_series_metrics",
    "get_experiment_df",
    "get_pipeline_df",
    "start_run",
    "start_execution",
    "Artifact",
    "AutoMLImageTrainingJob",
    "AutoMLTabularTrainingJob",
    "AutoMLForecastingTrainingJob",
    "AutoMLTextTrainingJob",
    "AutoMLVideoTrainingJob",
    "BatchPredictionJob",
    "CustomJob",
    "CustomTrainingJob",
    "CustomContainerTrainingJob",
    "CustomPythonPackageTrainingJob",
    "EmailAlertConfig",
    "Endpoint",
    "DriftDetectionConfig",
    "ExplanationConfig",
    "ObjectiveConfig",
    "SkewDetectionConfig",
    "EntityType",
    "Execution",
    "Experiment",
    "ExperimentRun",
    "Feature",
    "Featurestore",
    "MatchingEngineIndex",
    "MatchingEngineIndexEndpoint",
    "ImageDataset",
    "HyperparameterTuningJob",
    "Model",
    "ModelRegistry",
    "ModelEvaluation",
    "ModelDeploymentMonitoringJob",
    "PipelineJob",
    "PrivateEndpoint",
    "RandomSampleConfig",
    "SequenceToSequencePlusForecastingTrainingJob",
    "ScheduleConfig",
    "TabularDataset",
    "Tensorboard",
    "TensorboardExperiment",
    "TensorboardRun",
    "TensorboardTimeSeries",
    "TextDataset",
    "TimeSeriesDataset",
    "VideoDataset",
)
