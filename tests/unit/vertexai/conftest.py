# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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

import copy
import os
import shutil
import tempfile
from typing import Any
from unittest import mock
import uuid

from google import auth
from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud.logging import Logger
from google.cloud import storage
from google.cloud.aiplatform.compat.services import job_service_client
from google.cloud.aiplatform.compat.types import (
    custom_job as gca_custom_job_compat,
)
from google.cloud.aiplatform.compat.types import io as gca_io_compat
from google.cloud.aiplatform.compat.types import (
    job_state as gca_job_state_compat,
)
from google.cloud.aiplatform_v1beta1.services.persistent_resource_service import (
    PersistentResourceServiceClient,
)
from pyfakefs import fake_filesystem_unittest
import pytest
import tensorflow.saved_model as tf_saved_model
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    PersistentResource,
    ResourcePool,
    ResourceRuntimeSpec,
    ServiceAccountSpec,
)


_TEST_PROJECT = "test-project"
_TEST_PROJECT_NUMBER = "12345678"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_DISPLAY_NAME = f"{_TEST_PARENT}/customJobs/12345"
_TEST_BUCKET_NAME = "gs://test_bucket"
_TEST_BASE_OUTPUT_DIR = f"{_TEST_BUCKET_NAME}/test_base_output_dir"
_TEST_SERVICE_ACCOUNT = f"{_TEST_PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

_TEST_INPUTS = [
    "--arg_0=string_val_0",
    "--arg_1=string_val_1",
    "--arg_2=int_val_0",
    "--arg_3=int_val_1",
]
_TEST_IMAGE_URI = "test_image_uri"
_TEST_MACHINE_TYPE = "test_machine_type"
_TEST_WORKER_POOL_SPEC = [
    {
        "machine_spec": {
            "machine_type": _TEST_MACHINE_TYPE,
        },
        "replica_count": 1,
        "container_spec": {
            "image_uri": _TEST_IMAGE_URI,
            "args": _TEST_INPUTS,
        },
    }
]
_TEST_CUSTOM_JOB_PROTO = gca_custom_job_compat.CustomJob(
    display_name=_TEST_DISPLAY_NAME,
    job_spec={
        "worker_pool_specs": _TEST_WORKER_POOL_SPEC,
        "base_output_directory": gca_io_compat.GcsDestination(
            output_uri_prefix=_TEST_BASE_OUTPUT_DIR
        ),
    },
    labels={"trained_by_vertex_ai": "true"},
)

_TEST_REQUEST_RUNNING_DEFAULT = PersistentResource(
    resource_runtime_spec=ResourceRuntimeSpec(service_account_spec=ServiceAccountSpec())
)
resource_pool = ResourcePool()
resource_pool.machine_spec.machine_type = "n1-standard-4"
resource_pool.replica_count = 1
resource_pool.disk_spec.boot_disk_type = "pd-ssd"
resource_pool.disk_spec.boot_disk_size_gb = 100
_TEST_REQUEST_RUNNING_DEFAULT.resource_pools = [resource_pool]


_TEST_PERSISTENT_RESOURCE_RUNNING = PersistentResource(state="RUNNING")
_TEST_PERSISTENT_RESOURCE_SERVICE_ACCOUNT_RUNNING = PersistentResource(
    state="RUNNING",
    resource_runtime_spec=ResourceRuntimeSpec(
        service_account_spec=ServiceAccountSpec(
            enable_custom_service_account=True, service_account=_TEST_SERVICE_ACCOUNT
        )
    ),
)


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as auth_mock:
        auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            "test-project",
        )
        yield auth_mock


@pytest.fixture
def mock_filesystem():
    with fake_filesystem_unittest.Patcher() as patcher:
        patcher.setUp()
        yield patcher.fs
        patcher.tearDown()


@pytest.fixture
def mock_storage_blob(mock_filesystem):
    """Mocks the storage Blob API.

    Replaces the Blob factory method by a simpler method that records the
    destination_file_uri and, instead of uploading the file to gcs, copying it
    to the fake local file system.
    """

    class MockStorageBlob:
        """Mocks storage.Blob."""

        def __init__(self, destination_file_uri: str, client: Any):
            del client
            self.destination_file_uri = destination_file_uri

        @classmethod
        def from_string(cls, destination_file_uri: str, client: Any):
            if destination_file_uri.startswith("gs://"):
                # Do not copy files to gs:// since it's not a valid path in the fake
                # filesystem.
                destination_file_uri = destination_file_uri.split("/")[-1]
            return cls(destination_file_uri, client)

        def upload_from_filename(self, filename: str):
            shutil.copy(filename, self.destination_file_uri)

        def download_to_filename(self, filename: str):
            """To be replaced by an implementation of testing needs."""
            raise NotImplementedError

    with mock.patch.object(storage, "Blob", new=MockStorageBlob) as storage_blob:
        yield storage_blob


@pytest.fixture
def mock_storage_blob_tmp_dir(tmp_path):
    """Mocks the storage Blob API.

    Replaces the Blob factory method by a simpler method that records the
    destination_file_uri and, instead of uploading the file to gcs, copying it
    to a temporaray path in the local file system.
    """

    class MockStorageBlob:
        """Mocks storage.Blob."""

        def __init__(self, destination_file_uri: str, client: Any):
            del client
            self.destination_file_uri = destination_file_uri

        @classmethod
        def from_string(cls, destination_file_uri: str, client: Any):
            if destination_file_uri.startswith("gs://"):
                # Do not copy files to gs:// since it's not a valid path in the fake
                # filesystem.
                destination_file_uri = os.fspath(
                    tmp_path / destination_file_uri.split("/")[-1]
                )
            return cls(destination_file_uri, client)

        def upload_from_filename(self, filename: str):
            shutil.copy(filename, self.destination_file_uri)

        def download_to_filename(self, filename: str):
            """To be replaced by an implementation of testing needs."""
            raise NotImplementedError

    with mock.patch.object(storage, "Blob", new=MockStorageBlob) as storage_blob:
        yield storage_blob


@pytest.fixture
def mock_gcs_upload():
    def fake_upload_to_gcs(local_filename: str, gcs_destination: str):
        if gcs_destination.startswith("gs://") or gcs_destination.startswith("gcs/"):
            raise ValueError("Please don't use the real gcs path with mock_gcs_upload.")
        # instead of upload, just copy the file.
        shutil.copyfile(local_filename, gcs_destination)

    with mock.patch(
        "google.cloud.aiplatform.utils.gcs_utils.upload_to_gcs",
        new=fake_upload_to_gcs,
    ) as gcs_upload:
        yield gcs_upload


@pytest.fixture
def mock_temp_dir():
    with mock.patch.object(tempfile, "TemporaryDirectory") as temp_dir_mock:
        yield temp_dir_mock


@pytest.fixture
def mock_named_temp_file():
    with mock.patch.object(tempfile, "NamedTemporaryFile") as named_temp_file_mock:
        yield named_temp_file_mock


@pytest.fixture
def mock_create_custom_job():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_custom_job"
    ) as create_custom_job_mock:
        custom_job_proto = copy.deepcopy(_TEST_CUSTOM_JOB_PROTO)
        custom_job_proto.name = _TEST_DISPLAY_NAME
        custom_job_proto.state = gca_job_state_compat.JobState.JOB_STATE_PENDING
        create_custom_job_mock.return_value = custom_job_proto
        yield create_custom_job_mock


@pytest.fixture
def mock_get_custom_job_succeeded():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        custom_job_proto = copy.deepcopy(_TEST_CUSTOM_JOB_PROTO)
        custom_job_proto.name = _TEST_DISPLAY_NAME
        custom_job_proto.state = gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        get_custom_job_mock.return_value = custom_job_proto
        yield get_custom_job_mock


@pytest.fixture
def mock_blob_upload_from_filename():
    with mock.patch.object(storage.Blob, "upload_from_filename") as upload_mock:
        yield upload_mock


@pytest.fixture
def mock_blob_download_to_filename():
    with mock.patch.object(storage.Blob, "download_to_filename") as download_mock:
        yield download_mock


@pytest.fixture
def mock_uuid():
    with mock.patch.object(uuid, "uuid4") as uuid_mock:
        uuid_mock.return_value = 0
        yield uuid_mock


@pytest.fixture
def mock_tf_saved_model_load():
    with mock.patch.object(tf_saved_model, "load") as load_mock:
        yield load_mock


@pytest.fixture
def mock_cloud_logging_list_entries():
    with mock.patch.object(Logger, "list_entries") as list_entries_mock:
        list_entries_mock.return_value = []
        yield list_entries_mock


@pytest.fixture
def persistent_resource_running_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "get_persistent_resource",
    ) as persistent_resource_running_mock:
        persistent_resource_running_mock.return_value = (
            _TEST_PERSISTENT_RESOURCE_RUNNING
        )
        yield persistent_resource_running_mock


@pytest.fixture
def persistent_resource_service_account_running_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "get_persistent_resource",
    ) as persistent_resource_service_account_running_mock:
        persistent_resource_service_account_running_mock.return_value = (
            _TEST_PERSISTENT_RESOURCE_SERVICE_ACCOUNT_RUNNING
        )
        yield persistent_resource_service_account_running_mock


@pytest.fixture
def persistent_resource_exception_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "get_persistent_resource",
    ) as persistent_resource_exception_mock:
        persistent_resource_exception_mock.side_effect = Exception
        yield persistent_resource_exception_mock


@pytest.fixture
def create_persistent_resource_default_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "create_persistent_resource",
    ) as create_persistent_resource_default_mock:
        create_persistent_resource_lro_mock = mock.Mock(ga_operation.Operation)
        create_persistent_resource_lro_mock.result.return_value = (
            _TEST_REQUEST_RUNNING_DEFAULT
        )
        create_persistent_resource_default_mock.return_value = (
            create_persistent_resource_lro_mock
        )
        yield create_persistent_resource_default_mock
