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

from google.cloud import aiplatform

from experiment_tracking import start_execution_sample
import test_constants as constants


def test_start_execution_sample(
    mock_sdk_init,
    mock_get_execution,
    mock_get_artifact,
    mock_start_execution,
    mock_execution,
):

    input_art = aiplatform.Artifact()
    output_art = aiplatform.Artifact()

    exc = start_execution_sample.start_execution_sample(
        schema_title=constants.SCHEMA_TITLE,
        display_name=constants.DISPLAY_NAME,
        input_artifacts=[input_art],
        output_artifacts=[output_art],
        project=constants.PROJECT,
        location=constants.LOCATION,
        resource_id=constants.RESOURCE_ID,
        metadata=constants.METADATA,
        schema_version=constants.SCHEMA_VERSION,
        resume=True,
    )

    mock_sdk_init.assert_called_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_start_execution.assert_called_with(
        schema_title=constants.SCHEMA_TITLE,
        display_name=constants.DISPLAY_NAME,
        resource_id=constants.RESOURCE_ID,
        metadata=constants.METADATA,
        schema_version=constants.SCHEMA_VERSION,
        resume=True,
    )

    mock_execution.assign_input_artifacts.assert_called_with([input_art])
    mock_execution.assign_output_artifacts.assert_called_with([output_art])

    assert exc is mock_execution
