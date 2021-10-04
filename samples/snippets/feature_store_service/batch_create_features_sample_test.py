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

import batch_create_features_sample
import create_entity_type_sample

import pytest

import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_entity_type):
    yield


def setup_temp_entity_type(featurestore_id, entity_type_id, capsys):
    create_entity_type_sample.create_entity_type_sample(
        project=PROJECT_ID,
        featurestore_id=featurestore_id,
        entity_type_id=entity_type_id,
    )
    out, _ = capsys.readouterr()
    assert "create_entity_type_response" in out
    return helpers.get_featurestore_resource_name(out)


def test_ucaip_generated_batch_create_features_sample_vision(capsys, shared_state):
    featurestore_id = "perm_sample_featurestore"
    entity_type_id = f"users_{uuid4()}".replace("-", "_")[:60]
    entity_type_name = setup_temp_entity_type(featurestore_id, entity_type_id, capsys)
    location = "us-central1"
    batch_create_features_sample.batch_create_features_sample(
        project=PROJECT_ID,
        featurestore_id=featurestore_id,
        entity_type_id=entity_type_id,
        location=location,
    )
    out, _ = capsys.readouterr()
    assert "batch_create_features_response" in out

    shared_state["entity_type_name"] = entity_type_name
