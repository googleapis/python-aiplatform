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
from __future__ import annotations

from typing import MutableMapping, MutableSequence

import proto  # type: ignore

from google.cloud.aiplatform_v1beta1.types import api_auth
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "AvroSource",
        "CsvSource",
        "GcsSource",
        "GcsDestination",
        "BigQuerySource",
        "BigQueryDestination",
        "CsvDestination",
        "TFRecordDestination",
        "ContainerRegistryDestination",
        "GoogleDriveSource",
        "DirectUploadSource",
        "SlackSource",
        "JiraSource",
    },
)


class AvroSource(proto.Message):
    r"""The storage details for Avro input content.

    Attributes:
        gcs_source (google.cloud.aiplatform_v1beta1.types.GcsSource):
            Required. Google Cloud Storage location.
    """

    gcs_source: "GcsSource" = proto.Field(
        proto.MESSAGE,
        number=1,
        message="GcsSource",
    )


class CsvSource(proto.Message):
    r"""The storage details for CSV input content.

    Attributes:
        gcs_source (google.cloud.aiplatform_v1beta1.types.GcsSource):
            Required. Google Cloud Storage location.
    """

    gcs_source: "GcsSource" = proto.Field(
        proto.MESSAGE,
        number=1,
        message="GcsSource",
    )


class GcsSource(proto.Message):
    r"""The Google Cloud Storage location for the input content.

    Attributes:
        uris (MutableSequence[str]):
            Required. Google Cloud Storage URI(-s) to the
            input file(s). May contain wildcards. For more
            information on wildcards, see
            https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
    """

    uris: MutableSequence[str] = proto.RepeatedField(
        proto.STRING,
        number=1,
    )


class GcsDestination(proto.Message):
    r"""The Google Cloud Storage location where the output is to be
    written to.

    Attributes:
        output_uri_prefix (str):
            Required. Google Cloud Storage URI to output
            directory. If the uri doesn't end with
            '/', a '/' will be automatically appended. The
            directory is created if it doesn't exist.
    """

    output_uri_prefix: str = proto.Field(
        proto.STRING,
        number=1,
    )


class BigQuerySource(proto.Message):
    r"""The BigQuery location for the input content.

    Attributes:
        input_uri (str):
            Required. BigQuery URI to a table, up to 2000 characters
            long. Accepted forms:

            -  BigQuery path. For example:
               ``bq://projectId.bqDatasetId.bqTableId``.
    """

    input_uri: str = proto.Field(
        proto.STRING,
        number=1,
    )


class BigQueryDestination(proto.Message):
    r"""The BigQuery location for the output content.

    Attributes:
        output_uri (str):
            Required. BigQuery URI to a project or table, up to 2000
            characters long.

            When only the project is specified, the Dataset and Table is
            created. When the full table reference is specified, the
            Dataset must exist and table must not exist.

            Accepted forms:

            -  BigQuery path. For example: ``bq://projectId`` or
               ``bq://projectId.bqDatasetId`` or
               ``bq://projectId.bqDatasetId.bqTableId``.
    """

    output_uri: str = proto.Field(
        proto.STRING,
        number=1,
    )


class CsvDestination(proto.Message):
    r"""The storage details for CSV output content.

    Attributes:
        gcs_destination (google.cloud.aiplatform_v1beta1.types.GcsDestination):
            Required. Google Cloud Storage location.
    """

    gcs_destination: "GcsDestination" = proto.Field(
        proto.MESSAGE,
        number=1,
        message="GcsDestination",
    )


class TFRecordDestination(proto.Message):
    r"""The storage details for TFRecord output content.

    Attributes:
        gcs_destination (google.cloud.aiplatform_v1beta1.types.GcsDestination):
            Required. Google Cloud Storage location.
    """

    gcs_destination: "GcsDestination" = proto.Field(
        proto.MESSAGE,
        number=1,
        message="GcsDestination",
    )


class ContainerRegistryDestination(proto.Message):
    r"""The Container Registry location for the container image.

    Attributes:
        output_uri (str):
            Required. Container Registry URI of a container image. Only
            Google Container Registry and Artifact Registry are
            supported now. Accepted forms:

            -  Google Container Registry path. For example:
               ``gcr.io/projectId/imageName:tag``.

            -  Artifact Registry path. For example:
               ``us-central1-docker.pkg.dev/projectId/repoName/imageName:tag``.

            If a tag is not specified, "latest" will be used as the
            default tag.
    """

    output_uri: str = proto.Field(
        proto.STRING,
        number=1,
    )


class GoogleDriveSource(proto.Message):
    r"""The Google Drive location for the input content.

    Attributes:
        resource_ids (MutableSequence[google.cloud.aiplatform_v1beta1.types.GoogleDriveSource.ResourceId]):
            Required. Google Drive resource IDs.
    """

    class ResourceId(proto.Message):
        r"""The type and ID of the Google Drive resource.

        Attributes:
            resource_type (google.cloud.aiplatform_v1beta1.types.GoogleDriveSource.ResourceId.ResourceType):
                Required. The type of the Google Drive
                resource.
            resource_id (str):
                Required. The ID of the Google Drive
                resource.
        """

        class ResourceType(proto.Enum):
            r"""The type of the Google Drive resource.

            Values:
                RESOURCE_TYPE_UNSPECIFIED (0):
                    Unspecified resource type.
                RESOURCE_TYPE_FILE (1):
                    File resource type.
                RESOURCE_TYPE_FOLDER (2):
                    Folder resource type.
            """
            RESOURCE_TYPE_UNSPECIFIED = 0
            RESOURCE_TYPE_FILE = 1
            RESOURCE_TYPE_FOLDER = 2

        resource_type: "GoogleDriveSource.ResourceId.ResourceType" = proto.Field(
            proto.ENUM,
            number=1,
            enum="GoogleDriveSource.ResourceId.ResourceType",
        )
        resource_id: str = proto.Field(
            proto.STRING,
            number=2,
        )

    resource_ids: MutableSequence[ResourceId] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=ResourceId,
    )


class DirectUploadSource(proto.Message):
    r"""The input content is encapsulated and uploaded in the
    request.

    """


class SlackSource(proto.Message):
    r"""The Slack source for the ImportRagFilesRequest.

    Attributes:
        channels (MutableSequence[google.cloud.aiplatform_v1beta1.types.SlackSource.SlackChannels]):
            Required. The Slack channels.
    """

    class SlackChannels(proto.Message):
        r"""SlackChannels contains the Slack channels and corresponding
        access token.

        Attributes:
            channels (MutableSequence[google.cloud.aiplatform_v1beta1.types.SlackSource.SlackChannels.SlackChannel]):
                Required. The Slack channel IDs.
            api_key_config (google.cloud.aiplatform_v1beta1.types.ApiAuth.ApiKeyConfig):
                Required. The SecretManager secret version
                resource name (e.g.
                projects/{project}/secrets/{secret}/versions/{version})
                storing the Slack channel access token that has
                access to the slack channel IDs. See:
                https://api.slack.com/tutorials/tracks/getting-a-token.
        """

        class SlackChannel(proto.Message):
            r"""SlackChannel contains the Slack channel ID and the time range
            to import.

            Attributes:
                channel_id (str):
                    Required. The Slack channel ID.
                start_time (google.protobuf.timestamp_pb2.Timestamp):
                    Optional. The starting timestamp for messages
                    to import.
                end_time (google.protobuf.timestamp_pb2.Timestamp):
                    Optional. The ending timestamp for messages
                    to import.
            """

            channel_id: str = proto.Field(
                proto.STRING,
                number=1,
            )
            start_time: timestamp_pb2.Timestamp = proto.Field(
                proto.MESSAGE,
                number=2,
                message=timestamp_pb2.Timestamp,
            )
            end_time: timestamp_pb2.Timestamp = proto.Field(
                proto.MESSAGE,
                number=3,
                message=timestamp_pb2.Timestamp,
            )

        channels: MutableSequence[
            "SlackSource.SlackChannels.SlackChannel"
        ] = proto.RepeatedField(
            proto.MESSAGE,
            number=1,
            message="SlackSource.SlackChannels.SlackChannel",
        )
        api_key_config: api_auth.ApiAuth.ApiKeyConfig = proto.Field(
            proto.MESSAGE,
            number=3,
            message=api_auth.ApiAuth.ApiKeyConfig,
        )

    channels: MutableSequence[SlackChannels] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=SlackChannels,
    )


class JiraSource(proto.Message):
    r"""The Jira source for the ImportRagFilesRequest.

    Attributes:
        jira_queries (MutableSequence[google.cloud.aiplatform_v1beta1.types.JiraSource.JiraQueries]):
            Required. The Jira queries.
    """

    class JiraQueries(proto.Message):
        r"""JiraQueries contains the Jira queries and corresponding
        authentication.

        Attributes:
            projects (MutableSequence[str]):
                A list of Jira projects to import in their
                entirety.
            custom_queries (MutableSequence[str]):
                A list of custom Jira queries to import. For
                information about JQL (Jira Query Language), see
                https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/
            email (str):
                Required. The Jira email address.
            server_uri (str):
                Required. The Jira server URI.
            api_key_config (google.cloud.aiplatform_v1beta1.types.ApiAuth.ApiKeyConfig):
                Required. The SecretManager secret version
                resource name (e.g.
                projects/{project}/secrets/{secret}/versions/{version})
                storing the Jira API key
                (https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).
        """

        projects: MutableSequence[str] = proto.RepeatedField(
            proto.STRING,
            number=3,
        )
        custom_queries: MutableSequence[str] = proto.RepeatedField(
            proto.STRING,
            number=4,
        )
        email: str = proto.Field(
            proto.STRING,
            number=5,
        )
        server_uri: str = proto.Field(
            proto.STRING,
            number=6,
        )
        api_key_config: api_auth.ApiAuth.ApiKeyConfig = proto.Field(
            proto.MESSAGE,
            number=7,
            message=api_auth.ApiAuth.ApiKeyConfig,
        )

    jira_queries: MutableSequence[JiraQueries] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=JiraQueries,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
