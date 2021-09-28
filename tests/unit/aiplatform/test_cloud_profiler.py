# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

import importlib.util
import json
import os
import threading

import pytest
import unittest

from unittest import mock
from werkzeug import wrappers
from werkzeug.test import EnvironBuilder

from google.api_core import exceptions
from google.cloud import aiplatform
from google.cloud.aiplatform import training_utils
from google.cloud.aiplatform.tensorboard.plugins.tf_profiler import profile_uploader
from google.cloud.aiplatform.training_utils.cloud_profiler import base_plugin
from google.cloud.aiplatform.training_utils.cloud_profiler.plugins import tf_profiler
from google.cloud.aiplatform.training_utils.cloud_profiler.plugins.tf_profiler import (
    TFProfiler,
)
from google.cloud.aiplatform.training_utils.cloud_profiler.plugins import (
    tensorboard_api,
)
from google.cloud.aiplatform.training_utils.cloud_profiler import webserver
from google.cloud.aiplatform.training_utils.cloud_profiler import initializer


_ENV_VARS = training_utils.EnvironmentVariables()

# Mock cluster specs from the training environment.
_CLUSTER_SPEC_VM = '{"cluster":{"chief":["localhost:1234"]},"environment":"cloud","task":{"type":"chief","index":0}}'

_CLUSTER_SPEC_DISTRIB = '{"cluster":{"workerpool0":["host1:2222"],"workerpool1":["host2:2222"]},"environment":"cloud","task":{"type":"workerpool0","index":0},"job":"{\\"python_module\\":\\"\\",\\"package_uris\\":[],\\"job_args\\":[]}"}'


def _create_mock_plugin(plugin_name: str = "test_plugin"):
    mock_plugin = mock.Mock(spec=base_plugin.BasePlugin)
    mock_plugin.PLUGIN_NAME = plugin_name
    return mock_plugin


@pytest.fixture
def tf_profile_plugin_mock():
    """Mock the tensorboard profile plugin"""
    import tensorboard_plugin_profile.profile_plugin

    with mock.patch.object(
        tensorboard_plugin_profile.profile_plugin.ProfilePlugin, "capture_route"
    ) as profile_mock:
        profile_mock.return_value = (
            wrappers.BaseResponse(
                json.dumps({"error": "some error"}),
                content_type="application/json",
                status=200,
            ),
        )
        yield profile_mock


@pytest.fixture
def tensorboard_api_mock():
    with mock.patch.object(
        tensorboard_api, "create_profile_request_sender",
    ) as sender_mock:
        sender_mock.return_value = mock.Mock()
        yield sender_mock


@pytest.fixture
def setupEnvVars():
    os.environ["AIP_TF_PROFILER_PORT"] = "6009"
    os.environ["AIP_TENSORBOARD_LOG_DIR"] = "tmp/"
    os.environ["AIP_TENSORBOARD_API_URI"] = "test_api_uri"
    os.environ[
        "AIP_TENSORBOARD_RESOURCE_NAME"
    ] = "projects/123/region/us-central1/tensorboards/mytb"
    os.environ["CLUSTER_SPEC"] = _CLUSTER_SPEC_VM
    os.environ["CLOUD_ML_JOB_ID"] = "myjob"


@pytest.fixture
def mock_api_environment_variables():
    with mock.patch.object(tensorboard_api, "_ENV_VARS") as mock_env:
        mock_env.tensorboard_api_uri = "testuri"
        mock_env.tensorboard_resource_name = (
            "projects/testproj/locations/us-central1/tensorboards/123"
        )
        mock_env.cloud_ml_job_id = "test_job_id"
        mock_env.tensorboard_log_dir = "gs://my_log_dir"

        yield mock_env


def test_get_hostnames_vm():
    mock_cluster_spec = {
        "CLUSTER_SPEC": _CLUSTER_SPEC_VM,
        "AIP_TF_PROFILER_PORT": "6009",
    }
    with mock.patch.dict(os.environ, mock_cluster_spec):
        hosts = tf_profiler._get_hostnames()
    assert hosts == "grpc://localhost:6009"


def test_get_hostnames_cluster():
    mock_cluster_spec = {
        "CLUSTER_SPEC": _CLUSTER_SPEC_DISTRIB,
        "AIP_TF_PROFILER_PORT": "6009",
    }
    with mock.patch.dict(os.environ, mock_cluster_spec):
        hosts = tf_profiler._get_hostnames()
    assert hosts == "grpc://host1:6009,grpc://host2:6009"


class TestProfilerPlugin:
    # Initializion tests
    @pytest.mark.usefixtures("setupEnvVars")
    def testCanInitializeProfilerPortUnset(self):
        os.environ.pop("AIP_TF_PROFILER_PORT")
        assert not TFProfiler.can_initialize()

    @pytest.mark.usefixtures("setupEnvVars")
    def testCanInitializeTBLogDirUnset(self):
        os.environ.pop("AIP_TENSORBOARD_LOG_DIR")
        assert not TFProfiler.can_initialize()

    @pytest.mark.usefixtures("setupEnvVars")
    def testCanInitializeTBAPIuriUnset(self):
        os.environ.pop("AIP_TENSORBOARD_API_URI")
        assert not TFProfiler.can_initialize()

    @pytest.mark.usefixtures("setupEnvVars")
    def testCanInitializeTBResourceNameUnset(self):
        os.environ.pop("AIP_TENSORBOARD_RESOURCE_NAME")
        assert not TFProfiler.can_initialize()

    @pytest.mark.usefixtures("setupEnvVars")
    def testCanInitializeJobIdUnset(self):
        os.environ.pop("CLOUD_ML_JOB_ID")
        assert not TFProfiler.can_initialize()

    @pytest.mark.usefixtures("setupEnvVars")
    def testCanInitializeNoClusterSpec(self):
        os.environ["CLUSTER_SPEC"] = "{}"
        assert not TFProfiler.can_initialize()

    @pytest.mark.usefixtures("setupEnvVars")
    def testCanInitializeTFInstalled(self):
        orig_find_spec = importlib.util.find_spec

        def tf_import_mock(name, *args, **kwargs):
            if name == "tensorflow":
                return None
            return orig_find_spec(name, *args, **kwargs)

        with mock.patch("importlib.util.find_spec", side_effect=tf_import_mock):
            assert not TFProfiler.can_initialize()

    @pytest.mark.usefixtures("setupEnvVars")
    def testCanInitializeTFVersion(self):
        import tensorflow

        with mock.patch.dict(tensorflow.__dict__, {"__version__": "1.2.3.4"}):
            assert not TFProfiler.can_initialize()

    @pytest.mark.usefixtures("setupEnvVars")
    def testCanInitializeOldTFVersion(self):
        import tensorflow

        with mock.patch.dict(tensorflow.__dict__, {"__version__": "1.13.0"}):
            assert not TFProfiler.can_initialize()

    @pytest.mark.usefixtures("setupEnvVars")
    def testCanInitializeNoProfilePlugin(self):
        orig_find_spec = importlib.util.find_spec

        def plugin_import_mock(name, *args, **kwargs):
            if name == "tensorboard_plugin_profile":
                return None
            return orig_find_spec(name, *args, **kwargs)

        with mock.patch("importlib.util.find_spec", side_effect=plugin_import_mock):
            assert not TFProfiler.can_initialize()

    @pytest.mark.usefixtures("setupEnvVars")
    def testCanInitialize(self):
        assert TFProfiler.can_initialize()

    def testSetup(self):
        import tensorflow

        with mock.patch.object(
            tensorflow.profiler.experimental.server, "start", return_value=None
        ) as server_mock:
            TFProfiler.setup()

            assert server_mock.call_count == 1

    @pytest.mark.usefixtures("setupEnvVars")
    def testPostSetupChecksFail(self):
        with mock.patch.dict(os.environ, {"CLUSTER_SPEC": "{}"}):
            assert not TFProfiler.post_setup_check()

    @pytest.mark.usefixtures("setupEnvVars")
    def testPostSetupChecks(self):
        assert TFProfiler.post_setup_check()

    # Tests for plugin
    @pytest.mark.usefixtures("tf_profile_plugin_mock")
    @pytest.mark.usefixtures("tensorboard_api_mock")
    @pytest.mark.usefixtures("setupEnvVars")
    def testCaptureProfile(self):
        profiler = TFProfiler()
        environ = dict(QUERY_STRING="?service_addr=myhost1,myhost2&someotherdata=5")
        start_response = None

        resp = profiler.capture_profile_wrapper(environ, start_response)
        assert resp[0].status_code == 200

    @pytest.mark.usefixtures("tf_profile_plugin_mock")
    @pytest.mark.usefixtures("tensorboard_api_mock")
    @pytest.mark.usefixtures("setupEnvVars")
    def testCaptureProfileNoClusterSpec(self):
        profiler = TFProfiler()

        environ = dict(QUERY_STRING="?service_addr=myhost1,myhost2&someotherdata=5")
        start_response = None

        with mock.patch.dict(os.environ, {"CLUSTER_SPEC": "{}"}):
            resp = profiler.capture_profile_wrapper(environ, start_response)

        assert resp.status_code == 500

    @pytest.mark.usefixtures("tf_profile_plugin_mock")
    @pytest.mark.usefixtures("tensorboard_api_mock")
    @pytest.mark.usefixtures("setupEnvVars")
    def testCaptureProfileNoCluster(self):

        profiler = TFProfiler()

        environ = dict(QUERY_STRING="?service_addr=myhost1,myhost2&someotherdata=5")
        start_response = None

        with mock.patch.dict(os.environ, {"CLUSTER_SPEC": '{"cluster": {}}'}):
            resp = profiler.capture_profile_wrapper(environ, start_response)

        assert resp.status_code == 500

    @pytest.mark.usefixtures("tf_profile_plugin_mock")
    @pytest.mark.usefixtures("tensorboard_api_mock")
    @pytest.mark.usefixtures("setupEnvVars")
    def testGetRoutes(self):
        profiler = TFProfiler()

        routes = profiler.get_routes()
        assert isinstance(routes, dict)


# Tensorboard API tests
class TestTensorboardAPIBuilder(unittest.TestCase):
    @pytest.mark.usefixtures("mock_api_environment_variables")
    def test_get_api_client(self):
        with mock.patch.object(aiplatform, "initializer") as mock_initializer:
            tensorboard_api._get_api_client()
            mock_initializer.global_config.create_client.assert_called_once()

    def test_get_project_id_fail(self):
        with mock.patch.object(tensorboard_api, "_ENV_VARS") as mock_env:
            mock_env.tensorboard_resource_name = "bad_resource"
            self.assertRaises(ValueError, tensorboard_api._get_project_id)

    @pytest.mark.usefixtures("mock_api_environment_variables")
    def test_get_project_id(self):
        project_id = tensorboard_api._get_project_id()
        assert project_id == "testproj"

    @pytest.mark.usefixtures("mock_api_environment_variables")
    def test_get_or_create_experiment(self):
        api = mock.Mock()
        api.create_tensorboard_experiment.side_effect = exceptions.AlreadyExists("test")
        tensorboard_api._get_or_create_experiment(api, "test")
        api.get_tensorboard_experiment.assert_called_once()

    @pytest.mark.usefixtures("mock_api_environment_variables")
    def test_create_profile_request_sender(self):
        with mock.patch.object(profile_uploader, "ProfileRequestSender") as mock_sender:
            with mock.patch.object(aiplatform, "initializer"):
                tensorboard_api.create_profile_request_sender()
                mock_sender.assert_called_once()


# Webserver tests
class TestWebServer(unittest.TestCase):
    def test_create_webserver_bad_route(self):
        plugin = _create_mock_plugin()
        plugin.get_routes.return_value = {"my_route": "some_handler"}

        self.assertRaises(ValueError, webserver.WebServer, [plugin])

    def test_dispatch_bad_request(self):
        plugin = _create_mock_plugin()
        plugin.get_routes.return_value = {"/test_route": "test_handler"}

        ws = webserver.WebServer([plugin])

        builder = EnvironBuilder(method="GET", path="/")

        env = builder.get_environ()

        # Mock a start response callable
        response = []
        buff = []

        def start_response(status, headers):
            response[:] = [status, headers]
            return buff.append

        ws(env, start_response)

        assert response[0] == "404 NOT FOUND"

    def test_correct_response(self):
        res_dict = {"response": "OK"}

        def my_callable(var1, var2):
            return wrappers.BaseResponse(
                json.dumps(res_dict), content_type="application/json", status=200
            )

        plugin = _create_mock_plugin()
        plugin.get_routes.return_value = {"/my_route": my_callable}
        ws = webserver.WebServer([plugin])

        builder = EnvironBuilder(method="GET", path="/test_plugin/my_route")

        env = builder.get_environ()

        # Mock a start response callable
        response = []
        buff = []

        def start_response(status, headers):
            response[:] = [status, headers]
            return buff.append

        res = ws(env, start_response)

        final_response = json.loads(res.response[0].decode("utf-8"))

        assert final_response == res_dict


# Initializer tests
class TestInitializer(unittest.TestCase):
    def test_build_plugin_fail_initialize(self):
        plugin = _create_mock_plugin()
        plugin.can_initialize.return_value = False

        assert not initializer._build_plugin(plugin)

    def test_build_plugin_fail_setup_check(self):
        plugin = _create_mock_plugin()
        plugin.can_initialize.return_value = True
        plugin.post_setup_check.return_value = False

        assert not initializer._build_plugin(plugin)

    def test_build_plugin_success(self):
        plugin = _create_mock_plugin()
        plugin.can_initialize.return_value = True
        plugin.post_setup_check.return_value = True

        initializer._build_plugin(plugin)

        assert plugin.called

    def test_initialize_bad_plugin(self):
        with mock.patch.object(initializer, "_AVAILABLE_PLUGINS", {}):
            self.assertRaises(ValueError, initializer.initialize, "bad_plugin")

    def test_initialize_build_plugin_fail(self):
        plugin = _create_mock_plugin()
        with mock.patch.object(initializer, "_AVAILABLE_PLUGINS", {"test": plugin}):
            with mock.patch.object(initializer, "_build_plugin") as build_mock:
                with mock.patch.object(
                    initializer, "_run_app_thread"
                ) as app_thread_mock:
                    build_mock.return_value = None
                    initializer.initialize("test")

                    assert not app_thread_mock.call_count

    def test_initialize_build_plugin_success(self):
        plugin = _create_mock_plugin()
        plugin.get_routes.return_value = {"/test": "route"}

        with mock.patch.object(initializer, "_AVAILABLE_PLUGINS", {"test": plugin}):
            with mock.patch.object(initializer, "_build_plugin") as build_mock:
                with mock.patch.object(
                    initializer, "_run_app_thread"
                ) as app_thread_mock:
                    build_mock.return_value = plugin
                    initializer.initialize("test")

                    assert app_thread_mock.call_count == 1

    def test_run_app_thread(self):
        with mock.patch.object(threading, "Thread") as mock_thread:
            daemon_mock = mock.Mock()
            mock_thread.return_value = daemon_mock

            initializer._run_app_thread(None)

            assert daemon_mock.start.call_count == 1
