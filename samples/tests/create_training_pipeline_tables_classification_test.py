# Generated code sample for google.cloud.aiplatform.PipelineServiceClient.create_training_pipeline
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

from samples import create_training_pipeline_tables_classification_sample, cancel_training_pipeline_sample, delete_training_pipeline_sample

PROJECT_ID = "ucaip-sample-tests"
DATASET_ID = "2438839935709478912" # iris 1000
DISPLAY_NAME = f"temp_create_training_pipeline_test_{uuid4()}"
TARGET_COLUMN = "species"
PREDICTION_TYPE = "classification"

TRAINING_PIPELINE_NAME = None

@pytest.fixture(scope="function", autouse=True)
def teardown(capsys):
    yield

    assert TRAINING_PIPELINE_NAME is not None

    training_pipeline_id = TRAINING_PIPELINE_NAME.split("/")[-1]

    # Stop the training pipeline
    cancel_training_pipeline_sample.cancel_training_pipeline_sample(
        project=PROJECT_ID,
        training_pipeline_id=training_pipeline_id
    )

    # Delete the training pipeline
    delete_training_pipeline_sample.delete_training_pipeline_sample(
        project=PROJECT_ID,
        training_pipeline_id=training_pipeline_id
    )

    out, _ = capsys.readouterr()
    assert "delete_training_pipeline_response" in out

def test_ucaip_generated_create_training_pipeline_sample(capsys):
    global TRAINING_PIPELINE_NAME
    assert TRAINING_PIPELINE_NAME is None

    create_training_pipeline_tables_classification_sample.create_training_pipeline_tables_classification_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        dataset_id=DATASET_ID,
        model_display_name=f"Temp Model for {DISPLAY_NAME}",
        target_column=TARGET_COLUMN
    )

    out, _ = capsys.readouterr()
    
    # Save resource name of the newly created training pipeline
    TRAINING_PIPELINE_NAME = out.split("name:")[1].split("\n")[0]
