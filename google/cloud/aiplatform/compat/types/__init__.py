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
    accelerator_type as accelerator_type_v1beta1,
    annotation as annotation_v1beta1,
    annotation_spec as annotation_spec_v1beta1,
    artifact as artifact_v1beta1,
    batch_prediction_job as batch_prediction_job_v1beta1,
    completion_stats as completion_stats_v1beta1,
    context as context_v1beta1,
    custom_job as custom_job_v1beta1,
    data_item as data_item_v1beta1,
    data_labeling_job as data_labeling_job_v1beta1,
    dataset as dataset_v1beta1,
    dataset_service as dataset_service_v1beta1,
    deployed_index_ref as matching_engine_deployed_index_ref_v1beta1,
    deployed_model_ref as deployed_model_ref_v1beta1,
    deployment_resource_pool as deployment_resource_pool_v1beta1,
    deployment_resource_pool_service as deployment_resource_pool_service_v1beta1,
    encryption_spec as encryption_spec_v1beta1,
    endpoint as endpoint_v1beta1,
    endpoint_service as endpoint_service_v1beta1,
    entity_type as entity_type_v1beta1,
    env_var as env_var_v1beta1,
    event as event_v1beta1,
    execution as execution_v1beta1,
    explanation as explanation_v1beta1,
    explanation_metadata as explanation_metadata_v1beta1,
    feature as feature_v1beta1,
    feature_monitoring_stats as feature_monitoring_stats_v1beta1,
    feature_selector as feature_selector_v1beta1,
    featurestore as featurestore_v1beta1,
    featurestore_monitoring as featurestore_monitoring_v1beta1,
    featurestore_online_service as featurestore_online_service_v1beta1,
    featurestore_service as featurestore_service_v1beta1,
    index as index_v1beta1,
    index_endpoint as index_endpoint_v1beta1,
    hyperparameter_tuning_job as hyperparameter_tuning_job_v1beta1,
    io as io_v1beta1,
    job_service as job_service_v1beta1,
    job_state as job_state_v1beta1,
    lineage_subgraph as lineage_subgraph_v1beta1,
    machine_resources as machine_resources_v1beta1,
    manual_batch_tuning_parameters as manual_batch_tuning_parameters_v1beta1,
    match_service as match_service_v1beta1,
    metadata_schema as metadata_schema_v1beta1,
    metadata_service as metadata_service_v1beta1,
    metadata_store as metadata_store_v1beta1,
    model as model_v1beta1,
    model_evaluation as model_evaluation_v1beta1,
    model_evaluation_slice as model_evaluation_slice_v1beta1,
    model_deployment_monitoring_job as model_deployment_monitoring_job_v1beta1,
    model_garden_service as model_garden_service_v1beta1,
    model_service as model_service_v1beta1,
    model_monitoring as model_monitoring_v1beta1,
    operation as operation_v1beta1,
    pipeline_failure_policy as pipeline_failure_policy_v1beta1,
    pipeline_job as pipeline_job_v1beta1,
    pipeline_service as pipeline_service_v1beta1,
    pipeline_state as pipeline_state_v1beta1,
    prediction_service as prediction_service_v1beta1,
    publisher_model as publisher_model_v1beta1,
    schedule as schedule_v1beta1,
    schedule_service as schedule_service_v1beta1,
    specialist_pool as specialist_pool_v1beta1,
    specialist_pool_service as specialist_pool_service_v1beta1,
    study as study_v1beta1,
    tensorboard as tensorboard_v1beta1,
    tensorboard_data as tensorboard_data_v1beta1,
    tensorboard_experiment as tensorboard_experiment_v1beta1,
    tensorboard_run as tensorboard_run_v1beta1,
    tensorboard_service as tensorboard_service_v1beta1,
    tensorboard_time_series as tensorboard_time_series_v1beta1,
    training_pipeline as training_pipeline_v1beta1,
    types as types_v1beta1,
    vizier_service as vizier_service_v1beta1,
)
from google.cloud.aiplatform_v1.types import (
    accelerator_type as accelerator_type_v1,
    annotation as annotation_v1,
    annotation_spec as annotation_spec_v1,
    artifact as artifact_v1,
    batch_prediction_job as batch_prediction_job_v1,
    completion_stats as completion_stats_v1,
    context as context_v1,
    custom_job as custom_job_v1,
    data_item as data_item_v1,
    data_labeling_job as data_labeling_job_v1,
    dataset as dataset_v1,
    dataset_service as dataset_service_v1,
    deployed_index_ref as matching_engine_deployed_index_ref_v1,
    deployed_model_ref as deployed_model_ref_v1,
    encryption_spec as encryption_spec_v1,
    endpoint as endpoint_v1,
    endpoint_service as endpoint_service_v1,
    entity_type as entity_type_v1,
    env_var as env_var_v1,
    event as event_v1,
    execution as execution_v1,
    explanation as explanation_v1,
    explanation_metadata as explanation_metadata_v1,
    feature as feature_v1,
    feature_monitoring_stats as feature_monitoring_stats_v1,
    feature_selector as feature_selector_v1,
    featurestore as featurestore_v1,
    featurestore_online_service as featurestore_online_service_v1,
    featurestore_service as featurestore_service_v1,
    hyperparameter_tuning_job as hyperparameter_tuning_job_v1,
    index as index_v1,
    index_endpoint as index_endpoint_v1,
    io as io_v1,
    job_service as job_service_v1,
    job_state as job_state_v1,
    lineage_subgraph as lineage_subgraph_v1,
    machine_resources as machine_resources_v1,
    manual_batch_tuning_parameters as manual_batch_tuning_parameters_v1,
    metadata_service as metadata_service_v1,
    metadata_schema as metadata_schema_v1,
    metadata_store as metadata_store_v1,
    model as model_v1,
    model_evaluation as model_evaluation_v1,
    model_evaluation_slice as model_evaluation_slice_v1,
    model_deployment_monitoring_job as model_deployment_monitoring_job_v1,
    model_service as model_service_v1,
    model_monitoring as model_monitoring_v1,
    operation as operation_v1,
    pipeline_failure_policy as pipeline_failure_policy_v1,
    pipeline_job as pipeline_job_v1,
    pipeline_service as pipeline_service_v1,
    pipeline_state as pipeline_state_v1,
    prediction_service as prediction_service_v1,
    publisher_model as publisher_model_v1,
    schedule as schedule_v1,
    schedule_service as schedule_service_v1,
    specialist_pool as specialist_pool_v1,
    specialist_pool_service as specialist_pool_service_v1,
    study as study_v1,
    tensorboard as tensorboard_v1,
    tensorboard_data as tensorboard_data_v1,
    tensorboard_experiment as tensorboard_experiment_v1,
    tensorboard_run as tensorboard_run_v1,
    tensorboard_service as tensorboard_service_v1,
    tensorboard_time_series as tensorboard_time_series_v1,
    training_pipeline as training_pipeline_v1,
    types as types_v1,
    vizier_service as vizier_service_v1,
)

from google.cloud.aiplatform.compat import versions


if versions.DEFAULT_VERSION == versions.V1BETA1:
    accelerator_type = accelerator_type_v1beta1
    annotation = annotation_v1beta1
    annotation_spec = annotation_spec_v1beta1
    artifact = artifact_v1beta1
    batch_prediction_job = batch_prediction_job_v1beta1
    completion_stats = completion_stats_v1beta1
    context = context_v1beta1
    custom_job = custom_job_v1beta1
    data_item = data_item_v1beta1
    data_labeling_job = data_labeling_job_v1beta1
    dataset = dataset_v1beta1
    dataset_service = dataset_service_v1beta1
    deployed_model_ref = deployed_model_ref_v1beta1
    deployment_resource_pool = deployment_resource_pool_v1beta1
    encryption_spec = encryption_spec_v1beta1
    endpoint = endpoint_v1beta1
    endpoint_service = endpoint_service_v1beta1
    entity_type = entity_type_v1beta1
    env_var = env_var_v1beta1
    event = event_v1beta1
    execution = execution_v1beta1
    explanation = explanation_v1beta1
    explanation_metadata = explanation_metadata_v1beta1
    feature = feature_v1beta1
    feature_monitoring_stats = feature_monitoring_stats_v1beta1
    feature_selector = feature_selector_v1beta1
    featurestore = featurestore_v1beta1
    featurestore_monitoring = featurestore_monitoring_v1beta1
    featurestore_online_service = featurestore_online_service_v1beta1
    featurestore_service = featurestore_service_v1beta1
    hyperparameter_tuning_job = hyperparameter_tuning_job_v1beta1
    index = index_v1beta1
    index_endpoint = index_endpoint_v1beta1
    io = io_v1beta1
    job_service = job_service_v1beta1
    job_state = job_state_v1beta1
    lineage_subgraph = lineage_subgraph_v1beta1
    machine_resources = machine_resources_v1beta1
    manual_batch_tuning_parameters = manual_batch_tuning_parameters_v1beta1
    matching_engine_deployed_index_ref = matching_engine_deployed_index_ref_v1beta1
    matching_engine_index = index_v1beta1
    matching_engine_index_endpoint = index_endpoint_v1beta1
    metadata_service = metadata_service_v1beta1
    metadata_schema = metadata_schema_v1beta1
    metadata_store = metadata_store_v1beta1
    model = model_v1beta1
    model_evaluation = model_evaluation_v1beta1
    model_evaluation_slice = model_evaluation_slice_v1beta1
    model_deployment_monitoring_job = model_deployment_monitoring_job_v1beta1
    model_garden_service = model_garden_service_v1beta1
    model_monitoring = model_monitoring_v1beta1
    model_service = model_service_v1beta1
    operation = operation_v1beta1
    pipeline_failure_policy = pipeline_failure_policy_v1beta1
    pipeline_job = pipeline_job_v1beta1
    pipeline_service = pipeline_service_v1beta1
    pipeline_state = pipeline_state_v1beta1
    prediction_service = prediction_service_v1beta1
    publisher_model = publisher_model_v1beta1
    schedule = schedule_v1beta1
    schedule_service = schedule_service_v1beta1
    specialist_pool = specialist_pool_v1beta1
    specialist_pool_service = specialist_pool_service_v1beta1
    study = study_v1beta1
    tensorboard = tensorboard_v1beta1
    tensorboard_service = tensorboard_service_v1beta1
    tensorboard_data = tensorboard_data_v1beta1
    tensorboard_experiment = tensorboard_experiment_v1beta1
    tensorboard_run = tensorboard_run_v1beta1
    tensorboard_service = tensorboard_service_v1beta1
    tensorboard_time_series = tensorboard_time_series_v1beta1
    training_pipeline = training_pipeline_v1beta1
    types = types_v1beta1
    vizier_service = vizier_service_v1beta1

# if versions.DEFAULT_VERSION == versions.V1:
else:
    accelerator_type = accelerator_type_v1
    annotation = annotation_v1
    annotation_spec = annotation_spec_v1
    artifact = artifact_v1
    batch_prediction_job = batch_prediction_job_v1
    completion_stats = completion_stats_v1
    context = context_v1
    custom_job = custom_job_v1
    data_item = data_item_v1
    data_labeling_job = data_labeling_job_v1
    dataset = dataset_v1
    dataset_service = dataset_service_v1
    deployed_model_ref = deployed_model_ref_v1
    encryption_spec = encryption_spec_v1
    endpoint = endpoint_v1
    endpoint_service = endpoint_service_v1
    entity_type = entity_type_v1
    env_var = env_var_v1
    event = event_v1
    execution = execution_v1
    explanation = explanation_v1
    explanation_metadata = explanation_metadata_v1
    feature = feature_v1
    feature_monitoring_stats = feature_monitoring_stats_v1
    feature_selector = feature_selector_v1
    featurestore = featurestore_v1
    featurestore_online_service = featurestore_online_service_v1
    featurestore_service = featurestore_service_v1
    hyperparameter_tuning_job = hyperparameter_tuning_job_v1
    index = index_v1
    index_endpoint = index_endpoint_v1
    io = io_v1
    job_service = job_service_v1
    job_state = job_state_v1
    lineage_subgraph = lineage_subgraph_v1
    machine_resources = machine_resources_v1
    manual_batch_tuning_parameters = manual_batch_tuning_parameters_v1
    matching_engine_deployed_index_ref = matching_engine_deployed_index_ref_v1
    matching_engine_index = index_v1
    matching_engine_index_endpoint = index_endpoint_v1
    metadata_service = metadata_service_v1
    metadata_schema = metadata_schema_v1
    metadata_store = metadata_store_v1
    model = model_v1
    model_evaluation = model_evaluation_v1
    model_evaluation_slice = model_evaluation_slice_v1
    model_deployment_monitoring_job = model_deployment_monitoring_job_v1
    model_monitoring = model_monitoring_v1
    model_service = model_service_v1
    operation = operation_v1
    pipeline_failure_policy = pipeline_failure_policy_v1
    pipeline_job = pipeline_job_v1
    pipeline_service = pipeline_service_v1
    pipeline_state = pipeline_state_v1
    prediction_service = prediction_service_v1
    publisher_model = publisher_model_v1
    schedule = schedule_v1
    schedule_service = schedule_service_v1
    specialist_pool = specialist_pool_v1
    specialist_pool_service = specialist_pool_service_v1
    study = study_v1
    tensorboard = tensorboard_v1
    tensorboard_service = tensorboard_service_v1
    tensorboard_data = tensorboard_data_v1
    tensorboard_experiment = tensorboard_experiment_v1
    tensorboard_run = tensorboard_run_v1
    tensorboard_service = tensorboard_service_v1
    tensorboard_time_series = tensorboard_time_series_v1
    training_pipeline = training_pipeline_v1
    types = types_v1
    vizier_service = vizier_service_v1


__all__ = (
    # v1
    accelerator_type_v1,
    annotation_v1,
    annotation_spec_v1,
    artifact_v1,
    batch_prediction_job_v1,
    completion_stats_v1,
    context_v1,
    custom_job_v1,
    data_item_v1,
    data_labeling_job_v1,
    dataset_v1,
    dataset_service_v1,
    deployed_model_ref_v1,
    encryption_spec_v1,
    endpoint_v1,
    endpoint_service_v1,
    entity_type_v1,
    env_var_v1,
    event_v1,
    execution_v1,
    explanation_v1,
    explanation_metadata_v1,
    feature_v1,
    feature_monitoring_stats_v1,
    feature_selector_v1,
    featurestore_v1,
    featurestore_online_service_v1,
    featurestore_service_v1,
    hyperparameter_tuning_job_v1,
    io_v1,
    job_service_v1,
    job_state_v1,
    lineage_subgraph_v1,
    machine_resources_v1,
    manual_batch_tuning_parameters_v1,
    matching_engine_deployed_index_ref_v1,
    index_v1,
    index_endpoint_v1,
    metadata_service_v1,
    metadata_schema_v1,
    metadata_store_v1,
    model_v1,
    model_evaluation_v1,
    model_evaluation_slice_v1,
    model_deployment_monitoring_job_v1,
    model_service_v1,
    model_monitoring_v1,
    operation_v1,
    pipeline_failure_policy_v1,
    pipeline_job_v1,
    pipeline_service_v1,
    pipeline_state_v1,
    prediction_service_v1,
    publisher_model_v1,
    schedule_v1,
    schedule_service_v1,
    specialist_pool_v1,
    specialist_pool_service_v1,
    tensorboard_v1,
    tensorboard_data_v1,
    tensorboard_experiment_v1,
    tensorboard_run_v1,
    tensorboard_service_v1,
    tensorboard_time_series_v1,
    training_pipeline_v1,
    types_v1,
    study_v1,
    vizier_service_v1,
    # v1beta1
    accelerator_type_v1beta1,
    annotation_v1beta1,
    annotation_spec_v1beta1,
    artifact_v1beta1,
    batch_prediction_job_v1beta1,
    completion_stats_v1beta1,
    context_v1beta1,
    custom_job_v1beta1,
    data_item_v1beta1,
    data_labeling_job_v1beta1,
    dataset_v1beta1,
    dataset_service_v1beta1,
    deployment_resource_pool_v1beta1,
    deployment_resource_pool_service_v1beta1,
    deployed_model_ref_v1beta1,
    encryption_spec_v1beta1,
    endpoint_v1beta1,
    endpoint_service_v1beta1,
    entity_type_v1beta1,
    env_var_v1beta1,
    event_v1beta1,
    execution_v1beta1,
    explanation_v1beta1,
    explanation_metadata_v1beta1,
    feature_v1beta1,
    feature_monitoring_stats_v1beta1,
    feature_selector_v1beta1,
    featurestore_v1beta1,
    featurestore_monitoring_v1beta1,
    featurestore_online_service_v1beta1,
    featurestore_service_v1beta1,
    hyperparameter_tuning_job_v1beta1,
    io_v1beta1,
    job_service_v1beta1,
    job_state_v1beta1,
    lineage_subgraph_v1beta1,
    machine_resources_v1beta1,
    manual_batch_tuning_parameters_v1beta1,
    matching_engine_deployed_index_ref_v1beta1,
    index_v1beta1,
    index_endpoint_v1beta1,
    match_service_v1beta1,
    metadata_service_v1beta1,
    metadata_schema_v1beta1,
    metadata_store_v1beta1,
    model_v1beta1,
    model_evaluation_v1beta1,
    model_evaluation_slice_v1beta1,
    model_deployment_monitoring_job_v1beta1,
    model_garden_service_v1beta1,
    model_service_v1beta1,
    model_monitoring_v1beta1,
    operation_v1beta1,
    pipeline_failure_policy_v1beta1,
    pipeline_job_v1beta1,
    pipeline_service_v1beta1,
    pipeline_state_v1beta1,
    prediction_service_v1beta1,
    publisher_model_v1beta1,
    schedule_v1beta1,
    schedule_service_v1beta1,
    specialist_pool_v1beta1,
    specialist_pool_service_v1beta1,
    study_v1beta1,
    tensorboard_v1beta1,
    tensorboard_data_v1beta1,
    tensorboard_experiment_v1beta1,
    tensorboard_run_v1beta1,
    tensorboard_service_v1beta1,
    tensorboard_time_series_v1beta1,
    training_pipeline_v1beta1,
    types_v1beta1,
    vizier_service_v1beta1,
    # defult
    "accelerator_type",
    "annotation",
    "annotation_spec",
    "artifact",
    "batch_prediction_job",
    "completion_stats",
    "context",
    "custom_job",
    "data_item",
    "data_labeling_job",
    "dataset",
    "dataset_service",
    "deployment_resource_pool",
    "deployed_model_ref",
    "encryption_spec",
    "endpoint",
    "endpoint_service",
    "entity_type",
    "env_var",
    "event",
    "execution",
    "explanation",
    "explanation_metadata",
    "feature",
    "feature_monitoring_stats",
    "feature_selector",
    "featurestore",
    "featurestore_monitoring",
    "featurestore_online_service",
    "featurestore_service",
    "hyperparameter_tuning_job",
    "io",
    "job_service",
    "job_state",
    "lineage_subgraph",
    "machine_resources",
    "manual_batch_tuning_parameters",
    "matching_engine_deployed_index_ref",
    "index",
    "index_endpoint",
    "metadata_service",
    "metadata_schema",
    "metadata_store",
    "model",
    "model_evaluation",
    "model_evaluation_slice",
    "model_deployment_monitoring_job",
    "model_garden_service",
    "model_service",
    "model_monitoring",
    "operation",
    "pipeline_failure_policy",
    "pipeline_job",
    "pipeline_service",
    "pipeline_state",
    "prediction_service",
    "publisher_model",
    "schedule",
    "schedule_service",
    "specialist_pool",
    "specialist_pool_service",
    "study",
    "tensorboard",
    "tensorboard_data",
    "tensorboard_experiment",
    "tensorboard_run",
    "tensorboard_service",
    "tensorboard_time_series",
    "training_pipeline",
    "types",
    "vizier_service",
)

if versions.DEFAULT_VERSION == versions.V1BETA1:
    __all__.extend(
        [
            "deployment_resource_pool_service",
            "match_service",
        ]
    )
