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
import import_feature_values_sample
import pytest

import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
AVRO_GCS_URI = (
    "gs://cloud-samples-data-us-central1/vertex-ai/feature-store/datasets/users.avro"
)


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_entity_type):
    yield


def setup_features(featurestore_id, entity_type_id, capsys):
    batch_create_features_sample.batch_create_features_sample(
        project=PROJECT_ID,
        featurestore_id=featurestore_id,
        entity_type_id=entity_type_id,
    )
    out, _ = capsys.readouterr()
    assert "batch_create_features_response" in out


def setup_temp_entity_type(featurestore_id, entity_type_id, capsys):
    create_entity_type_sample.create_entity_type_sample(
        project=PROJECT_ID,
        featurestore_id=featurestore_id,
        entity_type_id=entity_type_id,
    )
    out, _ = capsys.readouterr()
    assert "create_entity_type_response" in out
    return helpers.get_featurestore_resource_name(out)


def test_ucaip_generated_import_feature_values_sample_vision(capsys, shared_state):
    featurestore_id = "perm_sample_featurestore"
    entity_type_id = f"users_{uuid4()}".replace("-", "_")[:60]
    entity_type_name = setup_temp_entity_type(featurestore_id, entity_type_id, capsys)
    setup_features(featurestore_id, entity_type_id, capsys)

    import_feature_values_sample.import_feature_values_sample(
        project=PROJECT_ID,
        featurestore_id=featurestore_id,
        entity_type_id=entity_type_id,
        avro_gcs_uri=AVRO_GCS_URI,
        entity_id_field="user_id",
        feature_time_field="update_time",
        worker_count=2,
        timeout=60 * 30,
    )

    out, _ = capsys.readouterr()
    assert "imported_feature_value_count: 12" in out

    shared_state["entity_type_name"] = entity_type_name
