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
from google.cloud import storage
import pytest

import helpers


@pytest.fixture()
def shared_state():
    state = {}
    yield state


@pytest.fixture
def storage_client():
    storage_client = storage.Client()
    return storage_client


@pytest.fixture()
def job_client():
    job_client = aiplatform.gapic.JobServiceClient(
        client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    )
    return job_client


@pytest.fixture()
def data_labeling_job_client():
    data_labeling_api_endpoint = os.getenv("DATA_LABELING_API_ENDPOINT")
    data_labeling_job_client = aiplatform.gapic.JobServiceClient(
        client_options={"api_endpoint": data_labeling_api_endpoint}
    )
    return data_labeling_job_client


@pytest.fixture
def pipeline_client():
    pipeline_client = aiplatform.gapic.PipelineServiceClient(
        client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    )
    return pipeline_client


@pytest.fixture
def model_client():
    model_client = aiplatform.gapic.ModelServiceClient(
        client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    )
    yield model_client


@pytest.fixture
def endpoint_client():
    endpoint_client = aiplatform.gapic.EndpointServiceClient(
        client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    )
    yield endpoint_client


@pytest.fixture
def dataset_client():
    dataset_client = aiplatform.gapic.DatasetServiceClient(
        client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    )
    yield dataset_client


# Shared setup/teardown.
@pytest.fixture()
def teardown_batch_prediction_job(shared_state, job_client):
    yield

    job_client.cancel_batch_prediction_job(
        name=shared_state["batch_prediction_job_name"]
    )

    # Waiting until the job is in CANCELLED state.
    helpers.wait_for_job_state(
        get_job_method=job_client.get_batch_prediction_job,
        name=shared_state["batch_prediction_job_name"],
    )

    job_client.delete_batch_prediction_job(
        name=shared_state["batch_prediction_job_name"]
    )


@pytest.fixture()
def teardown_data_labeling_job(capsys, shared_state, data_labeling_job_client):
    yield

    assert "/" in shared_state["data_labeling_job_name"]

    data_labeling_job_client.cancel_data_labeling_job(
        name=shared_state["data_labeling_job_name"]
    )

    # Verify Data Labelling Job is cancelled, or timeout after 400 seconds
    helpers.wait_for_job_state(
        get_job_method=data_labeling_job_client.get_data_labeling_job,
        name=shared_state["data_labeling_job_name"],
        timeout=400,
        freq=10,
    )

    # Delete the data labeling job
    response = data_labeling_job_client.delete_data_labeling_job(
        name=shared_state["data_labeling_job_name"]
    )
    print("Delete LRO:", response.operation.name)
    delete_data_labeling_job_response = response.result(timeout=300)
    print("delete_data_labeling_job_response", delete_data_labeling_job_response)

    out, _ = capsys.readouterr()
    assert "delete_data_labeling_job_response" in out


@pytest.fixture()
def teardown_hyperparameter_tuning_job(shared_state, job_client):
    yield

    # Cancel the created hyperparameter tuning job
    job_client.cancel_hyperparameter_tuning_job(
        name=shared_state["hyperparameter_tuning_job_name"]
    )

    # Waiting for hyperparameter tuning job to be in CANCELLED state
    helpers.wait_for_job_state(
        get_job_method=job_client.get_hyperparameter_tuning_job,
        name=shared_state["hyperparameter_tuning_job_name"],
    )

    # Delete the created hyperparameter tuning job
    job_client.delete_hyperparameter_tuning_job(
        name=shared_state["hyperparameter_tuning_job_name"]
    )


@pytest.fixture()
def teardown_training_pipeline(shared_state, pipeline_client):
    yield

    pipeline_client.cancel_training_pipeline(
        name=shared_state["training_pipeline_name"]
    )

    # Waiting for training pipeline to be in CANCELLED state
    helpers.wait_for_job_state(
        get_job_method=pipeline_client.get_training_pipeline,
        name=shared_state["training_pipeline_name"],
    )

    # Delete the training pipeline
    pipeline_client.delete_training_pipeline(
        name=shared_state["training_pipeline_name"]
    )


@pytest.fixture()
def create_dataset(shared_state, dataset_client):
    def create(
        project, location, metadata_schema_uri, test_name="temp_import_dataset_test"
    ):
        parent = f"projects/{project}/locations/{location}"
        dataset = aiplatform.gapic.Dataset(
            display_name=f"{test_name}_{uuid4()}",
            metadata_schema_uri=metadata_schema_uri,
        )

        operation = dataset_client.create_dataset(parent=parent, dataset=dataset)

        dataset = operation.result(timeout=300)
        shared_state["dataset_name"] = dataset.name

    yield create


@pytest.fixture()
def teardown_dataset(shared_state, dataset_client):
    yield

    # Delete the created dataset
    dataset_client.delete_dataset(name=shared_state["dataset_name"])


@pytest.fixture()
def create_endpoint(shared_state, endpoint_client):
    def create(project, location, test_name="temp_deploy_model_test"):
        parent = f"projects/{project}/locations/{location}"
        endpoint = aiplatform.gapic.Endpoint(display_name=f"{test_name}_{uuid4()}",)
        create_endpoint_response = endpoint_client.create_endpoint(
            parent=parent, endpoint=endpoint
        )

        endpoint = create_endpoint_response.result()
        shared_state["endpoint_name"] = endpoint.name

    yield create


@pytest.fixture()
def teardown_endpoint(shared_state, endpoint_client):
    yield

    undeploy_model_operation = endpoint_client.undeploy_model(
        deployed_model_id=shared_state["deployed_model_id"],
        endpoint=shared_state["endpoint_name"],
    )
    undeploy_model_operation.result()

    # Delete the endpoint
    endpoint_client.delete_endpoint(name=shared_state["endpoint_name"])


@pytest.fixture()
def teardown_model(shared_state, model_client):
    yield

    model_client.delete_model(name=shared_state["model_name"])
