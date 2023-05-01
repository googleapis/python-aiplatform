# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
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
import pathlib
import re
import proto
from typing import (
    Any,
    Dict,
    List,
    NamedTuple,
    Optional,
    Sequence,
    TYPE_CHECKING,
    Tuple,
    Union,
)

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import _models
from google.cloud.aiplatform import base
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.constants import (
    prediction as prediction_constants,
)
from google.cloud.aiplatform.preview import explain
from google.cloud.aiplatform.preview.explain import _explanation_utils
from google.cloud.aiplatform.utils import gcs_utils
from google.cloud.aiplatform_v1beta1.types import (
    env_var as env_var_v1beta1,
    model as model_v1beta1,
    model_service as model_service_v1beta1,
    endpoint as endpoint_v1beta1,
    io as io_v1beta1,
    encryption_spec as encryption_spec_v1beta1,
    machine_resources as machine_resources_v1beta1,
    explanation as explanation_v1beta1,
)

from google.cloud.aiplatform import initializer

from google.cloud.aiplatform.compat.services import (
    endpoint_service_client_v1beta1,
)
from google.protobuf import json_format

if TYPE_CHECKING:
    from google.cloud.aiplatform.prediction import LocalModel

_LOGGER = base.Logger(__name__)
_DEFAULT_MACHINE_TYPE = "n1-standard-2"


_SUPPORTED_MODEL_FILE_NAMES = [
    "model.pkl",
    "model.joblib",
    "model.bst",
    "model.mar",
    "saved_model.pb",
    "saved_model.pbtxt",
]


class Prediction(NamedTuple):
    predictions: List[Dict[str, Any]]
    deployed_model_id: str
    model_version_id: Optional[str] = None
    model_resource_name: Optional[str] = None
    explanations: Optional[Sequence[explanation_v1beta1.Explanation]] = None


class EndpointClientWithOverride(utils.EndpointClientWithOverride):
    _default_version = "v1beta1"


class ModelClientWithOverride(utils.ModelClientWithOverride):
    _default_version = "v1beta1"


class PredictionClientWithOverride(utils.PredictionClientWithOverride):
    _default_version = "v1beta1"


class Endpoint(_models._Endpoint):
    """Preview Endpoint resource for Vertex AI."""

    client_class = EndpointClientWithOverride

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

        super(_models._Endpoint, self).__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=endpoint_name,
        )

        endpoint_name = utils.full_resource_name(
            resource_name=endpoint_name,
            resource_noun="endpoints",
            parse_resource_name_method=self._parse_resource_name,
            format_resource_name_method=self._format_resource_name,
            project=project,
            location=location,
        )

        # Lazy load the Endpoint gca_resource until needed
        self._gca_resource = endpoint_v1beta1.Endpoint(name=endpoint_name)

        self._prediction_client = self._instantiate_prediction_client(
            location=self.location,
            credentials=credentials,
        )
        self.authorized_session = None
        self.raw_predict_request_url = None

    @staticmethod
    def _instantiate_prediction_client(
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> PredictionClientWithOverride:
        """Helper method to instantiates prediction client with optional
        overrides for this endpoint.

        Args:
            location (str): The location of this endpoint.
            credentials (google.auth.credentials.Credentials):
                Optional custom credentials to use when accessing interacting with
                the prediction client.

        Returns:
            prediction_client (PredictionServiceClient):
                Initialized prediction client with optional overrides.
        """
        return initializer.global_config.create_client(
            client_class=PredictionClientWithOverride,
            credentials=credentials,
            location_override=location,
            prediction_client=True,
        )

    @classmethod
    def create(
        cls,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec_key_name: Optional[str] = None,
        sync=True,
        create_request_timeout: Optional[float] = None,
        endpoint_id: Optional[str] = None,
        enable_request_response_logging=False,
        request_response_logging_sampling_rate: Optional[float] = None,
        request_response_logging_bq_destination_table: Optional[str] = None,
    ) -> "Endpoint":
        """Creates a new endpoint.

        Args:
            display_name (str):
                Optional. The user-defined name of the Endpoint.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            description (str):
                Optional. The description of the Endpoint.
            labels (Dict[str, str]):
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
                Required. Project to retrieve endpoint from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Required. Location to retrieve endpoint from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
            encryption_spec_key_name (str):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this Endpoint and all sub-resources of this Endpoint will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
            create_request_timeout (float):
                Optional. The timeout for the create request in seconds.
            endpoint_id (str):
                Optional. The ID to use for endpoint, which will become
                the final component of the endpoint resource name. If
                not provided, Vertex AI will generate a value for this
                ID.

                This value should be 1-10 characters, and valid
                characters are /[0-9]/. When using HTTP/JSON, this field
                is populated based on a query string argument, such as
                ``?endpoint_id=12345``. This is the fallback for fields
                that are not included in either the URI or the body.
            enable_request_response_logging (bool):
                Optional. Whether to enable request & response logging for this endpoint.
            request_response_logging_sampling_rate (float):
                Optional. The request response logging sampling rate. If not set, default is 0.0.
            request_response_logging_bq_destination_table (str):
                Optional. The request response logging bigquery destination. If not set, will create a table with name:
                ``bq://{project_id}.logging_{endpoint_display_name}_{endpoint_id}.request_response_logging``.

        Returns:
            endpoint (Endpoint):
                Created endpoint.
        """
        api_client = cls._instantiate_client(location=location, credentials=credentials)

        if not display_name:
            display_name = cls._generate_display_name()

        utils.validate_display_name(display_name)
        if labels:
            utils.validate_labels(labels)

        project = project or initializer.global_config.project
        location = location or initializer.global_config.location

        predict_request_response_logging_config = None
        if enable_request_response_logging:
            predict_request_response_logging_config = (
                endpoint_v1beta1.PredictRequestResponseLoggingConfig(
                    enabled=True,
                    sampling_rate=request_response_logging_sampling_rate,
                    bigquery_destination=io_v1beta1.BigQueryDestination(
                        output_uri=request_response_logging_bq_destination_table
                    ),
                )
            )
        return cls._create(
            api_client=api_client,
            display_name=display_name,
            project=project,
            location=location,
            description=description,
            labels=labels,
            metadata=metadata,
            credentials=credentials,
            encryption_spec=initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name
            ),
            sync=sync,
            create_request_timeout=create_request_timeout,
            endpoint_id=endpoint_id,
            predict_request_response_logging_config=predict_request_response_logging_config,
        )

    @classmethod
    @base.optional_sync()
    def _create(
        cls,
        api_client: endpoint_service_client_v1beta1.EndpointServiceClient,
        display_name: str,
        project: str,
        location: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec: Optional[encryption_spec_v1beta1.EncryptionSpec] = None,
        network: Optional[str] = None,
        sync=True,
        create_request_timeout: Optional[float] = None,
        endpoint_id: Optional[str] = None,
        predict_request_response_logging_config: Optional[
            endpoint_v1beta1.PredictRequestResponseLoggingConfig
        ] = None,
    ) -> "Endpoint":
        """Creates a new endpoint by calling the API client.

        Args:
            api_client (EndpointServiceClient):
                Required. An instance of EndpointServiceClient with the correct
                api_endpoint already set based on user's preferences.
            display_name (str):
                Required. The user-defined name of the Endpoint.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            project (str):
                Required. Project to retrieve endpoint from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Required. Location to retrieve endpoint from. If not set, location
                set in aiplatform.init will be used.
            description (str):
                Optional. The description of the Endpoint.
            labels (Dict[str, str]):
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
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
            encryption_spec (gca_encryption_spec.EncryptionSpec):
                Optional. The Cloud KMS customer managed encryption key used to protect the dataset.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this Dataset and all sub-resources of this Dataset will be secured by this key.
            network (str):
                Optional. The full name of the Compute Engine network to which
                this Endpoint will be peered. E.g. "projects/12345/global/networks/myVPC".
                Private services access must already be configured for the network.
                Read more about PrivateEndpoints
                [in the documentation](https://cloud.google.com/vertex-ai/docs/predictions/using-private-endpoints).
            sync (bool):
                Whether to create this endpoint synchronously.
            create_request_timeout (float):
                Optional. The timeout for the create request in seconds.
            endpoint_id (str):
                Optional. The ID to use for endpoint, which will become
                the final component of the endpoint resource name. If
                not provided, Vertex AI will generate a value for this
                ID.

                This value should be 1-10 characters, and valid
                characters are /[0-9]/. When using HTTP/JSON, this field
                is populated based on a query string argument, such as
                ``?endpoint_id=12345``. This is the fallback for fields
                that are not included in either the URI or the body.
            predict_request_response_logging_config (aiplatform.endpoint.PredictRequestResponseLoggingConfig):
                Optional. The request response logging configuration for online prediction.

        Returns:
            endpoint (Endpoint):
                Created endpoint.
        """

        parent = initializer.global_config.common_location_path(
            project=project, location=location
        )

        gapic_endpoint = endpoint_v1beta1.Endpoint(
            display_name=display_name,
            description=description,
            labels=labels,
            encryption_spec=encryption_spec,
            network=network,
            predict_request_response_logging_config=predict_request_response_logging_config,
        )

        operation_future = api_client.create_endpoint(
            parent=parent,
            endpoint=gapic_endpoint,
            endpoint_id=endpoint_id,
            metadata=metadata,
            timeout=create_request_timeout,
        )

        _LOGGER.log_create_with_lro(cls, operation_future)

        created_endpoint = operation_future.result()

        _LOGGER.log_create_complete(cls, created_endpoint, "endpoint")

        return cls._construct_sdk_resource_from_gapic(
            gapic_resource=created_endpoint,
            project=project,
            location=location,
            credentials=credentials,
        )

    @classmethod
    def _construct_sdk_resource_from_gapic(
        cls,
        gapic_resource: proto.Message,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "Endpoint":
        """Given a GAPIC Endpoint object, return the SDK representation.

        Args:
            gapic_resource (proto.Message):
                A GAPIC representation of a Endpoint resource, usually
                retrieved by a get_* or in a list_* API call.
            project (str):
                Optional. Project to construct Endpoint object from. If not set,
                project set in aiplatform.init will be used.
            location (str):
                Optional. Location to construct Endpoint object from. If not set,
                location set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to construct Endpoint.
                Overrides credentials set in aiplatform.init.

        Returns:
            Endpoint (aiplatform.Endpoint):
                An initialized Endpoint resource.
        """
        endpoint = cls._empty_constructor(
            project=project, location=location, credentials=credentials
        )

        endpoint._gca_resource = gapic_resource

        endpoint._prediction_client = cls._instantiate_prediction_client(
            location=endpoint.location,
            credentials=credentials,
        )
        endpoint.authorized_session = None
        endpoint.raw_predict_request_url = None

        return endpoint

    @classmethod
    def _deploy_call(
        cls,
        api_client: endpoint_service_client_v1beta1.EndpointServiceClient,
        endpoint_resource_name: str,
        model: "Model",
        endpoint_resource_traffic_split: Optional[proto.MapField] = None,
        network: Optional[str] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        service_account: Optional[str] = None,
        explanation_spec: Optional[explain.ExplanationSpec] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
    ):
        """Helper method to deploy model to endpoint.

        Args:
            api_client (endpoint_service_client_v1beta1.EndpointServiceClient):
                Required. endpoint_service_client_v1beta1.EndpointServiceClient to make call.
            endpoint_resource_name (str):
                Required. Endpoint resource name to deploy model to.
            model (aiplatform.Model):
                Required. Model to be deployed.
            endpoint_resource_traffic_split (proto.MapField):
                Optional. Endpoint current resource traffic split.
            network (str):
                Optional. The full name of the Compute Engine network to which
                this Endpoint will be peered. E.g. "projects/123/global/networks/my_vpc".
                Private services access must already be configured for the network.
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
            accelerator_type (str):
                Optional. Hardware accelerator type. Must also set accelerator_count if used.
                One of ACCELERATOR_TYPE_UNSPECIFIED, NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
                NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int):
                Optional. The number of accelerators to attach to a worker replica.
            service_account (str):
                The service account that the DeployedModel's container runs as. Specify the
                email address of the service account. If this service account is not
                specified, the container runs as a service account that doesn't have access
                to the resource project.
                Users deploying the Model must have the `iam.serviceAccounts.actAs`
                permission on this service account.
            explanation_spec (aiplatform.preview.explain.ExplanationSpec):
                Optional. Specification of Model explanation.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
            deploy_request_timeout (float):
                Optional. The timeout for the deploy request in seconds.
            autoscaling_target_cpu_utilization (int):
                Optional. Target CPU Utilization to use for Autoscaling Replicas.
                A default value of 60 will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int):
                Optional. Target Accelerator Duty Cycle.
                Must also set accelerator_type and accelerator_count if specified.
                A default value of 60 will be used if not specified.

        Raises:
            ValueError: If only `accelerator_type` or `accelerator_count` is specified.
            ValueError: If model does not support deployment.
            ValueError: If there is not current traffic split and traffic percentage
                is not 0 or 100.
        """

        max_replica_count = max(min_replica_count, max_replica_count)

        if bool(accelerator_type) != bool(accelerator_count):
            raise ValueError(
                "Both `accelerator_type` and `accelerator_count` should be specified or None."
            )

        if autoscaling_target_accelerator_duty_cycle is not None and (
            not accelerator_type or not accelerator_count
        ):
            raise ValueError(
                "Both `accelerator_type` and `accelerator_count` should be set "
                "when specifying autoscaling_target_accelerator_duty_cycle`"
            )

        deployed_model = endpoint_v1beta1.DeployedModel(
            model=model.versioned_resource_name,
            display_name=deployed_model_display_name,
            service_account=service_account,
        )

        supports_automatic_resources = (
            model_v1beta1.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
            in model.supported_deployment_resources_types
        )
        supports_dedicated_resources = (
            model_v1beta1.Model.DeploymentResourcesType.DEDICATED_RESOURCES
            in model.supported_deployment_resources_types
        )
        provided_custom_machine_spec = (
            machine_type
            or accelerator_type
            or accelerator_count
            or autoscaling_target_accelerator_duty_cycle
            or autoscaling_target_cpu_utilization
        )

        # If the model supports both automatic and dedicated deployment resources,
        # decide based on the presence of machine spec customizations
        use_dedicated_resources = supports_dedicated_resources and (
            not supports_automatic_resources or provided_custom_machine_spec
        )

        if provided_custom_machine_spec and not use_dedicated_resources:
            _LOGGER.info(
                "Model does not support dedicated deployment resources. "
                "The machine_type, accelerator_type and accelerator_count,"
                "autoscaling_target_accelerator_duty_cycle,"
                "autoscaling_target_cpu_utilization parameters are ignored."
            )

        if use_dedicated_resources and not machine_type:
            machine_type = _DEFAULT_MACHINE_TYPE
            _LOGGER.info(f"Using default machine_type: {machine_type}")

        if use_dedicated_resources:

            dedicated_resources = machine_resources_v1beta1.DedicatedResources(
                min_replica_count=min_replica_count,
                max_replica_count=max_replica_count,
            )

            machine_spec = machine_resources_v1beta1.MachineSpec(
                machine_type=machine_type
            )

            if autoscaling_target_cpu_utilization:
                autoscaling_metric_spec = machine_resources_v1beta1.AutoscalingMetricSpec(
                    metric_name="aiplatform.googleapis.com/prediction/online/cpu/utilization",
                    target=autoscaling_target_cpu_utilization,
                )
                dedicated_resources.autoscaling_metric_specs.extend(
                    [autoscaling_metric_spec]
                )

            if accelerator_type and accelerator_count:
                utils.validate_accelerator_type(accelerator_type)
                machine_spec.accelerator_type = accelerator_type
                machine_spec.accelerator_count = accelerator_count

                if autoscaling_target_accelerator_duty_cycle:
                    autoscaling_metric_spec = machine_resources_v1beta1.AutoscalingMetricSpec(
                        metric_name="aiplatform.googleapis.com/prediction/online/accelerator/duty_cycle",
                        target=autoscaling_target_accelerator_duty_cycle,
                    )
                    dedicated_resources.autoscaling_metric_specs.extend(
                        [autoscaling_metric_spec]
                    )

            dedicated_resources.machine_spec = machine_spec
            deployed_model.dedicated_resources = dedicated_resources

        elif supports_automatic_resources:
            deployed_model.automatic_resources = (
                machine_resources_v1beta1.AutomaticResources(
                    min_replica_count=min_replica_count,
                    max_replica_count=max_replica_count,
                )
            )
        else:
            _LOGGER.warning(
                "Model does not support deployment. "
                "See https://cloud.google.com/vertex-ai/docs/reference/rpc/google.cloud.aiplatform.v1#google.cloud.aiplatform.v1.Model.FIELDS.repeated.google.cloud.aiplatform.v1.Model.DeploymentResourcesType.google.cloud.aiplatform.v1.Model.supported_deployment_resources_types"
            )

        deployed_model.explanation_spec = explanation_spec

        # Checking if traffic percentage is valid
        # TODO(b/221059294) PrivateEndpoint should support traffic split
        if traffic_split is None and not network:
            # new model traffic needs to be 100 if no pre-existing models
            if not endpoint_resource_traffic_split:
                # default scenario
                if traffic_percentage == 0:
                    traffic_percentage = 100
                # verify user specified 100
                elif traffic_percentage < 100:
                    raise ValueError(
                        """There are currently no deployed models so the traffic
                        percentage for this deployed model needs to be 100."""
                    )
            traffic_split = cls._allocate_traffic(
                traffic_split=dict(endpoint_resource_traffic_split),
                traffic_percentage=traffic_percentage,
            )

        operation_future = api_client.deploy_model(
            endpoint=endpoint_resource_name,
            deployed_model=deployed_model,
            traffic_split=traffic_split,
            metadata=metadata,
            timeout=deploy_request_timeout,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Deploy", "model", cls, operation_future
        )

        operation_future.result(timeout=None)

    def explain(
        self,
        instances: List[Dict],
        parameters: Optional[Dict] = None,
        deployed_model_id: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Prediction:
        """Make a prediction with explanations against this Endpoint.

        Example usage:
            response = my_endpoint.explain(instances=[...])
            my_explanations = response.explanations

        Args:
            instances (List):
                Required. The instances that are the input to the
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
            deployed_model_id (str):
                Optional. If specified, this ExplainRequest will be served by the
                chosen DeployedModel, overriding this Endpoint's traffic split.
            timeout (float): Optional. The timeout for this request in seconds.

        Returns:
            prediction (aiplatform.preview.explain.Prediction):
                Prediction with returned predictions, explanations, and Model ID.
        """
        self.wait()

        explain_response = self._prediction_client.explain(
            endpoint=self.resource_name,
            instances=instances,
            parameters=parameters,
            deployed_model_id=deployed_model_id,
            timeout=timeout,
        )

        return Prediction(
            predictions=[
                json_format.MessageToDict(item)
                for item in explain_response.predictions.pb
            ],
            deployed_model_id=explain_response.deployed_model_id,
            explanations=explain_response.explanations,
        )

    def undeploy_all(self, sync: bool = True) -> "Endpoint":
        """Undeploys every model deployed to this Endpoint.

        Args:
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        """
        self._sync_gca_resource()

        models_in_traffic_split = sorted(  # Undeploy zero traffic models first
            self._gca_resource.traffic_split.keys(),
            key=lambda id: self._gca_resource.traffic_split[id],
        )

        # Some deployed models may not in the traffic_split dict.
        # These models have 0% traffic and should be undeployed first.
        models_not_in_traffic_split = [
            deployed_model.id
            for deployed_model in self._gca_resource.deployed_models
            if deployed_model.id not in models_in_traffic_split
        ]

        models_to_undeploy = models_not_in_traffic_split + models_in_traffic_split

        for deployed_model in models_to_undeploy:
            self._undeploy(deployed_model_id=deployed_model, sync=sync)

        return self


class PrivateEndpoint(Endpoint):
    pass


class Model(_models._Model):
    """Preview Model resource for Vertex AI."""

    client_class = ModelClientWithOverride

    @classmethod
    @base.optional_sync()
    def upload(
        cls,
        serving_container_image_uri: Optional[str] = None,
        *,
        artifact_uri: Optional[str] = None,
        model_id: Optional[str] = None,
        parent_model: Optional[str] = None,
        is_default_version: bool = True,
        version_aliases: Optional[Sequence[str]] = None,
        version_description: Optional[str] = None,
        serving_container_predict_route: Optional[str] = None,
        serving_container_health_route: Optional[str] = None,
        description: Optional[str] = None,
        serving_container_command: Optional[Sequence[str]] = None,
        serving_container_args: Optional[Sequence[str]] = None,
        serving_container_environment_variables: Optional[Dict[str, str]] = None,
        serving_container_ports: Optional[Sequence[int]] = None,
        local_model: Optional["LocalModel"] = None,
        instance_schema_uri: Optional[str] = None,
        parameters_schema_uri: Optional[str] = None,
        prediction_schema_uri: Optional[str] = None,
        explanation_metadata: Optional[explain.ExplanationMetadata] = None,
        explanation_parameters: Optional[explain.ExplanationParameters] = None,
        display_name: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        labels: Optional[Dict[str, str]] = None,
        encryption_spec_key_name: Optional[str] = None,
        staging_bucket: Optional[str] = None,
        sync=True,
        upload_request_timeout: Optional[float] = None,
    ) -> "Model":
        """Uploads a model and returns a Model representing the uploaded Model
        resource.

        Example usage:
            my_model = Model.upload(
                display_name="my-model",
                artifact_uri="gs://my-model/saved-model",
                serving_container_image_uri="tensorflow/serving"
            )

        Args:
            serving_container_image_uri (str):
                Optional. The URI of the Model serving container. This parameter is required
                if the parameter `local_model` is not specified.
            artifact_uri (str):
                Optional. The path to the directory containing the Model artifact and
                any of its supporting files. Leave blank for custom container prediction.
                Not present for AutoML Models.
            model_id (str):
                Optional. The ID to use for the uploaded Model, which will
                become the final component of the model resource name.
                This value may be up to 63 characters, and valid characters
                are `[a-z0-9_-]`. The first character cannot be a number or hyphen.
            parent_model (str):
                Optional. The resource name or model ID of an existing model that the
                newly-uploaded model will be a version of.

                Only set this field when uploading a new version of an existing model.
            is_default_version (bool):
                Optional. When set to True, the newly uploaded model version will
                automatically have alias "default" included. Subsequent uses of
                this model without a version specified will use this "default" version.

                When set to False, the "default" alias will not be moved.
                Actions targeting the newly-uploaded model version will need
                to specifically reference this version by ID or alias.

                New model uploads, i.e. version 1, will always be "default" aliased.
            version_aliases (Sequence[str]):
                Optional. User provided version aliases so that a model version
                can be referenced via alias instead of auto-generated version ID.
                A default version alias will be created for the first version of the model.

                The format is [a-z][a-zA-Z0-9-]{0,126}[a-z0-9]
            version_description (str):
                Optional. The description of the model version being uploaded.
            serving_container_predict_route (str):
                Optional. An HTTP path to send prediction requests to the container, and
                which must be supported by it. If not specified a default HTTP path will
                be used by Vertex AI.
            serving_container_health_route (str):
                Optional. An HTTP path to send health check requests to the container, and which
                must be supported by it. If not specified a standard HTTP path will be
                used by Vertex AI.
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
                primarily informational, it gives Vertex AI information about the
                network connections the container uses. Listing or not a port here has
                no impact on whether the port is actually exposed, any port listening on
                the default "0.0.0.0" address inside a container will be accessible from
                the network.
            local_model (Optional[LocalModel]):
                Optional. A LocalModel instance that includes a `serving_container_spec`.
                If provided, the `serving_container_spec` of the LocalModel instance
                will overwrite the values of all other serving container parameters.
            instance_schema_uri (str):
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
            parameters_schema_uri (str):
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
            prediction_schema_uri (str):
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
            explanation_metadata (aiplatform.preview.explain.ExplanationMetadata):
                Optional. Metadata describing the Model's input and output for explanation.
                `explanation_metadata` is optional while `explanation_parameters` must be
                specified when used.
                For more details, see `Ref docs <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.preview.explain.ExplanationParameters):
                Optional. Parameters to configure explaining for Model's predictions.
                For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            display_name (str):
                Optional. The display name of the Model. The name can be up to 128
                characters long and can be consist of any UTF-8 characters.
            project: Optional[str]=None,
                Project to upload this model to. Overrides project set in
                aiplatform.init.
            location: Optional[str]=None,
                Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials: Optional[auth_credentials.Credentials]=None,
                Custom credentials to use to upload this model. Overrides credentials
                set in aiplatform.init.
            labels (Dict[str, str]):
                Optional. The labels with user-defined metadata to
                organize your Models.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                and examples of labels.
            encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this Model and all sub-resources of this Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
            staging_bucket (str):
                Optional. Bucket to stage local model artifacts. Overrides
                staging_bucket set in aiplatform.init.
            upload_request_timeout (float):
                Optional. The timeout for the upload request in seconds.

        Returns:
            model (Model):
                Instantiated representation of the uploaded model resource.

        Raises:
            ValueError: If explanation_metadata is specified while explanation_parameters
                is not.

                Also if model directory does not contain a supported model file.
                If `local_model` is specified but `serving_container_spec.image_uri`
                in the `local_model` is None.
                If `local_model` is not specified and `serving_container_image_uri`
                is None.
        """
        if not display_name:
            display_name = cls._generate_display_name()
        utils.validate_display_name(display_name)
        if labels:
            utils.validate_labels(labels)

        appended_user_agent = None
        if local_model:
            container_spec = local_model.get_serving_container_spec()
            appended_user_agent = [prediction_constants.CUSTOM_PREDICTION_ROUTINES]
        else:
            if not serving_container_image_uri:
                raise ValueError(
                    "The parameter `serving_container_image_uri` is required "
                    "if no `local_model` is provided."
                )

            env = None
            ports = None

            if serving_container_environment_variables:
                env = [
                    env_var_v1beta1.EnvVar(name=str(key), value=str(value))
                    for key, value in serving_container_environment_variables.items()
                ]
            if serving_container_ports:
                ports = [
                    model_v1beta1.Port(container_port=port)
                    for port in serving_container_ports
                ]

            container_spec = model_v1beta1.ModelContainerSpec(
                image_uri=serving_container_image_uri,
                command=serving_container_command,
                args=serving_container_args,
                env=env,
                ports=ports,
                predict_route=serving_container_predict_route,
                health_route=serving_container_health_route,
            )

        model_predict_schemata = None
        if any([instance_schema_uri, parameters_schema_uri, prediction_schema_uri]):
            model_predict_schemata = model_v1beta1.PredictSchemata(
                instance_schema_uri=instance_schema_uri,
                parameters_schema_uri=parameters_schema_uri,
                prediction_schema_uri=prediction_schema_uri,
            )

        encryption_spec = initializer.global_config.get_encryption_spec(
            encryption_spec_key_name=encryption_spec_key_name, select_version="v1beta1"
        )

        parent_model = _models.ModelRegistry._get_true_version_parent(
            location=location, project=project, parent_model=parent_model
        )

        version_aliases = _models.ModelRegistry._get_true_alias_list(
            version_aliases=version_aliases, is_default_version=is_default_version
        )

        managed_model = model_v1beta1.Model(
            display_name=display_name,
            description=description,
            version_aliases=version_aliases,
            version_description=version_description,
            container_spec=container_spec,
            predict_schemata=model_predict_schemata,
            labels=labels,
            encryption_spec=encryption_spec,
        )

        if artifact_uri and not artifact_uri.startswith("gs://"):
            model_dir = pathlib.Path(artifact_uri)
            # Validating the model directory
            if not model_dir.exists():
                raise ValueError(f"artifact_uri path does not exist: '{artifact_uri}'")
            PREBUILT_IMAGE_RE = "(us|europe|asia)-docker.pkg.dev/vertex-ai/prediction/"
            if re.match(PREBUILT_IMAGE_RE, serving_container_image_uri):
                if not model_dir.is_dir():
                    raise ValueError(
                        f"artifact_uri path must be a directory: '{artifact_uri}' when using prebuilt image '{serving_container_image_uri}'"
                    )
                if not any(
                    (model_dir / file_name).exists()
                    for file_name in _SUPPORTED_MODEL_FILE_NAMES
                ):
                    raise ValueError(
                        "artifact_uri directory does not contain any supported model files. "
                        f"When using a prebuilt serving image, the upload method only supports the following model files: '{_SUPPORTED_MODEL_FILE_NAMES}'"
                    )

            # Uploading the model
            staged_data_uri = gcs_utils.stage_local_data_in_gcs(
                data_path=str(model_dir),
                staging_gcs_dir=staging_bucket,
                project=project,
                location=location,
                credentials=credentials,
            )
            artifact_uri = staged_data_uri

        if artifact_uri:
            managed_model.artifact_uri = artifact_uri

        managed_model.explanation_spec = (
            _explanation_utils.create_and_validate_explanation_spec(
                explanation_metadata=explanation_metadata,
                explanation_parameters=explanation_parameters,
            )
        )

        request = model_service_v1beta1.UploadModelRequest(
            parent=initializer.global_config.common_location_path(project, location),
            model=managed_model,
            parent_model=parent_model,
            model_id=model_id,
        )

        api_client = cls._instantiate_client(
            location, credentials, appended_user_agent=appended_user_agent
        )

        lro = api_client.upload_model(
            request=request,
            timeout=upload_request_timeout,
        )

        _LOGGER.log_create_with_lro(cls, lro)

        model_upload_response = lro.result()

        this_model = cls(
            model_upload_response.model, version=model_upload_response.model_version_id
        )

        _LOGGER.log_create_complete(cls, this_model._gca_resource, "model")

        return this_model

    def deploy(
        self,
        endpoint: Optional[Union["Endpoint", "PrivateEndpoint"]] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        service_account: Optional[str] = None,
        explanation_metadata: Optional[explain.ExplanationMetadata] = None,
        explanation_parameters: Optional[explain.ExplanationParameters] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
        network: Optional[str] = None,
        sync=True,
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
    ) -> Union[Endpoint, PrivateEndpoint]:
        """Deploys model to endpoint. Endpoint will be created if unspecified.

        Args:
            endpoint (Union[Endpoint, PrivateEndpoint]):
                Optional. Public or private Endpoint to deploy model to. If not specified,
                endpoint display name will be model display name+'_endpoint'.
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
            accelerator_type (str):
                Optional. Hardware accelerator type. Must also set accelerator_count if used.
                One of ACCELERATOR_TYPE_UNSPECIFIED, NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
                NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int):
                Optional. The number of accelerators to attach to a worker replica.
            service_account (str):
                The service account that the DeployedModel's container runs as. Specify the
                email address of the service account. If this service account is not
                specified, the container runs as a service account that doesn't have access
                to the resource project.
                Users deploying the Model must have the `iam.serviceAccounts.actAs`
                permission on this service account.
            explanation_metadata (aiplatform.preview.explain.ExplanationMetadata):
                Optional. Metadata describing the Model's input and output for explanation.
                `explanation_metadata` is optional while `explanation_parameters` must be
                specified when used.
                For more details, see `Ref docs <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.preview.explain.ExplanationParameters):
                Optional. Parameters to configure explaining for Model's predictions.
                For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
            encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this Endpoint and all sub-resources of this Endpoint will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
            network (str):
                Optional. The full name of the Compute Engine network to which
                the Endpoint, if created, will be peered to. E.g. "projects/12345/global/networks/myVPC".
                Private services access must already be configured for the network.
                If set or aiplatform.init(network=...) has been set, a PrivateEndpoint will be created.
                If left unspecified, an Endpoint will be created. Read more about PrivateEndpoints
                [in the documentation](https://cloud.google.com/vertex-ai/docs/predictions/using-private-endpoints).
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
            deploy_request_timeout (float):
                Optional. The timeout for the deploy request in seconds.
            autoscaling_target_cpu_utilization (int):
                Optional. Target CPU Utilization to use for Autoscaling Replicas.
                A default value of 60 will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int):
                Optional. Target Accelerator Duty Cycle.
                Must also set accelerator_type and accelerator_count if specified.
                A default value of 60 will be used if not specified.

        Returns:
            endpoint (Union[Endpoint, PrivateEndpoint]):
                Endpoint with the deployed model.

        Raises:
            ValueError: If `traffic_split` is set for PrivateEndpoint.
        """
        network = network or initializer.global_config.network

        Endpoint._validate_deploy_args(
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            deployed_model_display_name=deployed_model_display_name,
            traffic_split=traffic_split,
            traffic_percentage=traffic_percentage,
        )

        if isinstance(endpoint, PrivateEndpoint):
            if traffic_split:
                raise ValueError(
                    "Traffic splitting is not yet supported for PrivateEndpoint. "
                    "Try calling deploy() without providing `traffic_split`. "
                    "A maximum of one model can be deployed to each private Endpoint."
                )

        explanation_spec = _explanation_utils.create_and_validate_explanation_spec(
            explanation_metadata=explanation_metadata,
            explanation_parameters=explanation_parameters,
        )

        return self._deploy(
            endpoint=endpoint,
            deployed_model_display_name=deployed_model_display_name,
            traffic_percentage=traffic_percentage,
            traffic_split=traffic_split,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            service_account=service_account,
            explanation_spec=explanation_spec,
            metadata=metadata,
            encryption_spec_key_name=encryption_spec_key_name
            or initializer.global_config.encryption_spec_key_name,
            network=network,
            sync=sync,
            deploy_request_timeout=deploy_request_timeout,
            autoscaling_target_cpu_utilization=autoscaling_target_cpu_utilization,
            autoscaling_target_accelerator_duty_cycle=autoscaling_target_accelerator_duty_cycle,
        )

    @base.optional_sync(return_input_arg="endpoint", bind_future_to_self=False)
    def _deploy(
        self,
        endpoint: Optional[Union["Endpoint", "PrivateEndpoint"]] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        service_account: Optional[str] = None,
        explanation_spec: Optional[explain.ExplanationSpec] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
        network: Optional[str] = None,
        sync: bool = True,
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
    ) -> Union[Endpoint, PrivateEndpoint]:
        """Deploys model to endpoint. Endpoint will be created if unspecified.

        Args:
            endpoint (Union[Endpoint, PrivateEndpoint]):
                Optional. Public or private Endpoint to deploy model to. If not specified,
                endpoint display name will be model display name+'_endpoint'.
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
            accelerator_type (str):
                Optional. Hardware accelerator type. Must also set accelerator_count if used.
                One of ACCELERATOR_TYPE_UNSPECIFIED, NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
                NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int):
                Optional. The number of accelerators to attach to a worker replica.
            service_account (str):
                The service account that the DeployedModel's container runs as. Specify the
                email address of the service account. If this service account is not
                specified, the container runs as a service account that doesn't have access
                to the resource project.
                Users deploying the Model must have the `iam.serviceAccounts.actAs`
                permission on this service account.
            explanation_spec (aiplatform.preview.explain.ExplanationSpec):
                Optional. Specification of Model explanation.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
            encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this Model and all sub-resources of this Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init
            network (str):
                Optional. The full name of the Compute Engine network to which
                the Endpoint, if created, will be peered to. E.g. "projects/12345/global/networks/myVPC".
                Private services access must already be configured for the network.
                Read more about PrivateEndpoints
                [in the documentation](https://cloud.google.com/vertex-ai/docs/predictions/using-private-endpoints).
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
            deploy_request_timeout (float):
                Optional. The timeout for the deploy request in seconds.
            autoscaling_target_cpu_utilization (int):
                Optional. Target CPU Utilization to use for Autoscaling Replicas.
                A default value of 60 will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int):
                Optional. Target Accelerator Duty Cycle.
                Must also set accelerator_type and accelerator_count if specified.
                A default value of 60 will be used if not specified.

        Returns:
            endpoint (Union[Endpoint, PrivateEndpoint]):
                Endpoint with the deployed model.
        """

        if endpoint is None:
            display_name = self.display_name[:118] + "_endpoint"

            if not network:
                endpoint = Endpoint.create(
                    display_name=display_name,
                    project=self.project,
                    location=self.location,
                    credentials=self.credentials,
                    encryption_spec_key_name=encryption_spec_key_name,
                )

        _LOGGER.log_action_start_against_resource("Deploying model to", "", endpoint)

        endpoint._deploy_call(
            endpoint.api_client,
            endpoint.resource_name,
            self,
            endpoint._gca_resource.traffic_split,
            network=network,
            deployed_model_display_name=deployed_model_display_name,
            traffic_percentage=traffic_percentage,
            traffic_split=traffic_split,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            service_account=service_account,
            explanation_spec=explanation_spec,
            metadata=metadata,
            deploy_request_timeout=deploy_request_timeout,
            autoscaling_target_cpu_utilization=autoscaling_target_cpu_utilization,
            autoscaling_target_accelerator_duty_cycle=autoscaling_target_accelerator_duty_cycle,
        )

        _LOGGER.log_action_completed_against_resource("model", "deployed", endpoint)

        endpoint._sync_gca_resource()

        return endpoint
