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

from google.cloud.aiplatform_v1beta1.types import study
from google.cloud.aiplatform_v1beta1.types import study as gca_study
from google.cloud.aiplatform_v1beta1.types import vizier_service
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


class VizierServiceTransport(abc.ABC):
    """Abstract transport class for VizierService."""

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
            self.create_study: gapic_v1.method.wrap_method(
                self.create_study, default_timeout=5.0, client_info=client_info,
            ),
            self.get_study: gapic_v1.method.wrap_method(
                self.get_study, default_timeout=5.0, client_info=client_info,
            ),
            self.list_studies: gapic_v1.method.wrap_method(
                self.list_studies, default_timeout=5.0, client_info=client_info,
            ),
            self.delete_study: gapic_v1.method.wrap_method(
                self.delete_study, default_timeout=5.0, client_info=client_info,
            ),
            self.lookup_study: gapic_v1.method.wrap_method(
                self.lookup_study, default_timeout=5.0, client_info=client_info,
            ),
            self.suggest_trials: gapic_v1.method.wrap_method(
                self.suggest_trials, default_timeout=5.0, client_info=client_info,
            ),
            self.create_trial: gapic_v1.method.wrap_method(
                self.create_trial, default_timeout=5.0, client_info=client_info,
            ),
            self.get_trial: gapic_v1.method.wrap_method(
                self.get_trial, default_timeout=5.0, client_info=client_info,
            ),
            self.list_trials: gapic_v1.method.wrap_method(
                self.list_trials, default_timeout=5.0, client_info=client_info,
            ),
            self.add_trial_measurement: gapic_v1.method.wrap_method(
                self.add_trial_measurement,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.complete_trial: gapic_v1.method.wrap_method(
                self.complete_trial, default_timeout=5.0, client_info=client_info,
            ),
            self.delete_trial: gapic_v1.method.wrap_method(
                self.delete_trial, default_timeout=5.0, client_info=client_info,
            ),
            self.check_trial_early_stopping_state: gapic_v1.method.wrap_method(
                self.check_trial_early_stopping_state,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.stop_trial: gapic_v1.method.wrap_method(
                self.stop_trial, default_timeout=5.0, client_info=client_info,
            ),
            self.list_optimal_trials: gapic_v1.method.wrap_method(
                self.list_optimal_trials, default_timeout=5.0, client_info=client_info,
            ),
        }

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Return the client designed to process long-running operations."""
        raise NotImplementedError()

    @property
    def create_study(
        self,
    ) -> typing.Callable[
        [vizier_service.CreateStudyRequest],
        typing.Union[gca_study.Study, typing.Awaitable[gca_study.Study]],
    ]:
        raise NotImplementedError()

    @property
    def get_study(
        self,
    ) -> typing.Callable[
        [vizier_service.GetStudyRequest],
        typing.Union[study.Study, typing.Awaitable[study.Study]],
    ]:
        raise NotImplementedError()

    @property
    def list_studies(
        self,
    ) -> typing.Callable[
        [vizier_service.ListStudiesRequest],
        typing.Union[
            vizier_service.ListStudiesResponse,
            typing.Awaitable[vizier_service.ListStudiesResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def delete_study(
        self,
    ) -> typing.Callable[
        [vizier_service.DeleteStudyRequest],
        typing.Union[empty.Empty, typing.Awaitable[empty.Empty]],
    ]:
        raise NotImplementedError()

    @property
    def lookup_study(
        self,
    ) -> typing.Callable[
        [vizier_service.LookupStudyRequest],
        typing.Union[study.Study, typing.Awaitable[study.Study]],
    ]:
        raise NotImplementedError()

    @property
    def suggest_trials(
        self,
    ) -> typing.Callable[
        [vizier_service.SuggestTrialsRequest],
        typing.Union[operations.Operation, typing.Awaitable[operations.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def create_trial(
        self,
    ) -> typing.Callable[
        [vizier_service.CreateTrialRequest],
        typing.Union[study.Trial, typing.Awaitable[study.Trial]],
    ]:
        raise NotImplementedError()

    @property
    def get_trial(
        self,
    ) -> typing.Callable[
        [vizier_service.GetTrialRequest],
        typing.Union[study.Trial, typing.Awaitable[study.Trial]],
    ]:
        raise NotImplementedError()

    @property
    def list_trials(
        self,
    ) -> typing.Callable[
        [vizier_service.ListTrialsRequest],
        typing.Union[
            vizier_service.ListTrialsResponse,
            typing.Awaitable[vizier_service.ListTrialsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def add_trial_measurement(
        self,
    ) -> typing.Callable[
        [vizier_service.AddTrialMeasurementRequest],
        typing.Union[study.Trial, typing.Awaitable[study.Trial]],
    ]:
        raise NotImplementedError()

    @property
    def complete_trial(
        self,
    ) -> typing.Callable[
        [vizier_service.CompleteTrialRequest],
        typing.Union[study.Trial, typing.Awaitable[study.Trial]],
    ]:
        raise NotImplementedError()

    @property
    def delete_trial(
        self,
    ) -> typing.Callable[
        [vizier_service.DeleteTrialRequest],
        typing.Union[empty.Empty, typing.Awaitable[empty.Empty]],
    ]:
        raise NotImplementedError()

    @property
    def check_trial_early_stopping_state(
        self,
    ) -> typing.Callable[
        [vizier_service.CheckTrialEarlyStoppingStateRequest],
        typing.Union[operations.Operation, typing.Awaitable[operations.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def stop_trial(
        self,
    ) -> typing.Callable[
        [vizier_service.StopTrialRequest],
        typing.Union[study.Trial, typing.Awaitable[study.Trial]],
    ]:
        raise NotImplementedError()

    @property
    def list_optimal_trials(
        self,
    ) -> typing.Callable[
        [vizier_service.ListOptimalTrialsRequest],
        typing.Union[
            vizier_service.ListOptimalTrialsResponse,
            typing.Awaitable[vizier_service.ListOptimalTrialsResponse],
        ],
    ]:
        raise NotImplementedError()


__all__ = ("VizierServiceTransport",)
