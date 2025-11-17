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
