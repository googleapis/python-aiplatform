# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
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

from google.auth.transport.requests import AuthorizedSession  # type: ignore
import json  # type: ignore
import grpc  # type: ignore
from google.auth.transport.grpc import SslCredentials  # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore
from google.api_core import exceptions as core_exceptions
from google.api_core import retry as retries
from google.api_core import rest_helpers
from google.api_core import rest_streaming
from google.api_core import path_template
from google.api_core import gapic_v1

from google.protobuf import json_format
from google.api_core import operations_v1
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.cloud.location import locations_pb2  # type: ignore
from requests import __version__ as requests_version
import dataclasses
import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
import warnings

try:
    OptionalRetry = Union[retries.Retry, gapic_v1.method._MethodDefault, None]
except AttributeError:  # pragma: NO COVER
    OptionalRetry = Union[retries.Retry, object, None]  # type: ignore


from google.cloud.aiplatform_v1.types import batch_prediction_job
from google.cloud.aiplatform_v1.types import (
    batch_prediction_job as gca_batch_prediction_job,
)
from google.cloud.aiplatform_v1.types import custom_job
from google.cloud.aiplatform_v1.types import custom_job as gca_custom_job
from google.cloud.aiplatform_v1.types import data_labeling_job
from google.cloud.aiplatform_v1.types import data_labeling_job as gca_data_labeling_job
from google.cloud.aiplatform_v1.types import hyperparameter_tuning_job
from google.cloud.aiplatform_v1.types import (
    hyperparameter_tuning_job as gca_hyperparameter_tuning_job,
)
from google.cloud.aiplatform_v1.types import job_service
from google.cloud.aiplatform_v1.types import model_deployment_monitoring_job
from google.cloud.aiplatform_v1.types import (
    model_deployment_monitoring_job as gca_model_deployment_monitoring_job,
)
from google.cloud.aiplatform_v1.types import nas_job
from google.cloud.aiplatform_v1.types import nas_job as gca_nas_job
from google.protobuf import empty_pb2  # type: ignore
from google.longrunning import operations_pb2  # type: ignore

from .base import JobServiceTransport, DEFAULT_CLIENT_INFO as BASE_DEFAULT_CLIENT_INFO


DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
    gapic_version=BASE_DEFAULT_CLIENT_INFO.gapic_version,
    grpc_version=None,
    rest_version=requests_version,
)


class JobServiceRestInterceptor:
    """Interceptor for JobService.

    Interceptors are used to manipulate requests, request metadata, and responses
    in arbitrary ways.
    Example use cases include:
    * Logging
    * Verifying requests according to service or custom semantics
    * Stripping extraneous information from responses

    These use cases and more can be enabled by injecting an
    instance of a custom subclass when constructing the JobServiceRestTransport.

    .. code-block:: python
        class MyCustomJobServiceInterceptor(JobServiceRestInterceptor):
            def pre_cancel_batch_prediction_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def pre_cancel_custom_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def pre_cancel_data_labeling_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def pre_cancel_hyperparameter_tuning_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def pre_cancel_nas_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def pre_create_batch_prediction_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_create_batch_prediction_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_create_custom_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_create_custom_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_create_data_labeling_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_create_data_labeling_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_create_hyperparameter_tuning_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_create_hyperparameter_tuning_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_create_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_create_model_deployment_monitoring_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_create_nas_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_create_nas_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_delete_batch_prediction_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_delete_batch_prediction_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_delete_custom_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_delete_custom_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_delete_data_labeling_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_delete_data_labeling_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_delete_hyperparameter_tuning_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_delete_hyperparameter_tuning_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_delete_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_delete_model_deployment_monitoring_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_delete_nas_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_delete_nas_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_get_batch_prediction_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_get_batch_prediction_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_get_custom_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_get_custom_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_get_data_labeling_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_get_data_labeling_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_get_hyperparameter_tuning_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_get_hyperparameter_tuning_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_get_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_get_model_deployment_monitoring_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_get_nas_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_get_nas_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_get_nas_trial_detail(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_get_nas_trial_detail(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_list_batch_prediction_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_list_batch_prediction_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_list_custom_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_list_custom_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_list_data_labeling_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_list_data_labeling_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_list_hyperparameter_tuning_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_list_hyperparameter_tuning_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_list_model_deployment_monitoring_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_list_model_deployment_monitoring_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_list_nas_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_list_nas_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_list_nas_trial_details(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_list_nas_trial_details(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_pause_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def pre_resume_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def pre_search_model_deployment_monitoring_stats_anomalies(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_search_model_deployment_monitoring_stats_anomalies(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_update_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_update_model_deployment_monitoring_job(self, response):
                logging.log(f"Received response: {response}")
                return response

        transport = JobServiceRestTransport(interceptor=MyCustomJobServiceInterceptor())
        client = JobServiceClient(transport=transport)


    """

    def pre_cancel_batch_prediction_job(
        self,
        request: job_service.CancelBatchPredictionJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CancelBatchPredictionJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_batch_prediction_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def pre_cancel_custom_job(
        self,
        request: job_service.CancelCustomJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CancelCustomJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_custom_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def pre_cancel_data_labeling_job(
        self,
        request: job_service.CancelDataLabelingJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CancelDataLabelingJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_data_labeling_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def pre_cancel_hyperparameter_tuning_job(
        self,
        request: job_service.CancelHyperparameterTuningJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.CancelHyperparameterTuningJobRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for cancel_hyperparameter_tuning_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def pre_cancel_nas_job(
        self,
        request: job_service.CancelNasJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CancelNasJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_nas_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def pre_create_batch_prediction_job(
        self,
        request: job_service.CreateBatchPredictionJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CreateBatchPredictionJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for create_batch_prediction_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_create_batch_prediction_job(
        self, response: gca_batch_prediction_job.BatchPredictionJob
    ) -> gca_batch_prediction_job.BatchPredictionJob:
        """Post-rpc interceptor for create_batch_prediction_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_create_custom_job(
        self,
        request: job_service.CreateCustomJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CreateCustomJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for create_custom_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_create_custom_job(
        self, response: gca_custom_job.CustomJob
    ) -> gca_custom_job.CustomJob:
        """Post-rpc interceptor for create_custom_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_create_data_labeling_job(
        self,
        request: job_service.CreateDataLabelingJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CreateDataLabelingJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for create_data_labeling_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_create_data_labeling_job(
        self, response: gca_data_labeling_job.DataLabelingJob
    ) -> gca_data_labeling_job.DataLabelingJob:
        """Post-rpc interceptor for create_data_labeling_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_create_hyperparameter_tuning_job(
        self,
        request: job_service.CreateHyperparameterTuningJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.CreateHyperparameterTuningJobRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for create_hyperparameter_tuning_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_create_hyperparameter_tuning_job(
        self, response: gca_hyperparameter_tuning_job.HyperparameterTuningJob
    ) -> gca_hyperparameter_tuning_job.HyperparameterTuningJob:
        """Post-rpc interceptor for create_hyperparameter_tuning_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_create_model_deployment_monitoring_job(
        self,
        request: job_service.CreateModelDeploymentMonitoringJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.CreateModelDeploymentMonitoringJobRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for create_model_deployment_monitoring_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_create_model_deployment_monitoring_job(
        self, response: gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob
    ) -> gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob:
        """Post-rpc interceptor for create_model_deployment_monitoring_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_create_nas_job(
        self,
        request: job_service.CreateNasJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CreateNasJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for create_nas_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_create_nas_job(self, response: gca_nas_job.NasJob) -> gca_nas_job.NasJob:
        """Post-rpc interceptor for create_nas_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_delete_batch_prediction_job(
        self,
        request: job_service.DeleteBatchPredictionJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.DeleteBatchPredictionJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_batch_prediction_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_delete_batch_prediction_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_batch_prediction_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_delete_custom_job(
        self,
        request: job_service.DeleteCustomJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.DeleteCustomJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_custom_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_delete_custom_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_custom_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_delete_data_labeling_job(
        self,
        request: job_service.DeleteDataLabelingJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.DeleteDataLabelingJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_data_labeling_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_delete_data_labeling_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_data_labeling_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_delete_hyperparameter_tuning_job(
        self,
        request: job_service.DeleteHyperparameterTuningJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.DeleteHyperparameterTuningJobRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for delete_hyperparameter_tuning_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_delete_hyperparameter_tuning_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_hyperparameter_tuning_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_delete_model_deployment_monitoring_job(
        self,
        request: job_service.DeleteModelDeploymentMonitoringJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.DeleteModelDeploymentMonitoringJobRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for delete_model_deployment_monitoring_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_delete_model_deployment_monitoring_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_model_deployment_monitoring_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_delete_nas_job(
        self,
        request: job_service.DeleteNasJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.DeleteNasJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_nas_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_delete_nas_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_nas_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_get_batch_prediction_job(
        self,
        request: job_service.GetBatchPredictionJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.GetBatchPredictionJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_batch_prediction_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_get_batch_prediction_job(
        self, response: batch_prediction_job.BatchPredictionJob
    ) -> batch_prediction_job.BatchPredictionJob:
        """Post-rpc interceptor for get_batch_prediction_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_get_custom_job(
        self,
        request: job_service.GetCustomJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.GetCustomJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_custom_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_get_custom_job(
        self, response: custom_job.CustomJob
    ) -> custom_job.CustomJob:
        """Post-rpc interceptor for get_custom_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_get_data_labeling_job(
        self,
        request: job_service.GetDataLabelingJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.GetDataLabelingJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_data_labeling_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_get_data_labeling_job(
        self, response: data_labeling_job.DataLabelingJob
    ) -> data_labeling_job.DataLabelingJob:
        """Post-rpc interceptor for get_data_labeling_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_get_hyperparameter_tuning_job(
        self,
        request: job_service.GetHyperparameterTuningJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.GetHyperparameterTuningJobRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for get_hyperparameter_tuning_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_get_hyperparameter_tuning_job(
        self, response: hyperparameter_tuning_job.HyperparameterTuningJob
    ) -> hyperparameter_tuning_job.HyperparameterTuningJob:
        """Post-rpc interceptor for get_hyperparameter_tuning_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_get_model_deployment_monitoring_job(
        self,
        request: job_service.GetModelDeploymentMonitoringJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.GetModelDeploymentMonitoringJobRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for get_model_deployment_monitoring_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_get_model_deployment_monitoring_job(
        self, response: model_deployment_monitoring_job.ModelDeploymentMonitoringJob
    ) -> model_deployment_monitoring_job.ModelDeploymentMonitoringJob:
        """Post-rpc interceptor for get_model_deployment_monitoring_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_get_nas_job(
        self, request: job_service.GetNasJobRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[job_service.GetNasJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_nas_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_get_nas_job(self, response: nas_job.NasJob) -> nas_job.NasJob:
        """Post-rpc interceptor for get_nas_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_get_nas_trial_detail(
        self,
        request: job_service.GetNasTrialDetailRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.GetNasTrialDetailRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_nas_trial_detail

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_get_nas_trial_detail(
        self, response: nas_job.NasTrialDetail
    ) -> nas_job.NasTrialDetail:
        """Post-rpc interceptor for get_nas_trial_detail

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_list_batch_prediction_jobs(
        self,
        request: job_service.ListBatchPredictionJobsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.ListBatchPredictionJobsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_batch_prediction_jobs

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_list_batch_prediction_jobs(
        self, response: job_service.ListBatchPredictionJobsResponse
    ) -> job_service.ListBatchPredictionJobsResponse:
        """Post-rpc interceptor for list_batch_prediction_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_list_custom_jobs(
        self,
        request: job_service.ListCustomJobsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.ListCustomJobsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_custom_jobs

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_list_custom_jobs(
        self, response: job_service.ListCustomJobsResponse
    ) -> job_service.ListCustomJobsResponse:
        """Post-rpc interceptor for list_custom_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_list_data_labeling_jobs(
        self,
        request: job_service.ListDataLabelingJobsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.ListDataLabelingJobsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_data_labeling_jobs

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_list_data_labeling_jobs(
        self, response: job_service.ListDataLabelingJobsResponse
    ) -> job_service.ListDataLabelingJobsResponse:
        """Post-rpc interceptor for list_data_labeling_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_list_hyperparameter_tuning_jobs(
        self,
        request: job_service.ListHyperparameterTuningJobsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.ListHyperparameterTuningJobsRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for list_hyperparameter_tuning_jobs

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_list_hyperparameter_tuning_jobs(
        self, response: job_service.ListHyperparameterTuningJobsResponse
    ) -> job_service.ListHyperparameterTuningJobsResponse:
        """Post-rpc interceptor for list_hyperparameter_tuning_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_list_model_deployment_monitoring_jobs(
        self,
        request: job_service.ListModelDeploymentMonitoringJobsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.ListModelDeploymentMonitoringJobsRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for list_model_deployment_monitoring_jobs

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_list_model_deployment_monitoring_jobs(
        self, response: job_service.ListModelDeploymentMonitoringJobsResponse
    ) -> job_service.ListModelDeploymentMonitoringJobsResponse:
        """Post-rpc interceptor for list_model_deployment_monitoring_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_list_nas_jobs(
        self,
        request: job_service.ListNasJobsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.ListNasJobsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_nas_jobs

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_list_nas_jobs(
        self, response: job_service.ListNasJobsResponse
    ) -> job_service.ListNasJobsResponse:
        """Post-rpc interceptor for list_nas_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_list_nas_trial_details(
        self,
        request: job_service.ListNasTrialDetailsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.ListNasTrialDetailsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_nas_trial_details

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_list_nas_trial_details(
        self, response: job_service.ListNasTrialDetailsResponse
    ) -> job_service.ListNasTrialDetailsResponse:
        """Post-rpc interceptor for list_nas_trial_details

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_pause_model_deployment_monitoring_job(
        self,
        request: job_service.PauseModelDeploymentMonitoringJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.PauseModelDeploymentMonitoringJobRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for pause_model_deployment_monitoring_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def pre_resume_model_deployment_monitoring_job(
        self,
        request: job_service.ResumeModelDeploymentMonitoringJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.ResumeModelDeploymentMonitoringJobRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for resume_model_deployment_monitoring_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def pre_search_model_deployment_monitoring_stats_anomalies(
        self,
        request: job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest,
        Sequence[Tuple[str, str]],
    ]:
        """Pre-rpc interceptor for search_model_deployment_monitoring_stats_anomalies

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_search_model_deployment_monitoring_stats_anomalies(
        self,
        response: job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse,
    ) -> job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse:
        """Post-rpc interceptor for search_model_deployment_monitoring_stats_anomalies

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_update_model_deployment_monitoring_job(
        self,
        request: job_service.UpdateModelDeploymentMonitoringJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        job_service.UpdateModelDeploymentMonitoringJobRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for update_model_deployment_monitoring_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_update_model_deployment_monitoring_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for update_model_deployment_monitoring_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_get_location(
        self,
        request: locations_pb2.GetLocationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[locations_pb2.GetLocationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_location

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_get_location(
        self, response: locations_pb2.Location
    ) -> locations_pb2.Location:
        """Post-rpc interceptor for get_location

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_list_locations(
        self,
        request: locations_pb2.ListLocationsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[locations_pb2.ListLocationsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_locations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_list_locations(
        self, response: locations_pb2.ListLocationsResponse
    ) -> locations_pb2.ListLocationsResponse:
        """Post-rpc interceptor for list_locations

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_get_iam_policy(
        self,
        request: iam_policy_pb2.GetIamPolicyRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.GetIamPolicyRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_get_iam_policy(self, response: policy_pb2.Policy) -> policy_pb2.Policy:
        """Post-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_set_iam_policy(
        self,
        request: iam_policy_pb2.SetIamPolicyRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.SetIamPolicyRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_set_iam_policy(self, response: policy_pb2.Policy) -> policy_pb2.Policy:
        """Post-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_test_iam_permissions(
        self,
        request: iam_policy_pb2.TestIamPermissionsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.TestIamPermissionsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_test_iam_permissions(
        self, response: iam_policy_pb2.TestIamPermissionsResponse
    ) -> iam_policy_pb2.TestIamPermissionsResponse:
        """Post-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_cancel_operation(
        self,
        request: operations_pb2.CancelOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.CancelOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_cancel_operation(self, response: None) -> None:
        """Post-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_delete_operation(
        self,
        request: operations_pb2.DeleteOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.DeleteOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_delete_operation(self, response: None) -> None:
        """Post-rpc interceptor for delete_operation

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_get_operation(
        self,
        request: operations_pb2.GetOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.GetOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_get_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for get_operation

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_list_operations(
        self,
        request: operations_pb2.ListOperationsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.ListOperationsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_operations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_list_operations(
        self, response: operations_pb2.ListOperationsResponse
    ) -> operations_pb2.ListOperationsResponse:
        """Post-rpc interceptor for list_operations

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    def pre_wait_operation(
        self,
        request: operations_pb2.WaitOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.WaitOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for wait_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    def post_wait_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for wait_operation

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response


@dataclasses.dataclass
class JobServiceRestStub:
    _session: AuthorizedSession
    _host: str
    _interceptor: JobServiceRestInterceptor


class JobServiceRestTransport(JobServiceTransport):
    """REST backend transport for JobService.

    A service for creating and managing Vertex AI's jobs.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends JSON representations of protocol buffers over HTTP/1.1

    NOTE: This REST transport functionality is currently in a beta
    state (preview). We welcome your feedback via an issue in this
    library's source repository. Thank you!
    """

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: Optional[ga_credentials.Credentials] = None,
        credentials_file: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        client_cert_source_for_mtls: Optional[Callable[[], Tuple[bytes, bytes]]] = None,
        quota_project_id: Optional[str] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
        always_use_jwt_access: Optional[bool] = False,
        url_scheme: str = "https",
        interceptor: Optional[JobServiceRestInterceptor] = None,
        api_audience: Optional[str] = None,
    ) -> None:
        """Instantiate the transport.

        NOTE: This REST transport functionality is currently in a beta
        state (preview). We welcome your feedback via a GitHub issue in
        this library's repository. Thank you!

         Args:
             host (Optional[str]):
                  The hostname to connect to (default: 'aiplatform.googleapis.com').
             credentials (Optional[google.auth.credentials.Credentials]): The
                 authorization credentials to attach to requests. These
                 credentials identify the application to the service; if none
                 are specified, the client will attempt to ascertain the
                 credentials from the environment.

             credentials_file (Optional[str]): A file with credentials that can
                 be loaded with :func:`google.auth.load_credentials_from_file`.
                 This argument is ignored if ``channel`` is provided.
             scopes (Optional(Sequence[str])): A list of scopes. This argument is
                 ignored if ``channel`` is provided.
             client_cert_source_for_mtls (Callable[[], Tuple[bytes, bytes]]): Client
                 certificate to configure mutual TLS HTTP channel. It is ignored
                 if ``channel`` is provided.
             quota_project_id (Optional[str]): An optional project to use for billing
                 and quota.
             client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                 The client info used to send a user-agent string along with
                 API requests. If ``None``, then default info will be used.
                 Generally, you only need to set this if you are developing
                 your own client library.
             always_use_jwt_access (Optional[bool]): Whether self signed JWT should
                 be used for service account credentials.
             url_scheme: the protocol scheme for the API endpoint.  Normally
                 "https", but for testing or local servers,
                 "http" can be specified.
        """
        # Run the base constructor
        # TODO(yon-mg): resolve other ctor params i.e. scopes, quota, etc.
        # TODO: When custom host (api_endpoint) is set, `scopes` must *also* be set on the
        # credentials object
        maybe_url_match = re.match("^(?P<scheme>http(?:s)?://)?(?P<host>.*)$", host)
        if maybe_url_match is None:
            raise ValueError(
                f"Unexpected hostname structure: {host}"
            )  # pragma: NO COVER

        url_match_items = maybe_url_match.groupdict()

        host = f"{url_scheme}://{host}" if not url_match_items["scheme"] else host

        super().__init__(
            host=host,
            credentials=credentials,
            client_info=client_info,
            always_use_jwt_access=always_use_jwt_access,
            api_audience=api_audience,
        )
        self._session = AuthorizedSession(
            self._credentials, default_host=self.DEFAULT_HOST
        )
        self._operations_client: Optional[operations_v1.AbstractOperationsClient] = None
        if client_cert_source_for_mtls:
            self._session.configure_mtls_channel(client_cert_source_for_mtls)
        self._interceptor = interceptor or JobServiceRestInterceptor()
        self._prep_wrapped_messages(client_info)

    @property
    def operations_client(self) -> operations_v1.AbstractOperationsClient:
        """Create the client designed to process long-running operations.

        This property caches on the instance; repeated calls return the same
        client.
        """
        # Only create a new client if we do not already have one.
        if self._operations_client is None:
            http_options: Dict[str, List[Dict[str, str]]] = {
                "google.longrunning.Operations.CancelOperation": [
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tuningJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:cancel",
                    },
                ],
                "google.longrunning.Operations.DeleteOperation": [
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*}/operations",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/extensions/*}/operations",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                    },
                ],
                "google.longrunning.Operations.GetOperation": [
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDeploymentJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tuningJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                    },
                ],
                "google.longrunning.Operations.ListOperations": [
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/endpoints/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/extensions/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/customJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/indexes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/migratableResources/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/models/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/persistentResources/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/schedules/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/specialistPools/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/endpoints/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/customJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tuningJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/indexes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/migratableResources/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/models/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/persistentResources/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/schedules/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/specialistPools/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                    },
                ],
                "google.longrunning.Operations.WaitOperation": [
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                    },
                ],
            }

            rest_transport = operations_v1.OperationsRestTransport(
                host=self._host,
                # use the credentials which are saved
                credentials=self._credentials,
                scopes=self._scopes,
                http_options=http_options,
                path_prefix="v1",
            )

            self._operations_client = operations_v1.AbstractOperationsClient(
                transport=rest_transport
            )

        # Return the client from cache.
        return self._operations_client

    class _CancelBatchPredictionJob(JobServiceRestStub):
        def __hash__(self):
            return hash("CancelBatchPredictionJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.CancelBatchPredictionJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ):
            r"""Call the cancel batch prediction
            job method over HTTP.

                Args:
                    request (~.job_service.CancelBatchPredictionJobRequest):
                        The request object. Request message for
                    [JobService.CancelBatchPredictionJob][google.cloud.aiplatform.v1.JobService.CancelBatchPredictionJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/batchPredictionJobs/*}:cancel",
                    "body": "*",
                },
            ]
            request, metadata = self._interceptor.pre_cancel_batch_prediction_job(
                request, metadata
            )
            pb_request = job_service.CancelBatchPredictionJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

    class _CancelCustomJob(JobServiceRestStub):
        def __hash__(self):
            return hash("CancelCustomJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.CancelCustomJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ):
            r"""Call the cancel custom job method over HTTP.

            Args:
                request (~.job_service.CancelCustomJobRequest):
                    The request object. Request message for
                [JobService.CancelCustomJob][google.cloud.aiplatform.v1.JobService.CancelCustomJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/customJobs/*}:cancel",
                    "body": "*",
                },
            ]
            request, metadata = self._interceptor.pre_cancel_custom_job(
                request, metadata
            )
            pb_request = job_service.CancelCustomJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

    class _CancelDataLabelingJob(JobServiceRestStub):
        def __hash__(self):
            return hash("CancelDataLabelingJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.CancelDataLabelingJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ):
            r"""Call the cancel data labeling job method over HTTP.

            Args:
                request (~.job_service.CancelDataLabelingJobRequest):
                    The request object. Request message for
                [JobService.CancelDataLabelingJob][google.cloud.aiplatform.v1.JobService.CancelDataLabelingJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*}:cancel",
                    "body": "*",
                },
            ]
            request, metadata = self._interceptor.pre_cancel_data_labeling_job(
                request, metadata
            )
            pb_request = job_service.CancelDataLabelingJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

    class _CancelHyperparameterTuningJob(JobServiceRestStub):
        def __hash__(self):
            return hash("CancelHyperparameterTuningJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.CancelHyperparameterTuningJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ):
            r"""Call the cancel hyperparameter
            tuning job method over HTTP.

                Args:
                    request (~.job_service.CancelHyperparameterTuningJobRequest):
                        The request object. Request message for
                    [JobService.CancelHyperparameterTuningJob][google.cloud.aiplatform.v1.JobService.CancelHyperparameterTuningJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*}:cancel",
                    "body": "*",
                },
            ]
            request, metadata = self._interceptor.pre_cancel_hyperparameter_tuning_job(
                request, metadata
            )
            pb_request = job_service.CancelHyperparameterTuningJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

    class _CancelNasJob(JobServiceRestStub):
        def __hash__(self):
            return hash("CancelNasJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.CancelNasJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ):
            r"""Call the cancel nas job method over HTTP.

            Args:
                request (~.job_service.CancelNasJobRequest):
                    The request object. Request message for
                [JobService.CancelNasJob][google.cloud.aiplatform.v1.JobService.CancelNasJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/nasJobs/*}:cancel",
                    "body": "*",
                },
            ]
            request, metadata = self._interceptor.pre_cancel_nas_job(request, metadata)
            pb_request = job_service.CancelNasJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

    class _CreateBatchPredictionJob(JobServiceRestStub):
        def __hash__(self):
            return hash("CreateBatchPredictionJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.CreateBatchPredictionJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> gca_batch_prediction_job.BatchPredictionJob:
            r"""Call the create batch prediction
            job method over HTTP.

                Args:
                    request (~.job_service.CreateBatchPredictionJobRequest):
                        The request object. Request message for
                    [JobService.CreateBatchPredictionJob][google.cloud.aiplatform.v1.JobService.CreateBatchPredictionJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.gca_batch_prediction_job.BatchPredictionJob:
                        A job that uses a
                    [Model][google.cloud.aiplatform.v1.BatchPredictionJob.model]
                    to produce predictions on multiple [input
                    instances][google.cloud.aiplatform.v1.BatchPredictionJob.input_config].
                    If predictions for significant portion of the instances
                    fail, the job may finish without attempting predictions
                    for all remaining instances.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{parent=projects/*/locations/*}/batchPredictionJobs",
                    "body": "batch_prediction_job",
                },
            ]
            request, metadata = self._interceptor.pre_create_batch_prediction_job(
                request, metadata
            )
            pb_request = job_service.CreateBatchPredictionJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = gca_batch_prediction_job.BatchPredictionJob()
            pb_resp = gca_batch_prediction_job.BatchPredictionJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_create_batch_prediction_job(resp)
            return resp

    class _CreateCustomJob(JobServiceRestStub):
        def __hash__(self):
            return hash("CreateCustomJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.CreateCustomJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> gca_custom_job.CustomJob:
            r"""Call the create custom job method over HTTP.

            Args:
                request (~.job_service.CreateCustomJobRequest):
                    The request object. Request message for
                [JobService.CreateCustomJob][google.cloud.aiplatform.v1.JobService.CreateCustomJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.gca_custom_job.CustomJob:
                    Represents a job that runs custom
                workloads such as a Docker container or
                a Python package. A CustomJob can have
                multiple worker pools and each worker
                pool can have its own machine and input
                spec. A CustomJob will be cleaned up
                once the job enters terminal state
                (failed or succeeded).

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{parent=projects/*/locations/*}/customJobs",
                    "body": "custom_job",
                },
            ]
            request, metadata = self._interceptor.pre_create_custom_job(
                request, metadata
            )
            pb_request = job_service.CreateCustomJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = gca_custom_job.CustomJob()
            pb_resp = gca_custom_job.CustomJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_create_custom_job(resp)
            return resp

    class _CreateDataLabelingJob(JobServiceRestStub):
        def __hash__(self):
            return hash("CreateDataLabelingJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.CreateDataLabelingJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> gca_data_labeling_job.DataLabelingJob:
            r"""Call the create data labeling job method over HTTP.

            Args:
                request (~.job_service.CreateDataLabelingJobRequest):
                    The request object. Request message for
                [JobService.CreateDataLabelingJob][google.cloud.aiplatform.v1.JobService.CreateDataLabelingJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.gca_data_labeling_job.DataLabelingJob:
                    DataLabelingJob is used to trigger a
                human labeling job on unlabeled data
                from the following Dataset:

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{parent=projects/*/locations/*}/dataLabelingJobs",
                    "body": "data_labeling_job",
                },
            ]
            request, metadata = self._interceptor.pre_create_data_labeling_job(
                request, metadata
            )
            pb_request = job_service.CreateDataLabelingJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = gca_data_labeling_job.DataLabelingJob()
            pb_resp = gca_data_labeling_job.DataLabelingJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_create_data_labeling_job(resp)
            return resp

    class _CreateHyperparameterTuningJob(JobServiceRestStub):
        def __hash__(self):
            return hash("CreateHyperparameterTuningJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.CreateHyperparameterTuningJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> gca_hyperparameter_tuning_job.HyperparameterTuningJob:
            r"""Call the create hyperparameter
            tuning job method over HTTP.

                Args:
                    request (~.job_service.CreateHyperparameterTuningJobRequest):
                        The request object. Request message for
                    [JobService.CreateHyperparameterTuningJob][google.cloud.aiplatform.v1.JobService.CreateHyperparameterTuningJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.gca_hyperparameter_tuning_job.HyperparameterTuningJob:
                        Represents a HyperparameterTuningJob.
                    A HyperparameterTuningJob has a Study
                    specification and multiple CustomJobs
                    with identical CustomJob specification.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{parent=projects/*/locations/*}/hyperparameterTuningJobs",
                    "body": "hyperparameter_tuning_job",
                },
            ]
            request, metadata = self._interceptor.pre_create_hyperparameter_tuning_job(
                request, metadata
            )
            pb_request = job_service.CreateHyperparameterTuningJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = gca_hyperparameter_tuning_job.HyperparameterTuningJob()
            pb_resp = gca_hyperparameter_tuning_job.HyperparameterTuningJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_create_hyperparameter_tuning_job(resp)
            return resp

    class _CreateModelDeploymentMonitoringJob(JobServiceRestStub):
        def __hash__(self):
            return hash("CreateModelDeploymentMonitoringJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.CreateModelDeploymentMonitoringJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob:
            r"""Call the create model deployment
            monitoring job method over HTTP.

                Args:
                    request (~.job_service.CreateModelDeploymentMonitoringJobRequest):
                        The request object. Request message for
                    [JobService.CreateModelDeploymentMonitoringJob][google.cloud.aiplatform.v1.JobService.CreateModelDeploymentMonitoringJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob:
                        Represents a job that runs
                    periodically to monitor the deployed
                    models in an endpoint. It will analyze
                    the logged training & prediction data to
                    detect any abnormal behaviors.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{parent=projects/*/locations/*}/modelDeploymentMonitoringJobs",
                    "body": "model_deployment_monitoring_job",
                },
            ]
            (
                request,
                metadata,
            ) = self._interceptor.pre_create_model_deployment_monitoring_job(
                request, metadata
            )
            pb_request = job_service.CreateModelDeploymentMonitoringJobRequest.pb(
                request
            )
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
            pb_resp = (
                gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.pb(
                    resp
                )
            )

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_create_model_deployment_monitoring_job(resp)
            return resp

    class _CreateNasJob(JobServiceRestStub):
        def __hash__(self):
            return hash("CreateNasJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.CreateNasJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> gca_nas_job.NasJob:
            r"""Call the create nas job method over HTTP.

            Args:
                request (~.job_service.CreateNasJobRequest):
                    The request object. Request message for
                [JobService.CreateNasJob][google.cloud.aiplatform.v1.JobService.CreateNasJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.gca_nas_job.NasJob:
                    Represents a Neural Architecture
                Search (NAS) job.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{parent=projects/*/locations/*}/nasJobs",
                    "body": "nas_job",
                },
            ]
            request, metadata = self._interceptor.pre_create_nas_job(request, metadata)
            pb_request = job_service.CreateNasJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = gca_nas_job.NasJob()
            pb_resp = gca_nas_job.NasJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_create_nas_job(resp)
            return resp

    class _DeleteBatchPredictionJob(JobServiceRestStub):
        def __hash__(self):
            return hash("DeleteBatchPredictionJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.DeleteBatchPredictionJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the delete batch prediction
            job method over HTTP.

                Args:
                    request (~.job_service.DeleteBatchPredictionJobRequest):
                        The request object. Request message for
                    [JobService.DeleteBatchPredictionJob][google.cloud.aiplatform.v1.JobService.DeleteBatchPredictionJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.operations_pb2.Operation:
                        This resource represents a
                    long-running operation that is the
                    result of a network API call.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/batchPredictionJobs/*}",
                },
            ]
            request, metadata = self._interceptor.pre_delete_batch_prediction_job(
                request, metadata
            )
            pb_request = job_service.DeleteBatchPredictionJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = operations_pb2.Operation()
            json_format.Parse(response.content, resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_delete_batch_prediction_job(resp)
            return resp

    class _DeleteCustomJob(JobServiceRestStub):
        def __hash__(self):
            return hash("DeleteCustomJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.DeleteCustomJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the delete custom job method over HTTP.

            Args:
                request (~.job_service.DeleteCustomJobRequest):
                    The request object. Request message for
                [JobService.DeleteCustomJob][google.cloud.aiplatform.v1.JobService.DeleteCustomJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.operations_pb2.Operation:
                    This resource represents a
                long-running operation that is the
                result of a network API call.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/customJobs/*}",
                },
            ]
            request, metadata = self._interceptor.pre_delete_custom_job(
                request, metadata
            )
            pb_request = job_service.DeleteCustomJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = operations_pb2.Operation()
            json_format.Parse(response.content, resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_delete_custom_job(resp)
            return resp

    class _DeleteDataLabelingJob(JobServiceRestStub):
        def __hash__(self):
            return hash("DeleteDataLabelingJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.DeleteDataLabelingJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the delete data labeling job method over HTTP.

            Args:
                request (~.job_service.DeleteDataLabelingJobRequest):
                    The request object. Request message for
                [JobService.DeleteDataLabelingJob][google.cloud.aiplatform.v1.JobService.DeleteDataLabelingJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.operations_pb2.Operation:
                    This resource represents a
                long-running operation that is the
                result of a network API call.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*}",
                },
            ]
            request, metadata = self._interceptor.pre_delete_data_labeling_job(
                request, metadata
            )
            pb_request = job_service.DeleteDataLabelingJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = operations_pb2.Operation()
            json_format.Parse(response.content, resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_delete_data_labeling_job(resp)
            return resp

    class _DeleteHyperparameterTuningJob(JobServiceRestStub):
        def __hash__(self):
            return hash("DeleteHyperparameterTuningJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.DeleteHyperparameterTuningJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the delete hyperparameter
            tuning job method over HTTP.

                Args:
                    request (~.job_service.DeleteHyperparameterTuningJobRequest):
                        The request object. Request message for
                    [JobService.DeleteHyperparameterTuningJob][google.cloud.aiplatform.v1.JobService.DeleteHyperparameterTuningJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.operations_pb2.Operation:
                        This resource represents a
                    long-running operation that is the
                    result of a network API call.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*}",
                },
            ]
            request, metadata = self._interceptor.pre_delete_hyperparameter_tuning_job(
                request, metadata
            )
            pb_request = job_service.DeleteHyperparameterTuningJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = operations_pb2.Operation()
            json_format.Parse(response.content, resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_delete_hyperparameter_tuning_job(resp)
            return resp

    class _DeleteModelDeploymentMonitoringJob(JobServiceRestStub):
        def __hash__(self):
            return hash("DeleteModelDeploymentMonitoringJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.DeleteModelDeploymentMonitoringJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the delete model deployment
            monitoring job method over HTTP.

                Args:
                    request (~.job_service.DeleteModelDeploymentMonitoringJobRequest):
                        The request object. Request message for
                    [JobService.DeleteModelDeploymentMonitoringJob][google.cloud.aiplatform.v1.JobService.DeleteModelDeploymentMonitoringJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.operations_pb2.Operation:
                        This resource represents a
                    long-running operation that is the
                    result of a network API call.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}",
                },
            ]
            (
                request,
                metadata,
            ) = self._interceptor.pre_delete_model_deployment_monitoring_job(
                request, metadata
            )
            pb_request = job_service.DeleteModelDeploymentMonitoringJobRequest.pb(
                request
            )
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = operations_pb2.Operation()
            json_format.Parse(response.content, resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_delete_model_deployment_monitoring_job(resp)
            return resp

    class _DeleteNasJob(JobServiceRestStub):
        def __hash__(self):
            return hash("DeleteNasJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.DeleteNasJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the delete nas job method over HTTP.

            Args:
                request (~.job_service.DeleteNasJobRequest):
                    The request object. Request message for
                [JobService.DeleteNasJob][google.cloud.aiplatform.v1.JobService.DeleteNasJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.operations_pb2.Operation:
                    This resource represents a
                long-running operation that is the
                result of a network API call.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/nasJobs/*}",
                },
            ]
            request, metadata = self._interceptor.pre_delete_nas_job(request, metadata)
            pb_request = job_service.DeleteNasJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = operations_pb2.Operation()
            json_format.Parse(response.content, resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_delete_nas_job(resp)
            return resp

    class _GetBatchPredictionJob(JobServiceRestStub):
        def __hash__(self):
            return hash("GetBatchPredictionJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.GetBatchPredictionJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> batch_prediction_job.BatchPredictionJob:
            r"""Call the get batch prediction job method over HTTP.

            Args:
                request (~.job_service.GetBatchPredictionJobRequest):
                    The request object. Request message for
                [JobService.GetBatchPredictionJob][google.cloud.aiplatform.v1.JobService.GetBatchPredictionJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.batch_prediction_job.BatchPredictionJob:
                    A job that uses a
                [Model][google.cloud.aiplatform.v1.BatchPredictionJob.model]
                to produce predictions on multiple [input
                instances][google.cloud.aiplatform.v1.BatchPredictionJob.input_config].
                If predictions for significant portion of the instances
                fail, the job may finish without attempting predictions
                for all remaining instances.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/batchPredictionJobs/*}",
                },
            ]
            request, metadata = self._interceptor.pre_get_batch_prediction_job(
                request, metadata
            )
            pb_request = job_service.GetBatchPredictionJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = batch_prediction_job.BatchPredictionJob()
            pb_resp = batch_prediction_job.BatchPredictionJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_get_batch_prediction_job(resp)
            return resp

    class _GetCustomJob(JobServiceRestStub):
        def __hash__(self):
            return hash("GetCustomJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.GetCustomJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> custom_job.CustomJob:
            r"""Call the get custom job method over HTTP.

            Args:
                request (~.job_service.GetCustomJobRequest):
                    The request object. Request message for
                [JobService.GetCustomJob][google.cloud.aiplatform.v1.JobService.GetCustomJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.custom_job.CustomJob:
                    Represents a job that runs custom
                workloads such as a Docker container or
                a Python package. A CustomJob can have
                multiple worker pools and each worker
                pool can have its own machine and input
                spec. A CustomJob will be cleaned up
                once the job enters terminal state
                (failed or succeeded).

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/customJobs/*}",
                },
            ]
            request, metadata = self._interceptor.pre_get_custom_job(request, metadata)
            pb_request = job_service.GetCustomJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = custom_job.CustomJob()
            pb_resp = custom_job.CustomJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_get_custom_job(resp)
            return resp

    class _GetDataLabelingJob(JobServiceRestStub):
        def __hash__(self):
            return hash("GetDataLabelingJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.GetDataLabelingJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> data_labeling_job.DataLabelingJob:
            r"""Call the get data labeling job method over HTTP.

            Args:
                request (~.job_service.GetDataLabelingJobRequest):
                    The request object. Request message for
                [JobService.GetDataLabelingJob][google.cloud.aiplatform.v1.JobService.GetDataLabelingJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.data_labeling_job.DataLabelingJob:
                    DataLabelingJob is used to trigger a
                human labeling job on unlabeled data
                from the following Dataset:

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*}",
                },
            ]
            request, metadata = self._interceptor.pre_get_data_labeling_job(
                request, metadata
            )
            pb_request = job_service.GetDataLabelingJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = data_labeling_job.DataLabelingJob()
            pb_resp = data_labeling_job.DataLabelingJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_get_data_labeling_job(resp)
            return resp

    class _GetHyperparameterTuningJob(JobServiceRestStub):
        def __hash__(self):
            return hash("GetHyperparameterTuningJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.GetHyperparameterTuningJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> hyperparameter_tuning_job.HyperparameterTuningJob:
            r"""Call the get hyperparameter tuning
            job method over HTTP.

                Args:
                    request (~.job_service.GetHyperparameterTuningJobRequest):
                        The request object. Request message for
                    [JobService.GetHyperparameterTuningJob][google.cloud.aiplatform.v1.JobService.GetHyperparameterTuningJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.hyperparameter_tuning_job.HyperparameterTuningJob:
                        Represents a HyperparameterTuningJob.
                    A HyperparameterTuningJob has a Study
                    specification and multiple CustomJobs
                    with identical CustomJob specification.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*}",
                },
            ]
            request, metadata = self._interceptor.pre_get_hyperparameter_tuning_job(
                request, metadata
            )
            pb_request = job_service.GetHyperparameterTuningJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = hyperparameter_tuning_job.HyperparameterTuningJob()
            pb_resp = hyperparameter_tuning_job.HyperparameterTuningJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_get_hyperparameter_tuning_job(resp)
            return resp

    class _GetModelDeploymentMonitoringJob(JobServiceRestStub):
        def __hash__(self):
            return hash("GetModelDeploymentMonitoringJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.GetModelDeploymentMonitoringJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> model_deployment_monitoring_job.ModelDeploymentMonitoringJob:
            r"""Call the get model deployment
            monitoring job method over HTTP.

                Args:
                    request (~.job_service.GetModelDeploymentMonitoringJobRequest):
                        The request object. Request message for
                    [JobService.GetModelDeploymentMonitoringJob][google.cloud.aiplatform.v1.JobService.GetModelDeploymentMonitoringJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.model_deployment_monitoring_job.ModelDeploymentMonitoringJob:
                        Represents a job that runs
                    periodically to monitor the deployed
                    models in an endpoint. It will analyze
                    the logged training & prediction data to
                    detect any abnormal behaviors.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}",
                },
            ]
            (
                request,
                metadata,
            ) = self._interceptor.pre_get_model_deployment_monitoring_job(
                request, metadata
            )
            pb_request = job_service.GetModelDeploymentMonitoringJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
            pb_resp = model_deployment_monitoring_job.ModelDeploymentMonitoringJob.pb(
                resp
            )

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_get_model_deployment_monitoring_job(resp)
            return resp

    class _GetNasJob(JobServiceRestStub):
        def __hash__(self):
            return hash("GetNasJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.GetNasJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> nas_job.NasJob:
            r"""Call the get nas job method over HTTP.

            Args:
                request (~.job_service.GetNasJobRequest):
                    The request object. Request message for
                [JobService.GetNasJob][google.cloud.aiplatform.v1.JobService.GetNasJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.nas_job.NasJob:
                    Represents a Neural Architecture
                Search (NAS) job.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/nasJobs/*}",
                },
            ]
            request, metadata = self._interceptor.pre_get_nas_job(request, metadata)
            pb_request = job_service.GetNasJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = nas_job.NasJob()
            pb_resp = nas_job.NasJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_get_nas_job(resp)
            return resp

    class _GetNasTrialDetail(JobServiceRestStub):
        def __hash__(self):
            return hash("GetNasTrialDetail")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.GetNasTrialDetailRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> nas_job.NasTrialDetail:
            r"""Call the get nas trial detail method over HTTP.

            Args:
                request (~.job_service.GetNasTrialDetailRequest):
                    The request object. Request message for
                [JobService.GetNasTrialDetail][google.cloud.aiplatform.v1.JobService.GetNasTrialDetail].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.nas_job.NasTrialDetail:
                    Represents a NasTrial details along
                with its parameters. If there is a
                corresponding train NasTrial, the train
                NasTrial is also returned.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/nasJobs/*/nasTrialDetails/*}",
                },
            ]
            request, metadata = self._interceptor.pre_get_nas_trial_detail(
                request, metadata
            )
            pb_request = job_service.GetNasTrialDetailRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = nas_job.NasTrialDetail()
            pb_resp = nas_job.NasTrialDetail.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_get_nas_trial_detail(resp)
            return resp

    class _ListBatchPredictionJobs(JobServiceRestStub):
        def __hash__(self):
            return hash("ListBatchPredictionJobs")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.ListBatchPredictionJobsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> job_service.ListBatchPredictionJobsResponse:
            r"""Call the list batch prediction
            jobs method over HTTP.

                Args:
                    request (~.job_service.ListBatchPredictionJobsRequest):
                        The request object. Request message for
                    [JobService.ListBatchPredictionJobs][google.cloud.aiplatform.v1.JobService.ListBatchPredictionJobs].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.job_service.ListBatchPredictionJobsResponse:
                        Response message for
                    [JobService.ListBatchPredictionJobs][google.cloud.aiplatform.v1.JobService.ListBatchPredictionJobs]

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{parent=projects/*/locations/*}/batchPredictionJobs",
                },
            ]
            request, metadata = self._interceptor.pre_list_batch_prediction_jobs(
                request, metadata
            )
            pb_request = job_service.ListBatchPredictionJobsRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = job_service.ListBatchPredictionJobsResponse()
            pb_resp = job_service.ListBatchPredictionJobsResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_list_batch_prediction_jobs(resp)
            return resp

    class _ListCustomJobs(JobServiceRestStub):
        def __hash__(self):
            return hash("ListCustomJobs")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.ListCustomJobsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> job_service.ListCustomJobsResponse:
            r"""Call the list custom jobs method over HTTP.

            Args:
                request (~.job_service.ListCustomJobsRequest):
                    The request object. Request message for
                [JobService.ListCustomJobs][google.cloud.aiplatform.v1.JobService.ListCustomJobs].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.job_service.ListCustomJobsResponse:
                    Response message for
                [JobService.ListCustomJobs][google.cloud.aiplatform.v1.JobService.ListCustomJobs]

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{parent=projects/*/locations/*}/customJobs",
                },
            ]
            request, metadata = self._interceptor.pre_list_custom_jobs(
                request, metadata
            )
            pb_request = job_service.ListCustomJobsRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = job_service.ListCustomJobsResponse()
            pb_resp = job_service.ListCustomJobsResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_list_custom_jobs(resp)
            return resp

    class _ListDataLabelingJobs(JobServiceRestStub):
        def __hash__(self):
            return hash("ListDataLabelingJobs")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.ListDataLabelingJobsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> job_service.ListDataLabelingJobsResponse:
            r"""Call the list data labeling jobs method over HTTP.

            Args:
                request (~.job_service.ListDataLabelingJobsRequest):
                    The request object. Request message for
                [JobService.ListDataLabelingJobs][google.cloud.aiplatform.v1.JobService.ListDataLabelingJobs].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.job_service.ListDataLabelingJobsResponse:
                    Response message for
                [JobService.ListDataLabelingJobs][google.cloud.aiplatform.v1.JobService.ListDataLabelingJobs].

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{parent=projects/*/locations/*}/dataLabelingJobs",
                },
            ]
            request, metadata = self._interceptor.pre_list_data_labeling_jobs(
                request, metadata
            )
            pb_request = job_service.ListDataLabelingJobsRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = job_service.ListDataLabelingJobsResponse()
            pb_resp = job_service.ListDataLabelingJobsResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_list_data_labeling_jobs(resp)
            return resp

    class _ListHyperparameterTuningJobs(JobServiceRestStub):
        def __hash__(self):
            return hash("ListHyperparameterTuningJobs")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.ListHyperparameterTuningJobsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> job_service.ListHyperparameterTuningJobsResponse:
            r"""Call the list hyperparameter
            tuning jobs method over HTTP.

                Args:
                    request (~.job_service.ListHyperparameterTuningJobsRequest):
                        The request object. Request message for
                    [JobService.ListHyperparameterTuningJobs][google.cloud.aiplatform.v1.JobService.ListHyperparameterTuningJobs].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.job_service.ListHyperparameterTuningJobsResponse:
                        Response message for
                    [JobService.ListHyperparameterTuningJobs][google.cloud.aiplatform.v1.JobService.ListHyperparameterTuningJobs]

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{parent=projects/*/locations/*}/hyperparameterTuningJobs",
                },
            ]
            request, metadata = self._interceptor.pre_list_hyperparameter_tuning_jobs(
                request, metadata
            )
            pb_request = job_service.ListHyperparameterTuningJobsRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = job_service.ListHyperparameterTuningJobsResponse()
            pb_resp = job_service.ListHyperparameterTuningJobsResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_list_hyperparameter_tuning_jobs(resp)
            return resp

    class _ListModelDeploymentMonitoringJobs(JobServiceRestStub):
        def __hash__(self):
            return hash("ListModelDeploymentMonitoringJobs")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.ListModelDeploymentMonitoringJobsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> job_service.ListModelDeploymentMonitoringJobsResponse:
            r"""Call the list model deployment
            monitoring jobs method over HTTP.

                Args:
                    request (~.job_service.ListModelDeploymentMonitoringJobsRequest):
                        The request object. Request message for
                    [JobService.ListModelDeploymentMonitoringJobs][google.cloud.aiplatform.v1.JobService.ListModelDeploymentMonitoringJobs].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.job_service.ListModelDeploymentMonitoringJobsResponse:
                        Response message for
                    [JobService.ListModelDeploymentMonitoringJobs][google.cloud.aiplatform.v1.JobService.ListModelDeploymentMonitoringJobs].

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{parent=projects/*/locations/*}/modelDeploymentMonitoringJobs",
                },
            ]
            (
                request,
                metadata,
            ) = self._interceptor.pre_list_model_deployment_monitoring_jobs(
                request, metadata
            )
            pb_request = job_service.ListModelDeploymentMonitoringJobsRequest.pb(
                request
            )
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = job_service.ListModelDeploymentMonitoringJobsResponse()
            pb_resp = job_service.ListModelDeploymentMonitoringJobsResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_list_model_deployment_monitoring_jobs(resp)
            return resp

    class _ListNasJobs(JobServiceRestStub):
        def __hash__(self):
            return hash("ListNasJobs")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.ListNasJobsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> job_service.ListNasJobsResponse:
            r"""Call the list nas jobs method over HTTP.

            Args:
                request (~.job_service.ListNasJobsRequest):
                    The request object. Request message for
                [JobService.ListNasJobs][google.cloud.aiplatform.v1.JobService.ListNasJobs].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.job_service.ListNasJobsResponse:
                    Response message for
                [JobService.ListNasJobs][google.cloud.aiplatform.v1.JobService.ListNasJobs]

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{parent=projects/*/locations/*}/nasJobs",
                },
            ]
            request, metadata = self._interceptor.pre_list_nas_jobs(request, metadata)
            pb_request = job_service.ListNasJobsRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = job_service.ListNasJobsResponse()
            pb_resp = job_service.ListNasJobsResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_list_nas_jobs(resp)
            return resp

    class _ListNasTrialDetails(JobServiceRestStub):
        def __hash__(self):
            return hash("ListNasTrialDetails")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.ListNasTrialDetailsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> job_service.ListNasTrialDetailsResponse:
            r"""Call the list nas trial details method over HTTP.

            Args:
                request (~.job_service.ListNasTrialDetailsRequest):
                    The request object. Request message for
                [JobService.ListNasTrialDetails][google.cloud.aiplatform.v1.JobService.ListNasTrialDetails].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.job_service.ListNasTrialDetailsResponse:
                    Response message for
                [JobService.ListNasTrialDetails][google.cloud.aiplatform.v1.JobService.ListNasTrialDetails]

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1/{parent=projects/*/locations/*/nasJobs/*}/nasTrialDetails",
                },
            ]
            request, metadata = self._interceptor.pre_list_nas_trial_details(
                request, metadata
            )
            pb_request = job_service.ListNasTrialDetailsRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = job_service.ListNasTrialDetailsResponse()
            pb_resp = job_service.ListNasTrialDetailsResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_list_nas_trial_details(resp)
            return resp

    class _PauseModelDeploymentMonitoringJob(JobServiceRestStub):
        def __hash__(self):
            return hash("PauseModelDeploymentMonitoringJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.PauseModelDeploymentMonitoringJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ):
            r"""Call the pause model deployment
            monitoring job method over HTTP.

                Args:
                    request (~.job_service.PauseModelDeploymentMonitoringJobRequest):
                        The request object. Request message for
                    [JobService.PauseModelDeploymentMonitoringJob][google.cloud.aiplatform.v1.JobService.PauseModelDeploymentMonitoringJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}:pause",
                    "body": "*",
                },
            ]
            (
                request,
                metadata,
            ) = self._interceptor.pre_pause_model_deployment_monitoring_job(
                request, metadata
            )
            pb_request = job_service.PauseModelDeploymentMonitoringJobRequest.pb(
                request
            )
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

    class _ResumeModelDeploymentMonitoringJob(JobServiceRestStub):
        def __hash__(self):
            return hash("ResumeModelDeploymentMonitoringJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.ResumeModelDeploymentMonitoringJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ):
            r"""Call the resume model deployment
            monitoring job method over HTTP.

                Args:
                    request (~.job_service.ResumeModelDeploymentMonitoringJobRequest):
                        The request object. Request message for
                    [JobService.ResumeModelDeploymentMonitoringJob][google.cloud.aiplatform.v1.JobService.ResumeModelDeploymentMonitoringJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}:resume",
                    "body": "*",
                },
            ]
            (
                request,
                metadata,
            ) = self._interceptor.pre_resume_model_deployment_monitoring_job(
                request, metadata
            )
            pb_request = job_service.ResumeModelDeploymentMonitoringJobRequest.pb(
                request
            )
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

    class _SearchModelDeploymentMonitoringStatsAnomalies(JobServiceRestStub):
        def __hash__(self):
            return hash("SearchModelDeploymentMonitoringStatsAnomalies")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse:
            r"""Call the search model deployment
            monitoring stats anomalies method over HTTP.

                Args:
                    request (~.job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest):
                        The request object. Request message for
                    [JobService.SearchModelDeploymentMonitoringStatsAnomalies][google.cloud.aiplatform.v1.JobService.SearchModelDeploymentMonitoringStatsAnomalies].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse:
                        Response message for
                    [JobService.SearchModelDeploymentMonitoringStatsAnomalies][google.cloud.aiplatform.v1.JobService.SearchModelDeploymentMonitoringStatsAnomalies].

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{model_deployment_monitoring_job=projects/*/locations/*/modelDeploymentMonitoringJobs/*}:searchModelDeploymentMonitoringStatsAnomalies",
                    "body": "*",
                },
            ]
            (
                request,
                metadata,
            ) = self._interceptor.pre_search_model_deployment_monitoring_stats_anomalies(
                request, metadata
            )
            pb_request = (
                job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest.pb(
                    request
                )
            )
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse()
            pb_resp = (
                job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse.pb(
                    resp
                )
            )

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_search_model_deployment_monitoring_stats_anomalies(
                resp
            )
            return resp

    class _UpdateModelDeploymentMonitoringJob(JobServiceRestStub):
        def __hash__(self):
            return hash("UpdateModelDeploymentMonitoringJob")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {
            "updateMask": {},
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        def __call__(
            self,
            request: job_service.UpdateModelDeploymentMonitoringJobRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the update model deployment
            monitoring job method over HTTP.

                Args:
                    request (~.job_service.UpdateModelDeploymentMonitoringJobRequest):
                        The request object. Request message for
                    [JobService.UpdateModelDeploymentMonitoringJob][google.cloud.aiplatform.v1.JobService.UpdateModelDeploymentMonitoringJob].
                    retry (google.api_core.retry.Retry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.operations_pb2.Operation:
                        This resource represents a
                    long-running operation that is the
                    result of a network API call.

            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "patch",
                    "uri": "/v1/{model_deployment_monitoring_job.name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}",
                    "body": "model_deployment_monitoring_job",
                },
            ]
            (
                request,
                metadata,
            ) = self._interceptor.pre_update_model_deployment_monitoring_job(
                request, metadata
            )
            pb_request = job_service.UpdateModelDeploymentMonitoringJobRequest.pb(
                request
            )
            transcoded_request = path_template.transcode(http_options, pb_request)

            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=False
            )
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=False,
                )
            )
            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = operations_pb2.Operation()
            json_format.Parse(response.content, resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_update_model_deployment_monitoring_job(resp)
            return resp

    @property
    def cancel_batch_prediction_job(
        self,
    ) -> Callable[[job_service.CancelBatchPredictionJobRequest], empty_pb2.Empty]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CancelBatchPredictionJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def cancel_custom_job(
        self,
    ) -> Callable[[job_service.CancelCustomJobRequest], empty_pb2.Empty]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CancelCustomJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def cancel_data_labeling_job(
        self,
    ) -> Callable[[job_service.CancelDataLabelingJobRequest], empty_pb2.Empty]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CancelDataLabelingJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def cancel_hyperparameter_tuning_job(
        self,
    ) -> Callable[[job_service.CancelHyperparameterTuningJobRequest], empty_pb2.Empty]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CancelHyperparameterTuningJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def cancel_nas_job(
        self,
    ) -> Callable[[job_service.CancelNasJobRequest], empty_pb2.Empty]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CancelNasJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.CreateBatchPredictionJobRequest],
        gca_batch_prediction_job.BatchPredictionJob,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CreateBatchPredictionJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_custom_job(
        self,
    ) -> Callable[[job_service.CreateCustomJobRequest], gca_custom_job.CustomJob]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CreateCustomJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_data_labeling_job(
        self,
    ) -> Callable[
        [job_service.CreateDataLabelingJobRequest],
        gca_data_labeling_job.DataLabelingJob,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CreateDataLabelingJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.CreateHyperparameterTuningJobRequest],
        gca_hyperparameter_tuning_job.HyperparameterTuningJob,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CreateHyperparameterTuningJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.CreateModelDeploymentMonitoringJobRequest],
        gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CreateModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_nas_job(
        self,
    ) -> Callable[[job_service.CreateNasJobRequest], gca_nas_job.NasJob]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CreateNasJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.DeleteBatchPredictionJobRequest], operations_pb2.Operation
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._DeleteBatchPredictionJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_custom_job(
        self,
    ) -> Callable[[job_service.DeleteCustomJobRequest], operations_pb2.Operation]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._DeleteCustomJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_data_labeling_job(
        self,
    ) -> Callable[[job_service.DeleteDataLabelingJobRequest], operations_pb2.Operation]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._DeleteDataLabelingJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.DeleteHyperparameterTuningJobRequest], operations_pb2.Operation
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._DeleteHyperparameterTuningJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.DeleteModelDeploymentMonitoringJobRequest],
        operations_pb2.Operation,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._DeleteModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_nas_job(
        self,
    ) -> Callable[[job_service.DeleteNasJobRequest], operations_pb2.Operation]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._DeleteNasJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.GetBatchPredictionJobRequest],
        batch_prediction_job.BatchPredictionJob,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._GetBatchPredictionJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_custom_job(
        self,
    ) -> Callable[[job_service.GetCustomJobRequest], custom_job.CustomJob]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._GetCustomJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_data_labeling_job(
        self,
    ) -> Callable[
        [job_service.GetDataLabelingJobRequest], data_labeling_job.DataLabelingJob
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._GetDataLabelingJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.GetHyperparameterTuningJobRequest],
        hyperparameter_tuning_job.HyperparameterTuningJob,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._GetHyperparameterTuningJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.GetModelDeploymentMonitoringJobRequest],
        model_deployment_monitoring_job.ModelDeploymentMonitoringJob,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._GetModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_nas_job(self) -> Callable[[job_service.GetNasJobRequest], nas_job.NasJob]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._GetNasJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_nas_trial_detail(
        self,
    ) -> Callable[[job_service.GetNasTrialDetailRequest], nas_job.NasTrialDetail]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._GetNasTrialDetail(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_batch_prediction_jobs(
        self,
    ) -> Callable[
        [job_service.ListBatchPredictionJobsRequest],
        job_service.ListBatchPredictionJobsResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._ListBatchPredictionJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_custom_jobs(
        self,
    ) -> Callable[
        [job_service.ListCustomJobsRequest], job_service.ListCustomJobsResponse
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._ListCustomJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_data_labeling_jobs(
        self,
    ) -> Callable[
        [job_service.ListDataLabelingJobsRequest],
        job_service.ListDataLabelingJobsResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._ListDataLabelingJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_hyperparameter_tuning_jobs(
        self,
    ) -> Callable[
        [job_service.ListHyperparameterTuningJobsRequest],
        job_service.ListHyperparameterTuningJobsResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._ListHyperparameterTuningJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_model_deployment_monitoring_jobs(
        self,
    ) -> Callable[
        [job_service.ListModelDeploymentMonitoringJobsRequest],
        job_service.ListModelDeploymentMonitoringJobsResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._ListModelDeploymentMonitoringJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_nas_jobs(
        self,
    ) -> Callable[[job_service.ListNasJobsRequest], job_service.ListNasJobsResponse]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._ListNasJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_nas_trial_details(
        self,
    ) -> Callable[
        [job_service.ListNasTrialDetailsRequest],
        job_service.ListNasTrialDetailsResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._ListNasTrialDetails(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def pause_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.PauseModelDeploymentMonitoringJobRequest], empty_pb2.Empty
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._PauseModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def resume_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.ResumeModelDeploymentMonitoringJobRequest], empty_pb2.Empty
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._ResumeModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def search_model_deployment_monitoring_stats_anomalies(
        self,
    ) -> Callable[
        [job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest],
        job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._SearchModelDeploymentMonitoringStatsAnomalies(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def update_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.UpdateModelDeploymentMonitoringJobRequest],
        operations_pb2.Operation,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._UpdateModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_location(self):
        return self._GetLocation(self._session, self._host, self._interceptor)  # type: ignore

    class _GetLocation(JobServiceRestStub):
        def __call__(
            self,
            request: locations_pb2.GetLocationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> locations_pb2.Location:

            r"""Call the get location method over HTTP.

            Args:
                request (locations_pb2.GetLocationRequest):
                    The request object for GetLocation method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                locations_pb2.Location: Response from GetLocation method.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*}",
                },
            ]

            request, metadata = self._interceptor.pre_get_location(request, metadata)
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"

            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            resp = locations_pb2.Location()
            resp = json_format.Parse(response.content.decode("utf-8"), resp)
            resp = self._interceptor.post_get_location(resp)
            return resp

    @property
    def list_locations(self):
        return self._ListLocations(self._session, self._host, self._interceptor)  # type: ignore

    class _ListLocations(JobServiceRestStub):
        def __call__(
            self,
            request: locations_pb2.ListLocationsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> locations_pb2.ListLocationsResponse:

            r"""Call the list locations method over HTTP.

            Args:
                request (locations_pb2.ListLocationsRequest):
                    The request object for ListLocations method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                locations_pb2.ListLocationsResponse: Response from ListLocations method.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*}/locations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*}/locations",
                },
            ]

            request, metadata = self._interceptor.pre_list_locations(request, metadata)
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"

            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            resp = locations_pb2.ListLocationsResponse()
            resp = json_format.Parse(response.content.decode("utf-8"), resp)
            resp = self._interceptor.post_list_locations(resp)
            return resp

    @property
    def get_iam_policy(self):
        return self._GetIamPolicy(self._session, self._host, self._interceptor)  # type: ignore

    class _GetIamPolicy(JobServiceRestStub):
        def __call__(
            self,
            request: iam_policy_pb2.GetIamPolicyRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> policy_pb2.Policy:

            r"""Call the get iam policy method over HTTP.

            Args:
                request (iam_policy_pb2.GetIamPolicyRequest):
                    The request object for GetIamPolicy method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                policy_pb2.Policy: Response from GetIamPolicy method.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/featurestores/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/models/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/models/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/endpoints/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/publishers/*/models/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*/featureViews/*}:getIamPolicy",
                },
            ]

            request, metadata = self._interceptor.pre_get_iam_policy(request, metadata)
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"

            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            resp = policy_pb2.Policy()
            resp = json_format.Parse(response.content.decode("utf-8"), resp)
            resp = self._interceptor.post_get_iam_policy(resp)
            return resp

    @property
    def set_iam_policy(self):
        return self._SetIamPolicy(self._session, self._host, self._interceptor)  # type: ignore

    class _SetIamPolicy(JobServiceRestStub):
        def __call__(
            self,
            request: iam_policy_pb2.SetIamPolicyRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> policy_pb2.Policy:

            r"""Call the set iam policy method over HTTP.

            Args:
                request (iam_policy_pb2.SetIamPolicyRequest):
                    The request object for SetIamPolicy method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                policy_pb2.Policy: Response from SetIamPolicy method.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/featurestores/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/models/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/models/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/endpoints/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*/featureViews/*}:setIamPolicy",
                    "body": "*",
                },
            ]

            request, metadata = self._interceptor.pre_set_iam_policy(request, metadata)
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)

            body = json.dumps(transcoded_request["body"])
            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"

            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
                data=body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            resp = policy_pb2.Policy()
            resp = json_format.Parse(response.content.decode("utf-8"), resp)
            resp = self._interceptor.post_set_iam_policy(resp)
            return resp

    @property
    def test_iam_permissions(self):
        return self._TestIamPermissions(self._session, self._host, self._interceptor)  # type: ignore

    class _TestIamPermissions(JobServiceRestStub):
        def __call__(
            self,
            request: iam_policy_pb2.TestIamPermissionsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> iam_policy_pb2.TestIamPermissionsResponse:

            r"""Call the test iam permissions method over HTTP.

            Args:
                request (iam_policy_pb2.TestIamPermissionsRequest):
                    The request object for TestIamPermissions method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                iam_policy_pb2.TestIamPermissionsResponse: Response from TestIamPermissions method.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/featurestores/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/models/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/v1/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/models/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/endpoints/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*/featureViews/*}:testIamPermissions",
                },
            ]

            request, metadata = self._interceptor.pre_test_iam_permissions(
                request, metadata
            )
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"

            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            resp = iam_policy_pb2.TestIamPermissionsResponse()
            resp = json_format.Parse(response.content.decode("utf-8"), resp)
            resp = self._interceptor.post_test_iam_permissions(resp)
            return resp

    @property
    def cancel_operation(self):
        return self._CancelOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _CancelOperation(JobServiceRestStub):
        def __call__(
            self,
            request: operations_pb2.CancelOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> None:

            r"""Call the cancel operation method over HTTP.

            Args:
                request (operations_pb2.CancelOperationRequest):
                    The request object for CancelOperation method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/tuningJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:cancel",
                },
            ]

            request, metadata = self._interceptor.pre_cancel_operation(
                request, metadata
            )
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"

            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            return self._interceptor.post_cancel_operation(None)

    @property
    def delete_operation(self):
        return self._DeleteOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _DeleteOperation(JobServiceRestStub):
        def __call__(
            self,
            request: operations_pb2.DeleteOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> None:

            r"""Call the delete operation method over HTTP.

            Args:
                request (operations_pb2.DeleteOperationRequest):
                    The request object for DeleteOperation method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*}/operations",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/extensions/*}/operations",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                },
            ]

            request, metadata = self._interceptor.pre_delete_operation(
                request, metadata
            )
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"

            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            return self._interceptor.post_delete_operation(None)

    @property
    def get_operation(self):
        return self._GetOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _GetOperation(JobServiceRestStub):
        def __call__(
            self,
            request: operations_pb2.GetOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.Operation:

            r"""Call the get operation method over HTTP.

            Args:
                request (operations_pb2.GetOperationRequest):
                    The request object for GetOperation method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.Operation: Response from GetOperation method.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDeploymentJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/tuningJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                },
            ]

            request, metadata = self._interceptor.pre_get_operation(request, metadata)
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"

            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            resp = operations_pb2.Operation()
            resp = json_format.Parse(response.content.decode("utf-8"), resp)
            resp = self._interceptor.post_get_operation(resp)
            return resp

    @property
    def list_operations(self):
        return self._ListOperations(self._session, self._host, self._interceptor)  # type: ignore

    class _ListOperations(JobServiceRestStub):
        def __call__(
            self,
            request: operations_pb2.ListOperationsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.ListOperationsResponse:

            r"""Call the list operations method over HTTP.

            Args:
                request (operations_pb2.ListOperationsRequest):
                    The request object for ListOperations method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.ListOperationsResponse: Response from ListOperations method.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/endpoints/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/extensions/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/customJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/indexes/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/migratableResources/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/models/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/persistentResources/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/schedules/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/specialistPools/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/endpoints/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/customJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/tuningJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/indexes/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/migratableResources/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/models/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/studies/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/persistentResources/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/schedules/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/specialistPools/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                },
            ]

            request, metadata = self._interceptor.pre_list_operations(request, metadata)
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"

            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            resp = operations_pb2.ListOperationsResponse()
            resp = json_format.Parse(response.content.decode("utf-8"), resp)
            resp = self._interceptor.post_list_operations(resp)
            return resp

    @property
    def wait_operation(self):
        return self._WaitOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _WaitOperation(JobServiceRestStub):
        def __call__(
            self,
            request: operations_pb2.WaitOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.Operation:

            r"""Call the wait operation method over HTTP.

            Args:
                request (operations_pb2.WaitOperationRequest):
                    The request object for WaitOperation method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.Operation: Response from WaitOperation method.
            """

            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                },
            ]

            request, metadata = self._interceptor.pre_wait_operation(request, metadata)
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]

            # Jsonify the query params
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))

            # Send the request
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"

            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            resp = operations_pb2.Operation()
            resp = json_format.Parse(response.content.decode("utf-8"), resp)
            resp = self._interceptor.post_wait_operation(resp)
            return resp

    @property
    def kind(self) -> str:
        return "rest"

    def close(self):
        self._session.close()


__all__ = ("JobServiceRestTransport",)
