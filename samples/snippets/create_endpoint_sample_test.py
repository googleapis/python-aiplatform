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
import os
from uuid import uuid4

import helpers

import create_endpoint_sample, delete_endpoint_sample

DISPLAY_NAME = f"temp_create_endpoint_test_{uuid4()}"
PROJECT = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")


@pytest.fixture
def shared_state():
    state = {}
    yield state


@pytest.fixture(scope="function", autouse=True)
def teardown(shared_state):
    yield

    endpoint_id = shared_state["endpoint_name"].split("/")[-1]

    # Delete the endpoint that was just created
    delete_endpoint_sample.delete_endpoint_sample(
        project=PROJECT, endpoint_id=endpoint_id
    )


def test_ucaip_generated_create_endpoint_sample(capsys, shared_state):

    create_endpoint_sample.create_endpoint_sample(
        display_name=DISPLAY_NAME, project=PROJECT
    )

    out, _ = capsys.readouterr()
    assert "create_endpoint_response" in out

    shared_state["endpoint_name"] = helpers.get_name(out)
