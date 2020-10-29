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

from uuid import uuid4
import pytest
import os

import helpers

from samples import (
    create_training_pipeline_sample,
    cancel_training_pipeline_sample,
    delete_training_pipeline_sample,
    get_training_pipeline_sample,
)

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
DATASET_ID = "1084241610289446912"  # Permanent 50 Flowers Dataset
DISPLAY_NAME = f"temp_create_training_pipeline_test_{uuid4()}"
TRAINING_DEFINITION_GCS_PATH = "gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_image_classification_1.0.0.yaml"


@pytest.fixture(scope="function")
def training_pipeline_id(capsys):
    create_training_pipeline_sample.create_training_pipeline_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        training_task_definition=TRAINING_DEFINITION_GCS_PATH,
        dataset_id=DATASET_ID,
        model_display_name=f"Temp Model for {DISPLAY_NAME}",
    )

    out, _ = capsys.readouterr()

    training_pipeline_name = helpers.get_name(out)

    training_pipeline_id = training_pipeline_name.split("/")[-1]

    yield training_pipeline_id


@pytest.fixture(scope="function", autouse=True)
def teardown(training_pipeline_id):
    yield

    delete_training_pipeline_sample.delete_training_pipeline_sample(
        project=PROJECT_ID, training_pipeline_id=training_pipeline_id
    )


def test_ucaip_generated_cancel_training_pipeline_sample(capsys, training_pipeline_id):
    cancel_training_pipeline_sample.cancel_training_pipeline_sample(
        project=PROJECT_ID, training_pipeline_id=training_pipeline_id
    )

    # check the state of the training pipeline
    training_pipeline = get_training_pipeline_sample.get_training_pipeline_sample(
        project=PROJECT_ID, training_pipeline_id=training_pipeline_id
    )

    out, _ = capsys.readouterr()

    import sys

    sys.stdout.write(out)

    state = helpers.get_state(out)

    # proto-plus>=1.10 prints Enum full name.
    assert state in ("7", "PIPELINE_STATE_CANCELLED")
