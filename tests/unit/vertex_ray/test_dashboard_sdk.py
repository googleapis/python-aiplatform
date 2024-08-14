# Copyright 2023 Google LLC
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
import importlib

from google.cloud import aiplatform
from google.cloud.aiplatform import vertex_ray
import test_constants as tc
import mock
import pytest
from ray.dashboard.modules import dashboard_sdk as oss_dashboard_sdk


# -*- coding: utf-8 -*-


@pytest.fixture
def ray_get_job_submission_client_cluster_info_mock():
    with mock.patch.object(
        oss_dashboard_sdk, "get_job_submission_client_cluster_info"
    ) as ray_get_job_submission_client_cluster_info_mock:
        yield ray_get_job_submission_client_cluster_info_mock


@pytest.fixture
def get_persistent_resource_status_running_mock():
    with mock.patch.object(
        vertex_ray.util._gapic_utils, "get_persistent_resource"
    ) as get_persistent_resource:
        get_persistent_resource.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL
        )
        yield get_persistent_resource


@pytest.fixture
def get_persistent_resource_status_running_byosa_public_mock():
    # Cluster with BYOSA and no peering
    with mock.patch.object(
        vertex_ray.util._gapic_utils, "get_persistent_resource"
    ) as get_persistent_resource:
        get_persistent_resource.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL_BYOSA
        )
        yield get_persistent_resource


@pytest.fixture
def get_bearer_token_mock():
    with mock.patch.object(
        vertex_ray.util._validation_utils, "get_bearer_token"
    ) as get_bearer_token_mock:
        get_bearer_token_mock.return_value = tc.ClusterConstants.TEST_BEARER_TOKEN
        yield get_bearer_token_mock


class TestGetJobSubmissionClientClusterInfo:
    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures(
        "get_persistent_resource_status_running_mock", "google_auth_mock"
    )
    def test_job_submission_client_cluster_info_with_full_resource_name(
        self,
        ray_get_job_submission_client_cluster_info_mock,
        get_bearer_token_mock,
    ):
        vertex_ray.get_job_submission_client_cluster_info(
            tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
        )
        get_bearer_token_mock.assert_called_once_with()
        ray_get_job_submission_client_cluster_info_mock.assert_called_once_with(
            address=tc.ClusterConstants.TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
            _use_tls=True,
            headers=tc.ClusterConstants.TEST_HEADERS,
        )

    @pytest.mark.usefixtures(
        "get_persistent_resource_status_running_mock", "google_auth_mock"
    )
    def test_job_submission_client_cluster_info_with_cluster_name(
        self,
        ray_get_job_submission_client_cluster_info_mock,
        get_project_number_mock,
        get_bearer_token_mock,
    ):
        aiplatform.init(project=tc.ProjectConstants.TEST_GCP_PROJECT_ID)

        vertex_ray.get_job_submission_client_cluster_info(
            tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID
        )
        get_project_number_mock.assert_called_once_with(
            name="projects/{}".format(tc.ProjectConstants.TEST_GCP_PROJECT_ID)
        )
        get_bearer_token_mock.assert_called_once_with()
        ray_get_job_submission_client_cluster_info_mock.assert_called_once_with(
            address=tc.ClusterConstants.TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
            _use_tls=True,
            headers=tc.ClusterConstants.TEST_HEADERS,
        )

    @pytest.mark.usefixtures(
        "get_persistent_resource_status_running_mock", "google_auth_mock"
    )
    def test_job_submission_client_cluster_info_with_dashboard_address(
        self,
        ray_get_job_submission_client_cluster_info_mock,
        get_bearer_token_mock,
    ):
        aiplatform.init(project=tc.ProjectConstants.TEST_GCP_PROJECT_ID)

        vertex_ray.get_job_submission_client_cluster_info(
            tc.ClusterConstants.TEST_VERTEX_RAY_DASHBOARD_ADDRESS
        )
        get_bearer_token_mock.assert_called_once_with()
        ray_get_job_submission_client_cluster_info_mock.assert_called_once_with(
            address=tc.ClusterConstants.TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
            _use_tls=True,
            headers=tc.ClusterConstants.TEST_HEADERS,
        )

    @pytest.mark.usefixtures(
        "get_persistent_resource_status_running_byosa_public_mock", "google_auth_mock"
    )
    def test_job_submission_client_cluster_info_with_cluster_name_byosa_public(
        self,
        ray_get_job_submission_client_cluster_info_mock,
        get_bearer_token_mock,
        get_project_number_mock,
    ):
        aiplatform.init(project=tc.ProjectConstants.TEST_GCP_PROJECT_ID)

        vertex_ray.get_job_submission_client_cluster_info(
            tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID
        )
        get_project_number_mock.assert_called_once_with(
            name="projects/{}".format(tc.ProjectConstants.TEST_GCP_PROJECT_ID)
        )
        get_bearer_token_mock.assert_called_once_with()
        ray_get_job_submission_client_cluster_info_mock.assert_called_once_with(
            address=tc.ClusterConstants.TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
            _use_tls=True,
            headers=tc.ClusterConstants.TEST_HEADERS,
        )
