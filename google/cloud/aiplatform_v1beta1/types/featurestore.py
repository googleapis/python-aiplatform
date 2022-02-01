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
    package="google.cloud.aiplatform.v1beta1", manifest={"Featurestore",},
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
        labels (Sequence[google.cloud.aiplatform_v1beta1.types.Featurestore.LabelsEntry]):
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
        online_serving_config (google.cloud.aiplatform_v1beta1.types.Featurestore.OnlineServingConfig):
            Required. Config for online serving
            resources.
        state (google.cloud.aiplatform_v1beta1.types.Featurestore.State):
            Output only. State of the featurestore.
        encryption_spec (google.cloud.aiplatform_v1beta1.types.EncryptionSpec):
            Optional. Customer-managed encryption key
            spec for data storage. If set, both of the
            online and offline data storage will be secured
            by this key.
    """

    class State(proto.Enum):
        r"""Possible states a Featurestore can have."""
        STATE_UNSPECIFIED = 0
        STABLE = 1
        UPDATING = 2

    class OnlineServingConfig(proto.Message):
        r"""OnlineServingConfig specifies the details for provisioning
        online serving resources.

        Attributes:
            fixed_node_count (int):
                The number of nodes for each cluster. The number of nodes
                will not scale automatically but can be scaled manually by
                providing different values when updating. Only one of
                ``fixed_node_count`` and ``scaling`` can be set. Setting one
                will reset the other.
            scaling (google.cloud.aiplatform_v1beta1.types.Featurestore.OnlineServingConfig.Scaling):
                Online serving scaling configuration. Only one of
                ``fixed_node_count`` and ``scaling`` can be set. Setting one
                will reset the other.
        """

        class Scaling(proto.Message):
            r"""Online serving scaling configuration. If min_node_count and
            max_node_count are set to the same value, the cluster will be
            configured with the fixed number of node (no auto-scaling).

            Attributes:
                min_node_count (int):
                    Required. The minimum number of nodes to
                    scale down to. Must be greater than or equal to
                    1.
                max_node_count (int):
                    The maximum number of nodes to scale up to. Must be greater
                    or equal to min_node_count.
            """

            min_node_count = proto.Field(proto.INT32, number=1,)
            max_node_count = proto.Field(proto.INT32, number=2,)

        fixed_node_count = proto.Field(proto.INT32, number=2,)
        scaling = proto.Field(
            proto.MESSAGE, number=4, message="Featurestore.OnlineServingConfig.Scaling",
        )

    name = proto.Field(proto.STRING, number=1,)
    create_time = proto.Field(proto.MESSAGE, number=3, message=timestamp_pb2.Timestamp,)
    update_time = proto.Field(proto.MESSAGE, number=4, message=timestamp_pb2.Timestamp,)
    etag = proto.Field(proto.STRING, number=5,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=6,)
    online_serving_config = proto.Field(
        proto.MESSAGE, number=7, message=OnlineServingConfig,
    )
    state = proto.Field(proto.ENUM, number=8, enum=State,)
    encryption_spec = proto.Field(
        proto.MESSAGE, number=10, message=gca_encryption_spec.EncryptionSpec,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
