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


import create_and_import_dataset_time_series_gcs_sample
import test_constants as constants


def test_create_and_import_dataset_time_series_gcs_sample(
    mock_sdk_init, mock_create_time_series_dataset
):

    create_and_import_dataset_time_series_gcs_sample.create_and_import_dataset_time_series_gcs_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        gcs_source=constants.GCS_SOURCES,
        display_name=constants.DISPLAY_NAME,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )
    mock_create_time_series_dataset.assert_called_once_with(
        display_name=constants.DISPLAY_NAME,
        gcs_source=constants.GCS_SOURCES,
    )
