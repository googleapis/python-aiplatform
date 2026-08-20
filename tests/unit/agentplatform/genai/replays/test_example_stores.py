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

# pylint: disable=protected-access,bad-continuation,missing-function-docstring

from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper
import pytest

pytestmark = pytest_helper.setup(
    file=__file__,
)

pytest_plugins = ("pytest_asyncio",)

# Real resources in the recording project (GOOGLE_CLOUD_PROJECT). Hard-coded so
# the recorded request URL is stable across runs. Re-recording against a
# different store changes every fixture, so keep these pinned.
EXAMPLE_STORE = "exampleStores/7241040532904869888"

# Deliberately a non-existent example. removeExamples is a no-op for an unknown
# id, so this records a stable request/response pair without deleting the
# fixture example the search and fetch tests depend on.
EXAMPLE_ID = (
    "exampleTypes/stored_contents_example/examples/" "ffffffffffffffffffffffffffffffff"
)

# Not an Example Store resource name, so the transformer must reject it before
# any HTTP request. No fixture is recorded for this test.
NOT_AN_EXAMPLE_STORE = "projects/p/locations/us-central1/endpoints/123"


def _stored_contents_example(search_key):
    # search_key is required unless search_key_generation_method is set. With
    # neither, upsertExamples reports INVALID_ARGUMENT per example inside an
    # HTTP 200 and stores nothing.
    return {
        "stored_contents_example": {
            "search_key": search_key,
            "contents_example": {
                "contents": [{"role": "user", "parts": [{"text": search_key}]}],
                "expected_contents": [
                    {"content": {"role": "model", "parts": [{"text": "hi"}]}}
                ],
            },
        }
    }


def _assert_upserted(response):
    assert isinstance(response, types.UpsertExamplesResponse)
    # upsertExamples is partial-success: a result carries either an example or
    # an error status, and the whole batch can fail inside a 200. Asserting the
    # response type alone passes on an all-errors response.
    assert response.results
    assert response.results[0].status is None, response.results[0].status
    assert response.results[0].example


def test_get(client):
    response = client.example_stores.get(name=EXAMPLE_STORE)
    assert isinstance(response, types.ExampleStore)
    assert response.name


def test_upsert(client):
    response = client.example_stores.upsert_examples(
        name=EXAMPLE_STORE,
        examples=[_stored_contents_example("hello")],
    )
    _assert_upserted(response)


def test_search(client):
    response = client.example_stores.search_examples(
        name=EXAMPLE_STORE,
        stored_contents_example_parameters={"search_key": "hello"},
        config={"top_k": 1},
    )
    assert isinstance(response, types.SearchExamplesResponse)


def test_fetch(client):
    response = client.example_stores.fetch_examples(
        name=EXAMPLE_STORE,
        config={"page_size": 1},
    )
    assert isinstance(response, types.FetchExamplesResponse)


def test_remove(client):
    response = client.example_stores.remove_examples(
        name=EXAMPLE_STORE,
        config={"example_ids": [EXAMPLE_ID]},
    )
    assert isinstance(response, types.RemoveExamplesResponse)
    # EXAMPLE_ID does not exist, so this must remove nothing. Guards the config
    # binding: while example_ids was dropped before the wire, removeExamples
    # was sent an empty body and cleared the whole store instead.
    assert not response.example_ids


@pytest.mark.parametrize(
    "method", ["get", "upsert_examples", "search_examples", "fetch_examples"]
)
def test_rejects_non_example_store_name(client, method):
    # The replay session is opened lazily on the first HTTP request, so a call
    # that raises in the transformer never touches the wire and needs no fixture.
    kwargs = {"examples": []} if method == "upsert_examples" else {}
    with pytest.raises(ValueError, match="Invalid example store format"):
        getattr(client.example_stores, method)(name=NOT_AN_EXAMPLE_STORE, **kwargs)


@pytest.mark.asyncio
async def test_get_async(client):
    response = await client.aio.example_stores.get(name=EXAMPLE_STORE)
    assert isinstance(response, types.ExampleStore)
    assert response.name


@pytest.mark.asyncio
async def test_fetch_async(client):
    response = await client.aio.example_stores.fetch_examples(
        name=EXAMPLE_STORE,
        config={"page_size": 1},
    )
    assert isinstance(response, types.FetchExamplesResponse)


@pytest.mark.asyncio
async def test_upsert_async(client):
    response = await client.aio.example_stores.upsert_examples(
        name=EXAMPLE_STORE,
        examples=[_stored_contents_example("hello from the async client")],
    )
    _assert_upserted(response)


@pytest.mark.asyncio
async def test_search_async(client):
    response = await client.aio.example_stores.search_examples(
        name=EXAMPLE_STORE,
        stored_contents_example_parameters={"search_key": "hello"},
        config={"top_k": 1},
    )
    assert isinstance(response, types.SearchExamplesResponse)


@pytest.mark.asyncio
async def test_remove_async(client):
    response = await client.aio.example_stores.remove_examples(
        name=EXAMPLE_STORE,
        config={"example_ids": [EXAMPLE_ID]},
    )
    assert isinstance(response, types.RemoveExamplesResponse)
    assert not response.example_ids
