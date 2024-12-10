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
from typing import Dict, List, Optional, Tuple
from unittest.mock import patch

from google.cloud import aiplatform
from google.cloud.aiplatform import base

from feature_store_constants import (
    _TEST_PROJECT,
    _TEST_LOCATION,
    _TEST_FG1_ID,
    _TEST_FG1_FM1_DESCRIPTION,
    _TEST_FG1_FM1_FEATURE_SELECTION_CONFIGS,
    _TEST_FG1_FM1_ID,
    _TEST_FG1_FM1_LABELS,
    _TEST_FG1_FM1_PATH,
    _TEST_FG1_FM1_SCHEDULE_CONFIG,
    _TEST_FG1_FMJ1,
    _TEST_FG1_FMJ1_DESCRIPTION,
    _TEST_FG1_FMJ1_FEATURE_STATS_AND_ANOMALIES,
    _TEST_FG1_FMJ1_ID,
    _TEST_FG1_FMJ1_LABELS,
    _TEST_FG1_FMJ_LIST,
    _TEST_FG1_FMJ1_PATH,
    _TEST_FG1_FMJ2_DESCRIPTION,
    _TEST_FG1_FMJ2_LABELS,
    _TEST_FG1_FMJ2_PATH,
)
from vertexai.resources.preview import FeatureMonitor
from google.cloud.aiplatform_v1beta1.services.feature_registry_service import (
    FeatureRegistryServiceClient,
)
from google.cloud.aiplatform.compat import types
from vertexai.resources.preview.feature_store import (
    feature_monitor,
)
import pytest


pytestmark = pytest.mark.usefixtures("google_auth_mock")


@pytest.fixture
def fm_logger_mock():
    with patch.object(
        feature_monitor._LOGGER,
        "info",
        wraps=feature_monitor._LOGGER.info,
    ) as logger_mock:
        yield logger_mock


@pytest.fixture
def get_feature_monitor_job_mock():
    with patch.object(
        FeatureRegistryServiceClient,
        "get_feature_monitor_job",
    ) as get_fmj_mock:
        get_fmj_mock.return_value = _TEST_FG1_FMJ1
        yield get_fmj_mock


@pytest.fixture
def create_feature_monitor_job_mock():
    with patch.object(
        FeatureRegistryServiceClient,
        "create_feature_monitor_job",
    ) as create_feature_monitor_job_mock:
        create_feature_monitor_job_mock.return_value = _TEST_FG1_FMJ1
        yield create_feature_monitor_job_mock


@pytest.fixture
def list_feature_monitor_jobs_mock():
    with patch.object(
        FeatureRegistryServiceClient,
        "list_feature_monitor_jobs",
    ) as list_feature_monitor_jobs_mock:
        list_feature_monitor_jobs_mock.return_value = _TEST_FG1_FMJ_LIST
        yield list_feature_monitor_jobs_mock


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
    assert feature_monitor_to_check.schedule_config == schedule_config
    assert (
        feature_monitor_to_check.feature_selection_configs == feature_selection_configs
    )


def feature_monitor_job_eq(
    feature_monitor_job_to_check: FeatureMonitor.FeatureMonitorJob,
    resource_name: str,
    project: str,
    location: str,
    description: str,
    labels: Dict[str, str],
    feature_stats_and_anomalies: Optional[
        List[types.feature_monitor.FeatureStatsAndAnomaly]
    ] = None,
):
    """Check if a Feature Monitor Job has the appropriate values set."""
    assert feature_monitor_job_to_check.resource_name == resource_name
    assert feature_monitor_job_to_check.project == project
    assert feature_monitor_job_to_check.location == location
    assert feature_monitor_job_to_check.description == description
    assert feature_monitor_job_to_check.labels == labels
    if feature_stats_and_anomalies:
        assert (
            feature_monitor_job_to_check.feature_stats_and_anomalies
            == feature_stats_and_anomalies
        )


def test_init_with_feature_monitor_id_and_no_fg_id_raises_error():
    aiplatform.init(
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Since feature monitor 'my_fg1_fm1' is not provided as a path, please"
            " specify feature_group_id."
        ),
    ):
        FeatureMonitor(_TEST_FG1_FM1_ID)


def test_init_with_feature_monitor_path_and_fg_id_raises_error():
    aiplatform.init(
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Since feature monitor 'projects/test-project/locations/us-central1/"
            "featureGroups/my_fg1/featureMonitors/my_fg1_fm1' is provided as a "
            "path, feature_group_id should not be specified."
        ),
    ):
        FeatureMonitor(
            _TEST_FG1_FM1_PATH,
            feature_group_id=_TEST_FG1_ID,
        )


def test_init_with_feature_monitor_id(get_feature_monitor_mock):
    aiplatform.init(
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )

    feature_monitor = FeatureMonitor(
        _TEST_FG1_FM1_ID,
        feature_group_id=_TEST_FG1_ID,
    )

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


def test_init_with_feature_monitor_path(get_feature_monitor_mock):
    aiplatform.init(
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )

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


def test_init_with_feature_monitor_job_path(get_feature_monitor_job_mock):
    aiplatform.init(
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )

    feature_monitor_job = FeatureMonitor.FeatureMonitorJob(_TEST_FG1_FMJ1_PATH)

    get_feature_monitor_job_mock.assert_called_once_with(
        name=_TEST_FG1_FMJ1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    feature_monitor_job_eq(
        feature_monitor_job,
        resource_name=_TEST_FG1_FMJ1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_FMJ1_DESCRIPTION,
        labels=_TEST_FG1_FMJ1_LABELS,
        feature_stats_and_anomalies=_TEST_FG1_FMJ1_FEATURE_STATS_AND_ANOMALIES,
    )


@pytest.mark.parametrize("create_request_timeout", [None, 1.0])
def test_create_feature_monitor_job(
    get_feature_monitor_mock,
    get_feature_monitor_job_mock,
    create_feature_monitor_job_mock,
    create_request_timeout,
    fm_logger_mock,
):
    aiplatform.init(
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )

    fm = FeatureMonitor(
        _TEST_FG1_FM1_ID,
        feature_group_id=_TEST_FG1_ID,
    )
    feature_monitor_job = fm.create_feature_monitor_job(
        description=_TEST_FG1_FMJ1_DESCRIPTION,
        labels=_TEST_FG1_FMJ1_LABELS,
        create_request_timeout=create_request_timeout,
    )

    expected_feature_monitor_job = types.feature_monitor_job.FeatureMonitorJob(
        description=_TEST_FG1_FMJ1_DESCRIPTION,
        labels=_TEST_FG1_FMJ1_LABELS,
    )
    create_feature_monitor_job_mock.assert_called_once_with(
        parent=_TEST_FG1_FM1_PATH,
        feature_monitor_job=expected_feature_monitor_job,
        metadata=(),
        timeout=create_request_timeout,
    )

    feature_monitor_job_eq(
        feature_monitor_job,
        resource_name=_TEST_FG1_FMJ1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_FMJ1_DESCRIPTION,
        labels=_TEST_FG1_FMJ1_LABELS,
        feature_stats_and_anomalies=_TEST_FG1_FMJ1_FEATURE_STATS_AND_ANOMALIES,
    )


def test_get_feature_monitor_job(
    get_feature_monitor_mock, get_feature_monitor_job_mock
):
    aiplatform.init(
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )

    fm = FeatureMonitor(
        _TEST_FG1_FM1_ID,
        feature_group_id=_TEST_FG1_ID,
    )
    feature_monitor_job = fm.get_feature_monitor_job(_TEST_FG1_FMJ1_ID)

    get_feature_monitor_job_mock.assert_called_once_with(
        name=_TEST_FG1_FMJ1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    feature_monitor_job_eq(
        feature_monitor_job,
        resource_name=_TEST_FG1_FMJ1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_FMJ1_DESCRIPTION,
        labels=_TEST_FG1_FMJ1_LABELS,
        feature_stats_and_anomalies=_TEST_FG1_FMJ1_FEATURE_STATS_AND_ANOMALIES,
    )


def test_list_feature_monitors_jobs(
    get_feature_monitor_mock, list_feature_monitor_jobs_mock
):
    aiplatform.init(
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )

    feature_monitor_jobs = FeatureMonitor(
        _TEST_FG1_FM1_ID,
        feature_group_id=_TEST_FG1_ID,
    ).list_feature_monitor_jobs()

    list_feature_monitor_jobs_mock.assert_called_once_with(
        request={"parent": _TEST_FG1_FM1_PATH}
    )
    assert len(feature_monitor_jobs) == len(_TEST_FG1_FMJ_LIST)
    feature_monitor_job_eq(
        feature_monitor_jobs[0],
        resource_name=_TEST_FG1_FMJ1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_FMJ1_DESCRIPTION,
        labels=_TEST_FG1_FMJ1_LABELS,
    )
    feature_monitor_job_eq(
        feature_monitor_jobs[1],
        resource_name=_TEST_FG1_FMJ2_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_FMJ2_DESCRIPTION,
        labels=_TEST_FG1_FMJ2_LABELS,
    )
