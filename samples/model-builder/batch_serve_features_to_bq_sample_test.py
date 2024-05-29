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

import batch_serve_features_to_bq_sample
import test_constants as constants


def test_batch_serve_features_to_bq_sample(
    mock_sdk_init, mock_get_featurestore, mock_batch_serve_to_bq
):

    batch_serve_features_to_bq_sample.batch_serve_features_to_bq_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        featurestore_name=constants.FEATURESTORE_NAME,
        bq_destination_output_uri=constants.BQ_DESTINATION_OUTPUT_URI,
        read_instances_uri=constants.INPUT_CSV_FILE,
        sync=constants.SYNC,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_get_featurestore.assert_called_once_with(
        featurestore_name=constants.FEATURESTORE_NAME
    )

    mock_batch_serve_to_bq.assert_called_once_with(
        bq_destination_output_uri=constants.BQ_DESTINATION_OUTPUT_URI,
        serving_feature_ids=constants.SERVING_FEATURE_IDS,
        read_instances_uri=constants.INPUT_CSV_FILE,
        sync=constants.SYNC,
    )
