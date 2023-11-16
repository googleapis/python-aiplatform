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

from experiment_tracking import list_artifact_sample
import test_constants as constants


def test_list_artifact_with_sdk_sample(mock_artifact, mock_list_artifact):
    artifacts = list_artifact_sample.list_artifact_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        display_name_filter=constants.DISPLAY_NAME,
        create_date_filter=constants.CREATE_DATE,
        order_by=constants.ORDER_BY,
    )

    mock_list_artifact.assert_called_with(
        filter=f"{constants.DISPLAY_NAME} AND {constants.CREATE_DATE}",
        order_by=constants.ORDER_BY,
    )
    assert len(artifacts) == 2
    # Returning list of 2 context to avoid confusion with get method
    # which returns one unique context.
    assert artifacts[0] is mock_artifact
    assert artifacts[1] is mock_artifact
