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

import sys

from tests.unit.vertexai.genai.replays import pytest_helper

_TEST_CLASS_METHODS = [
    {"name": "async_stream_query", "api_mode": "async_stream"},
    {"name": "streaming_agent_run_with_events", "api_mode": "async_stream"},
]


def test_create_with_docker(
    client,
    mock_agent_engine_create_docker_base64_encoded_tarball,
    mock_agent_engine_create_path_exists,
):
    """Tests creating an agent engine with docker spec."""
    if sys.version_info >= (3, 13):
        try:
            client._api_client._initialize_replay_session_if_not_loaded()
            if client._api_client.replay_session:
                target_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
                for interaction in client._api_client.replay_session.interactions:

                    def _update_ver(obj):
                        if isinstance(obj, dict):
                            if "python_spec" in obj and isinstance(
                                obj["python_spec"], dict
                            ):
                                if "version" in obj["python_spec"]:
                                    obj["python_spec"]["version"] = target_ver
                            for v in obj.values():
                                _update_ver(v)
                        elif isinstance(obj, list):
                            for item in obj:
                                _update_ver(item)

                    if hasattr(interaction.request, "body_segments"):
                        _update_ver(interaction.request.body_segments)
                    if hasattr(interaction.request, "body"):
                        _update_ver(interaction.request.body)
        except Exception:
            pass
    with (
        mock_agent_engine_create_docker_base64_encoded_tarball,
        mock_agent_engine_create_path_exists,
    ):
        agent_engine = client.agent_engines.create(
            config={
                "display_name": "test-agent-engine-docker",
                "description": "test agent engine with docker spec",
                "source_packages": ["."],
                "agent_framework": "custom",
                "image_spec": {"build_args": {}},
                "class_methods": _TEST_CLASS_METHODS,
                "http_options": {
                    "base_url": "https://europe-west3-aiplatform.googleapis.com",
                    "api_version": "v1beta1",
                },
            },
        )
    assert agent_engine.api_resource.display_name == "test-agent-engine-docker"
    # Clean up resources.
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.create",
)
