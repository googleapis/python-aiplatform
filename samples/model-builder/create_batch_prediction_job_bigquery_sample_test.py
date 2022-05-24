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


import create_batch_prediction_job_bigquery_sample
import test_constants as constants


def test_create_batch_prediction_job_bigquery_sample(
    mock_sdk_init, mock_model, mock_init_model, mock_batch_predict_model
):

    create_batch_prediction_job_bigquery_sample.create_batch_prediction_job_bigquery_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        model_resource_name=constants.MODEL_NAME,
        job_display_name=constants.DISPLAY_NAME,
        bigquery_source=constants.BIGQUERY_SOURCE,
        bigquery_destination_prefix=constants.BIGQUERY_DESTINATION_PREFIX,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )
    mock_init_model.assert_called_once_with(constants.MODEL_NAME)
    mock_batch_predict_model.assert_called_once_with(
        job_display_name=constants.DISPLAY_NAME,
        bigquery_source=constants.BIGQUERY_SOURCE,
        bigquery_destination_prefix=constants.BIGQUERY_DESTINATION_PREFIX,
        sync=True,
    )
