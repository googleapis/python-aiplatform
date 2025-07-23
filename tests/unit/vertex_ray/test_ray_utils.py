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

from google.cloud.aiplatform import vertex_ray
import test_constants as tc
import pytest


class TestUtils:
    def test_get_persistent_resource_success(self, persistent_client_mock):
        response = vertex_ray.util._gapic_utils.get_persistent_resource(
            tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
        )

        persistent_client_mock.assert_called_once()
        assert response == tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL

    def test_get_persistent_resource_stopping(self, persistent_client_stopping_mock):
        with pytest.raises(RuntimeError) as e:
            vertex_ray.util._gapic_utils.get_persistent_resource(
                tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
            )

        persistent_client_stopping_mock.assert_called_once()
        e.match(regexp=r"Cluster .* is stopping.")

    def test_get_persistent_resource_error(self, persistent_client_error_mock):
        with pytest.raises(RuntimeError) as e:
            vertex_ray.util._gapic_utils.get_persistent_resource(
                tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
            )

        persistent_client_error_mock.assert_called_once()
        e.match(regexp=r"Cluster .* encountered an error.")
