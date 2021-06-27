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

from .services.dataset_service import DatasetServiceClient
from .services.dataset_service import DatasetServiceAsyncClient
from .services.endpoint_service import EndpointServiceClient
from .services.endpoint_service import EndpointServiceAsyncClient
from .services.job_service import JobServiceClient
from .services.job_service import JobServiceAsyncClient
from .services.migration_service import MigrationServiceClient
from .services.migration_service import MigrationServiceAsyncClient
from .services.model_service import ModelServiceClient
from .services.model_service import ModelServiceAsyncClient
from .services.pipeline_service import PipelineServiceClient
from .services.pipeline_service import PipelineServiceAsyncClient
from .services.prediction_service import PredictionServiceClient
from .services.prediction_service import PredictionServiceAsyncClient
from .services.specialist_pool_service import SpecialistPoolServiceClient
from .services.specialist_pool_service import SpecialistPoolServiceAsyncClient

from .types.accelerator_type import AcceleratorType
from .types.annotation import Annotation
from .types.annotation_spec import AnnotationSpec
from .types.batch_prediction_job import BatchPredictionJob
from .types.completion_stats import CompletionStats
from .types.custom_job import ContainerSpec
from .types.custom_job import CustomJob
from .types.custom_job import CustomJobSpec
from .types.custom_job import PythonPackageSpec
from .types.custom_job import Scheduling
from .types.custom_job import WorkerPoolSpec
from .types.data_item import DataItem
from .types.data_labeling_job import ActiveLearningConfig
from .types.data_labeling_job import DataLabelingJob
from .types.data_labeling_job import SampleConfig
from .types.data_labeling_job import TrainingConfig
from .types.dataset import Dataset
from .types.dataset import ExportDataConfig
from .types.dataset import ImportDataConfig
from .types.dataset_service import CreateDatasetOperationMetadata
from .types.dataset_service import CreateDatasetRequest
from .types.dataset_service import DeleteDatasetRequest
from .types.dataset_service import ExportDataOperationMetadata
from .types.dataset_service import ExportDataRequest
from .types.dataset_service import ExportDataResponse
from .types.dataset_service import GetAnnotationSpecRequest
from .types.dataset_service import GetDatasetRequest
from .types.dataset_service import ImportDataOperationMetadata
from .types.dataset_service import ImportDataRequest
from .types.dataset_service import ImportDataResponse
from .types.dataset_service import ListAnnotationsRequest
from .types.dataset_service import ListAnnotationsResponse
from .types.dataset_service import ListDataItemsRequest
from .types.dataset_service import ListDataItemsResponse
from .types.dataset_service import ListDatasetsRequest
from .types.dataset_service import ListDatasetsResponse
from .types.dataset_service import UpdateDatasetRequest
from .types.deployed_model_ref import DeployedModelRef
from .types.encryption_spec import EncryptionSpec
from .types.endpoint import DeployedModel
from .types.endpoint import Endpoint
from .types.endpoint_service import CreateEndpointOperationMetadata
from .types.endpoint_service import CreateEndpointRequest
from .types.endpoint_service import DeleteEndpointRequest
from .types.endpoint_service import DeployModelOperationMetadata
from .types.endpoint_service import DeployModelRequest
from .types.endpoint_service import DeployModelResponse
from .types.endpoint_service import GetEndpointRequest
from .types.endpoint_service import ListEndpointsRequest
from .types.endpoint_service import ListEndpointsResponse
from .types.endpoint_service import UndeployModelOperationMetadata
from .types.endpoint_service import UndeployModelRequest
from .types.endpoint_service import UndeployModelResponse
from .types.endpoint_service import UpdateEndpointRequest
from .types.env_var import EnvVar
from .types.hyperparameter_tuning_job import HyperparameterTuningJob
from .types.io import BigQueryDestination
from .types.io import BigQuerySource
from .types.io import ContainerRegistryDestination
from .types.io import GcsDestination
from .types.io import GcsSource
from .types.job_service import CancelBatchPredictionJobRequest
from .types.job_service import CancelCustomJobRequest
from .types.job_service import CancelDataLabelingJobRequest
from .types.job_service import CancelHyperparameterTuningJobRequest
from .types.job_service import CreateBatchPredictionJobRequest
from .types.job_service import CreateCustomJobRequest
from .types.job_service import CreateDataLabelingJobRequest
from .types.job_service import CreateHyperparameterTuningJobRequest
from .types.job_service import DeleteBatchPredictionJobRequest
from .types.job_service import DeleteCustomJobRequest
from .types.job_service import DeleteDataLabelingJobRequest
from .types.job_service import DeleteHyperparameterTuningJobRequest
from .types.job_service import GetBatchPredictionJobRequest
from .types.job_service import GetCustomJobRequest
from .types.job_service import GetDataLabelingJobRequest
from .types.job_service import GetHyperparameterTuningJobRequest
from .types.job_service import ListBatchPredictionJobsRequest
from .types.job_service import ListBatchPredictionJobsResponse
from .types.job_service import ListCustomJobsRequest
from .types.job_service import ListCustomJobsResponse
from .types.job_service import ListDataLabelingJobsRequest
from .types.job_service import ListDataLabelingJobsResponse
from .types.job_service import ListHyperparameterTuningJobsRequest
from .types.job_service import ListHyperparameterTuningJobsResponse
from .types.job_state import JobState
from .types.machine_resources import AutomaticResources
from .types.machine_resources import BatchDedicatedResources
from .types.machine_resources import DedicatedResources
from .types.machine_resources import DiskSpec
from .types.machine_resources import MachineSpec
from .types.machine_resources import ResourcesConsumed
from .types.manual_batch_tuning_parameters import ManualBatchTuningParameters
from .types.migratable_resource import MigratableResource
from .types.migration_service import BatchMigrateResourcesOperationMetadata
from .types.migration_service import BatchMigrateResourcesRequest
from .types.migration_service import BatchMigrateResourcesResponse
from .types.migration_service import MigrateResourceRequest
from .types.migration_service import MigrateResourceResponse
from .types.migration_service import SearchMigratableResourcesRequest
from .types.migration_service import SearchMigratableResourcesResponse
from .types.model import Model
from .types.model import ModelContainerSpec
from .types.model import Port
from .types.model import PredictSchemata
from .types.model_evaluation import ModelEvaluation
from .types.model_evaluation_slice import ModelEvaluationSlice
from .types.model_service import DeleteModelRequest
from .types.model_service import ExportModelOperationMetadata
from .types.model_service import ExportModelRequest
from .types.model_service import ExportModelResponse
from .types.model_service import GetModelEvaluationRequest
from .types.model_service import GetModelEvaluationSliceRequest
from .types.model_service import GetModelRequest
from .types.model_service import ListModelEvaluationSlicesRequest
from .types.model_service import ListModelEvaluationSlicesResponse
from .types.model_service import ListModelEvaluationsRequest
from .types.model_service import ListModelEvaluationsResponse
from .types.model_service import ListModelsRequest
from .types.model_service import ListModelsResponse
from .types.model_service import UpdateModelRequest
from .types.model_service import UploadModelOperationMetadata
from .types.model_service import UploadModelRequest
from .types.model_service import UploadModelResponse
from .types.operation import DeleteOperationMetadata
from .types.operation import GenericOperationMetadata
from .types.pipeline_service import CancelTrainingPipelineRequest
from .types.pipeline_service import CreateTrainingPipelineRequest
from .types.pipeline_service import DeleteTrainingPipelineRequest
from .types.pipeline_service import GetTrainingPipelineRequest
from .types.pipeline_service import ListTrainingPipelinesRequest
from .types.pipeline_service import ListTrainingPipelinesResponse
from .types.pipeline_state import PipelineState
from .types.prediction_service import PredictRequest
from .types.prediction_service import PredictResponse
from .types.specialist_pool import SpecialistPool
from .types.specialist_pool_service import CreateSpecialistPoolOperationMetadata
from .types.specialist_pool_service import CreateSpecialistPoolRequest
from .types.specialist_pool_service import DeleteSpecialistPoolRequest
from .types.specialist_pool_service import GetSpecialistPoolRequest
from .types.specialist_pool_service import ListSpecialistPoolsRequest
from .types.specialist_pool_service import ListSpecialistPoolsResponse
from .types.specialist_pool_service import UpdateSpecialistPoolOperationMetadata
from .types.specialist_pool_service import UpdateSpecialistPoolRequest
from .types.study import Measurement
from .types.study import StudySpec
from .types.study import Trial
from .types.training_pipeline import FilterSplit
from .types.training_pipeline import FractionSplit
from .types.training_pipeline import InputDataConfig
from .types.training_pipeline import PredefinedSplit
from .types.training_pipeline import TimestampSplit
from .types.training_pipeline import TrainingPipeline
from .types.user_action_reference import UserActionReference

__all__ = (
    "DatasetServiceAsyncClient",
    "EndpointServiceAsyncClient",
    "JobServiceAsyncClient",
    "MigrationServiceAsyncClient",
    "ModelServiceAsyncClient",
    "PipelineServiceAsyncClient",
    "PredictionServiceAsyncClient",
    "SpecialistPoolServiceAsyncClient",
    "AcceleratorType",
    "ActiveLearningConfig",
    "Annotation",
    "AnnotationSpec",
    "AutomaticResources",
    "BatchDedicatedResources",
    "BatchMigrateResourcesOperationMetadata",
    "BatchMigrateResourcesRequest",
    "BatchMigrateResourcesResponse",
    "BatchPredictionJob",
    "BigQueryDestination",
    "BigQuerySource",
    "CancelBatchPredictionJobRequest",
    "CancelCustomJobRequest",
    "CancelDataLabelingJobRequest",
    "CancelHyperparameterTuningJobRequest",
    "CancelTrainingPipelineRequest",
    "CompletionStats",
    "ContainerRegistryDestination",
    "ContainerSpec",
    "CreateBatchPredictionJobRequest",
    "CreateCustomJobRequest",
    "CreateDataLabelingJobRequest",
    "CreateDatasetOperationMetadata",
    "CreateDatasetRequest",
    "CreateEndpointOperationMetadata",
    "CreateEndpointRequest",
    "CreateHyperparameterTuningJobRequest",
    "CreateSpecialistPoolOperationMetadata",
    "CreateSpecialistPoolRequest",
    "CreateTrainingPipelineRequest",
    "CustomJob",
    "CustomJobSpec",
    "DataItem",
    "DataLabelingJob",
    "Dataset",
    "DatasetServiceClient",
    "DedicatedResources",
    "DeleteBatchPredictionJobRequest",
    "DeleteCustomJobRequest",
    "DeleteDataLabelingJobRequest",
    "DeleteDatasetRequest",
    "DeleteEndpointRequest",
    "DeleteHyperparameterTuningJobRequest",
    "DeleteModelRequest",
    "DeleteOperationMetadata",
    "DeleteSpecialistPoolRequest",
    "DeleteTrainingPipelineRequest",
    "DeployModelOperationMetadata",
    "DeployModelRequest",
    "DeployModelResponse",
    "DeployedModel",
    "DeployedModelRef",
    "DiskSpec",
    "EncryptionSpec",
    "Endpoint",
    "EndpointServiceClient",
    "EnvVar",
    "ExportDataConfig",
    "ExportDataOperationMetadata",
    "ExportDataRequest",
    "ExportDataResponse",
    "ExportModelOperationMetadata",
    "ExportModelRequest",
    "ExportModelResponse",
    "FilterSplit",
    "FractionSplit",
    "GcsDestination",
    "GcsSource",
    "GenericOperationMetadata",
    "GetAnnotationSpecRequest",
    "GetBatchPredictionJobRequest",
    "GetCustomJobRequest",
    "GetDataLabelingJobRequest",
    "GetDatasetRequest",
    "GetEndpointRequest",
    "GetHyperparameterTuningJobRequest",
    "GetModelEvaluationRequest",
    "GetModelEvaluationSliceRequest",
    "GetModelRequest",
    "GetSpecialistPoolRequest",
    "GetTrainingPipelineRequest",
    "HyperparameterTuningJob",
    "ImportDataConfig",
    "ImportDataOperationMetadata",
    "ImportDataRequest",
    "ImportDataResponse",
    "InputDataConfig",
    "JobServiceClient",
    "JobState",
    "ListAnnotationsRequest",
    "ListAnnotationsResponse",
    "ListBatchPredictionJobsRequest",
    "ListBatchPredictionJobsResponse",
    "ListCustomJobsRequest",
    "ListCustomJobsResponse",
    "ListDataItemsRequest",
    "ListDataItemsResponse",
    "ListDataLabelingJobsRequest",
    "ListDataLabelingJobsResponse",
    "ListDatasetsRequest",
    "ListDatasetsResponse",
    "ListEndpointsRequest",
    "ListEndpointsResponse",
    "ListHyperparameterTuningJobsRequest",
    "ListHyperparameterTuningJobsResponse",
    "ListModelEvaluationSlicesRequest",
    "ListModelEvaluationSlicesResponse",
    "ListModelEvaluationsRequest",
    "ListModelEvaluationsResponse",
    "ListModelsRequest",
    "ListModelsResponse",
    "ListSpecialistPoolsRequest",
    "ListSpecialistPoolsResponse",
    "ListTrainingPipelinesRequest",
    "ListTrainingPipelinesResponse",
    "MachineSpec",
    "ManualBatchTuningParameters",
    "Measurement",
    "MigratableResource",
    "MigrateResourceRequest",
    "MigrateResourceResponse",
    "MigrationServiceClient",
    "Model",
    "ModelContainerSpec",
    "ModelEvaluation",
    "ModelEvaluationSlice",
    "ModelServiceClient",
    "PipelineServiceClient",
    "PipelineState",
    "Port",
    "PredefinedSplit",
    "PredictRequest",
    "PredictResponse",
    "PredictSchemata",
    "PredictionServiceClient",
    "PythonPackageSpec",
    "ResourcesConsumed",
    "SampleConfig",
    "Scheduling",
    "SearchMigratableResourcesRequest",
    "SearchMigratableResourcesResponse",
    "SpecialistPool",
    "SpecialistPoolServiceClient",
    "StudySpec",
    "TimestampSplit",
    "TrainingConfig",
    "TrainingPipeline",
    "Trial",
    "UndeployModelOperationMetadata",
    "UndeployModelRequest",
    "UndeployModelResponse",
    "UpdateDatasetRequest",
    "UpdateEndpointRequest",
    "UpdateModelRequest",
    "UpdateSpecialistPoolOperationMetadata",
    "UpdateSpecialistPoolRequest",
    "UploadModelOperationMetadata",
    "UploadModelRequest",
    "UploadModelResponse",
    "UserActionReference",
    "WorkerPoolSpec",
)
