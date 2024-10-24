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

import google.auth

try:
    import aiohttp  # type: ignore
    from google.auth.aio.transport.sessions import AsyncAuthorizedSession  # type: ignore
    from google.api_core import rest_streaming_async  # type: ignore
    from google.api_core.operations_v1 import AsyncOperationsRestClient  # type: ignore
except ImportError as e:  # pragma: NO COVER
    raise ImportError(
        "`rest_asyncio` transport requires the library to be installed with the `async_rest` extra. Install the library with the `async_rest` extra using `pip install google-cloud-aiplatform[async_rest]`"
    ) from e

from google.auth.aio import credentials as ga_credentials_async  # type: ignore

from google.api_core import exceptions as core_exceptions
from google.api_core import gapic_v1
from google.api_core import operations_v1
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.cloud.location import locations_pb2  # type: ignore
from google.api_core import retry_async as retries
from google.api_core import rest_helpers
from google.api_core import rest_streaming_async  # type: ignore


from google.protobuf import json_format
from google.api_core import operations_v1
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.cloud.location import locations_pb2  # type: ignore

import json  # type: ignore
import dataclasses
from typing import Any, Dict, List, Callable, Tuple, Optional, Sequence, Union


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


from .rest_base import _BaseJobServiceRestTransport

from .base import DEFAULT_CLIENT_INFO as BASE_DEFAULT_CLIENT_INFO

try:
    OptionalRetry = Union[retries.AsyncRetry, gapic_v1.method._MethodDefault, None]
except AttributeError:  # pragma: NO COVER
    OptionalRetry = Union[retries.AsyncRetry, object, None]  # type: ignore

DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
    gapic_version=BASE_DEFAULT_CLIENT_INFO.gapic_version,
    grpc_version=None,
    rest_version=f"google-auth@{google.auth.__version__}",
)


class AsyncJobServiceRestInterceptor:
    """Asynchronous Interceptor for JobService.

    Interceptors are used to manipulate requests, request metadata, and responses
    in arbitrary ways.
    Example use cases include:
    * Logging
    * Verifying requests according to service or custom semantics
    * Stripping extraneous information from responses

    These use cases and more can be enabled by injecting an
    instance of a custom subclass when constructing the AsyncJobServiceRestTransport.

    .. code-block:: python
        class MyCustomJobServiceInterceptor(JobServiceRestInterceptor):
            async def pre_cancel_batch_prediction_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def pre_cancel_custom_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def pre_cancel_data_labeling_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def pre_cancel_hyperparameter_tuning_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def pre_cancel_nas_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def pre_create_batch_prediction_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_create_batch_prediction_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_create_custom_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_create_custom_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_create_data_labeling_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_create_data_labeling_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_create_hyperparameter_tuning_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_create_hyperparameter_tuning_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_create_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_create_model_deployment_monitoring_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_create_nas_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_create_nas_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_delete_batch_prediction_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_delete_batch_prediction_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_delete_custom_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_delete_custom_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_delete_data_labeling_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_delete_data_labeling_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_delete_hyperparameter_tuning_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_delete_hyperparameter_tuning_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_delete_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_delete_model_deployment_monitoring_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_delete_nas_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_delete_nas_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_get_batch_prediction_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_batch_prediction_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_get_custom_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_custom_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_get_data_labeling_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_data_labeling_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_get_hyperparameter_tuning_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_hyperparameter_tuning_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_get_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_model_deployment_monitoring_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_get_nas_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_nas_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_get_nas_trial_detail(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_nas_trial_detail(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_batch_prediction_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_batch_prediction_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_custom_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_custom_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_data_labeling_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_data_labeling_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_hyperparameter_tuning_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_hyperparameter_tuning_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_model_deployment_monitoring_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_model_deployment_monitoring_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_nas_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_nas_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_nas_trial_details(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_nas_trial_details(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_pause_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def pre_resume_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def pre_search_model_deployment_monitoring_stats_anomalies(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_search_model_deployment_monitoring_stats_anomalies(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_update_model_deployment_monitoring_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_update_model_deployment_monitoring_job(self, response):
                logging.log(f"Received response: {response}")
                return response

        transport = AsyncJobServiceRestTransport(interceptor=MyCustomJobServiceInterceptor())
        client = async JobServiceClient(transport=transport)


    """

    async def pre_cancel_batch_prediction_job(
        self,
        request: job_service.CancelBatchPredictionJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CancelBatchPredictionJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_batch_prediction_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def pre_cancel_custom_job(
        self,
        request: job_service.CancelCustomJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CancelCustomJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_custom_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def pre_cancel_data_labeling_job(
        self,
        request: job_service.CancelDataLabelingJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CancelDataLabelingJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_data_labeling_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def pre_cancel_hyperparameter_tuning_job(
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

    async def pre_cancel_nas_job(
        self,
        request: job_service.CancelNasJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CancelNasJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_nas_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def pre_create_batch_prediction_job(
        self,
        request: job_service.CreateBatchPredictionJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CreateBatchPredictionJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for create_batch_prediction_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_create_batch_prediction_job(
        self, response: gca_batch_prediction_job.BatchPredictionJob
    ) -> gca_batch_prediction_job.BatchPredictionJob:
        """Post-rpc interceptor for create_batch_prediction_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_create_custom_job(
        self,
        request: job_service.CreateCustomJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CreateCustomJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for create_custom_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_create_custom_job(
        self, response: gca_custom_job.CustomJob
    ) -> gca_custom_job.CustomJob:
        """Post-rpc interceptor for create_custom_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_create_data_labeling_job(
        self,
        request: job_service.CreateDataLabelingJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CreateDataLabelingJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for create_data_labeling_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_create_data_labeling_job(
        self, response: gca_data_labeling_job.DataLabelingJob
    ) -> gca_data_labeling_job.DataLabelingJob:
        """Post-rpc interceptor for create_data_labeling_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_create_hyperparameter_tuning_job(
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

    async def post_create_hyperparameter_tuning_job(
        self, response: gca_hyperparameter_tuning_job.HyperparameterTuningJob
    ) -> gca_hyperparameter_tuning_job.HyperparameterTuningJob:
        """Post-rpc interceptor for create_hyperparameter_tuning_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_create_model_deployment_monitoring_job(
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

    async def post_create_model_deployment_monitoring_job(
        self, response: gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob
    ) -> gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob:
        """Post-rpc interceptor for create_model_deployment_monitoring_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_create_nas_job(
        self,
        request: job_service.CreateNasJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.CreateNasJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for create_nas_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_create_nas_job(
        self, response: gca_nas_job.NasJob
    ) -> gca_nas_job.NasJob:
        """Post-rpc interceptor for create_nas_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_delete_batch_prediction_job(
        self,
        request: job_service.DeleteBatchPredictionJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.DeleteBatchPredictionJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_batch_prediction_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_delete_batch_prediction_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_batch_prediction_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_delete_custom_job(
        self,
        request: job_service.DeleteCustomJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.DeleteCustomJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_custom_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_delete_custom_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_custom_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_delete_data_labeling_job(
        self,
        request: job_service.DeleteDataLabelingJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.DeleteDataLabelingJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_data_labeling_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_delete_data_labeling_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_data_labeling_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_delete_hyperparameter_tuning_job(
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

    async def post_delete_hyperparameter_tuning_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_hyperparameter_tuning_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_delete_model_deployment_monitoring_job(
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

    async def post_delete_model_deployment_monitoring_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_model_deployment_monitoring_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_delete_nas_job(
        self,
        request: job_service.DeleteNasJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.DeleteNasJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_nas_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_delete_nas_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_nas_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_batch_prediction_job(
        self,
        request: job_service.GetBatchPredictionJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.GetBatchPredictionJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_batch_prediction_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_get_batch_prediction_job(
        self, response: batch_prediction_job.BatchPredictionJob
    ) -> batch_prediction_job.BatchPredictionJob:
        """Post-rpc interceptor for get_batch_prediction_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_custom_job(
        self,
        request: job_service.GetCustomJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.GetCustomJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_custom_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_get_custom_job(
        self, response: custom_job.CustomJob
    ) -> custom_job.CustomJob:
        """Post-rpc interceptor for get_custom_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_data_labeling_job(
        self,
        request: job_service.GetDataLabelingJobRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.GetDataLabelingJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_data_labeling_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_get_data_labeling_job(
        self, response: data_labeling_job.DataLabelingJob
    ) -> data_labeling_job.DataLabelingJob:
        """Post-rpc interceptor for get_data_labeling_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_hyperparameter_tuning_job(
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

    async def post_get_hyperparameter_tuning_job(
        self, response: hyperparameter_tuning_job.HyperparameterTuningJob
    ) -> hyperparameter_tuning_job.HyperparameterTuningJob:
        """Post-rpc interceptor for get_hyperparameter_tuning_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_model_deployment_monitoring_job(
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

    async def post_get_model_deployment_monitoring_job(
        self, response: model_deployment_monitoring_job.ModelDeploymentMonitoringJob
    ) -> model_deployment_monitoring_job.ModelDeploymentMonitoringJob:
        """Post-rpc interceptor for get_model_deployment_monitoring_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_nas_job(
        self, request: job_service.GetNasJobRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[job_service.GetNasJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_nas_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_get_nas_job(self, response: nas_job.NasJob) -> nas_job.NasJob:
        """Post-rpc interceptor for get_nas_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_nas_trial_detail(
        self,
        request: job_service.GetNasTrialDetailRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.GetNasTrialDetailRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_nas_trial_detail

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_get_nas_trial_detail(
        self, response: nas_job.NasTrialDetail
    ) -> nas_job.NasTrialDetail:
        """Post-rpc interceptor for get_nas_trial_detail

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_batch_prediction_jobs(
        self,
        request: job_service.ListBatchPredictionJobsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.ListBatchPredictionJobsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_batch_prediction_jobs

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_list_batch_prediction_jobs(
        self, response: job_service.ListBatchPredictionJobsResponse
    ) -> job_service.ListBatchPredictionJobsResponse:
        """Post-rpc interceptor for list_batch_prediction_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_custom_jobs(
        self,
        request: job_service.ListCustomJobsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.ListCustomJobsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_custom_jobs

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_list_custom_jobs(
        self, response: job_service.ListCustomJobsResponse
    ) -> job_service.ListCustomJobsResponse:
        """Post-rpc interceptor for list_custom_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_data_labeling_jobs(
        self,
        request: job_service.ListDataLabelingJobsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.ListDataLabelingJobsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_data_labeling_jobs

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_list_data_labeling_jobs(
        self, response: job_service.ListDataLabelingJobsResponse
    ) -> job_service.ListDataLabelingJobsResponse:
        """Post-rpc interceptor for list_data_labeling_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_hyperparameter_tuning_jobs(
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

    async def post_list_hyperparameter_tuning_jobs(
        self, response: job_service.ListHyperparameterTuningJobsResponse
    ) -> job_service.ListHyperparameterTuningJobsResponse:
        """Post-rpc interceptor for list_hyperparameter_tuning_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_model_deployment_monitoring_jobs(
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

    async def post_list_model_deployment_monitoring_jobs(
        self, response: job_service.ListModelDeploymentMonitoringJobsResponse
    ) -> job_service.ListModelDeploymentMonitoringJobsResponse:
        """Post-rpc interceptor for list_model_deployment_monitoring_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_nas_jobs(
        self,
        request: job_service.ListNasJobsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.ListNasJobsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_nas_jobs

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_list_nas_jobs(
        self, response: job_service.ListNasJobsResponse
    ) -> job_service.ListNasJobsResponse:
        """Post-rpc interceptor for list_nas_jobs

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_nas_trial_details(
        self,
        request: job_service.ListNasTrialDetailsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[job_service.ListNasTrialDetailsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_nas_trial_details

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_list_nas_trial_details(
        self, response: job_service.ListNasTrialDetailsResponse
    ) -> job_service.ListNasTrialDetailsResponse:
        """Post-rpc interceptor for list_nas_trial_details

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_pause_model_deployment_monitoring_job(
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

    async def pre_resume_model_deployment_monitoring_job(
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

    async def pre_search_model_deployment_monitoring_stats_anomalies(
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

    async def post_search_model_deployment_monitoring_stats_anomalies(
        self,
        response: job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse,
    ) -> job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse:
        """Post-rpc interceptor for search_model_deployment_monitoring_stats_anomalies

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_update_model_deployment_monitoring_job(
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

    async def post_update_model_deployment_monitoring_job(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for update_model_deployment_monitoring_job

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_location(
        self,
        request: locations_pb2.GetLocationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[locations_pb2.GetLocationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_location

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_get_location(
        self, response: locations_pb2.Location
    ) -> locations_pb2.Location:
        """Post-rpc interceptor for get_location

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_locations(
        self,
        request: locations_pb2.ListLocationsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[locations_pb2.ListLocationsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_locations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_list_locations(
        self, response: locations_pb2.ListLocationsResponse
    ) -> locations_pb2.ListLocationsResponse:
        """Post-rpc interceptor for list_locations

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_iam_policy(
        self,
        request: iam_policy_pb2.GetIamPolicyRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.GetIamPolicyRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_get_iam_policy(
        self, response: policy_pb2.Policy
    ) -> policy_pb2.Policy:
        """Post-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_set_iam_policy(
        self,
        request: iam_policy_pb2.SetIamPolicyRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.SetIamPolicyRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_set_iam_policy(
        self, response: policy_pb2.Policy
    ) -> policy_pb2.Policy:
        """Post-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_test_iam_permissions(
        self,
        request: iam_policy_pb2.TestIamPermissionsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.TestIamPermissionsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_test_iam_permissions(
        self, response: iam_policy_pb2.TestIamPermissionsResponse
    ) -> iam_policy_pb2.TestIamPermissionsResponse:
        """Post-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_cancel_operation(
        self,
        request: operations_pb2.CancelOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.CancelOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_cancel_operation(self, response: None) -> None:
        """Post-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_delete_operation(
        self,
        request: operations_pb2.DeleteOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.DeleteOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_delete_operation(self, response: None) -> None:
        """Post-rpc interceptor for delete_operation

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_operation(
        self,
        request: operations_pb2.GetOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.GetOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_get_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for get_operation

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_operations(
        self,
        request: operations_pb2.ListOperationsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.ListOperationsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_operations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_list_operations(
        self, response: operations_pb2.ListOperationsResponse
    ) -> operations_pb2.ListOperationsResponse:
        """Post-rpc interceptor for list_operations

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response

    async def pre_wait_operation(
        self,
        request: operations_pb2.WaitOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.WaitOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for wait_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the JobService server.
        """
        return request, metadata

    async def post_wait_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for wait_operation

        Override in a subclass to manipulate the response
        after it is returned by the JobService server but before
        it is returned to user code.
        """
        return response


@dataclasses.dataclass
class AsyncJobServiceRestStub:
    _session: AsyncAuthorizedSession
    _host: str
    _interceptor: AsyncJobServiceRestInterceptor


class AsyncJobServiceRestTransport(_BaseJobServiceRestTransport):
    """Asynchronous REST backend transport for JobService.

    A service for creating and managing Vertex AI's jobs.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends JSON representations of protocol buffers over HTTP/1.1
    """

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: Optional[ga_credentials_async.Credentials] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
        url_scheme: str = "https",
        interceptor: Optional[AsyncJobServiceRestInterceptor] = None,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]):
                 The hostname to connect to (default: 'aiplatform.googleapis.com').
            credentials (Optional[google.auth.aio.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you are developing
                your own client library.
            url_scheme (str): the protocol scheme for the API endpoint.  Normally
                "https", but for testing or local servers,
                "http" can be specified.
        """
        # Run the base constructor
        super().__init__(
            host=host,
            credentials=credentials,
            client_info=client_info,
            always_use_jwt_access=False,
            url_scheme=url_scheme,
            api_audience=None,
        )
        self._session = AsyncAuthorizedSession(self._credentials)  # type: ignore
        self._interceptor = interceptor or AsyncJobServiceRestInterceptor()
        self._wrap_with_kind = True
        self._prep_wrapped_messages(client_info)
        self._operations_client: Optional[
            operations_v1.AsyncOperationsRestClient
        ] = None

    def _prep_wrapped_messages(self, client_info):
        """Precompute the wrapped methods, overriding the base class method to use async wrappers."""
        self._wrapped_methods = {
            self.create_custom_job: self._wrap_method(
                self.create_custom_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_custom_job: self._wrap_method(
                self.get_custom_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_custom_jobs: self._wrap_method(
                self.list_custom_jobs,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_custom_job: self._wrap_method(
                self.delete_custom_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.cancel_custom_job: self._wrap_method(
                self.cancel_custom_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_data_labeling_job: self._wrap_method(
                self.create_data_labeling_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_data_labeling_job: self._wrap_method(
                self.get_data_labeling_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_data_labeling_jobs: self._wrap_method(
                self.list_data_labeling_jobs,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_data_labeling_job: self._wrap_method(
                self.delete_data_labeling_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.cancel_data_labeling_job: self._wrap_method(
                self.cancel_data_labeling_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_hyperparameter_tuning_job: self._wrap_method(
                self.create_hyperparameter_tuning_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_hyperparameter_tuning_job: self._wrap_method(
                self.get_hyperparameter_tuning_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_hyperparameter_tuning_jobs: self._wrap_method(
                self.list_hyperparameter_tuning_jobs,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_hyperparameter_tuning_job: self._wrap_method(
                self.delete_hyperparameter_tuning_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.cancel_hyperparameter_tuning_job: self._wrap_method(
                self.cancel_hyperparameter_tuning_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_nas_job: self._wrap_method(
                self.create_nas_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_nas_job: self._wrap_method(
                self.get_nas_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_nas_jobs: self._wrap_method(
                self.list_nas_jobs,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_nas_job: self._wrap_method(
                self.delete_nas_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.cancel_nas_job: self._wrap_method(
                self.cancel_nas_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_nas_trial_detail: self._wrap_method(
                self.get_nas_trial_detail,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_nas_trial_details: self._wrap_method(
                self.list_nas_trial_details,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_batch_prediction_job: self._wrap_method(
                self.create_batch_prediction_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_batch_prediction_job: self._wrap_method(
                self.get_batch_prediction_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_batch_prediction_jobs: self._wrap_method(
                self.list_batch_prediction_jobs,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_batch_prediction_job: self._wrap_method(
                self.delete_batch_prediction_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.cancel_batch_prediction_job: self._wrap_method(
                self.cancel_batch_prediction_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_model_deployment_monitoring_job: self._wrap_method(
                self.create_model_deployment_monitoring_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.search_model_deployment_monitoring_stats_anomalies: self._wrap_method(
                self.search_model_deployment_monitoring_stats_anomalies,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_model_deployment_monitoring_job: self._wrap_method(
                self.get_model_deployment_monitoring_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_model_deployment_monitoring_jobs: self._wrap_method(
                self.list_model_deployment_monitoring_jobs,
                default_timeout=None,
                client_info=client_info,
            ),
            self.update_model_deployment_monitoring_job: self._wrap_method(
                self.update_model_deployment_monitoring_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_model_deployment_monitoring_job: self._wrap_method(
                self.delete_model_deployment_monitoring_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.pause_model_deployment_monitoring_job: self._wrap_method(
                self.pause_model_deployment_monitoring_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.resume_model_deployment_monitoring_job: self._wrap_method(
                self.resume_model_deployment_monitoring_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_location: self._wrap_method(
                self.get_location,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_locations: self._wrap_method(
                self.list_locations,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_iam_policy: self._wrap_method(
                self.get_iam_policy,
                default_timeout=None,
                client_info=client_info,
            ),
            self.set_iam_policy: self._wrap_method(
                self.set_iam_policy,
                default_timeout=None,
                client_info=client_info,
            ),
            self.test_iam_permissions: self._wrap_method(
                self.test_iam_permissions,
                default_timeout=None,
                client_info=client_info,
            ),
            self.cancel_operation: self._wrap_method(
                self.cancel_operation,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_operation: self._wrap_method(
                self.delete_operation,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_operation: self._wrap_method(
                self.get_operation,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_operations: self._wrap_method(
                self.list_operations,
                default_timeout=None,
                client_info=client_info,
            ),
            self.wait_operation: self._wrap_method(
                self.wait_operation,
                default_timeout=None,
                client_info=client_info,
            ),
        }

    def _wrap_method(self, func, *args, **kwargs):
        if self._wrap_with_kind:  # pragma: NO COVER
            kwargs["kind"] = self.kind
        return gapic_v1.method_async.wrap_method(func, *args, **kwargs)

    class _CancelBatchPredictionJob(
        _BaseJobServiceRestTransport._BaseCancelBatchPredictionJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.CancelBatchPredictionJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseCancelBatchPredictionJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_cancel_batch_prediction_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseCancelBatchPredictionJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseCancelBatchPredictionJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseCancelBatchPredictionJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._CancelBatchPredictionJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

    class _CancelCustomJob(
        _BaseJobServiceRestTransport._BaseCancelCustomJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.CancelCustomJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseCancelCustomJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_cancel_custom_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseCancelCustomJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseCancelCustomJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseCancelCustomJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._CancelCustomJob._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                    body,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

    class _CancelDataLabelingJob(
        _BaseJobServiceRestTransport._BaseCancelDataLabelingJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.CancelDataLabelingJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseCancelDataLabelingJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_cancel_data_labeling_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseCancelDataLabelingJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseCancelDataLabelingJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseCancelDataLabelingJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._CancelDataLabelingJob._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                    body,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

    class _CancelHyperparameterTuningJob(
        _BaseJobServiceRestTransport._BaseCancelHyperparameterTuningJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.CancelHyperparameterTuningJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseCancelHyperparameterTuningJob._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_cancel_hyperparameter_tuning_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseCancelHyperparameterTuningJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseCancelHyperparameterTuningJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseCancelHyperparameterTuningJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._CancelHyperparameterTuningJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

    class _CancelNasJob(
        _BaseJobServiceRestTransport._BaseCancelNasJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.CancelNasJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseCancelNasJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_cancel_nas_job(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseCancelNasJob._get_transcoded_request(
                    http_options, request
                )
            )

            body = (
                _BaseJobServiceRestTransport._BaseCancelNasJob._get_request_body_json(
                    transcoded_request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseCancelNasJob._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._CancelNasJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

    class _CreateBatchPredictionJob(
        _BaseJobServiceRestTransport._BaseCreateBatchPredictionJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.CreateBatchPredictionJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseCreateBatchPredictionJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_create_batch_prediction_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseCreateBatchPredictionJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseCreateBatchPredictionJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseCreateBatchPredictionJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._CreateBatchPredictionJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = gca_batch_prediction_job.BatchPredictionJob()
            pb_resp = gca_batch_prediction_job.BatchPredictionJob.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_create_batch_prediction_job(resp)
            return resp

    class _CreateCustomJob(
        _BaseJobServiceRestTransport._BaseCreateCustomJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.CreateCustomJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseCreateCustomJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_create_custom_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseCreateCustomJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseCreateCustomJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseCreateCustomJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._CreateCustomJob._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                    body,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = gca_custom_job.CustomJob()
            pb_resp = gca_custom_job.CustomJob.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_create_custom_job(resp)
            return resp

    class _CreateDataLabelingJob(
        _BaseJobServiceRestTransport._BaseCreateDataLabelingJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.CreateDataLabelingJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseCreateDataLabelingJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_create_data_labeling_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseCreateDataLabelingJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseCreateDataLabelingJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseCreateDataLabelingJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._CreateDataLabelingJob._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                    body,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = gca_data_labeling_job.DataLabelingJob()
            pb_resp = gca_data_labeling_job.DataLabelingJob.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_create_data_labeling_job(resp)
            return resp

    class _CreateHyperparameterTuningJob(
        _BaseJobServiceRestTransport._BaseCreateHyperparameterTuningJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.CreateHyperparameterTuningJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseCreateHyperparameterTuningJob._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_create_hyperparameter_tuning_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseCreateHyperparameterTuningJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseCreateHyperparameterTuningJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseCreateHyperparameterTuningJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._CreateHyperparameterTuningJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = gca_hyperparameter_tuning_job.HyperparameterTuningJob()
            pb_resp = gca_hyperparameter_tuning_job.HyperparameterTuningJob.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_create_hyperparameter_tuning_job(resp)
            return resp

    class _CreateModelDeploymentMonitoringJob(
        _BaseJobServiceRestTransport._BaseCreateModelDeploymentMonitoringJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncJobServiceRestTransport.CreateModelDeploymentMonitoringJob"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseCreateModelDeploymentMonitoringJob._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_create_model_deployment_monitoring_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseCreateModelDeploymentMonitoringJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseCreateModelDeploymentMonitoringJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseCreateModelDeploymentMonitoringJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._CreateModelDeploymentMonitoringJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
            pb_resp = (
                gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.pb(
                    resp
                )
            )
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_create_model_deployment_monitoring_job(
                resp
            )
            return resp

    class _CreateNasJob(
        _BaseJobServiceRestTransport._BaseCreateNasJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.CreateNasJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.gca_nas_job.NasJob:
                    Represents a Neural Architecture
                Search (NAS) job.

            """

            http_options = (
                _BaseJobServiceRestTransport._BaseCreateNasJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_create_nas_job(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseCreateNasJob._get_transcoded_request(
                    http_options, request
                )
            )

            body = (
                _BaseJobServiceRestTransport._BaseCreateNasJob._get_request_body_json(
                    transcoded_request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseCreateNasJob._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._CreateNasJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = gca_nas_job.NasJob()
            pb_resp = gca_nas_job.NasJob.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_create_nas_job(resp)
            return resp

    class _DeleteBatchPredictionJob(
        _BaseJobServiceRestTransport._BaseDeleteBatchPredictionJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.DeleteBatchPredictionJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseDeleteBatchPredictionJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_delete_batch_prediction_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseDeleteBatchPredictionJob._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseDeleteBatchPredictionJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._DeleteBatchPredictionJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_delete_batch_prediction_job(resp)
            return resp

    class _DeleteCustomJob(
        _BaseJobServiceRestTransport._BaseDeleteCustomJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.DeleteCustomJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseDeleteCustomJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_delete_custom_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseDeleteCustomJob._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseDeleteCustomJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._DeleteCustomJob._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_delete_custom_job(resp)
            return resp

    class _DeleteDataLabelingJob(
        _BaseJobServiceRestTransport._BaseDeleteDataLabelingJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.DeleteDataLabelingJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseDeleteDataLabelingJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_delete_data_labeling_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseDeleteDataLabelingJob._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseDeleteDataLabelingJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._DeleteDataLabelingJob._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_delete_data_labeling_job(resp)
            return resp

    class _DeleteHyperparameterTuningJob(
        _BaseJobServiceRestTransport._BaseDeleteHyperparameterTuningJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.DeleteHyperparameterTuningJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseDeleteHyperparameterTuningJob._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_delete_hyperparameter_tuning_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseDeleteHyperparameterTuningJob._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseDeleteHyperparameterTuningJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._DeleteHyperparameterTuningJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_delete_hyperparameter_tuning_job(resp)
            return resp

    class _DeleteModelDeploymentMonitoringJob(
        _BaseJobServiceRestTransport._BaseDeleteModelDeploymentMonitoringJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncJobServiceRestTransport.DeleteModelDeploymentMonitoringJob"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseDeleteModelDeploymentMonitoringJob._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_delete_model_deployment_monitoring_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseDeleteModelDeploymentMonitoringJob._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseDeleteModelDeploymentMonitoringJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._DeleteModelDeploymentMonitoringJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_delete_model_deployment_monitoring_job(
                resp
            )
            return resp

    class _DeleteNasJob(
        _BaseJobServiceRestTransport._BaseDeleteNasJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.DeleteNasJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseDeleteNasJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_delete_nas_job(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseDeleteNasJob._get_transcoded_request(
                    http_options, request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseDeleteNasJob._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._DeleteNasJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_delete_nas_job(resp)
            return resp

    class _GetBatchPredictionJob(
        _BaseJobServiceRestTransport._BaseGetBatchPredictionJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.GetBatchPredictionJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseGetBatchPredictionJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_batch_prediction_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseGetBatchPredictionJob._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseGetBatchPredictionJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._GetBatchPredictionJob._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = batch_prediction_job.BatchPredictionJob()
            pb_resp = batch_prediction_job.BatchPredictionJob.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_batch_prediction_job(resp)
            return resp

    class _GetCustomJob(
        _BaseJobServiceRestTransport._BaseGetCustomJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.GetCustomJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseGetCustomJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_custom_job(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseGetCustomJob._get_transcoded_request(
                    http_options, request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseGetCustomJob._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._GetCustomJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = custom_job.CustomJob()
            pb_resp = custom_job.CustomJob.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_custom_job(resp)
            return resp

    class _GetDataLabelingJob(
        _BaseJobServiceRestTransport._BaseGetDataLabelingJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.GetDataLabelingJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseGetDataLabelingJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_data_labeling_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseGetDataLabelingJob._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseGetDataLabelingJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._GetDataLabelingJob._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = data_labeling_job.DataLabelingJob()
            pb_resp = data_labeling_job.DataLabelingJob.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_data_labeling_job(resp)
            return resp

    class _GetHyperparameterTuningJob(
        _BaseJobServiceRestTransport._BaseGetHyperparameterTuningJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.GetHyperparameterTuningJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseGetHyperparameterTuningJob._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_get_hyperparameter_tuning_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseGetHyperparameterTuningJob._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseGetHyperparameterTuningJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._GetHyperparameterTuningJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = hyperparameter_tuning_job.HyperparameterTuningJob()
            pb_resp = hyperparameter_tuning_job.HyperparameterTuningJob.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_hyperparameter_tuning_job(resp)
            return resp

    class _GetModelDeploymentMonitoringJob(
        _BaseJobServiceRestTransport._BaseGetModelDeploymentMonitoringJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.GetModelDeploymentMonitoringJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseGetModelDeploymentMonitoringJob._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_get_model_deployment_monitoring_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseGetModelDeploymentMonitoringJob._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseGetModelDeploymentMonitoringJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._GetModelDeploymentMonitoringJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
            pb_resp = model_deployment_monitoring_job.ModelDeploymentMonitoringJob.pb(
                resp
            )
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_model_deployment_monitoring_job(
                resp
            )
            return resp

    class _GetNasJob(
        _BaseJobServiceRestTransport._BaseGetNasJob, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.GetNasJob")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.nas_job.NasJob:
                    Represents a Neural Architecture
                Search (NAS) job.

            """

            http_options = (
                _BaseJobServiceRestTransport._BaseGetNasJob._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_nas_job(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseGetNasJob._get_transcoded_request(
                    http_options, request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseGetNasJob._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._GetNasJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = nas_job.NasJob()
            pb_resp = nas_job.NasJob.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_nas_job(resp)
            return resp

    class _GetNasTrialDetail(
        _BaseJobServiceRestTransport._BaseGetNasTrialDetail, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.GetNasTrialDetail")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseGetNasTrialDetail._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_nas_trial_detail(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseGetNasTrialDetail._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseGetNasTrialDetail._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._GetNasTrialDetail._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = nas_job.NasTrialDetail()
            pb_resp = nas_job.NasTrialDetail.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_nas_trial_detail(resp)
            return resp

    class _ListBatchPredictionJobs(
        _BaseJobServiceRestTransport._BaseListBatchPredictionJobs,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.ListBatchPredictionJobs")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.job_service.ListBatchPredictionJobsResponse:
                        Response message for
                    [JobService.ListBatchPredictionJobs][google.cloud.aiplatform.v1.JobService.ListBatchPredictionJobs]

            """

            http_options = (
                _BaseJobServiceRestTransport._BaseListBatchPredictionJobs._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_batch_prediction_jobs(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseListBatchPredictionJobs._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseListBatchPredictionJobs._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._ListBatchPredictionJobs._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = job_service.ListBatchPredictionJobsResponse()
            pb_resp = job_service.ListBatchPredictionJobsResponse.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_batch_prediction_jobs(resp)
            return resp

    class _ListCustomJobs(
        _BaseJobServiceRestTransport._BaseListCustomJobs, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.ListCustomJobs")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.job_service.ListCustomJobsResponse:
                    Response message for
                [JobService.ListCustomJobs][google.cloud.aiplatform.v1.JobService.ListCustomJobs]

            """

            http_options = (
                _BaseJobServiceRestTransport._BaseListCustomJobs._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_custom_jobs(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseListCustomJobs._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseListCustomJobs._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._ListCustomJobs._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = job_service.ListCustomJobsResponse()
            pb_resp = job_service.ListCustomJobsResponse.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_custom_jobs(resp)
            return resp

    class _ListDataLabelingJobs(
        _BaseJobServiceRestTransport._BaseListDataLabelingJobs, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.ListDataLabelingJobs")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.job_service.ListDataLabelingJobsResponse:
                    Response message for
                [JobService.ListDataLabelingJobs][google.cloud.aiplatform.v1.JobService.ListDataLabelingJobs].

            """

            http_options = (
                _BaseJobServiceRestTransport._BaseListDataLabelingJobs._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_data_labeling_jobs(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseListDataLabelingJobs._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseListDataLabelingJobs._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._ListDataLabelingJobs._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = job_service.ListDataLabelingJobsResponse()
            pb_resp = job_service.ListDataLabelingJobsResponse.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_data_labeling_jobs(resp)
            return resp

    class _ListHyperparameterTuningJobs(
        _BaseJobServiceRestTransport._BaseListHyperparameterTuningJobs,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.ListHyperparameterTuningJobs")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.job_service.ListHyperparameterTuningJobsResponse:
                        Response message for
                    [JobService.ListHyperparameterTuningJobs][google.cloud.aiplatform.v1.JobService.ListHyperparameterTuningJobs]

            """

            http_options = (
                _BaseJobServiceRestTransport._BaseListHyperparameterTuningJobs._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_list_hyperparameter_tuning_jobs(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseListHyperparameterTuningJobs._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseListHyperparameterTuningJobs._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._ListHyperparameterTuningJobs._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = job_service.ListHyperparameterTuningJobsResponse()
            pb_resp = job_service.ListHyperparameterTuningJobsResponse.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_hyperparameter_tuning_jobs(resp)
            return resp

    class _ListModelDeploymentMonitoringJobs(
        _BaseJobServiceRestTransport._BaseListModelDeploymentMonitoringJobs,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncJobServiceRestTransport.ListModelDeploymentMonitoringJobs"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.job_service.ListModelDeploymentMonitoringJobsResponse:
                        Response message for
                    [JobService.ListModelDeploymentMonitoringJobs][google.cloud.aiplatform.v1.JobService.ListModelDeploymentMonitoringJobs].

            """

            http_options = (
                _BaseJobServiceRestTransport._BaseListModelDeploymentMonitoringJobs._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_list_model_deployment_monitoring_jobs(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseListModelDeploymentMonitoringJobs._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseListModelDeploymentMonitoringJobs._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._ListModelDeploymentMonitoringJobs._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = job_service.ListModelDeploymentMonitoringJobsResponse()
            pb_resp = job_service.ListModelDeploymentMonitoringJobsResponse.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_model_deployment_monitoring_jobs(
                resp
            )
            return resp

    class _ListNasJobs(
        _BaseJobServiceRestTransport._BaseListNasJobs, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.ListNasJobs")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.job_service.ListNasJobsResponse:
                    Response message for
                [JobService.ListNasJobs][google.cloud.aiplatform.v1.JobService.ListNasJobs]

            """

            http_options = (
                _BaseJobServiceRestTransport._BaseListNasJobs._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_nas_jobs(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseListNasJobs._get_transcoded_request(
                    http_options, request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseListNasJobs._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._ListNasJobs._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = job_service.ListNasJobsResponse()
            pb_resp = job_service.ListNasJobsResponse.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_nas_jobs(resp)
            return resp

    class _ListNasTrialDetails(
        _BaseJobServiceRestTransport._BaseListNasTrialDetails, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.ListNasTrialDetails")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.job_service.ListNasTrialDetailsResponse:
                    Response message for
                [JobService.ListNasTrialDetails][google.cloud.aiplatform.v1.JobService.ListNasTrialDetails]

            """

            http_options = (
                _BaseJobServiceRestTransport._BaseListNasTrialDetails._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_nas_trial_details(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseListNasTrialDetails._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseListNasTrialDetails._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._ListNasTrialDetails._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = job_service.ListNasTrialDetailsResponse()
            pb_resp = job_service.ListNasTrialDetailsResponse.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_nas_trial_details(resp)
            return resp

    class _PauseModelDeploymentMonitoringJob(
        _BaseJobServiceRestTransport._BasePauseModelDeploymentMonitoringJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncJobServiceRestTransport.PauseModelDeploymentMonitoringJob"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.
            """

            http_options = (
                _BaseJobServiceRestTransport._BasePauseModelDeploymentMonitoringJob._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_pause_model_deployment_monitoring_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BasePauseModelDeploymentMonitoringJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BasePauseModelDeploymentMonitoringJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BasePauseModelDeploymentMonitoringJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._PauseModelDeploymentMonitoringJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

    class _ResumeModelDeploymentMonitoringJob(
        _BaseJobServiceRestTransport._BaseResumeModelDeploymentMonitoringJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncJobServiceRestTransport.ResumeModelDeploymentMonitoringJob"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseResumeModelDeploymentMonitoringJob._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_resume_model_deployment_monitoring_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseResumeModelDeploymentMonitoringJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseResumeModelDeploymentMonitoringJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseResumeModelDeploymentMonitoringJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._ResumeModelDeploymentMonitoringJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

    class _SearchModelDeploymentMonitoringStatsAnomalies(
        _BaseJobServiceRestTransport._BaseSearchModelDeploymentMonitoringStatsAnomalies,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncJobServiceRestTransport.SearchModelDeploymentMonitoringStatsAnomalies"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, str]]): Strings which should be
                        sent along with the request as metadata.

                Returns:
                    ~.job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse:
                        Response message for
                    [JobService.SearchModelDeploymentMonitoringStatsAnomalies][google.cloud.aiplatform.v1.JobService.SearchModelDeploymentMonitoringStatsAnomalies].

            """

            http_options = (
                _BaseJobServiceRestTransport._BaseSearchModelDeploymentMonitoringStatsAnomalies._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_search_model_deployment_monitoring_stats_anomalies(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseSearchModelDeploymentMonitoringStatsAnomalies._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseSearchModelDeploymentMonitoringStatsAnomalies._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseSearchModelDeploymentMonitoringStatsAnomalies._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._SearchModelDeploymentMonitoringStatsAnomalies._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse()
            pb_resp = (
                job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse.pb(
                    resp
                )
            )
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_search_model_deployment_monitoring_stats_anomalies(
                resp
            )
            return resp

    class _UpdateModelDeploymentMonitoringJob(
        _BaseJobServiceRestTransport._BaseUpdateModelDeploymentMonitoringJob,
        AsyncJobServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncJobServiceRestTransport.UpdateModelDeploymentMonitoringJob"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
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

            http_options = (
                _BaseJobServiceRestTransport._BaseUpdateModelDeploymentMonitoringJob._get_http_options()
            )
            (
                request,
                metadata,
            ) = await self._interceptor.pre_update_model_deployment_monitoring_job(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseUpdateModelDeploymentMonitoringJob._get_transcoded_request(
                http_options, request
            )

            body = _BaseJobServiceRestTransport._BaseUpdateModelDeploymentMonitoringJob._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseUpdateModelDeploymentMonitoringJob._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._UpdateModelDeploymentMonitoringJob._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_update_model_deployment_monitoring_job(
                resp
            )
            return resp

    @property
    def operations_client(self) -> AsyncOperationsRestClient:
        """Create the async client designed to process long-running operations.

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
                        "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}:cancel",
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
                        "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:cancel",
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
                        "uri": "/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:cancel",
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
                        "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}",
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
                        "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
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
                        "uri": "/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
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
                        "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}",
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
                        "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
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
                        "uri": "/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
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
                        "uri": "/ui/{name=projects/*/locations/*/agents/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/apps/*}/operations",
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
                        "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*}/operations",
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
                        "uri": "/v1/{name=projects/*/locations/*/notebookExecutionJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*}/operations",
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
                        "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}:wait",
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
                        "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:wait",
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
                        "uri": "/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:wait",
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

            rest_transport = operations_v1.AsyncOperationsRestTransport(  # type: ignore
                host=self._host,
                # use the credentials which are saved
                credentials=self._credentials,  # type: ignore
                http_options=http_options,
                path_prefix="v1",
            )

            self._operations_client = AsyncOperationsRestClient(
                transport=rest_transport
            )

        # Return the client from cache.
        return self._operations_client

    @property
    def cancel_batch_prediction_job(
        self,
    ) -> Callable[[job_service.CancelBatchPredictionJobRequest], empty_pb2.Empty]:
        return self._CancelBatchPredictionJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def cancel_custom_job(
        self,
    ) -> Callable[[job_service.CancelCustomJobRequest], empty_pb2.Empty]:
        return self._CancelCustomJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def cancel_data_labeling_job(
        self,
    ) -> Callable[[job_service.CancelDataLabelingJobRequest], empty_pb2.Empty]:
        return self._CancelDataLabelingJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def cancel_hyperparameter_tuning_job(
        self,
    ) -> Callable[[job_service.CancelHyperparameterTuningJobRequest], empty_pb2.Empty]:
        return self._CancelHyperparameterTuningJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def cancel_nas_job(
        self,
    ) -> Callable[[job_service.CancelNasJobRequest], empty_pb2.Empty]:
        return self._CancelNasJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.CreateBatchPredictionJobRequest],
        gca_batch_prediction_job.BatchPredictionJob,
    ]:
        return self._CreateBatchPredictionJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_custom_job(
        self,
    ) -> Callable[[job_service.CreateCustomJobRequest], gca_custom_job.CustomJob]:
        return self._CreateCustomJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_data_labeling_job(
        self,
    ) -> Callable[
        [job_service.CreateDataLabelingJobRequest],
        gca_data_labeling_job.DataLabelingJob,
    ]:
        return self._CreateDataLabelingJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.CreateHyperparameterTuningJobRequest],
        gca_hyperparameter_tuning_job.HyperparameterTuningJob,
    ]:
        return self._CreateHyperparameterTuningJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.CreateModelDeploymentMonitoringJobRequest],
        gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob,
    ]:
        return self._CreateModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_nas_job(
        self,
    ) -> Callable[[job_service.CreateNasJobRequest], gca_nas_job.NasJob]:
        return self._CreateNasJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.DeleteBatchPredictionJobRequest], operations_pb2.Operation
    ]:
        return self._DeleteBatchPredictionJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_custom_job(
        self,
    ) -> Callable[[job_service.DeleteCustomJobRequest], operations_pb2.Operation]:
        return self._DeleteCustomJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_data_labeling_job(
        self,
    ) -> Callable[[job_service.DeleteDataLabelingJobRequest], operations_pb2.Operation]:
        return self._DeleteDataLabelingJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.DeleteHyperparameterTuningJobRequest], operations_pb2.Operation
    ]:
        return self._DeleteHyperparameterTuningJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.DeleteModelDeploymentMonitoringJobRequest],
        operations_pb2.Operation,
    ]:
        return self._DeleteModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_nas_job(
        self,
    ) -> Callable[[job_service.DeleteNasJobRequest], operations_pb2.Operation]:
        return self._DeleteNasJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.GetBatchPredictionJobRequest],
        batch_prediction_job.BatchPredictionJob,
    ]:
        return self._GetBatchPredictionJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_custom_job(
        self,
    ) -> Callable[[job_service.GetCustomJobRequest], custom_job.CustomJob]:
        return self._GetCustomJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_data_labeling_job(
        self,
    ) -> Callable[
        [job_service.GetDataLabelingJobRequest], data_labeling_job.DataLabelingJob
    ]:
        return self._GetDataLabelingJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.GetHyperparameterTuningJobRequest],
        hyperparameter_tuning_job.HyperparameterTuningJob,
    ]:
        return self._GetHyperparameterTuningJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.GetModelDeploymentMonitoringJobRequest],
        model_deployment_monitoring_job.ModelDeploymentMonitoringJob,
    ]:
        return self._GetModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_nas_job(self) -> Callable[[job_service.GetNasJobRequest], nas_job.NasJob]:
        return self._GetNasJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_nas_trial_detail(
        self,
    ) -> Callable[[job_service.GetNasTrialDetailRequest], nas_job.NasTrialDetail]:
        return self._GetNasTrialDetail(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_batch_prediction_jobs(
        self,
    ) -> Callable[
        [job_service.ListBatchPredictionJobsRequest],
        job_service.ListBatchPredictionJobsResponse,
    ]:
        return self._ListBatchPredictionJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_custom_jobs(
        self,
    ) -> Callable[
        [job_service.ListCustomJobsRequest], job_service.ListCustomJobsResponse
    ]:
        return self._ListCustomJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_data_labeling_jobs(
        self,
    ) -> Callable[
        [job_service.ListDataLabelingJobsRequest],
        job_service.ListDataLabelingJobsResponse,
    ]:
        return self._ListDataLabelingJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_hyperparameter_tuning_jobs(
        self,
    ) -> Callable[
        [job_service.ListHyperparameterTuningJobsRequest],
        job_service.ListHyperparameterTuningJobsResponse,
    ]:
        return self._ListHyperparameterTuningJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_model_deployment_monitoring_jobs(
        self,
    ) -> Callable[
        [job_service.ListModelDeploymentMonitoringJobsRequest],
        job_service.ListModelDeploymentMonitoringJobsResponse,
    ]:
        return self._ListModelDeploymentMonitoringJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_nas_jobs(
        self,
    ) -> Callable[[job_service.ListNasJobsRequest], job_service.ListNasJobsResponse]:
        return self._ListNasJobs(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_nas_trial_details(
        self,
    ) -> Callable[
        [job_service.ListNasTrialDetailsRequest],
        job_service.ListNasTrialDetailsResponse,
    ]:
        return self._ListNasTrialDetails(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def pause_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.PauseModelDeploymentMonitoringJobRequest], empty_pb2.Empty
    ]:
        return self._PauseModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def resume_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.ResumeModelDeploymentMonitoringJobRequest], empty_pb2.Empty
    ]:
        return self._ResumeModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def search_model_deployment_monitoring_stats_anomalies(
        self,
    ) -> Callable[
        [job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest],
        job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse,
    ]:
        return self._SearchModelDeploymentMonitoringStatsAnomalies(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def update_model_deployment_monitoring_job(
        self,
    ) -> Callable[
        [job_service.UpdateModelDeploymentMonitoringJobRequest],
        operations_pb2.Operation,
    ]:
        return self._UpdateModelDeploymentMonitoringJob(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_location(self):
        return self._GetLocation(self._session, self._host, self._interceptor)  # type: ignore

    class _GetLocation(
        _BaseJobServiceRestTransport._BaseGetLocation, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.GetLocation")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                locations_pb2.Location: Response from GetLocation method.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseGetLocation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_location(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseGetLocation._get_transcoded_request(
                    http_options, request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseGetLocation._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._GetLocation._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = locations_pb2.Location()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_get_location(resp)
            return resp

    @property
    def list_locations(self):
        return self._ListLocations(self._session, self._host, self._interceptor)  # type: ignore

    class _ListLocations(
        _BaseJobServiceRestTransport._BaseListLocations, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.ListLocations")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                locations_pb2.ListLocationsResponse: Response from ListLocations method.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseListLocations._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_locations(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseListLocations._get_transcoded_request(
                    http_options, request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseListLocations._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._ListLocations._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = locations_pb2.ListLocationsResponse()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_list_locations(resp)
            return resp

    @property
    def get_iam_policy(self):
        return self._GetIamPolicy(self._session, self._host, self._interceptor)  # type: ignore

    class _GetIamPolicy(
        _BaseJobServiceRestTransport._BaseGetIamPolicy, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.GetIamPolicy")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                policy_pb2.Policy: Response from GetIamPolicy method.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseGetIamPolicy._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_iam_policy(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseGetIamPolicy._get_transcoded_request(
                    http_options, request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseGetIamPolicy._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._GetIamPolicy._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = policy_pb2.Policy()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_get_iam_policy(resp)
            return resp

    @property
    def set_iam_policy(self):
        return self._SetIamPolicy(self._session, self._host, self._interceptor)  # type: ignore

    class _SetIamPolicy(
        _BaseJobServiceRestTransport._BaseSetIamPolicy, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.SetIamPolicy")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                policy_pb2.Policy: Response from SetIamPolicy method.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseSetIamPolicy._get_http_options()
            )
            request, metadata = await self._interceptor.pre_set_iam_policy(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseSetIamPolicy._get_transcoded_request(
                    http_options, request
                )
            )

            body = (
                _BaseJobServiceRestTransport._BaseSetIamPolicy._get_request_body_json(
                    transcoded_request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseSetIamPolicy._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._SetIamPolicy._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = policy_pb2.Policy()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_set_iam_policy(resp)
            return resp

    @property
    def test_iam_permissions(self):
        return self._TestIamPermissions(self._session, self._host, self._interceptor)  # type: ignore

    class _TestIamPermissions(
        _BaseJobServiceRestTransport._BaseTestIamPermissions, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.TestIamPermissions")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                iam_policy_pb2.TestIamPermissionsResponse: Response from TestIamPermissions method.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseTestIamPermissions._get_http_options()
            )
            request, metadata = await self._interceptor.pre_test_iam_permissions(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseTestIamPermissions._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseTestIamPermissions._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._TestIamPermissions._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = iam_policy_pb2.TestIamPermissionsResponse()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_test_iam_permissions(resp)
            return resp

    @property
    def cancel_operation(self):
        return self._CancelOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _CancelOperation(
        _BaseJobServiceRestTransport._BaseCancelOperation, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.CancelOperation")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseCancelOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_cancel_operation(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseCancelOperation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseCancelOperation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._CancelOperation._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            return await self._interceptor.post_cancel_operation(None)

    @property
    def delete_operation(self):
        return self._DeleteOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _DeleteOperation(
        _BaseJobServiceRestTransport._BaseDeleteOperation, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.DeleteOperation")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseDeleteOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_delete_operation(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseDeleteOperation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseJobServiceRestTransport._BaseDeleteOperation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncJobServiceRestTransport._DeleteOperation._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            return await self._interceptor.post_delete_operation(None)

    @property
    def get_operation(self):
        return self._GetOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _GetOperation(
        _BaseJobServiceRestTransport._BaseGetOperation, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.GetOperation")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.Operation: Response from GetOperation method.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseGetOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_operation(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseGetOperation._get_transcoded_request(
                    http_options, request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseGetOperation._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._GetOperation._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = operations_pb2.Operation()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_get_operation(resp)
            return resp

    @property
    def list_operations(self):
        return self._ListOperations(self._session, self._host, self._interceptor)  # type: ignore

    class _ListOperations(
        _BaseJobServiceRestTransport._BaseListOperations, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.ListOperations")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.ListOperationsResponse: Response from ListOperations method.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseListOperations._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_operations(
                request, metadata
            )
            transcoded_request = _BaseJobServiceRestTransport._BaseListOperations._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseListOperations._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._ListOperations._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = operations_pb2.ListOperationsResponse()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_list_operations(resp)
            return resp

    @property
    def wait_operation(self):
        return self._WaitOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _WaitOperation(
        _BaseJobServiceRestTransport._BaseWaitOperation, AsyncJobServiceRestStub
    ):
        def __hash__(self):
            return hash("AsyncJobServiceRestTransport.WaitOperation")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.Operation: Response from WaitOperation method.
            """

            http_options = (
                _BaseJobServiceRestTransport._BaseWaitOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_wait_operation(
                request, metadata
            )
            transcoded_request = (
                _BaseJobServiceRestTransport._BaseWaitOperation._get_transcoded_request(
                    http_options, request
                )
            )

            # Jsonify the query params
            query_params = (
                _BaseJobServiceRestTransport._BaseWaitOperation._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = await AsyncJobServiceRestTransport._WaitOperation._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = operations_pb2.Operation()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_wait_operation(resp)
            return resp

    @property
    def kind(self) -> str:
        return "rest_asyncio"

    async def close(self):
        await self._session.close()
