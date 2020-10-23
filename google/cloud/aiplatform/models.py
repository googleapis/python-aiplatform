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

    # TODO(b/169782716) add support for deployment when Endpoint class complete
    def deploy(self):
        raise NotImplementedError("Deployment not implemented.")


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
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(project=project, location=location, credentials=credentials)
        if endpoint_name:
            self._gca_resource = _get_endpoint(endpoint_name)

    def _get_endpoint(self, endpoint_name: str) -> gca_endpoint.Endpoint:
        """Gets the endpoint from AI Platform.

        Args:
            endpoint_name (str): The name of the endpoint to retrieve.
        Returns:
            endpoint (gca_endpoint.Endpoint): Managed endpoint resource.
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

        endpoint = self.api_client.get_endpoint(name=endpoint_name)
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
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
        Returns:
            endpoint (Endpoint):
                Instantiated representation of the endpoint resource.
        """

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        operation_future = cls._create(
            api_client=api_client,
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            display_name=display_name,
            description=description,
            traffic_split=traffic_split,
            labels=labels,
            request_metadata=metadata,
        )

        created_endpoint = None
        endpoint_obj = cls(
            endpoint=created_endpoint,
            project=project,
            location=location,
            credentials=credentials,
        )

        create_endpoint_operation = lro.LRO(operation_future)
        create_endpoint_operation.add_update_resource_callback(
            resource_noun_obj=endpoint_obj,
            result_key="name",
            api_get=lambda name: api_client.get_endpoint(name=name),
        )

        return endpoint_obj

    @classmethod
    def _create(
        cls,
        api_client: EndpointServiceClient,
        parent: str,
        display_name: str,
        description: Optional[str] = None,
        traffic_split: Optional[Dict] = {},
        labels: Optional[Dict] = {},
        request_metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation.Operation:
        """
        Creates a new endpoint by calling the API client.

        Args:
            api_client (EndpointServiceClient):
                An instance of EndpointServiceClient with the correct api_endpoint
                already set based on user's preferences.
            parent (str):
                Also known as common location path, that usually contains the
                project and location that the user provided to the upstream method.
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
            request_metadata: Sequence[Tuple[str, str]] = ()
                Strings which should be sent along with the request as metadata.
            Returns:
                operation (Operation):
                    An object representing a long-running operation.
        """
        gapic_endpoint = gca_endpoint.Endpoint(
            display_name=display_name,
            description=description,
            traffic_split=traffic_split,
            labels=labels,
        )

        return api_client.create_endpoint(
            parent=parent, endpoint=gapic_endpoint, metadata=request_metadata
        )

    def deploy(
        self,
        *,
        model_name: Optional[str] = None,
        model: Optional[aiplatform.Model] = None,
        traffic_percentage: int = 0,
        min_replica_count: int = 0,
        max_replica_count: int = 1,
        machine_type: str = "n1-standard-2",
    ) -> aiplatform.Endpoint:
        """Deploys a Model to the Endpoint."""

    def undeploy(
        self, deployed_model_id: str, traffic_split: Optional[Dict] = None
    ) -> aiplatform.Endpoint:
        """Undeploys a deployed model.

        Proportionally adjusts the traffic_split among the remaining deployed
        models of the endpoint.
        """

    def predict(self, instances: List[Dict], parameters: Optional[Dict]) -> List[Dict]:
        """Online prediction."""

    def explain(self, instances: List[Dict], parameters: Optional[Dict]) -> List[Dict]:
        """Online prediction with explanation."""
