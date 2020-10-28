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

import datetime
import functools
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import Callable, Dict, Optional, Sequence


from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import datasets
from google.cloud.aiplatform import models
from google.cloud.aiplatform_v1beta1 import PipelineServiceClient
from google.cloud import storage


def _timestamped_copy_to_gcs(
    local_file_path: str,
    gcs_dir: str,
    project: Optional[str] = None,
    credentials: Optional[auth_credentials.Credentials] = None,
) -> str:
    """Copies a local file to a GCS path.

    The file copied to GCS is the name of the local file prepended with an
    "aiplatform-{timestamp}-" string.

    Args:
        local_file_path (str): Required. Local file to copy to GCS.
        gcs_dir (str):
            Required. The GCS directory to copy to.
        project (str):
            Project that contains the staging bucket. Default will be used if not
            provided. Model Builder callers should pass this in.
        credentials (auth_credentials.Credentials):
            Custom credentials to use with bucket. Model Builder callers should pass
            this in.
    Returns:
        gcs_path (str): The path of the copied file in gcs.
    """
    if gcs_dir.startswith("gs://"):
        gcs_dir = gcs_dir[5:]
    if gcs_dir.endswith("/"):
        gcs_dir = gcs_dir[:-1]

    gcs_parts = gcs_dir.split("/", 1)
    gcs_bucket = gcs_parts[0]
    gcs_blob_prefix = None if len(gcs_parts) == 1 else gcs_parts[1]

    local_file_name = pathlib.Path(local_file_path).name
    timestamp = datetime.datetime.now().isoformat(sep="-", timespec="milliseconds")
    blob_path = "-".join(["aiplatform", timestamp, local_file_name])

    if gcs_blob_prefix:
        blob_path = "/".join([gcs_blob_prefix, blob_path])

    # TODO(b/171202993) add user agent
    client = storage.Client(project=project, credentials=credentials)
    bucket = client.bucket(gcs_bucket)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_file_path)

    gcs_path = "".join(["gs://", "/".join([blob.bucket.name, blob.name])])
    return gcs_path


def _get_python_executable() -> str:
    """Returns Python executable.

    Raises:
        EnvironmentError if Python executable is not found.
    Returns:
        Python executable to use for setuptools packaging.
    """

    python_executable = sys.executable

    if not python_executable:
        raise EnvironmentError("Cannot find Python executable for packaging.")
    return python_executable


class _TrainingScriptPythonPackager:
    """Converts a Python script into Python package suitable for aiplatform training.

    Copies the script to specified location.

    Class Attributes:
        _TRAINER_FOLDER: Constant folder name to build package.
        _ROOT_MODULE: Constant root name of module.
        _TEST_MODULE_NAME: Constant name of module that will store script.
        _SETUP_PY_VERSION: Constant version of this created python package.
        _SETUP_PY_TEMPLATE: Constant template used to generate setup.py file.
        _SETUP_PY_SOURCE_DISTRIBUTION_CMD:
            Constant command to generate the source distribution package.

    Attributes:
        script_path: local path of script to package
        requirements: list of Python dependencies to add to package

    Usage:

    packager = TrainingScriptPythonPackager('my_script.py', ['pandas', 'pytorch'])
    gcs_path = packager.package_and_copy_to_gcs(
        gcs_staging_dir='my-bucket',
        project='my-prject')
    module_name = packager.module_name

    The package after installed can be executed as:
    python -m aiplatform_custom_trainer_script.task

    """

    _TRAINER_FOLDER = "trainer"
    _ROOT_MODULE = "aiplatform_custom_trainer_script"
    _TASK_MODULE_NAME = "task"
    _SETUP_PY_VERSION = "0.1"

    _SETUP_PY_TEMPLATE = """from setuptools import find_packages
from setuptools import setup

setup(
    name='{name}',
    version='{version}',
    packages=find_packages(),
    install_requires=({requirements}),
    include_package_data=True,
    description='My training application.'
)"""

    _SETUP_PY_SOURCE_DISTRIBUTION_CMD = (
        "{python_executable} setup.py sdist --formats=gztar"
    )

    def __init__(self, script_path: str, requirements: Optional[Sequence[str]] = None):
        """Initializes packager.

        Args:
            script_path (str): Required. Local path to script.
            requirements (Sequence[str]):
                List of python packages dependencies of script.
        """

        self.script_path = script_path
        self.requirements = requirements or []

    def make_package(self, package_directory: str) -> str:
        """Converts script into a Python package suitable for python module execution.

        Args:
            package_directory (str): Directory to build package in.
        Returns:
            source_distribution_path (str): Path to built package.
        Raises:
            RunTimeError if package creation fails.
        """
        # The root folder to builder the package in
        package_path = pathlib.Path(package_directory)

        # Root directory of the package
        trainer_root_path = package_path / self._TRAINER_FOLDER

        # The root module of the python package
        trainer_path = trainer_root_path / self._ROOT_MODULE

        # __init__.py path in root module
        init_path = trainer_path / "__init__.py"

        # The module that will contain the script
        script_out_path = trainer_path / f"{self._TASK_MODULE_NAME}.py"

        # The path to setup.py in the package.
        setup_py_path = trainer_root_path / "setup.py"

        # The path to the generated source distribution.
        source_distribution_path = (
            trainer_root_path
            / "dist"
            / f"{self._ROOT_MODULE}-{self._SETUP_PY_VERSION}.tar.gz"
        )

        trainer_root_path.mkdir()
        trainer_path.mkdir()

        # Make empty __init__.py
        with init_path.open("w"):
            pass

        # Format the setup.py file.
        setup_py_output = self._SETUP_PY_TEMPLATE.format(
            name=self._ROOT_MODULE,
            requirements=",".join(f'"{r}"' for r in self.requirements),
            version=self._SETUP_PY_VERSION,
        )

        # Write setup.py
        with setup_py_path.open("w") as fp:
            fp.write(setup_py_output)

        # Copy script as module of python package.
        shutil.copy(self.script_path, script_out_path)

        # Run setup.py to create the source distribution.
        setup_cmd = self._SETUP_PY_SOURCE_DISTRIBUTION_CMD.format(
            python_executable=_get_python_executable()
        ).split()

        p = subprocess.Popen(
            setup_cmd,
            cwd=trainer_root_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = p.communicate()

        # Raise informative error if packaging fails.
        if p.returncode != 0:
            raise RuntimeError(
                "Packaging of training script failed with code %d\n%s \n%s"
                % (p.returncode, output.decode(), error.decode())
            )

        return str(source_distribution_path)

    def package_and_copy(self, copy_method: Callable[[str], str]) -> str:
        """Packages the script and executes copy with given copy_method.

        Args:
            copy_method Callable[[str], str]
                Takes a string path, copies to a desired location, and returns the
                output path location.
        Returns:
            output_path str: Location of copied package.
        """

        with tempfile.TemporaryDirectory() as tmpdirname:
            source_distribution_path = self.make_package(tmpdirname)
            return copy_method(source_distribution_path)

    def package_and_copy_to_gcs(
        self,
        gcs_staging_dir: str,
        project: str = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> str:
        """Packages script in Python package and copies package to GCS bucket.

        Args
            gcs_staging_dir (str): Required. GCS Staging directory.
            project (str): Required. Project where GCS Staging bucket is located.
            credentials (auth_credentials.Credentials):
                Optional credentials used with GCS client.
        Returns:
            GCS location of Python package.
        """

        copy_method = functools.partial(
            _timestamped_copy_to_gcs,
            gcs_dir=gcs_staging_dir,
            project=project,
            credentials=credentials,
        )
        return self.package_and_copy(copy_method=copy_method)

    @property
    def module_name(self) -> str:
        """Module name that can be executed during training. ie. python -m"""
        return f"{self._ROOT_MODULE}.{self._TASK_MODULE_NAME}"


class TrainingJob(base.AiPlatformResourceNoun):

    client_class = PipelineServiceClient
    _is_client_prediction_client = False

    def __init__(
        self,
        display_name: str,
        script_path: str,
        container_uri: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        staging_bucket: Optional[str] = None,
    ):
        pass

    def run(
        self,
        dataset: Optional[datasets.Dataset],
        output_dir: Optional[str] = None,
        args: Optional[Dict[str, str]] = None,
        replica_count=0,
        machine_type="n1-standard-4",
        accelerator_type=None,
        accelerator_count=0,
        spec_yaml_path: Optional[str] = None,
    ) -> models.Model:
        pass


class CustomTrainingJob(TrainingJob):
    pass


class AutoMLTablesTrainingJob(TrainingJob):
    pass
