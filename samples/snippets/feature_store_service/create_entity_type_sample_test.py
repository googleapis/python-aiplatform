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

import create_entity_type_sample
import pytest

import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_entity_type):
    yield


def test_ucaip_generated_create_entity_type_sample_vision(capsys, shared_state):
    featurestore_id = "perm_sample_featurestore"
    entity_type_id = f"temp_create_entity_type_test_{uuid4()}".replace("-", "_")[:60]
    create_entity_type_sample.create_entity_type_sample(
        project=PROJECT_ID,
        featurestore_id=featurestore_id,
        entity_type_id=entity_type_id,
    )
    out, _ = capsys.readouterr()
    assert "create_entity_type_response" in out

    shared_state["entity_type_name"] = helpers.get_featurestore_resource_name(out)
