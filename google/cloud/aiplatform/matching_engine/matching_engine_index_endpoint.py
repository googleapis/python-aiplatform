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

from typing import Dict, Optional, Sequence, Tuple

from google.auth import credentials as auth_credentials
from google.protobuf import field_mask_pb2

from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat.types import (
    matching_engine_index_endpoint as gca_matching_engine_index_endpoint,
)
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils

from google.cloud.aiplatform import matching_engine

_LOGGER = base.Logger(__name__)


class MatchingEngineIndexEndpoint(base.VertexAiResourceNounWithFutureManager):
    """Matching Engine index endpoint resource for Vertex AI."""

    client_class = utils.IndexEndpointClientWithOverride

    _resource_noun = "indexEndpoints"
    _getter_method = "get_index_endpoint"
    _list_method = "list_index_endpoints"
    _delete_method = "delete_index_endpoint"
    _parse_resource_name_method = "parse_index_endpoint_path"
    _format_resource_name_method = "index_endpoint_path"

    def __init__(
        self,
        index_endpoint_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing index endpoint given a name or ID.

        Example Usage:

            my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
                index_endpoint_name='projects/123/locations/us-central1/index_endpoint/my_index_id'
            )
            or
            my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
                index_endpoint_name='my_index_endpoint_id'
            )

        Args:
            index_endpoint_name (str):
                Required. A fully-qualified index endpoint resource name or a index ID.
                Example: "projects/123/locations/us-central1/index_endpoints/my_index_id"
                or "my_index_id" when project and location are initialized or passed.
            project (str):
                Optional. Project to retrieve index endpoint from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve index endpoint from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this IndexEndpoint. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=index_endpoint_name,
        )
        self._gca_resource = self._get_gca_resource(resource_name=index_endpoint_name)

    @classmethod
    @base.optional_sync()
    def create(
        cls,
        index_id: str,
        display_name: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "MatchingEngineIndexEndpoint":
        """Creates a MatchingEngineIndexEndpoint resource.

        Example Usage:

            my_index_endpoint = aiplatform.IndexEndpoint.create(
                index_id='my_index_id',
            )

        Args:
            index_id (str):
                Required. The ID to use for this index endpoint, which will
                become the final component of the index endpoint's resource
                name.

                This value may be up to 60 characters, and valid characters
                are ``[a-z0-9_]``. The first character cannot be a number.

                The value must be unique within the project and location.
            display_name (str):
                Required. The display name of the IndexEndpoint.
                The name can be up to 128 characters long and
                can be consist of any UTF-8 characters.
            description (str):
                The description of the IndexEndpoint.
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your IndexEndpoint.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one
                IndexEndpoint (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            project (str):
                Optional. Project to create EntityType in. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to create EntityType in. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to create EntityTypes. Overrides
                credentials set in aiplatform.init.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            encryption_spec (str):
                Optional. Customer-managed encryption key
                spec for data storage. If set, both of the
                online and offline data storage will be secured
                by this key.
            sync (bool):
                Optional. Whether to execute this creation synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            MatchingEngineIndexEndpoint - IndexEndpoint resource object

        """
        gapic_index_endpoint = gca_matching_engine_index_endpoint.IndexEndpoint(
            name=index_id, display_name=display_name, description=description,
        )

        if labels:
            utils.validate_labels(labels)
            gapic_index_endpoint.labels = labels

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        create_lro = api_client.create_index_endpoint(
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            index_endpoint=gapic_index_endpoint,
            metadata=request_metadata,
        )

        _LOGGER.log_create_with_lro(cls, create_lro)

        created_index = create_lro.result()

        _LOGGER.log_create_complete(cls, created_index, "index_endpoint")

        index_obj = cls(
            index_endpoint_name=created_index.name,
            project=project,
            location=location,
            credentials=credentials,
        )

        return index_obj

    def update(
        self,
        display_name: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "MatchingEngineIndexEndpoint":
        """Updates an existing index endpoint resource.

        Args:
            display_name (str):
                Required. The display name of the IndexEndpoint.
                The name can be up to 128 characters long and
                can be consist of any UTF-8 characters.
            description (str):
                The description of the IndexEndpoint.
            metadata_schema_uri (str):
                Immutable. Points to a YAML file stored on Google Cloud
                Storage describing additional information about the IndexEndpoint,
                that is specific to it. Unset if the IndexEndpoint does not have any
                additional information. The schema is defined as an OpenAPI
                3.0.2 `Schema
                Object <https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md#schemaObject>`__.
                Note: The URI given on output will be immutable and probably
                different, including the URI scheme, than the one given on
                input. The output URI will point to a location where the
                user only has a read access.
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your Indexs.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one IndexEndpoint
                (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.

        Returns:
            MatchingEngineIndexEndpoint - The updated index endpoint resource object.
        """
        update_mask = list()

        if labels:
            utils.validate_labels(labels)
            update_mask.append("labels")

        if display_name is not None:
            update_mask.append("display_name")

        if description is not None:
            update_mask.append("description")

        update_mask = field_mask_pb2.FieldMask(paths=update_mask)

        gapic_index_endpoint = gca_matching_engine_index_endpoint.IndexEndpoint(
            name=self.resource_name, display_name=display_name, description=description,
        )

        _LOGGER.log_action_start_against_resource(
            "Updating", "index_endpoint", self,
        )

        update_lro = self.api_client.update_index_endpoint(
            index_endpoint=gapic_index_endpoint,
            update_mask=update_mask,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Update", "index_endpoint", self.__class__, update_lro
        )

        update_lro.result()

        _LOGGER.log_action_completed_against_resource("index_endpoint", "Updated", self)

        return self

    def deploy_index(
        self,
        id: str,
        index: matching_engine.MatchingEngineIndex,
        display_name: Optional[str] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "MatchingEngineIndexEndpoint":
        """Deploys an existing index resource to this endpoint resource.

        Args:
            id (str):
                Required. The user specified ID of the
                DeployedIndex. The ID can be up to 128
                characters long and must start with a letter and
                only contain letters, numbers, and underscores.
                The ID must be unique within the project it is
                created in.
            index (MatchingEngineIndex):
                Required. The Index this is the
                deployment of. We may refer to this Index as the
                DeployedIndex's "original" Index.
            display_name (str):
                The display name of the DeployedIndex. If not provided upon
                creation, the Index's display_name is used.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
        Returns:
            MatchingEngineIndexEndpoint - IndexEndpoint resource object                
        """

        _LOGGER.log_action_start_against_resource(
            "Deploying index", "index_endpoint", self,
        )

        deployed_index = {
            "id": id,
            "index": index.resource_name,
            "display_name": display_name,
        }

        deploy_lro = self.api_client.deploy_index(
            index_endpoint=self.resource_name,
            deployed_index=deployed_index,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Deploy index", "index_endpoint", self.__class__, deploy_lro
        )

        deploy_lro.result()

        _LOGGER.log_action_completed_against_resource(
            "index_endpoint", "Deployed index", self
        )

        return self

    def undeploy_index(
        self,
        deployed_index_id: str,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "MatchingEngineIndexEndpoint":
        """Undeploy a deployed index endpoint resource.

        Args:
            deployed_index_id (str):
                Required. The ID of the DeployedIndex
                to be undeployed from the IndexEndpoint.

                This corresponds to the ``deployed_index_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
        Returns:
            MatchingEngineIndexEndpoint - IndexEndpoint resource object                
        """

        _LOGGER.log_action_start_against_resource(
            "Undeploying index", "index_endpoint", self,
        )

        undeploy_lro = self.api_client.undeploy_index(
            index_endpoint=self.resource_name,
            deployed_index_id=deployed_index_id,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Undeploy index", "index_endpoint", self.__class__, undeploy_lro
        )

        undeploy_lro.result()

        _LOGGER.log_action_completed_against_resource(
            "index_endpoint", "Undeployed index", self
        )

        return self

    def mutate_deployed_index(
        self,
        id: str,
        index: matching_engine.MatchingEngineIndex,
        display_name: Optional[str] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ):
        """Updates an existing deployed index under this endpoint resource.

        Args:
            id (str):
                Required. The user specified ID of the
                DeployedIndex. The ID can be up to 128
                characters long and must start with a letter and
                only contain letters, numbers, and underscores.
                The ID must be unique within the project it is
                created in.
            index (MatchingEngineIndex):
                Required. The Index this is the
                deployment of. We may refer to this Index as the
                DeployedIndex's "original" Index.
            display_name (str):
                The display name of the DeployedIndex. If not provided upon
                creation, the Index's display_name is used.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
        """

        _LOGGER.log_action_start_against_resource(
            "Mutating index", "index_endpoint", self,
        )

        deployed_index = {
            "id": id,
            "index": index.resource_name,
            "display_name": display_name,
        }

        deploy_lro = self.api_client.mutate_deployed_index(
            index_endpoint=self.resource_name,
            deployed_index=deployed_index,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Mutate index", "index_endpoint", self.__class__, deploy_lro
        )

        deploy_lro.result()

        _LOGGER.log_action_completed_against_resource("index_endpoint", "Mutated", self)

        return self
