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


def test_delete_runtime_revision(
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
                "display_name": "test-agent-engine-delete-runtime-revision",
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
    # Create a second runtime revision,
    # since it's not possible to delete if there is only one runtime revision.
    with (
        mock_agent_engine_create_base64_encoded_tarball,
        mock_agent_engine_create_path_exists,
    ):
        updated_agent_engine = client.agent_engines.update(
            name=agent_engine.api_resource.name,
            config={
                "display_name": "test-agent-engine-update-traffic-with-agent-after-update",
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

    runtime_revisions_iter = client.agent_engines.runtimes.revisions.list(
        name=updated_agent_engine.api_resource.name,
    )
    runtime_revisions_list = list(runtime_revisions_iter)
    assert len(runtime_revisions_list) == 2
    revision_to_delete = runtime_revisions_list[1]
    operation = client.agent_engines.runtimes.revisions.delete(
        name=revision_to_delete.api_resource.name,
    )
    assert isinstance(operation, types.DeleteAgentEngineRuntimeRevisionOperation)
    assert operation.done
    runtime_revisions_iter = client.agent_engines.runtimes.revisions.list(
        name=updated_agent_engine.api_resource.name,
    )
    runtime_revisions_list = list(runtime_revisions_iter)
    assert len(runtime_revisions_list) == 1
    assert (
        runtime_revisions_list[0].api_resource.name
        != revision_to_delete.api_resource.name
    )
    client.agent_engines.delete(name=updated_agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.runtimes.revisions.delete",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_delete_runtime_revision_async(
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
                "display_name": "test-agent-engine-delete-runtime-revision",
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
    # Create a second runtime revision,
    # since it's not possible to delete if there is only one runtime revision.
    with (
        mock_agent_engine_create_base64_encoded_tarball,
        mock_agent_engine_create_path_exists,
    ):
        updated_agent_engine = client.agent_engines.update(
            name=agent_engine.api_resource.name,
            config={
                "display_name": "test-agent-engine-update-traffic-with-agent-after-update",
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

    runtime_revisions_iter = client.aio.agent_engines.runtimes.revisions.list(
        name=updated_agent_engine.api_resource.name,
    )
    runtime_revisions_list = []
    async for revision in runtime_revisions_iter:
        runtime_revisions_list.append(revision)
    assert len(runtime_revisions_list) == 2
    revision_to_delete = runtime_revisions_list[1]
    operation = await client.aio.agent_engines.runtimes.revisions.delete(
        name=revision_to_delete.api_resource.name,
    )
    assert isinstance(operation, types.DeleteAgentEngineRuntimeRevisionOperation)
    await client.aio.agent_engines.delete(
        name=updated_agent_engine.api_resource.name, force=True
    )
