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


"""Conftest for Vertex SDK GenAI tests."""

import os
from unittest import mock

from vertexai._genai import (
    client as vertexai_genai_client_module,
)
from google.cloud import storage, bigquery
from google.genai import _replay_api_client
from google.genai import client as google_genai_client_module
from vertexai._genai import _evals_utils
from vertexai._genai import prompt_optimizer
import pytest


from typing import Any, Optional, Union
import pydantic


def pop_undeterministic_headers(headers: dict[str, str]) -> None:
    """Remove headers that are not deterministic."""
    headers.pop("Date", None)  # pytype: disable=attribute-error
    headers.pop("Server-Timing", None)  # pytype: disable=attribute-error


class PatchedReplayResponse(pydantic.BaseModel):
    """Represents a single response in a replay."""

    status_code: int = 200
    headers: dict[str, str]
    body_segments: list[Union[list[dict[str, object]], dict[str, object]]]
    byte_segments: Optional[list[bytes]] = None
    sdk_response_segments: list[dict[str, object]]

    def model_post_init(self, __context: Any) -> None:
        pop_undeterministic_headers(self.headers)


class PatchedReplayInteraction(pydantic.BaseModel):
    """Represents a single interaction, request and response in a replay."""

    request: _replay_api_client.ReplayRequest
    response: PatchedReplayResponse


class PatchedReplayFile(pydantic.BaseModel):
    """Represents a recorded session."""

    replay_id: str
    interactions: list[PatchedReplayInteraction]


_replay_api_client.ReplayResponse = PatchedReplayResponse
_replay_api_client.ReplayInteraction = PatchedReplayInteraction
_replay_api_client.ReplayFile = PatchedReplayFile


IS_KOKORO = os.getenv("KOKORO_BUILD_NUMBER") is not None


def pytest_collection_modifyitems(config, items):
    if IS_KOKORO:
        test_dir = os.path.dirname(os.path.abspath(__file__))
        for item in items:
            if test_dir in item.fspath.strpath:
                item.add_marker(
                    pytest.mark.skipif(
                        IS_KOKORO, reason="This test is only run in google3 env."
                    )
                )


def pytest_addoption(parser):
    parser.addoption(
        "--mode",
        action="store",
        default="auto",
        help="""Replay mode.
    One of:
    * auto: Replay if replay files exist, otherwise record.
    * record: Always call the API and record.
    * replay: Always replay, fail if replay files do not exist.
    * api: Always call the API and do not record.
    * tap: Always replay, fail if replay files do not exist. Also sets default values for the API key and replay directory.
  """,
    )
    parser.addoption(
        "--replays-directory-prefix",
        action="store",
        default=None,
        help="""Directory to use for replays.
    If not set, the default directory will be used.
  """,
    )


@pytest.fixture
def use_vertex():
    return True


# Overridden at the module level for each test file.
@pytest.fixture
def replays_prefix():
    return "test"


def _get_replay_id(use_vertex: bool, replays_prefix: str) -> str:
    test_name_ending = os.environ.get("PYTEST_CURRENT_TEST").split("::")[-1]
    test_name = test_name_ending.split(" ")[0].split("[")[0] + "." + "vertex"
    return "/".join([replays_prefix, test_name])


EVAL_CONFIG_GCS_URI = (
    "gs://vertex-ai-generative-ai-eval-sdk-resources/metrics/text_quality/v1.0.0.yaml"
)


def _mock_read_file_contents_side_effect(uri: str):
    """
    Side effect to mock GcsUtils.read_file_contents for eval test test_batch_evaluate.
    """
    if uri == EVAL_CONFIG_GCS_URI:
        # Construct the absolute path to the local mock file.
        current_dir = os.path.dirname(__file__)
        local_yaml_path = os.path.join(
            current_dir, "test_resources/mock_eval_config.yaml"
        )
        try:
            with open(local_yaml_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                "The mock data file 'mock_eval_config.yaml' was not found."
            )

    raise ValueError(
        f"Unexpected GCS URI '{uri}' in replay test. Only "
        f"'{EVAL_CONFIG_GCS_URI}' is mocked."
    )


@pytest.fixture
def client(use_vertex, replays_prefix, http_options, request):

    mode = request.config.getoption("--mode")
    if mode not in ["auto", "record", "replay", "api", "tap"]:
        raise ValueError("Invalid mode: " + mode)
    test_function_name = request.function.__name__
    test_filename = os.path.splitext(os.path.basename(request.path))[0]
    if test_function_name.startswith(test_filename):
        raise ValueError(
            f"""
      {test_function_name}:
      Do not include the test filename in the test function name.
      keep the test function name short."""
        )

    replay_id = _get_replay_id(use_vertex, replays_prefix)

    if mode == "tap":
        mode = "replay"

        # Set various environment variables to ensure that the test runs.
        os.environ["GOOGLE_API_KEY"] = "dummy-api-key"
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
            os.path.dirname(__file__),
            "credentials.json",
        )
        os.environ["GOOGLE_CLOUD_PROJECT"] = "project-id"
        os.environ["GOOGLE_CLOUD_LOCATION"] = "location"
        os.environ["VAPO_CONFIG_PATH"] = "gs://dummy-test/dummy-config.json"
        os.environ["VAPO_SERVICE_ACCOUNT_PROJECT_NUMBER"] = "1234567890"
        os.environ["GCS_BUCKET"] = "test-bucket"

        # Set the replay directory to the root directory of the replays.
        # This is needed to ensure that the replay files are found.
        replays_root_directory = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../../../../../../../../google/cloud/aiplatform/sdk/genai/replays",
            )
        )
        os.environ["GOOGLE_GENAI_REPLAYS_DIRECTORY"] = replays_root_directory
    replay_client = _replay_api_client.ReplayApiClient(
        mode=mode,
        replay_id=replay_id,
        vertexai=use_vertex,
        http_options=http_options,
    )

    with mock.patch.object(
        google_genai_client_module.Client, "_get_api_client"
    ) as patch_method:
        patch_method.return_value = replay_client
        google_genai_client = vertexai_genai_client_module.Client()

        if mode != "replay":
            yield google_genai_client
        else:
            # Eval tests make a call to GCS and BigQuery
            # Need to mock this so it doesn't call the service in replay mode
            with mock.patch.object(storage, "Client") as mock_storage_client:
                mock_client_instance = mock.MagicMock()

                mock_blob = mock.MagicMock()

                mock_blob.name = "v1.0.0.yaml"

                mock_client_instance.list_blobs.return_value = [mock_blob]

                mock_storage_client.return_value = mock_client_instance

                with mock.patch.object(bigquery, "Client") as mock_bigquery_client:
                    mock_bigquery_client.return_value = mock.MagicMock()

                    with mock.patch.object(
                        _evals_utils.GcsUtils, "read_file_contents"
                    ) as mock_read_file_contents:
                        mock_read_file_contents.side_effect = (
                            _mock_read_file_contents_side_effect
                        )

                        with mock.patch.object(
                            prompt_optimizer.time, "sleep"
                        ) as mock_job_wait:
                            mock_job_wait.return_value = None

                            google_genai_client = vertexai_genai_client_module.Client()

                            # Yield the client so that cleanup can be completed at the end of the test.
                            yield google_genai_client

        replay_client.close()
