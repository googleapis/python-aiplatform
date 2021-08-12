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

from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import base
from google.cloud.aiplatform import compat
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils


from google.cloud.aiplatform.compat.types import tensorboard_v1beta1 as gca_tensorboard

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
                Optional. Project to retrieve tensorboard from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve tensorboard from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this Tensorboard. Overrides
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
        labels: Optional[Dict[str, str]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
    ) -> "Tensorboard":
        """Creates a new tensorboard.

        Example Usage:

            tb = aiplatform.Tensorboard.create(
                display_name='my display name',
                description='my description',
                labels={
                    'key1': 'value1',
                    'key2': 'value2'
                }
            )

        Args:
            display_name (str):
                Required. The user-defined name of the Tensorboard.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            description (str):
                Optional. Description of this Tensorboard.
            labels (Dict[str, str]):
                Optional. Labels with user-defined metadata to organize your Tensorboards.
                Label keys and values can be no longer than 64 characters
                (Unicode codepoints), can only contain lowercase letters, numeric
                characters, underscores and dashes. International characters are allowed.
                No more than 64 user labels can be associated with one Tensorboard
                (System labels are excluded).
                See https://goo.gl/xmQnxf for more information and examples of labels.
                System reserved label keys are prefixed with "aiplatform.googleapis.com/"
                and are immutable.
            project (str):
                Optional. Project to upload this model to. Overrides project set in
                aiplatform.init.
            location (str):
                Optional. Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            encryption_spec_key_name (str):
                Optional. Cloud KMS resource identifier of the customer
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
        if labels:
            utils.validate_labels(labels)

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        parent = initializer.global_config.common_location_path(
            project=project, location=location
        )

        encryption_spec = initializer.global_config.get_encryption_spec(
            encryption_spec_key_name=encryption_spec_key_name,
            select_version=compat.V1BETA1,
        )

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
            project=project or initializer.global_config.project,
            location=location or initializer.global_config.location,
            credentials=credentials,
        )

    def update(
        self,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
    ) -> "Tensorboard":
        """Updates an existing tensorboard.

        Example Usage:

            tb = aiplatform.Tensorboard(tensorboard_name='123456')
            tb.update(
                display_name='update my display name',
                description='update my description',
            )

        Args:
            display_name (str):
                Optional. User-defined name of the Tensorboard.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            description (str):
                Optional. Description of this Tensorboard.
            labels (Dict[str, str]):
                Optional. Labels with user-defined metadata to organize your Tensorboards.
                Label keys and values can be no longer than 64 characters
                (Unicode codepoints), can only contain lowercase letters, numeric
                characters, underscores and dashes. International characters are allowed.
                No more than 64 user labels can be associated with one Tensorboard
                (System labels are excluded).
                See https://goo.gl/xmQnxf for more information and examples of labels.
                System reserved label keys are prefixed with "aiplatform.googleapis.com/"
                and are immutable.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            encryption_spec_key_name (str):
                Optional. Cloud KMS resource identifier of the customer
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
            utils.validate_labels(labels)
            update_mask.append("labels")

        encryption_spec = None
        if encryption_spec_key_name:
            encryption_spec = initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name,
                select_version=compat.V1BETA1,
            )
            update_mask.append("encryption_spec")

        update_mask = field_mask_pb2.FieldMask(paths=update_mask)

        gapic_tensorboard = gca_tensorboard.Tensorboard(
            name=self.resource_name,
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
