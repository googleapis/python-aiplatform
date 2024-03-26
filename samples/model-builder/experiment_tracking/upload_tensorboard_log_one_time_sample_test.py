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


from experiment_tracking import upload_tensorboard_log_one_time_sample
import test_constants as constants


def test_upload_tensorboard_log_one_time_sample(
    mock_sdk_init,
    mock_tensorboard_uploader_onetime,
):
    upload_tensorboard_log_one_time_sample.upload_tensorboard_log_one_time_sample(
        tensorboard_id=constants.TENSORBOARD_ID,
        tensorboard_experiment_name=constants.TENSORBOARD_EXPERIMENT_NAME,
        project=constants.PROJECT,
        location=constants.LOCATION,
        logdir=constants.TENSORBOARD_LOG_DIR,
        run_name_prefix=constants.EXPERIMENT_RUN_NAME,
        allowed_plugins=constants.TENSORBOARD_PLUGIN_PROFILE_NAME,
        experiment_display_name=constants.EXPERIMENT_NAME,
        description=constants.DESCRIPTION,
        verbosity=constants.VERBOSITY,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
        experiment=constants.TENSORBOARD_EXPERIMENT_NAME,
    )

    mock_tensorboard_uploader_onetime.assert_called_once_with(
        tensorboard_id=constants.TENSORBOARD_ID,
        tensorboard_experiment_name=constants.TENSORBOARD_EXPERIMENT_NAME,
        logdir=constants.TENSORBOARD_LOG_DIR,
        run_name_prefix=constants.EXPERIMENT_RUN_NAME,
        allowed_plugins=constants.TENSORBOARD_PLUGIN_PROFILE_NAME,
        experiment_display_name=constants.EXPERIMENT_NAME,
        description=constants.DESCRIPTION,
        verbosity=constants.VERBOSITY,
    )
