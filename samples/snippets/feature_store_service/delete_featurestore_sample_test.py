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
from uuid import uuid4

import create_featurestore_sample
import delete_featurestore_sample
import pytest

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")


@pytest.fixture(scope="function", autouse=True)
def teardown():
    yield


def setup_test(capsys, featurestore_id):
    create_featurestore_sample.create_featurestore_sample(
        project=PROJECT_ID, featurestore_id=featurestore_id, fixed_node_count=1
    )
    out, _ = capsys.readouterr()
    assert "create_featurestore_response" in out


def test_ucaip_generated_delete_featurestore_sample_vision(capsys, shared_state):
    featurestore_id = f"temp_create_featurestore_test_{uuid4()}".replace("-", "_")[:60]
    setup_test(capsys, featurestore_id)
    delete_featurestore_sample.delete_featurestore_sample(
        project=PROJECT_ID, featurestore_id=featurestore_id
    )
    out, _ = capsys.readouterr()
    assert "delete_featurestore_response" in out
