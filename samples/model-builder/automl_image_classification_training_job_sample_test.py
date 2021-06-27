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


import automl_image_classification_training_job_sample
import test_constants as constants


def test_automl_image_classification_training_job_sample(
    mock_sdk_init,
    mock_image_dataset,
    mock_get_image_dataset,
    mock_get_automl_image_training_job,
    mock_run_automl_image_training_job,
):
    automl_image_classification_training_job_sample.automl_image_classification_training_job_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        dataset_id=constants.DATASET_NAME,
        display_name=constants.DISPLAY_NAME,
    )

    mock_get_image_dataset.assert_called_once_with(constants.DATASET_NAME)

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_get_automl_image_training_job.assert_called_once_with(
        display_name=constants.DISPLAY_NAME,
        base_model=None,
        model_type="CLOUD",
        multi_label=False,
        prediction_type="classification",
    )

    mock_run_automl_image_training_job.assert_called_once_with(
        budget_milli_node_hours=8000,
        disable_early_stopping=False,
        test_fraction_split=0.2,
        training_fraction_split=0.6,
        validation_fraction_split=0.2,
        model_display_name=constants.DISPLAY_NAME,
        dataset=mock_image_dataset,
    )
