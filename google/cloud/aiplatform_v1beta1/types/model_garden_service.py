# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
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
from __future__ import annotations

from typing import MutableMapping, MutableSequence

import proto  # type: ignore

from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import operation
from google.cloud.aiplatform_v1beta1.types import publisher_model as gca_publisher_model


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "PublisherModelView",
        "GetPublisherModelRequest",
        "ListPublisherModelsRequest",
        "ListPublisherModelsResponse",
        "DeployPublisherModelRequest",
        "DeployPublisherModelResponse",
        "DeployPublisherModelOperationMetadata",
    },
)


class PublisherModelView(proto.Enum):
    r"""View enumeration of PublisherModel.

    Values:
        PUBLISHER_MODEL_VIEW_UNSPECIFIED (0):
            The default / unset value. The API will
            default to the BASIC view.
        PUBLISHER_MODEL_VIEW_BASIC (1):
            Include basic metadata about the publisher
            model, but not the full contents.
        PUBLISHER_MODEL_VIEW_FULL (2):
            Include everything.
        PUBLISHER_MODEL_VERSION_VIEW_BASIC (3):
            Include: VersionId, ModelVersionExternalName,
            and SupportedActions.
    """
    PUBLISHER_MODEL_VIEW_UNSPECIFIED = 0
    PUBLISHER_MODEL_VIEW_BASIC = 1
    PUBLISHER_MODEL_VIEW_FULL = 2
    PUBLISHER_MODEL_VERSION_VIEW_BASIC = 3


class GetPublisherModelRequest(proto.Message):
    r"""Request message for
    [ModelGardenService.GetPublisherModel][google.cloud.aiplatform.v1beta1.ModelGardenService.GetPublisherModel]

    Attributes:
        name (str):
            Required. The name of the PublisherModel resource. Format:
            ``publishers/{publisher}/models/{publisher_model}``
        language_code (str):
            Optional. The IETF BCP-47 language code
            representing the language in which the publisher
            model's text information should be written in.
        view (google.cloud.aiplatform_v1beta1.types.PublisherModelView):
            Optional. PublisherModel view specifying
            which fields to read.
        is_hugging_face_model (bool):
            Optional. Boolean indicates whether the
            requested model is a Hugging Face model.
        hugging_face_token (str):
            Optional. Token used to access Hugging Face
            gated models.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    language_code: str = proto.Field(
        proto.STRING,
        number=2,
    )
    view: "PublisherModelView" = proto.Field(
        proto.ENUM,
        number=3,
        enum="PublisherModelView",
    )
    is_hugging_face_model: bool = proto.Field(
        proto.BOOL,
        number=5,
    )
    hugging_face_token: str = proto.Field(
        proto.STRING,
        number=6,
    )


class ListPublisherModelsRequest(proto.Message):
    r"""Request message for
    [ModelGardenService.ListPublisherModels][google.cloud.aiplatform.v1beta1.ModelGardenService.ListPublisherModels].

    Attributes:
        parent (str):
            Required. The name of the Publisher from which to list the
            PublisherModels. Format: ``publishers/{publisher}``
        filter (str):
            Optional. The standard list filter.
        page_size (int):
            Optional. The standard list page size.
        page_token (str):
            Optional. The standard list page token. Typically obtained
            via
            [ListPublisherModelsResponse.next_page_token][google.cloud.aiplatform.v1beta1.ListPublisherModelsResponse.next_page_token]
            of the previous
            [ModelGardenService.ListPublisherModels][google.cloud.aiplatform.v1beta1.ModelGardenService.ListPublisherModels]
            call.
        view (google.cloud.aiplatform_v1beta1.types.PublisherModelView):
            Optional. PublisherModel view specifying
            which fields to read.
        order_by (str):
            Optional. A comma-separated list of fields to
            order by, sorted in ascending order. Use "desc"
            after a field name for descending.
        language_code (str):
            Optional. The IETF BCP-47 language code
            representing the language in which the publisher
            models' text information should be written in.
            If not set, by default English (en).
        list_all_versions (bool):
            Optional. List all publisher model versions
            if the flag is set to true.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    filter: str = proto.Field(
        proto.STRING,
        number=2,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=3,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=4,
    )
    view: "PublisherModelView" = proto.Field(
        proto.ENUM,
        number=5,
        enum="PublisherModelView",
    )
    order_by: str = proto.Field(
        proto.STRING,
        number=6,
    )
    language_code: str = proto.Field(
        proto.STRING,
        number=7,
    )
    list_all_versions: bool = proto.Field(
        proto.BOOL,
        number=8,
    )


class ListPublisherModelsResponse(proto.Message):
    r"""Response message for
    [ModelGardenService.ListPublisherModels][google.cloud.aiplatform.v1beta1.ModelGardenService.ListPublisherModels].

    Attributes:
        publisher_models (MutableSequence[google.cloud.aiplatform_v1beta1.types.PublisherModel]):
            List of PublisherModels in the requested
            page.
        next_page_token (str):
            A token to retrieve next page of results. Pass to
            [ListPublisherModels.page_token][] to obtain that page.
    """

    @property
    def raw_page(self):
        return self

    publisher_models: MutableSequence[
        gca_publisher_model.PublisherModel
    ] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=gca_publisher_model.PublisherModel,
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class DeployPublisherModelRequest(proto.Message):
    r"""Request message for
    [ModelGardenService.DeployPublisherModel][google.cloud.aiplatform.v1beta1.ModelGardenService.DeployPublisherModel].

    Attributes:
        model (str):
            Required. The name of the PublisherModel resource. Format:
            ``publishers/{publisher}/models/{publisher_model}@{version_id}``,
            or
            ``publishers/hf-{hugging-face-author}/models/{hugging-face-model-name}@001``
            or Hugging Face model ID like ``google/gemma-2-2b-it``.
        destination (str):
            Required. The resource name of the Location to deploy the
            model in. Format:
            ``projects/{project}/locations/{location}``
        endpoint_display_name (str):
            Optional. The user-specified display name of
            the endpoint. If not set, a default name will be
            used.
        dedicated_resources (google.cloud.aiplatform_v1beta1.types.DedicatedResources):
            Optional. The dedicated resources to use for
            the endpoint. If not set, the default resources
            will be used.
        model_display_name (str):
            Optional. The user-specified display name of
            the uploaded model. If not set, a default name
            will be used.
        hugging_face_access_token (str):
            Optional. The Hugging Face read access token
            used to access the model artifacts of gated
            models.
        accept_eula (bool):
            Optional. Whether the user accepts the End
            User License Agreement (EULA) for the model.
    """

    model: str = proto.Field(
        proto.STRING,
        number=1,
    )
    destination: str = proto.Field(
        proto.STRING,
        number=2,
    )
    endpoint_display_name: str = proto.Field(
        proto.STRING,
        number=3,
    )
    dedicated_resources: machine_resources.DedicatedResources = proto.Field(
        proto.MESSAGE,
        number=4,
        message=machine_resources.DedicatedResources,
    )
    model_display_name: str = proto.Field(
        proto.STRING,
        number=5,
    )
    hugging_face_access_token: str = proto.Field(
        proto.STRING,
        number=6,
    )
    accept_eula: bool = proto.Field(
        proto.BOOL,
        number=7,
    )


class DeployPublisherModelResponse(proto.Message):
    r"""Response message for
    [ModelGardenService.DeployPublisherModel][google.cloud.aiplatform.v1beta1.ModelGardenService.DeployPublisherModel].

    Attributes:
        publisher_model (str):
            Output only. The name of the PublisherModel resource.
            Format:
            ``publishers/{publisher}/models/{publisher_model}@{version_id}``,
            or
            ``publishers/hf-{hugging-face-author}/models/{hugging-face-model-name}@001``
        endpoint (str):
            Output only. The name of the Endpoint created. Format:
            ``projects/{project}/locations/{location}/endpoints/{endpoint}``
        model (str):
            Output only. The name of the Model created. Format:
            ``projects/{project}/locations/{location}/models/{model}``
    """

    publisher_model: str = proto.Field(
        proto.STRING,
        number=1,
    )
    endpoint: str = proto.Field(
        proto.STRING,
        number=2,
    )
    model: str = proto.Field(
        proto.STRING,
        number=3,
    )


class DeployPublisherModelOperationMetadata(proto.Message):
    r"""Runtime operation information for
    [ModelGardenService.DeployPublisherModel][google.cloud.aiplatform.v1beta1.ModelGardenService.DeployPublisherModel].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            The operation generic information.
        publisher_model (str):
            Output only. The name of the PublisherModel resource.
            Format:
            ``publishers/{publisher}/models/{publisher_model}@{version_id}``,
            or
            ``publishers/hf-{hugging-face-author}/models/{hugging-face-model-name}@001``
        destination (str):
            Output only. The resource name of the Location to deploy the
            model in. Format:
            ``projects/{project}/locations/{location}``
        project_number (int):
            Output only. The project number where the
            deploy model request is sent.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )
    publisher_model: str = proto.Field(
        proto.STRING,
        number=2,
    )
    destination: str = proto.Field(
        proto.STRING,
        number=3,
    )
    project_number: int = proto.Field(
        proto.INT64,
        number=4,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
