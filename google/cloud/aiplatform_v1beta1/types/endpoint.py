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
from google.cloud.aiplatform_v1beta1.types import explanation
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1", manifest={"Endpoint", "DeployedModel",},
)


class Endpoint(proto.Message):
    r"""Models are deployed into it, and afterwards Endpoint is
    called to obtain predictions and explanations.

    Attributes:
        name (str):
            Output only. The resource name of the
            Endpoint.
        display_name (str):
            Required. The display name of the Endpoint.
            The name can be up to 128 characters long and
            can be consist of any UTF-8 characters.
        description (str):
            The description of the Endpoint.
        deployed_models (Sequence[google.cloud.aiplatform_v1beta1.types.DeployedModel]):
            Output only. The models deployed in this Endpoint. To add or
            remove DeployedModels use
            [EndpointService.DeployModel][google.cloud.aiplatform.v1beta1.EndpointService.DeployModel]
            and
            [EndpointService.UndeployModel][google.cloud.aiplatform.v1beta1.EndpointService.UndeployModel]
            respectively.
        traffic_split (Sequence[google.cloud.aiplatform_v1beta1.types.Endpoint.TrafficSplitEntry]):
            A map from a DeployedModel's ID to the
            percentage of this Endpoint's traffic that
            should be forwarded to that DeployedModel.
            If a DeployedModel's ID is not listed in this
            map, then it receives no traffic.

            The traffic percentage values must add up to
            100, or map must be empty if the Endpoint is to
            not accept any traffic at a moment.
        etag (str):
            Used to perform consistent read-modify-write
            updates. If not set, a blind "overwrite" update
            happens.
        labels (Sequence[google.cloud.aiplatform_v1beta1.types.Endpoint.LabelsEntry]):
            The labels with user-defined metadata to
            organize your Endpoints.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            and examples of labels.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this Endpoint was
            created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this Endpoint was
            last updated.
        encryption_spec (google.cloud.aiplatform_v1beta1.types.EncryptionSpec):
            Customer-managed encryption key spec for an
            Endpoint. If set, this Endpoint and all sub-
            resources of this Endpoint will be secured by
            this key.
    """

    name = proto.Field(proto.STRING, number=1,)
    display_name = proto.Field(proto.STRING, number=2,)
    description = proto.Field(proto.STRING, number=3,)
    deployed_models = proto.RepeatedField(
        proto.MESSAGE, number=4, message="DeployedModel",
    )
    traffic_split = proto.MapField(proto.STRING, proto.INT32, number=5,)
    etag = proto.Field(proto.STRING, number=6,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=7,)
    create_time = proto.Field(proto.MESSAGE, number=8, message=timestamp_pb2.Timestamp,)
    update_time = proto.Field(proto.MESSAGE, number=9, message=timestamp_pb2.Timestamp,)
    encryption_spec = proto.Field(
        proto.MESSAGE, number=10, message=gca_encryption_spec.EncryptionSpec,
    )


class DeployedModel(proto.Message):
    r"""A deployment of a Model. Endpoints contain one or more
    DeployedModels.

    Attributes:
        dedicated_resources (google.cloud.aiplatform_v1beta1.types.DedicatedResources):
            A description of resources that are dedicated
            to the DeployedModel, and that need a higher
            degree of manual configuration.
        automatic_resources (google.cloud.aiplatform_v1beta1.types.AutomaticResources):
            A description of resources that to large
            degree are decided by AI Platform, and require
            only a modest additional configuration.
        id (str):
            Output only. The ID of the DeployedModel.
        model (str):
            Required. The name of the Model that this is
            the deployment of. Note that the Model may be in
            a different location than the DeployedModel's
            Endpoint.
        display_name (str):
            The display name of the DeployedModel. If not provided upon
            creation, the Model's display_name is used.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when the DeployedModel
            was created.
        explanation_spec (google.cloud.aiplatform_v1beta1.types.ExplanationSpec):
            Explanation configuration for this DeployedModel.

            When deploying a Model using
            [EndpointService.DeployModel][google.cloud.aiplatform.v1beta1.EndpointService.DeployModel],
            this value overrides the value of
            [Model.explanation_spec][google.cloud.aiplatform.v1beta1.Model.explanation_spec].
            All fields of
            [explanation_spec][google.cloud.aiplatform.v1beta1.DeployedModel.explanation_spec]
            are optional in the request. If a field of
            [explanation_spec][google.cloud.aiplatform.v1beta1.DeployedModel.explanation_spec]
            is not populated, the value of the same field of
            [Model.explanation_spec][google.cloud.aiplatform.v1beta1.Model.explanation_spec]
            is inherited. If the corresponding
            [Model.explanation_spec][google.cloud.aiplatform.v1beta1.Model.explanation_spec]
            is not populated, all fields of the
            [explanation_spec][google.cloud.aiplatform.v1beta1.DeployedModel.explanation_spec]
            will be used for the explanation configuration.
        service_account (str):
            The service account that the DeployedModel's container runs
            as. Specify the email address of the service account. If
            this service account is not specified, the container runs as
            a service account that doesn't have access to the resource
            project.

            Users deploying the Model must have the
            ``iam.serviceAccounts.actAs`` permission on this service
            account.
        enable_container_logging (bool):
            If true, the container of the DeployedModel instances will
            send ``stderr`` and ``stdout`` streams to Stackdriver
            Logging.

            Only supported for custom-trained Models and AutoML Tabular
            Models.
        enable_access_logging (bool):
            These logs are like standard server access
            logs, containing information like timestamp and
            latency for each prediction request.
            Note that Stackdriver logs may incur a cost,
            especially if your project receives prediction
            requests at a high queries per second rate
            (QPS). Estimate your costs before enabling this
            option.
    """

    dedicated_resources = proto.Field(
        proto.MESSAGE,
        number=7,
        oneof="prediction_resources",
        message=machine_resources.DedicatedResources,
    )
    automatic_resources = proto.Field(
        proto.MESSAGE,
        number=8,
        oneof="prediction_resources",
        message=machine_resources.AutomaticResources,
    )
    id = proto.Field(proto.STRING, number=1,)
    model = proto.Field(proto.STRING, number=2,)
    display_name = proto.Field(proto.STRING, number=3,)
    create_time = proto.Field(proto.MESSAGE, number=6, message=timestamp_pb2.Timestamp,)
    explanation_spec = proto.Field(
        proto.MESSAGE, number=9, message=explanation.ExplanationSpec,
    )
    service_account = proto.Field(proto.STRING, number=11,)
    enable_container_logging = proto.Field(proto.BOOL, number=12,)
    enable_access_logging = proto.Field(proto.BOOL, number=13,)


__all__ = tuple(sorted(__protobuf__.manifest))
