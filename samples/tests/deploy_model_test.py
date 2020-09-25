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

from google.cloud import aiplatform as aip
from samples import deploy_model_sample, delete_endpoint_sample

from uuid import uuid4
import pytest

PROJECT_ID = "ucaip-sample-tests"
LOCATION = "us-central1"
PARENT = f"projects/{PROJECT_ID}/locations/{LOCATION}"
DISPLAY_NAME = f"temp_deploy_model_test_{uuid4()}"

# Resource Name of "permanent_50_flowers_new_model"
MODEL_NAME = "projects/580378083368/locations/us-central1/models/4190810559500779520"
CLIENT_OPTIONS = {
    "api_endpoint": "us-central1-aiplatform.googleapis.com"
}

ENDPOINT = None
ENDPOINT_CLIENT = None
DEPLOYED_MODEL_ID = None

@pytest.fixture(scope="function", autouse=True)
def setup():
    global ENDPOINT, ENDPOINT_CLIENT
    assert ENDPOINT is None

    # Create an temporary endpoint and store resource name
    ENDPOINT_CLIENT = aip.EndpointServiceClient(client_options=CLIENT_OPTIONS)
    create_endpoint_response = ENDPOINT_CLIENT.create_endpoint(
        parent=PARENT,
        endpoint={"display_name": DISPLAY_NAME}
    )
    ENDPOINT = create_endpoint_response.result().name


def test_ucaip_generated_deploy_model_sample(capsys):
    global DEPLOYED_MODEL_ID
    assert DEPLOYED_MODEL_ID is None
    assert ENDPOINT is not None

    # Deploy existing image classification model to endpoint
    deploy_model_sample.deploy_model_sample(
        project=PROJECT_ID,
        model_name=MODEL_NAME,
        deployed_model_display_name=DISPLAY_NAME,
        endpoint_id=ENDPOINT.split('/')[-1]
    )

    # Store deployed model ID for undeploying
    out, _ = capsys.readouterr()
    DEPLOYED_MODEL_ID = out.split("id:")[1].split("\n")[0].split(" ")[-1]
    assert "deploy_model_response" in out


@pytest.fixture(scope="function", autouse=True)
def teardown(capsys):
    yield

    assert DEPLOYED_MODEL_ID is not None

    undeploy_model_operation = ENDPOINT_CLIENT.undeploy_model(
        deployed_model_id=DEPLOYED_MODEL_ID,
        endpoint=ENDPOINT
    )
    undeploy_model_operation.result()

    # Delete the endpoint
    delete_endpoint_sample.delete_endpoint_sample(
        project=PROJECT_ID,
        endpoint_id=ENDPOINT.split('/')[-1]
    )

    out, _ = capsys.readouterr()
    assert "delete_endpoint_response" in out
