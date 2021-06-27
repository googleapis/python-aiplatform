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


import predict_text_sentiment_analysis_sample
import test_constants as constants


def test_predict_text_sentiment_analysis_sample(mock_sdk_init, mock_get_endpoint):

    predict_text_sentiment_analysis_sample.predict_text_sentiment_analysis_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        endpoint_id=constants.ENDPOINT_NAME,
        content=constants.PREDICTION_TEXT_INSTANCE,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_get_endpoint.assert_called_once_with(constants.ENDPOINT_NAME,)
