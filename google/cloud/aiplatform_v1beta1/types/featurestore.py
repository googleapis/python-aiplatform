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

from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1", manifest={"Featurestore",},
)


class Featurestore(proto.Message):
    r"""Featurestore configuration information on how the
    Featurestore is configured.

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
            Optional. Used to perform consistent read-
            odify-write updates. If not set, a blind
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
                The number of nodes for each cluster. The
                number of nodes will not scale automatically but
                can be scaled manually by providing different
                values when updating.
        """

        fixed_node_count = proto.Field(proto.INT32, number=2,)

    name = proto.Field(proto.STRING, number=1,)
    create_time = proto.Field(proto.MESSAGE, number=3, message=timestamp_pb2.Timestamp,)
    update_time = proto.Field(proto.MESSAGE, number=4, message=timestamp_pb2.Timestamp,)
    etag = proto.Field(proto.STRING, number=5,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=6,)
    online_serving_config = proto.Field(
        proto.MESSAGE, number=7, message=OnlineServingConfig,
    )
    state = proto.Field(proto.ENUM, number=8, enum=State,)


__all__ = tuple(sorted(__protobuf__.manifest))
