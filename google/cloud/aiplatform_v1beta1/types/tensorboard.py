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

from google.cloud.aiplatform_v1beta1.types import encryption_spec as gca_encryption_spec
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1", manifest={"Tensorboard",},
)


class Tensorboard(proto.Message):
    r"""Tensorboard is a physical database that stores users'
    training metrics. A default Tensorboard is provided in each
    region of a GCP project. If needed users can also create extra
    Tensorboards in their projects.

    Attributes:
        name (str):
            Output only. Name of the Tensorboard. Format:
            ``projects/{project}/locations/{location}/tensorboards/{tensorboard}``
        display_name (str):
            Required. User provided name of this
            Tensorboard.
        description (str):
            Description of this Tensorboard.
        encryption_spec (google.cloud.aiplatform_v1beta1.types.EncryptionSpec):
            Customer-managed encryption key spec for a
            Tensorboard. If set, this Tensorboard and all
            sub-resources of this Tensorboard will be
            secured by this key.
        blob_storage_path_prefix (str):
            Output only. Consumer project Cloud Storage
            path prefix used to store blob data, which can
            either be a bucket or directory. Does not end
            with a '/'.
        run_count (int):
            Output only. The number of Runs stored in
            this Tensorboard.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this Tensorboard
            was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this Tensorboard
            was last updated.
        labels (Sequence[google.cloud.aiplatform_v1beta1.types.Tensorboard.LabelsEntry]):
            The labels with user-defined metadata to
            organize your Tensorboards.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed. No more than 64 user labels can be
            associated with one Tensorboard (System labels
            are excluded).

            See https://goo.gl/xmQnxf for more information
            and examples of labels. System reserved label
            keys are prefixed with
            "aiplatform.googleapis.com/" and are immutable.
        etag (str):
            Used to perform a consistent read-modify-
            rite updates. If not set, a blind "overwrite"
            update happens.
    """

    name = proto.Field(proto.STRING, number=1,)
    display_name = proto.Field(proto.STRING, number=2,)
    description = proto.Field(proto.STRING, number=3,)
    encryption_spec = proto.Field(
        proto.MESSAGE, number=11, message=gca_encryption_spec.EncryptionSpec,
    )
    blob_storage_path_prefix = proto.Field(proto.STRING, number=10,)
    run_count = proto.Field(proto.INT32, number=5,)
    create_time = proto.Field(proto.MESSAGE, number=6, message=timestamp_pb2.Timestamp,)
    update_time = proto.Field(proto.MESSAGE, number=7, message=timestamp_pb2.Timestamp,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=8,)
    etag = proto.Field(proto.STRING, number=9,)


__all__ = tuple(sorted(__protobuf__.manifest))
