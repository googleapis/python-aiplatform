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

from typing import Dict, Optional, Sequence

from google.api_core import retry
from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import lro
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform_v1beta1.services.endpoint_service.client import (
    EndpointServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.model_service.client import (
    ModelServiceClient,
)
from google.cloud.aiplatform_v1beta1.types import endpoint as gca_endpoint
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types import env_var


class Model(base.AiPlatformResourceNoun):

    client_class = ModelServiceClient
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
        """Retrieves the model resource and instantiates it's representation.

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
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
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

        # Fully qualified model name, i.e. "projects/.../locations/.../models/12345"
        valid_name = utils.extract_fields_from_resource_name(
            resource_name=model_name, resource_noun="models"
        )

        # Partial model name (i.e. "12345") with known project and location
        if (
            not valid_name
            and utils.validate_id(model_name)
            and (self.project or initializer.global_config.project)
            and (self.location or initializer.global_config.location)
        ):
            model_name = ModelServiceClient.model_path(
                project=self.project or initializer.global_config.project,
                location=self.location or initializer.global_config.location,
                model=model_name,
            )

        # Invalid model_name parameter
        elif not valid_name:
            raise ValueError("Please provide a valid model name or ID")

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

    def deploy(
        self,
        endpoint: Optional["Endpoint"] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 100,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 0,
        max_replica_count: Optional[int] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        timeout: Optional[int] = None,
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
                100. Traffic of previously deployed models at the endpoint  will
                be scaled down to accommodate new deployed model's traffic.
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
            timeout (int):
                Optional. How long (in seconds) to wait for the endpoint creation
                operation to complete. If None, wait indefinitely.
        Returns:
            endpoint ("Endpoint"):
                Endpoint with the deployed model.

        """
        if endpoint is None:
            display_name = self.display_name + "_endpoint"
            endpoint = Endpoint.create(display_name=display_name)

            # TODO(b/171631203) queue deploy instead of block
            @retry.Retry(deadline=timeout)
            def endpoint_exist():
                if endpoint._gca_resource is None:
                    raise Exception("Endpoint not yet created.")

            endpoint_exist()

        endpoint.deploy(
            self,
            deployed_model_display_name=deployed_model_display_name,
            traffic_percentage=traffic_percentage,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            metadata=metadata,
        )

        return endpoint


class Endpoint(base.AiPlatformResourceNoun):

    client_class = EndpointServiceClient
    _is_client_prediction_client = False

    def __init__(
        self,
        endpoint_name: Optional[str] = None,
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
        if endpoint_name:
            self._gca_resource = _get_endpoint(endpoint_name)

    def _get_endpoint(self, endpoint_name: str) -> gca_endpoint.Endpoint:
        """Gets the endpoint from AI Platform.

        Args:
            endpoint_name (str):
                Required. The name of the endpoint to retrieve.
        Returns:
            endpoint (gca_endpoint.Endpoint):
                Managed endpoint resource.
        """

        # Fully qualified endpoint name, i.e. "projects/.../locations/.../endpoints/12345"
        valid_name = utils.extract_fields_from_resource_name(
            resource_name=endpoint_name, resource_noun="endpoints"
        )

        # Partial endpoint name (i.e. "12345") with known project and location
        if (
            not valid_name
            and utils.validate_id(endpoint_name)
            and (self.project or initializer.global_config.project)
            and (self.location or initializer.global_config.location)
        ):
            endpoint_name = EndpointServiceClient.endpoint_path(
                project=self.project or initializer.global_config.project,
                location=self.location or initializer.global_config.location,
                endpoint=endpoint_name,
            )

        # Invalid model_name parameter
        elif not valid_name:
            raise ValueError("Please provide a valid model name or ID")

        endpoint = self.endpoint_client.get_endpoint(name=endpoint_name)
        return endpoint

    @classmethod
    def create(
        cls,
        display_name: str,
        description: Optional[str] = None,
        traffic_split: Optional[Dict] = None,
        labels: Optional[Dict] = None,
        metadata: Sequence[Tuple[str, str]] = (),
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
            traffic_split (Dict):
                Optional. A map from a DeployedModel's ID to the
                percentage of this Endpoint's traffic that
                should be forwarded to that DeployedModel.
                If a DeployedModel's ID is not listed in this
                map, then it receives no traffic.

                The traffic percentage values must add up to
                100, or map must be empty if the Endpoint is to
                not accept any traffic at a moment.
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

        endpoint_client = cls._instantiate_client(
            location=location, credentials=credentials
        )

        client_class = PredictionServiceClient
        _is_client_prediction_client = True
        prediction_client = cls._instantiate_client(
            location=location, credentials=credentials
        )

        create_endpoint_operation = cls._create(
            endpoint_client=endpoint_client,
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            display_name=display_name,
            description=description,
            traffic_split=traffic_split,
            labels=labels,
            metadata=metadata,
        )

        created_endpoint = None
        endpoint = cls(
            endpoint=created_endpoint,
            project=project,
            location=location,
            credentials=credentials,
        )

        create_endpoint_operation.add_update_resource_callback(
            resource_noun_obj=endpoint,
            result_key="name",
            api_get=lambda name: endpoint_client.get_endpoint(name=name),
        )

        return endpoint

    @classmethod
    def _create(
        cls,
        endpoint_client: EndpointServiceClient,
        parent: str,
        display_name: str,
        description: Optional[str] = None,
        traffic_split: Optional[Dict] = None,
        labels: Optional[Dict] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> lro.LRO:
        """
        Creates a new endpoint by calling the API client.

        Args:
            endpoint_client (EndpointServiceClient):
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
            traffic_split (Dict):
                Optional. A map from a DeployedModel's ID to the
                percentage of this Endpoint's traffic that
                should be forwarded to that DeployedModel.
                If a DeployedModel's ID is not listed in this
                map, then it receives no traffic.

                The traffic percentage values must add up to
                100, or map must be empty if the Endpoint is to
                not accept any traffic at a moment.
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
            display_name=display_name,
            description=description,
            traffic_split=traffic_split,
            labels=labels,
        )

        operation_future = endpoint_client.create_endpoint(
            parent=parent, endpoint=gapic_endpoint, metadata=metadata
        )

        return lro.LRO(operation_future)

    def _allocate_traffic(
        traffic_split: Sequence[gca_endpoint.Endpoint.TrafficSplitEntry],
        traffic_percentage: int,
    ) -> Dict:
        """
        Allocates desired traffic to new deployed model and scales traffic of
        older deployed models.

        Args:
            traffic_split (Sequence[gca_endpoint.Endpoint.TrafficSplitEntry]):
                Required. Current traffic split of deployed models in endpoint.
            traffic_percentage (int):
                Required. Desired traffic to new deployed model.
        Returns:
            traffic_split (Dict):
                Traffic split to use.
        """
        old_models_traffic = 100 - traffic_percentage
        if old_models_traffic:
            unallocated_traffic = old_models_traffic
            for deployed_model in traffic_split:
                current_traffic = traffic_split[deployed_model]
                new_traffic = int(current_traffic / 100 * old_models_traffic)
                traffic_split[deployed_model] = new_traffic
                unallocated_traffic -= new_traffic
            # will likely under-allocate. make total 100.
            traffic_split[deployed_model] += unallocated_traffic

        traffic_split["0"] = traffic_percentage

        return traffic_split

    def _unallocate_traffic(
        traffic_split: Sequence[gca_endpoint.Endpoint.TrafficSplitEntry],
        deployed_model_id: str,
    ) -> Dict:
        """
        Sets deployed model id's traffic to 0 and scales the traffic of other
        deployed models.

        Args:
            traffic_split (Sequence[gca_endpoint.Endpoint.TrafficSplitEntry]):
                Required. Current traffic split of deployed models in endpoint.
            deployed_model_id (str):
                Required. Desired traffic to new deployed model.
        Returns:
            traffic_split (Dict):
                Traffic split to use.
        """
        deployed_model_id_traffic = traffic_split[deployed_model_id]
        del traffic_split[deployed_model_id]
        traffic_percent_left = 100 - deployed_model_id_traffic

        if traffic_percent_left:
            unallocated_traffic = traffic_percent_left
            for deployed_model in traffic_split:
                current_traffic = traffic_split[deployed_model]
                new_traffic = int(current_traffic / traffic_percent_left * 100)
                traffic_split[deployed_model] = new_traffic
                unallocated_traffic -= new_traffic
            # will likely under-allocate. make total 100.
            traffic_split[deployed_model] += unallocated_traffic

        traffic_split[deployed_model_id] = 0

        return traffic_split

    def deploy(
        self,
        *,
        model: "Model",
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 100,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 0,
        max_replica_count: Optional[int] = None,
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
                100. Traffic of previously deployed models at the endpoint  will
                be scaled down to accommodate new deployed model's traffic.
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
            lro (lro.LRO):
                LRO of model deployment.
        """
        max_replica_count = min(1, min_replica_count)
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

        traffic_split = self._allocate_traffic(
            traffic_split=self._gca_resource.traffic_split,
            traffic_percentage=traffic_percentage,
        )

        operation_future = self.endpoint_client.deploy_model(
            endpoint=self.resource_name,
            deployed_model=deployed_model,
            traffic_split=traffic_split,
            metadata=metadata,
        )

        return lro.LRO(operation_future)

    def undeploy(
        self,
        deployed_model_id: str,
        traffic_split: Optional[Dict] = None,
    ) -> lro.LRO:
        """Undeploys a deployed model.

        Proportionally adjusts the traffic_split among the remaining deployed
        models of the endpoint.

        Args:
            deployed_model_id (str):
                Required. The ID of the DeployedModel to be undeployed from the
                Endpoint.
            traffic_split (Sequence[gca_endpoint.Endpoint.TrafficSplitEntry]`):
                Optional. If this field is provided, then the Endpoint's traffic_split
                will be overwritten with it. If last DeployedModel is being
                undeployed from the Endpoint, the [Endpoint.traffic_split] will
                always end up empty when this operation completes. A DeployedModel
                will be successfully undeployed only if it doesn't have any traffic
                assigned to it. If this field is not provided, the traffic of the
                remaining deployed models will be scaled to fill 100 percent.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
        Returns:
            lro (lro.LRO):
                LRO of model undeployment.
        """
        if traffic_split is None:
            traffic_split = self._unallocate_traffic(
                traffic_split=self._gca_resource.traffic_split,
                deployed_model_id=deployed_model_id,
            )

        operation_future = self.endpoint_client.undeploy_model(
            endpoint=self.resource_name,
            deployed_model_id=deployed_model_id,
            traffic_split=traffic_split,
            metadata=metadata,
        )

        return lro.LRO(operation_future)

    def predict(self, instances: List[Dict], parameters: Optional[Dict]) -> List[Dict]:
        """Online prediction."""
        raise NotImplementedError("Prediction not implemented.")

    def explain(self, instances: List[Dict], parameters: Optional[Dict]) -> List[Dict]:
        """Online prediction with explanation."""
        raise NotImplementedError("Prediction not implemented.")
