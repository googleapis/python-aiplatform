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

from typing import Optional

from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import base
from google.cloud.aiplatform.metadata import metadata_store
from google.cloud.aiplatform.compat.types import metadata_schema as gca_metadata_schema
from google.cloud.aiplatform import utils

_LOGGER = base.Logger(__name__)


class _MetadataSchema(base.VertexAiResourceNounWithFutureManager):
    client_class = utils.MetadataClientWithOverride

    _resource_noun = "metadataSchema"
    _getter_method = "get_metadata_schema"
    _list_method = "list_metadata_schemas"
    _delete_method = None
    _parse_resource_name_method = "parse_metadata_schema_path"
    _format_resource_name_method = "metadata_schema_path"

    def __init__(
        self,
        metadata_schema_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=metadata_schema_name,
        )
        self._gca_resource = self._get_gca_resource(resource_name=metadata_schema_name)

    @classmethod
    def create(
        cls,
        metadata_schema: gca_metadata_schema.MetadataSchema,
        metadata_schema_id: str,
        metadata_store_name: str = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        api_client = cls._instantiate_client(location=location, credentials=credentials)

        parent = utils.full_resource_name(
            resource_name=metadata_store_name,
            resource_noun=metadata_store._MetadataStore._resource_noun,
            parse_resource_name_method=metadata_store._MetadataStore._parse_resource_name,
            format_resource_name_method=metadata_store._MetadataStore._format_resource_name,
            project=project,
            location=location,
        )

        _LOGGER.log_create_with_lro(cls)

        metadata_schema = api_client.create_metadata_schema(
            parent=parent,
            metadata_schema=metadata_schema,
            metadata_schema_id=metadata_schema_id,
        )

        _LOGGER.log_create_complete(cls, metadata_schema, "ms")

        return cls(
            metadata_schema_name=metadata_schema.name,
            credentials=credentials,
        )
