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

from typing import Dict, List
from unittest.mock import patch

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from vertexai.resources.preview import (
    FeatureGroup,
)
import vertexai.resources.preview.feature_store.utils as fs_utils
import pytest
from google.cloud.aiplatform.compat.services import (
    feature_registry_service_client,
)


from feature_store_constants import (
    _TEST_PROJECT,
    _TEST_LOCATION,
    _TEST_FG1,
    _TEST_FG1_ID,
    _TEST_FG1_PATH,
    _TEST_FG1_BQ_URI,
    _TEST_FG1_ENTITY_ID_COLUMNS,
    _TEST_FG1_LABELS,
)


pytestmark = pytest.mark.usefixtures("google_auth_mock")


@pytest.fixture
def get_fg_mock():
    with patch.object(
        feature_registry_service_client.FeatureRegistryServiceClient,
        "get_feature_group",
    ) as get_fg_mock:
        get_fg_mock.return_value = _TEST_FG1
        yield get_fg_mock


def fg_eq(
    fg_to_check: FeatureGroup,
    name: str,
    resource_name: str,
    source_uri: str,
    entity_id_columns: List[str],
    project: str,
    location: str,
    labels: Dict[str, str],
):
    """Check if a FeatureGroup has the appropriate values set."""
    assert fg_to_check.name == name
    assert fg_to_check.resource_name == resource_name
    assert fg_to_check.source == fs_utils.FeatureGroupBigQuerySource(
        uri=source_uri,
        entity_id_columns=entity_id_columns,
    )
    assert fg_to_check.project == project
    assert fg_to_check.location == location
    assert fg_to_check.labels == labels


@pytest.mark.parametrize(
    "feature_group_name",
    [_TEST_FG1_ID, _TEST_FG1_PATH],
)
def test_init(feature_group_name, get_fg_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fg = FeatureGroup(feature_group_name)

    get_fg_mock.assert_called_once_with(
        name=_TEST_FG1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    fg_eq(
        fg,
        name=_TEST_FG1_ID,
        resource_name=_TEST_FG1_PATH,
        source_uri=_TEST_FG1_BQ_URI,
        entity_id_columns=_TEST_FG1_ENTITY_ID_COLUMNS,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FG1_LABELS,
    )
