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

import re
from typing import Optional
from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.types import (
    feature_monitor_v1beta1 as gca_feature_monitor,
)


class FeatureMonitor(base.VertexAiResourceNounWithFutureManager):
    """Class for managing Feature Monitor resources."""

    client_class = utils.FeatureRegistryClientV1Beta1WithOverride

    _resource_noun = "feature_monitors"
    _getter_method = "get_feature_monitor"
    _list_method = "list_feature_monitors"
    _delete_method = "delete_feature_monitors"
    _parse_resource_name_method = "parse_feature_monitor_path"
    _format_resource_name_method = "feature_monitor_path"
    _gca_resource: gca_feature_monitor.FeatureMonitor

    def __init__(
        self,
        name: str,
        feature_group_id: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing managed feature.

        Args:
            name:
                The resource name
                (`projects/.../locations/.../featureGroups/.../featureMonitors/...`) or
                ID.
            feature_group_id:
                The feature group ID. Must be passed in if name is an ID and not
                a resource path.
            project:
                Project to retrieve feature from. If not set, the project set in
                aiplatform.init will be used.
            location:
                Location to retrieve feature from. If not set, the location set
                in aiplatform.init will be used.
            credentials:
                Custom credentials to use to retrieve this feature. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=name,
        )

        if re.fullmatch(
            r"projects/.+/locations/.+/featureGroups/.+/featureMonitors/.+",
            name,
        ):
            if feature_group_id:
                raise ValueError(
                    f"Since feature monitor '{name}' is provided as a path, feature_group_id should not be specified."
                )
            feature_monitor = name
        else:
            from .feature_group import FeatureGroup

            # Construct the feature path using feature group ID if  only the
            # feature group ID is provided.
            if not feature_group_id:
                raise ValueError(
                    f"Since feature monitor '{name}' is not provided as a path, please specify feature_group_id."
                )

            feature_group_path = utils.full_resource_name(
                resource_name=feature_group_id,
                resource_noun=FeatureGroup._resource_noun,
                parse_resource_name_method=FeatureGroup._parse_resource_name,
                format_resource_name_method=FeatureGroup._format_resource_name,
            )

            feature_monitor = f"{feature_group_path}/featureMonitors/{name}"

        self._gca_resource = self._get_gca_resource(resource_name=feature_monitor)

    @property
    def description(self) -> str:
        """The description of the feature monitor."""
        return self._gca_resource.description
