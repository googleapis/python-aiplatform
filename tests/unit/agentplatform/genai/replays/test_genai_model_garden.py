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


def test_list_deployable_models(client):
    """Tests listing deployable models in Model Garden."""
    models = client.model_garden.list_deployable_models(
        config=types.ListDeployableModelsConfig(
            include_hugging_face_models=False,
            model_filter="timesfm",
        )
    )
    assert len(models) > 0
    # Returns formatted strings like 'google/timesfm@timesfm-2.0'
    assert isinstance(models[0], str)
    assert "timesfm" in models[0].lower()


def test_list_models(client):
    """Tests listing all baseline models in Model Garden."""
    models = client.model_garden.list_models(
        config=types.ListModelGardenModelsConfig(
            include_hugging_face_models=False,
            model_filter="timesfm",
        )
    )
    assert len(models) > 0
    assert isinstance(models[0], str)
    assert "timesfm" in models[0].lower()


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_list_deployable_models_async(client):
    """Tests listing deployable models asynchronously."""
    models = await client.aio.model_garden.list_deployable_models(
        config=types.ListDeployableModelsConfig(
            include_hugging_face_models=False,
            model_filter="timesfm",
        )
    )
    assert len(models) > 0
    assert isinstance(models[0], str)
    assert "timesfm" in models[0].lower()


@pytest.mark.asyncio
async def test_list_models_async(client):
    """Tests listing all baseline models asynchronously."""
    models = await client.aio.model_garden.list_models(
        config=types.ListModelGardenModelsConfig(
            include_hugging_face_models=False,
            model_filter="timesfm",
        )
    )
    assert len(models) > 0
    assert isinstance(models[0], str)
    assert "timesfm" in models[0].lower()
