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
import warnings
from typing import Callable, Dict, Optional, Sequence, Tuple, Union

from google.api_core import grpc_helpers  # type: ignore
from google.api_core import operations_v1  # type: ignore
from google.api_core import gapic_v1  # type: ignore
import google.auth  # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore
from google.auth.transport.grpc import SslCredentials  # type: ignore

import grpc  # type: ignore

from google.cloud.aiplatform_v1beta1.types import study
from google.cloud.aiplatform_v1beta1.types import study as gca_study
from google.cloud.aiplatform_v1beta1.types import vizier_service
from google.longrunning import operations_pb2  # type: ignore
from google.protobuf import empty_pb2  # type: ignore
from .base import VizierServiceTransport, DEFAULT_CLIENT_INFO


class VizierServiceGrpcTransport(VizierServiceTransport):
    """gRPC backend transport for VizierService.

    Cloud AI Platform Vizier API.
    Vizier service is a GCP service to solve blackbox optimization
    problems, such as tuning machine learning hyperparameters and
    searching over deep learning architectures.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends protocol buffers over the wire using gRPC (which is built on
    top of HTTP/2); the ``grpcio`` package must be installed.
    """

    _stubs: Dict[str, Callable]

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: ga_credentials.Credentials = None,
        credentials_file: str = None,
        scopes: Sequence[str] = None,
        channel: grpc.Channel = None,
        api_mtls_endpoint: str = None,
        client_cert_source: Callable[[], Tuple[bytes, bytes]] = None,
        ssl_channel_credentials: grpc.ChannelCredentials = None,
        client_cert_source_for_mtls: Callable[[], Tuple[bytes, bytes]] = None,
        quota_project_id: Optional[str] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]):
                 The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
                This argument is ignored if ``channel`` is provided.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is ignored if ``channel`` is provided.
            scopes (Optional(Sequence[str])): A list of scopes. This argument is
                ignored if ``channel`` is provided.
            channel (Optional[grpc.Channel]): A ``Channel`` instance through
                which to make calls.
            api_mtls_endpoint (Optional[str]): Deprecated. The mutual TLS endpoint.
                If provided, it overrides the ``host`` argument and tries to create
                a mutual TLS channel with client SSL credentials from
                ``client_cert_source`` or applicatin default SSL credentials.
            client_cert_source (Optional[Callable[[], Tuple[bytes, bytes]]]):
                Deprecated. A callback to provide client SSL certificate bytes and
                private key bytes, both in PEM format. It is ignored if
                ``api_mtls_endpoint`` is None.
            ssl_channel_credentials (grpc.ChannelCredentials): SSL credentials
                for grpc channel. It is ignored if ``channel`` is provided.
            client_cert_source_for_mtls (Optional[Callable[[], Tuple[bytes, bytes]]]):
                A callback to provide client certificate bytes and private key bytes,
                both in PEM format. It is used to configure mutual TLS channel. It is
                ignored if ``channel`` or ``ssl_channel_credentials`` is provided.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.

        Raises:
          google.auth.exceptions.MutualTLSChannelError: If mutual TLS transport
              creation failed for any reason.
          google.api_core.exceptions.DuplicateCredentialArgs: If both ``credentials``
              and ``credentials_file`` are passed.
        """
        self._grpc_channel = None
        self._ssl_channel_credentials = ssl_channel_credentials
        self._stubs: Dict[str, Callable] = {}
        self._operations_client = None

        if api_mtls_endpoint:
            warnings.warn("api_mtls_endpoint is deprecated", DeprecationWarning)
        if client_cert_source:
            warnings.warn("client_cert_source is deprecated", DeprecationWarning)

        if channel:
            # Ignore credentials if a channel was passed.
            credentials = False
            # If a channel was explicitly provided, set it.
            self._grpc_channel = channel
            self._ssl_channel_credentials = None

        else:
            if api_mtls_endpoint:
                host = api_mtls_endpoint

                # Create SSL credentials with client_cert_source or application
                # default SSL credentials.
                if client_cert_source:
                    cert, key = client_cert_source()
                    self._ssl_channel_credentials = grpc.ssl_channel_credentials(
                        certificate_chain=cert, private_key=key
                    )
                else:
                    self._ssl_channel_credentials = SslCredentials().ssl_credentials

            else:
                if client_cert_source_for_mtls and not ssl_channel_credentials:
                    cert, key = client_cert_source_for_mtls()
                    self._ssl_channel_credentials = grpc.ssl_channel_credentials(
                        certificate_chain=cert, private_key=key
                    )

        # The base transport sets the host, credentials and scopes
        super().__init__(
            host=host,
            credentials=credentials,
            credentials_file=credentials_file,
            scopes=scopes,
            quota_project_id=quota_project_id,
            client_info=client_info,
        )

        if not self._grpc_channel:
            self._grpc_channel = type(self).create_channel(
                self._host,
                credentials=self._credentials,
                credentials_file=credentials_file,
                scopes=self._scopes,
                ssl_credentials=self._ssl_channel_credentials,
                quota_project_id=quota_project_id,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )

        # Wrap messages. This must be done after self._grpc_channel exists
        self._prep_wrapped_messages(client_info)

    @classmethod
    def create_channel(
        cls,
        host: str = "aiplatform.googleapis.com",
        credentials: ga_credentials.Credentials = None,
        credentials_file: str = None,
        scopes: Optional[Sequence[str]] = None,
        quota_project_id: Optional[str] = None,
        **kwargs,
    ) -> grpc.Channel:
        """Create and return a gRPC channel object.
        Args:
            host (Optional[str]): The host for the channel to use.
            credentials (Optional[~.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify this application to the service. If
                none are specified, the client will attempt to ascertain
                the credentials from the environment.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is mutually exclusive with credentials.
            scopes (Optional[Sequence[str]]): A optional list of scopes needed for this
                service. These are only used when credentials are not specified and
                are passed to :func:`google.auth.default`.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            kwargs (Optional[dict]): Keyword arguments, which are passed to the
                channel creation.
        Returns:
            grpc.Channel: A gRPC channel object.

        Raises:
            google.api_core.exceptions.DuplicateCredentialArgs: If both ``credentials``
              and ``credentials_file`` are passed.
        """

        self_signed_jwt_kwargs = cls._get_self_signed_jwt_kwargs(host, scopes)

        return grpc_helpers.create_channel(
            host,
            credentials=credentials,
            credentials_file=credentials_file,
            quota_project_id=quota_project_id,
            **self_signed_jwt_kwargs,
            **kwargs,
        )

    @property
    def grpc_channel(self) -> grpc.Channel:
        """Return the channel designed to connect to this service.
        """
        return self._grpc_channel

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Create the client designed to process long-running operations.

        This property caches on the instance; repeated calls return the same
        client.
        """
        # Sanity check: Only create a new client if we do not already have one.
        if self._operations_client is None:
            self._operations_client = operations_v1.OperationsClient(self.grpc_channel)

        # Return the client from cache.
        return self._operations_client

    @property
    def create_study(
        self,
    ) -> Callable[[vizier_service.CreateStudyRequest], gca_study.Study]:
        r"""Return a callable for the create study method over gRPC.

        Creates a Study. A resource name will be generated
        after creation of the Study.

        Returns:
            Callable[[~.CreateStudyRequest],
                    ~.Study]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_study" not in self._stubs:
            self._stubs["create_study"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/CreateStudy",
                request_serializer=vizier_service.CreateStudyRequest.serialize,
                response_deserializer=gca_study.Study.deserialize,
            )
        return self._stubs["create_study"]

    @property
    def get_study(self) -> Callable[[vizier_service.GetStudyRequest], study.Study]:
        r"""Return a callable for the get study method over gRPC.

        Gets a Study by name.

        Returns:
            Callable[[~.GetStudyRequest],
                    ~.Study]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_study" not in self._stubs:
            self._stubs["get_study"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/GetStudy",
                request_serializer=vizier_service.GetStudyRequest.serialize,
                response_deserializer=study.Study.deserialize,
            )
        return self._stubs["get_study"]

    @property
    def list_studies(
        self,
    ) -> Callable[
        [vizier_service.ListStudiesRequest], vizier_service.ListStudiesResponse
    ]:
        r"""Return a callable for the list studies method over gRPC.

        Lists all the studies in a region for an associated
        project.

        Returns:
            Callable[[~.ListStudiesRequest],
                    ~.ListStudiesResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_studies" not in self._stubs:
            self._stubs["list_studies"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/ListStudies",
                request_serializer=vizier_service.ListStudiesRequest.serialize,
                response_deserializer=vizier_service.ListStudiesResponse.deserialize,
            )
        return self._stubs["list_studies"]

    @property
    def delete_study(
        self,
    ) -> Callable[[vizier_service.DeleteStudyRequest], empty_pb2.Empty]:
        r"""Return a callable for the delete study method over gRPC.

        Deletes a Study.

        Returns:
            Callable[[~.DeleteStudyRequest],
                    ~.Empty]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_study" not in self._stubs:
            self._stubs["delete_study"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/DeleteStudy",
                request_serializer=vizier_service.DeleteStudyRequest.serialize,
                response_deserializer=empty_pb2.Empty.FromString,
            )
        return self._stubs["delete_study"]

    @property
    def lookup_study(
        self,
    ) -> Callable[[vizier_service.LookupStudyRequest], study.Study]:
        r"""Return a callable for the lookup study method over gRPC.

        Looks a study up using the user-defined display_name field
        instead of the fully qualified resource name.

        Returns:
            Callable[[~.LookupStudyRequest],
                    ~.Study]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "lookup_study" not in self._stubs:
            self._stubs["lookup_study"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/LookupStudy",
                request_serializer=vizier_service.LookupStudyRequest.serialize,
                response_deserializer=study.Study.deserialize,
            )
        return self._stubs["lookup_study"]

    @property
    def suggest_trials(
        self,
    ) -> Callable[[vizier_service.SuggestTrialsRequest], operations_pb2.Operation]:
        r"""Return a callable for the suggest trials method over gRPC.

        Adds one or more Trials to a Study, with parameter values
        suggested by AI Platform Vizier. Returns a long-running
        operation associated with the generation of Trial suggestions.
        When this long-running operation succeeds, it will contain a
        [SuggestTrialsResponse][google.cloud.ml.v1.SuggestTrialsResponse].

        Returns:
            Callable[[~.SuggestTrialsRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "suggest_trials" not in self._stubs:
            self._stubs["suggest_trials"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/SuggestTrials",
                request_serializer=vizier_service.SuggestTrialsRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs["suggest_trials"]

    @property
    def create_trial(
        self,
    ) -> Callable[[vizier_service.CreateTrialRequest], study.Trial]:
        r"""Return a callable for the create trial method over gRPC.

        Adds a user provided Trial to a Study.

        Returns:
            Callable[[~.CreateTrialRequest],
                    ~.Trial]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_trial" not in self._stubs:
            self._stubs["create_trial"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/CreateTrial",
                request_serializer=vizier_service.CreateTrialRequest.serialize,
                response_deserializer=study.Trial.deserialize,
            )
        return self._stubs["create_trial"]

    @property
    def get_trial(self) -> Callable[[vizier_service.GetTrialRequest], study.Trial]:
        r"""Return a callable for the get trial method over gRPC.

        Gets a Trial.

        Returns:
            Callable[[~.GetTrialRequest],
                    ~.Trial]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_trial" not in self._stubs:
            self._stubs["get_trial"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/GetTrial",
                request_serializer=vizier_service.GetTrialRequest.serialize,
                response_deserializer=study.Trial.deserialize,
            )
        return self._stubs["get_trial"]

    @property
    def list_trials(
        self,
    ) -> Callable[
        [vizier_service.ListTrialsRequest], vizier_service.ListTrialsResponse
    ]:
        r"""Return a callable for the list trials method over gRPC.

        Lists the Trials associated with a Study.

        Returns:
            Callable[[~.ListTrialsRequest],
                    ~.ListTrialsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_trials" not in self._stubs:
            self._stubs["list_trials"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/ListTrials",
                request_serializer=vizier_service.ListTrialsRequest.serialize,
                response_deserializer=vizier_service.ListTrialsResponse.deserialize,
            )
        return self._stubs["list_trials"]

    @property
    def add_trial_measurement(
        self,
    ) -> Callable[[vizier_service.AddTrialMeasurementRequest], study.Trial]:
        r"""Return a callable for the add trial measurement method over gRPC.

        Adds a measurement of the objective metrics to a
        Trial. This measurement is assumed to have been taken
        before the Trial is complete.

        Returns:
            Callable[[~.AddTrialMeasurementRequest],
                    ~.Trial]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "add_trial_measurement" not in self._stubs:
            self._stubs["add_trial_measurement"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/AddTrialMeasurement",
                request_serializer=vizier_service.AddTrialMeasurementRequest.serialize,
                response_deserializer=study.Trial.deserialize,
            )
        return self._stubs["add_trial_measurement"]

    @property
    def complete_trial(
        self,
    ) -> Callable[[vizier_service.CompleteTrialRequest], study.Trial]:
        r"""Return a callable for the complete trial method over gRPC.

        Marks a Trial as complete.

        Returns:
            Callable[[~.CompleteTrialRequest],
                    ~.Trial]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "complete_trial" not in self._stubs:
            self._stubs["complete_trial"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/CompleteTrial",
                request_serializer=vizier_service.CompleteTrialRequest.serialize,
                response_deserializer=study.Trial.deserialize,
            )
        return self._stubs["complete_trial"]

    @property
    def delete_trial(
        self,
    ) -> Callable[[vizier_service.DeleteTrialRequest], empty_pb2.Empty]:
        r"""Return a callable for the delete trial method over gRPC.

        Deletes a Trial.

        Returns:
            Callable[[~.DeleteTrialRequest],
                    ~.Empty]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_trial" not in self._stubs:
            self._stubs["delete_trial"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/DeleteTrial",
                request_serializer=vizier_service.DeleteTrialRequest.serialize,
                response_deserializer=empty_pb2.Empty.FromString,
            )
        return self._stubs["delete_trial"]

    @property
    def check_trial_early_stopping_state(
        self,
    ) -> Callable[
        [vizier_service.CheckTrialEarlyStoppingStateRequest], operations_pb2.Operation
    ]:
        r"""Return a callable for the check trial early stopping
        state method over gRPC.

        Checks whether a Trial should stop or not. Returns a
        long-running operation. When the operation is successful, it
        will contain a
        [CheckTrialEarlyStoppingStateResponse][google.cloud.ml.v1.CheckTrialEarlyStoppingStateResponse].

        Returns:
            Callable[[~.CheckTrialEarlyStoppingStateRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "check_trial_early_stopping_state" not in self._stubs:
            self._stubs[
                "check_trial_early_stopping_state"
            ] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/CheckTrialEarlyStoppingState",
                request_serializer=vizier_service.CheckTrialEarlyStoppingStateRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs["check_trial_early_stopping_state"]

    @property
    def stop_trial(self) -> Callable[[vizier_service.StopTrialRequest], study.Trial]:
        r"""Return a callable for the stop trial method over gRPC.

        Stops a Trial.

        Returns:
            Callable[[~.StopTrialRequest],
                    ~.Trial]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "stop_trial" not in self._stubs:
            self._stubs["stop_trial"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/StopTrial",
                request_serializer=vizier_service.StopTrialRequest.serialize,
                response_deserializer=study.Trial.deserialize,
            )
        return self._stubs["stop_trial"]

    @property
    def list_optimal_trials(
        self,
    ) -> Callable[
        [vizier_service.ListOptimalTrialsRequest],
        vizier_service.ListOptimalTrialsResponse,
    ]:
        r"""Return a callable for the list optimal trials method over gRPC.

        Lists the pareto-optimal Trials for multi-objective Study or the
        optimal Trials for single-objective Study. The definition of
        pareto-optimal can be checked in wiki page.
        https://en.wikipedia.org/wiki/Pareto_efficiency

        Returns:
            Callable[[~.ListOptimalTrialsRequest],
                    ~.ListOptimalTrialsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_optimal_trials" not in self._stubs:
            self._stubs["list_optimal_trials"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.VizierService/ListOptimalTrials",
                request_serializer=vizier_service.ListOptimalTrialsRequest.serialize,
                response_deserializer=vizier_service.ListOptimalTrialsResponse.deserialize,
            )
        return self._stubs["list_optimal_trials"]


__all__ = ("VizierServiceGrpcTransport",)
