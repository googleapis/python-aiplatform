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
"""Classes for working with Vertex AI Search."""

from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.constants import base as constants

# We just want to re-export certain classes
# pylint: disable=g-multiple-import,g-importing-member
from vertexai.preview.search._search import (
    App,
    DataType,
    DataSource,
    DataStore,
    IndustryVertical,
    TargetSite,
    InlineSource,
    GcsSource,
    BigQuerySource,
    SpannerSource,
    FirestoreSource,
    BigtableOptions,
    BigtableSource,
    AlloyDbSource,
    FhirStoreSource,
    ReconciliationMode,
    SearchTier,
    SearchAddOn,
)


def init(project: str, location: str = "global"):
    if location == "global":
        api_endpoint = constants.SEARCH_API_BASE_PATH
    else:
        api_endpoint = f"{location}-{constants.SEARCH_API_BASE_PATH}"
    initializer.search_config.init(
        project=project,
        location=location,
        api_endpoint=api_endpoint,
    )


__all__ = [
    "init",
    "App",
    "DataType",
    "DataSource",
    "DataStore",
    "IndustryVertical",
    "TargetSite",
    "InlineSource",
    "GcsSource",
    "BigQuerySource",
    "SpannerSource",
    "FirestoreSource",
    "BigtableOptions",
    "BigtableSource",
    "AlloyDbSource",
    "FhirStoreSource",
    "ReconciliationMode",
    "SearchTier",
    "SearchAddOn",
]
