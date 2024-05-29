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

from experiment_tracking import assign_artifact_as_execution_output_sample


def test_assign_artifact_as_execution_output_sample(
    mock_get_execution,
    mock_get_artifact,
):
    exc = aiplatform.Execution()
    art = aiplatform.Artifact()
    assign_artifact_as_execution_output_sample.assign_artifact_as_execution_output_sample(
        execution=exc, artifact=art
    )

    exc.assign_output_artifacts.assert_called_with([art])
