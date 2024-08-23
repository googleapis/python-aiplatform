# -*- coding: utf-8 -*-

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


from contextlib import redirect_stdout
import datetime
import io
import json
import mock
import pytest
from vertexai.preview import caching
from google.cloud.aiplatform import initializer
import vertexai
from google.cloud.aiplatform_v1beta1.types.cached_content import (
    CachedContent as GapicCachedContent,
)
from google.cloud.aiplatform_v1beta1.types.content import (
    Content as GapicContent,
    Part as GapicPart,
)
from google.cloud.aiplatform_v1beta1.types.tool import (
    ToolConfig as GapicToolConfig,
)
from google.cloud.aiplatform_v1beta1.services import (
    gen_ai_cache_service,
)


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_CREATED_CONTENT_ID = "contents-id-mocked"
_TEST_DISPLAY_NAME = "test-display-name"


@pytest.fixture
def mock_create_cached_content():
    """Mocks GenAiCacheServiceClient.create_cached_content()."""

    def create_cached_content(self, request):
        response = GapicCachedContent(
            name=f"{request.parent}/cachedContents/{_CREATED_CONTENT_ID}",
            model=f"{request.cached_content.model}",
            display_name=f"{request.cached_content.display_name}",
            create_time=datetime.datetime(
                year=2024,
                month=2,
                day=1,
                hour=1,
                minute=1,
                second=1,
                tzinfo=datetime.timezone.utc,
            ),
            update_time=datetime.datetime(
                year=2024,
                month=2,
                day=1,
                hour=1,
                minute=1,
                second=1,
                tzinfo=datetime.timezone.utc,
            ),
            expire_time=datetime.datetime(
                year=2024,
                month=2,
                day=1,
                hour=2,
                minute=1,
                second=1,
                tzinfo=datetime.timezone.utc,
            ),
        )
        return response

    with mock.patch.object(
        gen_ai_cache_service.client.GenAiCacheServiceClient,
        "create_cached_content",
        new=create_cached_content,
    ) as create_cached_content:
        yield create_cached_content


@pytest.fixture
def mock_get_cached_content():
    """Mocks GenAiCacheServiceClient.get_cached_content()."""

    def get_cached_content(self, name, retry=None):
        del self, retry
        response = GapicCachedContent(
            name=f"{name}",
            model="model-name",
        )
        return response

    with mock.patch.object(
        gen_ai_cache_service.client.GenAiCacheServiceClient,
        "get_cached_content",
        new=get_cached_content,
    ) as get_cached_content:
        yield get_cached_content


@pytest.fixture
def mock_list_cached_contents():
    """Mocks GenAiCacheServiceClient.get_cached_content()."""

    def list_cached_contents(self, request):
        del self, request
        response = [
            GapicCachedContent(
                name="cached_content1_from_list_request",
                model="model-name1",
            ),
            GapicCachedContent(
                name="cached_content2_from_list_request",
                model="model-name2",
            ),
        ]
        return response

    with mock.patch.object(
        gen_ai_cache_service.client.GenAiCacheServiceClient,
        "list_cached_contents",
        new=list_cached_contents,
    ) as list_cached_contents:
        yield list_cached_contents


@pytest.mark.usefixtures("google_auth_mock")
class TestCaching:
    """Unit tests for caching.CachedContent."""

    def setup_method(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_constructor_with_full_resource_name(self, mock_get_cached_content):
        full_resource_name = (
            "projects/123/locations/europe-west1/cachedContents/contents-id"
        )
        cache = caching.CachedContent(
            cached_content_name=full_resource_name,
        )

        assert cache.name == "contents-id"
        assert cache.resource_name == full_resource_name

    def test_constructor_with_only_content_id(self, mock_get_cached_content):
        partial_resource_name = "contents-id"

        cache = caching.CachedContent(
            cached_content_name=partial_resource_name,
        )

        assert cache.name == "contents-id"
        assert cache.resource_name == (
            f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/cachedContents/contents-id"
        )
        assert cache.model_name == "model-name"

    def test_get_with_content_id(self, mock_get_cached_content):
        partial_resource_name = "contents-id"

        cache = caching.CachedContent.get(
            cached_content_name=partial_resource_name,
        )

        assert cache.name == "contents-id"
        assert cache.resource_name == (
            f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/cachedContents/contents-id"
        )
        assert cache.model_name == "model-name"

    def test_create_with_real_payload(
        self, mock_create_cached_content, mock_get_cached_content
    ):
        cache = caching.CachedContent.create(
            model_name="model-name",
            system_instruction=GapicContent(
                role="system", parts=[GapicPart(text="system instruction")]
            ),
            tools=[],
            tool_config=GapicToolConfig(),
            contents=[GapicContent(role="user")],
            ttl=datetime.timedelta(days=1),
            display_name=_TEST_DISPLAY_NAME,
        )

        # parent is automantically set to align with the current project and location.
        # _CREATED_CONTENT_ID is from the mock
        assert cache.resource_name == (
            f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/cachedContents/{_CREATED_CONTENT_ID}"
        )
        assert cache.name == _CREATED_CONTENT_ID
        assert (
            cache.model_name
            == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/publishers/google/models/model-name"
        )
        assert cache.display_name == _TEST_DISPLAY_NAME

    def test_create_with_real_payload_and_wrapped_type(
        self, mock_create_cached_content, mock_get_cached_content
    ):
        cache = caching.CachedContent.create(
            model_name="model-name",
            system_instruction="Please answer my questions with cool",
            tools=[],
            tool_config=GapicToolConfig(),
            contents=["user content"],
            ttl=datetime.timedelta(days=1),
            display_name=_TEST_DISPLAY_NAME,
        )

        # parent is automantically set to align with the current project and location.
        # _CREATED_CONTENT_ID is from the mock
        assert (
            cache.model_name
            == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/publishers/google/models/model-name"
        )
        assert cache.name == _CREATED_CONTENT_ID
        assert cache.display_name == _TEST_DISPLAY_NAME

    def test_list(self, mock_list_cached_contents):
        cached_contents = caching.CachedContent.list()
        for i, cached_content in enumerate(cached_contents):
            assert cached_content.name == f"cached_content{i + 1}_from_list_request"
            assert cached_content.model_name == f"model-name{i + 1}"

    def test_print_a_cached_content(
        self, mock_create_cached_content, mock_get_cached_content
    ):
        cached_content = caching.CachedContent.create(
            model_name="model-name",
            system_instruction="Please answer my questions with cool",
            tools=[],
            tool_config=GapicToolConfig(),
            contents=["user content"],
            ttl=datetime.timedelta(days=1),
            display_name=_TEST_DISPLAY_NAME,
        )
        f = io.StringIO()
        with redirect_stdout(f):
            print(cached_content)
        output = f.getvalue()
        assert (
            json.dumps(
                {
                    "name": f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/cachedContents/{_CREATED_CONTENT_ID}",
                    "model": "projects/test-project/locations/us-central1/publishers/google/models/model-name",
                    "createTime": "2024-02-01T01:01:01Z",
                    "updateTime": "2024-02-01T01:01:01Z",
                    "expireTime": "2024-02-01T02:01:01Z",
                    "displayName": "test-display-name",
                },
                indent=2,
            )
            in output
        )
