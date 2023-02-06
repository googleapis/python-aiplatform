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

from experiment_tracking import delete_artifact_sample
import test_constants as constants


def test_delete_artifact_sample(mock_artifact, mock_artifact_get):
    delete_artifact_sample.delete_artifact_sample(
        artifact_id=constants.RESOURCE_ID,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_artifact_get.assert_called_with(
        resource_id=constants.RESOURCE_ID,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )
