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
    package="google.cloud.aiplatform.v1beta1", manifest={"TensorboardTimeSeries",},
)


class TensorboardTimeSeries(proto.Message):
    r"""TensorboardTimeSeries maps to times series produced in
    training runs

    Attributes:
        name (str):
            Output only. Name of the
            TensorboardTimeSeries.
        display_name (str):
            Required. User provided name of this
            TensorboardTimeSeries. This value should be
            unique among all TensorboardTimeSeries resources
            belonging to the same TensorboardRun resource
            (parent resource).
        description (str):
            Description of this TensorboardTimeSeries.
        value_type (google.cloud.aiplatform_v1beta1.types.TensorboardTimeSeries.ValueType):
            Required. Immutable. Type of
            TensorboardTimeSeries value.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            TensorboardTimeSeries was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            TensorboardTimeSeries was last updated.
        etag (str):
            Used to perform a consistent read-modify-
            rite updates. If not set, a blind "overwrite"
            update happens.
        plugin_name (str):
            Immutable. Name of the plugin this time
            series pertain to. Such as Scalar, Tensor, Blob
        plugin_data (bytes):
            Data of the current plugin, with the size
            limited to 65KB.
        metadata (google.cloud.aiplatform_v1beta1.types.TensorboardTimeSeries.Metadata):
            Output only. Scalar, Tensor, or Blob metadata
            for this TensorboardTimeSeries.
    """

    class ValueType(proto.Enum):
        r"""An enum representing the value type of a
        TensorboardTimeSeries.
        """
        VALUE_TYPE_UNSPECIFIED = 0
        SCALAR = 1
        TENSOR = 2
        BLOB_SEQUENCE = 3

    class Metadata(proto.Message):
        r"""Describes metadata for a TensorboardTimeSeries.
        Attributes:
            max_step (int):
                Output only. Max step index of all data
                points within a TensorboardTimeSeries.
            max_wall_time (google.protobuf.timestamp_pb2.Timestamp):
                Output only. Max wall clock timestamp of all
                data points within a TensorboardTimeSeries.
            max_blob_sequence_length (int):
                Output only. The largest blob sequence length (number of
                blobs) of all data points in this time series, if its
                ValueType is BLOB_SEQUENCE.
        """

        max_step = proto.Field(proto.INT64, number=1,)
        max_wall_time = proto.Field(
            proto.MESSAGE, number=2, message=timestamp_pb2.Timestamp,
        )
        max_blob_sequence_length = proto.Field(proto.INT64, number=3,)

    name = proto.Field(proto.STRING, number=1,)
    display_name = proto.Field(proto.STRING, number=2,)
    description = proto.Field(proto.STRING, number=3,)
    value_type = proto.Field(proto.ENUM, number=4, enum=ValueType,)
    create_time = proto.Field(proto.MESSAGE, number=5, message=timestamp_pb2.Timestamp,)
    update_time = proto.Field(proto.MESSAGE, number=6, message=timestamp_pb2.Timestamp,)
    etag = proto.Field(proto.STRING, number=7,)
    plugin_name = proto.Field(proto.STRING, number=8,)
    plugin_data = proto.Field(proto.BYTES, number=9,)
    metadata = proto.Field(proto.MESSAGE, number=10, message=Metadata,)


__all__ = tuple(sorted(__protobuf__.manifest))
