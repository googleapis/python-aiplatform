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

from google.cloud.aiplatform_v1beta1.types import tensorboard_time_series
from google.protobuf import timestamp_pb2  # type: ignore

__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "TimeSeriesData",
        "TimeSeriesDataPoint",
        "Scalar",
        "TensorboardTensor",
        "TensorboardBlobSequence",
        "TensorboardBlob",
    },
)


class TimeSeriesData(proto.Message):
  r"""All the data stored in a TensorboardTimeSeries.

    Attributes:
        tensorboard_time_series_id (str): Required. The ID of the
          TensorboardTimeSeries, which will become the final component of the
          TensorboardTimeSeries' resource name
        value_type
          (google.cloud.aiplatform_v1beta1.types.TensorboardTimeSeries.ValueType):
          Required. Immutable. The value type of this time series. All the
          values in this time series data must match this value type.
        values
          (Sequence[google.cloud.aiplatform_v1beta1.types.TimeSeriesDataPoint]):
          Required. Data points in this time series.
  """

  tensorboard_time_series_id = proto.Field(
      proto.STRING,
      number=1,
  )
  value_type = proto.Field(
      proto.ENUM,
      number=2,
      enum=tensorboard_time_series.TensorboardTimeSeries.ValueType,
  )
  values = proto.RepeatedField(
      proto.MESSAGE,
      number=3,
      message="TimeSeriesDataPoint",
  )


class TimeSeriesDataPoint(proto.Message):
  r"""A TensorboardTimeSeries data point.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof:
    https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        scalar (google.cloud.aiplatform_v1beta1.types.Scalar): A scalar value.
          This field is a member of `oneof`_ ``value``.
        tensor (google.cloud.aiplatform_v1beta1.types.TensorboardTensor): A
          tensor value.  This field is a member of `oneof`_ ``value``.
        blobs (google.cloud.aiplatform_v1beta1.types.TensorboardBlobSequence): A
          blob sequence value.  This field is a member of `oneof`_ ``value``.
        wall_time (google.protobuf.timestamp_pb2.Timestamp): Wall clock
          timestamp when this data point is generated by the end user.
        step (int): Step index of this data point within the run.
  """

  scalar = proto.Field(
      proto.MESSAGE,
      number=3,
      oneof="value",
      message="Scalar",
  )
  tensor = proto.Field(
      proto.MESSAGE,
      number=4,
      oneof="value",
      message="TensorboardTensor",
  )
  blobs = proto.Field(
      proto.MESSAGE,
      number=5,
      oneof="value",
      message="TensorboardBlobSequence",
  )
  wall_time = proto.Field(
      proto.MESSAGE,
      number=1,
      message=timestamp_pb2.Timestamp,
  )
  step = proto.Field(
      proto.INT64,
      number=2,
  )


class Scalar(proto.Message):
  r"""One point viewable on a scalar metric plot.

    Attributes:
        value (float): Value of the point at this step / timestamp.
  """

  value = proto.Field(
      proto.DOUBLE,
      number=1,
  )


class TensorboardTensor(proto.Message):
  r"""One point viewable on a tensor metric plot.

    Attributes:
        value (bytes): Required. Serialized form of
            https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/framework/tensor.proto
        version_number (int): Optional. Version number of TensorProto used to
          serialize
          [value][google.cloud.aiplatform.v1beta1.TensorboardTensor.value].
  """

  value = proto.Field(
      proto.BYTES,
      number=1,
  )
  version_number = proto.Field(
      proto.INT32,
      number=2,
  )


class TensorboardBlobSequence(proto.Message):
  r"""One point viewable on a blob metric plot, but mostly just a wrapper

    message to work around repeated fields can't be used directly within
    ``oneof`` fields.

    Attributes:
        values
          (Sequence[google.cloud.aiplatform_v1beta1.types.TensorboardBlob]):
          List of blobs contained within the sequence.
  """

  values = proto.RepeatedField(
      proto.MESSAGE,
      number=1,
      message="TensorboardBlob",
  )


class TensorboardBlob(proto.Message):
  r"""One blob (e.g, image, graph) viewable on a blob metric plot.

    Attributes:
        id (str): Output only. A URI safe key uniquely identifying a blob. Can
          be used to locate the blob stored in the Cloud Storage bucket of the
          consumer project.
        data (bytes): Optional. The bytes of the blob is not present unless it's
          returned by the ReadTensorboardBlobData endpoint.
  """

  id = proto.Field(
      proto.STRING,
      number=1,
  )
  data = proto.Field(
      proto.BYTES,
      number=2,
  )


__all__ = tuple(sorted(__protobuf__.manifest))
