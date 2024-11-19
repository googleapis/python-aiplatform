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
from typing import Dict, List, Tuple

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from feature_store_constants import _TEST_FG1_FM1_DESCRIPTION
from feature_store_constants import _TEST_FG1_FM1_ID
from feature_store_constants import _TEST_FG1_FM1_LABELS
from feature_store_constants import _TEST_FG1_FM1_PATH
from feature_store_constants import _TEST_FG1_ID
from feature_store_constants import _TEST_LOCATION
from feature_store_constants import _TEST_PROJECT
from feature_store_constants import _TEST_FG1_FM1_SCHEDULE_CONFIG
from feature_store_constants import _TEST_FG1_FM1_FEATURE_SELECTION_CONFIGS
from vertexai.resources.preview import FeatureMonitor
import pytest


pytestmark = pytest.mark.usefixtures("google_auth_mock")


def feature_monitor_eq(
    feature_monitor_to_check: FeatureMonitor,
    name: str,
    resource_name: str,
    project: str,
    location: str,
    description: str,
    labels: Dict[str, str],
    schedule_config: str,
    feature_selection_configs: List[Tuple[str, float]],
):
    """Check if a Feature Monitor has the appropriate values set."""
    assert feature_monitor_to_check.name == name
    assert feature_monitor_to_check.resource_name == resource_name
    assert feature_monitor_to_check.project == project
    assert feature_monitor_to_check.location == location
    assert feature_monitor_to_check.description == description
    assert feature_monitor_to_check.labels == labels


def test_init_with_feature_monitor_id_and_no_fg_id_raises_error():
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Since feature monitor 'my_fg1_fm1' is not provided as a path, please"
            " specify feature_group_id."
        ),
    ):
        FeatureMonitor(_TEST_FG1_FM1_ID)


def test_init_with_feature_monitor_path_and_fg_id_raises_error():
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Since feature monitor 'projects/test-project/locations/us-central1/"
            "featureGroups/my_fg1/featureMonitors/my_fg1_fm1' is provided as a "
            "path, feature_group_id should not be specified."
        ),
    ):
        FeatureMonitor(_TEST_FG1_FM1_PATH, feature_group_id=_TEST_FG1_ID)


def test_init_with_feature_monitor_id(get_feature_monitor_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    feature_monitor = FeatureMonitor(_TEST_FG1_FM1_ID, feature_group_id=_TEST_FG1_ID)

    get_feature_monitor_mock.assert_called_once_with(
        name=_TEST_FG1_FM1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    feature_monitor_eq(
        feature_monitor,
        name=_TEST_FG1_FM1_ID,
        resource_name=_TEST_FG1_FM1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_FM1_DESCRIPTION,
        labels=_TEST_FG1_FM1_LABELS,
        schedule_config=_TEST_FG1_FM1_SCHEDULE_CONFIG,
        feature_selection_configs=_TEST_FG1_FM1_FEATURE_SELECTION_CONFIGS,
    )


def test_init_with_feature_path(get_feature_monitor_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    feature_monitor = FeatureMonitor(_TEST_FG1_FM1_PATH)

    get_feature_monitor_mock.assert_called_once_with(
        name=_TEST_FG1_FM1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    feature_monitor_eq(
        feature_monitor,
        name=_TEST_FG1_FM1_ID,
        resource_name=_TEST_FG1_FM1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_FM1_DESCRIPTION,
        labels=_TEST_FG1_FM1_LABELS,
        schedule_config=_TEST_FG1_FM1_SCHEDULE_CONFIG,
        feature_selection_configs=_TEST_FG1_FM1_FEATURE_SELECTION_CONFIGS,
    )
