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


from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types

_TEST_CLASS_METHODS = [
    {"name": "query", "api_mode": ""},
]


def test_agent_engines_update_traffic_to_always_latest(client):

    client._api_client._http_options.base_url = (
        "https://us-central1-autopush-aiplatform.sandbox.googleapis.com/"
    )
    client._api_client._http_options.api_version = "v1beta1"

    agent_engine = client.agent_engines.create()

    traffic_config = types.ReasoningEngineTrafficConfig(
        traffic_split_always_latest=types.ReasoningEngineTrafficConfigTrafficSplitAlwaysLatest(),
    )

    updated_agent_engine = client.agent_engines.update(
        name=agent_engine.api_resource.name,
        config=types.AgentEngineConfig(
            traffic_config=traffic_config,
        ),
    )

    assert updated_agent_engine.api_resource.traffic_config == traffic_config

    agent_engine.delete(force=True)


def test_agent_engines_update_traffic_to_manual_split(
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
                "display_name": "test-agent-engine-update-traffic-to-manual-split",
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
        name=agent_engine.api_resource.name,
    )
    runtime_revisions_list = list(runtime_revisions_iter)
    assert len(runtime_revisions_list) == 1
    assert isinstance(
        runtime_revisions_list[0].api_resource, types.ReasoningEngineRuntimeRevision
    )
    runtime_revision_name = runtime_revisions_list[0].api_resource.name

    traffic_config = types.ReasoningEngineTrafficConfig(
        traffic_split_manual=types.ReasoningEngineTrafficConfigTrafficSplitManual(
            targets=[
                types.ReasoningEngineTrafficConfigTrafficSplitManualTarget(
                    runtime_revision_name=runtime_revision_name,
                    percent=100,
                ),
            ],
        ),
    )

    updated_agent_engine = client.agent_engines.update(
        name=agent_engine.api_resource.name,
        config=types.AgentEngineConfig(
            traffic_config=traffic_config,
        ),
    )

    assert updated_agent_engine.api_resource.traffic_config == traffic_config
    agent_engine.delete(force=True)


def test_agent_engines_update_traffic_with_agent_update(
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
                "display_name": "test-agent-engine-update-traffic-with-agent-before-update",
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
        == "test-agent-engine-update-traffic-with-agent-before-update"
    )
    assert agent_engine.api_resource.traffic_config is None
    runtime_revisions_iter = client.agent_engines.runtimes.revisions.list(
        name=agent_engine.api_resource.name,
    )
    runtime_revisions_list = list(runtime_revisions_iter)
    assert len(runtime_revisions_list) == 1
    assert isinstance(
        runtime_revisions_list[0].api_resource, types.ReasoningEngineRuntimeRevision
    )
    runtime_revision_name = runtime_revisions_list[0].api_resource.name

    traffic_config = types.ReasoningEngineTrafficConfig(
        traffic_split_manual=types.ReasoningEngineTrafficConfigTrafficSplitManual(
            targets=[
                types.ReasoningEngineTrafficConfigTrafficSplitManualTarget(
                    runtime_revision_name=runtime_revision_name,
                    percent=100,
                ),
            ],
        ),
    )

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
                "traffic_config": traffic_config,
            },
        )

    assert (
        updated_agent_engine.api_resource.display_name
        == "test-agent-engine-update-traffic-with-agent-after-update"
    )
    assert updated_agent_engine.api_resource.traffic_config == traffic_config
    runtime_revisions_iter = client.agent_engines.runtimes.revisions.list(
        name=agent_engine.api_resource.name,
    )
    runtime_revisions_list = list(runtime_revisions_iter)
    assert len(runtime_revisions_list) == 2
    assert isinstance(
        runtime_revisions_list[0].api_resource, types.ReasoningEngineRuntimeRevision
    )
    assert isinstance(
        runtime_revisions_list[1].api_resource, types.ReasoningEngineRuntimeRevision
    )
    assert (
        runtime_revisions_list[0].api_resource.name != runtime_revision_name
    )  # new revision
    assert runtime_revisions_list[1].api_resource.name == runtime_revision_name

    agent_engine.delete(force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.update",
)
