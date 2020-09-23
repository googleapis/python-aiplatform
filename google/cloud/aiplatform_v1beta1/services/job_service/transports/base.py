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

import abc
import typing

from google import auth
from google.api_core import operations_v1  # type: ignore
from google.auth import credentials  # type: ignore

from google.cloud.aiplatform_v1beta1.types import batch_prediction_job
from google.cloud.aiplatform_v1beta1.types import (
    batch_prediction_job as gca_batch_prediction_job,
)
from google.cloud.aiplatform_v1beta1.types import custom_job
from google.cloud.aiplatform_v1beta1.types import custom_job as gca_custom_job
from google.cloud.aiplatform_v1beta1.types import data_labeling_job
from google.cloud.aiplatform_v1beta1.types import (
    data_labeling_job as gca_data_labeling_job,
)
from google.cloud.aiplatform_v1beta1.types import hyperparameter_tuning_job
from google.cloud.aiplatform_v1beta1.types import (
    hyperparameter_tuning_job as gca_hyperparameter_tuning_job,
)
from google.cloud.aiplatform_v1beta1.types import job_service
from google.longrunning import operations_pb2 as operations  # type: ignore
from google.protobuf import empty_pb2 as empty  # type: ignore


class JobServiceTransport(metaclass=abc.ABCMeta):
    """Abstract transport class for JobService."""

    AUTH_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: credentials.Credentials = None,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]): The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
        """
        # Save the hostname. Default to port 443 (HTTPS) if none is specified.
        if ":" not in host:
            host += ":443"
        self._host = host

        # If no credentials are provided, then determine the appropriate
        # defaults.
        if credentials is None:
            credentials, _ = auth.default(scopes=self.AUTH_SCOPES)

        # Save the credentials.
        self._credentials = credentials

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Return the client designed to process long-running operations."""
        raise NotImplementedError

    @property
    def create_custom_job(
        self,
    ) -> typing.Callable[
        [job_service.CreateCustomJobRequest], gca_custom_job.CustomJob
    ]:
        raise NotImplementedError

    @property
    def get_custom_job(
        self,
    ) -> typing.Callable[[job_service.GetCustomJobRequest], custom_job.CustomJob]:
        raise NotImplementedError

    @property
    def list_custom_jobs(
        self,
    ) -> typing.Callable[
        [job_service.ListCustomJobsRequest], job_service.ListCustomJobsResponse
    ]:
        raise NotImplementedError

    @property
    def delete_custom_job(
        self,
    ) -> typing.Callable[[job_service.DeleteCustomJobRequest], operations.Operation]:
        raise NotImplementedError

    @property
    def cancel_custom_job(
        self,
    ) -> typing.Callable[[job_service.CancelCustomJobRequest], empty.Empty]:
        raise NotImplementedError

    @property
    def create_data_labeling_job(
        self,
    ) -> typing.Callable[
        [job_service.CreateDataLabelingJobRequest],
        gca_data_labeling_job.DataLabelingJob,
    ]:
        raise NotImplementedError

    @property
    def get_data_labeling_job(
        self,
    ) -> typing.Callable[
        [job_service.GetDataLabelingJobRequest], data_labeling_job.DataLabelingJob
    ]:
        raise NotImplementedError

    @property
    def list_data_labeling_jobs(
        self,
    ) -> typing.Callable[
        [job_service.ListDataLabelingJobsRequest],
        job_service.ListDataLabelingJobsResponse,
    ]:
        raise NotImplementedError

    @property
    def delete_data_labeling_job(
        self,
    ) -> typing.Callable[
        [job_service.DeleteDataLabelingJobRequest], operations.Operation
    ]:
        raise NotImplementedError

    @property
    def cancel_data_labeling_job(
        self,
    ) -> typing.Callable[[job_service.CancelDataLabelingJobRequest], empty.Empty]:
        raise NotImplementedError

    @property
    def create_hyperparameter_tuning_job(
        self,
    ) -> typing.Callable[
        [job_service.CreateHyperparameterTuningJobRequest],
        gca_hyperparameter_tuning_job.HyperparameterTuningJob,
    ]:
        raise NotImplementedError

    @property
    def get_hyperparameter_tuning_job(
        self,
    ) -> typing.Callable[
        [job_service.GetHyperparameterTuningJobRequest],
        hyperparameter_tuning_job.HyperparameterTuningJob,
    ]:
        raise NotImplementedError

    @property
    def list_hyperparameter_tuning_jobs(
        self,
    ) -> typing.Callable[
        [job_service.ListHyperparameterTuningJobsRequest],
        job_service.ListHyperparameterTuningJobsResponse,
    ]:
        raise NotImplementedError

    @property
    def delete_hyperparameter_tuning_job(
        self,
    ) -> typing.Callable[
        [job_service.DeleteHyperparameterTuningJobRequest], operations.Operation
    ]:
        raise NotImplementedError

    @property
    def cancel_hyperparameter_tuning_job(
        self,
    ) -> typing.Callable[
        [job_service.CancelHyperparameterTuningJobRequest], empty.Empty
    ]:
        raise NotImplementedError

    @property
    def create_batch_prediction_job(
        self,
    ) -> typing.Callable[
        [job_service.CreateBatchPredictionJobRequest],
        gca_batch_prediction_job.BatchPredictionJob,
    ]:
        raise NotImplementedError

    @property
    def get_batch_prediction_job(
        self,
    ) -> typing.Callable[
        [job_service.GetBatchPredictionJobRequest],
        batch_prediction_job.BatchPredictionJob,
    ]:
        raise NotImplementedError

    @property
    def list_batch_prediction_jobs(
        self,
    ) -> typing.Callable[
        [job_service.ListBatchPredictionJobsRequest],
        job_service.ListBatchPredictionJobsResponse,
    ]:
        raise NotImplementedError

    @property
    def delete_batch_prediction_job(
        self,
    ) -> typing.Callable[
        [job_service.DeleteBatchPredictionJobRequest], operations.Operation
    ]:
        raise NotImplementedError

    @property
    def cancel_batch_prediction_job(
        self,
    ) -> typing.Callable[[job_service.CancelBatchPredictionJobRequest], empty.Empty]:
        raise NotImplementedError


__all__ = ("JobServiceTransport",)
