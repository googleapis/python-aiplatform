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

from google.cloud import aiplatform
import pytest

import list_model_evaluations_tabular_forecasting_sample
import helpers

PROJECT_ID = "ucaip-sample-tests"  # TODO: Revert this to os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
MODEL_ID = "8531330622239539200"  # COVID Dataset


@pytest.fixture
def shared_state():
    state = {}
    yield state


@pytest.fixture(scope="function", autouse=True)
def teardown(shared_state):
    yield


def test_ucaip_generated_create_training_pipeline_sample(capsys, shared_state):

    list_model_evaluations_tabular_forecasting_sample.list_model_evaluations_tabular_forecasting_sample(
        project=PROJECT_ID, model_id=MODEL_ID
    )

    out, _ = capsys.readouterr()
    assert "response:" in out

    # Save resource name of the newly created training pipeline
    shared_state["training_pipeline_name"] = helpers.get_name(out)
