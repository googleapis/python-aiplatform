# Copyright 2025 Google LLC
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

# pylint: disable=protected-access,bad-continuation

import contextlib
import importlib
import pytest
import sys
import warnings
from unittest import mock

from google.cloud import aiplatform
import agentplatform
from agentplatform._genai import client as agentplatform_client
from google.cloud.aiplatform import initializer as aiplatform_initializer
import vertexai
from vertexai._genai import client as vertexai_client


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

_AGENTPLATFORM_GCS_UTILS = "agentplatform._genai._gcs_utils"
_AGENTPLATFORM_RAG = "agentplatform._genai.rag"
_VERTEXAI_GCS_UTILS = "vertexai._genai._gcs_utils"


pytestmark = pytest.mark.usefixtures("google_auth_mock")


class TestGenAiClient:
    """Unit tests for the GenAI client."""

    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(agentplatform)
        agentplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    @pytest.mark.usefixtures("google_auth_mock")
    def test_genai_client(self):
        test_client = agentplatform.Client(
            project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        assert test_client is not None
        assert test_client._api_client.vertexai
        assert test_client._api_client.project == _TEST_PROJECT
        assert test_client._api_client.location == _TEST_LOCATION

    @pytest.mark.parametrize("location", ["us", "eu"])
    @pytest.mark.usefixtures("google_auth_mock")
    def test_genai_client_mrep(self, location):
        test_client = agentplatform.Client(project=_TEST_PROJECT, location=location)
        expected_url = f"https://aiplatform.{location}.rep.googleapis.com/"
        assert test_client._api_client._http_options.base_url == expected_url

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("google_auth_mock")
    async def test_async_client(self):
        test_client = agentplatform.Client(
            project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        assert isinstance(test_client.aio, agentplatform._genai.client.AsyncClient)

    @pytest.mark.usefixtures("google_auth_mock")
    def test_live_client(self):
        test_client = agentplatform.Client(
            project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        test_async_client = test_client.aio
        assert isinstance(test_async_client.live, agentplatform._genai.live.AsyncLive)

    @pytest.mark.usefixtures("google_auth_mock")
    def test_types(self):
        assert agentplatform.types is not None
        assert agentplatform.types.LLMMetric is not None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("google_auth_mock")
    async def test_async_content_manager(self):
        with mock.patch.object(
            agentplatform_client.AsyncClient, "aclose", autospec=True
        ) as mock_aclose:
            async with agentplatform.Client(
                project=_TEST_PROJECT, location=_TEST_LOCATION
            ).aio as async_client:
                assert isinstance(async_client, agentplatform_client.AsyncClient)

            mock_aclose.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("google_auth_mock")
    async def test_call_aclose_async_client(self):
        with mock.patch.object(
            agentplatform_client.AsyncClient, "aclose", autospec=True
        ) as mock_aclose:
            async_client = agentplatform.Client(
                project=_TEST_PROJECT, location=_TEST_LOCATION
            ).aio
            await async_client.aclose()
            mock_aclose.assert_called()

    @pytest.mark.usefixtures("google_auth_mock")
    def test_vertexai_client_deprecation_warning(self):

        with mock.patch.object(vertexai_client, "_CLIENT_WARNING_SHOWN", False):
            # Assert that the warning is triggered on the first instantiation
            with pytest.warns(FutureWarning, match="The vertexai.Client class is deprecated"):
                _ = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
            # Assert that the warning is NOT triggered on subsequent instantiations
            with warnings.catch_warnings():
                warnings.simplefilter("error", FutureWarning)
                _ = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
                _ = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)


@contextlib.contextmanager
def _pandas_unavailable(reimported_modules=()):
    """Makes `import pandas` fail, as it does when the extra is not installed.

    Modules named in `reimported_modules` are evicted from the module cache and
    from their parent package, so that their top-level code runs again while
    pandas is unavailable. Evicting the parent package attribute matters because
    `from . import <submodule>` reads it in preference to re-importing.
    """
    evicted = []
    for name in reimported_modules:
        parent_name, _, attribute = name.rpartition(".")
        importlib.import_module(name)
        parent = sys.modules[parent_name]
        evicted.append((parent, attribute, getattr(parent, attribute)))
    try:
        with mock.patch.dict(sys.modules):
            for name in list(sys.modules):
                if name == "pandas" or name.startswith("pandas."):
                    del sys.modules[name]
            # A None entry makes the import machinery raise ModuleNotFoundError.
            sys.modules["pandas"] = None
            for name in reimported_modules:
                del sys.modules[name]
            for parent, attribute, _ in evicted:
                delattr(parent, attribute)
            yield
    finally:
        for parent, attribute, original in evicted:
            setattr(parent, attribute, original)


class TestPandasIsOptional:
    """pandas is only a dependency of the [evaluation] extra."""

    @pytest.mark.parametrize(
        "module_name", [_AGENTPLATFORM_GCS_UTILS, _VERTEXAI_GCS_UTILS]
    )
    def test_gcs_utils_imports_without_pandas(self, module_name):
        with _pandas_unavailable([module_name]):
            importlib.import_module(module_name)

    @pytest.mark.usefixtures("google_auth_mock")
    def test_rag_does_not_require_pandas(self):
        test_client = agentplatform.Client(
            project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        with _pandas_unavailable([_AGENTPLATFORM_RAG, _AGENTPLATFORM_GCS_UTILS]):
            assert test_client.rag is not None

    def test_read_gcs_file_to_dataframe_without_pandas_names_the_extra(self):
        gcs_utils_module = importlib.import_module(_AGENTPLATFORM_GCS_UTILS)
        with mock.patch.object(gcs_utils_module.storage, "Client", autospec=True):
            gcs_utils = gcs_utils_module.GcsUtils(mock.MagicMock())

        with _pandas_unavailable():
            with pytest.raises(ImportError, match=r"\[evaluation\]"):
                gcs_utils.read_gcs_file_to_dataframe("gs://bucket/data.csv", "csv")
