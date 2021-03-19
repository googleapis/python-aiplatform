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


import create_and_import_dataset_image_sample


def test_create_and_import_dataset_image_sample(
    mock_sdk_init, mock_create_image_dataset
):

    create_and_import_dataset_image_sample.create_and_import_dataset_image_sample(
        project="abc", location="us-central1", src_uris=["123"], display_name="test_dn"
    )

    mock_sdk_init.assert_called_once()
    mock_create_image_dataset.assert_called_once()
