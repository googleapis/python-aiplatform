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


import create_training_pipeline_image_classification_sample


def test_create_training_pipeline_image_classification_sample(
    mock_sdk_init,
    mock_init_automl_image_training_job,
    mock_init_dataset,
    mock_run_automl_image_training_job,
):

    create_training_pipeline_image_classification_sample.create_training_pipeline_image_classification_sample(
        project="abc123",
        display_name="678nod",
        dataset_id="123456789876554",
        model_display_name="newmodel",
        training_fraction_split=0.7,
        validation_fraction_split=0.15,
        test_fraction_split=0.15,
        budget_milli_node_hours=8000,
        disable_early_stopping=False,
    )

    mock_sdk_init.assert_called_once()
    mock_init_automl_image_training_job.assert_called_once()
    mock_init_dataset.assert_called_once()
    mock_run_automl_image_training_job.assert_called_once()
