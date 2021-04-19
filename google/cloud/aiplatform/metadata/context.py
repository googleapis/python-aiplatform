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

from typing import Optional, Dict, Sequence

import proto

from google.cloud.aiplatform import utils
from google.cloud.aiplatform.metadata.resource import _Resource
from google.cloud.aiplatform_v1beta1 import ListContextsRequest
from google.cloud.aiplatform_v1beta1.types import context as gca_context


class _Context(_Resource):
    """Metadata Context resource for AI Platform"""

    _resource_noun = "contexts"
    _getter_method = "get_context"

    def add_artifacts_and_executions(
        self,
        artifact_resource_names: Optional[Sequence[str]] = None,
        execution_resource_names: Optional[Sequence[str]] = None,
    ):
        """Associate Executions and attribute Artifacts to a given Context.

        Args:
            artifact_resource_names (Sequence[str]):
                Optional. The full resource name of Artifacts to attribute to the Context.
            execution_resource_names (Sequence[str]):
                Optional. The full resource name of Executions to associate with the Context.
        """
        self.api_client.add_context_artifacts_and_executions(
            context=self.resource_name,
            artifacts=artifact_resource_names,
            executions=execution_resource_names,
        )

    @classmethod
    def _create_resource(
        cls,
        client: utils.MetadataClientWithOverride,
        parent: str,
        resource_id: str,
        schema_title: str,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> proto.Message:
        gapic_context = gca_context.Context(
            schema_title=schema_title,
            schema_version=schema_version,
            display_name=display_name,
            description=description,
            metadata=metadata if metadata else {},
        )
        return client.create_context(
            parent=parent, context=gapic_context, context_id=resource_id,
        )

    @classmethod
    def _update_resource(
        cls, client: utils.MetadataClientWithOverride, resource: proto.Message,
    ) -> proto.Message:
        """Update Contexts with given input.

        Args:
            client (utils.MetadataClientWithOverride):
                Required. client to send require to Metadata Service.
            resource (proto.Message):
                Required. The proto.Message which contains the update information for the resource.
        """

        return client.update_context(context=resource)

    @classmethod
    def _list_resources(
        cls,
        client: utils.MetadataClientWithOverride,
        parent: str,
        filter: Optional[str] = None,
    ):
        """List Contexts in the parent path that matches the filter.

        Args:
            client (utils.MetadataClientWithOverride):
                Required. client to send require to Metadata Service.
            parent (str):
                Required. The path where Contexts are stored.
            filter (str):
                Optional. filter string to restrict the list result
        """

        list_request = ListContextsRequest(parent=parent, filter=filter,)
        return client.list_contexts(request=list_request)
