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


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={"PredictRequest", "PredictResponse",},
)


class PredictRequest(proto.Message):
    r"""Request message for
    [PredictionService.Predict][google.cloud.aiplatform.v1.PredictionService.Predict].

    Attributes:
        endpoint (str):
            Required. The name of the Endpoint requested to serve the
            prediction. Format:
            ``projects/{project}/locations/{location}/endpoints/{endpoint}``
        instances (Sequence[google.protobuf.struct_pb2.Value]):
            Required. The instances that are the input to the prediction
            call. A DeployedModel may have an upper limit on the number
            of instances it supports per request, and when it is
            exceeded the prediction call errors in case of AutoML
            Models, or, in case of customer created Models, the
            behaviour is as documented by that Model. The schema of any
            single instance may be specified via Endpoint's
            DeployedModels'
            [Model's][google.cloud.aiplatform.v1.DeployedModel.model]
            [PredictSchemata's][google.cloud.aiplatform.v1.Model.predict_schemata]
            [instance_schema_uri][google.cloud.aiplatform.v1.PredictSchemata.instance_schema_uri].
        parameters (google.protobuf.struct_pb2.Value):
            The parameters that govern the prediction. The schema of the
            parameters may be specified via Endpoint's DeployedModels'
            [Model's ][google.cloud.aiplatform.v1.DeployedModel.model]
            [PredictSchemata's][google.cloud.aiplatform.v1.Model.predict_schemata]
            [parameters_schema_uri][google.cloud.aiplatform.v1.PredictSchemata.parameters_schema_uri].
    """

    endpoint = proto.Field(proto.STRING, number=1,)
    instances = proto.RepeatedField(proto.MESSAGE, number=2, message=struct_pb2.Value,)
    parameters = proto.Field(proto.MESSAGE, number=3, message=struct_pb2.Value,)


class PredictResponse(proto.Message):
    r"""Response message for
    [PredictionService.Predict][google.cloud.aiplatform.v1.PredictionService.Predict].

    Attributes:
        predictions (Sequence[google.protobuf.struct_pb2.Value]):
            The predictions that are the output of the predictions call.
            The schema of any single prediction may be specified via
            Endpoint's DeployedModels' [Model's
            ][google.cloud.aiplatform.v1.DeployedModel.model]
            [PredictSchemata's][google.cloud.aiplatform.v1.Model.predict_schemata]
            [prediction_schema_uri][google.cloud.aiplatform.v1.PredictSchemata.prediction_schema_uri].
        deployed_model_id (str):
            ID of the Endpoint's DeployedModel that
            served this prediction.
    """

    predictions = proto.RepeatedField(
        proto.MESSAGE, number=1, message=struct_pb2.Value,
    )
    deployed_model_id = proto.Field(proto.STRING, number=2,)


__all__ = tuple(sorted(__protobuf__.manifest))
