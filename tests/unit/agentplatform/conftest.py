# Copyright 2026 Google LLC
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

import os
import shutil
import tempfile
from typing import Any
from unittest import mock

from google import auth
from google.auth import credentials as auth_credentials
from google.cloud import storage
from google.cloud.aiplatform import base as aiplatform_base
import pytest


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_BUCKET_NAME = "gs://test-bucket"


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as auth_mock:
        auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield auth_mock


@pytest.fixture
def generate_display_name_mock():
    with mock.patch.object(
        aiplatform_base.VertexAiResourceNoun, "_generate_display_name"
    ) as generate_display_name_mock:
        generate_display_name_mock.return_value = "test-display-name"
        yield generate_display_name_mock


@pytest.fixture
def mock_storage_blob():
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

        @classmethod
        def from_uri(cls, destination_file_uri: str, client: Any):
            return cls.from_string(destination_file_uri, client)

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

        @classmethod
        def from_uri(cls, destination_file_uri: str, client: Any):
            return cls.from_string(destination_file_uri, client)

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
        "google.cloud.aiplatform.aiplatform.utils.gcs_utils.upload_to_gcs",
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
