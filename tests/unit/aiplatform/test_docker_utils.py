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
from unittest import mock

from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.docker_utils import build
from google.cloud.aiplatform.docker_utils import local_util
from google.cloud.aiplatform.docker_utils import run
from google.cloud.aiplatform.docker_utils import utils


_TEST_CONTAINER_LOGS = b"line1\nline2\nline3\n"
_TEST_CONTAINER_LOGS_LEN = 3


@pytest.fixture
def execute_command_mock():
    with mock.patch.object(local_util, "execute_command") as execute_command_mock:
        execute_command_mock.return_value = 0
        yield execute_command_mock


class MockedPopen:
    def __init__(self, args, **kwargs):
        self.args = args
        self.returncode = 0
        self.stdin = mock.Mock()
        self.stdout = mock.Mock()

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
def docker_client_mock():
    with mock.patch("docker.from_env") as from_env_mock:
        client = from_env_mock.return_value
        client().containers.run.return_value = None
        yield client


@pytest.fixture
def docker_container_mock():
    container = mock.MagicMock()
    container.logs.return_value = _TEST_CONTAINER_LOGS
    return container


class TestBuild:
    BASE_IMAGE = "python:3.7"
    HOST_WORKDIR_BASENAME = "user_code"
    HOST_WORKDIR = f"./src/{HOST_WORKDIR_BASENAME}"
    HOME = build._DEFAULT_HOME
    WORKDIR = build._DEFAULT_WORKDIR
    SCRIPT = "./user_code/entrypoint.py"
    MAIN_SCRIPT = f"{HOST_WORKDIR}/entrypoint.py"
    PACKAGE = utils.Package(
        script=SCRIPT, package_path=HOST_WORKDIR, python_module=None
    )
    OUTPUT_IMAGE_NAME = "test_image:latest"

    def test_make_dockerfile(self):
        result = build.make_dockerfile(
            self.BASE_IMAGE, self.PACKAGE, self.WORKDIR, self.HOME
        )

        assert f"FROM {self.BASE_IMAGE}\n" in result
        assert f"WORKDIR {self.WORKDIR}\n" in result
        assert f"ENV HOME={self.HOME}\n" in result
        assert f'COPY [".", "{self.HOST_WORKDIR_BASENAME}"]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result

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
        assert f'COPY [".", "{self.HOST_WORKDIR_BASENAME}"]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert f'COPY ["{requirements_path}", "./requirements.txt"]\n' in result
        assert "RUN pip install --no-cache-dir -r ./requirements.txt\n" in result

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
        assert f'COPY [".", "{self.HOST_WORKDIR_BASENAME}"]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert f'COPY ["{setup_path}", "./setup.py"]\n' in result
        assert "RUN pip install --no-cache-dir .\n" in result

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
        assert f'COPY [".", "{self.HOST_WORKDIR_BASENAME}"]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert (
            f"RUN pip install --no-cache-dir --upgrade {extra_requirement}\n" in result
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
        assert f'COPY [".", "{self.HOST_WORKDIR_BASENAME}"]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert f'COPY ["{extra_package}", "{extra_package_basename}"]\n'
        assert f"RUN pip install --no-cache-dir {extra_package_basename}\n" in result

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
        assert f'COPY [".", "{self.HOST_WORKDIR_BASENAME}"]\n' in result
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
        assert f'COPY [".", "{self.HOST_WORKDIR_BASENAME}"]\n' in result
        assert f'ENTRYPOINT ["python", "{self.SCRIPT}"]' in result
        assert f"EXPOSE {exposed_port}\n" in result

    def test_build_image(self, execute_command_mock):
        image = build.build_image(
            self.BASE_IMAGE, self.HOST_WORKDIR, self.MAIN_SCRIPT, self.OUTPUT_IMAGE_NAME
        )

        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_with_python_module(self, execute_command_mock):
        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.MAIN_SCRIPT,
            self.OUTPUT_IMAGE_NAME,
            python_module="custom.python.module",
        )

        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_with_requirements(self, execute_command_mock):
        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.MAIN_SCRIPT,
            self.OUTPUT_IMAGE_NAME,
            requirements=["custom_package==1.0"],
        )

        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_with_requirements_path(self, execute_command_mock):
        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.MAIN_SCRIPT,
            self.OUTPUT_IMAGE_NAME,
            requirements_path=f"{self.HOST_WORKDIR}/requirements.txt",
        )

        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_invalid_requirements_path(self):
        requirements_path = "./another_src/requirements.txt"
        expected_message = f'The requirements_path "{requirements_path}" must be in "{self.HOST_WORKDIR}".'

        with pytest.raises(ValueError) as exception:
            _ = build.build_image(
                self.BASE_IMAGE,
                self.HOST_WORKDIR,
                self.MAIN_SCRIPT,
                self.OUTPUT_IMAGE_NAME,
                requirements_path=requirements_path,
            )

        assert str(exception.value) == expected_message

    def test_build_image_with_setup_path(self, execute_command_mock):
        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.MAIN_SCRIPT,
            self.OUTPUT_IMAGE_NAME,
            setup_path=f"{self.HOST_WORKDIR}/setup.py",
        )

        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_invalid_setup_path(self):
        setup_path = "./another_src/setup.py"
        expected_message = (
            f'The setup_path "{setup_path}" must be in "{self.HOST_WORKDIR}".'
        )

        with pytest.raises(ValueError) as exception:
            _ = build.build_image(
                self.BASE_IMAGE,
                self.HOST_WORKDIR,
                self.MAIN_SCRIPT,
                self.OUTPUT_IMAGE_NAME,
                setup_path=setup_path,
            )

        assert str(exception.value) == expected_message

    def test_build_image_with_extra_packages(self, execute_command_mock):
        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.MAIN_SCRIPT,
            self.OUTPUT_IMAGE_NAME,
            extra_packages=["./another_src/custom_package"],
        )

        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_with_container_workdir(self, execute_command_mock):
        container_workdir = "/custom_workdir"

        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.MAIN_SCRIPT,
            self.OUTPUT_IMAGE_NAME,
            container_workdir=container_workdir,
        )

        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == container_workdir

    def test_build_image_with_container_home(self, execute_command_mock):
        container_home = "/custom_home"

        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.MAIN_SCRIPT,
            self.OUTPUT_IMAGE_NAME,
            container_home=container_home,
        )

        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == container_home
        assert image.default_workdir == self.WORKDIR

    def test_build_image_with_extra_dirs(self, execute_command_mock):
        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.MAIN_SCRIPT,
            self.OUTPUT_IMAGE_NAME,
            extra_dirs=["./another_src"],
        )

        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR

    def test_build_image_with_exposed_ports(self, execute_command_mock):
        image = build.build_image(
            self.BASE_IMAGE,
            self.HOST_WORKDIR,
            self.MAIN_SCRIPT,
            self.OUTPUT_IMAGE_NAME,
            exposed_ports=[8080],
        )

        assert image.name == self.OUTPUT_IMAGE_NAME
        assert image.default_home == self.HOME
        assert image.default_workdir == self.WORKDIR


class TestLocalUtil:
    @mock.patch("subprocess.Popen", MockedPopen)
    def test_execute_command(self, textiowrapper_mock):
        return_code = local_util.execute_command(["ls"])

        assert return_code == 0

    @mock.patch("subprocess.Popen", MockedPopen)
    def test_execute_command_with_input_str(self, textiowrapper_mock):
        return_code = local_util.execute_command(["ls"], "Test string.")

        assert return_code == 0


class TestRun:
    IMAGE_URI = "test_image:latest"

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_run_prediction_container(self, docker_client_mock):
        run.run_prediction_container(self.IMAGE_URI)

        docker_client_mock.containers.run.assert_called_once_with(
            self.IMAGE_URI,
            command=None,
            ports={prediction.DEFAULT_AIP_HTTP_PORT: None},
            environment={
                prediction.AIP_HTTP_PORT: prediction.DEFAULT_AIP_HTTP_PORT,
                prediction.AIP_HEALTH_ROUTE: None,
                prediction.AIP_PREDICT_ROUTE: None,
                prediction.AIP_STORAGE_URI: None,
                run._ADC_ENVIRONMENT_VARIABLE: run._DEFAULT_CONTAINER_CRED_KEY_PATH,
            },
            volumes=[],
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
            command=serving_container_command + serving_container_args,
            ports={serving_container_ports[0]: host_port},
            environment=environment,
            volumes=volumes,
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
            ports={prediction.DEFAULT_AIP_HTTP_PORT: None},
            environment={
                prediction.AIP_HTTP_PORT: prediction.DEFAULT_AIP_HTTP_PORT,
                prediction.AIP_HEALTH_ROUTE: None,
                prediction.AIP_PREDICT_ROUTE: None,
                prediction.AIP_STORAGE_URI: None,
                run._ADC_ENVIRONMENT_VARIABLE: run._DEFAULT_CONTAINER_CRED_KEY_PATH,
            },
            volumes=volumes,
            detach=True,
        )

    def test_run_prediction_container_artifact_uri_is_not_gcs(self, docker_client_mock):
        artifact_uri = "./models"
        expected_message = (
            f'artifact_uri must be a GCS path but it is "{artifact_uri}".'
        )

        with pytest.raises(ValueError) as exception:
            run.run_prediction_container(self.IMAGE_URI, artifact_uri=artifact_uri)

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
