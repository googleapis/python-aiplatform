# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

import io
import os
import pytest
import textwrap
from unittest import mock

import docker

from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.docker_utils import build
from google.cloud.aiplatform.docker_utils import errors
from google.cloud.aiplatform.docker_utils import local_util
from google.cloud.aiplatform.docker_utils import run
from google.cloud.aiplatform.docker_utils import utils
from google.cloud.aiplatform.utils import prediction_utils


_TEST_CONTAINER_LOGS = b"line1\nline2\nline3\n"
_TEST_CONTAINER_LOGS_LEN = 3


@pytest.fixture
def docker_client_mock():
    with mock.patch("docker.from_env") as from_env_mock:
        client = from_env_mock.return_value
        client().containers.run.return_value = None
        client.images.get.return_value = None
        yield client


@pytest.fixture
def docker_client_mock_image_get_not_found():
    with mock.patch("docker.from_env") as from_env_mock:
        client = from_env_mock.return_value
        client.images.get.side_effect = docker.errors.ImageNotFound("")
        yield client


@pytest.fixture
def docker_client_mock_image_get_api_error():
    with mock.patch("docker.from_env") as from_env_mock:
        client = from_env_mock.return_value
        client.images.get.side_effect = docker.errors.APIError("")
        yield client


@pytest.fixture
def docker_container_mock():
    container = mock.MagicMock()
    container.logs.return_value = _TEST_CONTAINER_LOGS
    return container


@pytest.fixture
def execute_command_mock():
    with mock.patch.object(local_util, "execute_command") as execute_command_mock:
        execute_command_mock.return_value = 0
        yield execute_command_mock


@pytest.fixture
def execute_command_return_code_1_mock():
    with mock.patch.object(
        local_util, "execute_command"
    ) as execute_command_return_code_1_mock:
        execute_command_return_code_1_mock.return_value = 1
        yield execute_command_return_code_1_mock


class MockedPopen:
    def __init__(self, args, **kwargs):
        self.args = args
        self.returncode = 0
        self.stdin = mock.Mock()
        self.stdout = mock.Mock(return_value="fake output")

    def __enter__(self):
        return self

    def __exit__(self, exe_type, value, traceback):
        pass

    def communicate(self, input=None, timeout=None):
        return "", ""


@pytest.fixture
def textiowrapper_mock():
    with mock.patch.object(io, "TextIOWrapper") as textiowrapper_mock:
        textiowrapper_mock.return_value = io.TextIOWrapper(io.BytesIO(b""))
        yield textiowrapper_mock


@pytest.fixture
def make_dockerfile_mock():
    with mock.patch.object(build, "make_dockerfile") as make_dockerfile_mock:
        yield make_dockerfile_mock


class TestRun:
    IMAGE_URI = "test_image:latest"

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_run_prediction_container(self, docker_client_mock):
        run.run_prediction_container(self.IMAGE_URI)

        docker_client_mock.containers.run.assert_called_once_with(
            self.IMAGE_URI,
            command=None,
            entrypoint=None,
            ports={prediction.DEFAULT_AIP_HTTP_PORT: None},
            environment={
                prediction.AIP_HTTP_PORT: prediction.DEFAULT_AIP_HTTP_PORT,
                prediction.AIP_HEALTH_ROUTE: None,
                prediction.AIP_PREDICT_ROUTE: None,
                prediction.AIP_STORAGE_URI: "",
            },
            volumes=[],
            device_requests=None,
            detach=True,
        )

    def test_run_prediction_container_with_all_parameters(
        self, tmp_path, docker_client_mock
    ):
        artifact_uri = "gs://myproject/mymodel"
        serving_container_predict_route = "/custom_predict"
        serving_container_health_route = "/custom_health"
        serving_container_command = ["echo", "hello"]
        serving_container_args = [">", "tmp.log"]
        serving_container_environment_variables = {"custom_key": "custom_value"}
        serving_container_ports = [5555]
        credential_path = tmp_path / "key.json"
        credential_path.write_text("")
        host_port = 6666
        environment = {k: v for k, v in serving_container_environment_variables.items()}
        environment[prediction.AIP_HTTP_PORT] = serving_container_ports[0]
        environment[prediction.AIP_HEALTH_ROUTE] = serving_container_health_route
        environment[prediction.AIP_PREDICT_ROUTE] = serving_container_predict_route
        environment[prediction.AIP_STORAGE_URI] = artifact_uri
        environment[
            run._ADC_ENVIRONMENT_VARIABLE
        ] = run._DEFAULT_CONTAINER_CRED_KEY_PATH
        volumes = [f"{credential_path}:{run._DEFAULT_CONTAINER_CRED_KEY_PATH}"]

        run.run_prediction_container(
            self.IMAGE_URI,
            artifact_uri=artifact_uri,
            serving_container_predict_route=serving_container_predict_route,
            serving_container_health_route=serving_container_health_route,
            serving_container_command=serving_container_command,
            serving_container_args=serving_container_args,
            serving_container_environment_variables=serving_container_environment_variables,
            serving_container_ports=serving_container_ports,
            credential_path=credential_path,
            host_port=host_port,
        )

        docker_client_mock.containers.run.assert_called_once_with(
            self.IMAGE_URI,
            command=serving_container_args,
            entrypoint=serving_container_command,
            ports={serving_container_ports[0]: host_port},
            environment=environment,
            volumes=volumes,
            device_requests=None,
            detach=True,
        )

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_run_prediction_container_with_envs_replaced_by_envs(
        self, tmp_path, docker_client_mock
    ):
        serving_container_environment_variables = {
            "VAR_1": "foo",
            "VAR_2": "$(VAR_3) bar",
            "VAR_3": "$(VAR_1) bar",
            "VAR_4": "$$(VAR_1)",
        }
        environment = {k: v for k, v in serving_container_environment_variables.items()}
        environment[prediction.AIP_HTTP_PORT] = prediction.DEFAULT_AIP_HTTP_PORT
        environment[prediction.AIP_HEALTH_ROUTE] = None
        environment[prediction.AIP_PREDICT_ROUTE] = None
        environment[prediction.AIP_STORAGE_URI] = ""
        # Envs referencing earlier entries will be changed. Those envs referencing later
        # entries won't be changed.
        environment["VAR_3"] = "foo bar"
        # Double $$ will be replaced with a single $.
        environment["VAR_4"] = "$(VAR_1)"

        run.run_prediction_container(
            self.IMAGE_URI,
            serving_container_environment_variables=serving_container_environment_variables,
        )

        docker_client_mock.containers.run.assert_called_once_with(
            self.IMAGE_URI,
            command=None,
            entrypoint=None,
            ports={prediction.DEFAULT_AIP_HTTP_PORT: None},
            environment=environment,
            volumes=[],
            device_requests=None,
            detach=True,
        )

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_run_prediction_container_with_command_replaced_by_envs(
        self, tmp_path, docker_client_mock
    ):
        serving_container_command = ["$(VAR_1)", "$$(VAR_1)", "$(VAR_2)"]
        serving_container_environment_variables = {
            "VAR_1": "foo",
        }
        environment = {k: v for k, v in serving_container_environment_variables.items()}
        environment[prediction.AIP_HTTP_PORT] = prediction.DEFAULT_AIP_HTTP_PORT
        environment[prediction.AIP_HEALTH_ROUTE] = None
        environment[prediction.AIP_PREDICT_ROUTE] = None
        environment[prediction.AIP_STORAGE_URI] = ""
        # Command references existing environment variables.
        expected_entrypoint = ["foo", "$(VAR_1)", "$(VAR_2)"]

        run.run_prediction_container(
            self.IMAGE_URI,
            serving_container_command=serving_container_command,
            serving_container_environment_variables=serving_container_environment_variables,
        )

        docker_client_mock.containers.run.assert_called_once_with(
            self.IMAGE_URI,
            command=None,
            entrypoint=expected_entrypoint,
            ports={prediction.DEFAULT_AIP_HTTP_PORT: None},
            environment=environment,
            volumes=[],
            device_requests=None,
            detach=True,
        )

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_run_prediction_container_with_args_replaced_by_envs(
        self, tmp_path, docker_client_mock
    ):
        serving_container_args = ["$(VAR_1)", "$$(VAR_1)", "$(VAR_2)"]
        serving_container_environment_variables = {
            "VAR_1": "foo",
        }
        environment = {k: v for k, v in serving_container_environment_variables.items()}
        environment[prediction.AIP_HTTP_PORT] = prediction.DEFAULT_AIP_HTTP_PORT
        environment[prediction.AIP_HEALTH_ROUTE] = None
        environment[prediction.AIP_PREDICT_ROUTE] = None
        environment[prediction.AIP_STORAGE_URI] = ""
        # Args references existing environment variables.
        expected_command = ["foo", "$(VAR_1)", "$(VAR_2)"]

        run.run_prediction_container(
            self.IMAGE_URI,
            serving_container_args=serving_container_args,
            serving_container_environment_variables=serving_container_environment_variables,
        )

        docker_client_mock.containers.run.assert_called_once_with(
            self.IMAGE_URI,
            command=expected_command,
            entrypoint=None,
            ports={prediction.DEFAULT_AIP_HTTP_PORT: None},
            environment=environment,
            volumes=[],
            device_requests=None,
            detach=True,
        )

    def test_run_prediction_container_credential_from_adc(
        self, tmp_path, docker_client_mock
    ):
        credential_path = tmp_path / "key.json"
        credential_path.write_text("")
        volumes = [f"{credential_path}:{run._DEFAULT_CONTAINER_CRED_KEY_PATH}"]

        with mock.patch.dict(
            os.environ, {run._ADC_ENVIRONMENT_VARIABLE: credential_path.as_posix()}
        ):
            run.run_prediction_container(self.IMAGE_URI)

        docker_client_mock.containers.run.assert_called_once_with(
            self.IMAGE_URI,
            command=None,
            entrypoint=None,
            ports={prediction.DEFAULT_AIP_HTTP_PORT: None},
            environment={
                prediction.AIP_HTTP_PORT: prediction.DEFAULT_AIP_HTTP_PORT,
                prediction.AIP_HEALTH_ROUTE: None,
                prediction.AIP_PREDICT_ROUTE: None,
                prediction.AIP_STORAGE_URI: "",
                run._ADC_ENVIRONMENT_VARIABLE: run._DEFAULT_CONTAINER_CRED_KEY_PATH,
            },
            volumes=volumes,
            device_requests=None,
            detach=True,
        )

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_run_prediction_container_gpu_count(self, docker_client_mock):
        gpu_count = 1
        gpu_capabilities = [["gpu"]]

        run.run_prediction_container(
            self.IMAGE_URI,
            gpu_count=gpu_count,
            gpu_capabilities=gpu_capabilities,
        )

        docker_client_mock.containers.run.assert_called_once_with(
            self.IMAGE_URI,
            command=None,
            entrypoint=None,
            ports={prediction.DEFAULT_AIP_HTTP_PORT: None},
            environment={
                prediction.AIP_HTTP_PORT: prediction.DEFAULT_AIP_HTTP_PORT,
                prediction.AIP_HEALTH_ROUTE: None,
                prediction.AIP_PREDICT_ROUTE: None,
                prediction.AIP_STORAGE_URI: "",
            },
            volumes=[],
            device_requests=[
                docker.types.DeviceRequest(
                    count=gpu_count, capabilities=gpu_capabilities
                )
            ],
            detach=True,
        )

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_run_prediction_container_gpu_device_ids(self, docker_client_mock):
        gpu_device_ids = ["1"]
        gpu_capabilities = [["gpu"]]

        run.run_prediction_container(
            self.IMAGE_URI,
            gpu_device_ids=gpu_device_ids,
            gpu_capabilities=gpu_capabilities,
        )

        docker_client_mock.containers.run.assert_called_once_with(
            self.IMAGE_URI,
            command=None,
            entrypoint=None,
            ports={prediction.DEFAULT_AIP_HTTP_PORT: None},
            environment={
                prediction.AIP_HTTP_PORT: prediction.DEFAULT_AIP_HTTP_PORT,
                prediction.AIP_HEALTH_ROUTE: None,
                prediction.AIP_PREDICT_ROUTE: None,
                prediction.AIP_STORAGE_URI: "",
            },
            volumes=[],
            device_requests=[
                docker.types.DeviceRequest(
                    device_ids=gpu_device_ids, capabilities=gpu_capabilities
                )
            ],
            detach=True,
        )

    def test_run_prediction_container_artifact_uri_is_local_path_default_workdir(
        self, tmp_path, docker_client_mock
    ):
        artifact_uri = tmp_path / "models"
        artifact_uri.mkdir()
        fake_model_artifact = artifact_uri / "model.pb"
        fake_model_artifact.write_text("")
        environment = {}
        environment[prediction.AIP_HTTP_PORT] = prediction.DEFAULT_AIP_HTTP_PORT
        environment[prediction.AIP_HEALTH_ROUTE] = None
        environment[prediction.AIP_PREDICT_ROUTE] = None
        environment[prediction.AIP_STORAGE_URI] = utils.DEFAULT_MOUNTED_MODEL_DIRECTORY
        environment[
            run._ADC_ENVIRONMENT_VARIABLE
        ] = run._DEFAULT_CONTAINER_CRED_KEY_PATH
        credential_path = tmp_path / "key.json"
        credential_path.write_text("")
        volumes = [
            f"{fake_model_artifact.as_posix()}:{utils.DEFAULT_MOUNTED_MODEL_DIRECTORY + '/model.pb'}",
            f"{credential_path}:{run._DEFAULT_CONTAINER_CRED_KEY_PATH}",
        ]

        with mock.patch.dict(
            os.environ, {run._ADC_ENVIRONMENT_VARIABLE: credential_path.as_posix()}
        ):
            run.run_prediction_container(
                self.IMAGE_URI,
                artifact_uri=artifact_uri.as_posix(),
            )

        docker_client_mock.containers.run.assert_called_once_with(
            self.IMAGE_URI,
            command=None,
            entrypoint=None,
            ports={prediction.DEFAULT_AIP_HTTP_PORT: None},
            environment=environment,
            volumes=volumes,
            device_requests=None,
            detach=True,
        )

    def test_run_prediction_container_artifact_uri_is_local_path_but_not_exists(
        self, tmp_path, docker_client_mock
    ):
        artifact_uri = tmp_path / "models"
        environment = {}
        environment[prediction.AIP_HTTP_PORT] = prediction.DEFAULT_AIP_HTTP_PORT
        environment[prediction.AIP_HEALTH_ROUTE] = None
        environment[prediction.AIP_PREDICT_ROUTE] = None
        environment[prediction.AIP_STORAGE_URI] = utils.DEFAULT_WORKDIR
        environment[
            run._ADC_ENVIRONMENT_VARIABLE
        ] = run._DEFAULT_CONTAINER_CRED_KEY_PATH
        credential_path = tmp_path / "key.json"
        credential_path.write_text("")
        expected_message = (
            "artifact_uri should be specified as either a GCS uri which starts with "
            f"`{prediction_utils.GCS_URI_PREFIX}` or a path to a local directory. "
            f'However, "{artifact_uri}" does not exist.'
        )

        with pytest.raises(ValueError) as exception:
            with mock.patch.dict(
                os.environ, {run._ADC_ENVIRONMENT_VARIABLE: credential_path.as_posix()}
            ):
                run.run_prediction_container(
                    self.IMAGE_URI,
                    artifact_uri=artifact_uri.as_posix(),
                )

        assert str(exception.value) == expected_message

    def test_run_prediction_container_credential_path_not_exists(
        self, docker_client_mock
    ):
        credential_path = "key.json"
        expected_message = f'credential_path does not exist: "{credential_path}".'

        with pytest.raises(ValueError) as exception:
            run.run_prediction_container(
                self.IMAGE_URI, credential_path=credential_path
            )

        assert str(exception.value) == expected_message

    @mock.patch.dict(os.environ, {run._ADC_ENVIRONMENT_VARIABLE: "key.json"})
    def test_run_prediction_container_adc_value_not_exists(self, docker_client_mock):
        expected_message = (
            f"The file from the environment variable {run._ADC_ENVIRONMENT_VARIABLE} does "
            f'not exist: "key.json".'
        )

        with pytest.raises(ValueError) as exception:
            run.run_prediction_container(self.IMAGE_URI)

        assert str(exception.value) == expected_message

    def test_print_container_logs(self, docker_container_mock):
        with mock.patch(
            "google.cloud.aiplatform.docker_utils.run._logger"
        ) as logger_mock:
            logs_len = run.print_container_logs(docker_container_mock)

        assert logs_len == _TEST_CONTAINER_LOGS_LEN
        assert docker_container_mock.logs.called
        assert logger_mock.info.call_count == _TEST_CONTAINER_LOGS_LEN

    def test_print_container_logs_with_start_index(self, docker_container_mock):
        start_index = 1
        with mock.patch(
            "google.cloud.aiplatform.docker_utils.run._logger"
        ) as logger_mock:
            logs_len = run.print_container_logs(
                docker_container_mock, start_index=start_index
            )

        assert logs_len == _TEST_CONTAINER_LOGS_LEN
        assert docker_container_mock.logs.called
        assert logger_mock.info.call_count == (_TEST_CONTAINER_LOGS_LEN - start_index)

    def test_print_container_logs_with_message(self, docker_container_mock):
        with mock.patch(
            "google.cloud.aiplatform.docker_utils.run._logger"
        ) as logger_mock:
            logs_len = run.print_container_logs(
                docker_container_mock, message="Test message:"
            )

        assert logs_len == _TEST_CONTAINER_LOGS_LEN
        assert docker_container_mock.logs.called
        assert logger_mock.info.call_count == _TEST_CONTAINER_LOGS_LEN + 1


class TestBuild:
    BASE_IMAGE = "python:3.7"
    SOURCE_DIR = "src"
    HOST_WORKDIR_BASENAME = "user_code"
    HOST_WORKDIR = f"./{SOURCE_DIR}/{HOST_WORKDIR_BASENAME}"
    HOME = utils.DEFAULT_HOME
    WORKDIR = utils.DEFAULT_WORKDIR
    SCRIPT = "./user_code/entrypoint.py"
    SCRIPT_PACKAGE_PATH = "user_code/entrypoint.py"
    PYTHON_MODULE = "custom.python.module"
    PACKAGE = utils.Package(
        script=SCRIPT, package_path=HOST_WORKDIR, python_module=None
    )
    PACKAGE_WITH_PYTHON_MODULE = utils.Package(
        script=SCRIPT, package_path=HOST_WORKDIR, python_module=PYTHON_MODULE
    )
    PACKAGE_NO_SCRIPT_AND_MODULE = utils.Package(
        script=None, package_path=HOST_WORKDIR, python_module=None
    )
    OUTPUT_IMAGE_NAME = "test_image:latest"
    REQUIREMENTS_FILE = "requirements.txt"
    EXTRA_PACKAGE = "custom_package.tar.gz"
    SETUP_FILE = "setup.py"
    PIP = "pip"
    PYTHON = "python"

    def test_make_dockerfile(self):
        result = build.make_dockerfile(
            self.BASE_IMAGE, self.PACKAGE, self.WORKDIR, self.HOME
        )

        assert f"FROM {self.BASE_IMAGE}\n" in result
        assert f"WORKDIR {self.WORKDIR}\n" in result
        assert f"ENV HOME={self.HOME}\n" in result
        assert 'COPY [".", "."]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result

    def test_make_dockerfile_with_python_module(self):
        result = build.make_dockerfile(
            self.BASE_IMAGE, self.PACKAGE_WITH_PYTHON_MODULE, self.WORKDIR, self.HOME
        )

        assert f"FROM {self.BASE_IMAGE}\n" in result
        assert f"WORKDIR {self.WORKDIR}\n" in result
        assert f"ENV HOME={self.HOME}\n" in result
        assert 'COPY [".", "."]\n' in result
        assert f'ENTRYPOINT ["python", "-m", "{self.PYTHON_MODULE}"]' in result

    def test_make_dockerfile_no_script_and_module(self):
        result = build.make_dockerfile(
            self.BASE_IMAGE, self.PACKAGE_NO_SCRIPT_AND_MODULE, self.WORKDIR, self.HOME
        )

        assert f"FROM {self.BASE_IMAGE}\n" in result
        assert f"WORKDIR {self.WORKDIR}\n" in result
        assert f"ENV HOME={self.HOME}\n" in result
        assert 'COPY [".", "."]\n' in result
        assert "ENTRYPOINT" not in result

    def test_make_dockerfile_with_requirements_path(self):
        requirements_path = "./requirements.txt"

        result = build.make_dockerfile(
            self.BASE_IMAGE,
            self.PACKAGE,
            self.WORKDIR,
            self.HOME,
            requirements_path=requirements_path,
        )

        assert f"FROM {self.BASE_IMAGE}\n" in result
        assert f"WORKDIR {self.WORKDIR}\n" in result
        assert f"ENV HOME={self.HOME}\n" in result
        assert 'COPY [".", "."]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert (
            f"RUN pip install --no-cache-dir --force-reinstall -r {requirements_path}\n"
            in result
        )

    def test_make_dockerfile_with_setup_path(self):
        setup_path = "./custom_setup.py"

        result = build.make_dockerfile(
            self.BASE_IMAGE,
            self.PACKAGE,
            self.WORKDIR,
            self.HOME,
            setup_path=setup_path,
        )

        assert f"FROM {self.BASE_IMAGE}\n" in result
        assert f"WORKDIR {self.WORKDIR}\n" in result
        assert f"ENV HOME={self.HOME}\n" in result
        assert 'COPY [".", "."]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert f'COPY ["{setup_path}", "./setup.py"]\n' in result
        assert "RUN pip install --no-cache-dir --force-reinstall .\n" in result

    def test_make_dockerfile_with_extra_requirements(self):
        extra_requirement = "custom_package==1.0"

        result = build.make_dockerfile(
            self.BASE_IMAGE,
            self.PACKAGE,
            self.WORKDIR,
            self.HOME,
            extra_requirements=[extra_requirement],
        )

        assert f"FROM {self.BASE_IMAGE}\n" in result
        assert f"WORKDIR {self.WORKDIR}\n" in result
        assert f"ENV HOME={self.HOME}\n" in result
        assert 'COPY [".", "."]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert (
            f"RUN pip install --no-cache-dir --force-reinstall {extra_requirement}\n"
            in result
        )

    def test_make_dockerfile_with_extra_packages(self):
        extra_package_basename = "custom_package"
        extra_package = f"./{extra_package_basename}"

        result = build.make_dockerfile(
            self.BASE_IMAGE,
            self.PACKAGE,
            self.WORKDIR,
            self.HOME,
            extra_packages=[extra_package],
        )

        assert f"FROM {self.BASE_IMAGE}\n" in result
        assert f"WORKDIR {self.WORKDIR}\n" in result
        assert f"ENV HOME={self.HOME}\n" in result
        assert 'COPY [".", "."]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert (
            f"RUN pip install --no-cache-dir --force-reinstall {extra_package}\n"
            in result
        )

    def test_make_dockerfile_with_extra_dirs(self):
        extra_dir = "./subdir"

        result = build.make_dockerfile(
            self.BASE_IMAGE,
            self.PACKAGE,
            self.WORKDIR,
            self.HOME,
            extra_dirs=[extra_dir],
        )

        assert f"FROM {self.BASE_IMAGE}\n" in result
        assert f"WORKDIR {self.WORKDIR}\n" in result
        assert f"ENV HOME={self.HOME}\n" in result
        assert 'COPY [".", "."]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert f'COPY ["{extra_dir}", "{extra_dir}"]\n' in result

    def test_make_dockerfile_with_exposed_ports(self):
        exposed_port = 8080

        result = build.make_dockerfile(
            self.BASE_IMAGE,
            self.PACKAGE,
            self.WORKDIR,
            self.HOME,
            exposed_ports=[exposed_port],
        )

        assert f"FROM {self.BASE_IMAGE}\n" in result
        assert f"WORKDIR {self.WORKDIR}\n" in result
        assert f"ENV HOME={self.HOME}\n" in result
        assert 'COPY [".", "."]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert f"EXPOSE {exposed_port}\n" in result

    def test_make_dockerfile_with_environment_variables(self):
        environment_variables = {
            "FAKE_ENV1": "FAKE_VALUE1",
            "FAKE_ENV2": "FAKE_VALUE2",
        }

        result = build.make_dockerfile(
            self.BASE_IMAGE,
            self.PACKAGE,
            self.WORKDIR,
            self.HOME,
            environment_variables=environment_variables,
        )

        assert f"FROM {self.BASE_IMAGE}\n" in result
        assert f"WORKDIR {self.WORKDIR}\n" in result
        assert f"ENV HOME={self.HOME}\n" in result
        assert 'COPY [".", "."]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert "ENV FAKE_ENV1=FAKE_VALUE1\n" in result
        assert "ENV FAKE_ENV2=FAKE_VALUE2\n" in result

    def test_build_image(self, make_dockerfile_mock, execute_command_mock):
        image = build.build_image(
            self.BASE_IMAGE, self.HOST_WORKDIR, self.OUTPUT_IMAGE_NAME
        )

        make_dockerfile_mock.assert_called_once_with(
            self.BASE_IMAGE,
            utils.Package(
                script=None,
                package_path=self.HOST_WORKDIR,
                python_module=None,
            ),
            utils.DEFAULT_WORKDIR,
            utils.DEFAULT_HOME,
            requirements_path=None,
            setup_path=None,
            extra_requirements=None,
            extra_packages=None,
            extra_dirs=None,
            exposed_ports=None,
            pip_command=self.PIP,
            python_command=self.PYTHON,
        )
        execute_command_mock.assert_called_once_with(
            [
                "docker",
                "build",
                "--no-cache",
                "-t",
                self.OUTPUT_IMAGE_NAME,
                "--rm",
                "-f-",
                self.HOST_WORKDIR,
            ],
            input_str=make_dockerfile_mock.return_value,
        )
        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_with_python_module(
        self, make_dockerfile_mock, execute_command_mock
    ):
        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.OUTPUT_IMAGE_NAME,
            python_module=self.PYTHON_MODULE,
        )

        make_dockerfile_mock.assert_called_once_with(
            self.BASE_IMAGE,
            utils.Package(
                script=None,
                package_path=self.HOST_WORKDIR,
                python_module=self.PYTHON_MODULE,
            ),
            utils.DEFAULT_WORKDIR,
            utils.DEFAULT_HOME,
            requirements_path=None,
            setup_path=None,
            extra_requirements=None,
            extra_packages=None,
            extra_dirs=None,
            exposed_ports=None,
            pip_command=self.PIP,
            python_command=self.PYTHON,
        )
        execute_command_mock.assert_called_once_with(
            [
                "docker",
                "build",
                "--no-cache",
                "-t",
                self.OUTPUT_IMAGE_NAME,
                "--rm",
                "-f-",
                self.HOST_WORKDIR,
            ],
            input_str=make_dockerfile_mock.return_value,
        )
        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_with_extra_requirements(
        self, make_dockerfile_mock, execute_command_mock
    ):
        extra_requirements = ["custom_package==1.0"]
        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.OUTPUT_IMAGE_NAME,
            extra_requirements=extra_requirements,
        )

        make_dockerfile_mock.assert_called_once_with(
            self.BASE_IMAGE,
            utils.Package(
                script=None,
                package_path=self.HOST_WORKDIR,
                python_module=None,
            ),
            utils.DEFAULT_WORKDIR,
            utils.DEFAULT_HOME,
            requirements_path=None,
            setup_path=None,
            extra_requirements=extra_requirements,
            extra_packages=None,
            extra_dirs=None,
            exposed_ports=None,
            pip_command=self.PIP,
            python_command=self.PYTHON,
        )
        execute_command_mock.assert_called_once_with(
            [
                "docker",
                "build",
                "--no-cache",
                "-t",
                self.OUTPUT_IMAGE_NAME,
                "--rm",
                "-f-",
                self.HOST_WORKDIR,
            ],
            input_str=make_dockerfile_mock.return_value,
        )
        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_with_requirements_path(
        self, tmp_path, make_dockerfile_mock, execute_command_mock
    ):
        source_dir = tmp_path / self.SOURCE_DIR
        source_dir.mkdir()
        host_workdir = tmp_path / self.HOST_WORKDIR
        host_workdir.mkdir()
        requirements_file = host_workdir / self.REQUIREMENTS_FILE
        requirements_file.write_text("")

        image = build.build_image(
            self.BASE_IMAGE,
            host_workdir.as_posix(),
            self.OUTPUT_IMAGE_NAME,
            requirements_path=requirements_file.as_posix(),
        )

        make_dockerfile_mock.assert_called_once_with(
            self.BASE_IMAGE,
            utils.Package(
                script=None,
                package_path=host_workdir.as_posix(),
                python_module=None,
            ),
            utils.DEFAULT_WORKDIR,
            utils.DEFAULT_HOME,
            requirements_path=self.REQUIREMENTS_FILE,
            setup_path=None,
            extra_requirements=None,
            extra_packages=None,
            extra_dirs=None,
            exposed_ports=None,
            pip_command=self.PIP,
            python_command=self.PYTHON,
        )
        execute_command_mock.assert_called_once_with(
            [
                "docker",
                "build",
                "--no-cache",
                "-t",
                self.OUTPUT_IMAGE_NAME,
                "--rm",
                "-f-",
                host_workdir.as_posix(),
            ],
            input_str=make_dockerfile_mock.return_value,
        )
        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_not_found_requirements_path(self, make_dockerfile_mock):
        requirements_path = f"./another_src/{self.REQUIREMENTS_FILE}"
        expected_message = f'The requirements_path "{requirements_path}" must exist.'

        with pytest.raises(ValueError) as exception:
            _ = build.build_image(
                self.BASE_IMAGE,
                self.HOST_WORKDIR,
                self.OUTPUT_IMAGE_NAME,
                requirements_path=requirements_path,
            )

        assert not make_dockerfile_mock.called
        assert str(exception.value) == expected_message

    def test_build_image_invalid_requirements_path(
        self, tmp_path, make_dockerfile_mock
    ):
        source_dir = tmp_path / self.SOURCE_DIR
        source_dir.mkdir()
        host_workdir = tmp_path / self.HOST_WORKDIR
        host_workdir.mkdir()
        another_dir = tmp_path / "another_dir"
        another_dir.mkdir()
        requirements_file = another_dir / self.REQUIREMENTS_FILE
        requirements_file.write_text("")
        expected_message = (
            f'The requirements_path "{requirements_file}" must be in "{host_workdir}".'
        )

        with pytest.raises(ValueError) as exception:
            _ = build.build_image(
                self.BASE_IMAGE,
                host_workdir.as_posix(),
                self.OUTPUT_IMAGE_NAME,
                requirements_path=requirements_file.as_posix(),
            )

        assert not make_dockerfile_mock.called
        assert str(exception.value) == expected_message

    def test_build_image_with_setup_path(
        self, tmp_path, make_dockerfile_mock, execute_command_mock
    ):
        source_dir = tmp_path / self.SOURCE_DIR
        source_dir.mkdir()
        host_workdir = tmp_path / self.HOST_WORKDIR
        host_workdir.mkdir()
        setup_file = host_workdir / self.SETUP_FILE
        setup_file.write_text("")

        image = build.build_image(
            self.BASE_IMAGE,
            host_workdir.as_posix(),
            self.OUTPUT_IMAGE_NAME,
            setup_path=setup_file.as_posix(),
        )

        make_dockerfile_mock.assert_called_once_with(
            self.BASE_IMAGE,
            utils.Package(
                script=None,
                package_path=host_workdir.as_posix(),
                python_module=None,
            ),
            utils.DEFAULT_WORKDIR,
            utils.DEFAULT_HOME,
            requirements_path=None,
            setup_path=self.SETUP_FILE,
            extra_requirements=None,
            extra_packages=None,
            extra_dirs=None,
            exposed_ports=None,
            pip_command=self.PIP,
            python_command=self.PYTHON,
        )
        execute_command_mock.assert_called_once_with(
            [
                "docker",
                "build",
                "--no-cache",
                "-t",
                self.OUTPUT_IMAGE_NAME,
                "--rm",
                "-f-",
                host_workdir.as_posix(),
            ],
            input_str=make_dockerfile_mock.return_value,
        )
        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_not_found_setup_path(self, make_dockerfile_mock):
        setup_path = f"./another_src/{self.SETUP_FILE}"
        expected_message = f'The setup_path "{setup_path}" must exist.'

        with pytest.raises(ValueError) as exception:
            _ = build.build_image(
                self.BASE_IMAGE,
                self.HOST_WORKDIR,
                self.OUTPUT_IMAGE_NAME,
                setup_path=setup_path,
            )

        assert not make_dockerfile_mock.called
        assert str(exception.value) == expected_message

    def test_build_image_invalid_setup_path(self, tmp_path, make_dockerfile_mock):
        source_dir = tmp_path / self.SOURCE_DIR
        source_dir.mkdir()
        host_workdir = tmp_path / self.HOST_WORKDIR
        host_workdir.mkdir()
        another_dir = tmp_path / "another_dir"
        another_dir.mkdir()
        setup_file = another_dir / self.SETUP_FILE
        setup_file.write_text("")
        expected_message = f'The setup_path "{setup_file}" must be in "{host_workdir}".'

        with pytest.raises(ValueError) as exception:
            _ = build.build_image(
                self.BASE_IMAGE,
                host_workdir.as_posix(),
                self.OUTPUT_IMAGE_NAME,
                setup_path=setup_file.as_posix(),
            )

        assert not make_dockerfile_mock.called
        assert str(exception.value) == expected_message

    def test_build_image_with_extra_packages(
        self, tmp_path, make_dockerfile_mock, execute_command_mock
    ):
        source_dir = tmp_path / self.SOURCE_DIR
        source_dir.mkdir()
        host_workdir = tmp_path / self.HOST_WORKDIR
        host_workdir.mkdir()
        extra_package = host_workdir / self.EXTRA_PACKAGE
        extra_package.write_text("")

        image = build.build_image(
            self.BASE_IMAGE,
            host_workdir.as_posix(),
            self.OUTPUT_IMAGE_NAME,
            extra_packages=[extra_package.as_posix()],
        )

        make_dockerfile_mock.assert_called_once_with(
            self.BASE_IMAGE,
            utils.Package(
                script=None,
                package_path=host_workdir.as_posix(),
                python_module=None,
            ),
            utils.DEFAULT_WORKDIR,
            utils.DEFAULT_HOME,
            requirements_path=None,
            setup_path=None,
            extra_requirements=None,
            extra_packages=[self.EXTRA_PACKAGE],
            extra_dirs=None,
            exposed_ports=None,
            pip_command=self.PIP,
            python_command=self.PYTHON,
        )
        execute_command_mock.assert_called_once_with(
            [
                "docker",
                "build",
                "--no-cache",
                "-t",
                self.OUTPUT_IMAGE_NAME,
                "--rm",
                "-f-",
                host_workdir.as_posix(),
            ],
            input_str=make_dockerfile_mock.return_value,
        )
        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_not_found_extra_packages(self, make_dockerfile_mock):
        extra_package = f"./another_src/{self.EXTRA_PACKAGE}"
        expected_message = f'The extra_packages "{extra_package}" must exist.'

        with pytest.raises(ValueError) as exception:
            _ = build.build_image(
                self.BASE_IMAGE,
                self.HOST_WORKDIR,
                self.OUTPUT_IMAGE_NAME,
                extra_packages=[extra_package],
            )

        assert not make_dockerfile_mock.called
        assert str(exception.value) == expected_message

    def test_build_image_invalid_extra_packages(
        self, tmp_path, make_dockerfile_mock, execute_command_mock
    ):
        source_dir = tmp_path / self.SOURCE_DIR
        source_dir.mkdir()
        host_workdir = tmp_path / self.HOST_WORKDIR
        host_workdir.mkdir()
        another_dir = tmp_path / "another_dir"
        another_dir.mkdir()
        extra_package = another_dir / self.EXTRA_PACKAGE
        extra_package.write_text("")
        expected_message = (
            f'The extra_packages "{extra_package}" must be in "{host_workdir}".'
        )

        with pytest.raises(ValueError) as exception:
            _ = build.build_image(
                self.BASE_IMAGE,
                host_workdir.as_posix(),
                self.OUTPUT_IMAGE_NAME,
                extra_packages=[extra_package.as_posix()],
            )

        assert not make_dockerfile_mock.called
        assert str(exception.value) == expected_message

    def test_build_image_with_container_workdir(
        self, make_dockerfile_mock, execute_command_mock
    ):
        container_workdir = "/custom_workdir"

        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.OUTPUT_IMAGE_NAME,
            container_workdir=container_workdir,
        )

        make_dockerfile_mock.assert_called_once_with(
            self.BASE_IMAGE,
            utils.Package(
                script=None,
                package_path=self.HOST_WORKDIR,
                python_module=None,
            ),
            container_workdir,
            utils.DEFAULT_HOME,
            requirements_path=None,
            setup_path=None,
            extra_requirements=None,
            extra_packages=None,
            extra_dirs=None,
            exposed_ports=None,
            pip_command=self.PIP,
            python_command=self.PYTHON,
        )
        execute_command_mock.assert_called_once_with(
            [
                "docker",
                "build",
                "--no-cache",
                "-t",
                self.OUTPUT_IMAGE_NAME,
                "--rm",
                "-f-",
                self.HOST_WORKDIR,
            ],
            input_str=make_dockerfile_mock.return_value,
        )
        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == container_workdir

    def test_build_image_with_container_home(
        self, make_dockerfile_mock, execute_command_mock
    ):
        container_home = "/custom_home"

        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.OUTPUT_IMAGE_NAME,
            container_home=container_home,
        )

        make_dockerfile_mock.assert_called_once_with(
            self.BASE_IMAGE,
            utils.Package(
                script=None,
                package_path=self.HOST_WORKDIR,
                python_module=None,
            ),
            utils.DEFAULT_WORKDIR,
            container_home,
            requirements_path=None,
            setup_path=None,
            extra_requirements=None,
            extra_packages=None,
            extra_dirs=None,
            exposed_ports=None,
            pip_command=self.PIP,
            python_command=self.PYTHON,
        )
        execute_command_mock.assert_called_once_with(
            [
                "docker",
                "build",
                "--no-cache",
                "-t",
                self.OUTPUT_IMAGE_NAME,
                "--rm",
                "-f-",
                self.HOST_WORKDIR,
            ],
            input_str=make_dockerfile_mock.return_value,
        )
        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == container_home
        assert image.default_workdir == self.WORKDIR

    def test_build_image_with_extra_dirs(
        self, make_dockerfile_mock, execute_command_mock
    ):
        extra_dirs = ["./another_src"]
        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.OUTPUT_IMAGE_NAME,
            extra_dirs=extra_dirs,
        )

        make_dockerfile_mock.assert_called_once_with(
            self.BASE_IMAGE,
            utils.Package(
                script=None,
                package_path=self.HOST_WORKDIR,
                python_module=None,
            ),
            utils.DEFAULT_WORKDIR,
            utils.DEFAULT_HOME,
            requirements_path=None,
            setup_path=None,
            extra_requirements=None,
            extra_packages=None,
            extra_dirs=extra_dirs,
            exposed_ports=None,
            pip_command=self.PIP,
            python_command=self.PYTHON,
        )
        execute_command_mock.assert_called_once_with(
            [
                "docker",
                "build",
                "--no-cache",
                "-t",
                self.OUTPUT_IMAGE_NAME,
                "--rm",
                "-f-",
                self.HOST_WORKDIR,
            ],
            input_str=make_dockerfile_mock.return_value,
        )
        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_with_exposed_ports(
        self, make_dockerfile_mock, execute_command_mock
    ):
        exposed_ports = [8080]
        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.OUTPUT_IMAGE_NAME,
            exposed_ports=exposed_ports,
        )

        make_dockerfile_mock.assert_called_once_with(
            self.BASE_IMAGE,
            utils.Package(
                script=None,
                package_path=self.HOST_WORKDIR,
                python_module=None,
            ),
            utils.DEFAULT_WORKDIR,
            utils.DEFAULT_HOME,
            requirements_path=None,
            setup_path=None,
            extra_requirements=None,
            extra_packages=None,
            extra_dirs=None,
            exposed_ports=exposed_ports,
            pip_command=self.PIP,
            python_command=self.PYTHON,
        )
        execute_command_mock.assert_called_once_with(
            [
                "docker",
                "build",
                "--no-cache",
                "-t",
                self.OUTPUT_IMAGE_NAME,
                "--rm",
                "-f-",
                self.HOST_WORKDIR,
            ],
            input_str=make_dockerfile_mock.return_value,
        )
        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_fail(
        self, make_dockerfile_mock, execute_command_return_code_1_mock
    ):
        command = [
            "docker",
            "build",
            "--no-cache",
            "-t",
            self.OUTPUT_IMAGE_NAME,
            "--rm",
            "-f-",
            self.HOST_WORKDIR,
        ]
        return_code = 1
        expected_message = textwrap.dedent(
            """
            Docker failed with error code {return_code}.
            Command: {command}
            """.format(
                return_code=return_code, command=" ".join(command)
            )
        )

        with pytest.raises(errors.DockerError) as exception:
            _ = build.build_image(
                self.BASE_IMAGE,
                self.HOST_WORKDIR,
                self.OUTPUT_IMAGE_NAME,
            )

        make_dockerfile_mock.assert_called_once_with(
            self.BASE_IMAGE,
            utils.Package(
                script=None,
                package_path=self.HOST_WORKDIR,
                python_module=None,
            ),
            utils.DEFAULT_WORKDIR,
            utils.DEFAULT_HOME,
            requirements_path=None,
            setup_path=None,
            extra_requirements=None,
            extra_packages=None,
            extra_dirs=None,
            exposed_ports=None,
            pip_command=self.PIP,
            python_command=self.PYTHON,
        )
        execute_command_return_code_1_mock.assert_called_once_with(
            command,
            input_str=make_dockerfile_mock.return_value,
        )
        assert exception.value.message == expected_message
        assert exception.value.cmd == command
        assert exception.value.exit_code == return_code


class TestLocalUtil:
    @mock.patch("subprocess.Popen", MockedPopen)
    def test_execute_command(self, textiowrapper_mock):
        return_code = local_util.execute_command(["ls"])

        assert return_code == 0

    @mock.patch("subprocess.Popen", MockedPopen)
    def test_execute_command_with_input_str(self, textiowrapper_mock):
        return_code = local_util.execute_command(["ls"], "Test string.")

        assert return_code == 0


class TestErrors:
    def test_raise_docker_error_with_command(self):
        command = ["ls", "-l"]
        return_code = 1
        expected_message = textwrap.dedent(
            """
            Docker failed with error code {return_code}.
            Command: {command}
            """.format(
                return_code=return_code, command=" ".join(command)
            )
        )

        with pytest.raises(errors.DockerError) as exception:
            errors.raise_docker_error_with_command(command, return_code)

        assert exception.value.message == expected_message
        assert exception.value.cmd == command
        assert exception.value.exit_code == return_code


class TestUtils:
    IMAGE_URI = "test_image:latest"

    def test_check_image_exists_locally(self, docker_client_mock):
        assert utils.check_image_exists_locally(self.IMAGE_URI) is True

    def test_check_image_exists_locally_image_not_found(
        self, docker_client_mock_image_get_not_found
    ):
        assert utils.check_image_exists_locally(self.IMAGE_URI) is False

    def test_check_image_exists_locally_image_api_error(
        self, docker_client_mock_image_get_api_error
    ):
        assert utils.check_image_exists_locally(self.IMAGE_URI) is False
