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


from google.cloud.aiplatform_v1beta1.types import user_action_reference
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1", manifest={"Annotation",},
)


class Annotation(proto.Message):
    r"""Used to assign specific AnnotationSpec to a particular area
    of a DataItem or the whole part of the DataItem.

    Attributes:
        name (str):
            Output only. Resource name of the Annotation.
        payload_schema_uri (str):
            Required. Google Cloud Storage URI points to a YAML file
            describing
            ``payload``.
            The schema is defined as an `OpenAPI 3.0.2 Schema
            Object <https://tinyurl.com/y538mdwt>`__. The schema files
            that can be used here are found in
            gs://google-cloud-aiplatform/schema/dataset/annotation/,
            note that the chosen schema must be consistent with the
            parent Dataset's
            ``metadata``.
        payload (google.protobuf.struct_pb2.Value):
            Required. The schema of the payload can be found in
            ``payload_schema``.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this Annotation
            was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this Annotation
            was last updated.
        etag (str):
            Optional. Used to perform a consistent read-
            odify-write updates. If not set, a blind
            "overwrite" update happens.
        annotation_source (google.cloud.aiplatform_v1beta1.types.UserActionReference):
            Output only. The source of the Annotation.
        labels (Sequence[google.cloud.aiplatform_v1beta1.types.Annotation.LabelsEntry]):
            Optional. The labels with user-defined metadata to organize
            your Annotations.

            Label keys and values can be no longer than 64 characters
            (Unicode codepoints), can only contain lowercase letters,
            numeric characters, underscores and dashes. International
            characters are allowed. No more than 64 user labels can be
            associated with one Annotation(System labels are excluded).

            See https://goo.gl/xmQnxf for more information and examples
            of labels. System reserved label keys are prefixed with
            "aiplatform.googleapis.com/" and are immutable. Following
            system labels exist for each Annotation:

            -  "aiplatform.googleapis.com/annotation_set_name":
               optional, name of the UI's annotation set this Annotation
               belongs to. If not set the Annotation is not visible in
               the UI.

            -  "aiplatform.googleapis.com/payload_schema": output only,
               its value is the
               [payload_schema's][google.cloud.aiplatform.v1beta1.Annotation.payload_schema_uri]
               title.
    """

    name = proto.Field(proto.STRING, number=1)

    payload_schema_uri = proto.Field(proto.STRING, number=2)

    payload = proto.Field(proto.MESSAGE, number=3, message=struct.Value,)

    create_time = proto.Field(proto.MESSAGE, number=4, message=timestamp.Timestamp,)

    update_time = proto.Field(proto.MESSAGE, number=7, message=timestamp.Timestamp,)

    etag = proto.Field(proto.STRING, number=8)

    annotation_source = proto.Field(
        proto.MESSAGE, number=5, message=user_action_reference.UserActionReference,
    )

    labels = proto.MapField(proto.STRING, proto.STRING, number=6)


__all__ = tuple(sorted(__protobuf__.manifest))
