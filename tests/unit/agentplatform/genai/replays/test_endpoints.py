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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring

from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper
import pytest

pytestmark = pytest_helper.setup(
    file=__file__,
)

pytest_plugins = ("pytest_asyncio",)


GEMMA_3_ENDPOINT = "endpoints/mg-endpoint-7a076560-158a-4726-89f4-64b01874aac9"
DEDICATED_ENDPOINT = "https://mg-endpoint-7a076560-158a-4726-89f4-64b01874aac9.us-central1-410364378237.prediction.vertexai.goog/"
ENDPOINT_TO_BE_DELETED = "endpoints/mg-endpoint-40845fbb-96d3-4bbd-828f-08ea2003aeba"
DEPLOYED_MODEL_ID = "1206978444030640128"
PUBLISHER_MODEL = "publishers/google/models/gemma-3-1b-it"


def test_get_endpoint(client):
    """Test get an endpoint."""
    response = client.endpoints.get(name=ENDPOINT_TO_BE_DELETED)
    assert isinstance(response, types.Endpoint)
    assert response.dedicated_endpoint_dns


def test_predict_gemma3(client):
    # Tests prediction on an endpoint which deploys a Gemma 3 model.
    response = client.endpoints._predict(
        name=GEMMA_3_ENDPOINT,
        instances=[
            {
                "prompt": "Hello world!",
            }
        ],
        config={"http_options": {"base_url": DEDICATED_ENDPOINT, "api_version": "v1"}},
    )
    assert isinstance(response, types.PredictResponse)
    assert response.predictions


def test_predict_public_gemma3(client):
    # Tests prediction on an endpoint which deploys a Gemma 3 model.
    response = client.endpoints.predict(
        name=GEMMA_3_ENDPOINT,
        instances=[
            {
                "prompt": "Hello world!",
            }
        ],
    )
    assert isinstance(response, types.PredictResponse)
    assert response.predictions


def test_undeploy_model(client):
    # Tests undeploy model on an endpoint which deploys a Gemma 3 model.
    response = client.endpoints.undeploy(
        name=ENDPOINT_TO_BE_DELETED,
        deployed_model_id=DEPLOYED_MODEL_ID,
        config=types.UndeployModelConfig(wait_for_completion=True),
    )
    assert response is None


def test_delete_endpoint(client):
    # Tests delete endpoint.
    response = client.endpoints.delete(name=ENDPOINT_TO_BE_DELETED)
    assert response is None


@pytest.mark.parametrize(
    "method",
    ["get", "undeploy", "delete"],
)
def test_publisher_model_rejected(client, method):
    # A publisher model has no Endpoint resource, so only predict accepts one.
    kwargs = {"deployed_model_id": DEPLOYED_MODEL_ID} if method == "undeploy" else {}
    with pytest.raises(ValueError, match="is a publisher model"):
        getattr(client.endpoints, method)(name=PUBLISHER_MODEL, **kwargs)


@pytest.mark.asyncio
async def test_get_endpoint_async(client):
    """Test get an endpoint asynchronously."""
    response = await client.aio.endpoints.get(name=ENDPOINT_TO_BE_DELETED)
    assert isinstance(response, types.Endpoint)
    assert response.dedicated_endpoint_dns


@pytest.mark.asyncio
async def test_predict_public_gemma3_async(client):
    # Tests async prediction on an endpoint which deploys a Gemma 3 model.
    response = await client.aio.endpoints.predict(
        name=GEMMA_3_ENDPOINT,
        instances=[
            {
                "prompt": "Hello world!",
            }
        ],
    )
    assert isinstance(response, types.PredictResponse)
    assert response.predictions


@pytest.mark.asyncio
async def test_predict_does_not_mutate_config_async(client):
    # The dedicated endpoint override must not leak into the caller's config.
    config = types.PredictConfig()
    await client.aio.endpoints.predict(
        name=GEMMA_3_ENDPOINT,
        instances=[
            {
                "prompt": "Hello world!",
            }
        ],
        config=config,
    )
    assert config.http_options is None


@pytest.mark.asyncio
async def test_undeploy_model_async(client):
    # Tests async undeploy model on an endpoint which deploys a Gemma 3 model.
    response = await client.aio.endpoints.undeploy(
        name=ENDPOINT_TO_BE_DELETED,
        deployed_model_id=DEPLOYED_MODEL_ID,
        config=types.UndeployModelConfig(wait_for_completion=True),
    )
    assert response is None


@pytest.mark.asyncio
async def test_delete_endpoint_async(client):
    # Tests async delete endpoint.
    response = await client.aio.endpoints.delete(name=ENDPOINT_TO_BE_DELETED)
    assert response is None
