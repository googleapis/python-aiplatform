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
import os
import shutil
import subprocess
import time
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
    staging_bucket: str,
    project: Optional[str] = None,
    credentials: Optional[auth_credentials.Credentials] = None,
) -> str:
    """Copies a local file to a GCS bucket.

    The file copied to GCS is the name of the local file prepended with an
    "aiplatform-{timestamp}-" string.

    Args:
        local_file_path (str): Required. Local file to copy to GCS.
        staging_bucket (str):
            Required. The staging bucket to copy to. (should not include gs://)
        project (str):
            Project that containers the staging bucket. Default will be used if not
            provided. Model Builder callers should pass this in.
        credentials (auth_credentials.Credentials):
            Custom credentials to use with bucket. Model Builder callers should pass
            this in.
    Returns:
        gcs_path (str): The path of the copied file in gcs.
    """

    local_file_name = os.path.basename(local_file_path)

    timestamp = datetime.datetime.now().isoformat(sep="-", timespec="milliseconds")
    blob_path = "-".join(["aiplatform", timestamp, local_file_name])

    # TODO(b/171202993) add user agent
    client = storage.Client(project=project, credentials=credentials)
    bucket = client.bucket(staging_bucket)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_file_path)

    gcs_path = "".join(["gs://", "/".join([blob.bucket.name, blob.name])])
    return gcs_path


def _get_python3_alias():
    """Finds Python 3 alias which is used to execute setuptools packaging.

    Raises:
        RunTimeError if Python 3 alias is not found.
    Returns:
        Python 3 command alias to use for setuptools packaging.
    """

    def is_python3(python_cmd):
        try:
            check_python = subprocess.check_output([python_cmd, "--version"]).decode()
        except FileNotFoundError:
            return False
        return check_python.startswith("Python 3")

    python_cmd = "python"
    if is_python3(python_cmd):
        return python_cmd

    python_cmd = "python3"
    if is_python3(python_cmd):
        return python_cmd

    raise EnvironmentError(
        "Cannot find Python 3 alias for packaging."
        'Please alias Python 3 to "python" or "python3".'
    )


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
        staging_bucket='my-bucket',
        project='my-prject')
    module_name = packager.module_name

    The package after installed can be executed as:
    python -m trainer.task

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

    _SETUP_PY_SOURCE_DISTRIBUTION_CMD = "{python3} setup.py sdist --formats=gztar"

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
        trainer_root_path = os.path.join(package_directory, self._TRAINER_FOLDER)

        # The root module of the python package
        trainer_path = os.path.join(trainer_root_path, self._ROOT_MODULE)

        # __init__.py path in root module
        init_path = os.path.join(trainer_path, "__init__.py")

        # The module that will contain the script
        script_out_path = os.path.join(trainer_path, f"{self._TASK_MODULE_NAME}.py")

        # The path to setup.py in the package.
        setup_py_path = os.path.join(trainer_root_path, "setup.py")

        # The path to the generated source distribution.
        source_distribution_path = os.path.join(
            trainer_root_path,
            "dist",
            f"{self._ROOT_MODULE}-{self._SETUP_PY_VERSION}.tar.gz",
        )

        # Make required dirs
        os.mkdir(trainer_root_path)
        os.mkdir(trainer_path)

        # Make empty __init__.py
        with open(init_path, "w") as fp:
            pass

        # Format the setup.py file.
        setup_py_output = self._SETUP_PY_TEMPLATE.format(
            name=self._ROOT_MODULE,
            requirements=",".join(f'"{r}"' for r in self.requirements),
            version=self._SETUP_PY_VERSION,
        )

        # Write setup.py
        with open(setup_py_path, "w") as fp:
            fp.write(setup_py_output)

        # Copy script as module of python package.
        shutil.copy(self.script_path, script_out_path)

        # Run setup.py to create the source distribution.
        setup_cmd = self._SETUP_PY_SOURCE_DISTRIBUTION_CMD.format(
            python3=_get_python3_alias()
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

        return source_distribution_path

    def package_and_copy(self, copy_method: Callable[[str], str]) -> str:
        """Packages the script and executes copy with given copy_method.

        Args:
            copy_method Callable[[str], str]
                Takes a string path, copies to a desired location, and returns the
                output path location.
        Returns:
            output_path str: Location of copied package.
        """

        script_name = os.path.basename(self.script_path)

        with tempfile.TemporaryDirectory() as tmpdirname:
            source_distribution_path = self.make_package(tmpdirname)
            return copy_method(source_distribution_path)

    def package_and_copy_to_gcs(
        self,
        staging_bucket: str,
        project: str = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> str:
        """Packages script in Python package and copies package to GCS bucket.

        Args
            staging_bucket (str): Required. GCS Staging bucket. Should not contain gs://
            project (str): Required. Project where GCS Staging bucket is located.
            credentials (auth_credentials.Credentials):
                Optional credentials used with GCS client.
        Returns:
            GCS location of Python package.
        """

        copy_method = functools.partial(
            _timestamped_copy_to_gcs,
            staging_bucket=staging_bucket,
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
