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

from google.cloud.aiplatform_v1beta1.types import deployed_index_ref
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1", manifest={"Index",},
)


class Index(proto.Message):
    r"""A representation of a collection of database items organized
    in a way that allows for approximate nearest neighbor (a.k.a
    ANN) algorithms search.

    Attributes:
        name (str):
            Output only. The resource name of the Index.
        display_name (str):
            Required. The display name of the Index.
            The name can be up to 128 characters long and
            can be consist of any UTF-8 characters.
        description (str):
            The description of the Index.
        metadata_schema_uri (str):
            Immutable. Points to a YAML file stored on Google Cloud
            Storage describing additional information about the Index,
            that is specific to it. Unset if the Index does not have any
            additional information. The schema is defined as an OpenAPI
            3.0.2 `Schema
            Object <https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md#schemaObject>`__.
            Note: The URI given on output will be immutable and probably
            different, including the URI scheme, than the one given on
            input. The output URI will point to a location where the
            user only has a read access.
        metadata (google.protobuf.struct_pb2.Value):
            An additional information about the Index; the schema of the
            metadata can be found in
            [metadata_schema][google.cloud.aiplatform.v1beta1.Index.metadata_schema_uri].
        deployed_indexes (Sequence[google.cloud.aiplatform_v1beta1.types.DeployedIndexRef]):
            Output only. The pointers to DeployedIndexes
            created from this Index. An Index can be only
            deleted if all its DeployedIndexes had been
            undeployed first.
        etag (str):
            Used to perform consistent read-modify-write
            updates. If not set, a blind "overwrite" update
            happens.
        labels (Sequence[google.cloud.aiplatform_v1beta1.types.Index.LabelsEntry]):
            The labels with user-defined metadata to
            organize your Indexes.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            and examples of labels.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this Index was
            created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this Index was most recently
            updated. This also includes any update to the contents of
            the Index. Note that Operations working on this Index may
            have their
            [Operations.metadata.generic_metadata.update_time]
            [google.cloud.aiplatform.v1beta1.GenericOperationMetadata.update_time]
            a little after the value of this timestamp, yet that does
            not mean their results are not already reflected in the
            Index. Result of any successfully completed Operation on the
            Index is reflected in it.
    """

    name = proto.Field(proto.STRING, number=1,)
    display_name = proto.Field(proto.STRING, number=2,)
    description = proto.Field(proto.STRING, number=3,)
    metadata_schema_uri = proto.Field(proto.STRING, number=4,)
    metadata = proto.Field(proto.MESSAGE, number=6, message=struct_pb2.Value,)
    deployed_indexes = proto.RepeatedField(
        proto.MESSAGE, number=7, message=deployed_index_ref.DeployedIndexRef,
    )
    etag = proto.Field(proto.STRING, number=8,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=9,)
    create_time = proto.Field(
        proto.MESSAGE, number=10, message=timestamp_pb2.Timestamp,
    )
    update_time = proto.Field(
        proto.MESSAGE, number=11, message=timestamp_pb2.Timestamp,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
