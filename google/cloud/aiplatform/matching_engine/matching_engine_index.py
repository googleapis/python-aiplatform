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

from typing import Dict, Optional, Sequence, Tuple, Union

from google.auth import credentials as auth_credentials
from google.protobuf import field_mask_pb2

from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat.types import (
    matching_engine_index as gca_matching_engine_index,
)
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils

import google.cloud.aiplatform.matching_engine.matching_engine_index_config as matching_engine_index_config

_LOGGER = base.Logger(__name__)


class MatchingEngineIndex(base.VertexAiResourceNounWithFutureManager):
    """Matching Engine index resource for Vertex AI."""

    client_class = utils.IndexClientWithOverride

    _resource_noun = "indexes"
    _getter_method = "get_index"
    _list_method = "list_indexes"
    _delete_method = "delete_index"
    _parse_resource_name_method = "parse_index_path"
    _format_resource_name_method = "index_path"

    def __init__(
        self,
        index_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing index given an index name or ID.

        Example Usage:

            my_index = aiplatform.MatchingEngineIndex(
                index_name='projects/123/locations/us-central1/indexes/my_index_id'
            )
            or
            my_index = aiplatform.MatchingEngineIndex(
                index_name='my_index_id'
            )

        Args:
            index_name (str):
                Required. A fully-qualified index resource name or a index ID.
                Example: "projects/123/locations/us-central1/indexes/my_index_id"
                or "my_index_id" when project and location are initialized or passed.
            project (str):
                Optional. Project to retrieve index from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve index from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this Index. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=index_name,
        )
        self._gca_resource = self._get_gca_resource(resource_name=index_name)

    @property
    def description(self) -> str:
        """Description of the index."""
        self._assert_gca_resource_is_available()
        return self._gca_resource.description

    @classmethod
    @base.optional_sync()
    def create(
        cls,
        index_id: str,
        display_name: str,
        contents_delta_uri: str,
        config: matching_engine_index_config.MatchingEngineIndexConfig,
        description: Optional[str] = None,
        metadata_schema_uri: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "MatchingEngineIndex":
        """Creates a MatchingEngineIndex resource.

        Example Usage:

            my_index = aiplatform.Index.create(
                index_id='my_index_id',
            )

        Args:
            index_id (str):
                Required. The ID to use for this index, which will
                become the final component of the index's resource
                name.

                This value may be up to 60 characters, and valid characters
                are ``[a-z0-9_]``. The first character cannot be a number.

                The value must be unique within the project and location.
            display_name (str):
                Required. The display name of the Index.
                The name can be up to 128 characters long and
                can be consist of any UTF-8 characters.
            contents_delta_uri (str):
                Required. Allows inserting, updating  or deleting the contents of the Matching Engine Index.
                The string must be a valid Google Cloud Storage directory path. If this
                field is set when calling IndexService.UpdateIndex, then no other
                Index field can be  also updated as part of the same call.
                The expected structure and format of the files this URI points to is
                described at
                https://docs.google.com/document/d/12DLVB6Nq6rdv8grxfBsPhUA283KWrQ9ZenPBp0zUC30
            config (Union[matching_engine_index_config.MatchingEngineIndexConfig]):
                Required. The configuration with regard to the algorithms used for efficient search.                
            description (str):
                The description of the Index.
            metadata_schema_uri (str):
                Immutable. Points to a YAML file stored on Google Cloud
                Storage describing additional information about the Index,
                that is specific to it. Unset if the Index does not have any
                additional information. The schema is defined as an OpenAPI
                3.0.2 `Schema
                Object <https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md#schemaObject>`__.
                Note: The URI given on output will be immutable and probably
                different, including the URI scheme, than the one given on
                input. The output URI will point to a location where the
                user only has a read access.
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your Index.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one
                Index(System labels are excluded)."
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
            MatchingEngineIndex - Index resource object

        """
        gapic_index = gca_matching_engine_index.Index(
            name=index_id,
            display_name=display_name,
            description=description,
            metadata_schema_uri=metadata_schema_uri,
            metadata={
                "config": config.as_dict(),
                "contentsDeltaUri": contents_delta_uri,
            },
        )

        if labels:
            utils.validate_labels(labels)
            gapic_index.labels = labels

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        create_lro = api_client.create_index(
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            index=gapic_index,
            metadata=request_metadata,
        )

        _LOGGER.log_create_with_lro(cls, create_lro)

        created_index = create_lro.result()

        _LOGGER.log_create_complete(cls, created_index, "index")

        index_obj = cls(
            index_name=created_index.name,
            project=project,
            location=location,
            credentials=credentials,
        )

        return index_obj

    def update(
        self,
        display_name: str,
        contents_delta_uri: str,
        config: matching_engine_index_config.MatchingEngineIndexConfig,
        is_complete_overwrite: Optional[bool] = None,
        description: Optional[str] = None,
        metadata_schema_uri: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "MatchingEngineIndex":
        """Updates an existing managed index resource.

        Args:
            display_name (str):
                Required. The display name of the Index.
                The name can be up to 128 characters long and
                can be consist of any UTF-8 characters.
            contents_delta_uri (str):
                Required. Allows inserting, updating  or deleting the contents of the Matching Engine Index.
                The string must be a valid Google Cloud Storage directory path. If this
                field is set when calling IndexService.UpdateIndex, then no other
                Index field can be  also updated as part of the same call.
                The expected structure and format of the files this URI points to is
                described at
                https://docs.google.com/document/d/12DLVB6Nq6rdv8grxfBsPhUA283KWrQ9ZenPBp0zUC30
            config (matching_engine_index_config.MatchingEngineIndexConfig):
                Required. The configuration with regard to the algorithms used for efficient search.                
            is_complete_overwrite (str):
                If this field is set together with contentsDeltaUri when calling IndexService.UpdateIndex,
                then existing content of the Index will be replaced by the data from the contentsDeltaUri.                
            description (str):
                The description of the Index.
            metadata_schema_uri (str):
                Immutable. Points to a YAML file stored on Google Cloud
                Storage describing additional information about the Index,
                that is specific to it. Unset if the Index does not have any
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
                labels can be associated with one Index
                (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.

        Returns:
            MatchingEngineIndex - The updated index resource object.
        """
        update_mask = list()

        if labels:
            utils.validate_labels(labels)
            update_mask.append("labels")

        if display_name is not None:
            update_mask.append("display_name")

        if description is not None:
            update_mask.append("description")

        if metadata_schema_uri is not None:
            update_mask.append("metadata_schema_uri")

        update_mask = field_mask_pb2.FieldMask(paths=update_mask)

        gapic_index = gca_matching_engine_index.Index(
            name=self.resource_name,
            display_name=display_name,
            description=description,
            metadata_schema_uri=metadata_schema_uri,
            metadata={
                "config": config.as_dict(),
                "contentsDeltaUri": contents_delta_uri,
                "isCompleteOverwrite": is_complete_overwrite,
            },
        )

        _LOGGER.log_action_start_against_resource(
            "Updating", "index", self,
        )

        update_lro = self.api_client.update_index(
            index=gapic_index, update_mask=update_mask, metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Update", "index", self.__class__, update_lro
        )

        update_lro.result()

        _LOGGER.log_action_completed_against_resource("index", "Updated", self)

        return self
