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
import ray


# -*- coding: utf-8 -*-

_TEST_CLIENT_CONTEXT = ray.client_builder.ClientContext(
    dashboard_url=tc.ClusterConstants.TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
    python_version="MOCK_PYTHON_VERSION",
    ray_version="MOCK_RAY_VERSION",
    ray_commit="MOCK_RAY_COMMIT",
    _num_clients=1,
    _context_to_restore=None,
)

_TEST_VERTEX_RAY_CLIENT_CONTEXT = vertex_ray.client_builder._VertexRayClientContext(
    persistent_resource_id="MOCK_PERSISTENT_RESOURCE_ID",
    ray_head_uris={
        "RAY_DASHBOARD_URI": tc.ClusterConstants.TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
        "RAY_HEAD_NODE_INTERNAL_IP": tc.ClusterConstants.TEST_VERTEX_RAY_HEAD_NODE_IP,
    },
    ray_client_context=_TEST_CLIENT_CONTEXT,
)

_TEST_VERTEX_RAY_CLIENT_CONTEXT_PUBLIC = (
    vertex_ray.client_builder._VertexRayClientContext(
        persistent_resource_id="MOCK_PERSISTENT_RESOURCE_ID",
        ray_head_uris={
            "RAY_DASHBOARD_URI": tc.ClusterConstants.TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
            "RAY_CLIENT_ENDPOINT": tc.ClusterConstants.TEST_VERTEX_RAY_CLIENT_ENDPOINT,
        },
        ray_client_context=_TEST_CLIENT_CONTEXT,
    )
)


@pytest.fixture
def ray_client_init_mock():
    with mock.patch.object(ray.ClientBuilder, "__init__") as ray_client_init:
        ray_client_init.return_value = None
        yield ray_client_init


@pytest.fixture
def ray_client_connect_mock():
    with mock.patch.object(ray.ClientBuilder, "connect") as ray_client_connect:
        ray_client_connect.return_value = _TEST_CLIENT_CONTEXT
        yield ray_client_connect


@pytest.fixture
def get_persistent_resource_status_running_mock():
    with mock.patch.object(
        vertex_ray.util._gapic_utils, "get_persistent_resource"
    ) as resolve_head_ip:
        resolve_head_ip.return_value = tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL
        yield resolve_head_ip


@pytest.fixture
def get_persistent_resource_status_running_no_ray_mock():
    with mock.patch.object(
        vertex_ray.util._gapic_utils, "get_persistent_resource"
    ) as resolve_head_ip:
        resolve_head_ip.return_value = tc.ClusterConstants.TEST_RESPONSE_NO_RAY_RUNNING
        yield resolve_head_ip


@pytest.fixture
def get_persistent_resource_status_running_byosa_public_mock():
    with mock.patch.object(
        vertex_ray.util._gapic_utils, "get_persistent_resource"
    ) as resolve_head_ip:
        resolve_head_ip.return_value = tc.ClusterConstants.TEST_RESPONSE_1_POOL_BYOSA
        yield resolve_head_ip


@pytest.fixture
def get_persistent_resource_status_running_byosa_private_mock():
    with mock.patch.object(
        vertex_ray.util._gapic_utils, "get_persistent_resource"
    ) as resolve_head_ip:
        resolve_head_ip.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_1_POOL_BYOSA_PRIVATE
        )
        yield resolve_head_ip


class TestClientBuilder:
    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @tc.rovminversion
    @pytest.mark.usefixtures("get_persistent_resource_status_running_mock")
    def test_init_with_full_resource_name(
        self,
        ray_client_init_mock,
    ):
        vertex_ray.ClientBuilder(tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS)
        ray_client_init_mock.assert_called_once_with(
            tc.ClusterConstants.TEST_VERTEX_RAY_HEAD_NODE_IP,
        )

    @tc.rovminversion
    @pytest.mark.usefixtures(
        "get_persistent_resource_status_running_mock", "google_auth_mock"
    )
    def test_init_with_cluster_name(
        self,
        ray_client_init_mock,
        get_project_number_mock,
    ):
        aiplatform.init(project=tc.ProjectConstants.TEST_GCP_PROJECT_ID)

        vertex_ray.ClientBuilder(tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID)
        get_project_number_mock.assert_called_once_with(
            name="projects/{}".format(tc.ProjectConstants.TEST_GCP_PROJECT_ID)
        )
        ray_client_init_mock.assert_called_once_with(
            tc.ClusterConstants.TEST_VERTEX_RAY_HEAD_NODE_IP,
        )

    @tc.rovminversion
    @pytest.mark.usefixtures("get_persistent_resource_status_running_mock")
    def test_connect_running(self, ray_client_connect_mock):
        connect_result = vertex_ray.ClientBuilder(
            tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
        ).connect()
        ray_client_connect_mock.assert_called_once_with()
        assert connect_result == _TEST_VERTEX_RAY_CLIENT_CONTEXT
        assert (
            connect_result.persistent_resource_id
            == tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID
        )

    @tc.rovminversion
    @pytest.mark.usefixtures("get_persistent_resource_status_running_no_ray_mock")
    def test_connect_running_no_ray(self, ray_client_connect_mock):
        expected_message = (
            "Ray Cluster ",
            tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
            " failed to start Head node properly.",
        )
        with pytest.raises(ValueError) as exception:
            vertex_ray.ClientBuilder(
                tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
            ).connect()

            ray_client_connect_mock.assert_called_once_with()
            assert str(exception.value) == expected_message

    @tc.rovminversion
    @pytest.mark.usefixtures("get_persistent_resource_status_running_byosa_public_mock")
    def test_connect_running_byosa_public(self, ray_client_connect_mock):
        connect_result = vertex_ray.ClientBuilder(
            tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
        ).connect()
        ray_client_connect_mock.assert_called_once_with()
        assert connect_result == _TEST_VERTEX_RAY_CLIENT_CONTEXT_PUBLIC
        assert (
            connect_result.persistent_resource_id
            == tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID
        )

    @tc.rovminversion
    @pytest.mark.usefixtures(
        "get_persistent_resource_status_running_byosa_private_mock"
    )
    def test_connect_running_byosa_private(self, ray_client_connect_mock):
        expected_message = (
            "Ray Cluster ",
            tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
            " failed to start Head node properly because custom service"
            " account isn't supported in peered VPC network. ",
        )
        with pytest.raises(ValueError) as exception:
            vertex_ray.ClientBuilder(
                tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
            ).connect()

            ray_client_connect_mock.assert_called_once_with()
            assert str(exception.value) == expected_message

    @tc.rovminversion
    @pytest.mark.parametrize(
        "address",
        [
            "bad/format/address",
            "must/have/exactly/five/backslashes/no/more/or/less",
            "do/not/append/a/trailing/backslash/",
            tc.ClusterConstants.TEST_VERTEX_RAY_HEAD_NODE_IP,  # cannot input raw head node ip
        ],
    )
    def test_bad_format_address(self, address):
        expected_message = (
            "[Ray on Vertex AI]: Address must be in the following format: "
            "vertex_ray://projects/<project_num>/locations/<region>/"
            "persistentResources/<pr_id> or vertex_ray://<pr_id>."
        )

        with pytest.raises(ValueError) as exception:
            vertex_ray.ClientBuilder(address)

        assert str(exception.value) == expected_message
