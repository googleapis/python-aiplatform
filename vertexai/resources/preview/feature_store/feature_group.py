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

from typing import Optional
from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.types import (
    feature_group as gca_feature_group,
)
import vertexai.resources.preview.feature_store.utils as fs_utils


class FeatureGroup(base.VertexAiResourceNounWithFutureManager):
    """Class for managing Feature Group resources."""

    client_class = utils.FeatureRegistryClientWithOverride

    _resource_noun = "feature_groups"
    _getter_method = "get_feature_group"
    _list_method = "list_feature_groups"
    _delete_method = "delete_feature_group"
    _parse_resource_name_method = "parse_feature_group_path"
    _format_resource_name_method = "feature_group_path"
    _gca_resource: gca_feature_group.FeatureGroup

    def __init__(
        self,
        name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing managed feature group.

        Args:
            name:
                The resource name
                (`projects/.../locations/.../featureGroups/...`) or ID.
            project:
                Project to retrieve feature group from. If unset, the
                project set in aiplatform.init will be used.
            location:
                Location to retrieve feature group from. If not set,
                location set in aiplatform.init will be used.
            credentials:
                Custom credentials to use to retrieve this feature group.
                Overrides credentials set in aiplatform.init.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=name,
        )

        self._gca_resource = self._get_gca_resource(resource_name=name)

    @property
    def source(self) -> fs_utils.FeatureGroupBigQuerySource:
        return fs_utils.FeatureGroupBigQuerySource(
            uri=self._gca_resource.big_query.big_query_source.input_uri,
            entity_id_columns=self._gca_resource.big_query.entity_id_columns,
        )
