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
from typing import Dict, List, Optional
from unittest import mock
from unittest.mock import call, patch

from google.api_core import operation as ga_operation
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat import types
from google.cloud.aiplatform.compat.services import (
    feature_registry_service_client,
)
from google.cloud.aiplatform_v1beta1.services.feature_registry_service import (
    FeatureRegistryServiceClient,
)
from feature_store_constants import (
    _TEST_FG1_F1_DESCRIPTION,
    _TEST_FG1_F1_FEATURE_STATS_AND_ANOMALY,
    _TEST_FG1_F1_ID,
    _TEST_FG1_F1_LABELS,
    _TEST_FG1_F1_PATH,
    _TEST_FG1_F1_POINT_OF_CONTACT,
    _TEST_FG1_F1_WITH_STATS,
    _TEST_FG1_F2_DESCRIPTION,
    _TEST_FG1_F2_ID,
    _TEST_FG1_F2_LABELS,
    _TEST_FG1_F2_PATH,
    _TEST_FG1_F2_POINT_OF_CONTACT,
    _TEST_FG1_F2_VERSION_COLUMN_NAME,
    _TEST_FG1_ID,
    _TEST_LOCATION,
    _TEST_PROJECT,
)
from vertexai.resources.preview import (
    Feature,
    FeatureGroup,
)
import pytest


@pytest.fixture
def delete_feature_mock():
    with patch.object(
        feature_registry_service_client.FeatureRegistryServiceClient,
        "delete_feature",
    ) as delete_feature_mock:
        delete_feature_lro_mock = mock.Mock(ga_operation.Operation)
        delete_feature_mock.return_value = delete_feature_lro_mock
        yield delete_feature_mock


@pytest.fixture
def get_feature_with_stats_and_anomalies_mock():
    with patch.object(
        FeatureRegistryServiceClient,
        "get_feature",
    ) as get_feature_with_stats_and_anomalies_mock:
        get_feature_with_stats_and_anomalies_mock.return_value = _TEST_FG1_F1_WITH_STATS
        yield get_feature_with_stats_and_anomalies_mock


pytestmark = pytest.mark.usefixtures("google_auth_mock")


def feature_eq(
    feature_to_check: Feature,
    name: str,
    resource_name: str,
    project: str,
    location: str,
    description: str,
    labels: Dict[str, str],
    point_of_contact: str,
    version_column_name: Optional[str] = None,
    feature_stats_and_anomalies: Optional[
        List[types.feature_monitor.FeatureStatsAndAnomaly]
    ] = None,
):
    """Check if a Feature has the appropriate values set."""
    assert feature_to_check.name == name
    assert feature_to_check.resource_name == resource_name
    assert feature_to_check.project == project
    assert feature_to_check.location == location
    assert feature_to_check.description == description
    assert feature_to_check.labels == labels
    assert feature_to_check.point_of_contact == point_of_contact

    if version_column_name:
        assert feature_to_check.version_column_name == version_column_name
    if feature_stats_and_anomalies:
        assert (
            feature_to_check.feature_stats_and_anomalies == feature_stats_and_anomalies
        )


def test_init_with_feature_id_and_no_fg_id_raises_error(get_feature_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Since feature 'my_fg1_f1' is not provided as a path, please specify"
            + " feature_group_id."
        ),
    ):
        Feature(_TEST_FG1_F1_ID)


def test_init_with_feature_path_and_fg_id_raises_error(get_feature_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Since feature 'projects/test-project/locations/us-central1/featureGroups/my_fg1/features/my_fg1_f1' is provided as a path, feature_group_id should not be specified."
        ),
    ):
        Feature(_TEST_FG1_F1_PATH, feature_group_id=_TEST_FG1_ID)


def test_init_with_feature_id(get_feature_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    feature = Feature(_TEST_FG1_F1_ID, feature_group_id=_TEST_FG1_ID)

    get_feature_mock.assert_called_once_with(
        name=_TEST_FG1_F1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )


def test_init_with_feature_id_for_explicit_version_column(
    get_feature_with_version_column_mock,
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    feature = Feature(_TEST_FG1_F2_ID, feature_group_id=_TEST_FG1_ID)

    get_feature_with_version_column_mock.assert_called_once_with(
        name=_TEST_FG1_F2_PATH,
        retry=base._DEFAULT_RETRY,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F2_ID,
        resource_name=_TEST_FG1_F2_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F2_DESCRIPTION,
        labels=_TEST_FG1_F2_LABELS,
        point_of_contact=_TEST_FG1_F2_POINT_OF_CONTACT,
        version_column_name=_TEST_FG1_F2_VERSION_COLUMN_NAME,
    )


def test_init_with_feature_path(get_feature_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    feature = Feature(_TEST_FG1_F1_PATH)

    get_feature_mock.assert_called_once_with(
        name=_TEST_FG1_F1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )


def test_init_with_feature_path_for_explicit_version_column(
    get_feature_with_version_column_mock,
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    feature = Feature(_TEST_FG1_F2_PATH)

    get_feature_with_version_column_mock.assert_called_once_with(
        name=_TEST_FG1_F2_PATH,
        retry=base._DEFAULT_RETRY,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F2_ID,
        resource_name=_TEST_FG1_F2_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        version_column_name=_TEST_FG1_F2_VERSION_COLUMN_NAME,
        description=_TEST_FG1_F2_DESCRIPTION,
        labels=_TEST_FG1_F2_LABELS,
        point_of_contact=_TEST_FG1_F2_POINT_OF_CONTACT,
    )


def test_init_with_latest_stats_count(get_feature_with_stats_and_anomalies_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    feature = Feature(name=_TEST_FG1_F1_PATH, latest_stats_count=1)

    get_feature_with_stats_and_anomalies_mock.assert_called_once_with(
        request=types.featurestore_service_v1beta1.GetFeatureRequest(
            name=_TEST_FG1_F1_PATH,
            feature_stats_and_anomaly_spec=types.feature_monitor.FeatureStatsAndAnomalySpec(
                latest_stats_count=1
            ),
        )
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
        feature_stats_and_anomalies=[_TEST_FG1_F1_FEATURE_STATS_AND_ANOMALY],
    )


@pytest.mark.parametrize("sync", [True])
def test_delete_feature(
    get_fg_mock, get_feature_mock, delete_feature_mock, base_logger_mock, sync
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    feature = FeatureGroup(_TEST_FG1_ID).get_feature(_TEST_FG1_F1_ID)
    feature.delete(sync=sync)

    if not sync:
        feature.wait()

    delete_feature_mock.assert_called_once_with(
        name=_TEST_FG1_F1_PATH,
    )

    base_logger_mock.assert_has_calls(
        [
            call(
                "Deleting Feature resource:"
                " projects/test-project/locations/us-central1/featureGroups/my_fg1/features/my_fg1_f1"
            ),
            call(
                "Delete Feature backing LRO:"
                f" {delete_feature_mock.return_value.operation.name}"
            ),
            call(
                "Feature resource"
                " projects/test-project/locations/us-central1/featureGroups/my_fg1/features/my_fg1_f1"
                " deleted."
            ),
        ]
    )
