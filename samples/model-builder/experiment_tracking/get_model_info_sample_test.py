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

from experiment_tracking import get_model_info_sample
import test_constants as constants


@pytest.mark.usefixtures("mock_get_run")
def test_get_model_info_sample(
    mock_get_experiment_model, mock_get_model_info, mock_model_info
):

    model_info = get_model_info_sample.get_model_info_sample(
        artifact_id=constants.EXPERIMENT_MODEL_ID,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_get_experiment_model.assert_called_once_with(
        artifact_id=constants.EXPERIMENT_MODEL_ID,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )
    mock_get_model_info.assert_called_once()

    assert model_info is mock_model_info
