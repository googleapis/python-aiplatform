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

from experiment_tracking import get_artifact_with_uri_sample
import test_constants


def test_get_artifact_with_uri_sample(mock_artifact, mock_get_with_uri):
    artifact = get_artifact_with_uri_sample.get_artifact_with_uri_sample(
        uri=test_constants.MODEL_ARTIFACT_URI,
        project=test_constants.PROJECT,
        location=test_constants.LOCATION,
    )

    mock_get_with_uri.assert_called_with(
        uri=test_constants.MODEL_ARTIFACT_URI,
        project=test_constants.PROJECT,
        location=test_constants.LOCATION,
    )

    assert artifact is mock_artifact
