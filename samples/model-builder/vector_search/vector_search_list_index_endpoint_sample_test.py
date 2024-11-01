# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import test_constants as constants
from vector_search import vector_search_list_index_endpoint_sample


def test_vector_search_list_index_sample(
    mock_sdk_init,
    mock_index_endpoint,
    mock_list_index_endpoints,
):
    index_endpoints = vector_search_list_index_endpoint_sample.vector_search_list_index_endpoint(
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_sdk_init.assert_called_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
    )
    mock_list_index_endpoints.assert_called()
    assert len(index_endpoints) == 2
    assert index_endpoints[0] is mock_index_endpoint
    assert index_endpoints[1] is mock_index_endpoint
