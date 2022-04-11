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

from typing import List, Optional, Tuple

from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat import types
from google.cloud.aiplatform.metadata import constants as metadata_constants


_VERTEX_EXPERIMENT_TRACKING_LABEL = "vertex_experiment_tracking"

_TENSORBOARD_RUN_REFERENCE_ARTIFACT = types.artifact.Artifact(
    name="google-dev-vertex-tensorboard-run-v0-0-1",
    schema_title=metadata_constants._EXPERIMENTS_V2_TENSORBOARD_RUN,
    schema_version="0.0.1",
    metadata={_VERTEX_EXPERIMENT_TRACKING_LABEL: True},
)


def make_gcp_resource_url(resource: base.VertexAiResourceNoun) -> str:
    resource_name = resource.resource_name
    location = resource.location
    version = resource.api_client._default_version
    api_uri = resource.api_client.api_endpoint

    return f"https://{api_uri}/{version}/{resource_name}"


def make_gcp_resource_metadata_schema(
    title: str,
) -> types.metadata_schema.MetadataSchema:
    return types.metadata_schema.MetadataSchema(
        schema_version="0.0.1",
        schema=f"title: {title}\ntype: object\nproperties:\n  resourceName:\n    type: string\n",
        schema_type=types.metadata_schema.MetadataSchema.MetadataSchemaType.ARTIFACT_TYPE,
    )


def make_experiment_v2_metadata_schema() -> types.metadata_schema.MetadataSchema:
    return types.metadata_schema.MetadataSchema(
        schema_version="0.0.1",
        schema=f"title: {metadata_constants._EXPERIMENTS_V2_SYSTEM_RUN}\ntype: object\n",
        schema_type=types.metadata_schema.MetadataSchema.MetadataSchemaType.EXECUTION_TYPE,
    )


def get_tensorboard_board_run_metadata_schema() -> Tuple[
    str, types.metadata_schema.MetadataSchema
]:
    return (
        _TENSORBOARD_RUN_REFERENCE_ARTIFACT.name,
        make_gcp_resource_metadata_schema(
            title=_TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_title
        ),
    )

def make_filter_string(
        schema_title: Optional[str]=None,
        in_context: Optional[List[str]]=None,
        parent_contexts: Optional[List[str]]=None) -> str:
    parts = []
    if schema_title:
        parts.append(f'{schema_title}=schema_tile')
    if in_context:
        for context in in_context:
            parts.append(f'in_context({context})')
    if parent_contexts:
        parts.append(f'parent_contexts:{",".join(parent_contexts)}')
    return 'AND'.join(parts)
