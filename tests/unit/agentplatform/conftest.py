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
from google.api_core import operation as ga_operation
from google.cloud.aiplatform import base as aiplatform_base
from google.cloud.aiplatform.compat.services import (
    feature_online_store_admin_service_client,
)
from google.cloud.aiplatform.compat.services import (
    feature_registry_service_client,
)
from google.cloud.aiplatform_v1beta1.services.feature_registry_service import (
    FeatureRegistryServiceClient,
)
from .feature_store_constants import (
    _TEST_BIGTABLE_FOS1,
    _TEST_EMBEDDING_FV1,
    _TEST_ESF_OPTIMIZED_FOS,
    _TEST_ESF_OPTIMIZED_FOS2,
    _TEST_FG1,
    _TEST_FG1_F1,
    _TEST_FG1_F2,
    _TEST_FG1_FM1,
    _TEST_FV_LIST,
    _TEST_FV1,
    _TEST_FV3,
    _TEST_FV4,
    _TEST_OPTIMIZED_EMBEDDING_FV,
    _TEST_OPTIMIZED_FV1,
    _TEST_OPTIMIZED_FV2,
    _TEST_PSC_OPTIMIZED_FOS,
)
import pytest
from unittest.mock import patch


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_BUCKET_NAME = "gs://test-bucket"


@pytest.fixture
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


@pytest.fixture
def get_fos_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_online_store",
    ) as get_fos_mock:
        get_fos_mock.return_value = _TEST_BIGTABLE_FOS1
        yield get_fos_mock


@pytest.fixture
def get_esf_optimized_fos_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_online_store",
    ) as get_fos_mock:
        get_fos_mock.return_value = _TEST_ESF_OPTIMIZED_FOS
        yield get_fos_mock


@pytest.fixture
def get_psc_optimized_fos_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_online_store",
    ) as get_fos_mock:
        get_fos_mock.return_value = _TEST_PSC_OPTIMIZED_FOS
        yield get_fos_mock


@pytest.fixture
def get_esf_optimized_fos_no_endpoint_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_online_store",
    ) as get_fos_mock:
        get_fos_mock.return_value = _TEST_ESF_OPTIMIZED_FOS2
        yield get_fos_mock


@pytest.fixture
def create_bigtable_fos_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "create_feature_online_store",
    ) as create_bigtable_fos_mock:
        create_fos_lro_mock = mock.Mock(ga_operation.Operation)
        create_fos_lro_mock.result.return_value = _TEST_BIGTABLE_FOS1
        create_bigtable_fos_mock.return_value = create_fos_lro_mock
        yield create_bigtable_fos_mock


@pytest.fixture
def create_esf_optimized_fos_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "create_feature_online_store",
    ) as create_esf_optimized_fos_mock:
        create_fos_lro_mock = mock.Mock(ga_operation.Operation)
        create_fos_lro_mock.result.return_value = _TEST_ESF_OPTIMIZED_FOS
        create_esf_optimized_fos_mock.return_value = create_fos_lro_mock
        yield create_esf_optimized_fos_mock


@pytest.fixture
def create_psc_optimized_fos_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "create_feature_online_store",
    ) as create_psc_optimized_fos_mock:
        create_fos_lro_mock = mock.Mock(ga_operation.Operation)
        create_fos_lro_mock.result.return_value = _TEST_PSC_OPTIMIZED_FOS
        create_psc_optimized_fos_mock.return_value = create_fos_lro_mock
        yield create_psc_optimized_fos_mock


@pytest.fixture
def get_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_view",
    ) as get_fv_mock:
        get_fv_mock.return_value = _TEST_FV1
        yield get_fv_mock


@pytest.fixture
def get_rag_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_view",
    ) as get_rag_fv_mock:
        get_rag_fv_mock.return_value = _TEST_FV3
        yield get_rag_fv_mock


@pytest.fixture
def get_registry_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_view",
    ) as get_rag_fv_mock:
        get_rag_fv_mock.return_value = _TEST_FV4
        yield get_rag_fv_mock


@pytest.fixture
def list_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "list_feature_views",
    ) as list_fv:
        list_fv.return_value = _TEST_FV_LIST
        yield list_fv


@pytest.fixture
def create_bq_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "create_feature_view",
    ) as create_bq_fv_mock:
        create_bq_fv_lro_mock = mock.Mock(ga_operation.Operation)
        create_bq_fv_lro_mock.result.return_value = _TEST_FV1
        create_bq_fv_mock.return_value = create_bq_fv_lro_mock
        yield create_bq_fv_mock


@pytest.fixture
def create_rag_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "create_feature_view",
    ) as create_rag_fv_mock:
        create_rag_fv_lro_mock = mock.Mock(ga_operation.Operation)
        create_rag_fv_lro_mock.result.return_value = _TEST_FV3
        create_rag_fv_mock.return_value = create_rag_fv_lro_mock
        yield create_rag_fv_mock


@pytest.fixture
def create_registry_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "create_feature_view",
    ) as create_registry_fv_mock:
        create_registry_fv_lro_mock = mock.Mock(ga_operation.Operation)
        create_registry_fv_lro_mock.result.return_value = _TEST_FV4
        create_registry_fv_mock.return_value = create_registry_fv_lro_mock
        yield create_registry_fv_mock


@pytest.fixture
def create_embedding_fv_from_bq_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "create_feature_view",
    ) as create_embedding_fv_mock:
        create_embedding_fv_mock_lro = mock.Mock(ga_operation.Operation)
        create_embedding_fv_mock_lro.result.return_value = _TEST_OPTIMIZED_EMBEDDING_FV
        create_embedding_fv_mock.return_value = create_embedding_fv_mock_lro
        yield create_embedding_fv_mock


@pytest.fixture
def get_optimized_embedding_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_view",
    ) as get_fv_mock:
        get_fv_mock.return_value = _TEST_OPTIMIZED_EMBEDDING_FV
        yield get_fv_mock


@pytest.fixture
def get_optimized_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_view",
    ) as get_optimized_fv_mock:
        get_optimized_fv_mock.return_value = _TEST_OPTIMIZED_FV1
        yield get_optimized_fv_mock


@pytest.fixture
def get_embedding_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_view",
    ) as get_embedding_fv_mock:
        get_embedding_fv_mock.return_value = _TEST_EMBEDDING_FV1
        yield get_embedding_fv_mock


@pytest.fixture
def get_optimized_fv_no_endpointmock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_view",
    ) as get_optimized_fv_no_endpointmock:
        get_optimized_fv_no_endpointmock.return_value = _TEST_OPTIMIZED_FV2
        yield get_optimized_fv_no_endpointmock


@pytest.fixture
def get_fg_mock():
    with patch.object(
        feature_registry_service_client.FeatureRegistryServiceClient,
        "get_feature_group",
    ) as get_fg_mock:
        get_fg_mock.return_value = _TEST_FG1
        yield get_fg_mock


@pytest.fixture
def get_feature_mock():
    with patch.object(
        feature_registry_service_client.FeatureRegistryServiceClient,
        "get_feature",
    ) as get_fg_mock:
        get_fg_mock.return_value = _TEST_FG1_F1
        yield get_fg_mock


@pytest.fixture
def get_feature_with_version_column_mock():
    with patch.object(
        feature_registry_service_client.FeatureRegistryServiceClient,
        "get_feature",
    ) as get_fg_mock:
        get_fg_mock.return_value = _TEST_FG1_F2
        yield get_fg_mock


@pytest.fixture
def get_feature_monitor_mock():
    with patch.object(
        FeatureRegistryServiceClient,
        "get_feature_monitor",
    ) as get_fg_mock:
        get_fg_mock.return_value = _TEST_FG1_FM1
        yield get_fg_mock


@pytest.fixture
def base_logger_mock():
    with patch.object(
        aiplatform_base._LOGGER,
        "info",
        wraps=aiplatform_base._LOGGER.info,
    ) as logger_mock:
        yield logger_mock
