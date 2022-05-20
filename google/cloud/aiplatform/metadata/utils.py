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

from typing import List, Optional, Tuple, Union

from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat import types
from google.cloud.aiplatform.metadata import constants as metadata_constants


# constant to mark an Experiment context as originating from the SDK
_VERTEX_EXPERIMENT_TRACKING_LABEL = "vertex_experiment_tracking"


# TODO(remove this when TB Run is seeded)
_TENSORBOARD_RUN_REFERENCE_ARTIFACT = types.artifact.Artifact(
    name="google-dev-vertex-tensorboard-run-v0-0-1",
    schema_title=metadata_constants._EXPERIMENTS_V2_TENSORBOARD_RUN,
    schema_version="0.0.1",
    metadata={_VERTEX_EXPERIMENT_TRACKING_LABEL: True},
)


def make_gcp_resource_url(resource: base.VertexAiResourceNoun) -> str:
    """Helper function to format the GCP resource url for google.X metadata schemas.

    Args:
        resource (base.VertexAiResourceNoun): Required. A Vertex resource instance.
    Returns:
        The formatted url of resource.
    """
    resource_name = resource.resource_name
    version = resource.api_client._default_version
    api_uri = resource.api_client.api_endpoint

    return f"https://{api_uri}/{version}/{resource_name}"


# TODO(remove this when TB Run is seeded)
def make_gcp_resource_metadata_schema(
    title: str,
) -> types.metadata_schema.MetadataSchema:
    return types.metadata_schema.MetadataSchema(
        schema_version="0.0.1",
        schema=f"title: {title}\ntype: object\nproperties:\n  resourceName:\n    type: string\n",
        schema_type=types.metadata_schema.MetadataSchema.MetadataSchemaType.ARTIFACT_TYPE,
    )


# TODO(remove this when TB Run is seeded)
def get_tensorboard_board_run_metadata_schema() -> Tuple[
    str, types.metadata_schema.MetadataSchema
]:
    return (
        _TENSORBOARD_RUN_REFERENCE_ARTIFACT.name,
        make_gcp_resource_metadata_schema(
            title=_TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_title
        ),
    )


def _make_filter_string(
    schema_title: Optional[Union[str, List[str]]] = None,
    in_context: Optional[List[str]] = None,
    parent_contexts: Optional[List[str]] = None,
    uri: Optional[str] = None,
) -> str:
    """Helper method to format filter strings for Metadata querying.

    No enforcement of correctness.

    Args:
        schema_title (Union[str, List[str]]): Optional. schema_titles to filter for.
        in_context (List[str]):
            Optional. Context resource names that the node should be in. Only for Artifacts/Executions.
        parent_contexts (List[str]): Optional. Parent contexts the context should be in. Only for Contexts.
        uri (str): Optional. uri to match for. Only for Artifacts.
    Returns:
        String that can be used for Metadata service filtering.
    """
    parts = []
    if schema_title:
        if isinstance(schema_title, str):
            parts.append(f'schema_title="{schema_title}"')
        else:
            substring = " OR ".join(f'schema_title="{s}"' for s in schema_title)
            parts.append(f"({substring})")
    if in_context:
        for context in in_context:
            parts.append(f'in_context("{context}")')
    if parent_contexts:
        parent_context_str = ",".join([f'"{c}"' for c in parent_contexts])
        parts.append(f"parent_contexts:{parent_context_str}")
    if uri:
        parts.append(f'uri="{uri}"')
    return " AND ".join(parts)
