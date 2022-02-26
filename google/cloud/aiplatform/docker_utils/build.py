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

import json
import logging
import os
from pathlib import Path
import textwrap
from typing import List, Optional

from six.moves import shlex_quote

from google.cloud.aiplatform.docker_utils import local_util
from google.cloud.aiplatform.docker_utils.errors import DockerError
from google.cloud.aiplatform.docker_utils.utils import Image, Package
from google.cloud.aiplatform.utils import path_utils

_DEFAULT_HOME = "/home"
_DEFAULT_WORKDIR = "/usr/app"

_logger = logging.getLogger(__name__)


def _generate_copy_command(from_path: str, to_path: str, comment: Optional[str] = None):
    """Returns a Dockerfile entry that copies a file from host to container.

    Args:
        from_path (str):
            Required. The path of the source in host.
        to_path (str):
            Required. The path to the destination in the container.
        comment (str):
            Optional. A comment explaining the copy operation.
    """
    cmd = "COPY {}\n".format(json.dumps([from_path, to_path]))

    if comment is not None:
        formatted_comment = "\n# ".join(comment.split("\n"))
        return textwrap.dedent(
            """
            # {}
            {}
            """.format(
                formatted_comment, cmd,
            )
        )

    return cmd


def _prepare_dependency_entries(
    setup_path: Optional[str] = None,
    requirements_path: Optional[str] = None,
    extra_packages: Optional[List[str]] = None,
    extra_requirements: Optional[List[str]] = None,
    extra_dirs: Optional[List[str]] = None,
    pip_command: str = "pip",
):
    """Returns the Dockerfile entries required to install dependencies.

    Args:
        setup_path (str):
            Optional. The path that points to a setup.py.
        requirements_path (str):
            Optional. The path that points to a requirements.txt file.
        extra_packages (List[str]):
            Optional. The list of user custom dependency packages to install.
        extra_requirements (List[str]):
            Optional. The list of required dependencies to be installed from remote resource archives.
        extra_dirs (List[str]):
            Optional. The directories other than the work_dir required.
        pip_command (str):
            Required. The pip command used for install packages.
    """
    ret = ""

    if setup_path is not None:
        ret += _generate_copy_command(
            setup_path,
            "./setup.py",
            comment="setup.py file specified, thus copy it to the docker container.",
        ) + textwrap.dedent(
            """
            RUN {} install --no-cache-dir .
            """.format(
                pip_command,
            )
        )

    if requirements_path is not None:
        ret += _generate_copy_command(
            requirements_path,
            "./requirements.txt",
            comment="requirements.txt file specified, thus copy it to the docker container.",
        ) + textwrap.dedent(
            """
            RUN {} install --no-cache-dir -r ./requirements.txt
            """.format(
                pip_command,
            )
        )

    if extra_packages is not None:
        for extra in extra_packages:
            package_name = os.path.basename(extra)
            ret += textwrap.dedent(
                """
                {}
                RUN {} install --no-cache-dir {}
                """.format(
                    _generate_copy_command(extra, package_name),
                    pip_command,
                    shlex_quote(package_name),
                )
            )

    if extra_requirements is not None:
        for requirement in extra_requirements:
            ret += textwrap.dedent(
                """
                RUN {} install --no-cache-dir --upgrade {}
                """.format(
                    pip_command, shlex_quote(requirement)
                )
            )

    if extra_dirs is not None:
        for directory in extra_dirs:
            ret += "\n{}\n".format(_generate_copy_command(directory, directory))

    return ret


def _prepare_entrypoint(package: Package, python_command: str = "python"):
    """Generates dockerfile entry to set the container entrypoint.

    Args:
        package (Package):
            Required. The main application copied to the container.
        python_command (str):
            Required. The python command used for running python code.

    Returns:
        A string with Dockerfile directives to set ENTRYPOINT.
    """

    # Needs to use json so that quotes print as double quotes, not single quotes.
    if package.python_module is not None:
        exec_str = json.dumps([python_command, "-m", package.python_module])
    else:
        _, ext = os.path.splitext(package.script)
        executable = [python_command] if ext == ".py" else ["/bin/bash"]
        exec_str = json.dumps(executable + [package.script])

    return "\nENTRYPOINT {}".format(exec_str)


def _prepare_package_entry(package: Package):
    """Returns the Dockerfile entries required to append at the end before entrypoint.

    Including:
    - copy the parent directory of the main executable into a docker container.
    - inject an entrypoint that executes a script or python module inside that
      directory.

    Args:
        package (Package):
            Required. The main application copied to and run in the container.
    """
    copy_code = _generate_copy_command(
        ".",  # Dockefile context location has been changed to host_workdir
        Path(package.package_path).name,
        comment="Copy the source directory into the docker container.",
    )

    return "\n{}\n".format(copy_code)


def _prepare_exposed_ports(exposed_ports: Optional[List[int]] = None):
    """Returns the Dockerfile entries required to expose ports in containers.

    Args:
        exposed_ports (List[int]):
            Optional. The exposed ports that the container listens on at runtime.
    """
    ret = ""

    if exposed_ports is None:
        return ret

    for port in exposed_ports:
        ret += "EXPOSE {}".format(port)
    return ret


def make_dockerfile(
    base_image: str,
    main_package: Package,
    container_workdir: str,
    container_home: str,
    requirements_path: Optional[str] = None,
    setup_path: Optional[str] = None,
    extra_requirements: Optional[List[str]] = None,
    extra_packages: Optional[List[str]] = None,
    extra_dirs: Optional[List[str]] = None,
    exposed_ports: Optional[List[int]] = None,
    pip_command: str = "pip",
    python_command: str = "python",
) -> str:
    """Generates a Dockerfile for building an image.

    It builds on a specified base image to create a container that:
    - installs any dependency specified in a requirements.txt or a setup.py file,
    and any specified dependency packages existing locally or found from PyPI
    - copies all source needed by the main module, and potentially injects an
    entrypoint that, on run, will run that main module

    Args:
        base_image (str):
            Required. The ID or name of the base image to initialize the build stage.
        main_package (Package):
            Required. The main application to execute.
        container_workdir (str):
            Required. The working directory in the container.
        container_home (str):
            Required. The $HOME directory in the container.
        requirements_path (str):
            Optional. The path to a local requirements.txt file.
        setup_path (str):
            Optional. The path to a local setup.py file.
        extra_requirements (List[str]):
            Optional. The list of required dependencies to install from PyPI.
        extra_packages (List[str]):
            Optional. The list of user custom dependency packages to install.
        extra_dirs: (List[str]):
            Optional. The directories other than the work_dir required to be in the container.
        exposed_ports (List[int]):
            Optional. The exposed ports that the container listens on at runtime.
        pip_command (str):
            Required. The pip command used for install packages.
        python_command (str):
            Required. The python command used for running python code.

    Returns:
        A string that represents the content of a Dockerfile.
    """
    dockerfile = textwrap.dedent(
        """
        FROM {base_image}

        # The directory is created by root. This sets permissions so that any user can
        # access the folder.
        RUN mkdir -m 777 -p {workdir} {container_home}
        WORKDIR {workdir}
        ENV HOME={container_home}

        # Keeps Python from generating .pyc files in the container
        ENV PYTHONDONTWRITEBYTECODE=1
        """.format(
            base_image=base_image,
            workdir=shlex_quote(container_workdir),
            container_home=shlex_quote(container_home),
        )
    )

    dockerfile += _prepare_package_entry(main_package)

    dockerfile += _prepare_dependency_entries(
        requirements_path=requirements_path,
        setup_path=setup_path,
        extra_requirements=extra_requirements,
        extra_packages=extra_packages,
        extra_dirs=extra_dirs,
        pip_command=pip_command,
    )

    dockerfile += _prepare_exposed_ports(exposed_ports)
    dockerfile += _prepare_entrypoint(main_package, python_command=python_command)

    return dockerfile


def build_image(
    base_image: str,
    host_workdir: str,
    main_script: str,
    output_image_name: str,
    python_module: Optional[str] = None,
    requirements: Optional[List[str]] = None,
    requirements_path: Optional[str] = None,
    setup_path: Optional[str] = None,
    extra_packages: Optional[List[str]] = None,
    container_workdir: Optional[str] = None,
    container_home: Optional[str] = None,
    extra_dirs: Optional[List[str]] = None,
    exposed_ports: Optional[List[int]] = None,
    pip_command: str = "pip",
    python_command: str = "python",
    no_cache: bool = True,
    **kwargs,
) -> Image:
    """Builds a Docker image.

    Generates a Dockerfile and passes it to `docker build` via stdin.
    All output from the `docker build` process prints to stdout.

    Args:
        base_image (str):
            Required. The ID or name of the base image to initialize the build stage.
        host_workdir (str):
            Required. The path indicating where all the required sources locates.
        main_script (str):
            Required. The string that identifies the executable script under the working
            directory.
        output_image_name (str):
            Required. The name of the built image.
        python_module (str):
            Optional. The executable main script in form of a python module, if applicable.
        requirements (List[str]):
            Optional. The list of required dependencies to install from PyPI.
        requirements_path (str):
            Optional. The path to a local file including required dependencies to install from PyPI.
        setup_path (str):
            Optional. The path to a local setup.py used for installing packages.
        extra_packages (List[str]):
            Optional. The list of user custom dependency packages to install.
        container_workdir (str):
            Optional. The working directory in the container.
        container_home (str):
            Optional. The $HOME directory in the container.
        extra_dirs (List[str]):
            Optional. The directories other than the work_dir required.
        exposed_ports (List[int]):
            Optional. The exposed ports that the container listens on at runtime.
        pip_command (str):
            Required. The pip command used for installing packages.
        python_command (str):
            Required. The python command used for running python scripts.
        no_cache (bool):
            Required. Do not use cache when building the image.
        **kwargs:
            Other arguments to pass to underlying method that generates the Dockerfile.

    Returns:
        A Image class that contains info of the built image.

    Raises:
        DockerError: An error occurred when executing `docker build`
    """

    tag_options = ["-t", output_image_name]
    cache_args = ["--no-cache"] if no_cache else []

    command = (
        ["docker", "build"] + cache_args + tag_options + ["--rm", "-f-", host_workdir]
    )

    requirements_relative_path = None
    if requirements_path is not None:
        if not path_utils._is_relative_to(requirements_path, host_workdir):
            raise ValueError(
                f'The requirements_path "{requirements_path}" must be in "{host_workdir}".'
            )
        requirements_relative_path = (
            Path(requirements_path).relative_to(host_workdir).as_posix()
        )

    setup_relative_path = None
    if setup_path is not None:
        if not path_utils._is_relative_to(setup_path, host_workdir):
            raise ValueError(
                f'The setup_path "{setup_path}" must be in "{host_workdir}".'
            )
        setup_relative_path = Path(setup_path).relative_to(host_workdir).as_posix()

    home_dir = container_home or _DEFAULT_HOME
    work_dir = container_workdir or _DEFAULT_WORKDIR

    # The package will be used in Docker, thus norm it to POSIX path format.
    main_package = Package(
        script=Path(main_script).relative_to(Path(host_workdir).parent).as_posix(),
        package_path=host_workdir,
        python_module=python_module,
    )

    dockerfile = make_dockerfile(
        base_image,
        main_package,
        work_dir,
        home_dir,
        requirements_path=requirements_relative_path,
        setup_path=setup_relative_path,
        extra_requirements=requirements,
        extra_packages=extra_packages,
        extra_dirs=extra_dirs,
        exposed_ports=exposed_ports,
        pip_command=pip_command,
        python_command=python_command,
        **kwargs,
    )

    joined_command = " ".join(command)
    _logger.info("Running command: {}".format(joined_command))

    return_code = local_util.execute_command(command, input_str=dockerfile)
    if return_code == 0:
        return Image(output_image_name, home_dir, work_dir)
    else:
        error_msg = textwrap.dedent(
            """
            Docker failed with error code {code}.
            Command: {cmd}
            """.format(
                code=return_code, cmd=joined_command
            )
        )
        raise DockerError(error_msg, command, return_code)
