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
from vertexai._genai import _agent_engines_utils
from google.cloud import storage, bigquery
from google.genai import _replay_api_client
from google.genai import client as google_genai_client_module
from vertexai._genai import _gcs_utils
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


@pytest.fixture
def mock_agent_engine_create_path_exists():
    """Mocks os.path.exists to return True."""
    with mock.patch("os.path.exists", return_value=True) as mock_exists:
        yield mock_exists


@pytest.fixture
def mock_agent_engine_create_base64_encoded_tarball():
    """Mocks the _create_base64_encoded_tarball function."""
    with mock.patch.object(
        _agent_engines_utils, "_create_base64_encoded_tarball"
    ) as mock_create_base64_encoded_tarball:
        mock_create_base64_encoded_tarball.return_value = "H4sIAAAAAAAAA-3UvWrDMBAHcM9-CpEpGRLkD8VQ6JOUElT7LFxkydEHxG9f2V1CKXSyu_x_i6TjJN2gk6N7HByNZIK_hEfINsCTa82zilcNTyMvRSPKao2vBM8KwZu6vJZXITJepGyRMb5FMT9FH6RjLHsM0mpr1CyN-i1vcsMo3aycjdMede0kV9YqTedW29id5TBpGXrrxjep0pO4kVGDIf-e_3edsI1APtxG20VNl2ne5o6_-r-oRer_Ypk2dd0s_Z82oP_3kLdaes-ensFLzpKOenaP5OajJ92fvoMLRyE6ww7LjrTwkzWeDnm-nmA_PqkN7PX5vOMJnwcAAAAAAAAAAAAAAAAAAADAdr4AI-kzQQAoAAA="
        yield mock_create_base64_encoded_tarball


@pytest.fixture
def mock_agent_engine_create_docker_base64_encoded_tarball():
    """Mocks the _create_base64_encoded_tarball function."""
    with mock.patch.object(
        _agent_engines_utils, "_create_base64_encoded_tarball"
    ) as mock_agent_engine_create_docker_base64_encoded_tarball:
        mock_agent_engine_create_docker_base64_encoded_tarball.return_value = "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"
        yield mock_agent_engine_create_docker_base64_encoded_tarball


def _get_replay_id(use_vertex: bool, replays_prefix: str) -> str:
    test_name_ending = os.environ.get("PYTEST_CURRENT_TEST").split("::")[-1]
    test_name = test_name_ending.split(" ")[0].split("[")[0] + "." + "vertex"
    return "/".join([replays_prefix, test_name])


EVAL_CONFIG_GCS_URI = (
    "gs://vertex-ai-generative-ai-eval-sdk-resources/metrics/text_quality/v1.0.0.yaml"
)
EVAL_ITEM_REQUEST_GCS_URI = "gs://lakeyk-limited-bucket/agora_eval_080525/request_"
EVAL_ITEM_RESULT_GCS_URI = "gs://lakeyk-limited-bucket/agora_eval_080525/result_"
EVAL_ITEM_REQUEST_GCS_URI_2 = "gs://lakeyk-limited-bucket/eval-data/request_"
EVAL_ITEM_RESULT_GCS_URI_2 = "gs://lakeyk-limited-bucket/eval-data/result_"
EVAL_GCS_URI_ITEMS = {
    EVAL_CONFIG_GCS_URI: "test_resources/mock_eval_config.yaml",
    EVAL_ITEM_REQUEST_GCS_URI: "test_resources/request_4813679498589372416.json",
    EVAL_ITEM_RESULT_GCS_URI: "test_resources/result_1486082323915997184.json",
    EVAL_ITEM_REQUEST_GCS_URI_2: "test_resources/request_4813679498589372416.json",
    EVAL_ITEM_RESULT_GCS_URI_2: "test_resources/result_1486082323915997184.json",
}


def _mock_read_file_contents_side_effect(uri: str):
    """
    Side effect to mock GcsUtils.read_file_contents for eval test test_batch_evaluate.
    """
    local_mock_file_path = None
    current_dir = os.path.dirname(__file__)
    if uri in EVAL_GCS_URI_ITEMS:
        local_mock_file_path = os.path.join(current_dir, EVAL_GCS_URI_ITEMS[uri])
    elif uri.startswith(EVAL_ITEM_REQUEST_GCS_URI) or uri.startswith(
        EVAL_ITEM_REQUEST_GCS_URI_2
    ):
        local_mock_file_path = os.path.join(
            current_dir, EVAL_GCS_URI_ITEMS[EVAL_ITEM_REQUEST_GCS_URI]
        )
    elif uri.startswith(EVAL_ITEM_RESULT_GCS_URI) or uri.startswith(
        EVAL_ITEM_RESULT_GCS_URI_2
    ):
        local_mock_file_path = os.path.join(
            current_dir, EVAL_GCS_URI_ITEMS[EVAL_ITEM_RESULT_GCS_URI]
        )

    if local_mock_file_path:
        try:
            with open(local_mock_file_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"The mock data file '{local_mock_file_path}' was not found."
            )

    raise ValueError(
        f"Unexpected GCS URI '{uri}' in replay test. Only "
        f"'{EVAL_CONFIG_GCS_URI}', '{EVAL_ITEM_REQUEST_GCS_URI}', and "
        f"'{EVAL_ITEM_RESULT_GCS_URI}' are mocked."
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
                        _gcs_utils.GcsUtils, "read_file_contents"
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
