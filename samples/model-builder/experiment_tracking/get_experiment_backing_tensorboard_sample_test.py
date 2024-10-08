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

from experiment_tracking import get_experiment_backing_tensorboard_sample
import test_constants as constants


def test_get_experiment_backing_tensorboard_sample(
    mock_get_experiment, mock_get_backing_tensorboard_resource
):

    get_experiment_backing_tensorboard_sample.get_experiment_backing_tensorboard_sample(
        experiment_name=constants.EXPERIMENT_NAME,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_get_experiment.assert_called_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
        experiment_name=constants.EXPERIMENT_NAME
    )

    mock_get_backing_tensorboard_resource.assert_called_once()
