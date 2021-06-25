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

from google.cloud.aiplatform_v1.services.dataset_service.client import DatasetServiceClient
from google.cloud.aiplatform_v1.services.dataset_service.async_client import DatasetServiceAsyncClient
from google.cloud.aiplatform_v1.services.endpoint_service.client import EndpointServiceClient
from google.cloud.aiplatform_v1.services.endpoint_service.async_client import EndpointServiceAsyncClient
from google.cloud.aiplatform_v1.services.job_service.client import JobServiceClient
from google.cloud.aiplatform_v1.services.job_service.async_client import JobServiceAsyncClient
from google.cloud.aiplatform_v1.services.migration_service.client import MigrationServiceClient
from google.cloud.aiplatform_v1.services.migration_service.async_client import MigrationServiceAsyncClient
from google.cloud.aiplatform_v1.services.model_service.client import ModelServiceClient
from google.cloud.aiplatform_v1.services.model_service.async_client import ModelServiceAsyncClient
from google.cloud.aiplatform_v1.services.pipeline_service.client import PipelineServiceClient
from google.cloud.aiplatform_v1.services.pipeline_service.async_client import PipelineServiceAsyncClient
from google.cloud.aiplatform_v1.services.prediction_service.client import PredictionServiceClient
from google.cloud.aiplatform_v1.services.prediction_service.async_client import PredictionServiceAsyncClient
from google.cloud.aiplatform_v1.services.specialist_pool_service.client import SpecialistPoolServiceClient
from google.cloud.aiplatform_v1.services.specialist_pool_service.async_client import SpecialistPoolServiceAsyncClient

from google.cloud.aiplatform_v1.types.accelerator_type import AcceleratorType
from google.cloud.aiplatform_v1.types.annotation import Annotation
from google.cloud.aiplatform_v1.types.annotation_spec import AnnotationSpec
from google.cloud.aiplatform_v1.types.batch_prediction_job import BatchPredictionJob
from google.cloud.aiplatform_v1.types.completion_stats import CompletionStats
from google.cloud.aiplatform_v1.types.custom_job import ContainerSpec
from google.cloud.aiplatform_v1.types.custom_job import CustomJob
from google.cloud.aiplatform_v1.types.custom_job import CustomJobSpec
from google.cloud.aiplatform_v1.types.custom_job import PythonPackageSpec
from google.cloud.aiplatform_v1.types.custom_job import Scheduling
from google.cloud.aiplatform_v1.types.custom_job import WorkerPoolSpec
from google.cloud.aiplatform_v1.types.data_item import DataItem
from google.cloud.aiplatform_v1.types.data_labeling_job import ActiveLearningConfig
from google.cloud.aiplatform_v1.types.data_labeling_job import DataLabelingJob
from google.cloud.aiplatform_v1.types.data_labeling_job import SampleConfig
from google.cloud.aiplatform_v1.types.data_labeling_job import TrainingConfig
from google.cloud.aiplatform_v1.types.dataset import Dataset
from google.cloud.aiplatform_v1.types.dataset import ExportDataConfig
from google.cloud.aiplatform_v1.types.dataset import ImportDataConfig
from google.cloud.aiplatform_v1.types.dataset_service import CreateDatasetOperationMetadata
from google.cloud.aiplatform_v1.types.dataset_service import CreateDatasetRequest
from google.cloud.aiplatform_v1.types.dataset_service import DeleteDatasetRequest
from google.cloud.aiplatform_v1.types.dataset_service import ExportDataOperationMetadata
from google.cloud.aiplatform_v1.types.dataset_service import ExportDataRequest
from google.cloud.aiplatform_v1.types.dataset_service import ExportDataResponse
from google.cloud.aiplatform_v1.types.dataset_service import GetAnnotationSpecRequest
from google.cloud.aiplatform_v1.types.dataset_service import GetDatasetRequest
from google.cloud.aiplatform_v1.types.dataset_service import ImportDataOperationMetadata
from google.cloud.aiplatform_v1.types.dataset_service import ImportDataRequest
from google.cloud.aiplatform_v1.types.dataset_service import ImportDataResponse
from google.cloud.aiplatform_v1.types.dataset_service import ListAnnotationsRequest
from google.cloud.aiplatform_v1.types.dataset_service import ListAnnotationsResponse
from google.cloud.aiplatform_v1.types.dataset_service import ListDataItemsRequest
from google.cloud.aiplatform_v1.types.dataset_service import ListDataItemsResponse
from google.cloud.aiplatform_v1.types.dataset_service import ListDatasetsRequest
from google.cloud.aiplatform_v1.types.dataset_service import ListDatasetsResponse
from google.cloud.aiplatform_v1.types.dataset_service import UpdateDatasetRequest
from google.cloud.aiplatform_v1.types.deployed_model_ref import DeployedModelRef
from google.cloud.aiplatform_v1.types.encryption_spec import EncryptionSpec
from google.cloud.aiplatform_v1.types.endpoint import DeployedModel
from google.cloud.aiplatform_v1.types.endpoint import Endpoint
from google.cloud.aiplatform_v1.types.endpoint_service import CreateEndpointOperationMetadata
from google.cloud.aiplatform_v1.types.endpoint_service import CreateEndpointRequest
from google.cloud.aiplatform_v1.types.endpoint_service import DeleteEndpointRequest
from google.cloud.aiplatform_v1.types.endpoint_service import DeployModelOperationMetadata
from google.cloud.aiplatform_v1.types.endpoint_service import DeployModelRequest
from google.cloud.aiplatform_v1.types.endpoint_service import DeployModelResponse
from google.cloud.aiplatform_v1.types.endpoint_service import GetEndpointRequest
from google.cloud.aiplatform_v1.types.endpoint_service import ListEndpointsRequest
from google.cloud.aiplatform_v1.types.endpoint_service import ListEndpointsResponse
from google.cloud.aiplatform_v1.types.endpoint_service import UndeployModelOperationMetadata
from google.cloud.aiplatform_v1.types.endpoint_service import UndeployModelRequest
from google.cloud.aiplatform_v1.types.endpoint_service import UndeployModelResponse
from google.cloud.aiplatform_v1.types.endpoint_service import UpdateEndpointRequest
from google.cloud.aiplatform_v1.types.env_var import EnvVar
from google.cloud.aiplatform_v1.types.hyperparameter_tuning_job import HyperparameterTuningJob
from google.cloud.aiplatform_v1.types.io import BigQueryDestination
from google.cloud.aiplatform_v1.types.io import BigQuerySource
from google.cloud.aiplatform_v1.types.io import ContainerRegistryDestination
from google.cloud.aiplatform_v1.types.io import GcsDestination
from google.cloud.aiplatform_v1.types.io import GcsSource
from google.cloud.aiplatform_v1.types.job_service import CancelBatchPredictionJobRequest
from google.cloud.aiplatform_v1.types.job_service import CancelCustomJobRequest
from google.cloud.aiplatform_v1.types.job_service import CancelDataLabelingJobRequest
from google.cloud.aiplatform_v1.types.job_service import CancelHyperparameterTuningJobRequest
from google.cloud.aiplatform_v1.types.job_service import CreateBatchPredictionJobRequest
from google.cloud.aiplatform_v1.types.job_service import CreateCustomJobRequest
from google.cloud.aiplatform_v1.types.job_service import CreateDataLabelingJobRequest
from google.cloud.aiplatform_v1.types.job_service import CreateHyperparameterTuningJobRequest
from google.cloud.aiplatform_v1.types.job_service import DeleteBatchPredictionJobRequest
from google.cloud.aiplatform_v1.types.job_service import DeleteCustomJobRequest
from google.cloud.aiplatform_v1.types.job_service import DeleteDataLabelingJobRequest
from google.cloud.aiplatform_v1.types.job_service import DeleteHyperparameterTuningJobRequest
from google.cloud.aiplatform_v1.types.job_service import GetBatchPredictionJobRequest
from google.cloud.aiplatform_v1.types.job_service import GetCustomJobRequest
from google.cloud.aiplatform_v1.types.job_service import GetDataLabelingJobRequest
from google.cloud.aiplatform_v1.types.job_service import GetHyperparameterTuningJobRequest
from google.cloud.aiplatform_v1.types.job_service import ListBatchPredictionJobsRequest
from google.cloud.aiplatform_v1.types.job_service import ListBatchPredictionJobsResponse
from google.cloud.aiplatform_v1.types.job_service import ListCustomJobsRequest
from google.cloud.aiplatform_v1.types.job_service import ListCustomJobsResponse
from google.cloud.aiplatform_v1.types.job_service import ListDataLabelingJobsRequest
from google.cloud.aiplatform_v1.types.job_service import ListDataLabelingJobsResponse
from google.cloud.aiplatform_v1.types.job_service import ListHyperparameterTuningJobsRequest
from google.cloud.aiplatform_v1.types.job_service import ListHyperparameterTuningJobsResponse
from google.cloud.aiplatform_v1.types.job_state import JobState
from google.cloud.aiplatform_v1.types.machine_resources import AutomaticResources
from google.cloud.aiplatform_v1.types.machine_resources import BatchDedicatedResources
from google.cloud.aiplatform_v1.types.machine_resources import DedicatedResources
from google.cloud.aiplatform_v1.types.machine_resources import DiskSpec
from google.cloud.aiplatform_v1.types.machine_resources import MachineSpec
from google.cloud.aiplatform_v1.types.machine_resources import ResourcesConsumed
from google.cloud.aiplatform_v1.types.manual_batch_tuning_parameters import ManualBatchTuningParameters
from google.cloud.aiplatform_v1.types.migratable_resource import MigratableResource
from google.cloud.aiplatform_v1.types.migration_service import BatchMigrateResourcesOperationMetadata
from google.cloud.aiplatform_v1.types.migration_service import BatchMigrateResourcesRequest
from google.cloud.aiplatform_v1.types.migration_service import BatchMigrateResourcesResponse
from google.cloud.aiplatform_v1.types.migration_service import MigrateResourceRequest
from google.cloud.aiplatform_v1.types.migration_service import MigrateResourceResponse
from google.cloud.aiplatform_v1.types.migration_service import SearchMigratableResourcesRequest
from google.cloud.aiplatform_v1.types.migration_service import SearchMigratableResourcesResponse
from google.cloud.aiplatform_v1.types.model import Model
from google.cloud.aiplatform_v1.types.model import ModelContainerSpec
from google.cloud.aiplatform_v1.types.model import Port
from google.cloud.aiplatform_v1.types.model import PredictSchemata
from google.cloud.aiplatform_v1.types.model_evaluation import ModelEvaluation
from google.cloud.aiplatform_v1.types.model_evaluation_slice import ModelEvaluationSlice
from google.cloud.aiplatform_v1.types.model_service import DeleteModelRequest
from google.cloud.aiplatform_v1.types.model_service import ExportModelOperationMetadata
from google.cloud.aiplatform_v1.types.model_service import ExportModelRequest
from google.cloud.aiplatform_v1.types.model_service import ExportModelResponse
from google.cloud.aiplatform_v1.types.model_service import GetModelEvaluationRequest
from google.cloud.aiplatform_v1.types.model_service import GetModelEvaluationSliceRequest
from google.cloud.aiplatform_v1.types.model_service import GetModelRequest
from google.cloud.aiplatform_v1.types.model_service import ListModelEvaluationSlicesRequest
from google.cloud.aiplatform_v1.types.model_service import ListModelEvaluationSlicesResponse
from google.cloud.aiplatform_v1.types.model_service import ListModelEvaluationsRequest
from google.cloud.aiplatform_v1.types.model_service import ListModelEvaluationsResponse
from google.cloud.aiplatform_v1.types.model_service import ListModelsRequest
from google.cloud.aiplatform_v1.types.model_service import ListModelsResponse
from google.cloud.aiplatform_v1.types.model_service import UpdateModelRequest
from google.cloud.aiplatform_v1.types.model_service import UploadModelOperationMetadata
from google.cloud.aiplatform_v1.types.model_service import UploadModelRequest
from google.cloud.aiplatform_v1.types.model_service import UploadModelResponse
from google.cloud.aiplatform_v1.types.operation import DeleteOperationMetadata
from google.cloud.aiplatform_v1.types.operation import GenericOperationMetadata
from google.cloud.aiplatform_v1.types.pipeline_service import CancelTrainingPipelineRequest
from google.cloud.aiplatform_v1.types.pipeline_service import CreateTrainingPipelineRequest
from google.cloud.aiplatform_v1.types.pipeline_service import DeleteTrainingPipelineRequest
from google.cloud.aiplatform_v1.types.pipeline_service import GetTrainingPipelineRequest
from google.cloud.aiplatform_v1.types.pipeline_service import ListTrainingPipelinesRequest
from google.cloud.aiplatform_v1.types.pipeline_service import ListTrainingPipelinesResponse
from google.cloud.aiplatform_v1.types.pipeline_state import PipelineState
from google.cloud.aiplatform_v1.types.prediction_service import PredictRequest
from google.cloud.aiplatform_v1.types.prediction_service import PredictResponse
from google.cloud.aiplatform_v1.types.specialist_pool import SpecialistPool
from google.cloud.aiplatform_v1.types.specialist_pool_service import CreateSpecialistPoolOperationMetadata
from google.cloud.aiplatform_v1.types.specialist_pool_service import CreateSpecialistPoolRequest
from google.cloud.aiplatform_v1.types.specialist_pool_service import DeleteSpecialistPoolRequest
from google.cloud.aiplatform_v1.types.specialist_pool_service import GetSpecialistPoolRequest
from google.cloud.aiplatform_v1.types.specialist_pool_service import ListSpecialistPoolsRequest
from google.cloud.aiplatform_v1.types.specialist_pool_service import ListSpecialistPoolsResponse
from google.cloud.aiplatform_v1.types.specialist_pool_service import UpdateSpecialistPoolOperationMetadata
from google.cloud.aiplatform_v1.types.specialist_pool_service import UpdateSpecialistPoolRequest
from google.cloud.aiplatform_v1.types.study import Measurement
from google.cloud.aiplatform_v1.types.study import StudySpec
from google.cloud.aiplatform_v1.types.study import Trial
from google.cloud.aiplatform_v1.types.training_pipeline import FilterSplit
from google.cloud.aiplatform_v1.types.training_pipeline import FractionSplit
from google.cloud.aiplatform_v1.types.training_pipeline import InputDataConfig
from google.cloud.aiplatform_v1.types.training_pipeline import PredefinedSplit
from google.cloud.aiplatform_v1.types.training_pipeline import TimestampSplit
from google.cloud.aiplatform_v1.types.training_pipeline import TrainingPipeline
from google.cloud.aiplatform_v1.types.user_action_reference import UserActionReference

__all__ = ('DatasetServiceClient',
    'DatasetServiceAsyncClient',
    'EndpointServiceClient',
    'EndpointServiceAsyncClient',
    'JobServiceClient',
    'JobServiceAsyncClient',
    'MigrationServiceClient',
    'MigrationServiceAsyncClient',
    'ModelServiceClient',
    'ModelServiceAsyncClient',
    'PipelineServiceClient',
    'PipelineServiceAsyncClient',
    'PredictionServiceClient',
    'PredictionServiceAsyncClient',
    'SpecialistPoolServiceClient',
    'SpecialistPoolServiceAsyncClient',
    'AcceleratorType',
    'Annotation',
    'AnnotationSpec',
    'BatchPredictionJob',
    'CompletionStats',
    'ContainerSpec',
    'CustomJob',
    'CustomJobSpec',
    'PythonPackageSpec',
    'Scheduling',
    'WorkerPoolSpec',
    'DataItem',
    'ActiveLearningConfig',
    'DataLabelingJob',
    'SampleConfig',
    'TrainingConfig',
    'Dataset',
    'ExportDataConfig',
    'ImportDataConfig',
    'CreateDatasetOperationMetadata',
    'CreateDatasetRequest',
    'DeleteDatasetRequest',
    'ExportDataOperationMetadata',
    'ExportDataRequest',
    'ExportDataResponse',
    'GetAnnotationSpecRequest',
    'GetDatasetRequest',
    'ImportDataOperationMetadata',
    'ImportDataRequest',
    'ImportDataResponse',
    'ListAnnotationsRequest',
    'ListAnnotationsResponse',
    'ListDataItemsRequest',
    'ListDataItemsResponse',
    'ListDatasetsRequest',
    'ListDatasetsResponse',
    'UpdateDatasetRequest',
    'DeployedModelRef',
    'EncryptionSpec',
    'DeployedModel',
    'Endpoint',
    'CreateEndpointOperationMetadata',
    'CreateEndpointRequest',
    'DeleteEndpointRequest',
    'DeployModelOperationMetadata',
    'DeployModelRequest',
    'DeployModelResponse',
    'GetEndpointRequest',
    'ListEndpointsRequest',
    'ListEndpointsResponse',
    'UndeployModelOperationMetadata',
    'UndeployModelRequest',
    'UndeployModelResponse',
    'UpdateEndpointRequest',
    'EnvVar',
    'HyperparameterTuningJob',
    'BigQueryDestination',
    'BigQuerySource',
    'ContainerRegistryDestination',
    'GcsDestination',
    'GcsSource',
    'CancelBatchPredictionJobRequest',
    'CancelCustomJobRequest',
    'CancelDataLabelingJobRequest',
    'CancelHyperparameterTuningJobRequest',
    'CreateBatchPredictionJobRequest',
    'CreateCustomJobRequest',
    'CreateDataLabelingJobRequest',
    'CreateHyperparameterTuningJobRequest',
    'DeleteBatchPredictionJobRequest',
    'DeleteCustomJobRequest',
    'DeleteDataLabelingJobRequest',
    'DeleteHyperparameterTuningJobRequest',
    'GetBatchPredictionJobRequest',
    'GetCustomJobRequest',
    'GetDataLabelingJobRequest',
    'GetHyperparameterTuningJobRequest',
    'ListBatchPredictionJobsRequest',
    'ListBatchPredictionJobsResponse',
    'ListCustomJobsRequest',
    'ListCustomJobsResponse',
    'ListDataLabelingJobsRequest',
    'ListDataLabelingJobsResponse',
    'ListHyperparameterTuningJobsRequest',
    'ListHyperparameterTuningJobsResponse',
    'JobState',
    'AutomaticResources',
    'BatchDedicatedResources',
    'DedicatedResources',
    'DiskSpec',
    'MachineSpec',
    'ResourcesConsumed',
    'ManualBatchTuningParameters',
    'MigratableResource',
    'BatchMigrateResourcesOperationMetadata',
    'BatchMigrateResourcesRequest',
    'BatchMigrateResourcesResponse',
    'MigrateResourceRequest',
    'MigrateResourceResponse',
    'SearchMigratableResourcesRequest',
    'SearchMigratableResourcesResponse',
    'Model',
    'ModelContainerSpec',
    'Port',
    'PredictSchemata',
    'ModelEvaluation',
    'ModelEvaluationSlice',
    'DeleteModelRequest',
    'ExportModelOperationMetadata',
    'ExportModelRequest',
    'ExportModelResponse',
    'GetModelEvaluationRequest',
    'GetModelEvaluationSliceRequest',
    'GetModelRequest',
    'ListModelEvaluationSlicesRequest',
    'ListModelEvaluationSlicesResponse',
    'ListModelEvaluationsRequest',
    'ListModelEvaluationsResponse',
    'ListModelsRequest',
    'ListModelsResponse',
    'UpdateModelRequest',
    'UploadModelOperationMetadata',
    'UploadModelRequest',
    'UploadModelResponse',
    'DeleteOperationMetadata',
    'GenericOperationMetadata',
    'CancelTrainingPipelineRequest',
    'CreateTrainingPipelineRequest',
    'DeleteTrainingPipelineRequest',
    'GetTrainingPipelineRequest',
    'ListTrainingPipelinesRequest',
    'ListTrainingPipelinesResponse',
    'PipelineState',
    'PredictRequest',
    'PredictResponse',
    'SpecialistPool',
    'CreateSpecialistPoolOperationMetadata',
    'CreateSpecialistPoolRequest',
    'DeleteSpecialistPoolRequest',
    'GetSpecialistPoolRequest',
    'ListSpecialistPoolsRequest',
    'ListSpecialistPoolsResponse',
    'UpdateSpecialistPoolOperationMetadata',
    'UpdateSpecialistPoolRequest',
    'Measurement',
    'StudySpec',
    'Trial',
    'FilterSplit',
    'FractionSplit',
    'InputDataConfig',
    'PredefinedSplit',
    'TimestampSplit',
    'TrainingPipeline',
    'UserActionReference',
)
