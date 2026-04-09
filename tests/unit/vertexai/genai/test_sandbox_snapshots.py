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

import datetime
import importlib
from unittest import mock

from google import auth
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer
from google.genai import types as genai_types
import pytest

_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_RESOURCE_ID = "1028944691210842416"
_TEST_SANDBOX_ID = "sandbox-123"
_TEST_SNAPSHOT_ID = "snapshot-456"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_AGENT_ENGINE_RESOURCE_NAME = (
    f"{_TEST_PARENT}/reasoningEngines/{_TEST_RESOURCE_ID}"
)
_TEST_SANDBOX_RESOURCE_NAME = (
    f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}/sandboxes/{_TEST_SANDBOX_ID}"
)
_TEST_SNAPSHOT_RESOURCE_NAME = (
    f"{_TEST_SANDBOX_RESOURCE_NAME}/sandboxEnvironmentSnapshots/{_TEST_SNAPSHOT_ID}"
)


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestSandboxSnapshots:

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        self.client = vertexai.Client(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_create_snapshot(self):
        with mock.patch.object(
            self.client.agent_engines.sandboxes._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=b'{"expireTime": "2026-04-22T00:00:00Z"}', headers={}
            )

            snapshot = self.client.agent_engines.sandboxes.snapshots.create(
                name=_TEST_SANDBOX_RESOURCE_NAME,
                sandbox_environment_snapshot={},
            )

            assert isinstance(snapshot.expire_time, datetime.datetime)
            request_mock.assert_called_once()
            args, _ = request_mock.call_args
            assert args[0] == "post"
            assert args[1] == f"{_TEST_SANDBOX_RESOURCE_NAME}:snapshot"

    def test_delete_snapshot(self):
        with mock.patch.object(
            self.client.agent_engines.sandboxes._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=b'{"name": "operation-name"}', headers={}
            )

            operation = self.client.agent_engines.sandboxes.snapshots.delete(
                name=_TEST_SNAPSHOT_RESOURCE_NAME,
            )

            assert operation.name == "operation-name"
            request_mock.assert_called_once()
            args, _ = request_mock.call_args
            assert args[0] == "delete"
            assert args[1] == _TEST_SNAPSHOT_RESOURCE_NAME

    def test_get_snapshot(self):
        with mock.patch.object(
            self.client.agent_engines.sandboxes._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=b'{"expireTime": "2026-04-22T00:00:00Z"}', headers={}
            )

            snapshot = self.client.agent_engines.sandboxes.snapshots.get(
                name=_TEST_SNAPSHOT_RESOURCE_NAME,
            )

            assert isinstance(snapshot.expire_time, datetime.datetime)
            request_mock.assert_called_once()
            args, _ = request_mock.call_args
            assert args[0] == "get"
            assert args[1] == _TEST_SNAPSHOT_RESOURCE_NAME

    def test_list_snapshots(self):
        with mock.patch.object(
            self.client.agent_engines.sandboxes._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=(
                    b'{"sandboxEnvironmentSnapshots": [{"expireTime":'
                    b' "2026-04-22T00:00:00Z"}, {"expireTime":'
                    b' "2026-04-22T01:00:00Z"}]}'
                ),
                headers={},
            )

            response = self.client.agent_engines.sandboxes.snapshots.list(
                name=_TEST_SANDBOX_RESOURCE_NAME,
            )

            assert len(response.sandbox_environment_snapshots) == 2
            assert isinstance(
                response.sandbox_environment_snapshots[0].expire_time,
                datetime.datetime,
            )
            assert isinstance(
                response.sandbox_environment_snapshots[1].expire_time,
                datetime.datetime,
            )
            request_mock.assert_called_once()
            args, _ = request_mock.call_args
            assert args[0] == "get"
            assert (
                args[1] == f"{_TEST_SANDBOX_RESOURCE_NAME}/sandboxEnvironmentSnapshots"
            )
