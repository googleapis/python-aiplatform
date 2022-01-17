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
import pytest
from unittest import mock

from google.cloud.aiplatform.docker_utils import build
from google.cloud.aiplatform.docker_utils import local_util
from google.cloud.aiplatform.docker_utils import utils


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
