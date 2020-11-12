# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytest
import os
from unittest.mock import patch, mock_open, MagicMock

import import_data_text_classification_single_label_sample

# Test to assert that the import data function was called. We assert that the function was called
# rather than wait for this LRO to complete
def test_ucaip_generated_import_data_text_classification_single_label_sample():
    response = MagicMock()
    response.next_page_token = b""
    rpc = MagicMock(return_value=response)

    mock_channel = MagicMock()
    mock_channel.unary_unary = MagicMock(return_value=rpc)

    with patch(
        "google.api_core.grpc_helpers.create_channel", return_value=mock_channel
    ), patch("time.sleep"), patch("builtins.open", mock_open(read_data=b"")):
        import_data_text_classification_single_label_sample.import_data_text_classification_single_label_sample(
            gcs_source_uri="GCS_SOURCE_URI", project="PROJECT", dataset_id="DATASET_ID"
        )

        rpc.assert_called()
