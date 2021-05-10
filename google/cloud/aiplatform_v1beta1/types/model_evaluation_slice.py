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

from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1", manifest={"ModelEvaluationSlice",},
)


class ModelEvaluationSlice(proto.Message):
    r"""A collection of metrics calculated by comparing Model's
    predictions on a slice of the test data against ground truth
    annotations.

    Attributes:
        name (str):
            Output only. The resource name of the
            ModelEvaluationSlice.
        slice_ (google.cloud.aiplatform_v1beta1.types.ModelEvaluationSlice.Slice):
            Output only. The slice of the test data that
            is used to evaluate the Model.
        metrics_schema_uri (str):
            Output only. Points to a YAML file stored on Google Cloud
            Storage describing the
            [metrics][google.cloud.aiplatform.v1beta1.ModelEvaluationSlice.metrics]
            of this ModelEvaluationSlice. The schema is defined as an
            OpenAPI 3.0.2 `Schema
            Object <https://tinyurl.com/y538mdwt#schema-object>`__.
        metrics (google.protobuf.struct_pb2.Value):
            Output only. Sliced evaluation metrics of the Model. The
            schema of the metrics is stored in
            [metrics_schema_uri][google.cloud.aiplatform.v1beta1.ModelEvaluationSlice.metrics_schema_uri]
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            ModelEvaluationSlice was created.
    """

    class Slice(proto.Message):
        r"""Definition of a slice.
        Attributes:
            dimension (str):
                Output only. The dimension of the slice. Well-known
                dimensions are:

                -  ``annotationSpec``: This slice is on the test data that
                   has either ground truth or prediction with
                   [AnnotationSpec.display_name][google.cloud.aiplatform.v1beta1.AnnotationSpec.display_name]
                   equals to
                   [value][google.cloud.aiplatform.v1beta1.ModelEvaluationSlice.Slice.value].
            value (str):
                Output only. The value of the dimension in
                this slice.
        """

        dimension = proto.Field(proto.STRING, number=1,)
        value = proto.Field(proto.STRING, number=2,)

    name = proto.Field(proto.STRING, number=1,)
    slice_ = proto.Field(proto.MESSAGE, number=2, message=Slice,)
    metrics_schema_uri = proto.Field(proto.STRING, number=3,)
    metrics = proto.Field(proto.MESSAGE, number=4, message=struct_pb2.Value,)
    create_time = proto.Field(proto.MESSAGE, number=5, message=timestamp_pb2.Timestamp,)


__all__ = tuple(sorted(__protobuf__.manifest))
