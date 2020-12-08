# Copyright 2020 Google LLC
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

import os
from uuid import uuid4

import pytest

import deploy_model_sample
import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"

# Resource Name of "permanent_50_flowers_new_model"
MODEL_NAME = "projects/580378083368/locations/us-central1/models/4190810559500779520"


@pytest.fixture(scope="function", autouse=True)
def setup(create_endpoint):
    create_endpoint(PROJECT_ID, LOCATION)
    yield


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_endpoint):
    yield


def test_ucaip_generated_deploy_model_sample(capsys, shared_state):

    assert shared_state["endpoint_name"] is not None

    # Deploy existing image classification model to endpoint
    deploy_model_sample.deploy_model_sample(
        project=PROJECT_ID,
        model_name=MODEL_NAME,
        deployed_model_display_name=f"temp_deploy_model_test_{uuid4()}",
        endpoint_id=shared_state["endpoint_name"].split("/")[-1],
    )

    # Store deployed model ID for undeploying
    out, _ = capsys.readouterr()
    assert "deploy_model_response" in out

    shared_state["deployed_model_id"] = helpers.get_name(out=out, key="id")
