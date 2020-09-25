# Generated code sample for google.cloud.aiplatform.EndpointServiceClient.create_endpoint
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

import pytest
from uuid import uuid4

from samples import create_endpoint_sample, delete_endpoint_sample

DISPLAY_NAME = f"temp_create_endpoint_test_{uuid4()}"
PROJECT = "ucaip-sample-tests"
ENDPOINT_ID = None

@pytest.fixture(scope="function", autouse=True)
def teardown(capsys):
    yield

    assert ENDPOINT_ID is not None

    # Delete the endpoint that was just created
    delete_endpoint_sample.delete_endpoint_sample(
        project=PROJECT,
        endpoint_id=ENDPOINT_ID
    )

    out, _ = capsys.readouterr()
    assert "delete_endpoint_response:" in out


def test_ucaip_generated_create_endpoint_sample(capsys):
    global ENDPOINT_ID
    assert ENDPOINT_ID is None

    create_endpoint_sample.create_endpoint_sample(
        display_name=DISPLAY_NAME,
        project=PROJECT
    )

    out, _ = capsys.readouterr()
    assert "create_endpoint_response" in out

    ENDPOINT_ID = out.split("name:")[1].split("\n")[0].split("/")[-1]