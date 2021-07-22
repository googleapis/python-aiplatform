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


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "GcsSource",
        "GcsDestination",
        "BigQuerySource",
        "BigQueryDestination",
        "ContainerRegistryDestination",
    },
)


class GcsSource(proto.Message):
    r"""The Google Cloud Storage location for the input content.
    Attributes:
        uris (Sequence[str]):
            Required. Google Cloud Storage URI(-s) to the
            input file(s). May contain wildcards. For more
            information on wildcards, see
            https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
    """

    uris = proto.RepeatedField(proto.STRING, number=1,)


class GcsDestination(proto.Message):
    r"""The Google Cloud Storage location where the output is to be
    written to.

    Attributes:
        output_uri_prefix (str):
            Required. Google Cloud Storage URI to output
            directory. If the uri doesn't end with '/', a
            '/' will be automatically appended. The
            directory is created if it doesn't exist.
    """

    output_uri_prefix = proto.Field(proto.STRING, number=1,)


class BigQuerySource(proto.Message):
    r"""The BigQuery location for the input content.
    Attributes:
        input_uri (str):
            Required. BigQuery URI to a table, up to 2000 characters
            long. Accepted forms:

            -  BigQuery path. For example:
               ``bq://projectId.bqDatasetId.bqTableId``.
    """

    input_uri = proto.Field(proto.STRING, number=1,)


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

    output_uri = proto.Field(proto.STRING, number=1,)


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

    output_uri = proto.Field(proto.STRING, number=1,)


__all__ = tuple(sorted(__protobuf__.manifest))
