# Copyright 2021 Google LLC
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

import os

import pytest
import read_feature_values_sample

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")


@pytest.fixture(scope="function", autouse=True)
def teardown():
    yield


def test_ucaip_generated_read_feature_values_sample_vision(capsys, shared_state):
    featurestore_id = "perm_sample_featurestore"
    entity_type_id = "perm_users"
    read_feature_values_sample.read_feature_values_sample(
        project=PROJECT_ID,
        featurestore_id=featurestore_id,
        entity_type_id=entity_type_id,
        entity_id="alice",
    )
    out, _ = capsys.readouterr()
    assert "int64_value: 55" in out
