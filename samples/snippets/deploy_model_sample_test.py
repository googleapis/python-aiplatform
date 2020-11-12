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

from google.cloud import aiplatform
import deploy_model_sample, delete_endpoint_sample

from uuid import uuid4
import pytest
import os

import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
PARENT = f"projects/{PROJECT_ID}/locations/{LOCATION}"
DISPLAY_NAME = f"temp_deploy_model_test_{uuid4()}"

# Resource Name of "permanent_50_flowers_new_model"
MODEL_NAME = "projects/580378083368/locations/us-central1/models/4190810559500779520"
CLIENT_OPTIONS = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}


@pytest.fixture
def shared_state():
    state = {}
    yield state


@pytest.fixture(scope="function", autouse=True)
def setup(shared_state):

    # Create an temporary endpoint and store resource name
    shared_state["endpoint_client"] = aiplatform.gapic.EndpointServiceClient(
        client_options=CLIENT_OPTIONS
    )
    create_endpoint_response = shared_state["endpoint_client"].create_endpoint(
        parent=PARENT, endpoint={"display_name": DISPLAY_NAME}
    )
    shared_state["endpoint"] = create_endpoint_response.result().name


def test_ucaip_generated_deploy_model_sample(capsys, shared_state):

    assert shared_state["endpoint"] is not None

    # Deploy existing image classification model to endpoint
    deploy_model_sample.deploy_model_sample(
        project=PROJECT_ID,
        model_name=MODEL_NAME,
        deployed_model_display_name=DISPLAY_NAME,
        endpoint_id=shared_state["endpoint"].split("/")[-1],
    )

    # Store deployed model ID for undeploying
    out, _ = capsys.readouterr()
    assert "deploy_model_response" in out

    shared_state["deployed_model_id"] = helpers.get_name(out=out, key="id")


@pytest.fixture(scope="function", autouse=True)
def teardown(shared_state):
    yield

    undeploy_model_operation = shared_state["endpoint_client"].undeploy_model(
        deployed_model_id=shared_state["deployed_model_id"],
        endpoint=shared_state["endpoint"],
    )
    undeploy_model_operation.result()

    # Delete the endpoint
    delete_endpoint_sample.delete_endpoint_sample(
        project=PROJECT_ID, endpoint_id=shared_state["endpoint"].split("/")[-1]
    )
