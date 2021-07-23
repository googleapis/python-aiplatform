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
    package="google.cloud.aiplatform.v1beta1", manifest={"Event",},
)


class Event(proto.Message):
    r"""An edge describing the relationship between an Artifact and
    an Execution in a lineage graph.

    Attributes:
        artifact (str):
            Required. The relative resource name of the
            Artifact in the Event.
        execution (str):
            Output only. The relative resource name of
            the Execution in the Event.
        event_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time the Event occurred.
        type_ (google.cloud.aiplatform_v1beta1.types.Event.Type):
            Required. The type of the Event.
        labels (Sequence[google.cloud.aiplatform_v1beta1.types.Event.LabelsEntry]):
            The labels with user-defined metadata to
            annotate Events.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed. No more than 64 user labels can be
            associated with one Event (System labels are
            excluded).

            See https://goo.gl/xmQnxf for more information
            and examples of labels. System reserved label
            keys are prefixed with
            "aiplatform.googleapis.com/" and are immutable.
    """

    class Type(proto.Enum):
        r"""Describes whether an Event's Artifact is the Execution's
        input or output.
        """
        TYPE_UNSPECIFIED = 0
        INPUT = 1
        OUTPUT = 2

    artifact = proto.Field(proto.STRING, number=1,)
    execution = proto.Field(proto.STRING, number=2,)
    event_time = proto.Field(proto.MESSAGE, number=3, message=timestamp_pb2.Timestamp,)
    type_ = proto.Field(proto.ENUM, number=4, enum=Type,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=5,)


__all__ = tuple(sorted(__protobuf__.manifest))
