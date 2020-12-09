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
import logging
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Callable, Dict, List, Optional, NamedTuple, Sequence, Union

import abc

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import datasets
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform import schema
from google.cloud.aiplatform import utils
from google.cloud.aiplatform_v1beta1.services.pipeline_service import (
    client as pipeline_service_client,
)
from google.cloud.aiplatform_v1beta1.types import (
    accelerator_type as gca_accelerator_type,
)
from google.cloud.aiplatform_v1beta1.types import io as gca_io
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types import pipeline_state as gca_pipeline_state
from google.cloud.aiplatform_v1beta1.types import (
    training_pipeline as gca_training_pipeline,
)

from google.cloud import storage
from google.protobuf import json_format
from google.protobuf import struct_pb2
from google.rpc import code_pb2

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
_LOGGER = logging.getLogger(__name__)

_PIPELINE_COMPLETE_STATES = set(
    [
        gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
        gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED,
        gca_pipeline_state.PipelineState.PIPELINE_STATE_CANCELLED,
        gca_pipeline_state.PipelineState.PIPELINE_STATE_PAUSED,
    ]
)


class _TrainingJob(base.AiPlatformResourceNounWithFutureManager):
    client_class = pipeline_service_client.PipelineServiceClient
    _is_client_prediction_client = False

    def __init__(
        self,
        display_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Constructs a Training Job.

        Args:
            display_name (str):
                Required. The user-defined name of this TrainingPipeline.
            project (str):
                Optional project to retrieve model from. If not set, project set in
                aiplatform.init will be used.
            location (str):
                Optional location to retrieve model from. If not set, location set in
                aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional credentials to use to retrieve the model.
        """
        utils.validate_display_name(display_name)

        super().__init__(project=project, location=location, credentials=credentials)
        self._display_name = display_name
        self._project = project
        self._gca_resource = None

    @property
    @abc.abstractmethod
    def _model_upload_fail_string(self) -> str:
        """Helper property for model upload failure."""

        pass

    @abc.abstractmethod
    def run(self) -> Optional[models.Model]:
        """Runs the training job. Should call _run_job internally"""
        pass

    @staticmethod
    def _create_input_data_config(
        dataset: Optional[datasets.Dataset] = None,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        predefined_split_column_name: Optional[str] = None,
        gcs_destination_uri_prefix: Optional[str] = None,
    ) -> Optional[gca_training_pipeline.InputDataConfig]:
        """Constructs a input data config to pass to the training pipeline.

        Args:
            training_fraction_split (float):
                The fraction of the input data that is to be
                used to train the Model. This is ignored if Dataset is not provided.
            training_fraction_split (float):
                The fraction of the input data that is to be
                used to train the Model. This is ignored if Dataset is not provided.
            validation_fraction_split (float):
                The fraction of the input data that is to be
                used to validate the Model. This is ignored if Dataset is not provided.
            test_fraction_split (float):
                The fraction of the input data that is to be
                used to evaluate the Model. This is ignored if Dataset is not provided.
            predefined_split_column_name (str):
                Optional. The key is a name of one of the Dataset's data
                columns. The value of the key (either the label's value or
                value in the column) must be one of {``training``,
                ``validation``, ``test``}, and it defines to which set the
                given piece of data is assigned. If for a piece of data the
                key is not present or has an invalid value, that piece is
                ignored by the pipeline.

                Supported only for tabular Datasets.
            gcs_destination_uri_prefix (str):
                Optional. The Google Cloud Storage location.

                The AI Platform environment variables representing Google
                Cloud Storage data URIs will always be represented in the
                Google Cloud Storage wildcard format to support sharded
                data.

                -  AIP_DATA_FORMAT = "jsonl".
                -  AIP_TRAINING_DATA_URI = "gcs_destination/training-*"
                -  AIP_VALIDATION_DATA_URI = "gcs_destination/validation-*"
                -  AIP_TEST_DATA_URI = "gcs_destination/test-*".
        """

        input_data_config = None
        if dataset:
            # Create fraction split spec
            fraction_split = gca_training_pipeline.FractionSplit(
                training_fraction=training_fraction_split,
                validation_fraction=validation_fraction_split,
                test_fraction=test_fraction_split,
            )

            # Create predefined split spec
            predefined_split = None
            if predefined_split_column_name:
                if (
                    dataset._gca_resource.metadata_schema_uri
                    != schema.dataset.metadata.tabular
                ):
                    raise ValueError(
                        "A pre-defined split may only be used with a tabular Dataset"
                    )

                predefined_split = gca_training_pipeline.PredefinedSplit(
                    key=predefined_split_column_name
                )

            # Create GCS destination
            gcs_destination = None
            if gcs_destination_uri_prefix:
                gcs_destination = gca_io.GcsDestination(
                    output_uri_prefix=gcs_destination_uri_prefix
                )

            # create input data config
            input_data_config = gca_training_pipeline.InputDataConfig(
                fraction_split=fraction_split,
                predefined_split=predefined_split,
                dataset_id=dataset.name,
                gcs_destination=gcs_destination,
            )

        return input_data_config

    def _run_job(
        self,
        training_task_definition: str,
        training_task_inputs: dict,
        dataset: Optional[datasets.Dataset],
        training_fraction_split: float,
        validation_fraction_split: float,
        test_fraction_split: float,
        predefined_split_column_name: Optional[str] = None,
        model: Optional[gca_model.Model] = None,
        gcs_destination_uri_prefix: Optional[str] = None,
    ) -> Optional[models.Model]:
        """Runs the training job.

        Args:
            training_task_definition (str):
                Required. A Google Cloud Storage path to the
                YAML file that defines the training task which
                is responsible for producing the model artifact,
                and may also include additional auxiliary work.
                The definition files that can be used here are
                found in gs://google-cloud-
                aiplatform/schema/trainingjob/definition/. Note:
                The URI given on output will be immutable and
                probably different, including the URI scheme,
                than the one given on input. The output URI will
                point to a location where the user only has a
                read access.
            training_task_inputs (dict):
                Required. The training task's parameter(s), as specified in
                the
                ``training_task_definition``'s
                ``inputs``.
            dataset (aiplatform.Dataset):
                Optional. The dataset within the same Project from which data will be used to train the Model. The
                Dataset must use schema compatible with Model being trained,
                and what is compatible should be described in the used
                TrainingPipeline's [training_task_definition]
                [google.cloud.aiplatform.v1beta1.TrainingPipeline.training_task_definition].
                For tabular Datasets, all their data is exported to
                training, to pick and choose from.
            training_fraction_split (float):
                The fraction of the input data that is to be
                used to train the Model. This is ignored if Dataset is not provided.
            validation_fraction_split (float):
                The fraction of the input data that is to be
                used to validate the Model. This is ignored if Dataset is not provided.
            test_fraction_split (float):
                The fraction of the input data that is to be
                used to evaluate the Model. This is ignored if Dataset is not provided.
            predefined_split_column_name (str):
                Optional. The key is a name of one of the Dataset's data
                columns. The value of the key (either the label's value or
                value in the column) must be one of {``training``,
                ``validation``, ``test``}, and it defines to which set the
                given piece of data is assigned. If for a piece of data the
                key is not present or has an invalid value, that piece is
                ignored by the pipeline.

                Supported only for tabular Datasets.
            model (~.model.Model):
                Optional. Describes the Model that may be uploaded (via
                [ModelService.UploadMode][]) by this TrainingPipeline. The
                TrainingPipeline's
                ``training_task_definition``
                should make clear whether this Model description should be
                populated, and if there are any special requirements
                regarding how it should be filled. If nothing is mentioned
                in the
                ``training_task_definition``,
                then it should be assumed that this field should not be
                filled and the training task either uploads the Model
                without a need of this information, or that training task
                does not support uploading a Model as part of the pipeline.
                When the Pipeline's state becomes
                ``PIPELINE_STATE_SUCCEEDED`` and the trained Model had been
                uploaded into AI Platform, then the model_to_upload's
                resource ``name``
                is populated. The Model is always uploaded into the Project
                and Location in which this pipeline is.
            gcs_destination_uri_prefix (str):
                Optional. The Google Cloud Storage location.

                The AI Platform environment variables representing Google
                Cloud Storage data URIs will always be represented in the
                Google Cloud Storage wildcard format to support sharded
                data.

                -  AIP_DATA_FORMAT = "jsonl".
                -  AIP_TRAINING_DATA_URI = "gcs_destination/training-*"
                -  AIP_VALIDATION_DATA_URI = "gcs_destination/validation-*"
                -  AIP_TEST_DATA_URI = "gcs_destination/test-*".
        """

        input_data_config = self._create_input_data_config(
            dataset=dataset,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=predefined_split_column_name,
            gcs_destination_uri_prefix=gcs_destination_uri_prefix,
        )

        # create training pipeline
        training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=self._display_name,
            training_task_definition=training_task_definition,
            training_task_inputs=json_format.ParseDict(
                training_task_inputs, struct_pb2.Value()
            ),
            model_to_upload=model,
            input_data_config=input_data_config,
        )

        training_pipeline = self.api_client.create_training_pipeline(
            parent=initializer.global_config.common_location_path(
                self.project, self.location
            ),
            training_pipeline=training_pipeline,
        )

        self._gca_resource = training_pipeline

        _LOGGER.info("View Training:\n%s" % self._dashboard_uri())

        model = self._get_model()

        if model is None:
            _LOGGER.warning(
                "Training did not produce a Managed Model returning None. "
                + self._model_upload_fail_string
            )

        return model

    def _is_waiting_to_run(self) -> bool:
        """Returns True if the Job is pending on upstream tasks False otherwise."""
        self._raise_future_exception()
        if self._latest_future:
            _LOGGER.info(
                "Training Job is waiting for upstream SDK tasks to complete before"
                " launching."
            )
            return True
        return False

    @property
    def state(self) -> Optional[gca_pipeline_state.PipelineState]:
        """Current training state."""

        if self._assert_has_run():
            return

        return self._gca_resource.state

    def get_model(self) -> Optional[models.Model]:
        """AI Platform Model produced by this training, if one was produced.

        Returns:
            model: AI Platform Model produced by this training or None if a model was
                not produced by this training.
        """
        self._assert_has_run()

        if not self._gca_resource.model_to_upload:
            raise RuntimeError(self._model_upload_fail_string)

        return self._get_model()

    def _get_model(self) -> Optional[models.Model]:
        """Helper method to get and instantiate the Model to Upload.

        Returns:
            model: AI Platform Model if training succeeded and produced an AI Platform
                Model. None otherwise.

        Raises:
            RuntimeError if Training failed.
        """
        self._block_until_complete()

        if self.has_failed:
            raise RuntimeError(
                f"Training Pipeline {self.resource_name} failed. No model available."
            )

        if not self._gca_resource.model_to_upload:
            return None

        if self._gca_resource.model_to_upload.name:
            fields = utils.extract_fields_from_resource_name(
                self._gca_resource.model_to_upload.name
            )
            return models.Model(
                fields.id, project=fields.project, location=fields.location
            )

    def _block_until_complete(self):
        """Helper method to block and check on job until complete."""

        # Used these numbers so failures surface fast
        wait = 5  # start at five seconds
        max_wait = 60 * 5  # 5 minute wait
        multiplier = 2  # scale wait by 2 every iteration

        while self.state not in _PIPELINE_COMPLETE_STATES:
            self._sync_gca_resource()
            time.sleep(wait)
            _LOGGER.info(
                "Training %s current state:\n%s"
                % (self._gca_resource.name, self._gca_resource.state)
            )
            wait = min(wait * multiplier, max_wait)

        self._raise_failure()

        if self._gca_resource.model_to_upload and not self.has_failed:
            _LOGGER.info(
                "Model available at %s" % self._gca_resource.model_to_upload.name
            )

    def _raise_failure(self):
        """Helper method to raise failure if TrainingPipeline fails.

        Raises:
            RuntimeError: If training failed."""

        if self._gca_resource.error.code != code_pb2.OK:
            raise RuntimeError("Training failed with:\n%s" % self._gca_resource.error)

    @property
    def has_failed(self) -> bool:
        """Returns True if training has failed. False otherwise."""
        self._assert_has_run()
        return self.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED

    def _dashboard_uri(self) -> str:
        """Helper method to compose the dashboard uri where training can be viewed."""
        fields = utils.extract_fields_from_resource_name(self.resource_name)
        url = f"https://console.cloud.google.com/ai/platform/locations/{fields.location}/training/{fields.id}?project={fields.project}"
        return url

    def _sync_gca_resource(self):
        """Helper method to sync the local gca_source against the service."""
        self._gca_resource = self.api_client.get_training_pipeline(
            name=self.resource_name
        )

    @property
    def _has_run(self) -> bool:
        """Helper property to check if this training job has been run."""
        return self._gca_resource is not None

    def _assert_has_run(self) -> bool:
        """Helper method to assert that this training has run."""
        if not self._has_run:
            if self._is_waiting_to_run():
                return True
            raise RuntimeError(
                "TrainingPipeline has not been launched. You must run this"
                " TrainingPipeline using TrainingPipeline.run. "
            )
        return False


def _timestamped_gcs_dir(root_gcs_path: str, dir_name_prefix: str) -> str:
    """Composes a timestamped GCS directory.

    Args:
        root_gcs_path: GCS path to put the timestamped directory.
        dir_name_prefix: Prefix to add the timestamped directory.
    Returns:
        Timestamped gcs directory path in root_gcs_path.
    """
    timestamp = datetime.datetime.now().isoformat(sep="-", timespec="milliseconds")
    dir_name = "-".join([dir_name_prefix, timestamp])
    if root_gcs_path.endswith("/"):
        root_gcs_path = root_gcs_path[:-1]
    gcs_path = "/".join([root_gcs_path, dir_name])
    if not gcs_path.startswith("gs://"):
        return "gs://" + gcs_path
    return gcs_path


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

    gcs_bucket, gcs_blob_prefix = utils.extract_bucket_and_prefix_from_gcs_path(gcs_dir)

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

    # Module name that can be executed during training. ie. python -m
    module_name = f"{_ROOT_MODULE}.{_TASK_MODULE_NAME}"

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
            args=setup_cmd,
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
            output_location = copy_method(source_distribution_path)
            _LOGGER.info("Training script copied to:\n%s." % output_location)
            return output_location

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


class _MachineSpec(NamedTuple):
    """Specification container for Machine specs used for distributed training.

    Usage:

    spec = _MachineSpec(
                replica_count=10,
                machine_type='n1-standard-4',
                accelerator_count=2,
                accelerator_type='NVIDIA_TESLA_K80')

    Note that container and python package specs are not stored with this spec.
    """

    replica_count: int = 0
    machine_type: str = "n1-standard-4"
    accelerator_count: int = 0
    accelerator_type: str = "ACCELERATOR_TYPE_UNSPECIFIED"

    def _get_accelerator_type(self) -> Optional[str]:
        """Validates accelerator_type and returns the name of the accelerator.

        Returns:
            None if no accelerator or valid accelerator name.

        Raise:
            ValueError if accelerator type is invalid.
        """

        # validate accelerator type
        if (
            self.accelerator_type
            not in gca_accelerator_type.AcceleratorType._member_names_
        ):
            raise ValueError(
                f"accelerator_type `{self.accelerator_type}` invalid. "
                f"Choose one of {gca_accelerator_type.AcceleratorType._member_names_}"
            )

        accelerator_enum = getattr(
            gca_accelerator_type.AcceleratorType, self.accelerator_type
        )

        if (
            accelerator_enum
            != gca_accelerator_type.AcceleratorType.ACCELERATOR_TYPE_UNSPECIFIED
        ):
            return self.accelerator_type

    @property
    def spec_dict(self) -> Dict[str, Union[int, str, Dict[str, Union[int, str]]]]:
        """Return specification as a Dict."""
        spec = {
            "machineSpec": {"machineType": self.machine_type},
            "replicaCount": self.replica_count,
        }
        accelerator_type = self._get_accelerator_type()
        if accelerator_type and self.accelerator_count:
            spec["machineSpec"]["acceleratorType"] = accelerator_type
            spec["machineSpec"]["acceleratorCount"] = self.accelerator_count

        return spec

    @property
    def is_empty(self) -> bool:
        """Returns True is replica_count > 0 False otherwise."""
        return self.replica_count <= 0


class _DistributedTrainingSpec(NamedTuple):
    """Configuration for distributed training worker pool specs.

    AI Platform Training expects configuration in this order:
    [
        chief spec, # can only have one replica
        worker spec,
        parameter server spec,
        evaluator spec
    ]

    Usage:

    dist_training_spec = _DistributedTrainingSpec(
        chief_spec = _MachineSpec(
                replica_count=1,
                machine_type='n1-standard-4',
                accelerator_count=2,
                accelerator_type='NVIDIA_TESLA_K80'
                ),
        worker_spec = _MachineSpec(
                replica_count=10,
                machine_type='n1-standard-4',
                accelerator_count=2,
                accelerator_type='NVIDIA_TESLA_K80'
                )
    )

    """

    chief_spec: _MachineSpec = _MachineSpec()
    worker_spec: _MachineSpec = _MachineSpec()
    parameter_server_spec: _MachineSpec = _MachineSpec()
    evaluator_spec: _MachineSpec = _MachineSpec()

    @property
    def pool_specs(
        self,
    ) -> List[Dict[str, Union[int, str, Dict[str, Union[int, str]]]]]:
        """Return each pools spec in correct order for AI Platform as a list of dicts.

        Also removes specs if they are empty but leaves specs in if there unusual
        specifications to not break the ordering in AI Platform Training.
        ie. 0 chief replica, 10 worker replica, 3 ps replica

        Returns:
            Order list of worker pool specs suitable for AI Platform Training.
        """
        if self.chief_spec.replica_count > 1:
            raise ValueError("Chief spec replica count cannot be greater than 1.")

        spec_order = [
            self.chief_spec,
            self.worker_spec,
            self.parameter_server_spec,
            self.evaluator_spec,
        ]
        specs = [s.spec_dict for s in spec_order]
        for i in reversed(range(len(spec_order))):
            if spec_order[i].is_empty:
                specs.pop()
            else:
                break
        return specs

    @classmethod
    def chief_worker_pool(
        cls,
        replica_count: int = 0,
        machine_type: str = "n1-standard-4",
        accelerator_count: int = 0,
        accelerator_type: str = "ACCELERATOR_TYPE_UNSPECIFIED",
    ) -> "_DistributedTrainingSpec":
        """Parameterizes Config to support only chief with worker replicas.

        For replica is assigned to chief and the remainder to workers. All spec have the
        same machine type, accelerator count, and accelerator type.

        Args:
            replica_count (int):
                The number of worker replicas. Assigns 1 chief replica and
                replica_count - 1 worker replicas.
            machine_type (str):
                The type of machine to use for training.
            accelerator_type (str):
                Hardware accelerator type. One of ACCELERATOR_TYPE_UNSPECIFIED,
                NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100, NVIDIA_TESLA_P4,
                NVIDIA_TESLA_T4, TPU_V2, TPU_V3
            accelerator_count (int):
                The number of accelerators to attach to a worker replica.

        Returns:
            _DistributedTrainingSpec representing one chief and n workers all of same
            type. If replica_count <= 0 then an empty spec is returned.
        """
        if replica_count <= 0:
            return cls()

        chief_spec = _MachineSpec(
            replica_count=1,
            machine_type=machine_type,
            accelerator_count=accelerator_count,
            accelerator_type=accelerator_type,
        )

        worker_spec = _MachineSpec(
            replica_count=replica_count - 1,
            machine_type=machine_type,
            accelerator_count=accelerator_count,
            accelerator_type=accelerator_type,
        )

        return cls(chief_spec=chief_spec, worker_spec=worker_spec)


# TODO(b/172368325) add scheduling, custom_job.Scheduling
class CustomTrainingJob(_TrainingJob):
    """Class to launch a Custom Training Job in AI Platform using a script.

    Takes a training implementation as a python script and executes that script
    in Cloud AI Platform Training.
    """

    # TODO(b/172365796) add remainder of model optional arguments
    def __init__(
        self,
        display_name: str,
        script_path: str,
        container_uri: str,
        requirements: Optional[Sequence[str]] = None,
        model_serving_container_image_uri: Optional[str] = None,
        model_serving_container_predict_route: Optional[str] = None,
        model_serving_container_health_route: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        staging_bucket: Optional[str] = None,
    ):
        """Constructs a Custom Training Job from a Python script.

        job = aiplatform.CustomTrainingJob(
            display_name='test-train',
            script_path='test_script.py',
            requirements=['pandas', 'numpy'],
            container_uri='gcr.io/cloud-aiplatform/training/tf-cpu.2-2:latest',
            model_serving_container_image_uri='gcr.io/my-trainer/serving:1',
            model_serving_container_predict_route='predict',
            model_serving_container_health_route='metadata)

        Usage with Dataset:

        ds = aiplatform.Dataset(
            'projects/my-project/locations/us-central1/datasets/12345')

        job.run(ds, replica_count=1, model_display_name='my-trained-model')

        Usage without Dataset:

        job.run(replica_count=1, model_display_name='my-trained-model)


        TODO(b/169782082) add documentation about traning utilities
        To ensure your model gets saved in AI Platform, write your saved model to
        os.environ["AIP_MODEL_DIR"] in your provided training script.


        Args:
            display_name (str):
                Required. The user-defined name of this TrainingPipeline.
            script_path (str): Required. Local path to training script.
            container_uri (str):
                Required: Uri of the training container image in the GCR.
            requirements (Sequence[str]):
                List of python packages dependencies of script.
            model_serving_container_image_uri (str):
                If the training produces a managed AI Platform Model, the URI of the
                Model serving container suitable for serving the model produced by the
                training script.
            model_serving_container_predict_route (str):.
                If the training produces a managed AI Platform Model, An HTTP path to
                send prediction requests to the container, and which must be supported
                by it. If not specified a default HTTP path will be used by AI Platform.
            model_serving_container_health_route (str):
                If the training produces a managed AI Platform Model, an HTTP path to
                send health check requests to the container, and which must be supported
                by it. If not specified a standard HTTP path will be used by AI
                Platform.
            project (str):
                Project to run training in. Overrides project set in aiplatform.init.
            location (str):
                Location to run training in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to run call training service. Overrides
                credentials set in aiplatform.init.
            staging_bucket (str):
                Bucket used to stage source and training artifacts. Overrides
                staging_bucket set in aiplatform.init.
        """
        super().__init__(
            display_name=display_name,
            project=project,
            location=location,
            credentials=credentials,
        )

        self._container_uri = container_uri
        self._requirements = requirements
        self._model_serving_container_image_uri = model_serving_container_image_uri
        self._model_serving_container_predict_route = (
            model_serving_container_predict_route
        )
        self._model_serving_container_health_route = (
            model_serving_container_health_route
        )

        self._script_path = script_path
        self._staging_bucket = (
            staging_bucket or initializer.global_config.staging_bucket
        )

        if not self._staging_bucket:
            raise RuntimeError(
                "staging_bucket should be set in TrainingJob constructor or "
                "set using aiplatform.init(staging_bucket='gs://my-bucket'"
            )

    # TODO(b/172365904) add filter split, training_pipeline.FilterSplit
    # TODO(b/172368070) add timestamp split, training_pipeline.TimestampSplit
    def run(
        self,
        dataset: Optional[datasets.Dataset] = None,
        model_display_name: Optional[str] = None,
        base_output_dir: Optional[str] = None,
        args: Optional[List[Union[str, float, int]]] = None,
        replica_count: int = 0,
        machine_type: str = "n1-standard-4",
        accelerator_type: str = "ACCELERATOR_TYPE_UNSPECIFIED",
        accelerator_count: int = 0,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        predefined_split_column_name: Optional[str] = None,
        sync=True,
    ) -> Optional[models.Model]:
        """Runs the custom training job.

        Distributed Training Support:
        If replica count = 1 then one chief replica will be provisioned. If
        replica_count > 1 the remainder will be provisioned as a worker replica pool.
        ie: replica_count = 10 will result in 1 chief and 9 workers
        All replicas have same machine_type, accelerator_type, and accelerator_count

        Data fraction splits:
        Any of ``training_fraction_split``, ``validation_fraction_split`` and
        ``test_fraction_split`` may optionally be provided, they must sum to up to 1. If
        the provided ones sum to less than 1, the remainder is assigned to sets as
        decided by AI Platform.If none of the fractions are set, by default roughly 80%
        of data will be used for training, 10% for validation, and 10% for test.

        Args:
            dataset (aiplatform.Dataset):
                AI Platform to fit this training against. Custom training script should
                retrieve datasets through passed in environement variables uris:

                os.environ["AIP_TRAINING_DATA_URI"]
                os.environ["AIP_VALIDATION_DATA_URI"]
                os.environ["AIP_TEST_DATA_URI"]

                Additionally the dataset format is passed in as:

                os.environ["AIP_DATA_FORMAT"]
            model_display_name (str):
                If the script produces a managed AI Platform Model. The display name of
                the Model. The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            base_output_dir (str):
                GCS output directory of job. If not provided a
                timestamped directory in the staging directory will be used.
            args (List[Unions[str, int, float]]):
                Command line arguments to be passed to the Python script.
            replica_count (int):
                The number of worker replicas. If replica count = 1 then one chief
                replica will be provisioned. If replica_count > 1 the remainder will be
                provisioned as a worker replica pool.
            machine_type (str):
                The type of machine to use for training.
            accelerator_type (str):
                Hardware accelerator type. One of ACCELERATOR_TYPE_UNSPECIFIED,
                NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100, NVIDIA_TESLA_P4,
                NVIDIA_TESLA_T4, TPU_V2, TPU_V3
            accelerator_count (int):
                The number of accelerators to attach to a worker replica.
            training_fraction_split (float):
                The fraction of the input data that is to be
                used to train the Model. This is ignored if Dataset is not provided.
            validation_fraction_split (float):
                The fraction of the input data that is to be
                used to validate the Model. This is ignored if Dataset is not provided.
            test_fraction_split (float):
                The fraction of the input data that is to be
                used to evaluate the Model. This is ignored if Dataset is not provided.
            predefined_split_column_name (str):
                Optional. The key is a name of one of the Dataset's data
                columns. The value of the key (either the label's value or
                value in the column) must be one of {``training``,
                ``validation``, ``test``}, and it defines to which set the
                given piece of data is assigned. If for a piece of data the
                key is not present or has an invalid value, that piece is
                ignored by the pipeline.

                Supported only for tabular Datasets.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.

        Raises:
            RuntimeError if Training job has already been run, staging_bucket has not
                been set, or model_display_name was provided but required arguments
                were not provided in constructor.
        """
        if self._is_waiting_to_run():
            raise RuntimeError("Custom Training is already scheduled to run.")

        if self._has_run:
            raise RuntimeError("Custom Training has already run.")

        # if args needed for model is incomplete
        if model_display_name and not self._model_serving_container_image_uri:
            raise RuntimeError(
                """model_display_name was provided but
                model_serving_container_image_uri was not provided when this
                custom pipeline was constructed.
                """
            )

        # validates args and will raise
        worker_pool_specs = _DistributedTrainingSpec.chief_worker_pool(
            replica_count=replica_count,
            machine_type=machine_type,
            accelerator_count=accelerator_count,
            accelerator_type=accelerator_type,
        ).pool_specs

        # create model payload
        managed_model = None
        if model_display_name:
            utils.validate_display_name(model_display_name)

            container_spec = gca_model.ModelContainerSpec(
                image_uri=self._model_serving_container_image_uri,
                predict_route=self._model_serving_container_predict_route,
                health_route=self._model_serving_container_health_route,
            )

            managed_model = gca_model.Model(
                display_name=model_display_name, container_spec=container_spec
            )

        # make and copy package
        python_packager = _TrainingScriptPythonPackager(
            script_path=self._script_path, requirements=self._requirements
        )

        return self._run(
            python_packager=python_packager,
            dataset=dataset,
            worker_pool_specs=worker_pool_specs,
            managed_model=managed_model,
            args=args,
            base_output_dir=base_output_dir,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=predefined_split_column_name,
            sync=sync,
        )

    @base.optional_sync(construct_object_on_arg="managed_model")
    def _run(
        self,
        python_packager: _TrainingScriptPythonPackager,
        dataset: Optional[datasets.Dataset],
        worker_pool_specs: _DistributedTrainingSpec,
        managed_model: Optional[gca_model.Model] = None,
        args: Optional[List[Union[str, float, int]]] = None,
        base_output_dir: Optional[str] = None,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        predefined_split_column_name: Optional[str] = None,
        sync=True,
    ) -> Optional[models.Model]:
        """Packages local script and launches training_job.
        Args:
            python_packager (_TrainingScriptPythonPackager):
                Required. Python Packager poiting to training script locally.
            dataset (aiplatform.Dataset):
                AI Platform to fit this training against.
            worker_pools_spec (_DistributedTrainingSpec):
                Worker pools pecs required to run job.
            managed_model (gca_model.Model):
                Model proto if this script produces a Managed Model.
            args (List[Unions[str, int, float]]):
                Command line arguments to be passed to the Python script.
            base_output_dir (str):
                GCS output directory of job. If not provided a
                timestamped directory in the staging directory will be used.
            training_fraction_split (float):
                The fraction of the input data that is to be
                used to train the Model.
            validation_fraction_split (float):
                The fraction of the input data that is to be
                used to validate the Model.
            test_fraction_split (float):
                The fraction of the input data that is to be
                used to evaluate the Model.
            predefined_split_column_name (str):
                Optional. The key is a name of one of the Dataset's data
                columns. The value of the key (either the label's value or
                value in the column) must be one of {``training``,
                ``validation``, ``test``}, and it defines to which set the
                given piece of data is assigned. If for a piece of data the
                key is not present or has an invalid value, that piece is
                ignored by the pipeline.

                Supported only for tabular Datasets.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """
        # default directory if not given
        base_output_dir = base_output_dir or _timestamped_gcs_dir(
            self._staging_bucket, "aiplatform-custom-training"
        )

        _LOGGER.info("Training Output directory:\n%s " % base_output_dir)

        package_gcs_uri = python_packager.package_and_copy_to_gcs(
            gcs_staging_dir=self._staging_bucket,
            project=self.project,
            credentials=self.credentials,
        )

        for spec in worker_pool_specs:
            spec["pythonPackageSpec"] = {
                "executorImageUri": self._container_uri,
                "pythonModule": python_packager.module_name,
                "packageUris": [package_gcs_uri],
            }

            if args:
                spec["pythonPackageSpec"]["args"] = args

        training_task_inputs = {
            "workerPoolSpecs": worker_pool_specs,
            "baseOutputDirectory": {"output_uri_prefix": base_output_dir},
        }

        model = self._run_job(
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=training_task_inputs,
            dataset=dataset,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=predefined_split_column_name,
            model=managed_model,
            gcs_destination_uri_prefix=base_output_dir,
        )

        return model

    @property
    def _model_upload_fail_string(self) -> str:
        """Helper property for model upload failure."""
        return (
            f"Training Pipeline {self.resource_name} is not configured to upload a "
            "Model. Create the Training Pipeline with "
            "model_serving_container_image_uri and model_display_name passed in. "
            "Ensure that your training script saves to model to "
            "os.environ['AIP_MODEL_DIR']."
        )


class AutoMLTabularTrainingJob(_TrainingJob):
    def __init__(
        self,
        display_name: str,
        optimization_prediction_type: str,
        optimization_objective: Optional[str] = None,
        column_transformations: Optional[Union[Dict, List[Dict]]] = None,
        optimization_objective_recall_value: Optional[float] = None,
        optimization_objective_precision_value: Optional[float] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Constructs a AutoML Tabular Training Job.

        Args:
            display_name (str):
                Required. The user-defined name of this TrainingPipeline.
            optimization_prediction_type (str):
                The type of prediction the Model is to produce.
                "classification" - Predict one out of multiple target values is
                picked for each row.
                "regression" - Predict a value based on its relation to other values.
                This type is available only to columns that contain
                semantically numeric values, i.e. integers or floating
                point number, even if stored as e.g. strings.

            optimization_objective (str):
                Optional. Objective function the Model is to be optimized towards. The training
                task creates a Model that maximizes/minimizes the value of the objective
                function over the validation set.

                The supported optimization objectives depend on the prediction type, and
                in the case of classification also the number of distinct values in the
                target column (two distint values -> binary, 3 or more distinct values
                -> multi class).
                If the field is not set, the default objective function is used.

                Classification (binary):
                "maximize-au-roc" (default) - Maximize the area under the receiver
                                            operating characteristic (ROC) curve.
                "minimize-log-loss" - Minimize log loss.
                "maximize-au-prc" - Maximize the area under the precision-recall curve.
                "maximize-precision-at-recall" - Maximize precision for a specified
                                                recall value.
                "maximize-recall-at-precision" - Maximize recall for a specified
                                                precision value.

                Classification (multi class):
                "minimize-log-loss" (default) - Minimize log loss.

                Regression:
                "minimize-rmse" (default) - Minimize root-mean-squared error (RMSE).
                "minimize-mae" - Minimize mean-absolute error (MAE).
                "minimize-rmsle" - Minimize root-mean-squared log error (RMSLE).
            column_transformations (Optional[Union[Dict, List[Dict]]]):
                Optional. Transformations to apply to the input columns (i.e. columns other
                than the targetColumn). Each transformation may produce multiple
                result values from the column's value, and all are used for training.
                When creating transformation for BigQuery Struct column, the column
                should be flattened using "." as the delimiter.
                If an input column has no transformations on it, such a column is
                ignored by the training, except for the targetColumn, which should have
                no transformations defined on.
            optimization_objective_recall_value (float):
                Optional. Required when maximize-precision-at-recall optimizationObjective was
                picked, represents the recall value at which the optimization is done.

                The minimum value is 0 and the maximum is 1.0.
            optimization_objective_precision_value (float):
                Optional. Required when maximize-recall-at-precision optimizationObjective was
                picked, represents the precision value at which the optimization is
                done.

                The minimum value is 0 and the maximum is 1.0.
            project (str):
                Optional. Project to run training in. Overrides project set in aiplatform.init.
            location (str):
                Optional. Location to run training in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to run call training service. Overrides
                credentials set in aiplatform.init.
        """
        super().__init__(
            display_name=display_name,
            project=project,
            location=location,
            credentials=credentials,
        )
        self._column_transformations = column_transformations
        self._optimization_objective = optimization_objective
        self._optimization_prediction_type = optimization_prediction_type
        self._optimization_objective_recall_value = optimization_objective_recall_value
        self._optimization_objective_precision_value = (
            optimization_objective_precision_value
        )

    def run(
        self,
        dataset: datasets.Dataset,
        target_column: str,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        predefined_split_column_name: Optional[str] = None,
        weight_column: Optional[str] = None,
        budget_milli_node_hours: int = 1000,
        model_display_name: Optional[str] = None,
        disable_early_stopping: bool = False,
        sync: bool = True,
    ) -> models.Model:
        """Runs the training job and returns a model.

        Data fraction splits:
        Any of ``training_fraction_split``, ``validation_fraction_split`` and
        ``test_fraction_split`` may optionally be provided, they must sum to up to 1. If
        the provided ones sum to less than 1, the remainder is assigned to sets as
        decided by AI Platform.If none of the fractions are set, by default roughly 80%
        of data will be used for training, 10% for validation, and 10% for test.

        Args:
            dataset (aiplatform.Dataset):
                Required. The dataset within the same Project from which data will be used to train the Model. The
                Dataset must use schema compatible with Model being trained,
                and what is compatible should be described in the used
                TrainingPipeline's [training_task_definition]
                [google.cloud.aiplatform.v1beta1.TrainingPipeline.training_task_definition].
                For tabular Datasets, all their data is exported to
                training, to pick and choose from.
            training_fraction_split (float):
                Required. The fraction of the input data that is to be
                used to train the Model. This is ignored if Dataset is not provided.
            validation_fraction_split (float):
                Required. The fraction of the input data that is to be
                used to validate the Model. This is ignored if Dataset is not provided.
            test_fraction_split (float):
                Required. The fraction of the input data that is to be
                used to evaluate the Model. This is ignored if Dataset is not provided.
            predefined_split_column_name (str):
                Optional. The key is a name of one of the Dataset's data
                columns. The value of the key (either the label's value or
                value in the column) must be one of {``training``,
                ``validation``, ``test``}, and it defines to which set the
                given piece of data is assigned. If for a piece of data the
                key is not present or has an invalid value, that piece is
                ignored by the pipeline.

                Supported only for tabular Datasets.
            weight_column (str):
                Optional. Name of the column that should be used as the weight column.
                Higher values in this column give more importance to the row
                during Model training. The column must have numeric values between 0 and
                10000 inclusively, and 0 value means that the row is ignored.
                If the weight column field is not set, then all rows are assumed to have
                equal weight of 1.
            budget_milli_node_hours (int):
                Optional. The train budget of creating this Model, expressed in milli node
                hours i.e. 1,000 value in this field means 1 node hour.
                The training cost of the model will not exceed this budget. The final
                cost will be attempted to be close to the budget, though may end up
                being (even) noticeably smaller - at the backend's discretion. This
                especially may happen when further model training ceases to provide
                any improvements.
                If the budget is set to a value known to be insufficient to train a
                Model for the given training set, the training won't be attempted and
                will error.
                The minimum value is 1000 and the maximum is 72000.
            model_display_name (str):
                Optional. If the script produces a managed AI Platform Model. The display name of
                the Model. The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.

                If not provided upon creation, the job's display_name is used.
            disable_early_stopping (bool):
                Required. If true, the entire budget is used. This disables the early stopping
                feature. By default, the early stopping feature is enabled, which means
                that training might stop before the entire training budget has been
                used, if futrher training does no longer brings significant improvement
                to the model.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.

        Raises:
            RuntimeError if Training job has already been run or is waiting to run.
        """

        if self._is_waiting_to_run():
            raise RuntimeError("Custom Training is already scheduled to run.")

        if self._has_run:
            raise RuntimeError("Custom Training has already run.")

        return self._run(
            dataset=dataset,
            target_column=target_column,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=predefined_split_column_name,
            weight_column=weight_column,
            budget_milli_node_hours=budget_milli_node_hours,
            model_display_name=model_display_name,
            disable_early_stopping=disable_early_stopping,
            sync=sync,
        )

    @base.optional_sync()
    def _run(
        self,
        dataset: datasets.Dataset,
        target_column: str,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        predefined_split_column_name: Optional[str] = None,
        weight_column: Optional[str] = None,
        budget_milli_node_hours: int = 1000,
        model_display_name: Optional[str] = None,
        disable_early_stopping: bool = False,
        sync: bool = True,
    ) -> models.Model:
        """Runs the training job and returns a model.

        Data fraction splits:
        Any of ``training_fraction_split``, ``validation_fraction_split`` and
        ``test_fraction_split`` may optionally be provided, they must sum to up to 1. If
        the provided ones sum to less than 1, the remainder is assigned to sets as
        decided by AI Platform.If none of the fractions are set, by default roughly 80%
        of data will be used for training, 10% for validation, and 10% for test.

        Args:
            dataset (aiplatform.Dataset):
                Required. The dataset within the same Project from which data will be used to train the Model. The
                Dataset must use schema compatible with Model being trained,
                and what is compatible should be described in the used
                TrainingPipeline's [training_task_definition]
                [google.cloud.aiplatform.v1beta1.TrainingPipeline.training_task_definition].
                For tabular Datasets, all their data is exported to
                training, to pick and choose from.
            training_fraction_split (float):
                Required. The fraction of the input data that is to be
                used to train the Model. This is ignored if Dataset is not provided.
            validation_fraction_split (float):
                Required. The fraction of the input data that is to be
                used to validate the Model. This is ignored if Dataset is not provided.
            test_fraction_split (float):
                Required. The fraction of the input data that is to be
                used to evaluate the Model. This is ignored if Dataset is not provided.
            predefined_split_column_name (str):
                Optional. The key is a name of one of the Dataset's data
                columns. The value of the key (either the label's value or
                value in the column) must be one of {``training``,
                ``validation``, ``test``}, and it defines to which set the
                given piece of data is assigned. If for a piece of data the
                key is not present or has an invalid value, that piece is
                ignored by the pipeline.

                Supported only for tabular Datasets.
            weight_column (str):
                Optional. Name of the column that should be used as the weight column.
                Higher values in this column give more importance to the row
                during Model training. The column must have numeric values between 0 and
                10000 inclusively, and 0 value means that the row is ignored.
                If the weight column field is not set, then all rows are assumed to have
                equal weight of 1.
            budget_milli_node_hours (int):
                Optional. The train budget of creating this Model, expressed in milli node
                hours i.e. 1,000 value in this field means 1 node hour.
                The training cost of the model will not exceed this budget. The final
                cost will be attempted to be close to the budget, though may end up
                being (even) noticeably smaller - at the backend's discretion. This
                especially may happen when further model training ceases to provide
                any improvements.
                If the budget is set to a value known to be insufficient to train a
                Model for the given training set, the training won't be attempted and
                will error.
                The minimum value is 1000 and the maximum is 72000.
            model_display_name (str):
                Optional. If the script produces a managed AI Platform Model. The display name of
                the Model. The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.

                If not provided upon creation, the job's display_name is used.
            disable_early_stopping (bool):
                Required. If true, the entire budget is used. This disables the early stopping
                feature. By default, the early stopping feature is enabled, which means
                that training might stop before the entire training budget has been
                used, if futrher training does no longer brings significant improvement
                to the model.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """

        training_task_definition = schema.training_job.definition.tabular_task

        training_task_inputs_dict = {
            # required inputs
            "targetColumn": target_column,
            "transformations": self._column_transformations,
            "trainBudgetMilliNodeHours": budget_milli_node_hours,
            # optional inputs
            "weightColumnName": weight_column,
            "disableEarlyStopping": disable_early_stopping,
            "optimizationObjective": self._optimization_objective,
            "predictionType": self._optimization_prediction_type,
            "optimizationObjectiveRecallValue": self._optimization_objective_recall_value,
            "optimizationObjectivePrecisionValue": self._optimization_objective_precision_value,
        }

        if model_display_name is None:
            model_display_name = self._display_name

        model = gca_model.Model(display_name=model_display_name)

        return self._run_job(
            training_task_definition=training_task_definition,
            training_task_inputs=training_task_inputs_dict,
            dataset=dataset,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=predefined_split_column_name,
            model=model,
        )

    @property
    def _model_upload_fail_string(self) -> str:
        """Helper property for model upload failure."""
        return (
            f"Training Pipeline {self.resource_name} is not configured to upload a "
            "Model."
        )
