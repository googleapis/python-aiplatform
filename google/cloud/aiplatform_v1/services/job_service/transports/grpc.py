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
from google.longrunning import operations_pb2  # type: ignore
from google.protobuf import empty_pb2  # type: ignore
from .base import JobServiceTransport, DEFAULT_CLIENT_INFO


class JobServiceGrpcTransport(JobServiceTransport):
    """gRPC backend transport for JobService.

    A service for creating and managing AI Platform's jobs.

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
    def create_custom_job(
        self,
    ) -> Callable[[job_service.CreateCustomJobRequest], gca_custom_job.CustomJob]:
        r"""Return a callable for the create custom job method over gRPC.

        Creates a CustomJob. A created CustomJob right away
        will be attempted to be run.

        Returns:
            Callable[[~.CreateCustomJobRequest],
                    ~.CustomJob]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_custom_job" not in self._stubs:
            self._stubs["create_custom_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/CreateCustomJob",
                request_serializer=job_service.CreateCustomJobRequest.serialize,
                response_deserializer=gca_custom_job.CustomJob.deserialize,
            )
        return self._stubs["create_custom_job"]

    @property
    def get_custom_job(
        self,
    ) -> Callable[[job_service.GetCustomJobRequest], custom_job.CustomJob]:
        r"""Return a callable for the get custom job method over gRPC.

        Gets a CustomJob.

        Returns:
            Callable[[~.GetCustomJobRequest],
                    ~.CustomJob]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_custom_job" not in self._stubs:
            self._stubs["get_custom_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/GetCustomJob",
                request_serializer=job_service.GetCustomJobRequest.serialize,
                response_deserializer=custom_job.CustomJob.deserialize,
            )
        return self._stubs["get_custom_job"]

    @property
    def list_custom_jobs(
        self,
    ) -> Callable[
        [job_service.ListCustomJobsRequest], job_service.ListCustomJobsResponse
    ]:
        r"""Return a callable for the list custom jobs method over gRPC.

        Lists CustomJobs in a Location.

        Returns:
            Callable[[~.ListCustomJobsRequest],
                    ~.ListCustomJobsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_custom_jobs" not in self._stubs:
            self._stubs["list_custom_jobs"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/ListCustomJobs",
                request_serializer=job_service.ListCustomJobsRequest.serialize,
                response_deserializer=job_service.ListCustomJobsResponse.deserialize,
            )
        return self._stubs["list_custom_jobs"]

    @property
    def delete_custom_job(
        self,
    ) -> Callable[[job_service.DeleteCustomJobRequest], operations_pb2.Operation]:
        r"""Return a callable for the delete custom job method over gRPC.

        Deletes a CustomJob.

        Returns:
            Callable[[~.DeleteCustomJobRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_custom_job" not in self._stubs:
            self._stubs["delete_custom_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/DeleteCustomJob",
                request_serializer=job_service.DeleteCustomJobRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs["delete_custom_job"]

    @property
    def cancel_custom_job(
        self,
    ) -> Callable[[job_service.CancelCustomJobRequest], empty_pb2.Empty]:
        r"""Return a callable for the cancel custom job method over gRPC.

        Cancels a CustomJob. Starts asynchronous cancellation on the
        CustomJob. The server makes a best effort to cancel the job, but
        success is not guaranteed. Clients can use
        [JobService.GetCustomJob][google.cloud.aiplatform.v1.JobService.GetCustomJob]
        or other methods to check whether the cancellation succeeded or
        whether the job completed despite cancellation. On successful
        cancellation, the CustomJob is not deleted; instead it becomes a
        job with a
        [CustomJob.error][google.cloud.aiplatform.v1.CustomJob.error]
        value with a [google.rpc.Status.code][google.rpc.Status.code] of
        1, corresponding to ``Code.CANCELLED``, and
        [CustomJob.state][google.cloud.aiplatform.v1.CustomJob.state] is
        set to ``CANCELLED``.

        Returns:
            Callable[[~.CancelCustomJobRequest],
                    ~.Empty]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "cancel_custom_job" not in self._stubs:
            self._stubs["cancel_custom_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/CancelCustomJob",
                request_serializer=job_service.CancelCustomJobRequest.serialize,
                response_deserializer=empty_pb2.Empty.FromString,
            )
        return self._stubs["cancel_custom_job"]

    @property
    def create_data_labeling_job(
        self,
    ) -> Callable[
        [job_service.CreateDataLabelingJobRequest],
        gca_data_labeling_job.DataLabelingJob,
    ]:
        r"""Return a callable for the create data labeling job method over gRPC.

        Creates a DataLabelingJob.

        Returns:
            Callable[[~.CreateDataLabelingJobRequest],
                    ~.DataLabelingJob]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_data_labeling_job" not in self._stubs:
            self._stubs["create_data_labeling_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/CreateDataLabelingJob",
                request_serializer=job_service.CreateDataLabelingJobRequest.serialize,
                response_deserializer=gca_data_labeling_job.DataLabelingJob.deserialize,
            )
        return self._stubs["create_data_labeling_job"]

    @property
    def get_data_labeling_job(
        self,
    ) -> Callable[
        [job_service.GetDataLabelingJobRequest], data_labeling_job.DataLabelingJob
    ]:
        r"""Return a callable for the get data labeling job method over gRPC.

        Gets a DataLabelingJob.

        Returns:
            Callable[[~.GetDataLabelingJobRequest],
                    ~.DataLabelingJob]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_data_labeling_job" not in self._stubs:
            self._stubs["get_data_labeling_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/GetDataLabelingJob",
                request_serializer=job_service.GetDataLabelingJobRequest.serialize,
                response_deserializer=data_labeling_job.DataLabelingJob.deserialize,
            )
        return self._stubs["get_data_labeling_job"]

    @property
    def list_data_labeling_jobs(
        self,
    ) -> Callable[
        [job_service.ListDataLabelingJobsRequest],
        job_service.ListDataLabelingJobsResponse,
    ]:
        r"""Return a callable for the list data labeling jobs method over gRPC.

        Lists DataLabelingJobs in a Location.

        Returns:
            Callable[[~.ListDataLabelingJobsRequest],
                    ~.ListDataLabelingJobsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_data_labeling_jobs" not in self._stubs:
            self._stubs["list_data_labeling_jobs"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/ListDataLabelingJobs",
                request_serializer=job_service.ListDataLabelingJobsRequest.serialize,
                response_deserializer=job_service.ListDataLabelingJobsResponse.deserialize,
            )
        return self._stubs["list_data_labeling_jobs"]

    @property
    def delete_data_labeling_job(
        self,
    ) -> Callable[[job_service.DeleteDataLabelingJobRequest], operations_pb2.Operation]:
        r"""Return a callable for the delete data labeling job method over gRPC.

        Deletes a DataLabelingJob.

        Returns:
            Callable[[~.DeleteDataLabelingJobRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_data_labeling_job" not in self._stubs:
            self._stubs["delete_data_labeling_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/DeleteDataLabelingJob",
                request_serializer=job_service.DeleteDataLabelingJobRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs["delete_data_labeling_job"]

    @property
    def cancel_data_labeling_job(
        self,
    ) -> Callable[[job_service.CancelDataLabelingJobRequest], empty_pb2.Empty]:
        r"""Return a callable for the cancel data labeling job method over gRPC.

        Cancels a DataLabelingJob. Success of cancellation is
        not guaranteed.

        Returns:
            Callable[[~.CancelDataLabelingJobRequest],
                    ~.Empty]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "cancel_data_labeling_job" not in self._stubs:
            self._stubs["cancel_data_labeling_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/CancelDataLabelingJob",
                request_serializer=job_service.CancelDataLabelingJobRequest.serialize,
                response_deserializer=empty_pb2.Empty.FromString,
            )
        return self._stubs["cancel_data_labeling_job"]

    @property
    def create_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.CreateHyperparameterTuningJobRequest],
        gca_hyperparameter_tuning_job.HyperparameterTuningJob,
    ]:
        r"""Return a callable for the create hyperparameter tuning
        job method over gRPC.

        Creates a HyperparameterTuningJob

        Returns:
            Callable[[~.CreateHyperparameterTuningJobRequest],
                    ~.HyperparameterTuningJob]:
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
                "/google.cloud.aiplatform.v1.JobService/CreateHyperparameterTuningJob",
                request_serializer=job_service.CreateHyperparameterTuningJobRequest.serialize,
                response_deserializer=gca_hyperparameter_tuning_job.HyperparameterTuningJob.deserialize,
            )
        return self._stubs["create_hyperparameter_tuning_job"]

    @property
    def get_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.GetHyperparameterTuningJobRequest],
        hyperparameter_tuning_job.HyperparameterTuningJob,
    ]:
        r"""Return a callable for the get hyperparameter tuning job method over gRPC.

        Gets a HyperparameterTuningJob

        Returns:
            Callable[[~.GetHyperparameterTuningJobRequest],
                    ~.HyperparameterTuningJob]:
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
                "/google.cloud.aiplatform.v1.JobService/GetHyperparameterTuningJob",
                request_serializer=job_service.GetHyperparameterTuningJobRequest.serialize,
                response_deserializer=hyperparameter_tuning_job.HyperparameterTuningJob.deserialize,
            )
        return self._stubs["get_hyperparameter_tuning_job"]

    @property
    def list_hyperparameter_tuning_jobs(
        self,
    ) -> Callable[
        [job_service.ListHyperparameterTuningJobsRequest],
        job_service.ListHyperparameterTuningJobsResponse,
    ]:
        r"""Return a callable for the list hyperparameter tuning
        jobs method over gRPC.

        Lists HyperparameterTuningJobs in a Location.

        Returns:
            Callable[[~.ListHyperparameterTuningJobsRequest],
                    ~.ListHyperparameterTuningJobsResponse]:
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
                "/google.cloud.aiplatform.v1.JobService/ListHyperparameterTuningJobs",
                request_serializer=job_service.ListHyperparameterTuningJobsRequest.serialize,
                response_deserializer=job_service.ListHyperparameterTuningJobsResponse.deserialize,
            )
        return self._stubs["list_hyperparameter_tuning_jobs"]

    @property
    def delete_hyperparameter_tuning_job(
        self,
    ) -> Callable[
        [job_service.DeleteHyperparameterTuningJobRequest], operations_pb2.Operation
    ]:
        r"""Return a callable for the delete hyperparameter tuning
        job method over gRPC.

        Deletes a HyperparameterTuningJob.

        Returns:
            Callable[[~.DeleteHyperparameterTuningJobRequest],
                    ~.Operation]:
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
                "/google.cloud.aiplatform.v1.JobService/DeleteHyperparameterTuningJob",
                request_serializer=job_service.DeleteHyperparameterTuningJobRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs["delete_hyperparameter_tuning_job"]

    @property
    def cancel_hyperparameter_tuning_job(
        self,
    ) -> Callable[[job_service.CancelHyperparameterTuningJobRequest], empty_pb2.Empty]:
        r"""Return a callable for the cancel hyperparameter tuning
        job method over gRPC.

        Cancels a HyperparameterTuningJob. Starts asynchronous
        cancellation on the HyperparameterTuningJob. The server makes a
        best effort to cancel the job, but success is not guaranteed.
        Clients can use
        [JobService.GetHyperparameterTuningJob][google.cloud.aiplatform.v1.JobService.GetHyperparameterTuningJob]
        or other methods to check whether the cancellation succeeded or
        whether the job completed despite cancellation. On successful
        cancellation, the HyperparameterTuningJob is not deleted;
        instead it becomes a job with a
        [HyperparameterTuningJob.error][google.cloud.aiplatform.v1.HyperparameterTuningJob.error]
        value with a [google.rpc.Status.code][google.rpc.Status.code] of
        1, corresponding to ``Code.CANCELLED``, and
        [HyperparameterTuningJob.state][google.cloud.aiplatform.v1.HyperparameterTuningJob.state]
        is set to ``CANCELLED``.

        Returns:
            Callable[[~.CancelHyperparameterTuningJobRequest],
                    ~.Empty]:
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
                "/google.cloud.aiplatform.v1.JobService/CancelHyperparameterTuningJob",
                request_serializer=job_service.CancelHyperparameterTuningJobRequest.serialize,
                response_deserializer=empty_pb2.Empty.FromString,
            )
        return self._stubs["cancel_hyperparameter_tuning_job"]

    @property
    def create_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.CreateBatchPredictionJobRequest],
        gca_batch_prediction_job.BatchPredictionJob,
    ]:
        r"""Return a callable for the create batch prediction job method over gRPC.

        Creates a BatchPredictionJob. A BatchPredictionJob
        once created will right away be attempted to start.

        Returns:
            Callable[[~.CreateBatchPredictionJobRequest],
                    ~.BatchPredictionJob]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_batch_prediction_job" not in self._stubs:
            self._stubs["create_batch_prediction_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/CreateBatchPredictionJob",
                request_serializer=job_service.CreateBatchPredictionJobRequest.serialize,
                response_deserializer=gca_batch_prediction_job.BatchPredictionJob.deserialize,
            )
        return self._stubs["create_batch_prediction_job"]

    @property
    def get_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.GetBatchPredictionJobRequest],
        batch_prediction_job.BatchPredictionJob,
    ]:
        r"""Return a callable for the get batch prediction job method over gRPC.

        Gets a BatchPredictionJob

        Returns:
            Callable[[~.GetBatchPredictionJobRequest],
                    ~.BatchPredictionJob]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_batch_prediction_job" not in self._stubs:
            self._stubs["get_batch_prediction_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/GetBatchPredictionJob",
                request_serializer=job_service.GetBatchPredictionJobRequest.serialize,
                response_deserializer=batch_prediction_job.BatchPredictionJob.deserialize,
            )
        return self._stubs["get_batch_prediction_job"]

    @property
    def list_batch_prediction_jobs(
        self,
    ) -> Callable[
        [job_service.ListBatchPredictionJobsRequest],
        job_service.ListBatchPredictionJobsResponse,
    ]:
        r"""Return a callable for the list batch prediction jobs method over gRPC.

        Lists BatchPredictionJobs in a Location.

        Returns:
            Callable[[~.ListBatchPredictionJobsRequest],
                    ~.ListBatchPredictionJobsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_batch_prediction_jobs" not in self._stubs:
            self._stubs["list_batch_prediction_jobs"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/ListBatchPredictionJobs",
                request_serializer=job_service.ListBatchPredictionJobsRequest.serialize,
                response_deserializer=job_service.ListBatchPredictionJobsResponse.deserialize,
            )
        return self._stubs["list_batch_prediction_jobs"]

    @property
    def delete_batch_prediction_job(
        self,
    ) -> Callable[
        [job_service.DeleteBatchPredictionJobRequest], operations_pb2.Operation
    ]:
        r"""Return a callable for the delete batch prediction job method over gRPC.

        Deletes a BatchPredictionJob. Can only be called on
        jobs that already finished.

        Returns:
            Callable[[~.DeleteBatchPredictionJobRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_batch_prediction_job" not in self._stubs:
            self._stubs["delete_batch_prediction_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/DeleteBatchPredictionJob",
                request_serializer=job_service.DeleteBatchPredictionJobRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs["delete_batch_prediction_job"]

    @property
    def cancel_batch_prediction_job(
        self,
    ) -> Callable[[job_service.CancelBatchPredictionJobRequest], empty_pb2.Empty]:
        r"""Return a callable for the cancel batch prediction job method over gRPC.

        Cancels a BatchPredictionJob.

        Starts asynchronous cancellation on the BatchPredictionJob. The
        server makes the best effort to cancel the job, but success is
        not guaranteed. Clients can use
        [JobService.GetBatchPredictionJob][google.cloud.aiplatform.v1.JobService.GetBatchPredictionJob]
        or other methods to check whether the cancellation succeeded or
        whether the job completed despite cancellation. On a successful
        cancellation, the BatchPredictionJob is not deleted;instead its
        [BatchPredictionJob.state][google.cloud.aiplatform.v1.BatchPredictionJob.state]
        is set to ``CANCELLED``. Any files already outputted by the job
        are not deleted.

        Returns:
            Callable[[~.CancelBatchPredictionJobRequest],
                    ~.Empty]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "cancel_batch_prediction_job" not in self._stubs:
            self._stubs["cancel_batch_prediction_job"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1.JobService/CancelBatchPredictionJob",
                request_serializer=job_service.CancelBatchPredictionJobRequest.serialize,
                response_deserializer=empty_pb2.Empty.FromString,
            )
        return self._stubs["cancel_batch_prediction_job"]


__all__ = ("JobServiceGrpcTransport",)
