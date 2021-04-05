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
import proto
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple, Union

from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import jobs

from google.cloud.aiplatform_v1beta1.services.endpoint_service import (
    client as endpoint_service_client,
)
from google.cloud.aiplatform_v1beta1.services.model_service import (
    client as model_service_client,
)
from google.cloud.aiplatform_v1beta1.services.prediction_service import (
    client as prediction_service_client,
)

from google.cloud.aiplatform_v1beta1.types import encryption_spec as gca_encryption_spec
from google.cloud.aiplatform_v1beta1.types import endpoint as gca_endpoint
from google.cloud.aiplatform_v1beta1.types import explanation as gca_explanation
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types import env_var

from google.protobuf import json_format


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
        explanations:
            The explanations of the Model's predictions. It has the same number
            of elements as instances to be explained. Default is None.
    """

    predictions: Dict[str, List]
    deployed_model_id: str
    explanations: Optional[Sequence[gca_explanation.Explanation]] = None


class Endpoint(base.AiPlatformResourceNounWithFutureManager):

    client_class = endpoint_service_client.EndpointServiceClient
    _is_client_prediction_client = False
    _resource_noun = "endpoints"
    _getter_method = "get_endpoint"
    _delete_method = "delete_endpoint"

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
        self._gca_resource = self._get_gca_resource(resource_name=endpoint_name)
        self._prediction_client = self._instantiate_prediction_client(
            location=location or initializer.global_config.location,
            credentials=credentials,
        )

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
        encryption_spec_key_name: Optional[str] = None,
        sync=True,
    ) -> "Endpoint":
        """Creates a new endpoint.

        Args:
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
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
            encryption_spec_key_name (Optional[str]):
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
        Returns:
            endpoint (endpoint.Endpoint):
                Created endpoint.
        """

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        utils.validate_display_name(display_name)

        project = project or initializer.global_config.project
        location = location or initializer.global_config.location

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
        )

    @classmethod
    @base.optional_sync()
    def _create(
        cls,
        api_client: endpoint_service_client.EndpointServiceClient,
        display_name: str,
        project: str,
        location: str,
        description: Optional[str] = None,
        labels: Optional[Dict] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec: Optional[gca_encryption_spec.EncryptionSpec] = None,
        sync=True,
    ) -> "Endpoint":
        """
        Creates a new endpoint by calling the API client.
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
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
            encryption_spec (Optional[gca_encryption_spec.EncryptionSpec]):
                Optional. The Cloud KMS customer managed encryption key used to protect the dataset.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this Dataset and all sub-resources of this Dataset will be secured by this key.
            sync (bool):
                Whether to create this endpoint synchronously.
        Returns:
            endpoint (endpoint.Endpoint):
                Created endpoint.
        """

        parent = initializer.global_config.common_location_path(
            project=project, location=location
        )

        gapic_endpoint = gca_endpoint.Endpoint(
            display_name=display_name,
            description=description,
            labels=labels,
            encryption_spec=encryption_spec,
        )

        operation_future = api_client.create_endpoint(
            parent=parent, endpoint=gapic_endpoint, metadata=metadata
        )

        created_endpoint = operation_future.result()

        return cls(
            endpoint_name=created_endpoint.name,
            project=project,
            location=location,
            credentials=credentials,
        )

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

    @staticmethod
    def _validate_deploy_args(
        min_replica_count: int,
        max_replica_count: int,
        accelerator_type: Optional[str],
        deployed_model_display_name: Optional[str],
        traffic_split: Optional[Dict[str, int]],
        traffic_percentage: int,
    ):
        """Helper method to validate deploy arguments.

        Args:
            min_replica_count (int):
                Required. The minimum number of machine replicas this deployed
                model will be always deployed on. If traffic against it increases,
                it may dynamically be deployed onto more replicas, and as traffic
                decreases, some of these extra replicas may be freed.
            max_replica_count (int):
                Required. The maximum number of replicas this deployed model may
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
                Required. Hardware accelerator type. One of ACCELERATOR_TYPE_UNSPECIFIED,
                NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100, NVIDIA_TESLA_P4,
                NVIDIA_TESLA_T4, TPU_V2, TPU_V3
            deployed_model_display_name (str):
                Required. The display name of the DeployedModel. If not provided
                upon creation, the Model's display_name is used.
            traffic_split (Dict[str, int]):
                Required. A map from a DeployedModel's ID to the percentage of
                this Endpoint's traffic that should be forwarded to that DeployedModel.
                If a DeployedModel's ID is not listed in this map, then it receives
                no traffic. The traffic percentage values must add up to 100, or
                map must be empty if the Endpoint is to not accept any traffic at
                the moment. Key for model being deployed is "0". Should not be
                provided if traffic_percentage is provided.
            traffic_percentage (int):
                Required. Desired traffic to newly deployed model. Defaults to
                0 if there are pre-existing deployed models. Defaults to 100 if
                there are no pre-existing deployed models. Negative values should
                not be provided. Traffic of previously deployed models at the endpoint
                will be scaled down to accommodate new deployed model's traffic.
                Should not be provided if traffic_split is provided.

        Raises:
            ValueError if Min or Max replica is negative. Traffic percentage > 100 or
            < 0. Or if traffic_split does not sum to 100.

        """
        if min_replica_count < 0:
            raise ValueError("Min replica cannot be negative.")
        if max_replica_count < 0:
            raise ValueError("Max replica cannot be negative.")
        if deployed_model_display_name is not None:
            utils.validate_display_name(deployed_model_display_name)

        if traffic_split is None:
            if traffic_percentage > 100:
                raise ValueError("Traffic percentage cannot be greater than 100.")
            if traffic_percentage < 0:
                raise ValueError("Traffic percentage cannot be negative.")

        elif traffic_split:
            # TODO(b/172678233) verify every referenced deployed model exists
            if sum(traffic_split.values()) != 100:
                raise ValueError(
                    "Sum of all traffic within traffic split needs to be 100."
                )

        # Raises ValueError if invalid accelerator
        if accelerator_type:
            utils.validate_accelerator_type(accelerator_type)

    def deploy(
        self,
        model: "Model",
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: int = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        explanation_metadata: Optional["aiplatform.explain.ExplanationMetadata"] = None,
        explanation_parameters: Optional[
            "aiplatform.explain.ExplanationParameters"
        ] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync=True,
    ) -> None:
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
            accelerator_type (str):
                Optional. Hardware accelerator type. Must also set accelerator_count if used.
                One of ACCELERATOR_TYPE_UNSPECIFIED, NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
                NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4, TPU_V2, TPU_V3
            accelerator_count (int):
                Optional. The number of accelerators to attach to a worker replica.
            explanation_metadata (aiplatform.explain.ExplanationMetadata):
                Optional. Metadata describing the Model's input and output for explanation.
                Both `explanation_metadata` and `explanation_parameters` must be
                passed together when used. For more details, see
                `Ref docs <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.explain.ExplanationParameters):
                Optional. Parameters to configure explaining for Model's predictions.
                For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        """

        self._validate_deploy_args(
            min_replica_count,
            max_replica_count,
            accelerator_type,
            deployed_model_display_name,
            traffic_split,
            traffic_percentage,
        )

        self._deploy(
            model=model,
            deployed_model_display_name=deployed_model_display_name,
            traffic_percentage=traffic_percentage,
            traffic_split=traffic_split,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            explanation_metadata=explanation_metadata,
            explanation_parameters=explanation_parameters,
            metadata=metadata,
            sync=sync,
        )

    @base.optional_sync()
    def _deploy(
        self,
        model: "Model",
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 1,
        max_replica_count: Optional[int] = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        explanation_metadata: Optional["aiplatform.explain.ExplanationMetadata"] = None,
        explanation_parameters: Optional[
            "aiplatform.explain.ExplanationParameters"
        ] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync=True,
    ) -> None:
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
            accelerator_type (str):
                Optional. Hardware accelerator type. Must also set accelerator_count if used.
                One of ACCELERATOR_TYPE_UNSPECIFIED, NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
                NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4, TPU_V2, TPU_V3
            accelerator_count (int):
                Optional. The number of accelerators to attach to a worker replica.
            explanation_metadata (aiplatform.explain.ExplanationMetadata):
                Optional. Metadata describing the Model's input and output for explanation.
                Both `explanation_metadata` and `explanation_parameters` must be
                passed together when used. For more details, see
                `Ref docs <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.explain.ExplanationParameters):
                Optional. Parameters to configure explaining for Model's predictions.
                For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Raises:
            ValueError if there is not current traffic split and traffic percentage
            is not 0 or 100.
        """

        self._deploy_call(
            self.api_client,
            self.resource_name,
            model.resource_name,
            self._gca_resource.traffic_split,
            deployed_model_display_name=deployed_model_display_name,
            traffic_percentage=traffic_percentage,
            traffic_split=traffic_split,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            explanation_metadata=explanation_metadata,
            explanation_parameters=explanation_parameters,
            metadata=metadata,
        )

        self._sync_gca_resource()

    @classmethod
    def _deploy_call(
        cls,
        api_client: endpoint_service_client.EndpointServiceClient,
        endpoint_resource_name: str,
        model_resource_name: str,
        endpoint_resource_traffic_split: Optional[proto.MapField] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 1,
        max_replica_count: Optional[int] = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        explanation_metadata: Optional["aiplatform.explain.ExplanationMetadata"] = None,
        explanation_parameters: Optional[
            "aiplatform.explain.ExplanationParameters"
        ] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ):
        """Helper method to deploy model to endpoint.

        Args:
            api_client (endpoint_service_client.EndpointServiceClient):
                Required. endpoint_service_client.EndpointServiceClient to make call.
            endpoint_resource_name (str):
                Required. Endpoint resource name to deploy model to.
            model_resource_name (str):
                Required. Model resource name of Model to deploy.
            endpoint_resource_traffic_split (proto.MapField):
                Optional. Endpoint current resource traffic split.
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
            explanation_metadata (aiplatform.explain.ExplanationMetadata):
                Optional. Metadata describing the Model's input and output for explanation.
                Both `explanation_metadata` and `explanation_parameters` must be
                passed together when used. For more details, see
                `Ref docs <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.explain.ExplanationParameters):
                Optional. Parameters to configure explaining for Model's predictions.
                For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Raises:
            ValueError if there is not current traffic split and traffic percentage
                is not 0 or 100.
            ValueError if only `explanation_metadata` or `explanation_parameters`
                is specified.
        """

        max_replica_count = max(min_replica_count, max_replica_count)

        if bool(accelerator_type) != bool(accelerator_count):
            raise ValueError(
                "Both `accelerator_type` and `accelerator_count` should be specified or None."
            )
        if bool(explanation_metadata) != bool(explanation_parameters):
            raise ValueError(
                "Both `explanation_metadata` and `explanation_parameters` should be specified or None."
            )

        if machine_type:
            machine_spec = machine_resources.MachineSpec(machine_type=machine_type)

            if accelerator_type and accelerator_count:
                utils.validate_accelerator_type(accelerator_type)
                machine_spec.accelerator_type = accelerator_type
                machine_spec.accelerator_count = accelerator_count

            dedicated_resources = machine_resources.DedicatedResources(
                machine_spec=machine_spec,
                min_replica_count=min_replica_count,
                max_replica_count=max_replica_count,
            )
            deployed_model = gca_endpoint.DeployedModel(
                dedicated_resources=dedicated_resources,
                model=model_resource_name,
                display_name=deployed_model_display_name,
            )
        else:
            automatic_resources = machine_resources.AutomaticResources(
                min_replica_count=min_replica_count,
                max_replica_count=max_replica_count,
            )
            deployed_model = gca_endpoint.DeployedModel(
                automatic_resources=automatic_resources,
                model=model_resource_name,
                display_name=deployed_model_display_name,
            )

        # Service will throw error if both metadata and parameters are not provided
        if explanation_metadata and explanation_parameters:
            explanation_spec = gca_endpoint.explanation.ExplanationSpec()
            explanation_spec.metadata = explanation_metadata
            explanation_spec.parameters = explanation_parameters
            deployed_model.explanation_spec = explanation_spec

        if traffic_split is None:
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
        )

        operation_future.result()

    def undeploy(
        self,
        deployed_model_id: str,
        traffic_split: Optional[Dict[str, int]] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync=True,
    ) -> None:
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
        if traffic_split is not None:
            if deployed_model_id in traffic_split and traffic_split[deployed_model_id]:
                raise ValueError("Model being undeployed should have 0 traffic.")
            if sum(traffic_split.values()) != 100:
                # TODO(b/172678233) verify every referenced deployed model exists
                raise ValueError(
                    "Sum of all traffic within traffic split needs to be 100."
                )

        self._undeploy(
            deployed_model_id=deployed_model_id,
            traffic_split=traffic_split,
            metadata=metadata,
            sync=sync,
        )

    @base.optional_sync()
    def _undeploy(
        self,
        deployed_model_id: str,
        traffic_split: Optional[Dict[str, int]] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync=True,
    ) -> None:
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
        current_traffic_split = traffic_split or dict(self._gca_resource.traffic_split)

        if deployed_model_id in current_traffic_split:
            current_traffic_split = self._unallocate_traffic(
                traffic_split=current_traffic_split,
                deployed_model_id=deployed_model_id,
            )
            current_traffic_split.pop(deployed_model_id)

        operation_future = self.api_client.undeploy_model(
            endpoint=self.resource_name,
            deployed_model_id=deployed_model_id,
            traffic_split=current_traffic_split,
            metadata=metadata,
        )

        # block before returning
        operation_future.result()

        # update local resource
        self._sync_gca_resource()

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
        Returns:
            prediction: Prediction with returned predictions and Model Id.

        """
        self.wait()

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

    def explain(
        self,
        instances: List[Dict],
        parameters: Optional[Dict] = None,
        deployed_model_id: Optional[str] = None,
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
        Returns:
            prediction: Prediction with returned predictions, explanations and Model Id.
        """
        self.wait()

        explain_response = self._prediction_client.explain(
            endpoint=self.resource_name,
            instances=instances,
            parameters=parameters,
            deployed_model_id=deployed_model_id,
        )

        return Prediction(
            predictions=[
                json_format.MessageToDict(item)
                for item in explain_response.predictions.pb
            ],
            deployed_model_id=explain_response.deployed_model_id,
            explanations=explain_response.explanations,
        )

    def list_models(self) -> Sequence[gca_endpoint.DeployedModel]:
        """Returns a list of the models deployed to this Endpoint.

        Returns:
            deployed_models (Sequence[aiplatform.gapic.DeployedModel]):
                A list of the models deployed in this Endpoint.
        """
        self._sync_gca_resource()
        return self._gca_resource.deployed_models

    def undeploy_all(self, sync: bool = True) -> "Endpoint":
        """Undeploys every model deployed to this Endpoint.

        Args:
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        """
        self._sync_gca_resource()

        for deployed_model in self._gca_resource.deployed_models:
            self._undeploy(deployed_model_id=deployed_model.id, sync=sync)

        return self

    def delete(self, force: bool = False, sync: bool = True) -> None:
        """Deletes this AI Platform Endpoint resource. If force is set to True,
        all models on this Endpoint will be undeployed prior to deletion.

        Args:
            force (bool):
                Required. If force is set to True, all deployed models on this
                Endpoint will be undeployed first. Default is False.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Raises:
            FailedPrecondition: If models are deployed on this Endpoint and force = False.
        """
        if force:
            self.undeploy_all(sync=sync)

        super().delete(sync=sync)


class Model(base.AiPlatformResourceNounWithFutureManager):

    client_class = model_service_client.ModelServiceClient
    _is_client_prediction_client = False
    _resource_noun = "models"
    _getter_method = "get_model"
    _delete_method = "delete_model"

    @property
    def uri(self):
        """Uri of the model."""
        return self._gca_resource.artifact_uri

    @property
    def description(self):
        """Description of the model."""
        return self._gca_resource.description

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
        self._gca_resource = self._get_gca_resource(resource_name=model_name)

    # TODO(b/170979552) Add support for predict schemata
    # TODO(b/170979926) Add support for metadata and metadata schema
    @classmethod
    @base.optional_sync()
    def upload(
        cls,
        display_name: str,
        artifact_uri: str,
        serving_container_image_uri: str,
        *,
        serving_container_predict_route: Optional[str] = None,
        serving_container_health_route: Optional[str] = None,
        description: Optional[str] = None,
        serving_container_command: Optional[Sequence[str]] = None,
        serving_container_args: Optional[Sequence[str]] = None,
        serving_container_environment_variables: Optional[Dict[str, str]] = None,
        serving_container_ports: Optional[Sequence[int]] = None,
        instance_schema_uri: Optional[str] = None,
        parameters_schema_uri: Optional[str] = None,
        prediction_schema_uri: Optional[str] = None,
        explanation_metadata: Optional["aiplatform.explain.ExplanationMetadata"] = None,
        explanation_parameters: Optional[
            "aiplatform.explain.ExplanationParameters"
        ] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec_key_name: Optional[str] = None,
        sync=True,
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
                Optional. An HTTP path to send prediction requests to the container, and
                which must be supported by it. If not specified a default HTTP path will
                be used by AI Platform.
            serving_container_health_route (str):
                Optional. An HTTP path to send health check requests to the container, and which
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
            explanation_metadata (aiplatform.explain.ExplanationMetadata):
                Optional. Metadata describing the Model's input and output for explanation.
                Both `explanation_metadata` and `explanation_parameters` must be
                passed together when used. For more details, see
                `Ref docs <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.explain.ExplanationParameters):
                Optional. Parameters to configure explaining for Model's predictions.
                For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            project: Optional[str]=None,
                Project to upload this model to. Overrides project set in
                aiplatform.init.
            location: Optional[str]=None,
                Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials: Optional[auth_credentials.Credentials]=None,
                Custom credentials to use to upload this model. Overrides credentials
                set in aiplatform.init.
            encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this Model and all sub-resources of this Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
        Returns:
            model: Instantiated representation of the uploaded model resource.
        Raises:
            ValueError if only `explanation_metadata` or `explanation_parameters`
                is specified.
        """
        utils.validate_display_name(display_name)

        if bool(explanation_metadata) != bool(explanation_parameters):
            raise ValueError(
                "Both `explanation_metadata` and `explanation_parameters` should be specified or None."
            )

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

        model_predict_schemata = None
        if any([instance_schema_uri, parameters_schema_uri, prediction_schema_uri]):
            model_predict_schemata = gca_model.PredictSchemata(
                instance_schema_uri=instance_schema_uri,
                parameters_schema_uri=parameters_schema_uri,
                prediction_schema_uri=prediction_schema_uri,
            )

        # TODO(b/182388545) initializer.global_config.get_encryption_spec from a sync function
        encryption_spec = initializer.global_config.get_encryption_spec(
            encryption_spec_key_name=encryption_spec_key_name
        )

        managed_model = gca_model.Model(
            display_name=display_name,
            description=description,
            artifact_uri=artifact_uri,
            container_spec=container_spec,
            predict_schemata=model_predict_schemata,
            encryption_spec=encryption_spec,
        )

        # Override explanation_spec if both required fields are provided
        if explanation_metadata and explanation_parameters:
            explanation_spec = gca_endpoint.explanation.ExplanationSpec()
            explanation_spec.metadata = explanation_metadata
            explanation_spec.parameters = explanation_parameters
            managed_model.explanation_spec = explanation_spec

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
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        explanation_metadata: Optional["aiplatform.explain.ExplanationMetadata"] = None,
        explanation_parameters: Optional[
            "aiplatform.explain.ExplanationParameters"
        ] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
        sync=True,
    ) -> Endpoint:
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
            accelerator_type (str):
                Optional. Hardware accelerator type. Must also set accelerator_count if used.
                One of ACCELERATOR_TYPE_UNSPECIFIED, NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
                NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4, TPU_V2, TPU_V3
            accelerator_count (int):
                Optional. The number of accelerators to attach to a worker replica.
            explanation_metadata (aiplatform.explain.ExplanationMetadata):
                Optional. Metadata describing the Model's input and output for explanation.
                Both `explanation_metadata` and `explanation_parameters` must be
                passed together when used. For more details, see
                `Ref docs <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.explain.ExplanationParameters):
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

                If set, this Model and all sub-resources of this Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Returns:
            endpoint ("Endpoint"):
                Endpoint with the deployed model.

        """

        Endpoint._validate_deploy_args(
            min_replica_count,
            max_replica_count,
            accelerator_type,
            deployed_model_display_name,
            traffic_split,
            traffic_percentage,
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
            explanation_metadata=explanation_metadata,
            explanation_parameters=explanation_parameters,
            metadata=metadata,
            encryption_spec_key_name=encryption_spec_key_name
            or initializer.global_config.encryption_spec_key_name,
            sync=sync,
        )

    @base.optional_sync(return_input_arg="endpoint", bind_future_to_self=False)
    def _deploy(
        self,
        endpoint: Optional["Endpoint"] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 1,
        max_replica_count: Optional[int] = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        explanation_metadata: Optional["aiplatform.explain.ExplanationMetadata"] = None,
        explanation_parameters: Optional[
            "aiplatform.explain.ExplanationParameters"
        ] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
        sync: bool = True,
    ) -> Endpoint:
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
            accelerator_type (str):
                Optional. Hardware accelerator type. Must also set accelerator_count if used.
                One of ACCELERATOR_TYPE_UNSPECIFIED, NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
                NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4, TPU_V2, TPU_V3
            accelerator_count (int):
                Optional. The number of accelerators to attach to a worker replica.
            explanation_metadata (aiplatform.explain.ExplanationMetadata):
                Optional. Metadata describing the Model's input and output for explanation.
                Both `explanation_metadata` and `explanation_parameters` must be
                passed together when used. For more details, see
                `Ref docs <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.explain.ExplanationParameters):
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

                If set, this Model and all sub-resources of this Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Returns:
            endpoint ("Endpoint"):
                Endpoint with the deployed model.
        """

        if endpoint is None:
            display_name = self.display_name[:118] + "_endpoint"
            endpoint = Endpoint.create(
                display_name=display_name,
                project=self.project,
                location=self.location,
                credentials=self.credentials,
                encryption_spec_key_name=encryption_spec_key_name,
            )

        Endpoint._deploy_call(
            endpoint.api_client,
            endpoint.resource_name,
            self.resource_name,
            endpoint._gca_resource.traffic_split,
            deployed_model_display_name=deployed_model_display_name,
            traffic_percentage=traffic_percentage,
            traffic_split=traffic_split,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            explanation_metadata=explanation_metadata,
            explanation_parameters=explanation_parameters,
            metadata=metadata,
        )

        endpoint._sync_gca_resource()

        return endpoint

    def batch_predict(
        self,
        job_display_name: str,
        gcs_source: Optional[Union[str, Sequence[str]]] = None,
        bigquery_source: Optional[str] = None,
        instances_format: str = "jsonl",
        gcs_destination_prefix: Optional[str] = None,
        bigquery_destination_prefix: Optional[str] = None,
        predictions_format: str = "jsonl",
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
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec_key_name: Optional[str] = None,
        sync: bool = True,
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
            instances_format: str = "jsonl"
                Required. The format in which instances are given, must be one
                of "jsonl", "csv", "bigquery", "tf-record", "tf-record-gzip",
                or "file-list". Default is "jsonl" when using `gcs_source`. If a
                `bigquery_source` is provided, this is overriden to "bigquery".
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
            predictions_format: str = "jsonl"
                Required. The format in which AI Platform gives the
                predictions, must be one of "jsonl", "csv", or "bigquery".
                Default is "jsonl" when using `gcs_destination_prefix`. If a
                `bigquery_destination_prefix` is provided, this is overriden to
                "bigquery".
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
            labels: Optional[dict] = None
                Optional. The labels with user-defined metadata to organize your
                BatchPredictionJobs. Label keys and values can be no longer than
                64 characters (Unicode codepoints), can only contain lowercase
                letters, numeric characters, underscores and dashes.
                International characters are allowed. See https://goo.gl/xmQnxf
                for more information and examples of labels.
            credentials: Optional[auth_credentials.Credentials] = None
                Optional. Custom credentials to use to create this batch prediction
                job. Overrides credentials set in aiplatform.init.
            encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the model. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this Model and all sub-resources of this Model will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
        Returns:
            (jobs.BatchPredictionJob):
                Instantiated representation of the created batch prediction job.

        """
        self.wait()

        return jobs.BatchPredictionJob.create(
            job_display_name=job_display_name,
            model_name=self.resource_name,
            instances_format=instances_format,
            predictions_format=predictions_format,
            gcs_source=gcs_source,
            bigquery_source=bigquery_source,
            gcs_destination_prefix=gcs_destination_prefix,
            bigquery_destination_prefix=bigquery_destination_prefix,
            model_parameters=model_parameters,
            machine_type=machine_type,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            starting_replica_count=starting_replica_count,
            max_replica_count=max_replica_count,
            generate_explanation=generate_explanation,
            explanation_metadata=explanation_metadata,
            explanation_parameters=explanation_parameters,
            labels=labels,
            project=self.project,
            location=self.location,
            credentials=credentials or self.credentials,
            encryption_spec_key_name=encryption_spec_key_name,
            sync=sync,
        )
