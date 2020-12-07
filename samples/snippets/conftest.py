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

from google.cloud import aiplatform
from google.cloud import storage
import pytest


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
