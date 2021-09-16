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
from google.cloud import aiplatform_v1beta1 as aiplatform

import pytest

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_features):
    yield


def test_ucaip_generated_batch_create_features_sample_vision(capsys, shared_state):
    featurestore_id = "perm_sample_featurestore"
    entity_type_id = "perm_sample_entity_type"
    requests = [
        aiplatform.CreateFeatureRequest(
            feature=aiplatform.Feature(
                value_type=aiplatform.Feature.ValueType.STRING,
                description="lorem ipsum",
            ),
            feature_id=f"gender_{uuid4()}".replace("-", "_")[:60],
        ),
        aiplatform.CreateFeatureRequest(
            feature=aiplatform.Feature(
                value_type=aiplatform.Feature.ValueType.STRING_ARRAY,
                description="lorem ipsum",
            ),
            feature_id=f"liked_genres_{uuid4()}".replace("-", "_")[:60],
        ),
    ]
    location = "us-central1"
    batch_create_features_sample.batch_create_features_sample(
        project=PROJECT_ID,
        featurestore_id=featurestore_id,
        entity_type_id=entity_type_id,
        requests=requests,
        location=location,
    )
    out, _ = capsys.readouterr()
    assert "batch_create_features_response" in out

    parent = f"projects/{PROJECT_ID}/locations/{location}/featurestores/{featurestore_id}/entityTypes/{entity_type_id}/features/"
    shared_state["feature_names"] = []
    for request in requests:
        shared_state["feature_names"].append(parent + request.feature_id)
