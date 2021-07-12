# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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

from typing import Optional, Sequence, Dict, Tuple

from google.api_core import operation
from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import base
from google.cloud.aiplatform import compat
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils

from google.cloud.aiplatform.compat.services import tensorboard_service_client_v1beta1

from google.cloud.aiplatform.compat.types import (
    tensorboard_v1beta1 as gca_tensorboard,
    encryption_spec_v1beta1 as gca_encryption_spec,
)

from google.protobuf import field_mask_pb2

_LOGGER = base.Logger(__name__)


class Tensorboard(base.VertexAiResourceNounWithFutureManager):
    """Managed tensorboard resource for Vertex AI."""

    client_class = utils.TensorboardClientWithOverride
    _is_client_prediction_client = False
    _resource_noun = "tensorboards"
    _getter_method = "get_tensorboard"
    _list_method = "list_tensorboards"
    _delete_method = "delete_tensorboard"

    _supported_metadata_schema_uris: Tuple[str] = ()

    def __init__(
        self,
        tensorboard_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing managed tensorboard given a tensorboard name or ID.

    Args:
        tensorboard_name (str):
            Required. A fully-qualified tensorboard resource name or tensorboard ID.
            Example: "projects/123/locations/us-central1/tensorboards/456" or
            "456" when project and location are initialized or passed.
        project (str):
            Optional project to retrieve tensorboard from. If not set, project
            set in aiplatform.init will be used.
        location (str):
            Optional location to retrieve tensorboard from. If not set, location
            set in aiplatform.init will be used.
        credentials (auth_credentials.Credentials):
            Custom credentials to use to retreive this Tensorboard. Overrides
            credentials set in aiplatform.init.
    """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=tensorboard_name,
        )
        self._gca_resource = self._get_gca_resource(resource_name=tensorboard_name)

    @classmethod
    def create(
        cls,
        display_name: str,
        description: Optional[str] = None,
        labels: Optional[Dict] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
    ) -> "Tensorboard":
        """Creates a new tensorboard.

    Args:
        display_name (str):
            Required. The user-defined name of the Tensorboard.
            The name can be up to 128 characters long and can be consist
            of any UTF-8 characters.
        description (str):
            Description of this Tensorboard.
        labels (str):
            The labels with user-defined metadata to organize your Tensorboards.
            Label keys and values can be no longer than 64 characters
            (Unicode codepoints), can only contain lowercase letters, numeric
            characters, underscores and dashes. International characters are allowed.
            No more than 64 user labels can be associated with one Tensorboard
            (System labels are excluded).
            See https://goo.gl/xmQnxf for more information and examples of labels.
            System reserved label keys are prefixed with "aiplatform.googleapis.com/"
            and are immutable.
        project (str):
            Project to upload this model to. Overrides project set in
            aiplatform.init.
        location (str):
            Location to upload this model to. Overrides location set in
            aiplatform.init.
        credentials (auth_credentials.Credentials):
            Custom credentials to use to upload this model. Overrides
            credentials set in aiplatform.init.
        request_metadata (Sequence[Tuple[str, str]]):
            Strings which should be sent along with the request as metadata.
        encryption_spec_key_name (str):
            The Cloud KMS resource identifier of the customer
            managed encryption key used to protect the tensorboard. Has the
            form:
            ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
            The key needs to be in the same region as where the compute
            resource is created.

            If set, this Tensorboard and all sub-resources of this Tensorboard will be secured by this key.

            Overrides encryption_spec_key_name set in aiplatform.init.

    Returns:
        tensorboard (Tensorboard):
            Instantiated representation of the managed tensorboard resource.
    """

        utils.validate_display_name(display_name)

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        return cls._create(
            api_client=api_client,
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            project=project or initializer.global_config.project,
            location=location or initializer.global_config.location,
            display_name=display_name,
            description=description,
            labels=labels,
            request_metadata=request_metadata,
            encryption_spec=initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name,
                select_version=compat.V1BETA1,
            ),
        )

    @classmethod
    def _create(
        cls,
        api_client: tensorboard_service_client_v1beta1.TensorboardServiceClient,
        parent: str,
        project: str,
        location: str,
        display_name: str,
        description: Optional[str] = None,
        labels: Optional[Dict] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec: Optional[gca_encryption_spec.EncryptionSpec] = None,
    ) -> operation.Operation:
        """Creates a new managed tensorboard by directly calling API client.

    Args:
        api_client (tensorboard_service_client.TensorboardServiceClient):
            Required. An instance of TensorboardServiceClient with the correct api_endpoint
            already set based on user's preferences.
        parent (str):
            Required. Also known as common location path, that usually contains the
            project and location that the user provided to the upstream method.
            Example: "projects/my-prj/locations/us-central1"
        project (str):
            Required. Project to retrieve endpoint from. If not set, project
            set in aiplatform.init will be used.
        location (str):
            Required. Location to retrieve endpoint from. If not set, location
            set in aiplatform.init will be used.
        display_name (str):
            Required. The user-defined name of the Tensorboard.
            The name can be up to 128 characters long and can be consist
            of any UTF-8 characters.
        description (str):
            Description of this Tensorboard.
        labels (str):
            The labels with user-defined metadata to organize your Tensorboards.
            Label keys and values can be no longer than 64 characters
            (Unicode codepoints), can only contain lowercase letters, numeric
            characters, underscores and dashes. International characters are allowed.
            No more than 64 user labels can be associated with one Tensorboard
            (System labels are excluded).
            See https://goo.gl/xmQnxf for more information and examples of labels.
            System reserved label keys are prefixed with "aiplatform.googleapis.com/"
            and are immutable.
        request_metadata (Sequence[Tuple[str, str]]):
            Strings which should be sent along with the create_tensorboard
            request as metadata. Usually to specify special tensorboard config.
        credentials (auth_credentials.Credentials):
            Custom credentials to use to upload this model. Overrides
            credentials set in aiplatform.init.
        encryption_spec (gca_encryption_spec.EncryptionSpec):
            The Cloud KMS customer managed encryption key used to protect the tensorboard.
            The key needs to be in the same region as where the compute
            resource is created.

            If set, this Tensorboard and all sub-resources of this Tensorboard will be secured by this key.
    Returns:
        operation (Operation):
            An object representing a long-running operation.
    """

        gapic_tensorboard = gca_tensorboard.Tensorboard(
            display_name=display_name,
            description=description,
            labels=labels,
            encryption_spec=encryption_spec,
        )

        create_tensorboard_lro = api_client.create_tensorboard(
            parent=parent, tensorboard=gapic_tensorboard, metadata=request_metadata
        )

        _LOGGER.log_create_with_lro(cls, create_tensorboard_lro)

        created_tensorboard = create_tensorboard_lro.result()

        _LOGGER.log_create_complete(cls, created_tensorboard, "tb")

        return cls(
            tensorboard_name=created_tensorboard.name,
            project=project,
            location=location,
            credentials=credentials,
        )

    def update(
        self,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[Dict] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
    ) -> "Tensorboard":
        """Updates an existing tensorboard.

    Args:
        display_name (str):
            The user-defined name of the Tensorboard.
            The name can be up to 128 characters long and can be consist
            of any UTF-8 characters.
        description (str):
            Description of this Tensorboard.
        labels (Dict):
            The labels with user-defined metadata to organize your Tensorboards.
            Label keys and values can be no longer than 64 characters
            (Unicode codepoints), can only contain lowercase letters, numeric
            characters, underscores and dashes. International characters are allowed.
            No more than 64 user labels can be associated with one Tensorboard
            (System labels are excluded).
            See https://goo.gl/xmQnxf for more information and examples of labels.
            System reserved label keys are prefixed with "aiplatform.googleapis.com/"
            and are immutable.
        request_metadata (Sequence[Tuple[str, str]]):
            Strings which should be sent along with the request as metadata.
        encryption_spec_key_name (str):
            The Cloud KMS resource identifier of the customer
            managed encryption key used to protect the tensorboard. Has the
            form:
            ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
            The key needs to be in the same region as where the compute
            resource is created.

            If set, this Tensorboard and all sub-resources of this Tensorboard will be secured by this key.

            Overrides encryption_spec_key_name set in aiplatform.init.

    Returns:
        tensorboard (Tensorboard):
            The managed tensorboard resource.
    """
        update_mask = list()

        if display_name:
            utils.validate_display_name(display_name)
            update_mask.append("display_name")

        if description:
            update_mask.append("description")

        if labels:
            update_mask.append("labels")

        encryption_spec = None
        if encryption_spec_key_name:
            encryption_spec = initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name,
                select_version=compat.V1BETA1,
            )
            update_mask.append("encryption_spec")

        return self._update(
            display_name=display_name,
            description=description,
            labels=labels,
            encryption_spec=encryption_spec,
            update_mask=update_mask,
            request_metadata=request_metadata,
        )

    def _update(
        self,
        update_mask: Sequence[str] = (),
        request_metadata: Sequence[Tuple[str, str]] = (),
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[Dict] = None,
        encryption_spec: Optional[gca_encryption_spec.EncryptionSpec] = None,
    ) -> operation.Operation:
        """Updates a managed tensorboard by directly calling API client.

    Args:
        update_mask (Sequence[str]):
          Field mask is used to specify the fields to be overwritten in the
          Tensorboard resource by the update.
          The fields specified in the update_mask are relative to the resource, not
          the full request. A field will be overwritten if it is in the mask. If the
          user does not provide a mask then all fields will be overwritten if new
          values are specified.
        request_metadata (Sequence[Tuple[str, str]]):
            Strings which should be sent along with the create_tensorboard
            request as metadata. Usually to specify special tensorboard config.
        display_name (str):
            The user-defined name of the Tensorboard.
            The name can be up to 128 characters long and can be consist
            of any UTF-8 characters.
        description (str):
            Description of this Tensorboard.
        encryption_spec (gca_encryption_spec.EncryptionSpec):
            The Cloud KMS customer managed encryption key used to protect the tensorboard.
            The key needs to be in the same region as where the compute
            resource is created.

            If set, this Tensorboard and all sub-resources of this Tensorboard will be secured by this key.
    Returns:
        operation (Operation):
            An object representing a long-running operation.
    """

        update_mask = field_mask_pb2.FieldMask(paths=update_mask)

        gapic_tensorboard = gca_tensorboard.Tensorboard(
            display_name=display_name,
            description=description,
            labels=labels,
            encryption_spec=encryption_spec,
        )

        _LOGGER.log_action_start_against_resource(
            "Updating", "tensorboard", self,
        )

        update_tensorboard_lro = self.api_client.update_tensorboard(
            tensorboard=gapic_tensorboard,
            update_mask=update_mask,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Update", "tensorboard", self.__class__, update_tensorboard_lro
        )

        update_tensorboard_lro.result()

        _LOGGER.log_action_completed_against_resource("tensorboard", "updated", self)

        return self
