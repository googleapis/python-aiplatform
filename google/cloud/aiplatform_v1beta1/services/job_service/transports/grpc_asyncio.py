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
from typing import Awaitable, Callable, Dict, Optional, Sequence, Tuple

from google.api_core import gapic_v1  # type: ignore
from google.api_core import grpc_helpers_async  # type: ignore
from google.api_core import operations_v1  # type: ignore
from google import auth  # type: ignore
from google.auth import credentials  # type: ignore
from google.auth.transport.grpc import SslCredentials  # type: ignore

import grpc  # type: ignore
from grpc.experimental import aio  # type: ignore

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

from .base import JobServiceTransport, DEFAULT_CLIENT_INFO
from .grpc import JobServiceGrpcTransport


class JobServiceGrpcAsyncIOTransport(JobServiceTransport):
    """gRPC AsyncIO backend transport for JobService.

    A service for creating and managing AI Platform's jobs.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends protocol buffers over the wire using gRPC (which is built on
    top of HTTP/2); the ``grpcio`` package must be installed.
    """

    _grpc_channel: aio.Channel
    _stubs: Dict[str, Callable] = {}

    @classmethod
    def create_channel(
        cls,
        host: str = "aiplatform.googleapis.com",
        credentials: credentials.Credentials = None,
        credentials_file: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        quota_project_id: Optional[str] = None,
        **kwargs,
    ) -> aio.Channel:
        """Create and return a gRPC AsyncIO channel object.
        Args:
            address (Optional[str]): The host for the channel to use.
            credentials (Optional[~.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify this application to the service. If
                none are specified, the client will attempt to ascertain
                the credentials from the environment.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is ignored if ``channel`` is provided.
            scopes (Optional[Sequence[str]]): A optional list of scopes needed for this
                service. These are only used when credentials are not specified and
                are passed to :func:`google.auth.default`.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            kwargs (Optional[dict]): Keyword arguments, which are passed to the
                channel creation.
        Returns:
            aio.Channel: A gRPC AsyncIO channel object.
        """
        scopes = scopes or cls.AUTH_SCOPES
        return grpc_helpers_async.create_channel(
            host,
            credentials=credentials,
            credentials_file=credentials_file,
            scopes=scopes,
            quota_project_id=quota_project_id,
            **kwargs,
        )

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: credentials.Credentials = None,
        credentials_file: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        channel: aio.Channel = None,
        api_mtls_endpoint: str = None,
        client_cert_source: Callable[[], Tuple[bytes, bytes]] = None,
        ssl_channel_credentials: grpc.ChannelCredentials = None,
        client_cert_source_for_mtls: Callable[[], Tuple[bytes, bytes]] = None,
        quota_project_id=None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]): The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
                This argument is ignored if ``channel`` is provided.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is ignored if ``channel`` is provided.
            scopes (Optional[Sequence[str]]): A optional list of scopes needed for this
                service. These are only used when credentials are not specified and
                are passed to :func:`google.auth.default`.
            channel (Optional[aio.Channel]): A ``Channel`` instance through
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
            google.auth.exceptions.MutualTlsChannelError: If mutual TLS transport
              creation failed for any reason.
          google.api_core.exceptions.DuplicateCredentialArgs: If both ``credentials``
              and ``credentials_file`` are passed.
        """
        self._ssl_channel_credentials = ssl_channel_credentials

        if api_mtls_endpoint:
            warnings.warn("api_mtls_endpoint is deprecated", DeprecationWarning)
        if client_cert_source:
            warnings.warn("client_cert_source is deprecated", DeprecationWarning)

        if channel:
            # Sanity check: Ensure that channel and credentials are not both
            # provided.
            credentials = False

            # If a channel was explicitly provided, set it.
            self._grpc_channel = channel
            self._ssl_channel_credentials = None
        elif api_mtls_endpoint:
            host = (
                api_mtls_endpoint
                if ":" in api_mtls_endpoint
                else api_mtls_endpoint + ":443"
            )

            if credentials is None:
                credentials, _ = auth.default(
                    scopes=self.AUTH_SCOPES, quota_project_id=quota_project_id
                )

            # Create SSL credentials with client_cert_source or application
            # default SSL credentials.
            if client_cert_source:
                cert, key = client_cert_source()
                ssl_credentials = grpc.ssl_channel_credentials(
                    certificate_chain=cert, private_key=key
                )
            else:
                ssl_credentials = SslCredentials().ssl_credentials

            # create a new channel. The provided one is ignored.
            self._grpc_channel = type(self).create_channel(
                host,
                credentials=credentials,
                credentials_file=credentials_file,
                ssl_credentials=ssl_credentials,
                scopes=scopes or self.AUTH_SCOPES,
                quota_project_id=quota_project_id,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            self._ssl_channel_credentials = ssl_credentials
        else:
            host = host if ":" in host else host + ":443"

            if credentials is None:
                credentials, _ = auth.default(
                    scopes=self.AUTH_SCOPES, quota_project_id=quota_project_id
                )

            if client_cert_source_for_mtls and not ssl_channel_credentials:
                cert, key = client_cert_source_for_mtls()
                self._ssl_channel_credentials = grpc.ssl_channel_credentials(
                    certificate_chain=cert, private_key=key
                )

            # create a new channel. The provided one is ignored.
            self._grpc_channel = type(self).create_channel(
                host,
                credentials=credentials,
                credentials_file=credentials_file,
                ssl_credentials=self._ssl_channel_credentials,
                scopes=scopes or self.AUTH_SCOPES,
                quota_project_id=quota_project_id,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )

        # Run the base constructor.
        super().__init__(
            host=host,
            credentials=credentials,
            credentials_file=credentials_file,
            scopes=scopes or self.AUTH_SCOPES,
            quota_project_id=quota_project_id,
            client_info=client_info,
        )

        self._stubs = {}
        self._operations_client = None

    @property
    def grpc_channel(self) -> aio.Channel:
        """Create the channel designed to connect to this service.

        This property caches on the instance; repeated calls return
        the same channel.
        """
        # Return the channel from cache.
        return self._grpc_channel

    @property
    def operations_client(self) -> operations_v1.OperationsAsyncClient:
        """Create the client designed to process long-running operations.

        This property caches on the instance; repeated calls return the same
        client.
        """
        # Sanity check: Only create a new client if we do not already have one.
        if self._operations_client is None:
            self._operations_client = operations_v1.OperationsAsyncClient(
                self.grpc_channel
            )

        # Return the client from cache.
        return self._operations_client

    @property
    def create_custom_job(
        self,
    ) -> Callable[
        [job_service.CreateCustomJobRequest], Awaitable[gca_custom_job.CustomJob]
    ]:
        r"""Return a callable for the create custom job method over gRPC.

        Creates a CustomJob. A created CustomJob right away
        will be attempted to be run.

        Returns:
            Callable[[~.CreateCustomJobRequest],
                    Awaitable[~.CustomJob]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_custom_job" not in self._stubs:
            self._stubs["create_custom_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/CreateCustomJob",
                request_serializer=job_service.CreateCustomJobRequest.serialize,
                response_deserializer=gca_custom_job.CustomJob.deserialize,
            )
        return self._stubs["create_custom_job"]

    @property
    def get_custom_job(
        self,
    ) -> Callable[[job_service.GetCustomJobRequest], Awaitable[custom_job.CustomJob]]:
        r"""Return a callable for the get custom job method over gRPC.

        Gets a CustomJob.

        Returns:
            Callable[[~.GetCustomJobRequest],
                    Awaitable[~.CustomJob]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_custom_job" not in self._stubs:
            self._stubs["get_custom_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/GetCustomJob",
                request_serializer=job_service.GetCustomJobRequest.serialize,
                response_deserializer=custom_job.CustomJob.deserialize,
            )
        return self._stubs["get_custom_job"]

    @property
    def list_custom_jobs(
        self,
    ) -> Callable[
        [job_service.ListCustomJobsRequest],
        Awaitable[job_service.ListCustomJobsResponse],
    ]:
        r"""Return a callable for the list custom jobs method over gRPC.

        Lists CustomJobs in a Location.

        Returns:
            Callable[[~.ListCustomJobsRequest],
                    Awaitable[~.ListCustomJobsResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_custom_jobs" not in self._stubs:
            self._stubs["list_custom_jobs"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/ListCustomJobs",
                request_serializer=job_service.ListCustomJobsRequest.serialize,
                response_deserializer=job_service.ListCustomJobsResponse.deserialize,
            )
        return self._stubs["list_custom_jobs"]

    @property
    def delete_custom_job(
        self,
    ) -> Callable[
        [job_service.DeleteCustomJobRequest], Awaitable[operations.Operation]
    ]:
        r"""Return a callable for the delete custom job method over gRPC.

        Deletes a CustomJob.

        Returns:
            Callable[[~.DeleteCustomJobRequest],
                    Awaitable[~.Operation]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_custom_job" not in self._stubs:
            self._stubs["delete_custom_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/DeleteCustomJob",
                request_serializer=job_service.DeleteCustomJobRequest.serialize,
                response_deserializer=operations.Operation.FromString,
            )
        return self._stubs["delete_custom_job"]

    @property
    def cancel_custom_job(
        self,
    ) -> Callable[[job_service.CancelCustomJobRequest], Awaitable[empty.Empty]]:
        r"""Return a callable for the cancel custom job method over gRPC.

        Cancels a CustomJob. Starts asynchronous cancellation on the
        CustomJob. The server makes a best effort to cancel the job, but
        success is not guaranteed. Clients can use
        ``JobService.GetCustomJob``
        or other methods to check whether the cancellation succeeded or
        whether the job completed despite cancellation. On successful
        cancellation, the CustomJob is not deleted; instead it becomes a
        job with a
        ``CustomJob.error``
        value with a ``google.rpc.Status.code`` of
        1, corresponding to ``Code.CANCELLED``, and
        ``CustomJob.state``
        is set to ``CANCELLED``.

        Returns:
            Callable[[~.CancelCustomJobRequest],
                    Awaitable[~.Empty]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "cancel_custom_job" not in self._stubs:
            self._stubs["cancel_custom_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/CancelCustomJob",
                request_serializer=job_service.CancelCustomJobRequest.serialize,
                response_deserializer=empty.Empty.FromString,
            )
        return self._stubs["cancel_custom_job"]

    @property
    def create_data_labeling_job(
        self,
    ) -> Callable[
        [job_service.CreateDataLabelingJobRequest],
        Awaitable[gca_data_labeling_job.DataLabelingJob],
    ]:
        r"""Return a callable for the create data labeling job method over gRPC.

        Creates a DataLabelingJob.

        Returns:
            Callable[[~.CreateDataLabelingJobRequest],
                    Awaitable[~.DataLabelingJob]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_data_labeling_job" not in self._stubs:
            self._stubs["create_data_labeling_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/CreateDataLabelingJob",
                request_serializer=job_service.CreateDataLabelingJobRequest.serialize,
                response_deserializer=gca_data_labeling_job.DataLabelingJob.deserialize,
            )
        return self._stubs["create_data_labeling_job"]

    @property
    def get_data_labeling_job(
        self,
    ) -> Callable[
        [job_service.GetDataLabelingJobRequest],
        Awaitable[data_labeling_job.DataLabelingJob],
    ]:
        r"""Return a callable for the get data labeling job method over gRPC.

        Gets a DataLabelingJob.

        Returns:
            Callable[[~.GetDataLabelingJobRequest],
                    Awaitable[~.DataLabelingJob]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_data_labeling_job" not in self._stubs:
            self._stubs["get_data_labeling_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/GetDataLabelingJob",
                request_serializer=job_service.GetDataLabelingJobRequest.serialize,
                response_deserializer=data_labeling_job.DataLabelingJob.deserialize,
            )
        return self._stubs["get_data_labeling_job"]

    @property
    def list_data_labeling_jobs(
        self,
    ) -> Callable[
        [job_service.ListDataLabelingJobsRequest],
        Awaitable[job_service.ListDataLabelingJobsResponse],
    ]:
        r"""Return a callable for the list data labeling jobs method over gRPC.

        Lists DataLabelingJobs in a Location.

        Returns:
            Callable[[~.ListDataLabelingJobsRequest],
                    Awaitable[~.ListDataLabelingJobsResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_data_labeling_jobs" not in self._stubs:
            self._stubs["list_data_labeling_jobs"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/ListDataLabelingJobs",
                request_serializer=job_service.ListDataLabelingJobsRequest.serialize,
                response_deserializer=job_service.ListDataLabelingJobsResponse.deserialize,
            )
        return self._stubs["list_data_labeling_jobs"]

    @property
    def delete_data_labeling_job(
        self,
    ) -> Callable[
        [job_service.DeleteDataLabelingJobRequest], Awaitable[operations.Operation]
    ]:
        r"""Return a callable for the delete data labeling job method over gRPC.

        Deletes a DataLabelingJob.

        Returns:
            Callable[[~.DeleteDataLabelingJobRequest],
                    Awaitable[~.Operation]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_data_labeling_job" not in self._stubs:
            self._stubs["delete_data_labeling_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/DeleteDataLabelingJob",
                request_serializer=job_service.DeleteDataLabelingJobRequest.serialize,
                response_deserializer=operations.Operation.FromString,
            )
        return self._stubs["delete_data_labeling_job"]

    @property
    def cancel_data_labeling_job(
        self,
    ) -> Callable[[job_service.CancelDataLabelingJobRequest], Awaitable[empty.Empty]]:
        r"""Return a callable for the cancel data labeling job method over gRPC.

        Cancels a DataLabelingJob. Success of cancellation is
        not guaranteed.

        Returns:
            Callable[[~.CancelDataLabelingJobRequest],
                    Awaitable[~.Empty]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "cancel_data_labeling_job" not in self._stubs:
            self._stubs["cancel_data_labeling_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/CancelDataLabelingJob",
                request_serializer=job_service.CancelDataLabelingJobRequest.serialize,
                response_deserializer=empty.Empty.FromString,
            )
        return self._stubs["cancel_data_labeling_job"]

    @property
    def create_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.CreateHyperparameterTuningJobRequest],
        Awaitable[gca_hyperparameter_tuning_job.HyperparameterTuningJob],
    ]:
        r"""Return a callable for the create hyperparameter tuning
        job method over gRPC.

        Creates a HyperparameterTuningJob

        Returns:
            Callable[[~.CreateHyperparameterTuningJobRequest],
                    Awaitable[~.HyperparameterTuningJob]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_hyperparameter_tuning_job" not in self._stubs:
            self._stubs[
                "create_hyperparameter_tuning_job"
            ] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/CreateHyperparameterTuningJob",
                request_serializer=job_service.CreateHyperparameterTuningJobRequest.serialize,
                response_deserializer=gca_hyperparameter_tuning_job.HyperparameterTuningJob.deserialize,
            )
        return self._stubs["create_hyperparameter_tuning_job"]

    @property
    def get_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.GetHyperparameterTuningJobRequest],
        Awaitable[hyperparameter_tuning_job.HyperparameterTuningJob],
    ]:
        r"""Return a callable for the get hyperparameter tuning job method over gRPC.

        Gets a HyperparameterTuningJob

        Returns:
            Callable[[~.GetHyperparameterTuningJobRequest],
                    Awaitable[~.HyperparameterTuningJob]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_hyperparameter_tuning_job" not in self._stubs:
            self._stubs[
                "get_hyperparameter_tuning_job"
            ] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/GetHyperparameterTuningJob",
                request_serializer=job_service.GetHyperparameterTuningJobRequest.serialize,
                response_deserializer=hyperparameter_tuning_job.HyperparameterTuningJob.deserialize,
            )
        return self._stubs["get_hyperparameter_tuning_job"]

    @property
    def list_hyperparameter_tuning_jobs(
        self,
    ) -> Callable[
        [job_service.ListHyperparameterTuningJobsRequest],
        Awaitable[job_service.ListHyperparameterTuningJobsResponse],
    ]:
        r"""Return a callable for the list hyperparameter tuning
        jobs method over gRPC.

        Lists HyperparameterTuningJobs in a Location.

        Returns:
            Callable[[~.ListHyperparameterTuningJobsRequest],
                    Awaitable[~.ListHyperparameterTuningJobsResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_hyperparameter_tuning_jobs" not in self._stubs:
            self._stubs[
                "list_hyperparameter_tuning_jobs"
            ] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/ListHyperparameterTuningJobs",
                request_serializer=job_service.ListHyperparameterTuningJobsRequest.serialize,
                response_deserializer=job_service.ListHyperparameterTuningJobsResponse.deserialize,
            )
        return self._stubs["list_hyperparameter_tuning_jobs"]

    @property
    def delete_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.DeleteHyperparameterTuningJobRequest],
        Awaitable[operations.Operation],
    ]:
        r"""Return a callable for the delete hyperparameter tuning
        job method over gRPC.

        Deletes a HyperparameterTuningJob.

        Returns:
            Callable[[~.DeleteHyperparameterTuningJobRequest],
                    Awaitable[~.Operation]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_hyperparameter_tuning_job" not in self._stubs:
            self._stubs[
                "delete_hyperparameter_tuning_job"
            ] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/DeleteHyperparameterTuningJob",
                request_serializer=job_service.DeleteHyperparameterTuningJobRequest.serialize,
                response_deserializer=operations.Operation.FromString,
            )
        return self._stubs["delete_hyperparameter_tuning_job"]

    @property
    def cancel_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.CancelHyperparameterTuningJobRequest], Awaitable[empty.Empty]
    ]:
        r"""Return a callable for the cancel hyperparameter tuning
        job method over gRPC.

        Cancels a HyperparameterTuningJob. Starts asynchronous
        cancellation on the HyperparameterTuningJob. The server makes a
        best effort to cancel the job, but success is not guaranteed.
        Clients can use
        ``JobService.GetHyperparameterTuningJob``
        or other methods to check whether the cancellation succeeded or
        whether the job completed despite cancellation. On successful
        cancellation, the HyperparameterTuningJob is not deleted;
        instead it becomes a job with a
        ``HyperparameterTuningJob.error``
        value with a ``google.rpc.Status.code`` of
        1, corresponding to ``Code.CANCELLED``, and
        ``HyperparameterTuningJob.state``
        is set to ``CANCELLED``.

        Returns:
            Callable[[~.CancelHyperparameterTuningJobRequest],
                    Awaitable[~.Empty]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "cancel_hyperparameter_tuning_job" not in self._stubs:
            self._stubs[
                "cancel_hyperparameter_tuning_job"
            ] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/CancelHyperparameterTuningJob",
                request_serializer=job_service.CancelHyperparameterTuningJobRequest.serialize,
                response_deserializer=empty.Empty.FromString,
            )
        return self._stubs["cancel_hyperparameter_tuning_job"]

    @property
    def create_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.CreateBatchPredictionJobRequest],
        Awaitable[gca_batch_prediction_job.BatchPredictionJob],
    ]:
        r"""Return a callable for the create batch prediction job method over gRPC.

        Creates a BatchPredictionJob. A BatchPredictionJob
        once created will right away be attempted to start.

        Returns:
            Callable[[~.CreateBatchPredictionJobRequest],
                    Awaitable[~.BatchPredictionJob]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_batch_prediction_job" not in self._stubs:
            self._stubs["create_batch_prediction_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/CreateBatchPredictionJob",
                request_serializer=job_service.CreateBatchPredictionJobRequest.serialize,
                response_deserializer=gca_batch_prediction_job.BatchPredictionJob.deserialize,
            )
        return self._stubs["create_batch_prediction_job"]

    @property
    def get_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.GetBatchPredictionJobRequest],
        Awaitable[batch_prediction_job.BatchPredictionJob],
    ]:
        r"""Return a callable for the get batch prediction job method over gRPC.

        Gets a BatchPredictionJob

        Returns:
            Callable[[~.GetBatchPredictionJobRequest],
                    Awaitable[~.BatchPredictionJob]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_batch_prediction_job" not in self._stubs:
            self._stubs["get_batch_prediction_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/GetBatchPredictionJob",
                request_serializer=job_service.GetBatchPredictionJobRequest.serialize,
                response_deserializer=batch_prediction_job.BatchPredictionJob.deserialize,
            )
        return self._stubs["get_batch_prediction_job"]

    @property
    def list_batch_prediction_jobs(
        self,
    ) -> Callable[
        [job_service.ListBatchPredictionJobsRequest],
        Awaitable[job_service.ListBatchPredictionJobsResponse],
    ]:
        r"""Return a callable for the list batch prediction jobs method over gRPC.

        Lists BatchPredictionJobs in a Location.

        Returns:
            Callable[[~.ListBatchPredictionJobsRequest],
                    Awaitable[~.ListBatchPredictionJobsResponse]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_batch_prediction_jobs" not in self._stubs:
            self._stubs["list_batch_prediction_jobs"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/ListBatchPredictionJobs",
                request_serializer=job_service.ListBatchPredictionJobsRequest.serialize,
                response_deserializer=job_service.ListBatchPredictionJobsResponse.deserialize,
            )
        return self._stubs["list_batch_prediction_jobs"]

    @property
    def delete_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.DeleteBatchPredictionJobRequest], Awaitable[operations.Operation]
    ]:
        r"""Return a callable for the delete batch prediction job method over gRPC.

        Deletes a BatchPredictionJob. Can only be called on
        jobs that already finished.

        Returns:
            Callable[[~.DeleteBatchPredictionJobRequest],
                    Awaitable[~.Operation]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_batch_prediction_job" not in self._stubs:
            self._stubs["delete_batch_prediction_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/DeleteBatchPredictionJob",
                request_serializer=job_service.DeleteBatchPredictionJobRequest.serialize,
                response_deserializer=operations.Operation.FromString,
            )
        return self._stubs["delete_batch_prediction_job"]

    @property
    def cancel_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.CancelBatchPredictionJobRequest], Awaitable[empty.Empty]
    ]:
        r"""Return a callable for the cancel batch prediction job method over gRPC.

        Cancels a BatchPredictionJob.

        Starts asynchronous cancellation on the BatchPredictionJob. The
        server makes the best effort to cancel the job, but success is
        not guaranteed. Clients can use
        ``JobService.GetBatchPredictionJob``
        or other methods to check whether the cancellation succeeded or
        whether the job completed despite cancellation. On a successful
        cancellation, the BatchPredictionJob is not deleted;instead its
        ``BatchPredictionJob.state``
        is set to ``CANCELLED``. Any files already outputted by the job
        are not deleted.

        Returns:
            Callable[[~.CancelBatchPredictionJobRequest],
                    Awaitable[~.Empty]]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "cancel_batch_prediction_job" not in self._stubs:
            self._stubs["cancel_batch_prediction_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.JobService/CancelBatchPredictionJob",
                request_serializer=job_service.CancelBatchPredictionJobRequest.serialize,
                response_deserializer=empty.Empty.FromString,
            )
        return self._stubs["cancel_batch_prediction_job"]


__all__ = ("JobServiceGrpcAsyncIOTransport",)
