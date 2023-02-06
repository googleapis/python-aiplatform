# Copyright 2023 Google LLC
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

import pytest

from experiment_tracking import register_experiment_model_sample
import test_constants as constants


@pytest.mark.usefixtures("mock_get_run")
def test_register_experiment_model_sample(
    mock_get_experiment_model, mock_register_model, mock_model
):

    registered_model = (
        register_experiment_model_sample.register_experiment_model_sample(
            artifact_id=constants.EXPERIMENT_MODEL_ID,
            project=constants.PROJECT,
            location=constants.LOCATION,
            display_name=constants.DISPLAY_NAME,
        )
    )

    mock_get_experiment_model.assert_called_once_with(
        artifact_id=constants.EXPERIMENT_MODEL_ID,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )
    mock_register_model.assert_called_once_with(
        display_name=constants.DISPLAY_NAME,
    )

    assert registered_model is mock_model
