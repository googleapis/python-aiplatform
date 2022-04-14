# -*- coding: utf-8 -*-
# Copyright 2022 Google LLC
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

from google.cloud.aiplatform_v1.types import encryption_spec as gca_encryption_spec
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "Featurestore",
    },
)


class Featurestore(proto.Message):
    r"""Vertex AI Feature Store provides a centralized repository for
    organizing, storing, and serving ML features. The Featurestore
    is a top-level container for your features and their values.

    Attributes:
        name (str):
            Output only. Name of the Featurestore. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}``
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this Featurestore
            was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this Featurestore
            was last updated.
        etag (str):
            Optional. Used to perform consistent
            read-modify-write updates. If not set, a blind
            "overwrite" update happens.
        labels (Mapping[str, str]):
            Optional. The labels with user-defined
            metadata to organize your Featurestore.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            on and examples of labels. No more than 64 user
            labels can be associated with one
            Featurestore(System labels are excluded)."
            System reserved label keys are prefixed with
            "aiplatform.googleapis.com/" and are immutable.
        online_serving_config (google.cloud.aiplatform_v1.types.Featurestore.OnlineServingConfig):
            Optional. Config for online storage
            resources. If unset, the featurestore will not
            have an online store and cannot be used for
            online serving.
        state (google.cloud.aiplatform_v1.types.Featurestore.State):
            Output only. State of the featurestore.
        encryption_spec (google.cloud.aiplatform_v1.types.EncryptionSpec):
            Optional. Customer-managed encryption key
            spec for data storage. If set, both of the
            online and offline data storage will be secured
            by this key.
    """

    class State(proto.Enum):
        r"""Possible states a featurestore can have."""
        STATE_UNSPECIFIED = 0
        STABLE = 1
        UPDATING = 2

    class OnlineServingConfig(proto.Message):
        r"""OnlineServingConfig specifies the details for provisioning
        online serving resources.

        Attributes:
            fixed_node_count (int):
                The number of nodes for the online store. The
                number of nodes doesn't scale automatically, but
                you can manually update the number of nodes. If
                set to 0, the featurestore will not have an
                online store and cannot be used for online
                serving.
        """

        fixed_node_count = proto.Field(
            proto.INT32,
            number=2,
        )

    name = proto.Field(
        proto.STRING,
        number=1,
    )
    create_time = proto.Field(
        proto.MESSAGE,
        number=3,
        message=timestamp_pb2.Timestamp,
    )
    update_time = proto.Field(
        proto.MESSAGE,
        number=4,
        message=timestamp_pb2.Timestamp,
    )
    etag = proto.Field(
        proto.STRING,
        number=5,
    )
    labels = proto.MapField(
        proto.STRING,
        proto.STRING,
        number=6,
    )
    online_serving_config = proto.Field(
        proto.MESSAGE,
        number=7,
        message=OnlineServingConfig,
    )
    state = proto.Field(
        proto.ENUM,
        number=8,
        enum=State,
    )
    encryption_spec = proto.Field(
        proto.MESSAGE,
        number=10,
        message=gca_encryption_spec.EncryptionSpec,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
