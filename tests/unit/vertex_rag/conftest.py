# Copyright 2024 Google LLC
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
from unittest.mock import patch
from unittest import mock
from google import auth
from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from vertexai import rag
from vertexai.preview import rag as rag_preview
from google.cloud.aiplatform_v1 import (
    DeleteRagCorpusRequest,
    VertexRagDataServiceAsyncClient,
    VertexRagDataServiceClient,
)
from google.cloud.aiplatform_v1beta1 import (
    DeleteRagCorpusRequest as DeleteRagCorpusRequestPreview,
    VertexRagDataServiceAsyncClient as VertexRagDataServiceAsyncClientPreview,
    VertexRagDataServiceClient as VertexRagDataServiceClientPreview,
)
import test_rag_constants_preview
import test_rag_constants
import pytest


# -*- coding: utf-8 -*-

_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as auth_mock:
        auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            test_rag_constants_preview.TEST_PROJECT,
        )
        yield auth_mock


@pytest.fixture
def authorized_session_mock():
    with patch(
        "google.auth.transport.requests.AuthorizedSession"
    ) as MockAuthorizedSession:
        mock_auth_session = MockAuthorizedSession(_TEST_CREDENTIALS)
        yield mock_auth_session


@pytest.fixture
def rag_data_client_mock():
    with mock.patch.object(
        rag.utils._gapic_utils, "create_rag_data_service_client"
    ) as rag_data_client_mock:
        api_client_mock = mock.Mock(spec=VertexRagDataServiceClient)

        # get_rag_corpus
        api_client_mock.get_rag_corpus.return_value = (
            test_rag_constants.TEST_GAPIC_RAG_CORPUS
        )
        # delete_rag_corpus
        delete_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        delete_rag_corpus_lro_mock.result.return_value = DeleteRagCorpusRequest()
        api_client_mock.delete_rag_corpus.return_value = delete_rag_corpus_lro_mock
        # get_rag_file
        api_client_mock.get_rag_file.return_value = (
            test_rag_constants.TEST_GAPIC_RAG_FILE
        )

        rag_data_client_mock.return_value = api_client_mock
        yield rag_data_client_mock


@pytest.fixture
def rag_data_client_preview_mock():
    with mock.patch.object(
        rag_preview.utils._gapic_utils, "create_rag_data_service_client"
    ) as rag_data_client_mock:
        api_client_mock = mock.Mock(spec=VertexRagDataServiceClientPreview)

        # get_rag_corpus
        api_client_mock.get_rag_corpus.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS
        )
        # delete_rag_corpus
        delete_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        delete_rag_corpus_lro_mock.result.return_value = DeleteRagCorpusRequestPreview()
        api_client_mock.delete_rag_corpus.return_value = delete_rag_corpus_lro_mock
        # get_rag_file
        api_client_mock.get_rag_file.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_FILE
        )

        rag_data_client_mock.return_value = api_client_mock
        yield rag_data_client_mock


@pytest.fixture
def rag_data_client_mock_exception():
    with mock.patch.object(
        rag.utils._gapic_utils, "create_rag_data_service_client"
    ) as rag_data_client_mock_exception:
        api_client_mock = mock.Mock(spec=VertexRagDataServiceClient)
        # create_rag_corpus
        api_client_mock.create_rag_corpus.side_effect = Exception
        # update_rag_corpus
        api_client_mock.update_rag_corpus.side_effect = Exception
        # get_rag_corpus
        api_client_mock.get_rag_corpus.side_effect = Exception
        # list_rag_corpora
        api_client_mock.list_rag_corpora.side_effect = Exception
        # delete_rag_corpus
        api_client_mock.delete_rag_corpus.side_effect = Exception
        # upload_rag_file
        api_client_mock.upload_rag_file.side_effect = Exception
        # import_rag_files
        api_client_mock.import_rag_files.side_effect = Exception
        # get_rag_file
        api_client_mock.get_rag_file.side_effect = Exception
        # list_rag_files
        api_client_mock.list_rag_files.side_effect = Exception
        # delete_rag_file
        api_client_mock.delete_rag_file.side_effect = Exception
        rag_data_client_mock_exception.return_value = api_client_mock
        yield rag_data_client_mock_exception


@pytest.fixture
def rag_data_client_preview_mock_exception():
    with mock.patch.object(
        rag_preview.utils._gapic_utils, "create_rag_data_service_client"
    ) as rag_data_client_mock_exception:
        api_client_mock = mock.Mock(spec=VertexRagDataServiceClientPreview)
        # create_rag_corpus
        api_client_mock.create_rag_corpus.side_effect = Exception
        # update_rag_corpus
        api_client_mock.update_rag_corpus.side_effect = Exception
        # get_rag_corpus
        api_client_mock.get_rag_corpus.side_effect = Exception
        # list_rag_corpora
        api_client_mock.list_rag_corpora.side_effect = Exception
        # delete_rag_corpus
        api_client_mock.delete_rag_corpus.side_effect = Exception
        # upload_rag_file
        api_client_mock.upload_rag_file.side_effect = Exception
        # import_rag_files
        api_client_mock.import_rag_files.side_effect = Exception
        # get_rag_file
        api_client_mock.get_rag_file.side_effect = Exception
        # list_rag_files
        api_client_mock.list_rag_files.side_effect = Exception
        # delete_rag_file
        api_client_mock.delete_rag_file.side_effect = Exception
        # update_rag_engine_config
        api_client_mock.update_rag_engine_config.side_effect = Exception
        # get_rag_engine_config
        api_client_mock.get_rag_engine_config.side_effect = Exception
        rag_data_client_mock_exception.return_value = api_client_mock
        yield rag_data_client_mock_exception


@pytest.fixture
def rag_data_async_client_mock_exception():
    with mock.patch.object(
        rag.utils._gapic_utils, "create_rag_data_service_async_client"
    ) as rag_data_async_client_mock_exception:
        api_client_mock = mock.Mock(spec=VertexRagDataServiceAsyncClient)
        # import_rag_files
        api_client_mock.import_rag_files.side_effect = Exception
        rag_data_client_mock_exception.return_value = api_client_mock
        yield rag_data_async_client_mock_exception


@pytest.fixture
def rag_data_async_client_preview_mock_exception():
    with mock.patch.object(
        rag_preview.utils._gapic_utils, "create_rag_data_service_async_client"
    ) as rag_data_async_client_mock_exception:
        api_client_mock = mock.Mock(spec=VertexRagDataServiceAsyncClientPreview)
        # import_rag_files
        api_client_mock.import_rag_files.side_effect = Exception
        rag_data_client_mock_exception.return_value = api_client_mock
        yield rag_data_async_client_mock_exception
