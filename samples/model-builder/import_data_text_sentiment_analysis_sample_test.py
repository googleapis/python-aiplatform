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

import import_data_text_sentiment_analysis_sample
import test_constants as constants


def test_import_data_text_sentiment_analysis_sample(
    mock_sdk_init, mock_get_text_dataset, mock_import_text_dataset
):

    import_data_text_sentiment_analysis_sample.import_data_text_sentiment_analysis_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        dataset=constants.DATASET_NAME,
        src_uris=constants.GCS_SOURCES,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_get_text_dataset.assert_called_once_with(constants.DATASET_NAME,)

    mock_import_text_dataset.assert_called_once_with(
        gcs_source=constants.GCS_SOURCES,
        import_schema_uri=schema.dataset.ioformat.text.sentiment,
        sync=True,
    )
