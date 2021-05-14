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
from typing import Callable, Dict, List, Optional, NamedTuple, Sequence, Tuple, Union

import abc

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import constants
from google.cloud.aiplatform import datasets
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform import schema
from google.cloud.aiplatform import utils

from google.cloud.aiplatform.compat.types import (
    accelerator_type as gca_accelerator_type,
    env_var as gca_env_var,
    io as gca_io,
    model as gca_model,
    pipeline_state as gca_pipeline_state,
    training_pipeline as gca_training_pipeline,
)

from google.cloud.aiplatform.v1.schema.trainingjob import (
    definition_v1 as training_job_inputs,
)

from google.cloud import storage
from google.rpc import code_pb2

import proto


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
_LOGGER = base.Logger(__name__)

_PIPELINE_COMPLETE_STATES = set(
    [
        gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
        gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED,
        gca_pipeline_state.PipelineState.PIPELINE_STATE_CANCELLED,
        gca_pipeline_state.PipelineState.PIPELINE_STATE_PAUSED,
    ]
)


class _TrainingJob(base.AiPlatformResourceNounWithFutureManager):

    client_class = utils.PipelineClientWithOverride
    _is_client_prediction_client = False
    _resource_noun = "trainingPipelines"
    _getter_method = "get_training_pipeline"
    _list_method = "list_training_pipelines"
    _delete_method = "delete_training_pipeline"

    def __init__(
        self,
        display_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        training_encryption_spec_key_name: Optional[str] = None,
        model_encryption_spec_key_name: Optional[str] = None,
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
            training_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the training pipeline. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this TrainingPipeline will be secured by this key.

                Note: Model trained by this TrainingPipeline is also secured
                by this key if ``model_to_upload`` is not set separately.

                Overrides encryption_spec_key_name set in aiplatform.init.
            model_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, the trained Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
        """
        utils.validate_display_name(display_name)

        super().__init__(project=project, location=location, credentials=credentials)
        self._display_name = display_name
        self._training_encryption_spec = initializer.global_config.get_encryption_spec(
            encryption_spec_key_name=training_encryption_spec_key_name
        )
        self._model_encryption_spec = initializer.global_config.get_encryption_spec(
            encryption_spec_key_name=model_encryption_spec_key_name
        )
        self._gca_resource = None

    @property
    @classmethod
    @abc.abstractmethod
    def _supported_training_schemas(cls) -> Tuple[str]:
        """List of supported schemas for this training job."""

        pass

    @classmethod
    def get(
        cls,
        resource_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "_TrainingJob":
        """Get Training Job for the given resource_name.

        Args:
            resource_name (str):
                Required. A fully-qualified resource name or ID.
            project (str):
                Optional project to retrieve dataset from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional location to retrieve dataset from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.

        Raises:
            ValueError: If the retrieved training job's training task definition
                doesn't match the custom training task definition.

        Returns:
            An AI Platform Training Job
        """

        # Create job with dummy parameters
        # These parameters won't be used as user can not run the job again.
        # If they try, an exception will be raised.
        self = cls._empty_constructor(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=resource_name,
        )

        self._gca_resource = self._get_gca_resource(resource_name=resource_name)

        if (
            self._gca_resource.training_task_definition
            not in cls._supported_training_schemas
        ):
            raise ValueError(
                f"The retrieved job's training task definition "
                f"is {self._gca_resource.training_task_definition}, "
                f"which is not compatible with {cls.__name__}."
            )

        return self

    @property
    @abc.abstractmethod
    def _model_upload_fail_string(self) -> str:
        """Helper property for model upload failure."""

        pass

    @abc.abstractmethod
    def run(self) -> Optional[models.Model]:
        """Runs the training job.

        Should call _run_job internally
        """
        pass

    @staticmethod
    def _create_input_data_config(
        dataset: Optional[datasets._Dataset] = None,
        annotation_schema_uri: Optional[str] = None,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        predefined_split_column_name: Optional[str] = None,
        gcs_destination_uri_prefix: Optional[str] = None,
        bigquery_destination: Optional[str] = None,
    ) -> Optional[gca_training_pipeline.InputDataConfig]:
        """Constructs a input data config to pass to the training pipeline.

        Args:
            dataset (datasets._Dataset):
                The dataset within the same Project from which data will be used to train the Model. The
                Dataset must use schema compatible with Model being trained,
                and what is compatible should be described in the used
                TrainingPipeline's [training_task_definition]
                [google.cloud.aiplatform.v1beta1.TrainingPipeline.training_task_definition].
                For tabular Datasets, all their data is exported to
                training, to pick and choose from.
            annotation_schema_uri (str):
                Google Cloud Storage URI points to a YAML file describing
                annotation schema. The schema is defined as an OpenAPI 3.0.2
                [Schema Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schema-object) The schema files
                that can be used here are found in
                gs://google-cloud-aiplatform/schema/dataset/annotation/,
                note that the chosen schema must be consistent with
                ``metadata``
                of the Dataset specified by
                ``dataset_id``.

                Only Annotations that both match this schema and belong to
                DataItems not ignored by the split method are used in
                respectively training, validation or test role, depending on
                the role of the DataItem they are on.

                When used in conjunction with
                ``annotations_filter``,
                the Annotations used for training are filtered by both
                ``annotations_filter``
                and
                ``annotation_schema_uri``.
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

                Supported only for tabular and time series Datasets.
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
            bigquery_destination (str):
                The BigQuery project location where the training data is to
                be written to. In the given project a new dataset is created
                with name
                ``dataset_<dataset-id>_<annotation-type>_<timestamp-of-training-call>``
                where timestamp is in YYYY_MM_DDThh_mm_ss_sssZ format. All
                training input data will be written into that dataset. In
                the dataset three tables will be created, ``training``,
                ``validation`` and ``test``.

                -  AIP_DATA_FORMAT = "bigquery".
                -  AIP_TRAINING_DATA_URI ="bigquery_destination.dataset_*.training"
                -  AIP_VALIDATION_DATA_URI = "bigquery_destination.dataset_*.validation"
                -  AIP_TEST_DATA_URI = "bigquery_destination.dataset_*.test"
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
                if dataset._gca_resource.metadata_schema_uri not in (
                    schema.dataset.metadata.tabular,
                    schema.dataset.metadata.time_series,
                ):
                    raise ValueError(
                        "A pre-defined split may only be used with a tabular or time series Dataset"
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

            # TODO(b/177416223) validate managed BQ dataset is passed in
            bigquery_destination_proto = None
            if bigquery_destination:
                bigquery_destination_proto = gca_io.BigQueryDestination(
                    output_uri=bigquery_destination
                )

            # create input data config
            input_data_config = gca_training_pipeline.InputDataConfig(
                fraction_split=fraction_split,
                predefined_split=predefined_split,
                dataset_id=dataset.name,
                annotation_schema_uri=annotation_schema_uri,
                gcs_destination=gcs_destination,
                bigquery_destination=bigquery_destination_proto,
            )

        return input_data_config

    def _run_job(
        self,
        training_task_definition: str,
        training_task_inputs: Union[dict, proto.Message],
        dataset: Optional[datasets._Dataset],
        training_fraction_split: float,
        validation_fraction_split: float,
        test_fraction_split: float,
        annotation_schema_uri: Optional[str] = None,
        predefined_split_column_name: Optional[str] = None,
        model: Optional[gca_model.Model] = None,
        gcs_destination_uri_prefix: Optional[str] = None,
        bigquery_destination: Optional[str] = None,
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
            training_task_inputs (Union[dict, proto.Message]):
                Required. The training task's input that corresponds to the training_task_definition parameter.
            dataset (datasets._Dataset):
                The dataset within the same Project from which data will be used to train the Model. The
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
            annotation_schema_uri (str):
                Google Cloud Storage URI points to a YAML file describing
                annotation schema. The schema is defined as an OpenAPI 3.0.2
                [Schema Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schema-object) The schema files
                that can be used here are found in
                gs://google-cloud-aiplatform/schema/dataset/annotation/,
                note that the chosen schema must be consistent with
                ``metadata``
                of the Dataset specified by
                ``dataset_id``.

                Only Annotations that both match this schema and belong to
                DataItems not ignored by the split method are used in
                respectively training, validation or test role, depending on
                the role of the DataItem they are on.

                When used in conjunction with
                ``annotations_filter``,
                the Annotations used for training are filtered by both
                ``annotations_filter``
                and
                ``annotation_schema_uri``.
            predefined_split_column_name (str):
                Optional. The key is a name of one of the Dataset's data
                columns. The value of the key (either the label's value or
                value in the column) must be one of {``training``,
                ``validation``, ``test``}, and it defines to which set the
                given piece of data is assigned. If for a piece of data the
                key is not present or has an invalid value, that piece is
                ignored by the pipeline.

                Supported only for tabular and time series Datasets.
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
            bigquery_destination (str):
                The BigQuery project location where the training data is to
                be written to. In the given project a new dataset is created
                with name
                ``dataset_<dataset-id>_<annotation-type>_<timestamp-of-training-call>``
                where timestamp is in YYYY_MM_DDThh_mm_ss_sssZ format. All
                training input data will be written into that dataset. In
                the dataset three tables will be created, ``training``,
                ``validation`` and ``test``.

                -  AIP_DATA_FORMAT = "bigquery".
                -  AIP_TRAINING_DATA_URI ="bigquery_destination.dataset_*.training"
                -  AIP_VALIDATION_DATA_URI = "bigquery_destination.dataset_*.validation"
                -  AIP_TEST_DATA_URI = "bigquery_destination.dataset_*.test"
        """

        input_data_config = self._create_input_data_config(
            dataset=dataset,
            annotation_schema_uri=annotation_schema_uri,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=predefined_split_column_name,
            gcs_destination_uri_prefix=gcs_destination_uri_prefix,
            bigquery_destination=bigquery_destination,
        )

        # create training pipeline
        training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=self._display_name,
            training_task_definition=training_task_definition,
            training_task_inputs=training_task_inputs,
            model_to_upload=model,
            input_data_config=input_data_config,
            encryption_spec=self._training_encryption_spec,
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
        """Returns True if the Job is pending on upstream tasks False
        otherwise."""
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

        self._sync_gca_resource()
        return self._gca_resource.state

    def get_model(self, sync=True) -> models.Model:
        """AI Platform Model produced by this training, if one was produced.

        Args:
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: AI Platform Model produced by this training

        Raises:
            RuntimeError: If training failed or if a model was not produced by this training.
        """

        self._assert_has_run()
        if not self._gca_resource.model_to_upload:
            raise RuntimeError(self._model_upload_fail_string)

        return self._force_get_model(sync=sync)

    @base.optional_sync()
    def _force_get_model(self, sync: bool = True) -> models.Model:
        """AI Platform Model produced by this training, if one was produced.

        Args:
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: AI Platform Model produced by this training

        Raises:
            RuntimeError: If training failed or if a model was not produced by this training.
        """
        model = self._get_model()

        if model is None:
            raise RuntimeError(self._model_upload_fail_string)

        return model

    def _get_model(self) -> Optional[models.Model]:
        """Helper method to get and instantiate the Model to Upload.

        Returns:
            model: AI Platform Model if training succeeded and produced an AI Platform
                Model. None otherwise.

        Raises:
            RuntimeError: If Training failed.
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
                fields.id, project=fields.project, location=fields.location,
            )

    def _block_until_complete(self):
        """Helper method to block and check on job until complete."""

        # Used these numbers so failures surface fast
        wait = 5  # start at five seconds
        log_wait = 5
        max_wait = 60 * 5  # 5 minute wait
        multiplier = 2  # scale wait by 2 every iteration

        previous_time = time.time()
        while self.state not in _PIPELINE_COMPLETE_STATES:
            current_time = time.time()
            if current_time - previous_time >= log_wait:
                _LOGGER.info(
                    "%s %s current state:\n%s"
                    % (
                        self.__class__.__name__,
                        self._gca_resource.name,
                        self._gca_resource.state,
                    )
                )
                log_wait = min(log_wait * multiplier, max_wait)
                previous_time = current_time
            time.sleep(wait)

        self._raise_failure()

        _LOGGER.log_action_completed_against_resource("run", "completed", self)

        if self._gca_resource.model_to_upload and not self.has_failed:
            _LOGGER.info(
                "Model available at %s" % self._gca_resource.model_to_upload.name
            )

    def _raise_failure(self):
        """Helper method to raise failure if TrainingPipeline fails.

        Raises:
            RuntimeError: If training failed.
        """

        if self._gca_resource.error.code != code_pb2.OK:
            raise RuntimeError("Training failed with:\n%s" % self._gca_resource.error)

    @property
    def has_failed(self) -> bool:
        """Returns True if training has failed.

        False otherwise.
        """
        self._assert_has_run()
        return self.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED

    def _dashboard_uri(self) -> str:
        """Helper method to compose the dashboard uri where training can be
        viewed."""
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

    @classmethod
    def list(
        cls,
        filter: Optional[str] = None,
        order_by: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["base.AiPlatformResourceNoune"]:
        """List all instances of this TrainingJob resource.

        Example Usage:

        aiplatform.CustomTrainingJob.list(
            filter='display_name="experiment_a27"',
            order_by='create_time desc'
        )

        Args:
            filter (str):
                Optional. An expression for filtering the results of the request.
                For field names both snake_case and camelCase are supported.
            order_by (str):
                Optional. A comma-separated list of fields to order by, sorted in
                ascending order. Use "desc" after a field name for descending.
                Supported fields: `display_name`, `create_time`, `update_time`
            project (str):
                Optional. Project to retrieve list from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve list from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve list. Overrides
                credentials set in aiplatform.init.

        Returns:
            List[AiPlatformResourceNoun] - A list of TrainingJob resource objects
        """

        training_job_subclass_filter = (
            lambda gapic_obj: gapic_obj.training_task_definition
            in cls._supported_training_schemas
        )

        return cls._list_with_local_order(
            cls_filter=training_job_subclass_filter,
            filter=filter,
            order_by=order_by,
            project=project,
            location=location,
            credentials=credentials,
        )

    def cancel(self) -> None:
        """Starts asynchronous cancellation on the TrainingJob. The server
        makes a best effort to cancel the job, but success is not guaranteed.
        On successful cancellation, the TrainingJob is not deleted; instead it
        becomes a job with state set to `CANCELLED`.

        Raises:
            RuntimeError: If this TrainingJob has not started running.
        """
        if not self._has_run:
            raise RuntimeError(
                "This TrainingJob has not been launched, use the `run()` method "
                "to start. `cancel()` can only be called on a job that is running."
            )
        self.api_client.cancel_training_pipeline(name=self.resource_name)


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

    Returns:
        Python executable to use for setuptools packaging.
    Raises:
        EnvironmentError: If Python executable is not found.
    """

    python_executable = sys.executable

    if not python_executable:
        raise EnvironmentError("Cannot find Python executable for packaging.")
    return python_executable


class _TrainingScriptPythonPackager:
    """Converts a Python script into Python package suitable for aiplatform
    training.

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

    _SETUP_PY_SOURCE_DISTRIBUTION_CMD = "setup.py sdist --formats=gztar"

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
        """Converts script into a Python package suitable for python module
        execution.

        Args:
            package_directory (str): Directory to build package in.
        Returns:
            source_distribution_path (str): Path to built package.
        Raises:
            RunTimeError: If package creation fails.
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
        setup_cmd = [
            _get_python_executable()
        ] + self._SETUP_PY_SOURCE_DISTRIBUTION_CMD.split()

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

        # Raises ValueError if invalid accelerator_type
        utils.validate_accelerator_type(self.accelerator_type)

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
        """Return each pools spec in correct order for AI Platform as a list of
        dicts.

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
                NVIDIA_TESLA_T4
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


class _CustomTrainingJob(_TrainingJob):
    """ABC for Custom Training Pipelines.."""

    _supported_training_schemas = (schema.training_job.definition.custom_task,)

    def __init__(
        self,
        display_name: str,
        container_uri: str,
        model_serving_container_image_uri: Optional[str] = None,
        model_serving_container_predict_route: Optional[str] = None,
        model_serving_container_health_route: Optional[str] = None,
        model_serving_container_command: Optional[Sequence[str]] = None,
        model_serving_container_args: Optional[Sequence[str]] = None,
        model_serving_container_environment_variables: Optional[Dict[str, str]] = None,
        model_serving_container_ports: Optional[Sequence[int]] = None,
        model_description: Optional[str] = None,
        model_instance_schema_uri: Optional[str] = None,
        model_parameters_schema_uri: Optional[str] = None,
        model_prediction_schema_uri: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        training_encryption_spec_key_name: Optional[str] = None,
        model_encryption_spec_key_name: Optional[str] = None,
        staging_bucket: Optional[str] = None,
    ):
        """
        Args:
            display_name (str):
                Required. The user-defined name of this TrainingPipeline.
            container_uri (str):
                Required: Uri of the training container image in the GCR.
            model_serving_container_image_uri (str):
                If the training produces a managed AI Platform Model, the URI of the
                Model serving container suitable for serving the model produced by the
                training script.
            model_serving_container_predict_route (str):
                If the training produces a managed AI Platform Model, An HTTP path to
                send prediction requests to the container, and which must be supported
                by it. If not specified a default HTTP path will be used by AI Platform.
            model_serving_container_health_route (str):
                If the training produces a managed AI Platform Model, an HTTP path to
                send health check requests to the container, and which must be supported
                by it. If not specified a standard HTTP path will be used by AI
                Platform.
            model_serving_container_command (Sequence[str]):
                The command with which the container is run. Not executed within a
                shell. The Docker image's ENTRYPOINT is used if this is not provided.
                Variable references $(VAR_NAME) are expanded using the container's
                environment. If a variable cannot be resolved, the reference in the
                input string will be unchanged. The $(VAR_NAME) syntax can be escaped
                with a double $$, ie: $$(VAR_NAME). Escaped references will never be
                expanded, regardless of whether the variable exists or not.
            model_serving_container_args (Sequence[str]):
                The arguments to the command. The Docker image's CMD is used if this is
                not provided. Variable references $(VAR_NAME) are expanded using the
                container's environment. If a variable cannot be resolved, the reference
                in the input string will be unchanged. The $(VAR_NAME) syntax can be
                escaped with a double $$, ie: $$(VAR_NAME). Escaped references will
                never be expanded, regardless of whether the variable exists or not.
            model_serving_container_environment_variables (Dict[str, str]):
                The environment variables that are to be present in the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
            model_serving_container_ports (Sequence[int]):
                Declaration of ports that are exposed by the container. This field is
                primarily informational, it gives AI Platform information about the
                network connections the container uses. Listing or not a port here has
                no impact on whether the port is actually exposed, any port listening on
                the default "0.0.0.0" address inside a container will be accessible from
                the network.
            model_description (str):
                The description of the Model.
            model_instance_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the format of a single instance, which
                are used in
                ``PredictRequest.instances``,
                ``ExplainRequest.instances``
                and
                ``BatchPredictionJob.input_config``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform. Note: The URI given on output will be immutable
                and probably different, including the URI scheme, than the
                one given on input. The output URI will point to a location
                where the user only has a read access.
            model_parameters_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the parameters of prediction and
                explanation via
                ``PredictRequest.parameters``,
                ``ExplainRequest.parameters``
                and
                ``BatchPredictionJob.model_parameters``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform, if no parameters are supported it is set to an
                empty string. Note: The URI given on output will be
                immutable and probably different, including the URI scheme,
                than the one given on input. The output URI will point to a
                location where the user only has a read access.
            model_prediction_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the format of a single prediction
                produced by this Model, which are returned via
                ``PredictResponse.predictions``,
                ``ExplainResponse.explanations``,
                and
                ``BatchPredictionJob.output_config``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform. Note: The URI given on output will be immutable
                and probably different, including the URI scheme, than the
                one given on input. The output URI will point to a location
                where the user only has a read access.
            project (str):
                Project to run training in. Overrides project set in aiplatform.init.
            location (str):
                Location to run training in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to run call training service. Overrides
                credentials set in aiplatform.init.
            training_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the training pipeline. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this TrainingPipeline will be secured by this key.

                Note: Model trained by this TrainingPipeline is also secured
                by this key if ``model_to_upload`` is not set separately.

                Overrides encryption_spec_key_name set in aiplatform.init.
            model_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, the trained Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
            staging_bucket (str):
                Bucket used to stage source and training artifacts. Overrides
                staging_bucket set in aiplatform.init.
        """
        super().__init__(
            display_name=display_name,
            project=project,
            location=location,
            credentials=credentials,
            training_encryption_spec_key_name=training_encryption_spec_key_name,
            model_encryption_spec_key_name=model_encryption_spec_key_name,
        )

        self._container_uri = container_uri

        model_predict_schemata = None
        if any(
            [
                model_instance_schema_uri,
                model_parameters_schema_uri,
                model_prediction_schema_uri,
            ]
        ):
            model_predict_schemata = gca_model.PredictSchemata(
                instance_schema_uri=model_instance_schema_uri,
                parameters_schema_uri=model_parameters_schema_uri,
                prediction_schema_uri=model_prediction_schema_uri,
            )

        # Create the container spec
        env = None
        ports = None

        if model_serving_container_environment_variables:
            env = [
                gca_env_var.EnvVar(name=str(key), value=str(value))
                for key, value in model_serving_container_environment_variables.items()
            ]

        if model_serving_container_ports:
            ports = [
                gca_model.Port(container_port=port)
                for port in model_serving_container_ports
            ]

        container_spec = gca_model.ModelContainerSpec(
            image_uri=model_serving_container_image_uri,
            command=model_serving_container_command,
            args=model_serving_container_args,
            env=env,
            ports=ports,
            predict_route=model_serving_container_predict_route,
            health_route=model_serving_container_health_route,
        )

        # create model payload
        self._managed_model = gca_model.Model(
            description=model_description,
            predict_schemata=model_predict_schemata,
            container_spec=container_spec,
            encryption_spec=self._model_encryption_spec,
        )

        self._staging_bucket = (
            staging_bucket or initializer.global_config.staging_bucket
        )

        if not self._staging_bucket:
            raise RuntimeError(
                "staging_bucket should be set in TrainingJob constructor or "
                "set using aiplatform.init(staging_bucket='gs://my-bucket')"
            )

    def _prepare_and_validate_run(
        self,
        model_display_name: Optional[str] = None,
        replica_count: int = 0,
        machine_type: str = "n1-standard-4",
        accelerator_type: str = "ACCELERATOR_TYPE_UNSPECIFIED",
        accelerator_count: int = 0,
    ) -> Tuple[_DistributedTrainingSpec, Optional[gca_model.Model]]:
        """Create worker pool specs and managed model as well validating the
        run.

        Args:
            model_display_name (str):
                If the script produces a managed AI Platform Model. The display name of
                the Model. The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.

                If not provided upon creation, the job's display_name is used.
            replica_count (int):
                The number of worker replicas. If replica count = 1 then one chief
                replica will be provisioned. If replica_count > 1 the remainder will be
                provisioned as a worker replica pool.
            machine_type (str):
                The type of machine to use for training.
            accelerator_type (str):
                Hardware accelerator type. One of ACCELERATOR_TYPE_UNSPECIFIED,
                NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100, NVIDIA_TESLA_P4,
                NVIDIA_TESLA_T4
            accelerator_count (int):
                The number of accelerators to attach to a worker replica.
        Returns:
            Worker pools specs and managed model for run.

        Raises:
            RuntimeError: If Training job has already been run or model_display_name was
                provided but required arguments were not provided in constructor.
        """

        if self._is_waiting_to_run():
            raise RuntimeError("Custom Training is already scheduled to run.")

        if self._has_run:
            raise RuntimeError("Custom Training has already run.")

        # if args needed for model is incomplete
        if model_display_name and not self._managed_model.container_spec.image_uri:
            raise RuntimeError(
                """model_display_name was provided but
                model_serving_container_image_uri was not provided when this
                custom pipeline was constructed.
                """
            )

        if self._managed_model.container_spec.image_uri:
            model_display_name = model_display_name or self._display_name + "-model"

        # validates args and will raise
        worker_pool_specs = _DistributedTrainingSpec.chief_worker_pool(
            replica_count=replica_count,
            machine_type=machine_type,
            accelerator_count=accelerator_count,
            accelerator_type=accelerator_type,
        ).pool_specs

        managed_model = self._managed_model
        if model_display_name:
            utils.validate_display_name(model_display_name)
            managed_model.display_name = model_display_name
        else:
            managed_model = None

        return worker_pool_specs, managed_model

    def _prepare_training_task_inputs_and_output_dir(
        self,
        worker_pool_specs: _DistributedTrainingSpec,
        base_output_dir: Optional[str] = None,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
    ) -> Tuple[Dict, str]:
        """Prepares training task inputs and output directory for custom job.

        Args:
            worker_pools_spec (_DistributedTrainingSpec):
                Worker pools pecs required to run job.
            base_output_dir (str):
                GCS output directory of job. If not provided a
                timestamped directory in the staging directory will be used.
            service_account (str):
                Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
        Returns:
            Training task inputs and Output directory for custom job.
        """

        # default directory if not given
        base_output_dir = base_output_dir or _timestamped_gcs_dir(
            self._staging_bucket, "aiplatform-custom-training"
        )

        _LOGGER.info("Training Output directory:\n%s " % base_output_dir)

        training_task_inputs = {
            "workerPoolSpecs": worker_pool_specs,
            "baseOutputDirectory": {"output_uri_prefix": base_output_dir},
        }

        if service_account:
            training_task_inputs["serviceAccount"] = service_account
        if network:
            training_task_inputs["network"] = network

        return training_task_inputs, base_output_dir

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


# TODO(b/172368325) add scheduling, custom_job.Scheduling
class CustomTrainingJob(_CustomTrainingJob):
    """Class to launch a Custom Training Job in AI Platform using a script.

    Takes a training implementation as a python script and executes that
    script in Cloud AI Platform Training.
    """

    def __init__(
        self,
        display_name: str,
        script_path: str,
        container_uri: str,
        requirements: Optional[Sequence[str]] = None,
        model_serving_container_image_uri: Optional[str] = None,
        model_serving_container_predict_route: Optional[str] = None,
        model_serving_container_health_route: Optional[str] = None,
        model_serving_container_command: Optional[Sequence[str]] = None,
        model_serving_container_args: Optional[Sequence[str]] = None,
        model_serving_container_environment_variables: Optional[Dict[str, str]] = None,
        model_serving_container_ports: Optional[Sequence[int]] = None,
        model_description: Optional[str] = None,
        model_instance_schema_uri: Optional[str] = None,
        model_parameters_schema_uri: Optional[str] = None,
        model_prediction_schema_uri: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        training_encryption_spec_key_name: Optional[str] = None,
        model_encryption_spec_key_name: Optional[str] = None,
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

        ds = aiplatform.TabularDataset(
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
            model_serving_container_predict_route (str):
                If the training produces a managed AI Platform Model, An HTTP path to
                send prediction requests to the container, and which must be supported
                by it. If not specified a default HTTP path will be used by AI Platform.
            model_serving_container_health_route (str):
                If the training produces a managed AI Platform Model, an HTTP path to
                send health check requests to the container, and which must be supported
                by it. If not specified a standard HTTP path will be used by AI
                Platform.
            model_serving_container_command (Sequence[str]):
                The command with which the container is run. Not executed within a
                shell. The Docker image's ENTRYPOINT is used if this is not provided.
                Variable references $(VAR_NAME) are expanded using the container's
                environment. If a variable cannot be resolved, the reference in the
                input string will be unchanged. The $(VAR_NAME) syntax can be escaped
                with a double $$, ie: $$(VAR_NAME). Escaped references will never be
                expanded, regardless of whether the variable exists or not.
            model_serving_container_args (Sequence[str]):
                The arguments to the command. The Docker image's CMD is used if this is
                not provided. Variable references $(VAR_NAME) are expanded using the
                container's environment. If a variable cannot be resolved, the reference
                in the input string will be unchanged. The $(VAR_NAME) syntax can be
                escaped with a double $$, ie: $$(VAR_NAME). Escaped references will
                never be expanded, regardless of whether the variable exists or not.
            model_serving_container_environment_variables (Dict[str, str]):
                The environment variables that are to be present in the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
            model_serving_container_ports (Sequence[int]):
                Declaration of ports that are exposed by the container. This field is
                primarily informational, it gives AI Platform information about the
                network connections the container uses. Listing or not a port here has
                no impact on whether the port is actually exposed, any port listening on
                the default "0.0.0.0" address inside a container will be accessible from
                the network.
            model_description (str):
                The description of the Model.
            model_instance_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the format of a single instance, which
                are used in
                ``PredictRequest.instances``,
                ``ExplainRequest.instances``
                and
                ``BatchPredictionJob.input_config``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform. Note: The URI given on output will be immutable
                and probably different, including the URI scheme, than the
                one given on input. The output URI will point to a location
                where the user only has a read access.
            model_parameters_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the parameters of prediction and
                explanation via
                ``PredictRequest.parameters``,
                ``ExplainRequest.parameters``
                and
                ``BatchPredictionJob.model_parameters``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform, if no parameters are supported it is set to an
                empty string. Note: The URI given on output will be
                immutable and probably different, including the URI scheme,
                than the one given on input. The output URI will point to a
                location where the user only has a read access.
            model_prediction_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the format of a single prediction
                produced by this Model, which are returned via
                ``PredictResponse.predictions``,
                ``ExplainResponse.explanations``,
                and
                ``BatchPredictionJob.output_config``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform. Note: The URI given on output will be immutable
                and probably different, including the URI scheme, than the
                one given on input. The output URI will point to a location
                where the user only has a read access.
            project (str):
                Project to run training in. Overrides project set in aiplatform.init.
            location (str):
                Location to run training in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to run call training service. Overrides
                credentials set in aiplatform.init.
            training_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the training pipeline. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this TrainingPipeline will be secured by this key.

                Note: Model trained by this TrainingPipeline is also secured
                by this key if ``model_to_upload`` is not set separately.

                Overrides encryption_spec_key_name set in aiplatform.init.
            model_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, the trained Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
            staging_bucket (str):
                Bucket used to stage source and training artifacts. Overrides
                staging_bucket set in aiplatform.init.
        """
        super().__init__(
            display_name=display_name,
            project=project,
            location=location,
            credentials=credentials,
            training_encryption_spec_key_name=training_encryption_spec_key_name,
            model_encryption_spec_key_name=model_encryption_spec_key_name,
            container_uri=container_uri,
            model_instance_schema_uri=model_instance_schema_uri,
            model_parameters_schema_uri=model_parameters_schema_uri,
            model_prediction_schema_uri=model_prediction_schema_uri,
            model_serving_container_environment_variables=model_serving_container_environment_variables,
            model_serving_container_ports=model_serving_container_ports,
            model_serving_container_image_uri=model_serving_container_image_uri,
            model_serving_container_command=model_serving_container_command,
            model_serving_container_args=model_serving_container_args,
            model_serving_container_predict_route=model_serving_container_predict_route,
            model_serving_container_health_route=model_serving_container_health_route,
            model_description=model_description,
            staging_bucket=staging_bucket,
        )

        self._requirements = requirements
        self._script_path = script_path

    # TODO(b/172365904) add filter split, training_pipeline.FilterSplit
    # TODO(b/172368070) add timestamp split, training_pipeline.TimestampSplit
    def run(
        self,
        dataset: Optional[
            Union[
                datasets.ImageDataset,
                datasets.TabularDataset,
                datasets.TextDataset,
                datasets.VideoDataset,
            ]
        ] = None,
        annotation_schema_uri: Optional[str] = None,
        model_display_name: Optional[str] = None,
        base_output_dir: Optional[str] = None,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        bigquery_destination: Optional[str] = None,
        args: Optional[List[Union[str, float, int]]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
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
            dataset (
                Union[
                    datasets.ImageDataset,
                    datasets.TabularDataset,
                    datasets.TextDataset,
                    datasets.VideoDataset,
                ]
            ):
                AI Platform to fit this training against. Custom training script should
                retrieve datasets through passed in environment variables uris:

                os.environ["AIP_TRAINING_DATA_URI"]
                os.environ["AIP_VALIDATION_DATA_URI"]
                os.environ["AIP_TEST_DATA_URI"]

                Additionally the dataset format is passed in as:

                os.environ["AIP_DATA_FORMAT"]
            annotation_schema_uri (str):
                Google Cloud Storage URI points to a YAML file describing
                annotation schema. The schema is defined as an OpenAPI 3.0.2
                [Schema Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schema-object) The schema files
                that can be used here are found in
                gs://google-cloud-aiplatform/schema/dataset/annotation/,
                note that the chosen schema must be consistent with
                ``metadata``
                of the Dataset specified by
                ``dataset_id``.

                Only Annotations that both match this schema and belong to
                DataItems not ignored by the split method are used in
                respectively training, validation or test role, depending on
                the role of the DataItem they are on.

                When used in conjunction with
                ``annotations_filter``,
                the Annotations used for training are filtered by both
                ``annotations_filter``
                and
                ``annotation_schema_uri``.
            model_display_name (str):
                If the script produces a managed AI Platform Model. The display name of
                the Model. The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.

                If not provided upon creation, the job's display_name is used.
            base_output_dir (str):
                GCS output directory of job. If not provided a
                timestamped directory in the staging directory will be used.

                AI Platform sets the following environment variables when it runs your training code:

                -  AIP_MODEL_DIR: a Cloud Storage URI of a directory intended for saving model artifacts, i.e. <base_output_dir>/model/
                -  AIP_CHECKPOINT_DIR: a Cloud Storage URI of a directory intended for saving checkpoints, i.e. <base_output_dir>/checkpoints/
                -  AIP_TENSORBOARD_LOG_DIR: a Cloud Storage URI of a directory intended for saving TensorBoard logs, i.e. <base_output_dir>/logs/

            service_account (str):
                Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
            bigquery_destination (str):
                Provide this field if `dataset` is a BiqQuery dataset.
                The BigQuery project location where the training data is to
                be written to. In the given project a new dataset is created
                with name
                ``dataset_<dataset-id>_<annotation-type>_<timestamp-of-training-call>``
                where timestamp is in YYYY_MM_DDThh_mm_ss_sssZ format. All
                training input data will be written into that dataset. In
                the dataset three tables will be created, ``training``,
                ``validation`` and ``test``.

                -  AIP_DATA_FORMAT = "bigquery".
                -  AIP_TRAINING_DATA_URI ="bigquery_destination.dataset_*.training"
                -  AIP_VALIDATION_DATA_URI = "bigquery_destination.dataset_*.validation"
                -  AIP_TEST_DATA_URI = "bigquery_destination.dataset_*.test"
            args (List[Unions[str, int, float]]):
                Command line arguments to be passed to the Python script.
            environment_variables (Dict[str, str]):
                Environment variables to be passed to the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
                At most 10 environment variables can be specified.
                The Name of the environment variable must be unique.

                environment_variables = {
                    'MY_KEY': 'MY_VALUE'
                }
            replica_count (int):
                The number of worker replicas. If replica count = 1 then one chief
                replica will be provisioned. If replica_count > 1 the remainder will be
                provisioned as a worker replica pool.
            machine_type (str):
                The type of machine to use for training.
            accelerator_type (str):
                Hardware accelerator type. One of ACCELERATOR_TYPE_UNSPECIFIED,
                NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100, NVIDIA_TESLA_P4,
                NVIDIA_TESLA_T4
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

                Supported only for tabular and time series Datasets.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """
        worker_pool_specs, managed_model = self._prepare_and_validate_run(
            model_display_name=model_display_name,
            replica_count=replica_count,
            machine_type=machine_type,
            accelerator_count=accelerator_count,
            accelerator_type=accelerator_type,
        )

        # make and copy package
        python_packager = _TrainingScriptPythonPackager(
            script_path=self._script_path, requirements=self._requirements
        )

        return self._run(
            python_packager=python_packager,
            dataset=dataset,
            annotation_schema_uri=annotation_schema_uri,
            worker_pool_specs=worker_pool_specs,
            managed_model=managed_model,
            args=args,
            environment_variables=environment_variables,
            base_output_dir=base_output_dir,
            service_account=service_account,
            network=network,
            bigquery_destination=bigquery_destination,
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
        dataset: Optional[
            Union[
                datasets.ImageDataset,
                datasets.TabularDataset,
                datasets.TextDataset,
                datasets.VideoDataset,
            ]
        ],
        annotation_schema_uri: Optional[str],
        worker_pool_specs: _DistributedTrainingSpec,
        managed_model: Optional[gca_model.Model] = None,
        args: Optional[List[Union[str, float, int]]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        base_output_dir: Optional[str] = None,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        bigquery_destination: Optional[str] = None,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        predefined_split_column_name: Optional[str] = None,
        sync=True,
    ) -> Optional[models.Model]:
        """Packages local script and launches training_job.

        Args:
            python_packager (_TrainingScriptPythonPackager):
                Required. Python Packager pointing to training script locally.
            dataset (
                Union[
                    datasets.ImageDataset,
                    datasets.TabularDataset,
                    datasets.TextDataset,
                    datasets.VideoDataset,
                ]
            ):
                AI Platform to fit this training against.
            annotation_schema_uri (str):
                Google Cloud Storage URI points to a YAML file describing
                annotation schema.
            worker_pools_spec (_DistributedTrainingSpec):
                Worker pools pecs required to run job.
            managed_model (gca_model.Model):
                Model proto if this script produces a Managed Model.
            args (List[Unions[str, int, float]]):
                Command line arguments to be passed to the Python script.
            environment_variables (Dict[str, str]):
                Environment variables to be passed to the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
                At most 10 environment variables can be specified.
                The Name of the environment variable must be unique.

                environment_variables = {
                    'MY_KEY': 'MY_VALUE'
                }
            base_output_dir (str):
                GCS output directory of job. If not provided a
                timestamped directory in the staging directory will be used.

                AI Platform sets the following environment variables when it runs your training code:

                -  AIP_MODEL_DIR: a Cloud Storage URI of a directory intended for saving model artifacts, i.e. <base_output_dir>/model/
                -  AIP_CHECKPOINT_DIR: a Cloud Storage URI of a directory intended for saving checkpoints, i.e. <base_output_dir>/checkpoints/
                -  AIP_TENSORBOARD_LOG_DIR: a Cloud Storage URI of a directory intended for saving TensorBoard logs, i.e. <base_output_dir>/logs/

            service_account (str):
                Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
            bigquery_destination (str):
                Provide this field if `dataset` is a BiqQuery dataset.
                The BigQuery project location where the training data is to
                be written to. In the given project a new dataset is created
                with name
                ``dataset_<dataset-id>_<annotation-type>_<timestamp-of-training-call>``
                where timestamp is in YYYY_MM_DDThh_mm_ss_sssZ format. All
                training input data will be written into that dataset. In
                the dataset three tables will be created, ``training``,
                ``validation`` and ``test``.

                -  AIP_DATA_FORMAT = "bigquery".
                -  AIP_TRAINING_DATA_URI ="bigquery_destination.dataset_*.training"
                -  AIP_VALIDATION_DATA_URI = "bigquery_destination.dataset_*.validation"
                -  AIP_TEST_DATA_URI = "bigquery_destination.dataset_*.test"
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

                Supported only for tabular and time series Datasets.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """
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

            if environment_variables:
                spec["pythonPackageSpec"]["env"] = [
                    {"name": key, "value": value}
                    for key, value in environment_variables.items()
                ]

        (
            training_task_inputs,
            base_output_dir,
        ) = self._prepare_training_task_inputs_and_output_dir(
            worker_pool_specs=worker_pool_specs,
            base_output_dir=base_output_dir,
            service_account=service_account,
            network=network,
        )

        model = self._run_job(
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=training_task_inputs,
            dataset=dataset,
            annotation_schema_uri=annotation_schema_uri,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=predefined_split_column_name,
            model=managed_model,
            gcs_destination_uri_prefix=base_output_dir,
            bigquery_destination=bigquery_destination,
        )

        return model


class CustomContainerTrainingJob(_CustomTrainingJob):
    """Class to launch a Custom Training Job in AI Platform using a
    Container."""

    def __init__(
        self,
        display_name: str,
        container_uri: str,
        command: Sequence[str] = None,
        model_serving_container_image_uri: Optional[str] = None,
        model_serving_container_predict_route: Optional[str] = None,
        model_serving_container_health_route: Optional[str] = None,
        model_serving_container_command: Optional[Sequence[str]] = None,
        model_serving_container_args: Optional[Sequence[str]] = None,
        model_serving_container_environment_variables: Optional[Dict[str, str]] = None,
        model_serving_container_ports: Optional[Sequence[int]] = None,
        model_description: Optional[str] = None,
        model_instance_schema_uri: Optional[str] = None,
        model_parameters_schema_uri: Optional[str] = None,
        model_prediction_schema_uri: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        training_encryption_spec_key_name: Optional[str] = None,
        model_encryption_spec_key_name: Optional[str] = None,
        staging_bucket: Optional[str] = None,
    ):
        """Constructs a Custom Container Training Job.

        job = aiplatform.CustomTrainingJob(
            display_name='test-train',
            container_uri='gcr.io/cloud-aiplatform/training/tf-cpu.2-2:latest',
            command=['python3', 'run_script.py']
            model_serving_container_image_uri='gcr.io/my-trainer/serving:1',
            model_serving_container_predict_route='predict',
            model_serving_container_health_route='metadata)

        Usage with Dataset:

        ds = aiplatform.TabularDataset(
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
            container_uri (str):
                Required: Uri of the training container image in the GCR.
            command (Sequence[str]):
                The command to be invoked when the container is started.
                It overrides the entrypoint instruction in Dockerfile when provided
            model_serving_container_image_uri (str):
                If the training produces a managed AI Platform Model, the URI of the
                Model serving container suitable for serving the model produced by the
                training script.
            model_serving_container_predict_route (str):
                If the training produces a managed AI Platform Model, An HTTP path to
                send prediction requests to the container, and which must be supported
                by it. If not specified a default HTTP path will be used by AI Platform.
            model_serving_container_health_route (str):
                If the training produces a managed AI Platform Model, an HTTP path to
                send health check requests to the container, and which must be supported
                by it. If not specified a standard HTTP path will be used by AI
                Platform.
            model_serving_container_command (Sequence[str]):
                The command with which the container is run. Not executed within a
                shell. The Docker image's ENTRYPOINT is used if this is not provided.
                Variable references $(VAR_NAME) are expanded using the container's
                environment. If a variable cannot be resolved, the reference in the
                input string will be unchanged. The $(VAR_NAME) syntax can be escaped
                with a double $$, ie: $$(VAR_NAME). Escaped references will never be
                expanded, regardless of whether the variable exists or not.
            model_serving_container_args (Sequence[str]):
                The arguments to the command. The Docker image's CMD is used if this is
                not provided. Variable references $(VAR_NAME) are expanded using the
                container's environment. If a variable cannot be resolved, the reference
                in the input string will be unchanged. The $(VAR_NAME) syntax can be
                escaped with a double $$, ie: $$(VAR_NAME). Escaped references will
                never be expanded, regardless of whether the variable exists or not.
            model_serving_container_environment_variables (Dict[str, str]):
                The environment variables that are to be present in the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
            model_serving_container_ports (Sequence[int]):
                Declaration of ports that are exposed by the container. This field is
                primarily informational, it gives AI Platform information about the
                network connections the container uses. Listing or not a port here has
                no impact on whether the port is actually exposed, any port listening on
                the default "0.0.0.0" address inside a container will be accessible from
                the network.
            model_description (str):
                The description of the Model.
            model_instance_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the format of a single instance, which
                are used in
                ``PredictRequest.instances``,
                ``ExplainRequest.instances``
                and
                ``BatchPredictionJob.input_config``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform. Note: The URI given on output will be immutable
                and probably different, including the URI scheme, than the
                one given on input. The output URI will point to a location
                where the user only has a read access.
            model_parameters_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the parameters of prediction and
                explanation via
                ``PredictRequest.parameters``,
                ``ExplainRequest.parameters``
                and
                ``BatchPredictionJob.model_parameters``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform, if no parameters are supported it is set to an
                empty string. Note: The URI given on output will be
                immutable and probably different, including the URI scheme,
                than the one given on input. The output URI will point to a
                location where the user only has a read access.
            model_prediction_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the format of a single prediction
                produced by this Model, which are returned via
                ``PredictResponse.predictions``,
                ``ExplainResponse.explanations``,
                and
                ``BatchPredictionJob.output_config``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform. Note: The URI given on output will be immutable
                and probably different, including the URI scheme, than the
                one given on input. The output URI will point to a location
                where the user only has a read access.
            project (str):
                Project to run training in. Overrides project set in aiplatform.init.
            location (str):
                Location to run training in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to run call training service. Overrides
                credentials set in aiplatform.init.
            training_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the training pipeline. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this TrainingPipeline will be secured by this key.

                Note: Model trained by this TrainingPipeline is also secured
                by this key if ``model_to_upload`` is not set separately.

                Overrides encryption_spec_key_name set in aiplatform.init.
            model_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, the trained Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
            staging_bucket (str):
                Bucket used to stage source and training artifacts. Overrides
                staging_bucket set in aiplatform.init.
        """
        super().__init__(
            display_name=display_name,
            project=project,
            location=location,
            credentials=credentials,
            training_encryption_spec_key_name=training_encryption_spec_key_name,
            model_encryption_spec_key_name=model_encryption_spec_key_name,
            container_uri=container_uri,
            model_instance_schema_uri=model_instance_schema_uri,
            model_parameters_schema_uri=model_parameters_schema_uri,
            model_prediction_schema_uri=model_prediction_schema_uri,
            model_serving_container_environment_variables=model_serving_container_environment_variables,
            model_serving_container_ports=model_serving_container_ports,
            model_serving_container_image_uri=model_serving_container_image_uri,
            model_serving_container_command=model_serving_container_command,
            model_serving_container_args=model_serving_container_args,
            model_serving_container_predict_route=model_serving_container_predict_route,
            model_serving_container_health_route=model_serving_container_health_route,
            model_description=model_description,
            staging_bucket=staging_bucket,
        )

        self._command = command

    # TODO(b/172365904) add filter split, training_pipeline.FilterSplit
    # TODO(b/172368070) add timestamp split, training_pipeline.TimestampSplit
    def run(
        self,
        dataset: Optional[
            Union[
                datasets.ImageDataset,
                datasets.TabularDataset,
                datasets.TextDataset,
                datasets.VideoDataset,
            ]
        ] = None,
        annotation_schema_uri: Optional[str] = None,
        model_display_name: Optional[str] = None,
        base_output_dir: Optional[str] = None,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        bigquery_destination: Optional[str] = None,
        args: Optional[List[Union[str, float, int]]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
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
        decided by AI Platform. If none of the fractions are set, by default roughly 80%
        of data will be used for training, 10% for validation, and 10% for test.

        Args:
            dataset (Union[datasets.ImageDataset,datasets.TabularDataset,datasets.TextDataset,datasets.VideoDataset]):
                AI Platform to fit this training against. Custom training script should
                retrieve datasets through passed in environment variables uris:

                os.environ["AIP_TRAINING_DATA_URI"]
                os.environ["AIP_VALIDATION_DATA_URI"]
                os.environ["AIP_TEST_DATA_URI"]

                Additionally the dataset format is passed in as:

                os.environ["AIP_DATA_FORMAT"]
            annotation_schema_uri (str):
                Google Cloud Storage URI points to a YAML file describing
                annotation schema. The schema is defined as an OpenAPI 3.0.2
                [Schema Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schema-object) The schema files
                that can be used here are found in
                gs://google-cloud-aiplatform/schema/dataset/annotation/,
                note that the chosen schema must be consistent with
                ``metadata``
                of the Dataset specified by
                ``dataset_id``.

                Only Annotations that both match this schema and belong to
                DataItems not ignored by the split method are used in
                respectively training, validation or test role, depending on
                the role of the DataItem they are on.

                When used in conjunction with
                ``annotations_filter``,
                the Annotations used for training are filtered by both
                ``annotations_filter``
                and
                ``annotation_schema_uri``.
            model_display_name (str):
                If the script produces a managed AI Platform Model. The display name of
                the Model. The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.

                If not provided upon creation, the job's display_name is used.
            base_output_dir (str):
                GCS output directory of job. If not provided a
                timestamped directory in the staging directory will be used.

                AI Platform sets the following environment variables when it runs your training code:

                -  AIP_MODEL_DIR: a Cloud Storage URI of a directory intended for saving model artifacts, i.e. <base_output_dir>/model/
                -  AIP_CHECKPOINT_DIR: a Cloud Storage URI of a directory intended for saving checkpoints, i.e. <base_output_dir>/checkpoints/
                -  AIP_TENSORBOARD_LOG_DIR: a Cloud Storage URI of a directory intended for saving TensorBoard logs, i.e. <base_output_dir>/logs/

            service_account (str):
                Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
            bigquery_destination (str):
                Provide this field if `dataset` is a BiqQuery dataset.
                The BigQuery project location where the training data is to
                be written to. In the given project a new dataset is created
                with name
                ``dataset_<dataset-id>_<annotation-type>_<timestamp-of-training-call>``
                where timestamp is in YYYY_MM_DDThh_mm_ss_sssZ format. All
                training input data will be written into that dataset. In
                the dataset three tables will be created, ``training``,
                ``validation`` and ``test``.

                -  AIP_DATA_FORMAT = "bigquery".
                -  AIP_TRAINING_DATA_URI ="bigquery_destination.dataset_*.training"
                -  AIP_VALIDATION_DATA_URI = "bigquery_destination.dataset_*.validation"
                -  AIP_TEST_DATA_URI = "bigquery_destination.dataset_*.test"
            args (List[Unions[str, int, float]]):
                Command line arguments to be passed to the Python script.
            environment_variables (Dict[str, str]):
                Environment variables to be passed to the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
                At most 10 environment variables can be specified.
                The Name of the environment variable must be unique.

                environment_variables = {
                    'MY_KEY': 'MY_VALUE'
                }
            replica_count (int):
                The number of worker replicas. If replica count = 1 then one chief
                replica will be provisioned. If replica_count > 1 the remainder will be
                provisioned as a worker replica pool.
            machine_type (str):
                The type of machine to use for training.
            accelerator_type (str):
                Hardware accelerator type. One of ACCELERATOR_TYPE_UNSPECIFIED,
                NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100, NVIDIA_TESLA_P4,
                NVIDIA_TESLA_T4
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

                Supported only for tabular and time series Datasets.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.

        Raises:
            RuntimeError: If Training job has already been run, staging_bucket has not
                been set, or model_display_name was provided but required arguments
                were not provided in constructor.
        """
        worker_pool_specs, managed_model = self._prepare_and_validate_run(
            model_display_name=model_display_name,
            replica_count=replica_count,
            machine_type=machine_type,
            accelerator_count=accelerator_count,
            accelerator_type=accelerator_type,
        )

        return self._run(
            dataset=dataset,
            annotation_schema_uri=annotation_schema_uri,
            worker_pool_specs=worker_pool_specs,
            managed_model=managed_model,
            args=args,
            environment_variables=environment_variables,
            base_output_dir=base_output_dir,
            service_account=service_account,
            network=network,
            bigquery_destination=bigquery_destination,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=predefined_split_column_name,
            sync=sync,
        )

    @base.optional_sync(construct_object_on_arg="managed_model")
    def _run(
        self,
        dataset: Optional[
            Union[
                datasets.ImageDataset,
                datasets.TabularDataset,
                datasets.TextDataset,
                datasets.VideoDataset,
            ]
        ],
        annotation_schema_uri: Optional[str],
        worker_pool_specs: _DistributedTrainingSpec,
        managed_model: Optional[gca_model.Model] = None,
        args: Optional[List[Union[str, float, int]]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        base_output_dir: Optional[str] = None,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        bigquery_destination: Optional[str] = None,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        predefined_split_column_name: Optional[str] = None,
        sync=True,
    ) -> Optional[models.Model]:
        """Packages local script and launches training_job.
        Args:
            dataset (
                Union[
                    datasets.ImageDataset,
                    datasets.TabularDataset,
                    datasets.TextDataset,
                    datasets.VideoDataset,
                ]
            ):
                AI Platform to fit this training against.
            annotation_schema_uri (str):
                Google Cloud Storage URI points to a YAML file describing
                annotation schema.
            worker_pools_spec (_DistributedTrainingSpec):
                Worker pools pecs required to run job.
            managed_model (gca_model.Model):
                Model proto if this script produces a Managed Model.
            args (List[Unions[str, int, float]]):
                Command line arguments to be passed to the Python script.
            environment_variables (Dict[str, str]):
                Environment variables to be passed to the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
                At most 10 environment variables can be specified.
                The Name of the environment variable must be unique.

                environment_variables = {
                    'MY_KEY': 'MY_VALUE'
                }
            base_output_dir (str):
                GCS output directory of job. If not provided a
                timestamped directory in the staging directory will be used.

                AI Platform sets the following environment variables when it runs your training code:

                -  AIP_MODEL_DIR: a Cloud Storage URI of a directory intended for saving model artifacts, i.e. <base_output_dir>/model/
                -  AIP_CHECKPOINT_DIR: a Cloud Storage URI of a directory intended for saving checkpoints, i.e. <base_output_dir>/checkpoints/
                -  AIP_TENSORBOARD_LOG_DIR: a Cloud Storage URI of a directory intended for saving TensorBoard logs, i.e. <base_output_dir>/logs/

            service_account (str):
                Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
            bigquery_destination (str):
                The BigQuery project location where the training data is to
                be written to. In the given project a new dataset is created
                with name
                ``dataset_<dataset-id>_<annotation-type>_<timestamp-of-training-call>``
                where timestamp is in YYYY_MM_DDThh_mm_ss_sssZ format. All
                training input data will be written into that dataset. In
                the dataset three tables will be created, ``training``,
                ``validation`` and ``test``.

                -  AIP_DATA_FORMAT = "bigquery".
                -  AIP_TRAINING_DATA_URI ="bigquery_destination.dataset_*.training"
                -  AIP_VALIDATION_DATA_URI = "bigquery_destination.dataset_*.validation"
                -  AIP_TEST_DATA_URI = "bigquery_destination.dataset_*.test"
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

                Supported only for tabular and time series Datasets.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """

        for spec in worker_pool_specs:
            spec["containerSpec"] = {"imageUri": self._container_uri}

            if self._command:
                spec["containerSpec"]["command"] = self._command

            if args:
                spec["containerSpec"]["args"] = args

            if environment_variables:
                spec["containerSpec"]["env"] = [
                    {"name": key, "value": value}
                    for key, value in environment_variables.items()
                ]

        (
            training_task_inputs,
            base_output_dir,
        ) = self._prepare_training_task_inputs_and_output_dir(
            worker_pool_specs=worker_pool_specs,
            base_output_dir=base_output_dir,
            service_account=service_account,
            network=network,
        )

        model = self._run_job(
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=training_task_inputs,
            dataset=dataset,
            annotation_schema_uri=annotation_schema_uri,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=predefined_split_column_name,
            model=managed_model,
            gcs_destination_uri_prefix=base_output_dir,
            bigquery_destination=bigquery_destination,
        )

        return model


class AutoMLTabularTrainingJob(_TrainingJob):
    _supported_training_schemas = (schema.training_job.definition.automl_tabular,)

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
        training_encryption_spec_key_name: Optional[str] = None,
        model_encryption_spec_key_name: Optional[str] = None,
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
            training_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the training pipeline. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this TrainingPipeline will be secured by this key.

                Note: Model trained by this TrainingPipeline is also secured
                by this key if ``model_to_upload`` is not set separately.

                Overrides encryption_spec_key_name set in aiplatform.init.
            model_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, the trained Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
        """
        super().__init__(
            display_name=display_name,
            project=project,
            location=location,
            credentials=credentials,
            training_encryption_spec_key_name=training_encryption_spec_key_name,
            model_encryption_spec_key_name=model_encryption_spec_key_name,
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
        dataset: datasets.TabularDataset,
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
        decided by AI Platform. If none of the fractions are set, by default roughly 80%
        of data will be used for training, 10% for validation, and 10% for test.

        Args:
            dataset (datasets.TabularDataset):
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

                Supported only for tabular and time series Datasets.
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
                used, if further training does no longer brings significant improvement
                to the model.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.

        Raises:
            RuntimeError: If Training job has already been run or is waiting to run.
        """

        if self._is_waiting_to_run():
            raise RuntimeError("AutoML Tabular Training is already scheduled to run.")

        if self._has_run:
            raise RuntimeError("AutoML Tabular Training has already run.")

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
        dataset: datasets.TabularDataset,
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
        decided by AI Platform. If none of the fractions are set, by default roughly 80%
        of data will be used for training, 10% for validation, and 10% for test.

        Args:
            dataset (datasets.TabularDataset):
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

                Supported only for tabular and time series Datasets.
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
                used, if further training does no longer brings significant improvement
                to the model.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """

        training_task_definition = schema.training_job.definition.automl_tabular

        if self._column_transformations is None:
            _LOGGER.info(
                "No column transformations provided, so now retrieving columns from dataset in order to set default column transformations."
            )

            column_names = [
                column_name
                for column_name in dataset.column_names
                if column_name != target_column
            ]
            column_transformations = [
                {"auto": {"column_name": column_name}} for column_name in column_names
            ]

            _LOGGER.info(
                "The column transformation of type 'auto' was set for the following columns: %s."
                % column_names
            )
        else:
            column_transformations = self._column_transformations

        training_task_inputs_dict = {
            # required inputs
            "targetColumn": target_column,
            "transformations": column_transformations,
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

        model = gca_model.Model(
            display_name=model_display_name,
            encryption_spec=self._model_encryption_spec,
        )

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


class AutoMLForecastingTrainingJob(_TrainingJob):
    _supported_training_schemas = (schema.training_job.definition.automl_forecasting,)

    def __init__(
        self,
        display_name: str,
        optimization_objective: Optional[str] = None,
        column_transformations: Optional[Union[Dict, List[Dict]]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Constructs a AutoML Forecasting Training Job.

        Args:
            display_name (str):
                Required. The user-defined name of this TrainingPipeline.
            optimization_objective (str):
                Optional. Objective function the model is to be optimized towards.
                The training process creates a Model that optimizes the value of the objective
                function over the validation set. The supported optimization objectives:
                "minimize-rmse" (default) - Minimize root-mean-squared error (RMSE).
                "minimize-mae" - Minimize mean-absolute error (MAE).
                "minimize-rmsle" - Minimize root-mean-squared log error (RMSLE).
                "minimize-rmspe" - Minimize root-mean-squared percentage error (RMSPE).
                "minimize-wape-mae" - Minimize the combination of weighted absolute percentage error (WAPE)
                                      and mean-absolute-error (MAE).
                "minimize-quantile-loss" - Minimize the quantile loss at the defined quantiles.
                                           (Set this objective to build quantile forecasts.)
            column_transformations (Optional[Union[Dict, List[Dict]]]):
                Optional. Transformations to apply to the input columns (i.e. columns other
                than the targetColumn). Each transformation may produce multiple
                result values from the column's value, and all are used for training.
                When creating transformation for BigQuery Struct column, the column
                should be flattened using "." as the delimiter.
                If an input column has no transformations on it, such a column is
                ignored by the training, except for the targetColumn, which should have
                no transformations defined on.
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

    def run(
        self,
        dataset: datasets.TimeSeriesDataset,
        target_column: str,
        time_column: str,
        time_series_identifier_column: str,
        unavailable_at_forecast_columns: List[str],
        available_at_forecast_columns: List[str],
        forecast_horizon: int,
        data_granularity_unit: str,
        data_granularity_count: int,
        predefined_split_column_name: Optional[str] = None,
        weight_column: Optional[str] = None,
        time_series_attribute_columns: Optional[List[str]] = None,
        context_window: Optional[int] = None,
        export_evaluated_data_items: bool = False,
        export_evaluated_data_items_bigquery_destination_uri: Optional[str] = None,
        export_evaluated_data_items_override_destination: bool = False,
        quantiles: Optional[List[float]] = None,
        validation_options: Optional[str] = None,
        budget_milli_node_hours: int = 1000,
        model_display_name: Optional[str] = None,
        sync: bool = True,
    ) -> models.Model:
        """Runs the training job and returns a model.

        The training data splits are set by default: Roughly 80% will be used for training,
        10% for validation, and 10% for test.

        Args:
            dataset (datasets.Dataset):
                Required. The dataset within the same Project from which data will be used to train the Model. The
                Dataset must use schema compatible with Model being trained,
                and what is compatible should be described in the used
                TrainingPipeline's [training_task_definition]
                [google.cloud.aiplatform.v1beta1.TrainingPipeline.training_task_definition].
                For time series Datasets, all their data is exported to
                training, to pick and choose from.
            target_column (str):
                Required. Name of the column that the Model is to predict values for.
            time_column (str):
                Required. Name of the column that identifies time order in the time series.
            time_series_identifier_column (str):
                Required. Name of the column that identifies the time series.
            unavailable_at_forecast_columns (List[str]):
                Required. Column names of columns that are unavailable at forecast.
                Each column contains information for the given entity (identified by the
                [time_series_identifier_column]) that is unknown before the forecast
                (e.g. population of a city in a given year, or weather on a given day).
            available_at_forecast_columns (List[str]):
                Required. Column names of columns that are available at forecast.
                Each column contains information for the given entity (identified by the
                [time_series_identifier_column]) that is known at forecast.
            forecast_horizon: (int):
                Required. The amount of time into the future for which forecasted values for the target are
                returned. Expressed in number of units defined by the [data_granularity_unit] and
                [data_granularity_count] field. Inclusive.
            data_granularity_unit (str):
                Required. The data granularity unit. Accepted values are ``minute``,
                ``hour``, ``day``, ``week``, ``month``, ``year``.
            data_granularity_count (int):
                Required. The number of data granularity units between data points in the training
                data. If [data_granularity_unit] is `minute`, can be 1, 5, 10, 15, or 30. For all other
                values of [data_granularity_unit], must be 1.
            predefined_split_column_name (str):
                Optional. The key is a name of one of the Dataset's data
                columns. The value of the key (either the label's value or
                value in the column) must be one of {``TRAIN``,
                ``VALIDATE``, ``TEST``}, and it defines to which set the
                given piece of data is assigned. If for a piece of data the
                key is not present or has an invalid value, that piece is
                ignored by the pipeline.

                Supported only for tabular and time series Datasets.
            weight_column (str):
                Optional. Name of the column that should be used as the weight column.
                Higher values in this column give more importance to the row
                during Model training. The column must have numeric values between 0 and
                10000 inclusively, and 0 value means that the row is ignored.
                If the weight column field is not set, then all rows are assumed to have
                equal weight of 1.
            time_series_attribute_columns (List[str]):
                Optional. Column names that should be used as attribute columns.
                Each column is constant within a time series.
            context_window (int):
                Optional. The amount of time into the past training and prediction data is used for
                model training and prediction respectively. Expressed in number of units defined by the
                [data_granularity_unit] and [data_granularity_count] fields. When not provided uses the
                default value of 0 which means the model sets each series context window to be 0 (also
                known as "cold start"). Inclusive.
            export_evaluated_data_items (bool):
                Whether to export the test set predictions to a BigQuery table.
                If False, then the export is not performed.
            export_evaluated_data_items_bigquery_destination_uri (string):
                Optional. URI of desired destination BigQuery table for exported test set predictions.

                Expected format:
                ``bq://<project_id>:<dataset_id>:<table>``

                If not specified, then results are exported to the following auto-created BigQuery
                table:
                ``<project_id>:export_evaluated_examples_<model_name>_<yyyy_MM_dd'T'HH_mm_ss_SSS'Z'>.evaluated_examples``

                Applies only if [export_evaluated_data_items] is True.
            export_evaluated_data_items_override_destination (bool):
                Whether to override the contents of [export_evaluated_data_items_bigquery_destination_uri],
                if the table exists, for exported test set predictions. If False, and the
                table exists, then the training job will fail.

                Applies only if [export_evaluated_data_items] is True and
                [export_evaluated_data_items_bigquery_destination_uri] is specified.
            quantiles (List[float]):
                Quantiles to use for the `minizmize-quantile-loss`
                [AutoMLForecastingTrainingJob.optimization_objective]. This argument is required in
                this case.

                Accepts up to 5 quantiles in the form of a double from 0 to 1, exclusive.
                Each quantile must be unique.
            validation_options (str):
                Validation options for the data validation component. The available options are:
                "fail-pipeline" - (default), will validate against the validation and fail the pipeline
                                  if it fails.
                "ignore-validation" - ignore the results of the validation and continue the pipeline
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
            raise RuntimeError(
                "AutoML Forecasting Training is already scheduled to run."
            )

        if self._has_run:
            raise RuntimeError("AutoML Forecasting Training has already run.")

        return self._run(
            dataset=dataset,
            target_column=target_column,
            time_column=time_column,
            time_series_identifier_column=time_series_identifier_column,
            unavailable_at_forecast_columns=unavailable_at_forecast_columns,
            available_at_forecast_columns=available_at_forecast_columns,
            forecast_horizon=forecast_horizon,
            data_granularity_unit=data_granularity_unit,
            data_granularity_count=data_granularity_count,
            predefined_split_column_name=predefined_split_column_name,
            weight_column=weight_column,
            time_series_attribute_columns=time_series_attribute_columns,
            context_window=context_window,
            budget_milli_node_hours=budget_milli_node_hours,
            export_evaluated_data_items=export_evaluated_data_items,
            export_evaluated_data_items_bigquery_destination_uri=export_evaluated_data_items_bigquery_destination_uri,
            export_evaluated_data_items_override_destination=export_evaluated_data_items_override_destination,
            quantiles=quantiles,
            validation_options=validation_options,
            model_display_name=model_display_name,
            sync=sync,
        )

    @base.optional_sync()
    def _run(
        self,
        dataset: datasets.TimeSeriesDataset,
        target_column: str,
        time_column: str,
        time_series_identifier_column: str,
        unavailable_at_forecast_columns: List[str],
        available_at_forecast_columns: List[str],
        forecast_horizon: int,
        data_granularity_unit: str,
        data_granularity_count: int,
        predefined_split_column_name: Optional[str] = None,
        weight_column: Optional[str] = None,
        time_series_attribute_columns: Optional[List[str]] = None,
        context_window: Optional[int] = None,
        export_evaluated_data_items: bool = False,
        export_evaluated_data_items_bigquery_destination_uri: Optional[str] = None,
        export_evaluated_data_items_override_destination: bool = False,
        quantiles: Optional[List[float]] = None,
        validation_options: Optional[str] = None,
        budget_milli_node_hours: int = 1000,
        model_display_name: Optional[str] = None,
        sync: bool = True,
    ) -> models.Model:
        """Runs the training job and returns a model.

        The training data splits are set by default: Roughly 80% will be used for training,
        10% for validation, and 10% for test.

        Args:
            dataset (datasets.Dataset):
                Required. The dataset within the same Project from which data will be used to train the Model. The
                Dataset must use schema compatible with Model being trained,
                and what is compatible should be described in the used
                TrainingPipeline's [training_task_definition]
                [google.cloud.aiplatform.v1beta1.TrainingPipeline.training_task_definition].
                For time series Datasets, all their data is exported to
                training, to pick and choose from.
            target_column (str):
                Required. Name of the column that the Model is to predict values for.
            time_column (str):
                Required. Name of the column that identifies time order in the time series.
            time_series_identifier_column (str):
                Required. Name of the column that identifies the time series.
            unavailable_at_forecast_columns (List[str]):
                Required. Column names of columns that are unavailable at forecast.
                Each column contains information for the given entity (identified by the
                [time_series_identifier_column]) that is unknown before the forecast
                (e.g. population of a city in a given year, or weather on a given day).
            available_at_forecast_columns (List[str]):
                Required. Column names of columns that are available at forecast.
                Each column contains information for the given entity (identified by the
                [time_series_identifier_column]) that is known at forecast.
            forecast_horizon: (int):
                Required. The amount of time into the future for which forecasted values for the target are
                returned. Expressed in number of units defined by the [data_granularity_unit] and
                [data_granularity_count] field. Inclusive.
            data_granularity_unit (str):
                Required. The data granularity unit. Accepted values are ``minute``,
                ``hour``, ``day``, ``week``, ``month``, ``year``.
            data_granularity_count (int):
                Required. The number of data granularity units between data points in the training
                data. If [data_granularity_unit] is `minute`, can be 1, 5, 10, 15, or 30. For all other
                values of [data_granularity_unit], must be 1.
            predefined_split_column_name (str):
                Optional. The key is a name of one of the Dataset's data
                columns. The value of the key (either the label's value or
                value in the column) must be one of {``TRAIN``,
                ``VALIDATE``, ``TEST``}, and it defines to which set the
                given piece of data is assigned. If for a piece of data the
                key is not present or has an invalid value, that piece is
                ignored by the pipeline.

                Supported only for tabular and time series Datasets.
            weight_column (str):
                Optional. Name of the column that should be used as the weight column.
                Higher values in this column give more importance to the row
                during Model training. The column must have numeric values between 0 and
                10000 inclusively, and 0 value means that the row is ignored.
                If the weight column field is not set, then all rows are assumed to have
                equal weight of 1.
            time_series_attribute_columns (List[str]):
                Optional. Column names that should be used as attribute columns.
                Each column is constant within a time series.
            context_window (int):
                Optional. The number of periods offset into the past to restrict past sequence, where each
                period is one unit of granularity as defined by [period]. When not provided uses the
                default value of 0 which means the model sets each series historical window to be 0 (also
                known as "cold start"). Inclusive.
            export_evaluated_data_items (bool):
                Whether to export the test set predictions to a BigQuery table.
                If False, then the export is not performed.
            export_evaluated_data_items_bigquery_destination_uri (string):
                Optional. URI of desired destination BigQuery table for exported test set predictions.

                Expected format:
                ``bq://<project_id>:<dataset_id>:<table>``

                If not specified, then results are exported to the following auto-created BigQuery
                table:
                ``<project_id>:export_evaluated_examples_<model_name>_<yyyy_MM_dd'T'HH_mm_ss_SSS'Z'>.evaluated_examples``

                Applies only if [export_evaluated_data_items] is True.
            export_evaluated_data_items_override_destination (bool):
                Whether to override the contents of [export_evaluated_data_items_bigquery_destination_uri],
                if the table exists, for exported test set predictions. If False, and the
                table exists, then the training job will fail.

                Applies only if [export_evaluated_data_items] is True and
                [export_evaluated_data_items_bigquery_destination_uri] is specified.
            quantiles (List[float]):
                Quantiles to use for the `minizmize-quantile-loss`
                [AutoMLForecastingTrainingJob.optimization_objective]. This argument is required in
                this case.

                Accepts up to 5 quantiles in the form of a double from 0 to 1, exclusive.
                Each quantile must be unique.
            validation_options (str):
                Validation options for the data validation component. The available options are:
                "fail-pipeline" - (default), will validate against the validation and fail the pipeline
                                  if it fails.
                "ignore-validation" - ignore the results of the validation and continue the pipeline
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
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """

        training_task_definition = schema.training_job.definition.automl_forecasting

        training_task_inputs_dict = {
            # required inputs
            "targetColumn": target_column,
            "timeColumn": time_column,
            "timeSeriesIdentifierColumn": time_series_identifier_column,
            "timeSeriesAttributeColumns": time_series_attribute_columns,
            "unavailableAtForecastColumns": unavailable_at_forecast_columns,
            "availableAtForecastColumns": available_at_forecast_columns,
            "forecastHorizon": forecast_horizon,
            "dataGranularity": {
                "unit": data_granularity_unit,
                "quantity": data_granularity_count,
            },
            "transformations": self._column_transformations,
            "trainBudgetMilliNodeHours": budget_milli_node_hours,
            # optional inputs
            "weightColumn": weight_column,
            "contextWindow": context_window,
            "quantiles": quantiles,
            "validationOptions": validation_options,
            "optimizationObjective": self._optimization_objective,
        }

        final_export_eval_bq_uri = export_evaluated_data_items_bigquery_destination_uri
        if final_export_eval_bq_uri and not final_export_eval_bq_uri.startswith(
            "bq://"
        ):
            final_export_eval_bq_uri = f"bq://{final_export_eval_bq_uri}"

        if export_evaluated_data_items:
            training_task_inputs_dict["exportEvaluatedDataItemsConfig"] = {
                "destinationBigqueryUri": final_export_eval_bq_uri,
                "overrideExistingTable": export_evaluated_data_items_override_destination,
            }

        if model_display_name is None:
            model_display_name = self._display_name

        model = gca_model.Model(display_name=model_display_name)

        return self._run_job(
            training_task_definition=training_task_definition,
            training_task_inputs=training_task_inputs_dict,
            dataset=dataset,
            training_fraction_split=0.8,
            validation_fraction_split=0.1,
            test_fraction_split=0.1,
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


class AutoMLImageTrainingJob(_TrainingJob):
    _supported_training_schemas = (
        schema.training_job.definition.automl_image_classification,
        schema.training_job.definition.automl_image_object_detection,
    )

    def __init__(
        self,
        display_name: str,
        prediction_type: str = "classification",
        multi_label: bool = False,
        model_type: str = "CLOUD",
        base_model: Optional[models.Model] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        training_encryption_spec_key_name: Optional[str] = None,
        model_encryption_spec_key_name: Optional[str] = None,
    ):
        """Constructs a AutoML Image Training Job.

        Args:
            display_name (str):
                Required. The user-defined name of this TrainingPipeline.
            prediction_type (str):
                The type of prediction the Model is to produce, one of:
                    "classification" - Predict one out of multiple target values is
                        picked for each row.
                    "object_detection" - Predict a value based on its relation to other values.
                        This type is available only to columns that contain
                        semantically numeric values, i.e. integers or floating
                        point number, even if stored as e.g. strings.
            multi_label: bool = False
                Required. Default is False.
                If false, a single-label (multi-class) Model will be trained
                (i.e. assuming that for each image just up to one annotation may be
                applicable). If true, a multi-label Model will be trained (i.e.
                assuming that for each image multiple annotations may be applicable).

                This is only applicable for the "classification" prediction_type and
                will be ignored otherwise.
            model_type: str = "CLOUD"
                Required. One of the following:
                    "CLOUD" - Default for Image Classification.
                        A Model best tailored to be used within Google Cloud, and
                        which cannot be exported.
                    "CLOUD_HIGH_ACCURACY_1" - Default for Image Object Detection.
                        A model best tailored to be used within Google Cloud, and
                        which cannot be exported. Expected to have a higher latency,
                        but should also have a higher prediction quality than other
                        cloud models.
                    "CLOUD_LOW_LATENCY_1" - A model best tailored to be used within
                        Google Cloud, and which cannot be exported. Expected to have a
                        low latency, but may have lower prediction quality than other
                        cloud models.
                    "MOBILE_TF_LOW_LATENCY_1" - A model that, in addition to being
                        available within Google Cloud, can also be exported as TensorFlow
                        or Core ML model and used on a mobile or edge device afterwards.
                        Expected to have low latency, but may have lower prediction
                        quality than other mobile models.
                    "MOBILE_TF_VERSATILE_1" - A model that, in addition to being
                        available within Google Cloud, can also be exported as TensorFlow
                        or Core ML model and used on a mobile or edge device with afterwards.
                    "MOBILE_TF_HIGH_ACCURACY_1" - A model that, in addition to being
                        available within Google Cloud, can also be exported as TensorFlow
                        or Core ML model and used on a mobile or edge device afterwards.
                        Expected to have a higher latency, but should also have a higher
                        prediction quality than other mobile models.
            base_model: Optional[models.Model] = None
                Optional. Only permitted for Image Classification models.
                If it is specified, the new model will be trained based on the `base` model.
                Otherwise, the new model will be trained from scratch. The `base` model
                must be in the same Project and Location as the new Model to train,
                and have the same model_type.
            project (str):
                Optional. Project to run training in. Overrides project set in aiplatform.init.
            location (str):
                Optional. Location to run training in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to run call training service. Overrides
                credentials set in aiplatform.init.
            training_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the training pipeline. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this TrainingPipeline will be secured by this key.

                Note: Model trained by this TrainingPipeline is also secured
                by this key if ``model_to_upload`` is not set separately.

                Overrides encryption_spec_key_name set in aiplatform.init.
            model_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, the trained Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
        Raises:
            ValueError: When an invalid prediction_type or model_type is provided.
        """

        valid_model_types = constants.AUTOML_IMAGE_PREDICTION_MODEL_TYPES.get(
            prediction_type, None
        )

        if not valid_model_types:
            raise ValueError(
                f"'{prediction_type}' is not a supported prediction type for AutoML Image Training. "
                f"Please choose one of: {tuple(constants.AUTOML_IMAGE_PREDICTION_MODEL_TYPES.keys())}."
            )

        # Override default model_type for object_detection
        if model_type == "CLOUD" and prediction_type == "object_detection":
            model_type = "CLOUD_HIGH_ACCURACY_1"

        if model_type not in valid_model_types:
            raise ValueError(
                f"'{model_type}' is not a supported model_type for prediction_type of '{prediction_type}'. "
                f"Please choose one of: {tuple(valid_model_types)}"
            )

        if base_model and prediction_type != "classification":
            raise ValueError(
                "Training with a `base_model` is only supported in AutoML Image Classification. "
                f"However '{prediction_type}' was provided as `prediction_type`."
            )

        super().__init__(
            display_name=display_name,
            project=project,
            location=location,
            credentials=credentials,
            training_encryption_spec_key_name=training_encryption_spec_key_name,
            model_encryption_spec_key_name=model_encryption_spec_key_name,
        )

        self._model_type = model_type
        self._prediction_type = prediction_type
        self._multi_label = multi_label
        self._base_model = base_model

    def run(
        self,
        dataset: datasets.ImageDataset,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        budget_milli_node_hours: int = 1000,
        model_display_name: Optional[str] = None,
        disable_early_stopping: bool = False,
        sync: bool = True,
    ) -> models.Model:
        """Runs the AutoML Image training job and returns a model.

        Data fraction splits:
        Any of ``training_fraction_split``, ``validation_fraction_split`` and
        ``test_fraction_split`` may optionally be provided, they must sum to up to 1. If
        the provided ones sum to less than 1, the remainder is assigned to sets as
        decided by AI Platform. If none of the fractions are set, by default roughly 80%
        of data will be used for training, 10% for validation, and 10% for test.

        Args:
            dataset (datasets.ImageDataset):
                Required. The dataset within the same Project from which data will be used to train the Model. The
                Dataset must use schema compatible with Model being trained,
                and what is compatible should be described in the used
                TrainingPipeline's [training_task_definition]
                [google.cloud.aiplatform.v1beta1.TrainingPipeline.training_task_definition].
                For tabular Datasets, all their data is exported to
                training, to pick and choose from.
            training_fraction_split: float = 0.8
                Required. The fraction of the input data that is to be
                used to train the Model. This is ignored if Dataset is not provided.
            validation_fraction_split: float = 0.1
                Required. The fraction of the input data that is to be
                used to validate the Model. This is ignored if Dataset is not provided.
            test_fraction_split: float = 0.1
                Required. The fraction of the input data that is to be
                used to evaluate the Model. This is ignored if Dataset is not provided.
            budget_milli_node_hours: int = 1000
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
                Optional. The display name of the managed AI Platform Model. The name
                can be up to 128 characters long and can be consist of any UTF-8
                characters. If not provided upon creation, the job's display_name is used.
            disable_early_stopping: bool = False
                Required. If true, the entire budget is used. This disables the early stopping
                feature. By default, the early stopping feature is enabled, which means
                that training might stop before the entire training budget has been
                used, if further training does no longer brings significant improvement
                to the model.
            sync: bool = True
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.

        Raises:
            RuntimeError: If Training job has already been run or is waiting to run.
        """

        if self._is_waiting_to_run():
            raise RuntimeError("AutoML Image Training is already scheduled to run.")

        if self._has_run:
            raise RuntimeError("AutoML Image Training has already run.")

        return self._run(
            dataset=dataset,
            base_model=self._base_model,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            budget_milli_node_hours=budget_milli_node_hours,
            model_display_name=model_display_name,
            disable_early_stopping=disable_early_stopping,
            sync=sync,
        )

    @base.optional_sync()
    def _run(
        self,
        dataset: datasets.ImageDataset,
        base_model: Optional[models.Model] = None,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
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
        decided by AI Platform. If none of the fractions are set, by default roughly 80%
        of data will be used for training, 10% for validation, and 10% for test.

        Args:
            dataset (datasets.ImageDataset):
                Required. The dataset within the same Project from which data will be used to train the Model. The
                Dataset must use schema compatible with Model being trained,
                and what is compatible should be described in the used
                TrainingPipeline's [training_task_definition]
                [google.cloud.aiplatform.v1beta1.TrainingPipeline.training_task_definition].
                For tabular Datasets, all their data is exported to
                training, to pick and choose from.
            base_model: Optional[models.Model] = None
                Optional. Only permitted for Image Classification models.
                If it is specified, the new model will be trained based on the `base` model.
                Otherwise, the new model will be trained from scratch. The `base` model
                must be in the same Project and Location as the new Model to train,
                and have the same model_type.
            training_fraction_split (float):
                Required. The fraction of the input data that is to be
                used to train the Model. This is ignored if Dataset is not provided.
            validation_fraction_split (float):
                Required. The fraction of the input data that is to be
                used to validate the Model. This is ignored if Dataset is not provided.
            test_fraction_split (float):
                Required. The fraction of the input data that is to be
                used to evaluate the Model. This is ignored if Dataset is not provided.
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
                Optional. The display name of the managed AI Platform Model. The name
                can be up to 128 characters long and can be consist of any UTF-8
                characters. If a `base_model` was provided, the display_name in the
                base_model will be overritten with this value. If not provided upon
                creation, the job's display_name is used.
            disable_early_stopping (bool):
                Required. If true, the entire budget is used. This disables the early stopping
                feature. By default, the early stopping feature is enabled, which means
                that training might stop before the entire training budget has been
                used, if further training does no longer brings significant improvement
                to the model.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """

        # Retrieve the objective-specific training task schema based on prediction_type
        training_task_definition = getattr(
            schema.training_job.definition, f"automl_image_{self._prediction_type}"
        )

        training_task_inputs_dict = {
            # required inputs
            "modelType": self._model_type,
            "budgetMilliNodeHours": budget_milli_node_hours,
            # optional inputs
            "disableEarlyStopping": disable_early_stopping,
        }

        if self._prediction_type == "classification":
            training_task_inputs_dict["multiLabel"] = self._multi_label

        # gca Model to be trained
        model_tbt = gca_model.Model(encryption_spec=self._model_encryption_spec)

        model_tbt.display_name = model_display_name or self._display_name

        if base_model:
            # Use provided base_model to pass to model_to_upload causing the
            # description and labels from base_model to be passed onto the new model
            model_tbt.description = getattr(base_model._gca_resource, "description")
            model_tbt.labels = getattr(base_model._gca_resource, "labels")

            # Set ID of AI Platform Model to base this training job off of
            training_task_inputs_dict["baseModelId"] = base_model.name

        return self._run_job(
            training_task_definition=training_task_definition,
            training_task_inputs=training_task_inputs_dict,
            dataset=dataset,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            model=model_tbt,
        )

    @property
    def _model_upload_fail_string(self) -> str:
        """Helper property for model upload failure."""
        return (
            f"AutoML Image Training Pipeline {self.resource_name} is not "
            "configured to upload a Model."
        )


class CustomPythonPackageTrainingJob(_CustomTrainingJob):
    """Class to launch a Custom Training Job in AI Platform using a Python
    Package.

    Takes a training implementation as a python package and executes
    that package in Cloud AI Platform Training.
    """

    def __init__(
        self,
        display_name: str,
        python_package_gcs_uri: str,
        python_module_name: str,
        container_uri: str,
        model_serving_container_image_uri: Optional[str] = None,
        model_serving_container_predict_route: Optional[str] = None,
        model_serving_container_health_route: Optional[str] = None,
        model_serving_container_command: Optional[Sequence[str]] = None,
        model_serving_container_args: Optional[Sequence[str]] = None,
        model_serving_container_environment_variables: Optional[Dict[str, str]] = None,
        model_serving_container_ports: Optional[Sequence[int]] = None,
        model_description: Optional[str] = None,
        model_instance_schema_uri: Optional[str] = None,
        model_parameters_schema_uri: Optional[str] = None,
        model_prediction_schema_uri: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        training_encryption_spec_key_name: Optional[str] = None,
        model_encryption_spec_key_name: Optional[str] = None,
        staging_bucket: Optional[str] = None,
    ):
        """Constructs a Custom Training Job from a Python Package.

        job = aiplatform.CustomPythonPackageTrainingJob(
            display_name='test-train',
            python_package_gcs_uri='gs://my-bucket/my-python-package.tar.gz',
            python_module_name='my-training-python-package.task',
            container_uri='gcr.io/cloud-aiplatform/training/tf-cpu.2-2:latest',
            model_serving_container_image_uri='gcr.io/my-trainer/serving:1',
            model_serving_container_predict_route='predict',
            model_serving_container_health_route='metadata
        )

        Usage with Dataset:

            ds = aiplatform.TabularDataset(
                'projects/my-project/locations/us-central1/datasets/12345'
            )

            job.run(
                ds,
                replica_count=1,
                model_display_name='my-trained-model'
            )

        Usage without Dataset:

            job.run(
                replica_count=1,
                model_display_name='my-trained-model'
            )

        To ensure your model gets saved in AI Platform, write your saved model to
        os.environ["AIP_MODEL_DIR"] in your provided training script.

        Args:
            display_name (str):
                Required. The user-defined name of this TrainingPipeline.
            python_package_gcs_uri (str):
                Required: GCS location of the training python package.
            python_module_name (str):
                Required: The module name of the training python package.
            container_uri (str):
                Required: Uri of the training container image in the GCR.
            model_serving_container_image_uri (str):
                If the training produces a managed AI Platform Model, the URI of the
                Model serving container suitable for serving the model produced by the
                training script.
            model_serving_container_predict_route (str):
                If the training produces a managed AI Platform Model, An HTTP path to
                send prediction requests to the container, and which must be supported
                by it. If not specified a default HTTP path will be used by AI Platform.
            model_serving_container_health_route (str):
                If the training produces a managed AI Platform Model, an HTTP path to
                send health check requests to the container, and which must be supported
                by it. If not specified a standard HTTP path will be used by AI
                Platform.
            model_serving_container_command (Sequence[str]):
                The command with which the container is run. Not executed within a
                shell. The Docker image's ENTRYPOINT is used if this is not provided.
                Variable references $(VAR_NAME) are expanded using the container's
                environment. If a variable cannot be resolved, the reference in the
                input string will be unchanged. The $(VAR_NAME) syntax can be escaped
                with a double $$, ie: $$(VAR_NAME). Escaped references will never be
                expanded, regardless of whether the variable exists or not.
            model_serving_container_args (Sequence[str]):
                The arguments to the command. The Docker image's CMD is used if this is
                not provided. Variable references $(VAR_NAME) are expanded using the
                container's environment. If a variable cannot be resolved, the reference
                in the input string will be unchanged. The $(VAR_NAME) syntax can be
                escaped with a double $$, ie: $$(VAR_NAME). Escaped references will
                never be expanded, regardless of whether the variable exists or not.
            model_serving_container_environment_variables (Dict[str, str]):
                The environment variables that are to be present in the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
            model_serving_container_ports (Sequence[int]):
                Declaration of ports that are exposed by the container. This field is
                primarily informational, it gives AI Platform information about the
                network connections the container uses. Listing or not a port here has
                no impact on whether the port is actually exposed, any port listening on
                the default "0.0.0.0" address inside a container will be accessible from
                the network.
            model_description (str):
                The description of the Model.
            model_instance_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the format of a single instance, which
                are used in
                ``PredictRequest.instances``,
                ``ExplainRequest.instances``
                and
                ``BatchPredictionJob.input_config``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform. Note: The URI given on output will be immutable
                and probably different, including the URI scheme, than the
                one given on input. The output URI will point to a location
                where the user only has a read access.
            model_parameters_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the parameters of prediction and
                explanation via
                ``PredictRequest.parameters``,
                ``ExplainRequest.parameters``
                and
                ``BatchPredictionJob.model_parameters``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform, if no parameters are supported it is set to an
                empty string. Note: The URI given on output will be
                immutable and probably different, including the URI scheme,
                than the one given on input. The output URI will point to a
                location where the user only has a read access.
            model_prediction_schema_uri (str):
                Optional. Points to a YAML file stored on Google Cloud
                Storage describing the format of a single prediction
                produced by this Model, which are returned via
                ``PredictResponse.predictions``,
                ``ExplainResponse.explanations``,
                and
                ``BatchPredictionJob.output_config``.
                The schema is defined as an OpenAPI 3.0.2 `Schema
                Object <https://tinyurl.com/y538mdwt#schema-object>`__.
                AutoML Models always have this field populated by AI
                Platform. Note: The URI given on output will be immutable
                and probably different, including the URI scheme, than the
                one given on input. The output URI will point to a location
                where the user only has a read access.
            project (str):
                Project to run training in. Overrides project set in aiplatform.init.
            location (str):
                Location to run training in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to run call training service. Overrides
                credentials set in aiplatform.init.
            training_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the training pipeline. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this TrainingPipeline will be secured by this key.

                Note: Model trained by this TrainingPipeline is also secured
                by this key if ``model_to_upload`` is not set separately.

                Overrides encryption_spec_key_name set in aiplatform.init.
            model_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, the trained Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
            staging_bucket (str):
                Bucket used to stage source and training artifacts. Overrides
                staging_bucket set in aiplatform.init.
        """
        super().__init__(
            display_name=display_name,
            project=project,
            location=location,
            credentials=credentials,
            training_encryption_spec_key_name=training_encryption_spec_key_name,
            model_encryption_spec_key_name=model_encryption_spec_key_name,
            container_uri=container_uri,
            model_instance_schema_uri=model_instance_schema_uri,
            model_parameters_schema_uri=model_parameters_schema_uri,
            model_prediction_schema_uri=model_prediction_schema_uri,
            model_serving_container_environment_variables=model_serving_container_environment_variables,
            model_serving_container_ports=model_serving_container_ports,
            model_serving_container_image_uri=model_serving_container_image_uri,
            model_serving_container_command=model_serving_container_command,
            model_serving_container_args=model_serving_container_args,
            model_serving_container_predict_route=model_serving_container_predict_route,
            model_serving_container_health_route=model_serving_container_health_route,
            model_description=model_description,
            staging_bucket=staging_bucket,
        )

        self._package_gcs_uri = python_package_gcs_uri
        self._python_module = python_module_name

    def run(
        self,
        dataset: Optional[
            Union[
                datasets.ImageDataset,
                datasets.TabularDataset,
                datasets.TextDataset,
                datasets.VideoDataset,
            ]
        ] = None,
        annotation_schema_uri: Optional[str] = None,
        model_display_name: Optional[str] = None,
        base_output_dir: Optional[str] = None,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        bigquery_destination: Optional[str] = None,
        args: Optional[List[Union[str, float, int]]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
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
            dataset (Union[datasets.ImageDataset,datasets.TabularDataset,datasets.TextDataset,datasets.VideoDataset,]):
                AI Platform to fit this training against. Custom training script should
                retrieve datasets through passed in environment variables uris:

                os.environ["AIP_TRAINING_DATA_URI"]
                os.environ["AIP_VALIDATION_DATA_URI"]
                os.environ["AIP_TEST_DATA_URI"]

                Additionally the dataset format is passed in as:

                os.environ["AIP_DATA_FORMAT"]
            annotation_schema_uri (str):
                Google Cloud Storage URI points to a YAML file describing
                annotation schema. The schema is defined as an OpenAPI 3.0.2
                [Schema Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schema-object) The schema files
                that can be used here are found in
                gs://google-cloud-aiplatform/schema/dataset/annotation/,
                note that the chosen schema must be consistent with
                ``metadata``
                of the Dataset specified by
                ``dataset_id``.

                Only Annotations that both match this schema and belong to
                DataItems not ignored by the split method are used in
                respectively training, validation or test role, depending on
                the role of the DataItem they are on.

                When used in conjunction with
                ``annotations_filter``,
                the Annotations used for training are filtered by both
                ``annotations_filter``
                and
                ``annotation_schema_uri``.
            model_display_name (str):
                If the script produces a managed AI Platform Model. The display name of
                the Model. The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.

                If not provided upon creation, the job's display_name is used.
            base_output_dir (str):
                GCS output directory of job. If not provided a
                timestamped directory in the staging directory will be used.

                AI Platform sets the following environment variables when it runs your training code:

                -  AIP_MODEL_DIR: a Cloud Storage URI of a directory intended for saving model artifacts, i.e. <base_output_dir>/model/
                -  AIP_CHECKPOINT_DIR: a Cloud Storage URI of a directory intended for saving checkpoints, i.e. <base_output_dir>/checkpoints/
                -  AIP_TENSORBOARD_LOG_DIR: a Cloud Storage URI of a directory intended for saving TensorBoard logs, i.e. <base_output_dir>/logs/

            service_account (str):
                Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
            bigquery_destination (str):
                Provide this field if `dataset` is a BiqQuery dataset.
                The BigQuery project location where the training data is to
                be written to. In the given project a new dataset is created
                with name
                ``dataset_<dataset-id>_<annotation-type>_<timestamp-of-training-call>``
                where timestamp is in YYYY_MM_DDThh_mm_ss_sssZ format. All
                training input data will be written into that dataset. In
                the dataset three tables will be created, ``training``,
                ``validation`` and ``test``.

                -  AIP_DATA_FORMAT = "bigquery".
                -  AIP_TRAINING_DATA_URI ="bigquery_destination.dataset_*.training"
                -  AIP_VALIDATION_DATA_URI = "bigquery_destination.dataset_*.validation"
                -  AIP_TEST_DATA_URI = "bigquery_destination.dataset_*.test"
            args (List[Unions[str, int, float]]):
                Command line arguments to be passed to the Python script.
            environment_variables (Dict[str, str]):
                Environment variables to be passed to the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
                At most 10 environment variables can be specified.
                The Name of the environment variable must be unique.

                environment_variables = {
                    'MY_KEY': 'MY_VALUE'
                }
            replica_count (int):
                The number of worker replicas. If replica count = 1 then one chief
                replica will be provisioned. If replica_count > 1 the remainder will be
                provisioned as a worker replica pool.
            machine_type (str):
                The type of machine to use for training.
            accelerator_type (str):
                Hardware accelerator type. One of ACCELERATOR_TYPE_UNSPECIFIED,
                NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100, NVIDIA_TESLA_P4,
                NVIDIA_TESLA_T4
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

                Supported only for tabular and time series Datasets.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """
        worker_pool_specs, managed_model = self._prepare_and_validate_run(
            model_display_name=model_display_name,
            replica_count=replica_count,
            machine_type=machine_type,
            accelerator_count=accelerator_count,
            accelerator_type=accelerator_type,
        )

        return self._run(
            dataset=dataset,
            annotation_schema_uri=annotation_schema_uri,
            worker_pool_specs=worker_pool_specs,
            managed_model=managed_model,
            args=args,
            environment_variables=environment_variables,
            base_output_dir=base_output_dir,
            service_account=service_account,
            network=network,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=predefined_split_column_name,
            bigquery_destination=bigquery_destination,
            sync=sync,
        )

    @base.optional_sync(construct_object_on_arg="managed_model")
    def _run(
        self,
        dataset: Optional[
            Union[
                datasets.ImageDataset,
                datasets.TabularDataset,
                datasets.TextDataset,
                datasets.VideoDataset,
            ]
        ],
        annotation_schema_uri: Optional[str],
        worker_pool_specs: _DistributedTrainingSpec,
        managed_model: Optional[gca_model.Model] = None,
        args: Optional[List[Union[str, float, int]]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        base_output_dir: Optional[str] = None,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        predefined_split_column_name: Optional[str] = None,
        bigquery_destination: Optional[str] = None,
        sync=True,
    ) -> Optional[models.Model]:
        """Packages local script and launches training_job.

        Args:
            dataset (
                Union[
                    datasets.ImageDataset,
                    datasets.TabularDataset,
                    datasets.TextDataset,
                    datasets.VideoDataset,
                ]
            ):
                AI Platform to fit this training against.
            annotation_schema_uri (str):
                Google Cloud Storage URI points to a YAML file describing
                annotation schema.
            worker_pools_spec (_DistributedTrainingSpec):
                Worker pools pecs required to run job.
            managed_model (gca_model.Model):
                Model proto if this script produces a Managed Model.
            args (List[Unions[str, int, float]]):
                Command line arguments to be passed to the Python script.
            environment_variables (Dict[str, str]):
                Environment variables to be passed to the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
                At most 10 environment variables can be specified.
                The Name of the environment variable must be unique.

                environment_variables = {
                    'MY_KEY': 'MY_VALUE'
                }
            base_output_dir (str):
                GCS output directory of job. If not provided a
                timestamped directory in the staging directory will be used.

                AI Platform sets the following environment variables when it runs your training code:

                -  AIP_MODEL_DIR: a Cloud Storage URI of a directory intended for saving model artifacts, i.e. <base_output_dir>/model/
                -  AIP_CHECKPOINT_DIR: a Cloud Storage URI of a directory intended for saving checkpoints, i.e. <base_output_dir>/checkpoints/
                -  AIP_TENSORBOARD_LOG_DIR: a Cloud Storage URI of a directory intended for saving TensorBoard logs, i.e. <base_output_dir>/logs/

            service_account (str):
                Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
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

                Supported only for tabular and time series Datasets.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """
        for spec in worker_pool_specs:
            spec["pythonPackageSpec"] = {
                "executorImageUri": self._container_uri,
                "pythonModule": self._python_module,
                "packageUris": [self._package_gcs_uri],
            }

            if args:
                spec["pythonPackageSpec"]["args"] = args

            if environment_variables:
                spec["pythonPackageSpec"]["env"] = [
                    {"name": key, "value": value}
                    for key, value in environment_variables.items()
                ]

        (
            training_task_inputs,
            base_output_dir,
        ) = self._prepare_training_task_inputs_and_output_dir(
            worker_pool_specs=worker_pool_specs,
            base_output_dir=base_output_dir,
            service_account=service_account,
            network=network,
        )

        model = self._run_job(
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=training_task_inputs,
            dataset=dataset,
            annotation_schema_uri=annotation_schema_uri,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=predefined_split_column_name,
            model=managed_model,
            gcs_destination_uri_prefix=base_output_dir,
            bigquery_destination=bigquery_destination,
        )

        return model


class AutoMLVideoTrainingJob(_TrainingJob):

    _supported_training_schemas = (
        schema.training_job.definition.automl_video_classification,
        schema.training_job.definition.automl_video_object_tracking,
        schema.training_job.definition.automl_video_action_recognition,
    )

    def __init__(
        self,
        display_name: str,
        prediction_type: str = "classification",
        model_type: str = "CLOUD",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        training_encryption_spec_key_name: Optional[str] = None,
        model_encryption_spec_key_name: Optional[str] = None,
    ):
        """Constructs a AutoML Video Training Job.

        Args:
            display_name (str):
                Required. The user-defined name of this TrainingPipeline.
            prediction_type (str):
                The type of prediction the Model is to produce, one of:
                    "classification" - A video classification model classifies shots
                        and segments in your videos according to your own defined labels.
                    "object_tracking" - A video object tracking model detects and tracks
                        multiple objects in shots and segments. You can use these
                        models to track objects in your videos according to your
                        own pre-defined, custom labels.
                    "action_recognition" - A video action reconition model pinpoints
                        the location of actions with short temporal durations (~1 second).
            model_type: str = "CLOUD"
                Required. One of the following:
                    "CLOUD" - available for "classification", "object_tracking" and "action_recognition"
                        A Model best tailored to be used within Google Cloud,
                        and which cannot be exported.
                    "MOBILE_VERSATILE_1" - available for "classification", "object_tracking" and "action_recognition"
                        A model that, in addition to being available within Google
                        Cloud, can also be exported (see ModelService.ExportModel)
                        as a TensorFlow or TensorFlow Lite model and used on a
                        mobile or edge device with afterwards.
                    "MOBILE_CORAL_VERSATILE_1" - available only for "object_tracking"
                        A versatile model that is meant to be exported (see
                        ModelService.ExportModel) and used on a Google Coral device.
                    "MOBILE_CORAL_LOW_LATENCY_1" - available only for "object_tracking"
                        A model that trades off quality for low latency, to be
                        exported (see ModelService.ExportModel) and used on a
                        Google Coral device.
                    "MOBILE_JETSON_VERSATILE_1" - available only for "object_tracking"
                        A versatile model that is meant to be exported (see
                        ModelService.ExportModel) and used on an NVIDIA Jetson device.
                    "MOBILE_JETSON_LOW_LATENCY_1" - available only for "object_tracking"
                        A model that trades off quality for low latency, to be
                        exported (see ModelService.ExportModel) and used on an
                        NVIDIA Jetson device.
            project (str):
                Optional. Project to run training in. Overrides project set in aiplatform.init.
            location (str):
                Optional. Location to run training in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to run call training service. Overrides
                credentials set in aiplatform.init.
            training_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the training pipeline. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this TrainingPipeline will be secured by this key.

                Note: Model trained by this TrainingPipeline is also secured
                by this key if ``model_to_upload`` is not set separately.

                Overrides encryption_spec_key_name set in aiplatform.init.
            model_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, the trained Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
        Raises:
            ValueError: When an invalid prediction_type and/or model_type is provided.
        """
        valid_model_types = constants.AUTOML_VIDEO_PREDICTION_MODEL_TYPES.get(
            prediction_type, None
        )

        if not valid_model_types:
            raise ValueError(
                f"'{prediction_type}' is not a supported prediction type for AutoML Video Training. "
                f"Please choose one of: {tuple(constants.AUTOML_VIDEO_PREDICTION_MODEL_TYPES.keys())}."
            )

        if model_type not in valid_model_types:
            raise ValueError(
                f"'{model_type}' is not a supported model_type for prediction_type of '{prediction_type}'. "
                f"Please choose one of: {tuple(valid_model_types)}"
            )

        super().__init__(
            display_name=display_name,
            project=project,
            location=location,
            credentials=credentials,
            training_encryption_spec_key_name=training_encryption_spec_key_name,
            model_encryption_spec_key_name=model_encryption_spec_key_name,
        )

        self._model_type = model_type
        self._prediction_type = prediction_type

    def run(
        self,
        dataset: datasets.VideoDataset,
        training_fraction_split: float = 0.8,
        test_fraction_split: float = 0.2,
        model_display_name: Optional[str] = None,
        sync: bool = True,
    ) -> models.Model:
        """Runs the AutoML Image training job and returns a model.

        Data fraction splits:
        ``training_fraction_split``, and ``test_fraction_split`` may optionally
        be provided, they must sum to up to 1. If none of the fractions are set,
        by default roughly 80% of data will be used for training, and 20% for test.

        Args:
            dataset (datasets.VideoDataset):
                Required. The dataset within the same Project from which data will be used to train the Model. The
                Dataset must use schema compatible with Model being trained,
                and what is compatible should be described in the used
                TrainingPipeline's [training_task_definition]
                [google.cloud.aiplatform.v1beta1.TrainingPipeline.training_task_definition].
                For tabular Datasets, all their data is exported to
                training, to pick and choose from.
            training_fraction_split: float = 0.8
                Required. The fraction of the input data that is to be
                used to train the Model. This is ignored if Dataset is not provided.
            test_fraction_split: float = 0.2
                Required. The fraction of the input data that is to be
                used to evaluate the Model. This is ignored if Dataset is not provided.
            model_display_name (str):
                Optional. The display name of the managed AI Platform Model. The name
                can be up to 128 characters long and can be consist of any UTF-8
                characters. If not provided upon creation, the job's display_name is used.
            sync: bool = True
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.

        Raises:
            RuntimeError: If Training job has already been run or is waiting to run.
        """

        if self._is_waiting_to_run():
            raise RuntimeError("AutoML Video Training is already scheduled to run.")

        if self._has_run:
            raise RuntimeError("AutoML Video Training has already run.")

        return self._run(
            dataset=dataset,
            training_fraction_split=training_fraction_split,
            test_fraction_split=test_fraction_split,
            model_display_name=model_display_name,
            sync=sync,
        )

    @base.optional_sync()
    def _run(
        self,
        dataset: datasets.VideoDataset,
        training_fraction_split: float = 0.8,
        test_fraction_split: float = 0.2,
        model_display_name: Optional[str] = None,
        sync: bool = True,
    ) -> models.Model:
        """Runs the training job and returns a model.

        Data fraction splits:
        Any of ``training_fraction_split``, and ``test_fraction_split`` may optionally
        be provided, they must sum to up to 1. If none of the fractions are set,
        by default roughly 80% of data will be used for training, and 20% for test.

        Args:
            dataset (datasets.VideoDataset):
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
            test_fraction_split (float):
                Required. The fraction of the input data that is to be
                used to evaluate the Model. This is ignored if Dataset is not provided.
            model_display_name (str):
                Optional. The display name of the managed AI Platform Model. The name
                can be up to 128 characters long and can be consist of any UTF-8
                characters. If a `base_model` was provided, the display_name in the
                base_model will be overritten with this value. If not provided upon
                creation, the job's display_name is used.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """

        # Retrieve the objective-specific training task schema based on prediction_type
        training_task_definition = getattr(
            schema.training_job.definition, f"automl_video_{self._prediction_type}"
        )

        training_task_inputs_dict = {
            "modelType": self._model_type,
        }

        # gca Model to be trained
        model_tbt = gca_model.Model(encryption_spec=self._model_encryption_spec)
        model_tbt.display_name = model_display_name or self._display_name

        return self._run_job(
            training_task_definition=training_task_definition,
            training_task_inputs=training_task_inputs_dict,
            dataset=dataset,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=0.0,
            test_fraction_split=test_fraction_split,
            model=model_tbt,
        )

    @property
    def _model_upload_fail_string(self) -> str:
        """Helper property for model upload failure."""
        return (
            f"AutoML Video Training Pipeline {self.resource_name} is not "
            "configured to upload a Model."
        )


class AutoMLTextTrainingJob(_TrainingJob):
    _supported_training_schemas = (
        schema.training_job.definition.automl_text_classification,
        schema.training_job.definition.automl_text_extraction,
        schema.training_job.definition.automl_text_sentiment,
    )

    def __init__(
        self,
        display_name: str,
        prediction_type: str,
        multi_label: bool = False,
        sentiment_max: int = 10,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        training_encryption_spec_key_name: Optional[str] = None,
        model_encryption_spec_key_name: Optional[str] = None,
    ):
        """Constructs a AutoML Text Training Job.

        Args:
            display_name (str):
                Required. The user-defined name of this TrainingPipeline.
            prediction_type (str):
                The type of prediction the Model is to produce, one of:
                    "classification" - A classification model analyzes text data and
                        returns a list of categories that apply to the text found in the data.
                        AI Platform offers both single-label and multi-label text classification models.
                    "extraction" - An entity extraction model inspects text data
                        for known entities referenced in the data and
                        labels those entities in the text.
                    "sentiment" - A sentiment analysis model inspects text data and identifies the
                        prevailing emotional opinion within it, especially to determine a writer's attitude
                        as positive, negative, or neutral.
            multi_label (bool):
                Required and only applicable for text classification task. If false, a single-label (multi-class) Model will be trained (i.e.
                assuming that for each text snippet just up to one annotation may be
                applicable). If true, a multi-label Model will be trained (i.e.
                assuming that for each text snippet multiple annotations may be
                applicable).
            sentiment_max (int):
                Required and only applicable for sentiment task. A sentiment is expressed as an integer
                ordinal, where higher value means a more
                positive sentiment. The range of sentiments that
                will be used is between 0 and sentimentMax
                (inclusive on both ends), and all the values in
                the range must be represented in the dataset
                before a model can be created.
                Only the Annotations with this sentimentMax will
                be used for training. sentimentMax value must be
                between 1 and 10 (inclusive).
            project (str):
                Optional. Project to run training in. Overrides project set in aiplatform.init.
            location (str):
                Optional. Location to run training in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to run call training service. Overrides
                credentials set in aiplatform.init.
            training_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the training pipeline. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this TrainingPipeline will be secured by this key.

                Note: Model trained by this TrainingPipeline is also secured
                by this key if ``model_to_upload`` is not set separately.

                Overrides encryption_spec_key_name set in aiplatform.init.
            model_encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, the trained Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
        """
        super().__init__(
            display_name=display_name,
            project=project,
            location=location,
            credentials=credentials,
            training_encryption_spec_key_name=training_encryption_spec_key_name,
            model_encryption_spec_key_name=model_encryption_spec_key_name,
        )

        training_task_definition: str
        training_task_inputs_dict: proto.Message

        if prediction_type == "classification":
            training_task_definition = (
                schema.training_job.definition.automl_text_classification
            )

            training_task_inputs_dict = training_job_inputs.AutoMlTextClassificationInputs(
                multi_label=multi_label
            )
        elif prediction_type == "extraction":
            training_task_definition = (
                schema.training_job.definition.automl_text_extraction
            )

            training_task_inputs_dict = training_job_inputs.AutoMlTextExtractionInputs()
        elif prediction_type == "sentiment":
            training_task_definition = (
                schema.training_job.definition.automl_text_sentiment
            )

            training_task_inputs_dict = training_job_inputs.AutoMlTextSentimentInputs(
                sentiment_max=sentiment_max
            )
        else:
            raise ValueError(
                "Prediction type must be one of 'classification', 'extraction', or 'sentiment'."
            )

        self._training_task_definition = training_task_definition
        self._training_task_inputs_dict = training_task_inputs_dict

    def run(
        self,
        dataset: datasets.TextDataset,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        model_display_name: Optional[str] = None,
        sync: bool = True,
    ) -> models.Model:
        """Runs the training job and returns a model.

        Data fraction splits:
        Any of ``training_fraction_split``, ``validation_fraction_split`` and
        ``test_fraction_split`` may optionally be provided, they must sum to up to 1. If
        the provided ones sum to less than 1, the remainder is assigned to sets as
        decided by AI Platform. If none of the fractions are set, by default roughly 80%
        of data will be used for training, 10% for validation, and 10% for test.

        Args:
            dataset (datasets.TextDataset):
                Required. The dataset within the same Project from which data will be used to train the Model. The
                Dataset must use schema compatible with Model being trained,
                and what is compatible should be described in the used
                TrainingPipeline's [training_task_definition]
                [google.cloud.aiplatform.v1beta1.TrainingPipeline.training_task_definition].
            training_fraction_split: float = 0.8
                Required. The fraction of the input data that is to be
                used to train the Model. This is ignored if Dataset is not provided.
            validation_fraction_split: float = 0.1
                Required. The fraction of the input data that is to be
                used to validate the Model. This is ignored if Dataset is not provided.
            test_fraction_split: float = 0.1
                Required. The fraction of the input data that is to be
                used to evaluate the Model. This is ignored if Dataset is not provided.
            model_display_name (str):
                Optional. The display name of the managed AI Platform Model.
                The name can be up to 128 characters long and can consist
                of any UTF-8 characters.

                If not provided upon creation, the job's display_name is used.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Returns:
            model: The trained AI Platform Model resource.

        Raises:
            RuntimeError: If Training job has already been run or is waiting to run.
        """

        if self._is_waiting_to_run():
            raise RuntimeError("AutoML Text Training is already scheduled to run.")

        if self._has_run:
            raise RuntimeError("AutoML Text Training has already run.")

        return self._run(
            dataset=dataset,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            model_display_name=model_display_name,
            sync=sync,
        )

    @base.optional_sync()
    def _run(
        self,
        dataset: datasets.TextDataset,
        training_fraction_split: float = 0.8,
        validation_fraction_split: float = 0.1,
        test_fraction_split: float = 0.1,
        model_display_name: Optional[str] = None,
        sync: bool = True,
    ) -> models.Model:
        """Runs the training job and returns a model.

        Data fraction splits:
        Any of ``training_fraction_split``, ``validation_fraction_split`` and
        ``test_fraction_split`` may optionally be provided, they must sum to up to 1. If
        the provided ones sum to less than 1, the remainder is assigned to sets as
        decided by AI Platform. If none of the fractions are set, by default roughly 80%
        of data will be used for training, 10% for validation, and 10% for test.

        Args:
            dataset (datasets.TextDataset):
                Required. The dataset within the same Project from which data will be used to train the Model. The
                Dataset must use schema compatible with Model being trained,
                and what is compatible should be described in the used
                TrainingPipeline's [training_task_definition]
                [google.cloud.aiplatform.v1beta1.TrainingPipeline.training_task_definition].
                For Text Datasets, all their data is exported to
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
            model_display_name (str):
                Optional. If the script produces a managed AI Platform Model. The display name of
                the Model. The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.

                If not provided upon creation, the job's display_name is used.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            model: The trained AI Platform Model resource or None if training did not
                produce an AI Platform Model.
        """

        if model_display_name is None:
            model_display_name = self._display_name

        model = gca_model.Model(
            display_name=model_display_name,
            encryption_spec=self._model_encryption_spec,
        )

        return self._run_job(
            training_task_definition=self._training_task_definition,
            training_task_inputs=self._training_task_inputs_dict,
            dataset=dataset,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            predefined_split_column_name=None,
            model=model,
        )

    @property
    def _model_upload_fail_string(self) -> str:
        """Helper property for model upload failure."""
        return (
            f"AutoML Text Training Pipeline {self.resource_name} is not "
            "configured to upload a Model."
        )
