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

from typing import Iterable, Optional, Union, Sequence, Dict, List

import abc
import copy
import datetime
import time

from google.cloud import storage
from google.cloud import bigquery

from google.auth import credentials as auth_credentials
from google.protobuf import duration_pb2  # type: ignore
from google.rpc import status_pb2

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import compat
from google.cloud.aiplatform import constants
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import hyperparameter_tuning
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import console_utils
from google.cloud.aiplatform.utils import source_utils
from google.cloud.aiplatform.utils import worker_spec_utils

from google.cloud.aiplatform.compat.services import job_service_client
from google.cloud.aiplatform.compat.types import (
    batch_prediction_job as gca_bp_job_compat,
    batch_prediction_job_v1 as gca_bp_job_v1,
    batch_prediction_job_v1beta1 as gca_bp_job_v1beta1,
    completion_stats as gca_completion_stats,
    custom_job as gca_custom_job_compat,
    custom_job_v1beta1 as gca_custom_job_v1beta1,
    explanation_v1beta1 as gca_explanation_v1beta1,
    io as gca_io_compat,
    io_v1beta1 as gca_io_v1beta1,
    job_state as gca_job_state,
    hyperparameter_tuning_job as gca_hyperparameter_tuning_job_compat,
    hyperparameter_tuning_job_v1beta1 as gca_hyperparameter_tuning_job_v1beta1,
    machine_resources as gca_machine_resources_compat,
    machine_resources_v1beta1 as gca_machine_resources_v1beta1,
    study as gca_study_compat,
)

_LOGGER = base.Logger(__name__)

_JOB_COMPLETE_STATES = (
    gca_job_state.JobState.JOB_STATE_SUCCEEDED,
    gca_job_state.JobState.JOB_STATE_FAILED,
    gca_job_state.JobState.JOB_STATE_CANCELLED,
    gca_job_state.JobState.JOB_STATE_PAUSED,
)

_JOB_ERROR_STATES = (
    gca_job_state.JobState.JOB_STATE_FAILED,
    gca_job_state.JobState.JOB_STATE_CANCELLED,
)


class _Job(base.VertexAiResourceNounWithFutureManager):
    """Class that represents a general Job resource in Vertex AI.
    Cannot be directly instantiated.

    Serves as base class to specific Job types, i.e. BatchPredictionJob or
    DataLabelingJob to re-use shared functionality.

    Subclasses requires one class attribute:

    _getter_method (str): The name of JobServiceClient getter method for specific
    Job type, i.e. 'get_custom_job' for CustomJob
    _cancel_method (str): The name of the specific JobServiceClient cancel method
    _delete_method (str): The name of the specific JobServiceClient delete method
    """

    client_class = utils.JobClientWithOverride
    _is_client_prediction_client = False

    def __init__(
        self,
        job_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrives Job subclass resource by calling a subclass-specific getter
        method.

        Args:
            job_name (str):
                Required. A fully-qualified job resource name or job ID.
                Example: "projects/123/locations/us-central1/batchPredictionJobs/456" or
                "456" when project, location and job_type are initialized or passed.
            project: Optional[str] = None,
                Optional project to retrieve Job subclass from. If not set,
                project set in aiplatform.init will be used.
            location: Optional[str] = None,
                Optional location to retrieve Job subclass from. If not set,
                location set in aiplatform.init will be used.
            credentials: Optional[auth_credentials.Credentials] = None,
                Custom credentials to use. If not set, credentials set in
                aiplatform.init will be used.
        """
        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=job_name,
        )
        self._gca_resource = self._get_gca_resource(resource_name=job_name)

    @property
    def state(self) -> gca_job_state.JobState:
        """Fetch Job again and return the current JobState.

        Returns:
            state (job_state.JobState):
                Enum that describes the state of a Vertex AI job.
        """

        # Fetch the Job again for most up-to-date job state
        self._sync_gca_resource()

        return self._gca_resource.state

    @property
    def start_time(self) -> Optional[datetime.datetime]:
        """Time when the Job resource entered the `JOB_STATE_RUNNING` for the
        first time."""
        self._sync_gca_resource()
        return getattr(self._gca_resource, "start_time")

    @property
    def end_time(self) -> Optional[datetime.datetime]:
        """Time when the Job resource entered the `JOB_STATE_SUCCEEDED`,
        `JOB_STATE_FAILED`, or `JOB_STATE_CANCELLED` state."""
        self._sync_gca_resource()
        return getattr(self._gca_resource, "end_time")

    @property
    def error(self) -> Optional[status_pb2.Status]:
        """Detailed error info for this Job resource. Only populated when the
        Job's state is `JOB_STATE_FAILED` or `JOB_STATE_CANCELLED`."""
        self._sync_gca_resource()
        return getattr(self._gca_resource, "error")

    @property
    @abc.abstractmethod
    def _job_type(cls) -> str:
        """Job type."""
        pass

    @property
    @abc.abstractmethod
    def _cancel_method(cls) -> str:
        """Name of cancellation method for cancelling the specific job type."""
        pass

    def _dashboard_uri(self) -> Optional[str]:
        """Helper method to compose the dashboard uri where job can be
        viewed."""
        fields = utils.extract_fields_from_resource_name(self.resource_name)
        url = f"https://console.cloud.google.com/ai/platform/locations/{fields.location}/{self._job_type}/{fields.id}?project={fields.project}"
        return url

    def _block_until_complete(self):
        """Helper method to block and check on job until complete.

        Raises:
            RuntimeError: If job failed or cancelled.
        """

        # Used these numbers so failures surface fast
        wait = 5  # start at five seconds
        log_wait = 5
        max_wait = 60 * 5  # 5 minute wait
        multiplier = 2  # scale wait by 2 every iteration

        previous_time = time.time()
        while self.state not in _JOB_COMPLETE_STATES:
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

        _LOGGER.info(
            "%s %s current state:\n%s"
            % (
                self.__class__.__name__,
                self._gca_resource.name,
                self._gca_resource.state,
            )
        )
        # Error is only populated when the job state is
        # JOB_STATE_FAILED or JOB_STATE_CANCELLED.
        if self._gca_resource.state in _JOB_ERROR_STATES:
            raise RuntimeError("Job failed with:\n%s" % self._gca_resource.error)
        else:
            _LOGGER.log_action_completed_against_resource("run", "completed", self)

    @classmethod
    def list(
        cls,
        filter: Optional[str] = None,
        order_by: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List[base.VertexAiResourceNoun]:
        """List all instances of this Job Resource.

        Example Usage:

        aiplatform.BatchPredictionJobs.list(
            filter='state="JOB_STATE_SUCCEEDED" AND display_name="my_job"',
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
            List[VertexAiResourceNoun] - A list of Job resource objects
        """

        return cls._list_with_local_order(
            filter=filter,
            order_by=order_by,
            project=project,
            location=location,
            credentials=credentials,
        )

    def cancel(self) -> None:
        """Cancels this Job.

        Success of cancellation is not guaranteed. Use `Job.state`
        property to verify if cancellation was successful.
        """

        _LOGGER.log_action_start_against_resource("Cancelling", "run", self)
        getattr(self.api_client, self._cancel_method)(name=self.resource_name)


class BatchPredictionJob(_Job):

    _resource_noun = "batchPredictionJobs"
    _getter_method = "get_batch_prediction_job"
    _list_method = "list_batch_prediction_jobs"
    _cancel_method = "cancel_batch_prediction_job"
    _delete_method = "delete_batch_prediction_job"
    _job_type = "batch-predictions"

    def __init__(
        self,
        batch_prediction_job_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves a BatchPredictionJob resource and instantiates its
        representation.

        Args:
            batch_prediction_job_name (str):
                Required. A fully-qualified BatchPredictionJob resource name or ID.
                Example: "projects/.../locations/.../batchPredictionJobs/456" or
                "456" when project and location are initialized or passed.
            project: Optional[str] = None,
                Optional project to retrieve BatchPredictionJob from. If not set,
                project set in aiplatform.init will be used.
            location: Optional[str] = None,
                Optional location to retrieve BatchPredictionJob from. If not set,
                location set in aiplatform.init will be used.
            credentials: Optional[auth_credentials.Credentials] = None,
                Custom credentials to use. If not set, credentials set in
                aiplatform.init will be used.
        """

        super().__init__(
            job_name=batch_prediction_job_name,
            project=project,
            location=location,
            credentials=credentials,
        )

    @property
    def output_info(self,) -> Optional[aiplatform.gapic.BatchPredictionJob.OutputInfo]:
        """Information describing the output of this job, including output location
        into which prediction output is written.

        This is only available for batch predicition jobs that have run successfully.
        """
        return self._gca_resource.output_info

    @property
    def partial_failures(self) -> Optional[Sequence[status_pb2.Status]]:
        """Partial failures encountered. For example, single files that can't be read.
        This field never exceeds 20 entries. Status details fields contain standard
        GCP error details."""
        return getattr(self._gca_resource, "partial_failures")

    @property
    def completion_stats(self) -> Optional[gca_completion_stats.CompletionStats]:
        """Statistics on completed and failed prediction instances."""
        return getattr(self._gca_resource, "completion_stats")

    @classmethod
    def create(
        cls,
        job_display_name: str,
        model_name: str,
        instances_format: str = "jsonl",
        predictions_format: str = "jsonl",
        gcs_source: Optional[Union[str, Sequence[str]]] = None,
        bigquery_source: Optional[str] = None,
        gcs_destination_prefix: Optional[str] = None,
        bigquery_destination_prefix: Optional[str] = None,
        model_parameters: Optional[Dict] = None,
        machine_type: Optional[str] = None,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        starting_replica_count: Optional[int] = None,
        max_replica_count: Optional[int] = None,
        generate_explanation: Optional[bool] = False,
        explanation_metadata: Optional["aiplatform.explain.ExplanationMetadata"] = None,
        explanation_parameters: Optional[
            "aiplatform.explain.ExplanationParameters"
        ] = None,
        labels: Optional[dict] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec_key_name: Optional[str] = None,
        sync: bool = True,
    ) -> "BatchPredictionJob":
        """Create a batch prediction job.

        Args:
            job_display_name (str):
                Required. The user-defined name of the BatchPredictionJob.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            model_name (str):
                Required. A fully-qualified model resource name or model ID.
                Example: "projects/123/locations/us-central1/models/456" or
                "456" when project and location are initialized or passed.
            instances_format (str):
                Required. The format in which instances are given, must be one
                of "jsonl", "csv", "bigquery", "tf-record", "tf-record-gzip",
                or "file-list". Default is "jsonl" when using `gcs_source`. If a
                `bigquery_source` is provided, this is overriden to "bigquery".
            predictions_format (str):
                Required. The format in which Vertex AI gives the
                predictions, must be one of "jsonl", "csv", or "bigquery".
                Default is "jsonl" when using `gcs_destination_prefix`. If a
                `bigquery_destination_prefix` is provided, this is overriden to
                "bigquery".
            gcs_source (Optional[Sequence[str]]):
                Google Cloud Storage URI(-s) to your instances to run
                batch prediction on. They must match `instances_format`.
                May contain wildcards. For more information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
            bigquery_source (Optional[str]):
                BigQuery URI to a table, up to 2000 characters long. For example:
                `projectId.bqDatasetId.bqTableId`
            gcs_destination_prefix (Optional[str]):
                The Google Cloud Storage location of the directory where the
                output is to be written to. In the given directory a new
                directory is created. Its name is
                ``prediction-<model-display-name>-<job-create-time>``, where
                timestamp is in YYYY-MM-DDThh:mm:ss.sssZ ISO-8601 format.
                Inside of it files ``predictions_0001.<extension>``,
                ``predictions_0002.<extension>``, ...,
                ``predictions_N.<extension>`` are created where
                ``<extension>`` depends on chosen ``predictions_format``,
                and N may equal 0001 and depends on the total number of
                successfully predicted instances. If the Model has both
                ``instance`` and ``prediction`` schemata defined then each such
                file contains predictions as per the ``predictions_format``.
                If prediction for any instance failed (partially or
                completely), then an additional ``errors_0001.<extension>``,
                ``errors_0002.<extension>``,..., ``errors_N.<extension>``
                files are created (N depends on total number of failed
                predictions). These files contain the failed instances, as
                per their schema, followed by an additional ``error`` field
                which as value has ```google.rpc.Status`` <Status>`__
                containing only ``code`` and ``message`` fields.
            bigquery_destination_prefix (Optional[str]):
                The BigQuery project location where the output is to be
                written to. In the given project a new dataset is created
                with name
                ``prediction_<model-display-name>_<job-create-time>`` where
                is made BigQuery-dataset-name compatible (for example, most
                special characters become underscores), and timestamp is in
                YYYY_MM_DDThh_mm_ss_sssZ "based on ISO-8601" format. In the
                dataset two tables will be created, ``predictions``, and
                ``errors``. If the Model has both ``instance`` and ``prediction``
                schemata defined then the tables have columns as follows:
                The ``predictions`` table contains instances for which the
                prediction succeeded, it has columns as per a concatenation
                of the Model's instance and prediction schemata. The
                ``errors`` table contains rows for which the prediction has
                failed, it has instance columns, as per the instance schema,
                followed by a single "errors" column, which as values has
                ```google.rpc.Status`` <Status>`__ represented as a STRUCT,
                and containing only ``code`` and ``message``.
            model_parameters (Optional[Dict]):
                The parameters that govern the predictions. The schema of
                the parameters may be specified via the Model's `parameters_schema_uri`.
            machine_type (Optional[str]):
                The type of machine for running batch prediction on
                dedicated resources. Not specifying machine type will result in
                batch prediction job being run with automatic resources.
            accelerator_type (Optional[str]):
                The type of accelerator(s) that may be attached
                to the machine as per `accelerator_count`. Only used if
                `machine_type` is set.
            accelerator_count (Optional[int]):
                The number of accelerators to attach to the
                `machine_type`. Only used if `machine_type` is set.
            starting_replica_count (Optional[int]):
                The number of machine replicas used at the start of the batch
                operation. If not set, Vertex AI decides starting number, not
                greater than `max_replica_count`. Only used if `machine_type` is
                set.
            max_replica_count (Optional[int]):
                The maximum number of machine replicas the batch operation may
                be scaled to. Only used if `machine_type` is set.
                Default is 10.
            generate_explanation (bool):
                Optional. Generate explanation along with the batch prediction
                results. This will cause the batch prediction output to include
                explanations based on the `prediction_format`:
                    - `bigquery`: output includes a column named `explanation`. The value
                        is a struct that conforms to the [aiplatform.gapic.Explanation] object.
                    - `jsonl`: The JSON objects on each line include an additional entry
                        keyed `explanation`. The value of the entry is a JSON object that
                        conforms to the [aiplatform.gapic.Explanation] object.
                    - `csv`: Generating explanations for CSV format is not supported.
            explanation_metadata (aiplatform.explain.ExplanationMetadata):
                Optional. Explanation metadata configuration for this BatchPredictionJob.
                Can be specified only if `generate_explanation` is set to `True`.

                This value overrides the value of `Model.explanation_metadata`.
                All fields of `explanation_metadata` are optional in the request. If
                a field of the `explanation_metadata` object is not populated, the
                corresponding field of the `Model.explanation_metadata` object is inherited.
                For more details, see `Ref docs <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.explain.ExplanationParameters):
                Optional. Parameters to configure explaining for Model's predictions.
                Can be specified only if `generate_explanation` is set to `True`.

                This value overrides the value of `Model.explanation_parameters`.
                All fields of `explanation_parameters` are optional in the request. If
                a field of the `explanation_parameters` object is not populated, the
                corresponding field of the `Model.explanation_parameters` object is inherited.
                For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            labels (Optional[dict]):
                The labels with user-defined metadata to organize your
                BatchPredictionJobs. Label keys and values can be no longer than
                64 characters (Unicode codepoints), can only contain lowercase
                letters, numeric characters, underscores and dashes.
                International characters are allowed. See https://goo.gl/xmQnxf
                for more information and examples of labels.
            credentials (Optional[auth_credentials.Credentials]):
                Custom credentials to use to create this batch prediction
                job. Overrides credentials set in aiplatform.init.
            encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the job. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If this is set, then all
                resources created by the BatchPredictionJob will
                be encrypted with the provided encryption key.

                Overrides encryption_spec_key_name set in aiplatform.init.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            (jobs.BatchPredictionJob):
                Instantiated representation of the created batch prediction job.
        """

        utils.validate_display_name(job_display_name)

        model_name = utils.full_resource_name(
            resource_name=model_name,
            resource_noun="models",
            project=project,
            location=location,
        )

        # Raise error if both or neither source URIs are provided
        if bool(gcs_source) == bool(bigquery_source):
            raise ValueError(
                "Please provide either a gcs_source or bigquery_source, "
                "but not both."
            )

        # Raise error if both or neither destination prefixes are provided
        if bool(gcs_destination_prefix) == bool(bigquery_destination_prefix):
            raise ValueError(
                "Please provide either a gcs_destination_prefix or "
                "bigquery_destination_prefix, but not both."
            )

        # Raise error if unsupported instance format is provided
        if instances_format not in constants.BATCH_PREDICTION_INPUT_STORAGE_FORMATS:
            raise ValueError(
                f"{predictions_format} is not an accepted instances format "
                f"type. Please choose from: {constants.BATCH_PREDICTION_INPUT_STORAGE_FORMATS}"
            )

        # Raise error if unsupported prediction format is provided
        if predictions_format not in constants.BATCH_PREDICTION_OUTPUT_STORAGE_FORMATS:
            raise ValueError(
                f"{predictions_format} is not an accepted prediction format "
                f"type. Please choose from: {constants.BATCH_PREDICTION_OUTPUT_STORAGE_FORMATS}"
            )
        gca_bp_job = gca_bp_job_compat
        gca_io = gca_io_compat
        gca_machine_resources = gca_machine_resources_compat
        select_version = compat.DEFAULT_VERSION
        if generate_explanation:
            gca_bp_job = gca_bp_job_v1beta1
            gca_io = gca_io_v1beta1
            gca_machine_resources = gca_machine_resources_v1beta1
            select_version = compat.V1BETA1

        gapic_batch_prediction_job = gca_bp_job.BatchPredictionJob()

        # Required Fields
        gapic_batch_prediction_job.display_name = job_display_name
        gapic_batch_prediction_job.model = model_name

        input_config = gca_bp_job.BatchPredictionJob.InputConfig()
        output_config = gca_bp_job.BatchPredictionJob.OutputConfig()

        if bigquery_source:
            input_config.instances_format = "bigquery"
            input_config.bigquery_source = gca_io.BigQuerySource()
            input_config.bigquery_source.input_uri = bigquery_source
        else:
            input_config.instances_format = instances_format
            input_config.gcs_source = gca_io.GcsSource(
                uris=gcs_source if type(gcs_source) == list else [gcs_source]
            )

        if bigquery_destination_prefix:
            output_config.predictions_format = "bigquery"
            output_config.bigquery_destination = gca_io.BigQueryDestination()

            bq_dest_prefix = bigquery_destination_prefix

            if not bq_dest_prefix.startswith("bq://"):
                bq_dest_prefix = f"bq://{bq_dest_prefix}"

            output_config.bigquery_destination.output_uri = bq_dest_prefix
        else:
            output_config.predictions_format = predictions_format
            output_config.gcs_destination = gca_io.GcsDestination(
                output_uri_prefix=gcs_destination_prefix
            )

        gapic_batch_prediction_job.input_config = input_config
        gapic_batch_prediction_job.output_config = output_config

        # Optional Fields
        gapic_batch_prediction_job.encryption_spec = initializer.global_config.get_encryption_spec(
            encryption_spec_key_name=encryption_spec_key_name,
            select_version=select_version,
        )

        if model_parameters:
            gapic_batch_prediction_job.model_parameters = model_parameters

        # Custom Compute
        if machine_type:

            machine_spec = gca_machine_resources.MachineSpec()
            machine_spec.machine_type = machine_type
            machine_spec.accelerator_type = accelerator_type
            machine_spec.accelerator_count = accelerator_count

            dedicated_resources = gca_machine_resources.BatchDedicatedResources()

            dedicated_resources.machine_spec = machine_spec
            dedicated_resources.starting_replica_count = starting_replica_count
            dedicated_resources.max_replica_count = max_replica_count

            gapic_batch_prediction_job.dedicated_resources = dedicated_resources

            gapic_batch_prediction_job.manual_batch_tuning_parameters = None

        # User Labels
        gapic_batch_prediction_job.labels = labels

        # Explanations
        if generate_explanation:
            gapic_batch_prediction_job.generate_explanation = generate_explanation

        if explanation_metadata or explanation_parameters:
            gapic_batch_prediction_job.explanation_spec = gca_explanation_v1beta1.ExplanationSpec(
                metadata=explanation_metadata, parameters=explanation_parameters
            )

        # TODO (b/174502913): Support private feature once released

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        return cls._create(
            api_client=api_client,
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            batch_prediction_job=gapic_batch_prediction_job,
            generate_explanation=generate_explanation,
            project=project or initializer.global_config.project,
            location=location or initializer.global_config.location,
            credentials=credentials or initializer.global_config.credentials,
            sync=sync,
        )

    @classmethod
    @base.optional_sync()
    def _create(
        cls,
        api_client: job_service_client.JobServiceClient,
        parent: str,
        batch_prediction_job: Union[
            gca_bp_job_v1beta1.BatchPredictionJob, gca_bp_job_v1.BatchPredictionJob
        ],
        generate_explanation: bool,
        project: str,
        location: str,
        credentials: Optional[auth_credentials.Credentials],
        sync: bool = True,
    ) -> "BatchPredictionJob":
        """Create a batch prediction job.

        Args:
            api_client (dataset_service_client.DatasetServiceClient):
                Required. An instance of DatasetServiceClient with the correct api_endpoint
                already set based on user's preferences.
            batch_prediction_job (gca_bp_job.BatchPredictionJob):
                Required. a batch prediction job proto for creating a batch prediction job on Vertex AI.
            generate_explanation (bool):
                Required. Generate explanation along with the batch prediction
                results.
            parent (str):
                Required. Also known as common location path, that usually contains the
                project and location that the user provided to the upstream method.
                Example: "projects/my-prj/locations/us-central1"
            project (str):
                Required. Project to upload this model to. Overrides project set in
                aiplatform.init.
            location (str):
                Required. Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials (Optional[auth_credentials.Credentials]):
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.

        Returns:
            (jobs.BatchPredictionJob):
                Instantiated representation of the created batch prediction job.

        Raises:
            ValueError:
                If no or multiple source or destinations are provided. Also, if
                provided instances_format or predictions_format are not supported
                by Vertex AI.
        """
        # select v1beta1 if explain else use default v1
        if generate_explanation:
            api_client = api_client.select_version(compat.V1BETA1)

        _LOGGER.log_create_with_lro(cls)

        gca_batch_prediction_job = api_client.create_batch_prediction_job(
            parent=parent, batch_prediction_job=batch_prediction_job
        )

        batch_prediction_job = cls(
            batch_prediction_job_name=gca_batch_prediction_job.name,
            project=project,
            location=location,
            credentials=credentials,
        )

        _LOGGER.log_create_complete(cls, batch_prediction_job._gca_resource, "bpj")

        _LOGGER.info(
            "View Batch Prediction Job:\n%s" % batch_prediction_job._dashboard_uri()
        )

        batch_prediction_job._block_until_complete()

        return batch_prediction_job

    def iter_outputs(
        self, bq_max_results: Optional[int] = 100
    ) -> Union[Iterable[storage.Blob], Iterable[bigquery.table.RowIterator]]:
        """Returns an Iterable object to traverse the output files, either a
        list of GCS Blobs or a BigQuery RowIterator depending on the output
        config set when the BatchPredictionJob was created.

        Args:
            bq_max_results: Optional[int] = 100
                Limit on rows to retrieve from prediction table in BigQuery dataset.
                Only used when retrieving predictions from a bigquery_destination_prefix.
                Default is 100.

        Returns:
            Union[Iterable[storage.Blob], Iterable[bigquery.table.RowIterator]]:
                Either a list of GCS Blob objects within the prediction output
                directory or an iterable BigQuery RowIterator with predictions.

        Raises:
            RuntimeError:
                If BatchPredictionJob is in a JobState other than SUCCEEDED,
                since outputs cannot be retrieved until the Job has finished.
            NotImplementedError:
                If BatchPredictionJob succeeded and output_info does not have a
                GCS or BQ output provided.
        """

        if self.state != gca_job_state.JobState.JOB_STATE_SUCCEEDED:
            raise RuntimeError(
                f"Cannot read outputs until BatchPredictionJob has succeeded, "
                f"current state: {self._gca_resource.state}"
            )

        output_info = self._gca_resource.output_info

        # GCS Destination, return Blobs
        if output_info.gcs_output_directory:

            # Build a Storage Client using the same credentials as JobServiceClient
            storage_client = storage.Client(
                project=self.project,
                credentials=self.api_client._transport._credentials,
            )

            gcs_bucket, gcs_prefix = utils.extract_bucket_and_prefix_from_gcs_path(
                output_info.gcs_output_directory
            )

            blobs = storage_client.list_blobs(gcs_bucket, prefix=gcs_prefix)

            return blobs

        # BigQuery Destination, return RowIterator
        elif output_info.bigquery_output_dataset:

            # Build a BigQuery Client using the same credentials as JobServiceClient
            bq_client = bigquery.Client(
                project=self.project,
                credentials=self.api_client._transport._credentials,
            )

            # Format from service is `bq://projectId.bqDatasetId`
            bq_dataset = output_info.bigquery_output_dataset

            if bq_dataset.startswith("bq://"):
                bq_dataset = bq_dataset[5:]

            # # Split project ID and BQ dataset ID
            _, bq_dataset_id = bq_dataset.split(".", 1)

            row_iterator = bq_client.list_rows(
                table=f"{bq_dataset_id}.predictions", max_results=bq_max_results
            )

            return row_iterator

        # Unknown Destination type
        else:
            raise NotImplementedError(
                f"Unsupported batch prediction output location, here are details"
                f"on your prediction output:\n{output_info}"
            )


class _RunnableJob(_Job):
    """ABC to interface job as a runnable training class."""

    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Initializes job with project, location, and api_client.

        Args:
            project(str): Project of the resource noun.
            location(str): The location of the resource noun.
            credentials(google.auth.crendentials.Crendentials): Optional custom
                credentials to use when accessing interacting with resource noun.
        """

        base.VertexAiResourceNounWithFutureManager.__init__(
            self, project=project, location=location, credentials=credentials
        )

        self._parent = aiplatform.initializer.global_config.common_location_path(
            project=project, location=location
        )

    @abc.abstractmethod
    def run(self) -> None:
        pass

    @property
    def _has_run(self) -> bool:
        """Property returns true if this class has a resource name."""
        return bool(self._gca_resource.name)

    @property
    def state(self) -> gca_job_state.JobState:
        """Current state of job.

        Raises:
            RuntimeError if job run has not been called.
        """
        if not self._has_run:
            raise RuntimeError("Job has not run. No state available.")

        return super().state

    @classmethod
    def get(
        cls,
        resource_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "_RunnableJob":
        """Get a Vertex AI Job for the given resource_name.

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

        Returns:
            A Vertex AI Job.
        """
        self = cls._empty_constructor(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=resource_name,
        )

        self._gca_resource = self._get_gca_resource(resource_name=resource_name)

        return self


class DataLabelingJob(_Job):
    _resource_noun = "dataLabelingJobs"
    _getter_method = "get_data_labeling_job"
    _list_method = "list_data_labeling_jobs"
    _cancel_method = "cancel_data_labeling_job"
    _delete_method = "delete_data_labeling_job"
    _job_type = "labeling-tasks"
    pass


class CustomJob(_RunnableJob):
    """Vertex AI Custom Job."""

    _resource_noun = "customJobs"
    _getter_method = "get_custom_job"
    _list_method = "list_custom_jobs"
    _cancel_method = "cancel_custom_job"
    _delete_method = "delete_custom_job"
    _job_type = "training"

    def __init__(
        self,
        display_name: str,
        worker_pool_specs: Union[List[Dict], List[aiplatform.gapic.WorkerPoolSpec]],
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec_key_name: Optional[str] = None,
        staging_bucket: Optional[str] = None,
    ):
        """Cosntruct a Custom Job with Worker Pool Specs.

        ```
        Example usage:
        worker_pool_specs = [
                {
                    "machine_spec": {
                        "machine_type": "n1-standard-4",
                        "accelerator_type": "NVIDIA_TESLA_K80",
                        "accelerator_count": 1,
                    },
                    "replica_count": 1,
                    "container_spec": {
                        "image_uri": container_image_uri,
                        "command": [],
                        "args": [],
                    },
                }
            ]

        my_job = aiplatform.CustomJob(
            display_name='my_job',
            worker_pool_specs=worker_pool_specs
        )

        my_job.run()
        ```


        For more information on configuring worker pool specs please visit:
        https://cloud.google.com/ai-platform-unified/docs/training/create-custom-job


        Args:
            display_name (str):
                Required. The user-defined name of the HyperparameterTuningJob.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            worker_pool_specs (Union[List[Dict], List[aiplatform.gapic.WorkerPoolSpec]]):
                Required. The spec of the worker pools including machine type and Docker image.
                Can provided as a list of dictionaries or list of WorkerPoolSpec proto messages.
            project (str):
                Optional.Project to run the custom job in. Overrides project set in aiplatform.init.
            location (str):
                Optional.Location to run the custom job in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional.Custom credentials to use to run call custom job service. Overrides
                credentials set in aiplatform.init.
            encryption_spec_key_name (str):
                Optional.Customer-managed encryption key name for a
                CustomJob. If this is set, then all resources
                created by the CustomJob will be encrypted with
                the provided encryption key.
            staging_bucket (str):
                Optional. Bucket for produced custom job artifacts. Overrides
                staging_bucket set in aiplatform.init.

        Raises:
            RuntimeError is not staging bucket was set using aiplatfrom.init and a staging
            bucket was not passed in.
        """

        super().__init__(project=project, location=location, credentials=credentials)

        staging_bucket = staging_bucket or initializer.global_config.staging_bucket

        if not staging_bucket:
            raise RuntimeError(
                "staging_bucket should be passed to CustomJob constructor or "
                "should be set using aiplatform.init(staging_bucket='gs://my-bucket')"
            )

        self._gca_resource = gca_custom_job_compat.CustomJob(
            display_name=display_name,
            job_spec=gca_custom_job_compat.CustomJobSpec(
                worker_pool_specs=worker_pool_specs,
                base_output_directory=gca_io_compat.GcsDestination(
                    output_uri_prefix=staging_bucket
                ),
            ),
            encryption_spec=initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name
            ),
        )

    @property
    def network(self) -> Optional[str]:
        """The full name of the Google Compute Engine
        [network](https://cloud.google.com/vpc/docs/vpc#networks) to which this
        CustomJob should be peered.

        Takes the format `projects/{project}/global/networks/{network}`. Where
        {project} is a project number, as in `12345`, and {network} is a network name.

        Private services access must already be configured for the network. If left
        unspecified, the CustomJob is not peered with any network.
        """
        return getattr(self._gca_resource, "network")

    @classmethod
    def from_local_script(
        cls,
        display_name: str,
        script_path: str,
        container_uri: str,
        args: Optional[List[Union[str, float, int]]] = None,
        requirements: Optional[Sequence[str]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        replica_count: int = 1,
        machine_type: str = "n1-standard-4",
        accelerator_type: str = "ACCELERATOR_TYPE_UNSPECIFIED",
        accelerator_count: int = 0,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec_key_name: Optional[str] = None,
        staging_bucket: Optional[str] = None,
    ) -> "CustomJob":
        """Configures a custom job from a local script.

        Example usage:
        ```
        job = aiplatform.CustomJob.from_local_script(
            display_name="my-custom-job",
            script_path="training_script.py",
            container_uri="gcr.io/cloud-aiplatform/training/tf-cpu.2-2:latest",
            requirements=["gcsfs==0.7.1"],
            replica_count=1,
            args=['--dataset', 'gs://my-bucket/my-dataset',
            '--model_output_uri', 'gs://my-bucket/model']
        )

        job.run()
        ```

        Args:
            display_name (str):
                Required. The user-defined name of this CustomJob.
            script_path (str):
                Required. Local path to training script.
            container_uri (str):
                Required: Uri of the training container image to use for custom job.
            args (Optional[List[Union[str, float, int]]]):
                Optional. Command line arguments to be passed to the Python task.
            requirements (Sequence[str]):
                Optional. List of python packages dependencies of script.
            environment_variables (Dict[str, str]):
                Optional. Environment variables to be passed to the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
                At most 10 environment variables can be specified.
                The Name of the environment variable must be unique.

                environment_variables = {
                    'MY_KEY': 'MY_VALUE'
                }
            replica_count (int):
                Optional. The number of worker replicas. If replica count = 1 then one chief
                replica will be provisioned. If replica_count > 1 the remainder will be
                provisioned as a worker replica pool.
            machine_type (str):
                Optional. The type of machine to use for training.
            accelerator_type (str):
                Optional. Hardware accelerator type. One of ACCELERATOR_TYPE_UNSPECIFIED,
                NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100, NVIDIA_TESLA_P4,
                NVIDIA_TESLA_T4
            accelerator_count (int):
                Optional. The number of accelerators to attach to a worker replica.
            project (str):
                Optional. Project to run the custom job in. Overrides project set in aiplatform.init.
            location (str):
                Optional. Location to run the custom job in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to run call custom job service. Overrides
                credentials set in aiplatform.init.
            encryption_spec_key_name (str):
                Optional. Customer-managed encryption key name for a
                CustomJob. If this is set, then all resources
                created by the CustomJob will be encrypted with
                the provided encryption key.
            staging_bucket (str):
                Optional. Bucket for produced custom job artifacts. Overrides
                staging_bucket set in aiplatform.init.

        Raises:
            RuntimeError is not staging bucket was set using aiplatfrom.init and a staging
            bucket was not passed in.
        """

        project = project or initializer.global_config.project
        location = location or initializer.global_config.location
        staging_bucket = staging_bucket or initializer.global_config.staging_bucket

        if not staging_bucket:
            raise RuntimeError(
                "staging_bucket should be passed to CustomJob.from_local_script or "
                "should be set using aiplatform.init(staging_bucket='gs://my-bucket')"
            )

        worker_pool_specs = worker_spec_utils._DistributedTrainingSpec.chief_worker_pool(
            replica_count=replica_count,
            machine_type=machine_type,
            accelerator_count=accelerator_count,
            accelerator_type=accelerator_type,
        ).pool_specs

        python_packager = source_utils._TrainingScriptPythonPackager(
            script_path=script_path, requirements=requirements
        )

        package_gcs_uri = python_packager.package_and_copy_to_gcs(
            gcs_staging_dir=staging_bucket, project=project, credentials=credentials,
        )

        for spec in worker_pool_specs:
            spec["python_package_spec"] = {
                "executor_image_uri": container_uri,
                "python_module": python_packager.module_name,
                "package_uris": [package_gcs_uri],
            }

            if args:
                spec["python_package_spec"]["args"] = args

            if environment_variables:
                spec["python_package_spec"]["env"] = [
                    {"name": key, "value": value}
                    for key, value in environment_variables.items()
                ]

        return cls(
            display_name=display_name,
            worker_pool_specs=worker_pool_specs,
            project=project,
            location=location,
            credentials=credentials,
            encryption_spec_key_name=encryption_spec_key_name,
            staging_bucket=staging_bucket,
        )

    @base.optional_sync()
    def run(
        self,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        timeout: Optional[int] = None,
        restart_job_on_worker_restart: bool = False,
        tensorboard: Optional[str] = None,
        sync: bool = True,
    ) -> None:
        """Run this configured CustomJob.

        Args:
            service_account (str):
                Optional. Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                Optional. The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
            timeout (int):
                The maximum job running time in seconds. The default is 7 days.
            restart_job_on_worker_restart (bool):
                Restarts the entire CustomJob if a worker
                gets restarted. This feature can be used by
                distributed training jobs that are not resilient
                to workers leaving and joining a job.
            tensorboard (str):
                Optional. The name of a Vertex AI
                [Tensorboard][google.cloud.aiplatform.v1beta1.Tensorboard]
                resource to which this CustomJob will upload Tensorboard
                logs. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}``

                The training script should write Tensorboard to following Vertex AI environment
                variable:

                AIP_TENSORBOARD_LOG_DIR

                `service_account` is required with provided `tensorboard`.
                For more information on configuring your service account please visit:
                https://cloud.google.com/vertex-ai/docs/experiments/tensorboard-training
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will unblock and it will be executed in a concurrent Future.
        """

        if service_account:
            self._gca_resource.job_spec.service_account = service_account

        if network:
            self._gca_resource.job_spec.network = network

        if timeout or restart_job_on_worker_restart:
            timeout = duration_pb2.Duration(seconds=timeout) if timeout else None
            self._gca_resource.job_spec.scheduling = gca_custom_job_compat.Scheduling(
                timeout=timeout,
                restart_job_on_worker_restart=restart_job_on_worker_restart,
            )

        if tensorboard:
            v1beta1_gca_resource = gca_custom_job_v1beta1.CustomJob()
            v1beta1_gca_resource._pb.MergeFromString(
                self._gca_resource._pb.SerializeToString()
            )
            self._gca_resource = v1beta1_gca_resource
            self._gca_resource.job_spec.tensorboard = tensorboard

        _LOGGER.log_create_with_lro(self.__class__)

        version = "v1beta1" if tensorboard else "v1"
        self._gca_resource = self.api_client.select_version(version).create_custom_job(
            parent=self._parent, custom_job=self._gca_resource
        )

        _LOGGER.log_create_complete_with_getter(
            self.__class__, self._gca_resource, "custom_job"
        )

        _LOGGER.info("View Custom Job:\n%s" % self._dashboard_uri())

        if tensorboard:
            _LOGGER.info(
                "View Tensorboard:\n%s"
                % console_utils.custom_job_tensorboard_console_uri(
                    tensorboard, self.resource_name
                )
            )

        self._block_until_complete()

    @property
    def job_spec(self):
        return self._gca_resource.job_spec


_SEARCH_ALGORITHM_TO_PROTO_VALUE = {
    "random": gca_study_compat.StudySpec.Algorithm.RANDOM_SEARCH,
    "grid": gca_study_compat.StudySpec.Algorithm.GRID_SEARCH,
    None: gca_study_compat.StudySpec.Algorithm.ALGORITHM_UNSPECIFIED,
}

_MEASUREMENT_SELECTION_TO_PROTO_VALUE = {
    "best": gca_study_compat.StudySpec.MeasurementSelectionType.BEST_MEASUREMENT,
    "last": gca_study_compat.StudySpec.MeasurementSelectionType.LAST_MEASUREMENT,
}


class HyperparameterTuningJob(_RunnableJob):
    """Vertex AI Hyperparameter Tuning Job."""

    _resource_noun = "hyperparameterTuningJobs"
    _getter_method = "get_hyperparameter_tuning_job"
    _list_method = "list_hyperparameter_tuning_jobs"
    _cancel_method = "cancel_hyperparameter_tuning_job"
    _delete_method = "delete_hyperparameter_tuning_job"
    _job_type = "training"

    def __init__(
        self,
        display_name: str,
        custom_job: CustomJob,
        metric_spec: Dict[str, str],
        parameter_spec: Dict[str, hyperparameter_tuning._ParameterSpec],
        max_trial_count: int,
        parallel_trial_count: int,
        max_failed_trial_count: int = 0,
        search_algorithm: Optional[str] = None,
        measurement_selection: Optional[str] = "best",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec_key_name: Optional[str] = None,
    ):
        """
        Configures a HyperparameterTuning Job.

        Example usage:

        ```
        from google.cloud.aiplatform import hyperparameter_tuning as hpt

        worker_pool_specs = [
                {
                    "machine_spec": {
                        "machine_type": "n1-standard-4",
                        "accelerator_type": "NVIDIA_TESLA_K80",
                        "accelerator_count": 1,
                    },
                    "replica_count": 1,
                    "container_spec": {
                        "image_uri": container_image_uri,
                        "command": [],
                        "args": [],
                    },
                }
            ]

        custom_job = aiplatform.CustomJob(
            display_name='my_job',
            worker_pool_specs=worker_pool_specs
        )


        hp_job = aiplatform.HyperparameterTuningJob(
            display_name='hp-test',
            custom_job=job,
            metric_spec={
                'loss': 'minimize',
            },
            parameter_spec={
                'lr': hpt.DoubleParameterSpec(min=0.001, max=0.1, scale='log'),
                'units': hpt.IntegerParameterSpec(min=4, max=128, scale='linear'),
                'activation': hpt.CategoricalParameterSpec(values=['relu', 'selu']),
                'batch_size': hpt.DiscreteParameterSpec(values=[128, 256], scale='linear')
            },
            max_trial_count=128,
            parallel_trial_count=8,
            )

        hp_job.run()

        print(hp_job.trials)
        ```


        For more information on using hyperparameter tuning please visit:
        https://cloud.google.com/ai-platform-unified/docs/training/using-hyperparameter-tuning

        Args:
            display_name (str):
                Required. The user-defined name of the HyperparameterTuningJob.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            custom_job (aiplatform.CustomJob):
                Required. Configured CustomJob. The worker pool spec from this custom job
                applies to the CustomJobs created in all the trials.
            metric_spec: Dict[str, str]
                Required. Dicionary representing metrics to optimize. The dictionary key is the metric_id,
                which is reported by your training job, and the dictionary value is the
                optimization goal of the metric('minimize' or 'maximize'). example:

                metric_spec = {'loss': 'minimize', 'accuracy': 'maximize'}

            parameter_spec (Dict[str, hyperparameter_tuning._ParameterSpec]):
                Required. Dictionary representing parameters to optimize. The dictionary key is the metric_id,
                which is passed into your training job as a command line key word arguemnt, and the
                dictionary value is the parameter specification of the metric.


                from google.cloud.aiplatform import hyperparameter_tuning as hpt

                parameter_spec={
                    'decay': hpt.DoubleParameterSpec(min=1e-7, max=1, scale='linear'),
                    'learning_rate': hpt.DoubleParameterSpec(min=1e-7, max=1, scale='linear')
                    'batch_size': hpt.DiscreteParamterSpec(values=[4, 8, 16, 32, 64, 128], scale='linear')
                }

                Supported parameter specifications can be found until aiplatform.hyperparameter_tuning.
                These parameter specification are currently supported:
                DoubleParameterSpec, IntegerParameterSpec, CategoricalParameterSpace, DiscreteParameterSpec

            max_trial_count (int):
                Reuired. The desired total number of Trials.
            parallel_trial_count (int):
                Required. The desired number of Trials to run in parallel.
            max_failed_trial_count (int):
                Optional. The number of failed Trials that need to be
                seen before failing the HyperparameterTuningJob.
                If set to 0, Vertex AI decides how many Trials
                must fail before the whole job fails.
            search_algorithm (str):
                The search algorithm specified for the Study.
                Accepts one of the following:
                    `None` - If you do not specify an algorithm, your job uses
                    the default Vertex AI algorithm. The default algorithm
                    applies Bayesian optimization to arrive at the optimal
                    solution with a more effective search over the parameter space.

                    'grid' - A simple grid search within the feasible space. This
                    option is particularly useful if you want to specify a quantity
                    of trials that is greater than the number of points in the
                    feasible space. In such cases, if you do not specify a grid
                    search, the Vertex AI default algorithm may generate duplicate
                    suggestions. To use grid search, all parameter specs must be
                    of type `IntegerParameterSpec`, `CategoricalParameterSpace`,
                    or `DiscreteParameterSpec`.

                    'random' - A simple random search within the feasible space.
            measurement_selection (str):
                This indicates which measurement to use if/when the service
                automatically selects the final measurement from previously reported
                intermediate measurements.

                Accepts: 'best', 'last'

                Choose this based on two considerations:
                A) Do you expect your measurements to monotonically improve? If so,
                choose 'last'. On the other hand, if you're in a situation
                where your system can "over-train" and you expect the performance to
                get better for a while but then start declining, choose
                'best'. B) Are your measurements significantly noisy
                and/or irreproducible? If so, 'best' will tend to be
                over-optimistic, and it may be better to choose 'last'. If
                both or neither of (A) and (B) apply, it doesn't matter which
                selection type is chosen.
            project (str):
                Optional. Project to run the HyperparameterTuningjob in. Overrides project set in aiplatform.init.
            location (str):
                Optional. Location to run the HyperparameterTuning in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to run call HyperparameterTuning service. Overrides
                credentials set in aiplatform.init.
            encryption_spec_key_name (str):
                Optional. Customer-managed encryption key options for a
                HyperparameterTuningJob. If this is set, then
                all resources created by the
                HyperparameterTuningJob will be encrypted with
                the provided encryption key.
        """
        super().__init__(project=project, location=location, credentials=credentials)

        metrics = [
            gca_study_compat.StudySpec.MetricSpec(
                metric_id=metric_id, goal=goal.upper()
            )
            for metric_id, goal in metric_spec.items()
        ]

        parameters = [
            parameter._to_parameter_spec(parameter_id=parameter_id)
            for parameter_id, parameter in parameter_spec.items()
        ]

        study_spec = gca_study_compat.StudySpec(
            metrics=metrics,
            parameters=parameters,
            algorithm=_SEARCH_ALGORITHM_TO_PROTO_VALUE[search_algorithm],
            measurement_selection_type=_MEASUREMENT_SELECTION_TO_PROTO_VALUE[
                measurement_selection
            ],
        )

        self._gca_resource = gca_hyperparameter_tuning_job_compat.HyperparameterTuningJob(
            display_name=display_name,
            study_spec=study_spec,
            max_trial_count=max_trial_count,
            parallel_trial_count=parallel_trial_count,
            max_failed_trial_count=max_failed_trial_count,
            trial_job_spec=copy.deepcopy(custom_job.job_spec),
            encryption_spec=initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name
            ),
        )

    @property
    def network(self) -> Optional[str]:
        """The full name of the Google Compute Engine
        [network](https://cloud.google.com/vpc/docs/vpc#networks) to which this
        HyperparameterTuningJob should be peered.

        Takes the format `projects/{project}/global/networks/{network}`. Where
        {project} is a project number, as in `12345`, and {network} is a network name.

        Private services access must already be configured for the network. If left
        unspecified, the HyperparameterTuningJob is not peered with any network.
        """
        return getattr(self._gca_resource.trial_job_spec, "network")

    @base.optional_sync()
    def run(
        self,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        timeout: Optional[int] = None,  # seconds
        restart_job_on_worker_restart: bool = False,
        tensorboard: Optional[str] = None,
        sync: bool = True,
    ) -> None:
        """Run this configured CustomJob.

        Args:
            service_account (str):
                Optional. Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                Optional. The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
            timeout (int):
                Optional. The maximum job running time in seconds. The default is 7 days.
            restart_job_on_worker_restart (bool):
                Restarts the entire CustomJob if a worker
                gets restarted. This feature can be used by
                distributed training jobs that are not resilient
                to workers leaving and joining a job.
            tensorboard (str):
                Optional. The name of a Vertex AI
                [Tensorboard][google.cloud.aiplatform.v1beta1.Tensorboard]
                resource to which this CustomJob will upload Tensorboard
                logs. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}``

                The training script should write Tensorboard to following Vertex AI environment
                variable:

                AIP_TENSORBOARD_LOG_DIR

                `service_account` is required with provided `tensorboard`.
                For more information on configuring your service account please visit:
                https://cloud.google.com/vertex-ai/docs/experiments/tensorboard-training
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will unblock and it will be executed in a concurrent Future.
        """

        if service_account:
            self._gca_resource.trial_job_spec.service_account = service_account

        if network:
            self._gca_resource.trial_job_spec.network = network

        if timeout or restart_job_on_worker_restart:
            duration = duration_pb2.Duration(seconds=timeout) if timeout else None
            self._gca_resource.trial_job_spec.scheduling = gca_custom_job_compat.Scheduling(
                timeout=duration,
                restart_job_on_worker_restart=restart_job_on_worker_restart,
            )

        if tensorboard:
            v1beta1_gca_resource = (
                gca_hyperparameter_tuning_job_v1beta1.HyperparameterTuningJob()
            )
            v1beta1_gca_resource._pb.MergeFromString(
                self._gca_resource._pb.SerializeToString()
            )
            self._gca_resource = v1beta1_gca_resource
            self._gca_resource.trial_job_spec.tensorboard = tensorboard

        _LOGGER.log_create_with_lro(self.__class__)

        version = "v1beta1" if tensorboard else "v1"
        self._gca_resource = self.api_client.select_version(
            version
        ).create_hyperparameter_tuning_job(
            parent=self._parent, hyperparameter_tuning_job=self._gca_resource
        )

        _LOGGER.log_create_complete_with_getter(
            self.__class__, self._gca_resource, "hpt_job"
        )

        _LOGGER.info("View HyperparameterTuningJob:\n%s" % self._dashboard_uri())

        if tensorboard:
            _LOGGER.info(
                "View Tensorboard:\n%s"
                % console_utils.custom_job_tensorboard_console_uri(
                    tensorboard, self.resource_name
                )
            )

        self._block_until_complete()

    @property
    def trials(self) -> List[gca_study_compat.Trial]:
        return list(self._gca_resource.trials)
