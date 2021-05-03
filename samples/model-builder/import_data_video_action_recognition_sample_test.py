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

from google.cloud.aiplatform import schema

import pytest

import import_data_video_action_recognition_sample

import test_constants as constants


@pytest.mark.usefixtures("mock_get_video_dataset")
def test_import_data_video_action_recognition_sample(
    mock_sdk_init, mock_import_video_data
):

    import_data_video_action_recognition_sample.import_data_video_action_recognition_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        dataset_name=constants.DATASET_NAME,
        src_uris=constants.GCS_SOURCES,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_import_video_data.assert_called_once_with(
        gcs_source=constants.GCS_SOURCES,
        import_schema_uri=schema.dataset.ioformat.video.action_recognition,
        sync=True,
    )
