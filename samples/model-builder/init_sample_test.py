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


import init_sample

from google.auth import credentials


def test_init_sample(mock_sdk_init):

    init_sample.init_sample(
        project="abc",
        location="europe-west4",
        experiment="fraud-detection-72",
        staging_bucket="gs://my-staging-bucket",
        credentials=credentials.AnonymousCredentials(),
        encryption_spec_key_name="projects/abc/locations/europe-west4/keyRings/789/cryptoKeys/123",
    )

    mock_sdk_init.assert_called_once()
