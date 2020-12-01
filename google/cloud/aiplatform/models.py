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
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import lro
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import jobs
from google.cloud.aiplatform import constants

from google.cloud.aiplatform_v1beta1.services.endpoint_service.client import (
    EndpointServiceClient,
)
from google.cloud.aiplatform_v1beta1.services import model_service
from google.cloud.aiplatform_v1beta1.services import job_service
from google.cloud.aiplatform_v1beta1 import types
from google.cloud.aiplatform_v1beta1.types import endpoint as gca_endpoint
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types import env_var

from google.cloud.aiplatform_v1beta1.services.prediction_service import (
    client as prediction_service_client,
)
from google.protobuf import json_format


class Model(base.AiPlatformResourceNoun):

    client_class = model_service.ModelServiceClient
    _is_client_prediction_client = False

    @property
    def uri(self):
        """Uri of the model."""
        return self._gca_resource.artifact_uri

    @property
    def description(self):
        """Description of the model."""
        return self._gca_model.description

    def __init__(
        self,
        model_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves the model resource and instantiates its representation.

        Args:
            model_name (str):
                Required. A fully-qualified model resource name or model ID.
                Example: "projects/123/locations/us-central1/models/456" or
                "456" when project and location are initialized or passed.
            project (str):
                Optional project to retrieve model from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional location to retrieve model from. If not set, location
                set in aiplatform.init will be used.
            credentials: Optional[auth_credentials.Credentials]=None,
                Custom credentials to use to upload this model. If not set,
                credentials set in aiplatform.init will be used.
        """

        super().__init__(project=project, location=location, credentials=credentials)
        self._gca_resource = self._get_model(model_name)

    def _get_model(self, model_name: str) -> gca_model.Model:
        """Gets the model from AI Platform.

        Args:
            model_name (str): The name of the model to retrieve.
        Returns:
            model: Managed Model resource.
        """

        model_name = utils.full_resource_name(
            resource_name=model_name,
            resource_noun="models",
            project=self.project,
            location=self.location,
        )
        model = self.api_client.get_model(name=model_name)

        return model

    # TODO(b/170979552) Add support for predict schemata
    # TODO(b/170979926) Add support for metadata and metadata schema
    @classmethod
    def upload(
        cls,
        display_name: str,
        artifact_uri: str,
        serving_container_image_uri: str,
        # TODO (b/162273530) lift requirement for predict/health route when
        # validation lifted and move these args down
        serving_container_predict_route: str,
        serving_container_health_route: str,
        *,
        description: Optional[str] = None,
        serving_container_command: Optional[Sequence[str]] = None,
        serving_container_args: Optional[Sequence[str]] = None,
        serving_container_environment_variables: Optional[Dict[str, str]] = None,
        serving_container_ports: Optional[Sequence[int]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "Model":
        """Uploads a model and returns a Model representing the uploaded Model resource.

        Example usage:

        my_model = Model.upload(
            display_name='my-model',
            artifact_uri='gs://my-model/saved-model'
            serving_container_image_uri='tensorflow/serving'
        )

        Args:
            display_name (str):
                Required. The display name of the Model. The name can be up to 128
                characters long and can be consist of any UTF-8 characters.
            artifact_uri (str):
                Required. The path to the directory containing the Model artifact and
                any of its supporting files. Not present for AutoML Models.
            serving_container_image_uri (str):
                Required. The URI of the Model serving container.
            serving_container_predict_route (str):
                Required. An HTTP path to send prediction requests to the container, and
                which must be supported by it. If not specified a default HTTP path will
                be used by AI Platform.
            serving_container_health_route (str):
                An HTTP path to send health check requests to the container, and which
                must be supported by it. If not specified a standard HTTP path will be
                used by AI Platform.
            description (str):
                The description of the model.
            serving_container_command: Optional[Sequence[str]]=None,
                The command with which the container is run. Not executed within a
                shell. The Docker image's ENTRYPOINT is used if this is not provided.
                Variable references $(VAR_NAME) are expanded using the container's
                environment. If a variable cannot be resolved, the reference in the
                input string will be unchanged. The $(VAR_NAME) syntax can be escaped
                with a double $$, ie: $$(VAR_NAME). Escaped references will never be
                expanded, regardless of whether the variable exists or not.
            serving_container_args: Optional[Sequence[str]]=None,
                The arguments to the command. The Docker image's CMD is used if this is
                not provided. Variable references $(VAR_NAME) are expanded using the
                container's environment. If a variable cannot be resolved, the reference
                in the input string will be unchanged. The $(VAR_NAME) syntax can be
                escaped with a double $$, ie: $$(VAR_NAME). Escaped references will
                never be expanded, regardless of whether the variable exists or not.
            serving_container_environment_variables: Optional[Dict[str, str]]=None,
                The environment variables that are to be present in the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names.
            serving_container_ports: Optional[Sequence[int]]=None,
                Declaration of ports that are exposed by the container. This field is
                primarily informational, it gives AI Platform information about the
                network connections the container uses. Listing or not a port here has
                no impact on whether the port is actually exposed, any port listening on
                the default "0.0.0.0" address inside a container will be accessible from
                the network.
            project: Optional[str]=None,
                Project to upload this model to. Overrides project set in
                aiplatform.init.
            location: Optional[str]=None,
                Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials: Optional[auth_credentials.Credentials]=None,
                Custom credentials to use to upload this model. Overrides credentials
                set in aiplatform.init.
        Returns:
            model: Instantiated representation of the uploaded model resource.
        """
        utils.validate_display_name(display_name)

        api_client = cls._instantiate_client(location, credentials)
        env = None
        ports = None

        if serving_container_environment_variables:
            env = [
                env_var.EnvVar(name=str(key), value=str(value))
                for key, value in serving_container_environment_variables.items()
            ]
        if serving_container_ports:
            ports = [
                gca_model.Port(container_port=port) for port in serving_container_ports
            ]

        container_spec = gca_model.ModelContainerSpec(
            image_uri=serving_container_image_uri,
            command=serving_container_command,
            args=serving_container_args,
            env=env,
            ports=ports,
            predict_route=serving_container_predict_route,
            health_route=serving_container_health_route,
        )

        managed_model = gca_model.Model(
            display_name=display_name,
            description=description,
            artifact_uri=artifact_uri,
            container_spec=container_spec,
        )

        lro = api_client.upload_model(
            parent=initializer.global_config.common_location_path(project, location),
            model=managed_model,
        )

        managed_model = lro.result()
        fields = utils.extract_fields_from_resource_name(managed_model.model)
        return cls(
            model_name=fields.id, project=fields.project, location=fields.location
        )

    # TODO(b/172502059) support deploying with endpoint resource name
    def deploy(
        self,
        endpoint: Optional["Endpoint"] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 1,
        max_replica_count: Optional[int] = 1,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "Endpoint":
        """
        Deploys model to endpoint. Endpoint will be created if unspecified.

        Args:
            endpoint ("Endpoint"):
                Optional. Endpoint to deploy model to. If not specified, endpoint
                display name will be model display name+'_endpoint'.
            deployed_model_display_name (str):
                Optional. The display name of the DeployedModel. If not provided
                upon creation, the Model's display_name is used.
            traffic_percentage (int):
                Optional. Desired traffic to newly deployed model. Defaults to
                0 if there are pre-existing deployed models. Defaults to 100 if
                there are no pre-existing deployed models. Negative values should
                not be provided. Traffic of previously deployed models at the endpoint
                will be scaled down to accommodate new deployed model's traffic.
                Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]):
                Optional. A map from a DeployedModel's ID to the percentage of
                this Endpoint's traffic that should be forwarded to that DeployedModel.
                If a DeployedModel's ID is not listed in this map, then it receives
                no traffic. The traffic percentage values must add up to 100, or
                map must be empty if the Endpoint is to not accept any traffic at
                the moment. Key for model being deployed is "0". Should not be
                provided if traffic_percentage is provided.
            machine_type (str):
                Optional. The type of machine. Not specifying machine type will
                result in model to be deployed with automatic resources.
            min_replica_count (int):
                Optional. The minimum number of machine replicas this deployed
                model will be always deployed on. If traffic against it increases,
                it may dynamically be deployed onto more replicas, and as traffic
                decreases, some of these extra replicas may be freed.
            max_replica_count (int):
                Optional. The maximum number of replicas this deployed model may
                be deployed on when the traffic against it increases. If requested
                value is too large, the deployment will error, but if deployment
                succeeds then the ability to scale the model to that many replicas
                is guaranteed (barring service outages). If traffic against the
                deployed model increases beyond what its replicas at maximum may
                handle, a portion of the traffic will be dropped. If this value
                is not provided, the smaller value of min_replica_count or 1 will
                be used.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
        Returns:
            endpoint ("Endpoint"):
                Endpoint with the deployed model.

        """
        if endpoint is None:
            display_name = self.display_name[:118] + "_endpoint"
            endpoint = Endpoint.create(display_name=display_name)

        endpoint.deploy(
            model=self,
            deployed_model_display_name=deployed_model_display_name,
            traffic_percentage=traffic_percentage,
            traffic_split=traffic_split,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            metadata=metadata,
        )

        return endpoint

    def batch_predict(
        self,
        job_display_name: str,
        gcs_source: Optional[Sequence[str]] = None,
        bigquery_source: Optional[str] = None,
        instances_format: Optional[str] = "jsonl",
        gcs_destination_prefix: Optional[str] = None,
        bigquery_destination_prefix: Optional[str] = None,
        predictions_format: Optional[str] = "jsonl",
        model_parameters: Optional[Dict] = None,
        machine_type: Optional[str] = None,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        starting_replica_count: Optional[int] = None,
        max_replica_count: Optional[int] = None,
        labels: Optional[dict] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> jobs.BatchPredictionJob:
        """Creates a batch prediction job using this Model and outputs prediction
        results to the provided destination prefix in the specified
        `predictions_format`. One source and one destination prefix are required.

        Example usage:

        my_model.batch_predict(
            job_display_name="prediction-123",
            gcs_source="gs://example-bucket/instances.csv",
            instances_format="csv",
            bigquery_destination_prefix="projectId.bqDatasetId.bqTableId"
        )

        Args:
            job_display_name (str):
                Required. The user-defined name of the BatchPredictionJob.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            gcs_source: Optional[Sequence[str]] = None
                Google Cloud Storage URI(-s) to your instances to run
                batch prediction on. They must match `instances_format`.
                May contain wildcards. For more information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
            bigquery_source: Optional[str] = None
                BigQuery URI to a table, up to 2000 characters long. For example:
                `projectId.bqDatasetId.bqTableId`
            instances_format: Optional[str] = "jsonl"
                Required. The format in which instances are given, must be one
                of "jsonl", "csv", "bigquery", "tf-record", "tf-record-gzip",
                or "file-list". Default is "jsonl".
            gcs_destination_prefix: Optional[str] = None
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
            bigquery_destination_prefix: Optional[str] = None
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
            predictions_format: Optional[str] = "jsonl"
                Required. The format in which AI Platform gives the
                predictions, must be one of "jsonl", "csv", or "bigquery".
                Default is "jsonl".
            model_parameters: Optional[Dict] = None
                Optional. The parameters that govern the predictions. The schema of
                the parameters may be specified via the Model's `parameters_schema_uri`.
            machine_type: Optional[str] = None
                Optional. The type of machine for running batch prediction on
                dedicated resources. Not specifying machine type will result in
                batch prediction job being run with automatic resources.
            accelerator_type: Optional[str] = None
                Optional. The type of accelerator(s) that may be attached
                to the machine as per `accelerator_count`. Only used if
                `machine_type` is set.
            accelerator_count: Optional[int] = None
                Optional. The number of accelerators to attach to the
                `machine_type`. Only used if `machine_type` is set.
            starting_replica_count: Optional[int] = None
                The number of machine replicas used at the start of the batch
                operation. If not set, AI Platform decides starting number, not
                greater than `max_replica_count`. Only used if `machine_type` is
                set.
            max_replica_count: Optional[int] = None
                The maximum number of machine replicas the batch operation may
                be scaled to. Only used if `machine_type` is set.
                Default is 10.
            labels: Optional[dict] = None
                Optional. The labels with user-defined metadata to organize your
                BatchPredictionJobs. Label keys and values can be no longer than
                64 characters (Unicode codepoints), can only contain lowercase
                letters, numeric characters, underscores and dashes.
                International characters are allowed. See https://goo.gl/xmQnxf
                for more information and examples of labels.
            location: Optional[str] = None
                Optional. Location to run batch prediction from. If not set,
                location set in aiplatform.init will be used.
            credentials: Optional[auth_credentials.Credentials] = None
                Optional. Custom credentials to use to create this batch prediction
                job. Overrides credentials set in aiplatform.init.
        Returns:
            (BatchPredictionJob):
                Instantiated representation of the created batch prediction job.

        Raises:
            ValueError:
                If no or multiple source or destinations are provided. Also, if
                provided instances_format or predictions_format are not supported
                by AI Platform.
        """

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

        gapic_batch_prediction_job = types.BatchPredictionJob()

        # Required Fields
        gapic_batch_prediction_job.display_name = job_display_name
        gapic_batch_prediction_job.model = self.resource_name

        input_config = types.BatchPredictionJob.InputConfig()
        output_config = types.BatchPredictionJob.OutputConfig()

        if bigquery_source:
            input_config.instances_format = "bigquery"
            input_config.bigquery_source = types.BigQuerySource()
            input_config.bigquery_source.input_uri = bigquery_source
        else:
            input_config.instances_format = instances_format
            input_config.gcs_source = types.GcsSource(
                uris=gcs_source if type(gcs_source) == list else [gcs_source]
            )

        if bigquery_destination_prefix:
            output_config.predictions_format = "bigquery"
            output_config.bigquery_destination = types.BigQueryDestination()

            bq_dest_prefix = bigquery_destination_prefix

            if not bq_dest_prefix.startswith("bq://"):
                bq_dest_prefix = f"bq://{bq_dest_prefix}"

            output_config.bigquery_destination.output_uri = bq_dest_prefix
        else:
            output_config.predictions_format = predictions_format
            output_config.gcs_destination = types.GcsDestination(
                output_uri_prefix=gcs_destination_prefix
            )

        gapic_batch_prediction_job.input_config = input_config
        gapic_batch_prediction_job.output_config = output_config

        # Optional Fields

        if model_parameters:
            gapic_batch_prediction_job.model_parameters = model_parameters

        # Custom Compute
        if machine_type:

            machine_spec = types.MachineSpec()
            machine_spec.machine_type = machine_type
            machine_spec.accelerator_type = accelerator_type
            machine_spec.accelerator_count = accelerator_count

            dedicated_resources = types.BatchDedicatedResources()

            dedicated_resources.machine_spec = machine_spec
            dedicated_resources.starting_replica_count = starting_replica_count
            dedicated_resources.max_replica_count = max_replica_count

            gapic_batch_prediction_job.dedicated_resources = dedicated_resources

            gapic_batch_prediction_job.manual_batch_tuning_parameters = None

        # User Labels
        gapic_batch_prediction_job.labels = labels

        # TODO (b/174502675): Support Explainability on Batch Prediction
        # TODO (b/174502913): Support private feature once released

        # Build BatchPredictionJob request
        create_batch_prediction_job_request = types.CreateBatchPredictionJobRequest(
            parent=f"projects/{self.project}/locations/{self.location}",
            batch_prediction_job=gapic_batch_prediction_job,
        )

        self._job_client = initializer.global_config.create_client(
            client_class=job_service.JobServiceClient,
            credentials=credentials,
            location_override=location,
        )

        # Make blocking call to service
        gapic_batch_prediction_job = self._job_client.create_batch_prediction_job(
            request=create_batch_prediction_job_request
        )

        # Get name of new BatchPredictionJob and return SDK representation
        new_batch_prediction_job_name = gapic_batch_prediction_job.name

        return jobs.BatchPredictionJob(
            batch_prediction_job_name=new_batch_prediction_job_name
        )


class Prediction(NamedTuple):
    """Prediction class envelopes returned Model predictions and the Model id.

    Attributes:
        predictions:
            The predictions that are the output of the predictions
            call. The schema of any single prediction may be specified via
            Endpoint's DeployedModels' [Model's][google.cloud.aiplatform.v1beta1.DeployedModel.model]
            [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
        deployed_model_id:
            ID of the Endpoint's DeployedModel that served this prediction.
    """

    predictions: Dict[str, List]
    deployed_model_id: str


class Endpoint(base.AiPlatformResourceNoun):

    client_class = EndpointServiceClient
    _is_client_prediction_client = False

    def __init__(
        self,
        endpoint_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an endpoint resource.

        Args:
            endpoint_name (str):
                Required. A fully-qualified endpoint resource name or endpoint ID.
                Example: "projects/123/locations/us-central1/endpoints/456" or
                "456" when project and location are initialized or passed.
            project (str):
                Optional. Project to retrieve endpoint from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve endpoint from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(project=project, location=location, credentials=credentials)
        self._gca_resource = self._get_endpoint(endpoint_name)
        self._prediction_client = self._instantiate_prediction_client(
            location=location or initializer.global_config.location,
            credentials=credentials,
        )

    def _get_endpoint(self, endpoint_name: str) -> gca_endpoint.Endpoint:
        """Gets the endpoint from AI Platform.

        Args:
            endpoint_name (str):
                Required. The name of the endpoint to retrieve.
        Returns:
            endpoint (gca_endpoint.Endpoint):
                Managed endpoint resource.
        """

        endpoint_name = utils.full_resource_name(
            resource_name=endpoint_name,
            resource_noun="endpoints",
            project=self.project,
            location=self.location,
        )
        endpoint = self.api_client.get_endpoint(name=endpoint_name)

        return endpoint

    @classmethod
    def create(
        cls,
        display_name: str,
        description: Optional[str] = None,
        labels: Optional[Dict] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "Endpoint":
        """Creates a new endpoint.

        Args:
            display_name (str):
                Required. The user-defined name of the Endpoint.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            description (str):
                Optional. The description of the Endpoint.
            labels (Dict):
                Optional. The labels with user-defined metadata to
                organize your Endpoints.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                and examples of labels.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
            project (str):
                Optional. Project to retrieve endpoint from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve endpoint from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
        Returns:
            endpoint (Endpoint):
                Instantiated representation of the endpoint resource.
        """

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        utils.validate_display_name(display_name)

        create_endpoint_operation = cls._create(
            api_client=api_client,
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            display_name=display_name,
            description=description,
            labels=labels,
            metadata=metadata,
        )

        created_endpoint = create_endpoint_operation.operation_future.result()

        endpoint = cls(
            endpoint_name=created_endpoint.name,
            project=project,
            location=location,
            credentials=credentials,
        )
        return endpoint

    @classmethod
    def _create(
        cls,
        api_client: EndpointServiceClient,
        parent: str,
        display_name: str,
        description: Optional[str] = None,
        labels: Optional[Dict] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> lro.LRO:
        """
        Creates a new endpoint by calling the API client.

        Args:
            api_client (EndpointServiceClient):
                Required. An instance of EndpointServiceClient with the correct
                api_endpoint already set based on user's preferences.
            parent (str):
                Required. Also known as common location path, that usually contains
                the project and location that the user provided to the upstream
                method.
                Example: "projects/my-prj/locations/us-central1"
            display_name (str):
                Required. The user-defined name of the Endpoint.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            description (str):
                Optional. The description of the Endpoint.
            labels (Dict):
                Optional. The labels with user-defined metadata to
                organize your Endpoints.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                and examples of labels.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
        Returns:
            operation (lro.LRO):
                Long-running operation of endpoint creation.
        """
        gapic_endpoint = gca_endpoint.Endpoint(
            display_name=display_name, description=description, labels=labels,
        )

        operation_future = api_client.create_endpoint(
            parent=parent, endpoint=gapic_endpoint, metadata=metadata
        )

        return lro.LRO(operation_future)

    @staticmethod
    def _allocate_traffic(
        traffic_split: Dict[str, int], traffic_percentage: int,
    ) -> Dict[str, int]:
        """
        Allocates desired traffic to new deployed model and scales traffic of
        older deployed models.

        Args:
            traffic_split (Dict[str, int]):
                Required. Current traffic split of deployed models in endpoint.
            traffic_percentage (int):
                Required. Desired traffic to new deployed model.
        Returns:
            new_traffic_split (Dict[str, int]):
                Traffic split to use.
        """
        new_traffic_split = {}
        old_models_traffic = 100 - traffic_percentage
        if old_models_traffic:
            unallocated_traffic = old_models_traffic
            for deployed_model in traffic_split:
                current_traffic = traffic_split[deployed_model]
                new_traffic = int(current_traffic / 100 * old_models_traffic)
                new_traffic_split[deployed_model] = new_traffic
                unallocated_traffic -= new_traffic
            # will likely under-allocate. make total 100.
            for deployed_model in new_traffic_split:
                if unallocated_traffic == 0:
                    break
                new_traffic_split[deployed_model] += 1
                unallocated_traffic -= 1

        new_traffic_split["0"] = traffic_percentage

        return new_traffic_split

    @staticmethod
    def _unallocate_traffic(
        traffic_split: Dict[str, int], deployed_model_id: str,
    ) -> Dict[str, int]:
        """
        Sets deployed model id's traffic to 0 and scales the traffic of other
        deployed models.

        Args:
            traffic_split (Dict[str, int]):
                Required. Current traffic split of deployed models in endpoint.
            deployed_model_id (str):
                Required. Desired traffic to new deployed model.
        Returns:
            new_traffic_split (Dict[str, int]):
                Traffic split to use.
        """
        new_traffic_split = traffic_split.copy()
        del new_traffic_split[deployed_model_id]
        deployed_model_id_traffic = traffic_split[deployed_model_id]
        traffic_percent_left = 100 - deployed_model_id_traffic

        if traffic_percent_left:
            unallocated_traffic = 100
            for deployed_model in new_traffic_split:
                current_traffic = traffic_split[deployed_model]
                new_traffic = int(current_traffic / traffic_percent_left * 100)
                new_traffic_split[deployed_model] = new_traffic
                unallocated_traffic -= new_traffic
            # will likely under-allocate. make total 100.
            for deployed_model in new_traffic_split:
                if unallocated_traffic == 0:
                    break
                new_traffic_split[deployed_model] += 1
                unallocated_traffic -= 1

        new_traffic_split[deployed_model_id] = 0

        return new_traffic_split

    def deploy(
        self,
        model: "Model",
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 1,
        max_replica_count: Optional[int] = 1,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> lro.LRO:
        """
        Deploys a Model to the Endpoint.

        Args:
            model (aiplatform.Model):
                Required. Model to be deployed.
            deployed_model_display_name (str):
                Optional. The display name of the DeployedModel. If not provided
                upon creation, the Model's display_name is used.
            traffic_percentage (int):
                Optional. Desired traffic to newly deployed model. Defaults to
                0 if there are pre-existing deployed models. Defaults to 100 if
                there are no pre-existing deployed models. Negative values should
                not be provided. Traffic of previously deployed models at the endpoint
                will be scaled down to accommodate new deployed model's traffic.
                Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]):
                Optional. A map from a DeployedModel's ID to the percentage of
                this Endpoint's traffic that should be forwarded to that DeployedModel.
                If a DeployedModel's ID is not listed in this map, then it receives
                no traffic. The traffic percentage values must add up to 100, or
                map must be empty if the Endpoint is to not accept any traffic at
                the moment. Key for model being deployed is "0". Should not be
                provided if traffic_percentage is provided.
            machine_type (str):
                Optional. The type of machine. Not specifying machine type will
                result in model to be deployed with automatic resources.
            min_replica_count (int):
                Optional. The minimum number of machine replicas this deployed
                model will be always deployed on. If traffic against it increases,
                it may dynamically be deployed onto more replicas, and as traffic
                decreases, some of these extra replicas may be freed.
            max_replica_count (int):
                Optional. The maximum number of replicas this deployed model may
                be deployed on when the traffic against it increases. If requested
                value is too large, the deployment will error, but if deployment
                succeeds then the ability to scale the model to that many replicas
                is guaranteed (barring service outages). If traffic against the
                deployed model increases beyond what its replicas at maximum may
                handle, a portion of the traffic will be dropped. If this value
                is not provided, the larger value of min_replica_count or 1 will
                be used. If value provided is smaller than min_replica_count, it
                will automatically be increased to be min_replica_count.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
        Returns:
            lro (lro.LRO):
                LRO of model deployment.
        """
        if min_replica_count < 0:
            raise ValueError("Min replica cannot be negative.")
        if max_replica_count < 0:
            raise ValueError("Max replica cannot be negative.")
        if deployed_model_display_name is not None:
            utils.validate_display_name(deployed_model_display_name)

        max_replica_count = max(min_replica_count, max_replica_count)
        if machine_type:
            machine_spec = machine_resources.MachineSpec(machine_type=machine_type)
            dedicated_resources = machine_resources.DedicatedResources(
                machine_spec=machine_spec,
                min_replica_count=min_replica_count,
                max_replica_count=max_replica_count,
            )
            deployed_model = gca_endpoint.DeployedModel(
                dedicated_resources=dedicated_resources,
                model=model.resource_name,
                display_name=deployed_model_display_name,
            )
        else:
            automatic_resources = machine_resources.AutomaticResources(
                min_replica_count=min_replica_count,
                max_replica_count=max_replica_count,
            )
            deployed_model = gca_endpoint.DeployedModel(
                automatic_resources=automatic_resources,
                model=model.resource_name,
                display_name=deployed_model_display_name,
            )

        if traffic_split is None:
            if traffic_percentage > 100:
                raise ValueError("Traffic percentage cannot be greater than 100.")
            if traffic_percentage < 0:
                raise ValueError("Traffic percentage cannot be negative.")

            # new model traffic needs to be 100 if no pre-existing models
            if not self._gca_resource.traffic_split:
                # default scenario
                if traffic_percentage == 0:
                    traffic_percentage = 100
                # verify user specified 100
                elif traffic_percentage < 100:
                    raise ValueError(
                        """There are currently no deployed models so the traffic
                        percentage for this deployed model needs to be 100."""
                    )
            traffic_split = self._allocate_traffic(
                traffic_split=dict(self._gca_resource.traffic_split),
                traffic_percentage=traffic_percentage,
            )
        elif traffic_split:
            traffic_sum = 0
            for item in traffic_split:
                # TODO(b/172678233) verify every referenced deployed model exists
                traffic_sum += traffic_split[item]
            if traffic_sum != 100:
                raise ValueError(
                    "Sum of all traffic within traffic split needs to be 100."
                )

        operation_future = self.api_client.deploy_model(
            endpoint=self.resource_name,
            deployed_model=deployed_model,
            traffic_split=traffic_split,
            metadata=metadata,
        )

        # block before returning
        operation_future.result()

        return

    def undeploy(
        self,
        deployed_model_id: str,
        traffic_split: Optional[Dict[str, int]] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ):
        """Undeploys a deployed model.

        Proportionally adjusts the traffic_split among the remaining deployed
        models of the endpoint.

        Args:
            deployed_model_id (str):
                Required. The ID of the DeployedModel to be undeployed from the
                Endpoint.
            traffic_split (Dict[str, int]):
                Optional. A map from a DeployedModel's ID to the percentage of
                this Endpoint's traffic that should be forwarded to that DeployedModel.
                If a DeployedModel's ID is not listed in this map, then it receives
                no traffic. The traffic percentage values must add up to 100, or
                map must be empty if the Endpoint is to not accept any traffic at
                the moment. Key for model being deployed is "0". Should not be
                provided if traffic_percentage is provided.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
        """
        if traffic_split is None:
            traffic_split = self._unallocate_traffic(
                traffic_split=dict(self._gca_resource.traffic_split),
                deployed_model_id=deployed_model_id,
            )
        else:
            if deployed_model_id in traffic_split and traffic_split[deployed_model_id]:
                raise ValueError("Model being undeployed should have 0 traffic.")
            traffic_sum = 0
            for item in traffic_split:
                # TODO(b/172678233) verify every referenced deployed model exists
                traffic_sum += traffic_split[item]
            if traffic_sum != 100:
                raise ValueError(
                    "Sum of all traffic within traffic split needs to be 100."
                )

        operation_future = self.api_client.undeploy_model(
            endpoint=self.resource_name,
            deployed_model_id=deployed_model_id,
            traffic_split=traffic_split,
            metadata=metadata,
        )

        # block before returning
        operation_future.result()
        return

    @staticmethod
    def _instantiate_prediction_client(
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> prediction_service_client.PredictionServiceClient:
        """Helper method to instantiates prediction client for this endpoint.

        Args:
            location (str): The location of this endpoint.
            credentials (google.auth.credentials.Credentials):
                Optional custom credentials to use when accessing interacting with
                the prediction client.
        Returns:
            prediction_client (prediction_service_client.PredictionServiceClient):
                Initalized prediction client.
        """
        return initializer.global_config.create_client(
            client_class=prediction_service_client.PredictionServiceClient,
            credentials=credentials,
            location_override=location,
            prediction_client=True,
        )

    def predict(self, instances: List, parameters: Optional[Dict] = None) -> Prediction:
        """Make a prediction against this Endpoint.

        Args:
            instances (List):
                Required. Required. The instances that are the input to the
                prediction call. A DeployedModel may have an upper limit
                on the number of instances it supports per request, and
                when it is exceeded the prediction call errors in case
                of AutoML Models, or, in case of customer created
                Models, the behaviour is as documented by that Model.
                The schema of any single instance may be specified via
                Endpoint's DeployedModels'
                [Model's][google.cloud.aiplatform.v1beta1.DeployedModel.model]
                [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
                ``instance_schema_uri``.
            parameters (Dict):
                The parameters that govern the prediction. The schema of
                the parameters may be specified via Endpoint's
                DeployedModels' [Model's
                ][google.cloud.aiplatform.v1beta1.DeployedModel.model]
                [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
                ``parameters_schema_uri``.
        Returns:
            prediction: Prediction with returned predictions and Model Id.

        """
        prediction_response = self._prediction_client.predict(
            endpoint=self.resource_name, instances=instances, parameters=parameters
        )

        return Prediction(
            predictions=[
                json_format.MessageToDict(item)
                for item in prediction_response.predictions.pb
            ],
            deployed_model_id=prediction_response.deployed_model_id,
        )

    # TODO(b/172828587): implement prediction
    def explain(self, instances: List[Dict], parameters: Optional[Dict]) -> List[Dict]:
        """Online prediction with explanation."""
        raise NotImplementedError("Prediction not implemented.")
