# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from importlib import reload
import pytest
import time
import torch
import os
from typing import Optional

from google.cloud.aiplatform.experimental.vertex_model import base
from google.cloud.aiplatform.experimental.vertex_model import serializers
from google.cloud.aiplatform.experimental.vertex_model import source
from google.cloud.aiplatform import initializer

rom google.protobuf import duration_pb2  # type: ignore
from google.rpc import status_pb2

import test_training_jobs
from test_training_jobs import mock_python_package_to_gcs  # noqa: F401

from google.cloud import aiplatform
from google.cloud.aiplatform.compat.types import custom_job as gca_custom_job_compat
from google.cloud.aiplatform.compat.types import (
    custom_job_v1beta1 as gca_custom_job_v1beta1,
)
from google.cloud.aiplatform.compat.types import io as gca_io_compat
from google.cloud.aiplatform.compat.types import job_state as gca_job_state_compat
from google.cloud.aiplatform.compat.types import (
    encryption_spec as gca_encryption_spec_compat,
)
from google.cloud.aiplatform_v1.services.job_service import client as job_service_client
from google.cloud.aiplatform_v1beta1.services.job_service import (
    client as job_service_client_v1beta1,
)

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_ID = "1028944691210842416"
_TEST_DISPLAY_NAME = "my_job_1234"

_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

_TEST_CUSTOM_JOB_NAME = f"{_TEST_PARENT}/customJobs/{_TEST_ID}"
_TEST_TENSORBOARD_NAME = f"{_TEST_PARENT}/tensorboards/{_TEST_ID}"

_TEST_TRAINING_CONTAINER_IMAGE = "gcr.io/test-training/container:image"

_TEST_WORKER_POOL_SPEC = [
    {
        "machine_spec": {
            "machine_type": "n1-standard-4",
            "accelerator_type": "NVIDIA_TESLA_K80",
            "accelerator_count": 1,
        },
        "replica_count": 1,
        "container_spec": {
            "image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
            "command": [],
            "args": [],
        },
    }
]

_TEST_STAGING_BUCKET = "gs://test-staging-bucket"

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_default"
_TEST_DEFAULT_ENCRYPTION_SPEC = gca_encryption_spec_compat.EncryptionSpec(
    kms_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME
)

_TEST_SERVICE_ACCOUNT = "vinnys@my-project.iam.gserviceaccount.com"

_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_ID}"

_TEST_TIMEOUT = 8000
_TEST_RESTART_JOB_ON_WORKER_RESTART = True

_TEST_BASE_CUSTOM_JOB_PROTO = gca_custom_job_compat.CustomJob(
    display_name=_TEST_DISPLAY_NAME,
    job_spec=gca_custom_job_compat.CustomJobSpec(
        worker_pool_specs=_TEST_WORKER_POOL_SPEC,
        base_output_directory=gca_io_compat.GcsDestination(
            output_uri_prefix=_TEST_STAGING_BUCKET
        ),
        scheduling=gca_custom_job_compat.Scheduling(
            timeout=duration_pb2.Duration(seconds=_TEST_TIMEOUT),
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
        ),
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
    ),
    encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
)


@pytest.fixture
def create_custom_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_custom_job"
    ) as create_custom_job_mock:
        create_custom_job_mock.return_value = _get_custom_job_proto(
            name=_TEST_CUSTOM_JOB_NAME,
            state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
        )
        yield create_custom_job_mock


@pytest.fixture
def get_custom_job_mock():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            ),
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
            ),
        ]
        yield get_custom_job_mock


def _get_custom_job_proto(state=None, name=None, error=None, version="v1"):
    custom_job_proto = copy.deepcopy(_TEST_BASE_CUSTOM_JOB_PROTO)
    custom_job_proto.name = name
    custom_job_proto.state = state
    custom_job_proto.error = error

    if version == "v1beta1":
        v1beta1_custom_job_proto = gca_custom_job_v1beta1.CustomJob()
        v1beta1_custom_job_proto._pb.MergeFromString(
            custom_job_proto._pb.SerializeToString()
        )
        custom_job_proto = v1beta1_custom_job_proto
        custom_job_proto.job_spec.tensorboard = _TEST_TENSORBOARD_NAME

    return custom_job_proto


class LinearRegression(VertexModel): 
 
        # constraint on no constructor arguments
        def __init__(self):
            input_size = 10
            output_size = 10
            super(LinearRegression, self).__init__()
            self.linear = torch.nn.Linear(input_size, output_size)

        def forward(self, x):
            return self.linear(x)

        def train_loop(self, dataloader, loss_fn, optimizer):
            size = len(dataloader.size)
            for batch, (X, y) in enumerate(dataloader):
                pred = self.predict(X)
                loss = loss_fn(pred, y)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        def fit(self, dataset):
            loss_fn = nn.CrossEntropyLoss()
            optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
            for t in range(epochs):
                self.train_loop(data, loss_fn, optimizer)


class TestCloudModelClass:

    def test_create_cloud_class(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        my_model = LinearRegression()
        my_model.training_mode = 'cloud'

        assert(my_model != None)

    def test_fit_cloud_class(self, create_custom_job_mock, get_custom_job_mock):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        my_model = LinearRegression()
        my_model.training_mode = 'cloud'
        my_model.fit(pd.DataFrame())

        with tempfile.TemporaryDirectory() as tmpdirname:
            script_path = pathlib.Path(tmpdirname) / "training_script.py"

        assert(os.path.isfile(script_path))

