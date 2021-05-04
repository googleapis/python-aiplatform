# Copyright 2021 Google LLC
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


import get_model_sample
import test_constants as constants


def test_get_model_sample(mock_sdk_init, mock_init_model):

    get_model_sample.get_model_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        model_name=constants.MODEL_NAME,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_init_model.assert_called_once_with(model_name=constants.MODEL_NAME)
