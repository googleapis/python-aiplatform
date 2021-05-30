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
import pkg_resources

from google import auth  # type: ignore
from google.api_core import exceptions  # type: ignore
from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.api_core import operations_v1  # type: ignore
from google.auth import credentials  # type: ignore

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
from google.longrunning import operations_pb2 as operations  # type: ignore
from google.protobuf import empty_pb2 as empty  # type: ignore


try:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            "google-cloud-aiplatform",
        ).version,
    )
except pkg_resources.DistributionNotFound:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo()


class JobServiceTransport(abc.ABC):
    """Abstract transport class for JobService."""

    AUTH_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: credentials.Credentials = None,
        credentials_file: typing.Optional[str] = None,
        scopes: typing.Optional[typing.Sequence[str]] = AUTH_SCOPES,
        quota_project_id: typing.Optional[str] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
        **kwargs,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]): The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is mutually exclusive with credentials.
            scope (Optional[Sequence[str]]): A list of scopes.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):	
                The client info used to send a user-agent string along with	
                API requests. If ``None``, then default info will be used.	
                Generally, you only need to set this if you're developing	
                your own client library.
        """
        # Save the hostname. Default to port 443 (HTTPS) if none is specified.
        if ":" not in host:
            host += ":443"
        self._host = host

        # If no credentials are provided, then determine the appropriate
        # defaults.
        if credentials and credentials_file:
            raise exceptions.DuplicateCredentialArgs(
                "'credentials_file' and 'credentials' are mutually exclusive"
            )

        if credentials_file is not None:
            credentials, _ = auth.load_credentials_from_file(
                credentials_file, scopes=scopes, quota_project_id=quota_project_id
            )

        elif credentials is None:
            credentials, _ = auth.default(
                scopes=scopes, quota_project_id=quota_project_id
            )

        # Save the credentials.
        self._credentials = credentials

        # Lifted into its own function so it can be stubbed out during tests.
        self._prep_wrapped_messages(client_info)

    def _prep_wrapped_messages(self, client_info):
        # Precompute the wrapped methods.
        self._wrapped_methods = {
            self.create_custom_job: gapic_v1.method.wrap_method(
                self.create_custom_job, default_timeout=None, client_info=client_info,
            ),
            self.get_custom_job: gapic_v1.method.wrap_method(
                self.get_custom_job, default_timeout=None, client_info=client_info,
            ),
            self.list_custom_jobs: gapic_v1.method.wrap_method(
                self.list_custom_jobs, default_timeout=None, client_info=client_info,
            ),
            self.delete_custom_job: gapic_v1.method.wrap_method(
                self.delete_custom_job, default_timeout=None, client_info=client_info,
            ),
            self.cancel_custom_job: gapic_v1.method.wrap_method(
                self.cancel_custom_job, default_timeout=None, client_info=client_info,
            ),
            self.create_data_labeling_job: gapic_v1.method.wrap_method(
                self.create_data_labeling_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_data_labeling_job: gapic_v1.method.wrap_method(
                self.get_data_labeling_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_data_labeling_jobs: gapic_v1.method.wrap_method(
                self.list_data_labeling_jobs,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_data_labeling_job: gapic_v1.method.wrap_method(
                self.delete_data_labeling_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.cancel_data_labeling_job: gapic_v1.method.wrap_method(
                self.cancel_data_labeling_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_hyperparameter_tuning_job: gapic_v1.method.wrap_method(
                self.create_hyperparameter_tuning_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_hyperparameter_tuning_job: gapic_v1.method.wrap_method(
                self.get_hyperparameter_tuning_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_hyperparameter_tuning_jobs: gapic_v1.method.wrap_method(
                self.list_hyperparameter_tuning_jobs,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_hyperparameter_tuning_job: gapic_v1.method.wrap_method(
                self.delete_hyperparameter_tuning_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.cancel_hyperparameter_tuning_job: gapic_v1.method.wrap_method(
                self.cancel_hyperparameter_tuning_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_batch_prediction_job: gapic_v1.method.wrap_method(
                self.create_batch_prediction_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_batch_prediction_job: gapic_v1.method.wrap_method(
                self.get_batch_prediction_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_batch_prediction_jobs: gapic_v1.method.wrap_method(
                self.list_batch_prediction_jobs,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_batch_prediction_job: gapic_v1.method.wrap_method(
                self.delete_batch_prediction_job,
                default_timeout=None,
                client_info=client_info,
            ),
            self.cancel_batch_prediction_job: gapic_v1.method.wrap_method(
                self.cancel_batch_prediction_job,
                default_timeout=None,
                client_info=client_info,
            ),
        }

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Return the client designed to process long-running operations."""
        raise NotImplementedError()

    @property
    def create_custom_job(
        self,
    ) -> typing.Callable[
        [job_service.CreateCustomJobRequest],
        typing.Union[
            gca_custom_job.CustomJob, typing.Awaitable[gca_custom_job.CustomJob]
        ],
    ]:
        raise NotImplementedError()

    @property
    def get_custom_job(
        self,
    ) -> typing.Callable[
        [job_service.GetCustomJobRequest],
        typing.Union[custom_job.CustomJob, typing.Awaitable[custom_job.CustomJob]],
    ]:
        raise NotImplementedError()

    @property
    def list_custom_jobs(
        self,
    ) -> typing.Callable[
        [job_service.ListCustomJobsRequest],
        typing.Union[
            job_service.ListCustomJobsResponse,
            typing.Awaitable[job_service.ListCustomJobsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def delete_custom_job(
        self,
    ) -> typing.Callable[
        [job_service.DeleteCustomJobRequest],
        typing.Union[operations.Operation, typing.Awaitable[operations.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def cancel_custom_job(
        self,
    ) -> typing.Callable[
        [job_service.CancelCustomJobRequest],
        typing.Union[empty.Empty, typing.Awaitable[empty.Empty]],
    ]:
        raise NotImplementedError()

    @property
    def create_data_labeling_job(
        self,
    ) -> typing.Callable[
        [job_service.CreateDataLabelingJobRequest],
        typing.Union[
            gca_data_labeling_job.DataLabelingJob,
            typing.Awaitable[gca_data_labeling_job.DataLabelingJob],
        ],
    ]:
        raise NotImplementedError()

    @property
    def get_data_labeling_job(
        self,
    ) -> typing.Callable[
        [job_service.GetDataLabelingJobRequest],
        typing.Union[
            data_labeling_job.DataLabelingJob,
            typing.Awaitable[data_labeling_job.DataLabelingJob],
        ],
    ]:
        raise NotImplementedError()

    @property
    def list_data_labeling_jobs(
        self,
    ) -> typing.Callable[
        [job_service.ListDataLabelingJobsRequest],
        typing.Union[
            job_service.ListDataLabelingJobsResponse,
            typing.Awaitable[job_service.ListDataLabelingJobsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def delete_data_labeling_job(
        self,
    ) -> typing.Callable[
        [job_service.DeleteDataLabelingJobRequest],
        typing.Union[operations.Operation, typing.Awaitable[operations.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def cancel_data_labeling_job(
        self,
    ) -> typing.Callable[
        [job_service.CancelDataLabelingJobRequest],
        typing.Union[empty.Empty, typing.Awaitable[empty.Empty]],
    ]:
        raise NotImplementedError()

    @property
    def create_hyperparameter_tuning_job(
        self,
    ) -> typing.Callable[
        [job_service.CreateHyperparameterTuningJobRequest],
        typing.Union[
            gca_hyperparameter_tuning_job.HyperparameterTuningJob,
            typing.Awaitable[gca_hyperparameter_tuning_job.HyperparameterTuningJob],
        ],
    ]:
        raise NotImplementedError()

    @property
    def get_hyperparameter_tuning_job(
        self,
    ) -> typing.Callable[
        [job_service.GetHyperparameterTuningJobRequest],
        typing.Union[
            hyperparameter_tuning_job.HyperparameterTuningJob,
            typing.Awaitable[hyperparameter_tuning_job.HyperparameterTuningJob],
        ],
    ]:
        raise NotImplementedError()

    @property
    def list_hyperparameter_tuning_jobs(
        self,
    ) -> typing.Callable[
        [job_service.ListHyperparameterTuningJobsRequest],
        typing.Union[
            job_service.ListHyperparameterTuningJobsResponse,
            typing.Awaitable[job_service.ListHyperparameterTuningJobsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def delete_hyperparameter_tuning_job(
        self,
    ) -> typing.Callable[
        [job_service.DeleteHyperparameterTuningJobRequest],
        typing.Union[operations.Operation, typing.Awaitable[operations.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def cancel_hyperparameter_tuning_job(
        self,
    ) -> typing.Callable[
        [job_service.CancelHyperparameterTuningJobRequest],
        typing.Union[empty.Empty, typing.Awaitable[empty.Empty]],
    ]:
        raise NotImplementedError()

    @property
    def create_batch_prediction_job(
        self,
    ) -> typing.Callable[
        [job_service.CreateBatchPredictionJobRequest],
        typing.Union[
            gca_batch_prediction_job.BatchPredictionJob,
            typing.Awaitable[gca_batch_prediction_job.BatchPredictionJob],
        ],
    ]:
        raise NotImplementedError()

    @property
    def get_batch_prediction_job(
        self,
    ) -> typing.Callable[
        [job_service.GetBatchPredictionJobRequest],
        typing.Union[
            batch_prediction_job.BatchPredictionJob,
            typing.Awaitable[batch_prediction_job.BatchPredictionJob],
        ],
    ]:
        raise NotImplementedError()

    @property
    def list_batch_prediction_jobs(
        self,
    ) -> typing.Callable[
        [job_service.ListBatchPredictionJobsRequest],
        typing.Union[
            job_service.ListBatchPredictionJobsResponse,
            typing.Awaitable[job_service.ListBatchPredictionJobsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def delete_batch_prediction_job(
        self,
    ) -> typing.Callable[
        [job_service.DeleteBatchPredictionJobRequest],
        typing.Union[operations.Operation, typing.Awaitable[operations.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def cancel_batch_prediction_job(
        self,
    ) -> typing.Callable[
        [job_service.CancelBatchPredictionJobRequest],
        typing.Union[empty.Empty, typing.Awaitable[empty.Empty]],
    ]:
        raise NotImplementedError()


__all__ = ("JobServiceTransport",)
