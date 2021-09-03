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

from google.api import httpbody_pb2  # type: ignore
from google.cloud.aiplatform_v1beta1.types import explanation
from google.protobuf import struct_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "PredictRequest",
        "PredictResponse",
        "RawPredictRequest",
        "ExplainRequest",
        "ExplainResponse",
    },
)


class PredictRequest(proto.Message):
    r"""Request message for
    [PredictionService.Predict][google.cloud.aiplatform.v1beta1.PredictionService.Predict].

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
            [Model's][google.cloud.aiplatform.v1beta1.DeployedModel.model]
            [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
            [instance_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri].
        parameters (google.protobuf.struct_pb2.Value):
            The parameters that govern the prediction. The schema of the
            parameters may be specified via Endpoint's DeployedModels'
            [Model's
            ][google.cloud.aiplatform.v1beta1.DeployedModel.model]
            [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
            [parameters_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.parameters_schema_uri].
    """

    endpoint = proto.Field(proto.STRING, number=1,)
    instances = proto.RepeatedField(proto.MESSAGE, number=2, message=struct_pb2.Value,)
    parameters = proto.Field(proto.MESSAGE, number=3, message=struct_pb2.Value,)


class PredictResponse(proto.Message):
    r"""Response message for
    [PredictionService.Predict][google.cloud.aiplatform.v1beta1.PredictionService.Predict].

    Attributes:
        predictions (Sequence[google.protobuf.struct_pb2.Value]):
            The predictions that are the output of the predictions call.
            The schema of any single prediction may be specified via
            Endpoint's DeployedModels' [Model's
            ][google.cloud.aiplatform.v1beta1.DeployedModel.model]
            [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
            [prediction_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.prediction_schema_uri].
        deployed_model_id (str):
            ID of the Endpoint's DeployedModel that
            served this prediction.
    """

    predictions = proto.RepeatedField(
        proto.MESSAGE, number=1, message=struct_pb2.Value,
    )
    deployed_model_id = proto.Field(proto.STRING, number=2,)


class RawPredictRequest(proto.Message):
    r"""Request message for
    [PredictionService.RawPredict][google.cloud.aiplatform.v1beta1.PredictionService.RawPredict].

    Attributes:
        endpoint (str):
            Required. The name of the Endpoint requested to serve the
            prediction. Format:
            ``projects/{project}/locations/{location}/endpoints/{endpoint}``
        http_body (google.api.httpbody_pb2.HttpBody):
            The prediction input. Supports HTTP headers and arbitrary
            data payload.

            A
            [DeployedModel][google.cloud.aiplatform.v1beta1.DeployedModel]
            may have an upper limit on the number of instances it
            supports per request. When this limit it is exceeded for an
            AutoML model, the
            [RawPredict][google.cloud.aiplatform.v1beta1.PredictionService.RawPredict]
            method returns an error. When this limit is exceeded for a
            custom-trained model, the behavior varies depending on the
            model.

            You can specify the schema for each instance in the
            [predict_schemata.instance_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri]
            field when you create a
            [Model][google.cloud.aiplatform.v1beta1.Model]. This schema
            applies when you deploy the ``Model`` as a ``DeployedModel``
            to an [Endpoint][google.cloud.aiplatform.v1beta1.Endpoint]
            and use the ``RawPredict`` method.
    """

    endpoint = proto.Field(proto.STRING, number=1,)
    http_body = proto.Field(proto.MESSAGE, number=2, message=httpbody_pb2.HttpBody,)


class ExplainRequest(proto.Message):
    r"""Request message for
    [PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain].

    Attributes:
        endpoint (str):
            Required. The name of the Endpoint requested to serve the
            explanation. Format:
            ``projects/{project}/locations/{location}/endpoints/{endpoint}``
        instances (Sequence[google.protobuf.struct_pb2.Value]):
            Required. The instances that are the input to the
            explanation call. A DeployedModel may have an upper limit on
            the number of instances it supports per request, and when it
            is exceeded the explanation call errors in case of AutoML
            Models, or, in case of customer created Models, the
            behaviour is as documented by that Model. The schema of any
            single instance may be specified via Endpoint's
            DeployedModels'
            [Model's][google.cloud.aiplatform.v1beta1.DeployedModel.model]
            [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
            [instance_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri].
        parameters (google.protobuf.struct_pb2.Value):
            The parameters that govern the prediction. The schema of the
            parameters may be specified via Endpoint's DeployedModels'
            [Model's
            ][google.cloud.aiplatform.v1beta1.DeployedModel.model]
            [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
            [parameters_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.parameters_schema_uri].
        explanation_spec_override (google.cloud.aiplatform_v1beta1.types.ExplanationSpecOverride):
            If specified, overrides the
            [explanation_spec][google.cloud.aiplatform.v1beta1.DeployedModel.explanation_spec]
            of the DeployedModel. Can be used for explaining prediction
            results with different configurations, such as:

            -  Explaining top-5 predictions results as opposed to top-1;
            -  Increasing path count or step count of the attribution
               methods to reduce approximate errors;
            -  Using different baselines for explaining the prediction
               results.
        deployed_model_id (str):
            If specified, this ExplainRequest will be served by the
            chosen DeployedModel, overriding
            [Endpoint.traffic_split][google.cloud.aiplatform.v1beta1.Endpoint.traffic_split].
    """

    endpoint = proto.Field(proto.STRING, number=1,)
    instances = proto.RepeatedField(proto.MESSAGE, number=2, message=struct_pb2.Value,)
    parameters = proto.Field(proto.MESSAGE, number=4, message=struct_pb2.Value,)
    explanation_spec_override = proto.Field(
        proto.MESSAGE, number=5, message=explanation.ExplanationSpecOverride,
    )
    deployed_model_id = proto.Field(proto.STRING, number=3,)


class ExplainResponse(proto.Message):
    r"""Response message for
    [PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain].

    Attributes:
        explanations (Sequence[google.cloud.aiplatform_v1beta1.types.Explanation]):
            The explanations of the Model's
            [PredictResponse.predictions][google.cloud.aiplatform.v1beta1.PredictResponse.predictions].

            It has the same number of elements as
            [instances][google.cloud.aiplatform.v1beta1.ExplainRequest.instances]
            to be explained.
        deployed_model_id (str):
            ID of the Endpoint's DeployedModel that
            served this explanation.
        predictions (Sequence[google.protobuf.struct_pb2.Value]):
            The predictions that are the output of the predictions call.
            Same as
            [PredictResponse.predictions][google.cloud.aiplatform.v1beta1.PredictResponse.predictions].
    """

    explanations = proto.RepeatedField(
        proto.MESSAGE, number=1, message=explanation.Explanation,
    )
    deployed_model_id = proto.Field(proto.STRING, number=2,)
    predictions = proto.RepeatedField(
        proto.MESSAGE, number=3, message=struct_pb2.Value,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
