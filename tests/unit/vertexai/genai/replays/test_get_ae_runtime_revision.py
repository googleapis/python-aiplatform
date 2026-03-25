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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring

import pytest

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types

_TEST_CLASS_METHODS = [
    {"name": "query", "api_mode": ""},
]


def test_get_runtime_revisions(
    client,
    mock_agent_engine_create_base64_encoded_tarball,
    mock_agent_engine_create_path_exists,
):
    client._api_client._http_options.base_url = (
        "https://us-central1-autopush-aiplatform.sandbox.googleapis.com/"
    )
    client._api_client._http_options.api_version = "v1beta1"

    with (
        mock_agent_engine_create_base64_encoded_tarball,
        mock_agent_engine_create_path_exists,
    ):
        agent_engine = client.agent_engines.create(
            config={
                "display_name": "test-agent-engine-get-runtime-revisions",
                "source_packages": [
                    "test_module.py",
                    "requirements.txt",
                ],
                "entrypoint_module": "test_module",
                "entrypoint_object": "test_object",
                "class_methods": _TEST_CLASS_METHODS,
                "http_options": {
                    "base_url": "https://us-central1-autopush-aiplatform.sandbox.googleapis.com",
                    "api_version": "v1beta1",
                },
            },
        )
    assert (
        agent_engine.api_resource.display_name
        == "test-agent-engine-get-runtime-revisions"
    )
    runtime_revisions_iter = client.agent_engines.runtimes.revisions.list(
        name=agent_engine.api_resource.name,
    )
    runtime_revisions_list = list(runtime_revisions_iter)
    assert len(runtime_revisions_list) == 1

    assert isinstance(runtime_revisions_list[0], types.AgentEngineRuntimeRevision)
    runtime_revision_name = runtime_revisions_list[0].api_resource.name
    runtime_revision = client.agent_engines.runtimes.revisions.get(
        name=runtime_revision_name,
    )
    assert isinstance(runtime_revision, types.AgentEngineRuntimeRevision)
    assert runtime_revision.api_resource.name == runtime_revision_name
    # Clean up resources.
    agent_engine.delete(force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.runtimes.revisions.get",
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_async_get_runtime_revisions(
    client,
    mock_agent_engine_create_base64_encoded_tarball,
    mock_agent_engine_create_path_exists,
):
    client._api_client._http_options.base_url = (
        "https://us-central1-autopush-aiplatform.sandbox.googleapis.com/"
    )
    client._api_client._http_options.api_version = "v1beta1"

    with (
        mock_agent_engine_create_base64_encoded_tarball,
        mock_agent_engine_create_path_exists,
    ):
        agent_engine = client.agent_engines.create(
            config={
                "display_name": "test-agent-engine-get-runtime-revisions",
                "source_packages": [
                    "test_module.py",
                    "requirements.txt",
                ],
                "entrypoint_module": "test_module",
                "entrypoint_object": "test_object",
                "class_methods": _TEST_CLASS_METHODS,
                "http_options": {
                    "base_url": "https://us-central1-autopush-aiplatform.sandbox.googleapis.com",
                    "api_version": "v1beta1",
                },
            },
        )
    assert (
        agent_engine.api_resource.display_name
        == "test-agent-engine-get-runtime-revisions"
    )
    runtime_revisions_iter = client.aio.agent_engines.runtimes.revisions.list(
        name=agent_engine.api_resource.name,
    )
    runtime_revisions_list = []
    async for revision in runtime_revisions_iter:
        runtime_revisions_list.append(revision)
    assert len(runtime_revisions_list) == 1
    assert isinstance(runtime_revisions_list[0], types.AgentEngineRuntimeRevision)
    runtime_revision_name = runtime_revisions_list[0].api_resource.name
    runtime_revision = await client.aio.agent_engines.runtimes.revisions.get(
        name=runtime_revision_name,
    )
    assert isinstance(runtime_revision, types.AgentEngineRuntimeRevision)
    assert runtime_revision.api_resource.name == runtime_revision_name
    # Clean up resources.
    await client.aio.agent_engines.delete(
        name=agent_engine.api_resource.name, force=True
    )
