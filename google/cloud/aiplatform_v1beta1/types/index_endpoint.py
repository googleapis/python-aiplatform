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
import proto  # type: ignore

from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "IndexEndpoint",
        "DeployedIndex",
        "DeployedIndexAuthConfig",
        "IndexPrivateEndpoints",
    },
)


class IndexEndpoint(proto.Message):
    r"""Indexes are deployed into it. An IndexEndpoint can have
    multiple DeployedIndexes.

    Attributes:
        name (str):
            Output only. The resource name of the
            IndexEndpoint.
        display_name (str):
            Required. The display name of the
            IndexEndpoint. The name can be up to 128
            characters long and can consist of any UTF-8
            characters.
        description (str):
            The description of the IndexEndpoint.
        deployed_indexes (Sequence[google.cloud.aiplatform_v1beta1.types.DeployedIndex]):
            Output only. The indexes deployed in this
            endpoint.
        etag (str):
            Used to perform consistent read-modify-write
            updates. If not set, a blind "overwrite" update
            happens.
        labels (Sequence[google.cloud.aiplatform_v1beta1.types.IndexEndpoint.LabelsEntry]):
            The labels with user-defined metadata to
            organize your IndexEndpoints.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            and examples of labels.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            IndexEndpoint was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            IndexEndpoint was last updated. This timestamp
            is not updated when the endpoint's
            DeployedIndexes are updated, e.g. due to updates
            of the original Indexes they are the deployments
            of.
        network (str):
            Required. Immutable. The full name of the Google Compute
            Engine
            `network <https://cloud.google.com/compute/docs/networks-and-firewalls#networks>`__
            to which the IndexEndpoint should be peered.

            Private services access must already be configured for the
            network. If left unspecified, the Endpoint is not peered
            with any network.

            `Format <https://cloud.google.com/compute/docs/reference/rest/v1/networks/insert>`__:
            projects/{project}/global/networks/{network}. Where
            {project} is a project number, as in '12345', and {network}
            is network name.
    """

    name = proto.Field(proto.STRING, number=1,)
    display_name = proto.Field(proto.STRING, number=2,)
    description = proto.Field(proto.STRING, number=3,)
    deployed_indexes = proto.RepeatedField(
        proto.MESSAGE, number=4, message="DeployedIndex",
    )
    etag = proto.Field(proto.STRING, number=5,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=6,)
    create_time = proto.Field(proto.MESSAGE, number=7, message=timestamp_pb2.Timestamp,)
    update_time = proto.Field(proto.MESSAGE, number=8, message=timestamp_pb2.Timestamp,)
    network = proto.Field(proto.STRING, number=9,)


class DeployedIndex(proto.Message):
    r"""A deployment of an Index. IndexEndpoints contain one or more
    DeployedIndexes.

    Attributes:
        id (str):
            Required. The user specified ID of the
            DeployedIndex. The ID can be up to 128
            characters long and must start with a letter and
            only contain letters, numbers, and underscores.
            The ID must be unique within the project it is
            created in.
        index (str):
            Required. The name of the Index this is the
            deployment of. We may refer to this Index as the
            DeployedIndex's "original" Index.
        display_name (str):
            The display name of the DeployedIndex. If not provided upon
            creation, the Index's display_name is used.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when the DeployedIndex
            was created.
        private_endpoints (google.cloud.aiplatform_v1beta1.types.IndexPrivateEndpoints):
            Output only. Provides paths for users to send requests
            directly to the deployed index services running on Cloud via
            private services access. This field is populated if
            [network][google.cloud.aiplatform.v1beta1.IndexEndpoint.network]
            is configured.
        index_sync_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. The DeployedIndex may depend on various data on
            its original Index. Additionally when certain changes to the
            original Index are being done (e.g. when what the Index
            contains is being changed) the DeployedIndex may be
            asynchronously updated in the background to reflect this
            changes. If this timestamp's value is at least the
            [Index.update_time][google.cloud.aiplatform.v1beta1.Index.update_time]
            of the original Index, it means that this DeployedIndex and
            the original Index are in sync. If this timestamp is older,
            then to see which updates this DeployedIndex already
            contains (and which not), one must
            [list][Operations.ListOperations] [Operations][Operation]
            [working][Operation.name] on the original Index. Only the
            successfully completed Operations with
            [Operations.metadata.generic_metadata.update_time]
            [google.cloud.aiplatform.v1beta1.GenericOperationMetadata.update_time]
            equal or before this sync time are contained in this
            DeployedIndex.
        automatic_resources (google.cloud.aiplatform_v1beta1.types.AutomaticResources):
            Optional. A description of resources that the DeployedIndex
            uses, which to large degree are decided by AI Platform, and
            optionally allows only a modest additional configuration. If
            min_replica_count is not set, the default value is 1. If
            max_replica_count is not set, the default value is
            min_replica_count. The max allowed replica count is 1000.

            The user is billed for the resources (at least their minimal
            amount) even if the DeployedIndex receives no traffic.
        enable_access_logging (bool):
            Optional. If true, private endpoint's access
            logs are sent to StackDriver Logging.
            These logs are like standard server access logs,
            containing information like timestamp and
            latency for each MatchRequest.
            Note that Stackdriver logs may incur a cost,
            especially if the deployed index receives a high
            queries per second rate (QPS). Estimate your
            costs before enabling this option.
        deployed_index_auth_config (google.cloud.aiplatform_v1beta1.types.DeployedIndexAuthConfig):
            Optional. If set, the authentication is
            enabled for the private endpoint.
    """

    id = proto.Field(proto.STRING, number=1,)
    index = proto.Field(proto.STRING, number=2,)
    display_name = proto.Field(proto.STRING, number=3,)
    create_time = proto.Field(proto.MESSAGE, number=4, message=timestamp_pb2.Timestamp,)
    private_endpoints = proto.Field(
        proto.MESSAGE, number=5, message="IndexPrivateEndpoints",
    )
    index_sync_time = proto.Field(
        proto.MESSAGE, number=6, message=timestamp_pb2.Timestamp,
    )
    automatic_resources = proto.Field(
        proto.MESSAGE, number=7, message=machine_resources.AutomaticResources,
    )
    enable_access_logging = proto.Field(proto.BOOL, number=8,)
    deployed_index_auth_config = proto.Field(
        proto.MESSAGE, number=9, message="DeployedIndexAuthConfig",
    )


class DeployedIndexAuthConfig(proto.Message):
    r"""Used to set up the auth on the DeployedIndex's private
    endpoint.

    Attributes:
        auth_provider (google.cloud.aiplatform_v1beta1.types.DeployedIndexAuthConfig.AuthProvider):
            Defines the authentication provider that the
            DeployedIndex uses.
    """

    class AuthProvider(proto.Message):
        r"""Configuration for an authentication provider, including support for
        `JSON Web Token
        (JWT) <https://tools.ietf.org/html/draft-ietf-oauth-json-web-token-32>`__.

        Attributes:
            audiences (Sequence[str]):
                The list of JWT
                `audiences <https://tools.ietf.org/html/draft-ietf-oauth-json-web-token-32#section-4.1.3>`__.
                that are allowed to access. A JWT containing any of these
                audiences will be accepted.
            allowed_issuers (Sequence[str]):
                A list of allowed JWT issuers. Each entry must be a valid
                Google service account, in the following format:

                ``service-account-name@project-id.iam.gserviceaccount.com``
        """

        audiences = proto.RepeatedField(proto.STRING, number=1,)
        allowed_issuers = proto.RepeatedField(proto.STRING, number=2,)

    auth_provider = proto.Field(proto.MESSAGE, number=1, message=AuthProvider,)


class IndexPrivateEndpoints(proto.Message):
    r"""IndexPrivateEndpoints proto is used to provide paths for
    users to send requests via private services access.

    Attributes:
        match_grpc_address (str):
            Output only. The ip address used to send
            match gRPC requests.
    """

    match_grpc_address = proto.Field(proto.STRING, number=1,)


__all__ = tuple(sorted(__protobuf__.manifest))
