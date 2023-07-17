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

from experiment_tracking import create_artifact_sample
import test_constants as constants


def test_create_artifact_sample(mock_artifact, mock_create_artifact):
    artifact = create_artifact_sample.create_artifact_sample(
        schema_title=constants.SCHEMA_TITLE,
        uri=constants.MODEL_ARTIFACT_URI,
        resource_id=constants.RESOURCE_ID,
        display_name=constants.DISPLAY_NAME,
        schema_version=constants.SCHEMA_VERSION,
        description=constants.DESCRIPTION,
        metadata=constants.METADATA,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_create_artifact.assert_called_with(
        schema_title=constants.SCHEMA_TITLE,
        uri=constants.MODEL_ARTIFACT_URI,
        resource_id=constants.RESOURCE_ID,
        display_name=constants.DISPLAY_NAME,
        schema_version=constants.SCHEMA_VERSION,
        description=constants.DESCRIPTION,
        metadata=constants.METADATA,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    assert artifact is mock_artifact
