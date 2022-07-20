# Copyright 2022 Google LLC
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

import list_context_sample

import test_constants


def test_list_context_sample(mock_context, mock_context_list):
    context = list_context_sample.list_context_sample(
        context_id=test_constants.RESOURCE_ID,
        project=test_constants.PROJECT,
        location=test_constants.LOCATION,
        )

    mock_context_list.assert_called_with(
        resource_id=test_constants.RESOURCE_ID,
        project=test_constants.PROJECT,
        location=test_constants.LOCATION,
        )

    assert context[0] is mock_context
    assert context[1] is mock_context