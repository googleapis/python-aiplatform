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

from google.cloud.aiplatform.compat import services
from google.cloud.aiplatform.compat import types

V1BETA1 = "v1beta1"
V1 = "v1"

DEFAULT_VERSION = V1

if DEFAULT_VERSION == V1BETA1:

    services.dataset_service_client = services.dataset_service_client_v1beta1
    services.endpoint_service_client = services.endpoint_service_client_v1beta1
    services.job_service_client = services.job_service_client_v1beta1
    services.model_service_client = services.model_service_client_v1beta1
    services.pipeline_service_client = services.pipeline_service_client_v1beta1
    services.prediction_service_client = services.prediction_service_client_v1beta1
    services.specialist_pool_service_client = (
        services.specialist_pool_service_client_v1beta1
    )
    services.metadata_service_client = services.metadata_service_client_v1beta1
    services.tensorboard_service_client = services.tensorboard_service_client_v1beta1

    types.accelerator_type = types.accelerator_type_v1beta1
    types.annotation = types.annotation_v1beta1
    types.annotation_spec = types.annotation_spec_v1beta1
    types.batch_prediction_job = types.batch_prediction_job_v1beta1
    types.completion_stats = types.completion_stats_v1beta1
    types.custom_job = types.custom_job_v1beta1
    types.data_item = types.data_item_v1beta1
    types.data_labeling_job = types.data_labeling_job_v1beta1
    types.dataset = types.dataset_v1beta1
    types.dataset_service = types.dataset_service_v1beta1
    types.deployed_model_ref = types.deployed_model_ref_v1beta1
    types.encryption_spec = types.encryption_spec_v1beta1
    types.endpoint = types.endpoint_v1beta1
    types.endpoint_service = types.endpoint_service_v1beta1
    types.env_var = types.env_var_v1beta1
    types.explanation = types.explanation_v1beta1
    types.explanation_metadata = types.explanation_metadata_v1beta1
    types.hyperparameter_tuning_job = types.hyperparameter_tuning_job_v1beta1
    types.io = types.io_v1beta1
    types.job_service = types.job_service_v1beta1
    types.job_state = types.job_state_v1beta1
    types.machine_resources = types.machine_resources_v1beta1
    types.manual_batch_tuning_parameters = types.manual_batch_tuning_parameters_v1beta1
    types.model = types.model_v1beta1
    types.model_evaluation = types.model_evaluation_v1beta1
    types.model_evaluation_slice = types.model_evaluation_slice_v1beta1
    types.model_service = types.model_service_v1beta1
    types.operation = types.operation_v1beta1
    types.pipeline_service = types.pipeline_service_v1beta1
    types.pipeline_state = types.pipeline_state_v1beta1
    types.prediction_service = types.prediction_service_v1beta1
    types.specialist_pool = types.specialist_pool_v1beta1
    types.specialist_pool_service = types.specialist_pool_service_v1beta1
    types.training_pipeline = types.training_pipeline_v1beta1
    types.metadata_service = types.metadata_service_v1beta1
    types.tensorboard_service = types.tensorboard_service_v1beta1
    types.tensorboard_data = types.tensorboard_data_v1beta1
    types.tensorboard_experiment = types.tensorboard_experiment_v1beta1
    types.tensorboard_run = types.tensorboard_run_v1beta1
    types.tensorboard_service = types.tensorboard_service_v1beta1
    types.tensorboard_time_series = types.tensorboard_time_series_v1beta1

if DEFAULT_VERSION == V1:

    services.dataset_service_client = services.dataset_service_client_v1
    services.endpoint_service_client = services.endpoint_service_client_v1
    services.job_service_client = services.job_service_client_v1
    services.model_service_client = services.model_service_client_v1
    services.pipeline_service_client = services.pipeline_service_client_v1
    services.prediction_service_client = services.prediction_service_client_v1
    services.specialist_pool_service_client = services.specialist_pool_service_client_v1

    types.accelerator_type = types.accelerator_type_v1
    types.annotation = types.annotation_v1
    types.annotation_spec = types.annotation_spec_v1
    types.batch_prediction_job = types.batch_prediction_job_v1
    types.completion_stats = types.completion_stats_v1
    types.custom_job = types.custom_job_v1
    types.data_item = types.data_item_v1
    types.data_labeling_job = types.data_labeling_job_v1
    types.dataset = types.dataset_v1
    types.dataset_service = types.dataset_service_v1
    types.deployed_model_ref = types.deployed_model_ref_v1
    types.encryption_spec = types.encryption_spec_v1
    types.endpoint = types.endpoint_v1
    types.endpoint_service = types.endpoint_service_v1
    types.env_var = types.env_var_v1
    types.hyperparameter_tuning_job = types.hyperparameter_tuning_job_v1
    types.io = types.io_v1
    types.job_service = types.job_service_v1
    types.job_state = types.job_state_v1
    types.machine_resources = types.machine_resources_v1
    types.manual_batch_tuning_parameters = types.manual_batch_tuning_parameters_v1
    types.model = types.model_v1
    types.model_evaluation = types.model_evaluation_v1
    types.model_evaluation_slice = types.model_evaluation_slice_v1
    types.model_service = types.model_service_v1
    types.operation = types.operation_v1
    types.pipeline_service = types.pipeline_service_v1
    types.pipeline_state = types.pipeline_state_v1
    types.prediction_service = types.prediction_service_v1
    types.specialist_pool = types.specialist_pool_v1
    types.specialist_pool_service = types.specialist_pool_service_v1
    types.training_pipeline = types.training_pipeline_v1

__all__ = (
    DEFAULT_VERSION,
    V1BETA1,
    V1,
    services,
    types,
)
