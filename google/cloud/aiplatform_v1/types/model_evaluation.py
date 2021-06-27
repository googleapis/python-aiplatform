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
    package="google.cloud.aiplatform.v1", manifest={"ModelEvaluation",},
)


class ModelEvaluation(proto.Message):
    r"""A collection of metrics calculated by comparing Model's
    predictions on all of the test data against annotations from the
    test data.

    Attributes:
        name (str):
            Output only. The resource name of the
            ModelEvaluation.
        metrics_schema_uri (str):
            Output only. Points to a YAML file stored on Google Cloud
            Storage describing the
            [metrics][google.cloud.aiplatform.v1.ModelEvaluation.metrics]
            of this ModelEvaluation. The schema is defined as an OpenAPI
            3.0.2 `Schema
            Object <https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md#schemaObject>`__.
        metrics (google.protobuf.struct_pb2.Value):
            Output only. Evaluation metrics of the Model. The schema of
            the metrics is stored in
            [metrics_schema_uri][google.cloud.aiplatform.v1.ModelEvaluation.metrics_schema_uri]
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            ModelEvaluation was created.
        slice_dimensions (Sequence[str]):
            Output only. All possible
            [dimensions][ModelEvaluationSlice.slice.dimension] of
            ModelEvaluationSlices. The dimensions can be used as the
            filter of the
            [ModelService.ListModelEvaluationSlices][google.cloud.aiplatform.v1.ModelService.ListModelEvaluationSlices]
            request, in the form of ``slice.dimension = <dimension>``.
    """

    name = proto.Field(proto.STRING, number=1,)
    metrics_schema_uri = proto.Field(proto.STRING, number=2,)
    metrics = proto.Field(proto.MESSAGE, number=3, message=struct_pb2.Value,)
    create_time = proto.Field(proto.MESSAGE, number=4, message=timestamp_pb2.Timestamp,)
    slice_dimensions = proto.RepeatedField(proto.STRING, number=5,)


__all__ = tuple(sorted(__protobuf__.manifest))
