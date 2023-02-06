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

from experiment_tracking import create_execution_with_sdk_sample
import test_constants as constants


def test_create_execution_sample(
    mock_sdk_init,
    mock_create_artifact,
    mock_create_schema_base_execution,
    mock_execution,
):

    input_art = mock_create_artifact()
    output_art = mock_create_artifact()

    exc = create_execution_with_sdk_sample.create_execution_sample(
        display_name=constants.DISPLAY_NAME,
        input_artifacts=[input_art],
        output_artifacts=[output_art],
        project=constants.PROJECT,
        location=constants.LOCATION,
        execution_id=constants.RESOURCE_ID,
        metadata=constants.METADATA,
        schema_version=constants.SCHEMA_VERSION,
        description=constants.DESCRIPTION,
    )

    mock_sdk_init.assert_called_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_create_schema_base_execution.assert_called_with()

    mock_execution.assign_input_artifacts.assert_called_with([input_art])
    mock_execution.assign_output_artifacts.assert_called_with([output_art])

    assert exc is mock_execution
