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


import create_training_pipeline_tabular_regression_sample
import test_constants as constants


def test_create_training_pipeline_tabular_regression_sample(
    mock_sdk_init,
    mock_tabular_dataset,
    mock_get_automl_tabular_training_job,
    mock_run_automl_tabular_training_job,
    mock_get_tabular_dataset,
):

    create_training_pipeline_tabular_regression_sample.create_training_pipeline_tabular_regression_sample(
        project=constants.PROJECT,
        display_name=constants.DISPLAY_NAME,
        dataset_id=constants.RESOURCE_ID,
        model_display_name=constants.DISPLAY_NAME_2,
        training_fraction_split=constants.TRAINING_FRACTION_SPLIT,
        validation_fraction_split=constants.VALIDATION_FRACTION_SPLIT,
        test_fraction_split=constants.TEST_FRACTION_SPLIT,
        budget_milli_node_hours=constants.BUDGET_MILLI_NODE_HOURS_8000,
        disable_early_stopping=False,
    )

    mock_get_tabular_dataset.assert_called_once_with(constants.RESOURCE_ID)

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )
    mock_get_automl_tabular_training_job.assert_called_once_with(
        display_name=constants.DISPLAY_NAME,
    )
    mock_run_automl_tabular_training_job.assert_called_once_with(
        dataset=mock_tabular_dataset,
        model_display_name=constants.DISPLAY_NAME_2,
        training_fraction_split=constants.TRAINING_FRACTION_SPLIT,
        validation_fraction_split=constants.VALIDATION_FRACTION_SPLIT,
        test_fraction_split=constants.TEST_FRACTION_SPLIT,
        budget_milli_node_hours=constants.BUDGET_MILLI_NODE_HOURS_8000,
        disable_early_stopping=False,
        sync=True,
    )
