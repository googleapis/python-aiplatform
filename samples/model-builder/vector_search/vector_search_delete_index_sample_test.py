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
from vector_search import vector_search_delete_index_sample


def test_vector_search_delete_index_sample(
    mock_sdk_init,
    mock_index_init,
    mock_index_delete,
):
    vector_search_delete_index_sample.vector_search_delete_index(
        project=constants.PROJECT,
        location=constants.LOCATION,
        index_name=constants.VECTOR_SEARCH_INDEX,
    )

    # Check client initialization
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    # Check index initialization with right index name
    mock_index_init.assert_called_with(index_name=constants.VECTOR_SEARCH_INDEX)

    # Check index deletion
    mock_index_delete.assert_called()
