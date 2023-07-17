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

from experiment_tracking import save_model_sample
import test_constants as constants


@pytest.mark.usefixtures("mock_sdk_init")
def test_save_model_sample(mock_save_model):

    save_model_sample.save_model_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        model=constants.ML_MODEL,
        artifact_id=constants.EXPERIMENT_MODEL_ID,
        uri=constants.MODEL_ARTIFACT_URI,
        input_example=constants.EXPERIMENT_MODEL_INPUT_EXAMPLE,
        display_name=constants.DISPLAY_NAME,
    )

    mock_save_model.assert_called_once_with(
        model=constants.ML_MODEL,
        artifact_id=constants.EXPERIMENT_MODEL_ID,
        uri=constants.MODEL_ARTIFACT_URI,
        input_example=constants.EXPERIMENT_MODEL_INPUT_EXAMPLE,
        display_name=constants.DISPLAY_NAME,
    )
