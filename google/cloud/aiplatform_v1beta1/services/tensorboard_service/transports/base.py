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
from google.api_core import gapic_v1    # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.api_core import operations_v1  # type: ignore
from google.auth import credentials  # type: ignore

from google.cloud.aiplatform_v1beta1.types import tensorboard
from google.cloud.aiplatform_v1beta1.types import tensorboard_experiment
from google.cloud.aiplatform_v1beta1.types import tensorboard_experiment as gca_tensorboard_experiment
from google.cloud.aiplatform_v1beta1.types import tensorboard_run
from google.cloud.aiplatform_v1beta1.types import tensorboard_run as gca_tensorboard_run
from google.cloud.aiplatform_v1beta1.types import tensorboard_service
from google.cloud.aiplatform_v1beta1.types import tensorboard_time_series
from google.cloud.aiplatform_v1beta1.types import tensorboard_time_series as gca_tensorboard_time_series
from google.longrunning import operations_pb2 as operations  # type: ignore


try:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            'google-cloud-aiplatform',
        ).version,
    )
except pkg_resources.DistributionNotFound:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo()

class TensorboardServiceTransport(abc.ABC):
    """Abstract transport class for TensorboardService."""

    AUTH_SCOPES = (
        'https://www.googleapis.com/auth/cloud-platform',
    )

    def __init__(
            self, *,
            host: str = 'aiplatform.googleapis.com',
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
        if ':' not in host:
            host += ':443'
        self._host = host

        # Save the scopes.
        self._scopes = scopes or self.AUTH_SCOPES

        # If no credentials are provided, then determine the appropriate
        # defaults.
        if credentials and credentials_file:
            raise exceptions.DuplicateCredentialArgs("'credentials_file' and 'credentials' are mutually exclusive")

        if credentials_file is not None:
            credentials, _ = auth.load_credentials_from_file(
                                credentials_file,
                                scopes=self._scopes,
                                quota_project_id=quota_project_id
                            )

        elif credentials is None:
            credentials, _ = auth.default(scopes=self._scopes, quota_project_id=quota_project_id)

        # Save the credentials.
        self._credentials = credentials

    def _prep_wrapped_messages(self, client_info):
        # Precompute the wrapped methods.
        self._wrapped_methods = {
            self.create_tensorboard: gapic_v1.method.wrap_method(
                self.create_tensorboard,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_tensorboard: gapic_v1.method.wrap_method(
                self.get_tensorboard,
                default_timeout=None,
                client_info=client_info,
            ),
            self.update_tensorboard: gapic_v1.method.wrap_method(
                self.update_tensorboard,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_tensorboards: gapic_v1.method.wrap_method(
                self.list_tensorboards,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_tensorboard: gapic_v1.method.wrap_method(
                self.delete_tensorboard,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_tensorboard_experiment: gapic_v1.method.wrap_method(
                self.create_tensorboard_experiment,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_tensorboard_experiment: gapic_v1.method.wrap_method(
                self.get_tensorboard_experiment,
                default_timeout=None,
                client_info=client_info,
            ),
            self.update_tensorboard_experiment: gapic_v1.method.wrap_method(
                self.update_tensorboard_experiment,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_tensorboard_experiments: gapic_v1.method.wrap_method(
                self.list_tensorboard_experiments,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_tensorboard_experiment: gapic_v1.method.wrap_method(
                self.delete_tensorboard_experiment,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_tensorboard_run: gapic_v1.method.wrap_method(
                self.create_tensorboard_run,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_tensorboard_run: gapic_v1.method.wrap_method(
                self.get_tensorboard_run,
                default_timeout=None,
                client_info=client_info,
            ),
            self.update_tensorboard_run: gapic_v1.method.wrap_method(
                self.update_tensorboard_run,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_tensorboard_runs: gapic_v1.method.wrap_method(
                self.list_tensorboard_runs,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_tensorboard_run: gapic_v1.method.wrap_method(
                self.delete_tensorboard_run,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_tensorboard_time_series: gapic_v1.method.wrap_method(
                self.create_tensorboard_time_series,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_tensorboard_time_series: gapic_v1.method.wrap_method(
                self.get_tensorboard_time_series,
                default_timeout=None,
                client_info=client_info,
            ),
            self.update_tensorboard_time_series: gapic_v1.method.wrap_method(
                self.update_tensorboard_time_series,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_tensorboard_time_series: gapic_v1.method.wrap_method(
                self.list_tensorboard_time_series,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_tensorboard_time_series: gapic_v1.method.wrap_method(
                self.delete_tensorboard_time_series,
                default_timeout=None,
                client_info=client_info,
            ),
            self.read_tensorboard_time_series_data: gapic_v1.method.wrap_method(
                self.read_tensorboard_time_series_data,
                default_timeout=None,
                client_info=client_info,
            ),
            self.read_tensorboard_blob_data: gapic_v1.method.wrap_method(
                self.read_tensorboard_blob_data,
                default_timeout=None,
                client_info=client_info,
            ),
            self.write_tensorboard_run_data: gapic_v1.method.wrap_method(
                self.write_tensorboard_run_data,
                default_timeout=None,
                client_info=client_info,
            ),
            self.export_tensorboard_time_series_data: gapic_v1.method.wrap_method(
                self.export_tensorboard_time_series_data,
                default_timeout=None,
                client_info=client_info,
            ),

        }

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Return the client designed to process long-running operations."""
        raise NotImplementedError()

    @property
    def create_tensorboard(self) -> typing.Callable[
            [tensorboard_service.CreateTensorboardRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def get_tensorboard(self) -> typing.Callable[
            [tensorboard_service.GetTensorboardRequest],
            typing.Union[
                tensorboard.Tensorboard,
                typing.Awaitable[tensorboard.Tensorboard]
            ]]:
        raise NotImplementedError()

    @property
    def update_tensorboard(self) -> typing.Callable[
            [tensorboard_service.UpdateTensorboardRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def list_tensorboards(self) -> typing.Callable[
            [tensorboard_service.ListTensorboardsRequest],
            typing.Union[
                tensorboard_service.ListTensorboardsResponse,
                typing.Awaitable[tensorboard_service.ListTensorboardsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def delete_tensorboard(self) -> typing.Callable[
            [tensorboard_service.DeleteTensorboardRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def create_tensorboard_experiment(self) -> typing.Callable[
            [tensorboard_service.CreateTensorboardExperimentRequest],
            typing.Union[
                gca_tensorboard_experiment.TensorboardExperiment,
                typing.Awaitable[gca_tensorboard_experiment.TensorboardExperiment]
            ]]:
        raise NotImplementedError()

    @property
    def get_tensorboard_experiment(self) -> typing.Callable[
            [tensorboard_service.GetTensorboardExperimentRequest],
            typing.Union[
                tensorboard_experiment.TensorboardExperiment,
                typing.Awaitable[tensorboard_experiment.TensorboardExperiment]
            ]]:
        raise NotImplementedError()

    @property
    def update_tensorboard_experiment(self) -> typing.Callable[
            [tensorboard_service.UpdateTensorboardExperimentRequest],
            typing.Union[
                gca_tensorboard_experiment.TensorboardExperiment,
                typing.Awaitable[gca_tensorboard_experiment.TensorboardExperiment]
            ]]:
        raise NotImplementedError()

    @property
    def list_tensorboard_experiments(self) -> typing.Callable[
            [tensorboard_service.ListTensorboardExperimentsRequest],
            typing.Union[
                tensorboard_service.ListTensorboardExperimentsResponse,
                typing.Awaitable[tensorboard_service.ListTensorboardExperimentsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def delete_tensorboard_experiment(self) -> typing.Callable[
            [tensorboard_service.DeleteTensorboardExperimentRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def create_tensorboard_run(self) -> typing.Callable[
            [tensorboard_service.CreateTensorboardRunRequest],
            typing.Union[
                gca_tensorboard_run.TensorboardRun,
                typing.Awaitable[gca_tensorboard_run.TensorboardRun]
            ]]:
        raise NotImplementedError()

    @property
    def get_tensorboard_run(self) -> typing.Callable[
            [tensorboard_service.GetTensorboardRunRequest],
            typing.Union[
                tensorboard_run.TensorboardRun,
                typing.Awaitable[tensorboard_run.TensorboardRun]
            ]]:
        raise NotImplementedError()

    @property
    def update_tensorboard_run(self) -> typing.Callable[
            [tensorboard_service.UpdateTensorboardRunRequest],
            typing.Union[
                gca_tensorboard_run.TensorboardRun,
                typing.Awaitable[gca_tensorboard_run.TensorboardRun]
            ]]:
        raise NotImplementedError()

    @property
    def list_tensorboard_runs(self) -> typing.Callable[
            [tensorboard_service.ListTensorboardRunsRequest],
            typing.Union[
                tensorboard_service.ListTensorboardRunsResponse,
                typing.Awaitable[tensorboard_service.ListTensorboardRunsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def delete_tensorboard_run(self) -> typing.Callable[
            [tensorboard_service.DeleteTensorboardRunRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def create_tensorboard_time_series(self) -> typing.Callable[
            [tensorboard_service.CreateTensorboardTimeSeriesRequest],
            typing.Union[
                gca_tensorboard_time_series.TensorboardTimeSeries,
                typing.Awaitable[gca_tensorboard_time_series.TensorboardTimeSeries]
            ]]:
        raise NotImplementedError()

    @property
    def get_tensorboard_time_series(self) -> typing.Callable[
            [tensorboard_service.GetTensorboardTimeSeriesRequest],
            typing.Union[
                tensorboard_time_series.TensorboardTimeSeries,
                typing.Awaitable[tensorboard_time_series.TensorboardTimeSeries]
            ]]:
        raise NotImplementedError()

    @property
    def update_tensorboard_time_series(self) -> typing.Callable[
            [tensorboard_service.UpdateTensorboardTimeSeriesRequest],
            typing.Union[
                gca_tensorboard_time_series.TensorboardTimeSeries,
                typing.Awaitable[gca_tensorboard_time_series.TensorboardTimeSeries]
            ]]:
        raise NotImplementedError()

    @property
    def list_tensorboard_time_series(self) -> typing.Callable[
            [tensorboard_service.ListTensorboardTimeSeriesRequest],
            typing.Union[
                tensorboard_service.ListTensorboardTimeSeriesResponse,
                typing.Awaitable[tensorboard_service.ListTensorboardTimeSeriesResponse]
            ]]:
        raise NotImplementedError()

    @property
    def delete_tensorboard_time_series(self) -> typing.Callable[
            [tensorboard_service.DeleteTensorboardTimeSeriesRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def read_tensorboard_time_series_data(self) -> typing.Callable[
            [tensorboard_service.ReadTensorboardTimeSeriesDataRequest],
            typing.Union[
                tensorboard_service.ReadTensorboardTimeSeriesDataResponse,
                typing.Awaitable[tensorboard_service.ReadTensorboardTimeSeriesDataResponse]
            ]]:
        raise NotImplementedError()

    @property
    def read_tensorboard_blob_data(self) -> typing.Callable[
            [tensorboard_service.ReadTensorboardBlobDataRequest],
            typing.Union[
                tensorboard_service.ReadTensorboardBlobDataResponse,
                typing.Awaitable[tensorboard_service.ReadTensorboardBlobDataResponse]
            ]]:
        raise NotImplementedError()

    @property
    def write_tensorboard_run_data(self) -> typing.Callable[
            [tensorboard_service.WriteTensorboardRunDataRequest],
            typing.Union[
                tensorboard_service.WriteTensorboardRunDataResponse,
                typing.Awaitable[tensorboard_service.WriteTensorboardRunDataResponse]
            ]]:
        raise NotImplementedError()

    @property
    def export_tensorboard_time_series_data(self) -> typing.Callable[
            [tensorboard_service.ExportTensorboardTimeSeriesDataRequest],
            typing.Union[
                tensorboard_service.ExportTensorboardTimeSeriesDataResponse,
                typing.Awaitable[tensorboard_service.ExportTensorboardTimeSeriesDataResponse]
            ]]:
        raise NotImplementedError()


__all__ = (
    'TensorboardServiceTransport',
)
