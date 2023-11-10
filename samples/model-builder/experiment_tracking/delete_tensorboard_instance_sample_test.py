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

from experiment_tracking import delete_tensorboard_instance_sample
import test_constants


def test_delete_tensorboard_instance_sample(mock_tensorboard, mock_get_tensorboard):
    delete_tensorboard_instance_sample.delete_tensorboard_instance_sample(
        tensorboard_name=test_constants.TENSORBOARD_NAME,
        project=test_constants.PROJECT,
        location=test_constants.LOCATION,
    )

    mock_get_tensorboard.assert_called_with(
        tensorboard_name=test_constants.TENSORBOARD_NAME,
        project=test_constants.PROJECT,
        location=test_constants.LOCATION,
    )

    mock_tensorboard.delete.assert_called()
