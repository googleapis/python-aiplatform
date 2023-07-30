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
import itertools
from typing import Dict, List, Optional, Sequence, Tuple, Union, Any

from google.auth import credentials as auth_credentials
import proto

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform.preview import model_evaluation
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import _explanation_utils
from google.cloud.aiplatform.compat.services import (
    deployment_resource_pool_service_client_v1beta1,
    endpoint_service_client,
)
from google.cloud.aiplatform.compat.types import (
    deployed_model_ref_v1beta1 as gca_deployed_model_ref_compat,
    deployment_resource_pool_v1beta1 as gca_deployment_resource_pool_compat,
    endpoint_v1beta1 as gca_endpoint_compat,
    machine_resources_v1beta1 as gca_machine_resources_compat,
    model_v1 as gca_model_compat,
    model_evaluation_slice as gca_model_evaluation_slice_compat,
)

_DEFAULT_MACHINE_TYPE = "n1-standard-2"

_LOGGER = base.Logger(__name__)


class DeploymentResourcePool(base.VertexAiResourceNounWithFutureManager):
    client_class = utils.DeploymentResourcePoolClientWithOverride
    _resource_noun = "deploymentResourcePools"
    _getter_method = "get_deployment_resource_pool"
    _list_method = "list_deployment_resource_pools"
    _delete_method = "delete_deployment_resource_pool"
    _parse_resource_name_method = "parse_deployment_resource_pool_path"
    _format_resource_name_method = "deployment_resource_pool_path"

    def __init__(
        self,
        deployment_resource_pool_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves a DeploymentResourcePool.

        Args:
            deployment_resource_pool_name (str):
                Required. The fully-qualified resource name or ID of the
                deployment resource pool. Example:
                "projects/123/locations/us-central1/deploymentResourcePools/456"
                or "456" when project and location are initialized or passed.
            project (str):
                Optional. Project containing the deployment resource pool to
                retrieve. If not set, the project given to `aiplatform.init`
                will be used.
            location (str):
                Optional. Location containing the deployment resource pool to
                retrieve. If not set, the location given to `aiplatform.init`
                will be used.
            credentials: Optional[auth_credentials.Credentials]=None,
                Custom credentials to use to retrieve the deployment resource
                pool. If not set, the credentials given to `aiplatform.init`
                will be used.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=deployment_resource_pool_name,
        )

        deployment_resource_pool_name = utils.full_resource_name(
            resource_name=deployment_resource_pool_name,
            resource_noun=self._resource_noun,
            parse_resource_name_method=self._parse_resource_name,
            format_resource_name_method=self._format_resource_name,
            project=project,
            location=location,
        )

        self._gca_resource = self._get_gca_resource(
            resource_name=deployment_resource_pool_name
        )

    @classmethod
    def create(
        cls,
        deployment_resource_pool_id: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        metadata: Sequence[Tuple[str, str]] = (),
        credentials: Optional[auth_credentials.Credentials] = None,
        machine_type: Optional[str] = None,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        sync=True,
        create_request_timeout: Optional[float] = None,
    ) -> "DeploymentResourcePool":
        """Creates a new DeploymentResourcePool.

        Args:
            deployment_resource_pool_id (str):
                Required. User-specified name for the new deployment resource
                pool.
            project (str):
                Optional. Project containing the deployment resource pool to
                retrieve. If not set, the project given to `aiplatform.init`
                will be used.
            location (str):
                Optional. Location containing the deployment resource pool to
                retrieve. If not set, the location given to `aiplatform.init`
                will be used.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
            credentials: Optional[auth_credentials.Credentials]=None,
                Optional. Custom credentials to use to retrieve the deployment
                resource pool. If not set, the credentials given to
                `aiplatform.init` will be used.
            machine_type (str):
                Optional. Machine type to use for the deployment resource pool.
                If not set, the default machine type of `n1-standard-2` is
                used.
            min_replica_count (int):
                Optional. The minimum replica count of the new deployment
                resource pool. Each replica serves a copy of each model deployed
                on the deployment resource pool. If this value is less than
                `max_replica_count`, then autoscaling is enabled, and the actual
                number of replicas will be adjusted to bring resource usage in
                line with the autoscaling targets.
            max_replica_count (int):
                Optional. The maximum replica count of the new deployment
                resource pool.
            accelerator_type (str):
                Optional. Hardware accelerator type. Must also set accelerator_
                count if used. One of NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
                NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4, or
                NVIDIA_TESLA_A100.
            accelerator_count (int):
                Optional. The number of accelerators attached to each replica.
            autoscaling_target_cpu_utilization (int):
                Optional. Target CPU utilization value for autoscaling. A
                default value of 60 will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int):
                Optional. Target accelerator duty cycle percentage to use for
                autoscaling. Must also set accelerator_type and accelerator
                count if specified. A default value of 60 will be used if
                accelerators are requested and this is not specified.
            sync (bool):
                Optional. Whether to execute this method synchronously. If
                False, this method will be executed in a concurrent Future and
                any downstream object will be immediately returned and synced
                when the Future has completed.
            create_request_timeout (float):
                Optional. The create request timeout in seconds.

        Returns:
            DeploymentResourcePool
        """

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        project = project or initializer.global_config.project
        location = location or initializer.global_config.location

        return cls._create(
            api_client=api_client,
            deployment_resource_pool_id=deployment_resource_pool_id,
            project=project,
            location=location,
            metadata=metadata,
            credentials=credentials,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            autoscaling_target_cpu_utilization=autoscaling_target_cpu_utilization,
            autoscaling_target_accelerator_duty_cycle=autoscaling_target_accelerator_duty_cycle,
            sync=sync,
            create_request_timeout=create_request_timeout,
        )

    @classmethod
    @base.optional_sync()
    def _create(
        cls,
        api_client: deployment_resource_pool_service_client_v1beta1.DeploymentResourcePoolServiceClient,
        deployment_resource_pool_id: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        metadata: Sequence[Tuple[str, str]] = (),
        credentials: Optional[auth_credentials.Credentials] = None,
        machine_type: Optional[str] = None,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        sync=True,
        create_request_timeout: Optional[float] = None,
    ) -> "DeploymentResourcePool":
        """Creates a new DeploymentResourcePool.

        Args:
            api_client (DeploymentResourcePoolServiceClient):
                Required. DeploymentResourcePoolServiceClient used to make the
                underlying CreateDeploymentResourcePool API call.
            deployment_resource_pool_id (str):
                Required. User-specified name for the new deployment resource
                pool.
            project (str):
                Optional. Project containing the deployment resource pool to
                retrieve. If not set, the project given to `aiplatform.init`
                will be used.
            location (str):
                Optional. Location containing the deployment resource pool to
                retrieve. If not set, the location given to `aiplatform.init`
                will be used.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
            credentials: Optional[auth_credentials.Credentials]=None,
                Optional. Custom credentials to use to retrieve the deployment
                resource pool. If not set, the credentials given to
                `aiplatform.init` will be used.
            machine_type (str):
                Optional. Machine type to use for the deployment resource pool.
                If not set, the default machine type of `n1-standard-2` is
                used.
            min_replica_count (int):
                Optional. The minimum replica count of the new deployment
                resource pool. Each replica serves a copy of each model deployed
                on the deployment resource pool. If this value is less than
                `max_replica_count`, then autoscaling is enabled, and the actual
                number of replicas will be adjusted to bring resource usage in
                line with the autoscaling targets.
            max_replica_count (int):
                Optional. The maximum replica count of the new deployment
                resource pool.
            accelerator_type (str):
                Optional. Hardware accelerator type. Must also set accelerator_
                count if used. One of NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
                NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4, or
                NVIDIA_TESLA_A100.
            accelerator_count (int):
                Optional. The number of accelerators attached to each replica.
            autoscaling_target_cpu_utilization (int):
                Optional. Target CPU utilization value for autoscaling. A
                default value of 60 will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int):
                Optional. Target accelerator duty cycle percentage to use for
                autoscaling. Must also set accelerator_type and accelerator
                count if specified. A default value of 60 will be used if
                accelerators are requested and this is not specified.
            sync (bool):
                Optional. Whether to execute this method synchronously. If
                False, this method will be executed in a concurrent Future and
                any downstream object will be immediately returned and synced
                when the Future has completed.
            create_request_timeout (float):
                Optional. The create request timeout in seconds.

        Returns:
            DeploymentResourcePool
        """

        parent = initializer.global_config.common_location_path(
            project=project, location=location
        )

        dedicated_resources = gca_machine_resources_compat.DedicatedResources(
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
        )

        machine_spec = gca_machine_resources_compat.MachineSpec(
            machine_type=machine_type
        )

        if autoscaling_target_cpu_utilization:
            autoscaling_metric_spec = (
                gca_machine_resources_compat.AutoscalingMetricSpec(
                    metric_name=(
                        "aiplatform.googleapis.com/prediction/online/cpu/utilization"
                    ),
                    target=autoscaling_target_cpu_utilization,
                )
            )
            dedicated_resources.autoscaling_metric_specs.extend(
                [autoscaling_metric_spec]
            )

        if accelerator_type and accelerator_count:
            utils.validate_accelerator_type(accelerator_type)
            machine_spec.accelerator_type = accelerator_type
            machine_spec.accelerator_count = accelerator_count

            if autoscaling_target_accelerator_duty_cycle:
                autoscaling_metric_spec = gca_machine_resources_compat.AutoscalingMetricSpec(
                    metric_name="aiplatform.googleapis.com/prediction/online/accelerator/duty_cycle",
                    target=autoscaling_target_accelerator_duty_cycle,
                )
                dedicated_resources.autoscaling_metric_specs.extend(
                    [autoscaling_metric_spec]
                )

        dedicated_resources.machine_spec = machine_spec

        gapic_drp = gca_deployment_resource_pool_compat.DeploymentResourcePool(
            dedicated_resources=dedicated_resources
        )

        operation_future = api_client.create_deployment_resource_pool(
            parent=parent,
            deployment_resource_pool=gapic_drp,
            deployment_resource_pool_id=deployment_resource_pool_id,
            metadata=metadata,
            timeout=create_request_timeout,
        )

        _LOGGER.log_create_with_lro(cls, operation_future)

        created_drp = operation_future.result()

        _LOGGER.log_create_complete(cls, created_drp, "deployment resource pool")

        return cls._construct_sdk_resource_from_gapic(
            gapic_resource=created_drp,
            project=project,
            location=location,
            credentials=credentials,
        )

    def query_deployed_models(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List[gca_deployed_model_ref_compat.DeployedModelRef]:
        """Lists the deployed models using this resource pool.

        Args:
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
            List of DeployedModelRef objects containing the endpoint ID and
            deployed model ID of the deployed models using this resource pool.
        """
        project = project or initializer.global_config.project
        location = location or initializer.global_config.location
        api_client = DeploymentResourcePool._instantiate_client(
            location=location, credentials=credentials
        )
        response = api_client.query_deployed_models(
            deployment_resource_pool=self.resource_name
        )
        return list(
            itertools.chain(page.deployed_model_refs for page in response.pages)
        )

    @classmethod
    def list(
        cls,
        filter: Optional[str] = None,
        order_by: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["models.DeploymentResourcePool"]:
        """Lists the deployment resource pools.

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
            List of deployment resource pools.
        """
        return cls._list(
            filter=filter,
            order_by=order_by,
            project=project,
            location=location,
            credentials=credentials,
        )


class Endpoint(aiplatform.Endpoint):
    @staticmethod
    def _validate_deploy_args(
        min_replica_count: Optional[int],
        max_replica_count: Optional[int],
        accelerator_type: Optional[str],
        deployed_model_display_name: Optional[str],
        traffic_split: Optional[Dict[str, int]],
        traffic_percentage: Optional[int],
        deployment_resource_pool: Optional[DeploymentResourcePool],
    ):
        """Helper method to validate deploy arguments.

        Args:
            min_replica_count (int): Required. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Required. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the larger value of min_replica_count or 1 will
              be used. If value provided is smaller than min_replica_count, it will
              automatically be increased to be min_replica_count.
            accelerator_type (str): Required. Hardware accelerator type. One of
              ACCELERATOR_TYPE_UNSPECIFIED, NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
              NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            deployed_model_display_name (str): Required. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              arguments.

        Raises:
            ValueError: if min/max replica or accelerator type are specified
              along with a deployment resource pool, or if min/max replicas are
              omitted or negative without specifying a deployment resource pool,
              or if traffic percentage > 100 or < 0, or if traffic_split does
              not sum to 100, or if the provided accelerator type is invalid.
        """
        if not deployment_resource_pool:
            if not (min_replica_count and max_replica_count):
                raise ValueError(
                    "Minimum and maximum replica counts must not be "
                    "if not using a shared resource pool."
                )
            return super()._validate_deploy_args(
                min_replica_count=min_replica_count,
                max_replica_count=max_replica_count,
                accelerator_type=accelerator_type,
                deployed_model_display_name=deployed_model_display_name,
                traffic_split=traffic_split,
                traffic_percentage=traffic_percentage,
            )

        if (
            min_replica_count
            and min_replica_count != 1
            or max_replica_count
            and max_replica_count != 1
        ):
            _LOGGER.warning(
                "Ignoring explicitly specified replica counts, "
                "since deployment_resource_pool was also given."
            )
        if accelerator_type:
            raise ValueError(
                "Conflicting deployment parameters were given."
                "deployment_resource_pool may not be specified at the same time"
                "as accelerator_type."
            )
        if traffic_split is None:
            if traffic_percentage > 100:
                raise ValueError("Traffic percentage cannot be greater than 100.")
            if traffic_percentage < 0:
                raise ValueError("Traffic percentage cannot be negative.")

        elif traffic_split:
            if sum(traffic_split.values()) != 100:
                raise ValueError(
                    "Sum of all traffic within traffic split needs to be 100."
                )
        if deployed_model_display_name is not None:
            utils.validate_display_name(deployed_model_display_name)

    def deploy(
        self,
        model: "Model",
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: int = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 1,
        max_replica_count: Optional[int] = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        service_account: Optional[str] = None,
        explanation_metadata: Optional[aiplatform.explain.ExplanationMetadata] = None,
        explanation_parameters: Optional[
            aiplatform.explain.ExplanationParameters
        ] = None,
        metadata: Sequence[Tuple[str, str]] = (),
        sync=True,
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        deployment_resource_pool: Optional[DeploymentResourcePool] = None,
    ) -> None:
        """Deploys a Model to the Endpoint.

        Args:
            model (aiplatform.Model): Required. Model to be deployed.
            deployed_model_display_name (str): Optional. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            machine_type (str): Optional. The type of machine. Not specifying
              machine type will result in model to be deployed with automatic
              resources.
            min_replica_count (int): Optional. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Optional. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the larger value of min_replica_count or 1 will
              be used. If value provided is smaller than min_replica_count, it will
              automatically be increased to be min_replica_count.
            accelerator_type (str): Optional. Hardware accelerator type. Must also
              set accelerator_count if used. One of ACCELERATOR_TYPE_UNSPECIFIED,
              NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100,
              NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int): Optional. The number of accelerators to attach
              to a worker replica.
            service_account (str): The service account that the DeployedModel's
              container runs as. Specify the email address of the service account.
              If this service account is not specified, the container runs as a
              service account that doesn't have access to the resource project.
              Users deploying the Model must have the `iam.serviceAccounts.actAs`
              permission on this service account.
            explanation_metadata (aiplatform.explain.ExplanationMetadata): Optional.
              Metadata describing the Model's input and output for explanation.
              `explanation_metadata` is optional while `explanation_parameters` must
              be specified when used. For more details, see `Ref docs
              <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.explain.ExplanationParameters):
              Optional. Parameters to configure explaining for Model's predictions.
              For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            metadata (Sequence[Tuple[str, str]]): Optional. Strings which should be
              sent along with the request as metadata.
            sync (bool): Whether to execute this method synchronously. If False,
              this method will be executed in concurrent Future and any downstream
              object will be immediately returned and synced when the Future has
              completed.
            deploy_request_timeout (float): Optional. The timeout for the deploy
              request in seconds.
            autoscaling_target_cpu_utilization (int): Target CPU Utilization to use
              for Autoscaling Replicas. A default value of 60 will be used if not
              specified.
            autoscaling_target_accelerator_duty_cycle (int): Target Accelerator Duty
              Cycle. Must also set accelerator_type and accelerator_count if
              specified. A default value of 60 will be used if not specified.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              arguments.
        """
        self._sync_gca_resource_if_skipped()

        self._validate_deploy_args(
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            deployed_model_display_name=deployed_model_display_name,
            traffic_split=traffic_split,
            traffic_percentage=traffic_percentage,
            deployment_resource_pool=deployment_resource_pool,
        )

        explanation_spec = _explanation_utils.create_and_validate_explanation_spec(
            explanation_metadata=explanation_metadata,
            explanation_parameters=explanation_parameters,
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
            service_account=service_account,
            explanation_spec=explanation_spec,
            metadata=metadata,
            sync=sync,
            deploy_request_timeout=deploy_request_timeout,
            autoscaling_target_cpu_utilization=autoscaling_target_cpu_utilization,
            autoscaling_target_accelerator_duty_cycle=autoscaling_target_accelerator_duty_cycle,
            deployment_resource_pool=deployment_resource_pool,
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
        service_account: Optional[str] = None,
        explanation_spec: Optional[aiplatform.explain.ExplanationSpec] = None,
        metadata: Sequence[Tuple[str, str]] = (),
        sync=True,
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        deployment_resource_pool: Optional[DeploymentResourcePool] = None,
    ) -> None:
        """Deploys a Model to the Endpoint.

        Args:
            model (aiplatform.Model): Required. Model to be deployed.
            deployed_model_display_name (str): Optional. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            machine_type (str): Optional. The type of machine. Not specifying
              machine type will result in model to be deployed with automatic
              resources.
            min_replica_count (int): Optional. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Optional. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the larger value of min_replica_count or 1 will
              be used. If value provided is smaller than min_replica_count, it will
              automatically be increased to be min_replica_count.
            accelerator_type (str): Optional. Hardware accelerator type. Must also
              set accelerator_count if used. One of ACCELERATOR_TYPE_UNSPECIFIED,
              NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100,
              NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int): Optional. The number of accelerators to attach
              to a worker replica.
            service_account (str): The service account that the DeployedModel's
              container runs as. Specify the email address of the service account.
              If this service account is not specified, the container runs as a
              service account that doesn't have access to the resource project.
              Users deploying the Model must have the `iam.serviceAccounts.actAs`
              permission on this service account.
            explanation_spec (aiplatform.explain.ExplanationSpec): Optional.
              Specification of Model explanation.
            metadata (Sequence[Tuple[str, str]]): Optional. Strings which should be
              sent along with the request as metadata.
            sync (bool): Whether to execute this method synchronously. If False,
              this method will be executed in concurrent Future and any downstream
              object will be immediately returned and synced when the Future has
              completed.
            deploy_request_timeout (float): Optional. The timeout for the deploy
              request in seconds.
            autoscaling_target_cpu_utilization (int): Target CPU Utilization to use
              for Autoscaling Replicas. A default value of 60 will be used if not
              specified.
            autoscaling_target_accelerator_duty_cycle (int): Target Accelerator Duty
              Cycle. Must also set accelerator_type and accelerator_count if
              specified. A default value of 60 will be used if not specified.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              arguments.
        """
        _LOGGER.log_action_start_against_resource(
            f"Deploying Model {model.resource_name} to", "", self
        )

        self._deploy_call(
            api_client=self.api_client,
            endpoint_resource_name=self.resource_name,
            model=model,
            endpoint_resource_traffic_split=self._gca_resource.traffic_split,
            network=self.network,
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
            deployment_resource_pool=deployment_resource_pool,
        )

        _LOGGER.log_action_completed_against_resource("model", "deployed", self)

        self._sync_gca_resource()

    @classmethod
    def _deploy_call(
        cls,
        api_client: endpoint_service_client.EndpointServiceClient,
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
        explanation_spec: Optional[aiplatform.explain.ExplanationSpec] = None,
        metadata: Sequence[Tuple[str, str]] = (),
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        deployment_resource_pool: Optional[DeploymentResourcePool] = None,
    ) -> None:
        """Helper method to deploy model to endpoint.

        Args:
            api_client (endpoint_service_client.EndpointServiceClient): Required.
              endpoint_service_client.EndpointServiceClient to make call.
            endpoint_resource_name (str): Required. Endpoint resource name to deploy
              model to.
            model (aiplatform.Model): Required. Model to be deployed.
            endpoint_resource_traffic_split (proto.MapField): Optional. Endpoint
              current resource traffic split.
            network (str): Optional. The full name of the Compute Engine network to
              which this Endpoint will be peered. E.g.
              "projects/123/global/networks/my_vpc". Private services access must
              already be configured for the network.
            deployed_model_display_name (str): Optional. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            machine_type (str): Optional. The type of machine. Not specifying
              machine type will result in model to be deployed with automatic
              resources.
            min_replica_count (int): Optional. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Optional. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the larger value of min_replica_count or 1 will
              be used. If value provided is smaller than min_replica_count, it will
              automatically be increased to be min_replica_count.
            accelerator_type (str): Optional. Hardware accelerator type. Must also
              set accelerator_count if used. One of ACCELERATOR_TYPE_UNSPECIFIED,
              NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100,
              NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int): Optional. The number of accelerators to attach
              to a worker replica.
            service_account (str): The service account that the DeployedModel's
              container runs as. Specify the email address of the service account.
              If this service account is not specified, the container runs as a
              service account that doesn't have access to the resource project.
              Users deploying the Model must have the `iam.serviceAccounts.actAs`
              permission on this service account.
            explanation_spec (aiplatform.explain.ExplanationSpec): Optional.
              Specification of Model explanation.
            metadata (Sequence[Tuple[str, str]]): Optional. Strings which should be
              sent along with the request as metadata.
            deploy_request_timeout (float): Optional. The timeout for the deploy
              request in seconds.
            autoscaling_target_cpu_utilization (int): Optional. Target CPU
              Utilization to use for Autoscaling Replicas. A default value of 60
              will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int): Optional. Target
              Accelerator Duty Cycle. Must also set accelerator_type and
              accelerator_count if specified. A default value of 60 will be used if
              not specified.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              arguments.

        Raises:
            ValueError: If only `accelerator_type` or `accelerator_count` is
            specified.
            ValueError: If model does not support deployment.
            ValueError: If there is not current traffic split and traffic percentage
                is not 0 or 100.
            ValueError: If `deployment_resource_pool` and a custom machine spec
                are both present.
            ValueError: If both `explanation_spec` and `deployment_resource_pool`
                are present.
        """
        if not deployment_resource_pool:
            return super()._deploy_call(
                api_client=api_client,
                endpoint_resource_name=endpoint_resource_name,
                model=model,
                endpoint_resource_traffic_split=endpoint_resource_traffic_split,
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

        deployed_model = gca_endpoint_compat.DeployedModel(
            model=model.versioned_resource_name,
            display_name=deployed_model_display_name,
            service_account=service_account,
        )

        _LOGGER.info(model.supported_deployment_resources_types)
        supports_shared_resources = (
            gca_model_compat.Model.DeploymentResourcesType.SHARED_RESOURCES
            in model.supported_deployment_resources_types
        )

        if not supports_shared_resources:
            raise ValueError(
                "`deployment_resource_pool` may only be specified for models "
                " which support shared resources."
            )

        provided_custom_machine_spec = (
            machine_type
            or accelerator_type
            or accelerator_count
            or autoscaling_target_accelerator_duty_cycle
            or autoscaling_target_cpu_utilization
        )

        if provided_custom_machine_spec:
            raise ValueError(
                "Conflicting parameters in deployment request. "
                "The machine_type, accelerator_type and accelerator_count,"
                "autoscaling_target_accelerator_duty_cycle,"
                "autoscaling_target_cpu_utilization parameters may not be set "
                "when `deployment_resource_pool` is specified."
            )

        deployed_model.shared_resources = deployment_resource_pool.resource_name

        if explanation_spec:
            raise ValueError(
                "Model explanation is not supported for deployments using "
                "shared resources."
            )

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

        operation_future = api_client.select_version("v1beta1").deploy_model(
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


_SUPPORTED_EVAL_PREDICTION_TYPES = [
    "classification",
    "regression",
    "forecasting",
]


class Model(aiplatform.Model):
    def deploy(
        self,
        endpoint: Optional[Union["Endpoint", models.PrivateEndpoint]] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 1,
        max_replica_count: Optional[int] = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        service_account: Optional[str] = None,
        explanation_metadata: Optional[aiplatform.explain.ExplanationMetadata] = None,
        explanation_parameters: Optional[
            aiplatform.explain.ExplanationParameters
        ] = None,
        metadata: Sequence[Tuple[str, str]] = (),
        encryption_spec_key_name: Optional[str] = None,
        network: Optional[str] = None,
        sync=True,
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        deployment_resource_pool: Optional[DeploymentResourcePool] = None,
    ) -> Union[Endpoint, models.PrivateEndpoint]:
        """Deploys model to endpoint.

        Endpoint will be created if unspecified.

        Args:
            endpoint (Union[Endpoint, models.PrivateEndpoint]): Optional. Public or
              private Endpoint to deploy model to. If not specified, endpoint
              display name will be model display name+'_endpoint'.
            deployed_model_display_name (str): Optional. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            machine_type (str): Optional. The type of machine. Not specifying
              machine type will result in model to be deployed with automatic
              resources.
            min_replica_count (int): Optional. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Optional. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the smaller value of min_replica_count or 1
              will be used.
            accelerator_type (str): Optional. Hardware accelerator type. Must also
              set accelerator_count if used. One of ACCELERATOR_TYPE_UNSPECIFIED,
              NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100,
              NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int): Optional. The number of accelerators to attach
              to a worker replica.
            service_account (str): The service account that the DeployedModel's
              container runs as. Specify the email address of the service account.
              If this service account is not specified, the container runs as a
              service account that doesn't have access to the resource project.
              Users deploying the Model must have the `iam.serviceAccounts.actAs`
              permission on this service account.
            explanation_metadata (aiplatform.explain.ExplanationMetadata): Optional.
              Metadata describing the Model's input and output for explanation.
              `explanation_metadata` is optional while `explanation_parameters` must
              be specified when used. For more details, see `Ref docs
              <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.explain.ExplanationParameters):
              Optional. Parameters to configure explaining for Model's predictions.
              For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            metadata (Sequence[Tuple[str, str]]): Optional. Strings which should be
              sent along with the request as metadata.
            encryption_spec_key_name (Optional[str]): Optional. The Cloud KMS
              resource identifier of the customer managed encryption key used to
              protect the model. Has the
                form:
                  ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                  The key needs to be in the same region as where the compute
                  resource is created.  If set, this Endpoint and all sub-resources
                  of this Endpoint will be secured by this key.  Overrides
                  encryption_spec_key_name set in aiplatform.init.
            network (str): Optional. The full name of the Compute Engine network to
              which the Endpoint, if created, will be peered to. E.g.
              "projects/12345/global/networks/myVPC". Private services access must
              already be configured for the network. If set or
              aiplatform.init(network=...) has been set, a PrivateEndpoint will be
              created. If left unspecified, an Endpoint will be created. Read more
              about PrivateEndpoints [in the
              documentation](https://cloud.google.com/vertex-ai/docs/predictions/using-private-endpoints).
            sync (bool): Whether to execute this method synchronously. If False,
              this method will be executed in concurrent Future and any downstream
              object will be immediately returned and synced when the Future has
              completed.
            deploy_request_timeout (float): Optional. The timeout for the deploy
              request in seconds.
            autoscaling_target_cpu_utilization (int): Optional. Target CPU
              Utilization to use for Autoscaling Replicas. A default value of 60
              will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int): Optional. Target
              Accelerator Duty Cycle. Must also set accelerator_type and
              accelerator_count if specified. A default value of 60 will be used if
              not specified.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              arguments.

        Returns:
            endpoint (Union[Endpoint, models.PrivateEndpoint]):
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
            deployment_resource_pool=deployment_resource_pool,
        )

        if isinstance(endpoint, models.PrivateEndpoint):
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
            deployment_resource_pool=deployment_resource_pool,
        )

    @base.optional_sync(return_input_arg="endpoint", bind_future_to_self=False)
    def _deploy(
        self,
        endpoint: Optional[Union["Endpoint", models.PrivateEndpoint]] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 1,
        max_replica_count: Optional[int] = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        service_account: Optional[str] = None,
        explanation_spec: Optional[aiplatform.explain.ExplanationSpec] = None,
        metadata: Sequence[Tuple[str, str]] = (),
        encryption_spec_key_name: Optional[str] = None,
        network: Optional[str] = None,
        sync: bool = True,
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        deployment_resource_pool: Optional[DeploymentResourcePool] = None,
    ) -> Union[Endpoint, models.PrivateEndpoint]:
        """Deploys model to endpoint.

        Endpoint will be created if unspecified.

        Args:
            endpoint (Union[Endpoint, PrivateEndpoint]): Optional. Public or private
              Endpoint to deploy model to. If not specified, endpoint display name
              will be model display name+'_endpoint'.
            deployed_model_display_name (str): Optional. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            machine_type (str): Optional. The type of machine. Not specifying
              machine type will result in model to be deployed with automatic
              resources.
            min_replica_count (int): Optional. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Optional. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the smaller value of min_replica_count or 1
              will be used.
            accelerator_type (str): Optional. Hardware accelerator type. Must also
              set accelerator_count if used. One of ACCELERATOR_TYPE_UNSPECIFIED,
              NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100,
              NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int): Optional. The number of accelerators to attach
              to a worker replica.
            service_account (str): The service account that the DeployedModel's
              container runs as. Specify the email address of the service account.
              If this service account is not specified, the container runs as a
              service account that doesn't have access to the resource project.
              Users deploying the Model must have the `iam.serviceAccounts.actAs`
              permission on this service account.
            explanation_spec (aiplatform.explain.ExplanationSpec): Optional.
              Specification of Model explanation.
            metadata (Sequence[Tuple[str, str]]): Optional. Strings which should be
              sent along with the request as metadata.
            encryption_spec_key_name (Optional[str]): Optional. The Cloud KMS
              resource identifier of the customer managed encryption key used to
              protect the model. Has the
                form:
                  ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                  The key needs to be in the same region as where the compute
                  resource is created.  If set, this Model and all sub-resources of
                  this Model will be secured by this key.  Overrides
                  encryption_spec_key_name set in aiplatform.init
            network (str): Optional. The full name of the Compute Engine network to
              which the Endpoint, if created, will be peered to. E.g.
              "projects/12345/global/networks/myVPC". Private services access must
              already be configured for the network. Read more about
              PrivateEndpoints [in the
              documentation](https://cloud.google.com/vertex-ai/docs/predictions/using-private-endpoints).
            sync (bool): Whether to execute this method synchronously. If False,
              this method will be executed in concurrent Future and any downstream
              object will be immediately returned and synced when the Future has
              completed.
            deploy_request_timeout (float): Optional. The timeout for the deploy
              request in seconds.
            autoscaling_target_cpu_utilization (int): Optional. Target CPU
              Utilization to use for Autoscaling Replicas. A default value of 60
              will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int): Optional. Target
              Accelerator Duty Cycle. Must also set accelerator_type and
              accelerator_count if specified. A default value of 60 will be used if
              not specified.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              arguments.

        Returns:
            endpoint (Union[Endpoint, models.PrivateEndpoint]):
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
            else:
                endpoint = models.PrivateEndpoint.create(
                    display_name=display_name,
                    network=network,
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
            deployment_resource_pool=deployment_resource_pool,
        )

        _LOGGER.log_action_completed_against_resource("model", "deployed", endpoint)

        endpoint._sync_gca_resource()

        return endpoint

    def evaluate(
        self,
        prediction_type: str,
        target_field_name: Optional[str] = None,
        gcs_source_uris: Optional[List[str]] = None,
        bigquery_source_uri: Optional[str] = None,
        bigquery_destination_output_uri: Optional[str] = None,
        class_labels: Optional[List[str]] = None,
        prediction_label_column: Optional[str] = None,
        prediction_score_column: Optional[str] = None,
        sliced_metrics_config: Optional[List[Dict[str, Any]]] = None,
        evaluation_staging_path: Optional[str] = None,
        service_account: Optional[str] = None,
        generate_feature_attributions: Optional[bool] = False,
        evaluation_pipeline_display_name: Optional[str] = None,
        evaluation_metrics_display_name: Optional[str] = None,
        network: Optional[str] = None,
        encryption_spec_key_name: Optional[str] = None,
        experiment: Optional[Union[str, "aiplatform.Experiment"]] = None,
        enable_error_analysis: Optional[bool] = False,
        test_dataset_resource_name: Optional[str] = "",
        test_dataset_annotation_set_name: Optional[str] = "",
        training_dataset_resource_name: Optional[str] = "",
        training_dataset_annotation_set_name: Optional[str] = "",
        test_dataset_storage_source_uris: Optional[List[str]] = [],
        training_dataset_storage_source_uris: Optional[List[str]] = [],
        instances_format: str = "jsonl",
        batch_predict_predictions_format: str = "jsonl",
        batch_predict_machine_type: str = "n1-standard-32",
        batch_predict_starting_replica_count: int = 5,
        batch_predict_max_replica_count: int = 10,
        batch_predict_accelerator_type: str = "",
        batch_predict_accelerator_count: int = 0,
        dataflow_machine_type: str = "n1-standard-8",
        dataflow_max_num_workers: int = 5,
        dataflow_disk_size_gb: int = 50,
        dataflow_service_account: str = "",
        dataflow_subnetwork: str = "",
        dataflow_use_public_ips: bool = True,
    ) -> "model_evaluation.ModelEvaluationJob":
        """Creates a model evaluation job running on Vertex Pipelines and returns the resulting
        ModelEvaluationJob resource.
        Example usage:
            my_model = Model(
                model_name="projects/123/locations/us-central1/models/456"
            )
            my_evaluation_job = my_model.evaluate(
                prediction_type="classification",
                target_field_name="type",
                data_source_uris=["gs://sdk-model-eval/my-prediction-data.csv"],
                evaluation_staging_path="gs://my-staging-bucket/eval_pipeline_root",
            )
            my_evaluation_job.wait()
            my_evaluation = my_evaluation_job.get_model_evaluation()
            my_evaluation.metrics
        Args:
            prediction_type (str):
                The problem type being addressed by this evaluation run. 'classification', 'regression',
                and 'forecasting' are the currently supported problem types.
            target_field_name (str):
                Optional. The column name of the field containing the label for this prediction task.
            gcs_source_uris (List[str]):
                Optional. A list of Cloud Storage data files containing the ground truth data to use for this
                evaluation job. These files should contain your model's prediction column. Currently only Google Cloud Storage
                urls are supported, for example: "gs://path/to/your/data.csv". The provided data files must be
                either CSV or JSONL. One of `gcs_source_uris` or `bigquery_source_uri` is required.
            bigquery_source_uri (str):
                Optional. A bigquery table URI containing the ground truth data to use for this evaluation job. This uri should
                be in the format 'bq://my-project-id.dataset.table'. One of `gcs_source_uris` or `bigquery_source_uri` is
                required.
            bigquery_destination_output_uri (str):
                Optional. A bigquery table URI where the Batch Prediction job associated with your Model Evaluation will write
                prediction output. This can be a BigQuery URI to a project ('bq://my-project'), a dataset
                ('bq://my-project.my-dataset'), or a table ('bq://my-project.my-dataset.my-table'). Required if `bigquery_source_uri`
                is provided.
            class_labels (List[str]):
                Optional. For custom (non-AutoML) classification models, a list of possible class names, in the
                same order that predictions are generated. This argument is required when prediction_type is 'classification'.
                For example, in a classification model with 3 possible classes that are outputted in the format: [0.97, 0.02, 0.01]
                with the class names "cat", "dog", and "fish", the value of `class_labels` should be `["cat", "dog", "fish"]` where
                the class "cat" corresponds with 0.97 in the example above.
            prediction_label_column (str):
                Optional. The column name of the field containing classes the model is scoring. Formatted to be able to find nested
                columns, delimeted by `.`. If not set, defaulted to `prediction.classes` for classification.
            prediction_score_column (str):
                Optional. The column name of the field containing batch prediction scores. Formatted to be able to find nested columns,
                delimeted by `.`. If not set, defaulted to `prediction.scores` for a `classification` problem_type, `prediction.value`
                for a `regression` problem_type.
            sliced_metrics_config (List[Dict[str, Union[str, int, dict[str, list[float, float]]]]]):
                Optional. A configuration for calculating model evaluation metrics on slices of data. This argument should contain
                a single list with a dictionary for each slicing spec. Each dictionary can contain multiple feature keys. The keys in
                `sliced_metrics_config` dictionaries should correspond to the names of features in your dataset. The value should
                indicate the values for that feature to compute the sliced metrics on. To compute sliced metrics for a string feature named 'country'
                on all data with a value of 'USA', `sliced_metrics_config` should be in the format: {"country": "USA"}. To compute
                sliced metrics for an int feature named 'age' on all data with an age of 10, `sliced_metrics_config` should be {"age": 10}.
                To compute a slice across a range of numerical values for a particular feature, pass a dictionary with a 'range' key.
                In the age example, to compute a slice on all data with ages ranging from 10 - 19, `sliced_metrics_config` should be
                {"age": {"range": [10,20]}}. To compute sliced metrics for all values of a given feature, pass the string "all_values" for that feature,
                for example: {"age": "all_values"}. Passing "all_values" will result in a separate slice generated for each possible value of that
                feature. "all_values" supports up to 50 values, the evaluation job will fail if you provide "all_values" for a feature with more than 50
                distinct values. You can combine the above configurations in a single dictionary to create slices based on multiple feature
                configurations. For example, passing [{"country": "USA", "age": 10}] to `sliced_metrics_config` would result in a slice
                containing metrics for all data with the value "USA" for country AND 10 for age.
            evaluation_staging_path (str):
                Optional. The GCS directory to use for staging files from this evaluation job. Defaults to the value set in
                aiplatform.init(staging_bucket=...) if not provided. Required if staging_bucket is not set in aiplatform.init().
            service_account (str):
                Optional. Specifies the service account for workload run-as account for this Model Evaluation PipelineJob.
                Users submitting jobs must have act-as permission on this run-as account. The service account running
                this Model Evaluation job needs the following permissions: Dataflow Worker, Storage Admin,
                Vertex AI Administrator, and Vertex AI Service Agent.
            generate_feature_attributions (boolean):
                Optional. Whether the model evaluation job should generate feature attributions. Defaults to False if not specified.
            evaluation_pipeline_display_name (str):
                Optional. The display name of your model evaluation job. This is the display name that will be applied to the
                Vertex Pipeline run for your evaluation job. If not set, a display name will be generated automatically.
            evaluation_metrics_display_name (str):
                Optional. The display name of the model evaluation resource uploaded to Vertex from your Model Evaluation pipeline.
            network (str):
                Optional. The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
            encryption_spec_key_name (str):
                Optional. The Cloud KMS resource identifier of the customer managed encryption key used to protect the job. Has the
                form: ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``. The key needs to be in the same
                region as where the compute resource is created. If this is set, then all
                resources created by the PipelineJob for this Model Evaluation will be encrypted with the provided encryption key.
                If not specified, encryption_spec of original PipelineJob will be used.
            experiment (Union[str, experiments_resource.Experiment]):
                Optional. The Vertex AI experiment name or instance to associate to the PipelineJob executing
                this model evaluation job. Metrics produced by the PipelineJob as system.Metric Artifacts
                will be associated as metrics to the provided experiment, and parameters from this PipelineJob
                will be associated as parameters to the provided experiment.
            enable_error_analysis (boolean):
                Optional. Whether the model evaluation job should generate error analysis. Defaults to False if not specified.
            test_dataset_resource_name (str):
                Optional.  A google.VertexDataset artifact of the test dataset.
                If `test_dataset_storage_source_uris` is also provided, this
                Vertex Dataset argument will override the GCS source.
            test_dataset_annotation_set_name (str):
                Optional. A string of the annotation_set resource name containing
                the ground truth of the test dataset used for evaluation.
            training_dataset_resource_name (str):
                Optional. A google.VertexDataset artifact of the training dataset.
                If `training_dataset_storage_source_uris` is also provided, this
                Vertex Dataset argument will override the GCS source.
            training_dataset_annotation_set_name (str):
                Optional. A string of the annotation_set resource name containing
                the ground truth of the test dataset used for evaluation.
            test_dataset_storage_source_uris (str):
                Optional. Google Cloud Storage URI(-s) to unmanaged test datasets.
                `jsonl` is currently the only allowed format. If `test_dataset`
                is also provided, this field will be overriden by the provided Vertex Dataset.
            training_dataset_storage_source_uris(str):
                Optional. Google Cloud Storage URI(-s) to unmanaged test datasets.
                `jsonl` is currently the only allowed format. If `training_dataset`
                is also provided, this field will be overriden by the provided Vertex Dataset.
            instances_format(str):
                Optional. The format in which instances are given,
                must be one of the Model's supportedInputStorageFormats. If not set,
                default to "jsonl". For more details about this input config, see
                https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.batchPredictionJobs#InputConfig.
            batch_predict_predictions_format(str):
                Optional. The format in which Vertex AI gives the
                predictions. Must be one of the Model's supportedOutputStorageFormats. If
                not set, default to "jsonl". If not set, default to "jsonl". For more details
                about this output config, see
                https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.batchPredictionJobs#OutputConfig.
            batch_predict_machine_type(str):
                Optional. The type of machine for running batch prediction
                on dedicated resources. If the Model supports DEDICATED_RESOURCES this
                config may be provided (and the job will use these resources). If the
                Model doesn't support AUTOMATIC_RESOURCES, this config must be provided.
                If not set, defaulted to `n1-standard-32`. For more details about the
                BatchDedicatedResources, see
                https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.batchPredictionJobs#BatchDedicatedResources.
                For more details about the machine spec, see
                https://cloud.google.com/vertex-ai/docs/reference/rest/v1/MachineSpec
            batch_predict_starting_replica_count(int):
                Optional. The number of machine replicas used at
                the start of the batch operation. If not set, Vertex AI decides starting
                number, not greater than `max_replica_count`. Only used if `machine_type`
                is set.
            batch_predict_max_replica_count(int):
                Optional. The maximum number of machine replicas the
                batch operation may be scaled to. Only used if `machine_type` is set.
                Default is 10.
            batch_predict_accelerator_type(str):
                Optional. The type of accelerator(s) that may be
                attached to the machine as per `batch_predict_accelerator_count`. Only
                used if `batch_predict_machine_type` is set. For more details about the
                machine spec, see
                https://cloud.google.com/vertex-ai/docs/reference/rest/v1/MachineSpec
                batch_predict_accelerator_count: The number of accelerators to attach to the
                `batch_predict_machine_type`. Only used if `batch_predict_machine_type` is
                set.
            dataflow_machine_type(str):
                Optional. The dataflow machine type for evaluation components.
            dataflow_max_num_workers(int):
                Optional. The max number of Dataflow workers for evaluation
                components.
            dataflow_disk_size_gb(int):
                Optional. Dataflow worker's disk size in GB for evaluation
                components.
            dataflow_service_account(str):
                Optional. Custom service account to run dataflow jobs.
            dataflow_subnetwork(str):
                Optional. Dataflow's fully qualified subnetwork name, when empty
                the default subnetwork will be used. Example:
                https://cloud.google.com/dataflow/docs/guides/specifying-networks#example_network_and_subnetwork_specifications
            dataflow_use_public_ips(bool):
                Optional. Specifies whether Dataflow workers use public IPaddresses.
        Returns:
            model_evaluation.ModelEvaluationJob: Instantiated representation of the
            _ModelEvaluationJob.
        Raises:
            ValueError:
                If staging_bucket was not set in aiplatform.init() and evaluation_staging_bucket was not provided.
                If the provided `prediction_type` is not valid.
                If the provided `data_source_uris` don't start with 'gs://'.
                If vertex dataset and custom dataset uris were not provided.
        """
        if prediction_type not in _SUPPORTED_EVAL_PREDICTION_TYPES:
            raise ValueError("Please provide a supported model prediction type.")

        # TODO: add a comment where this file is defined so we're notified if it changes
        if (
            self._gca_resource.metadata_schema_uri
            == "https://storage.googleapis.com/google-cloud-aiplatform/schema/model/metadata/automl_tabular_1.0.0.yaml"
        ):
            model_type = "automl_tabular"
        elif (
            self._gca_resource.metadata_schema_uri
            == "https://storage.googleapis.com/google-cloud-aiplatform/schema/model/metadata/automl_image_classification_1.0.0.yaml"
        ):
            model_type = "automl_vision"
        else:
            model_type = "other"

        if model_type == "automl_vision" and enable_error_analysis is True:
            target_field_name = "ground-truth"
            if (
                test_dataset_resource_name is None
                or test_dataset_annotation_set_name is None
                or training_dataset_resource_name is None
                or training_dataset_annotation_set_name is None
            ) and (
                test_dataset_storage_source_uris is None
                or training_dataset_storage_source_uris is None
            ):
                raise ValueError(
                    "Either `test_dataset_resource_name`, `test_dataset_annotation_set_name`, `training_dataset_resource_name` and `training_dataset_annotation_set_name` must be provided. Or `test_dataset_storage_source_uris` and `training_dataset_storage_source_uris` must be provided."
                )
        elif (
            model_type == "automl_vision"
            and enable_error_analysis is False
            and generate_feature_attributions is False
        ):
            target_field_name = "ground-truth"
            if (
                test_dataset_resource_name is None
                or test_dataset_annotation_set_name is None
            ) and (test_dataset_storage_source_uris is None):
                raise ValueError(
                    "Either `test_dataset_resource_name` and `test_dataset_annotation_set_name` must be provided. Or `test_dataset_storage_source_uris` must be provided."
                )
        else:
            if target_field_name is None:
                raise ValueError("`target_field_name` must be provided.")

            if not gcs_source_uris and not bigquery_source_uri:
                raise ValueError(
                    "One of `gcs_source_uris` or `bigquery_source_uri` must be provided."
                )

            if gcs_source_uris and bigquery_source_uri:
                raise ValueError(
                    "Exactly one of `gcs_source_uris` or `bigquery_source_uri` must be provided, but not both."
                )

            if isinstance(gcs_source_uris, str):
                gcs_source_uris = [gcs_source_uris]

            if bigquery_source_uri is not None and not isinstance(
                bigquery_source_uri, str
            ):
                raise ValueError("The provided `bigquery_source_uri` must be a string.")

            if bigquery_source_uri is not None and not bigquery_destination_output_uri:
                raise ValueError(
                    "`bigquery_destination_output_uri` must be provided if `bigquery_source_uri` is used as the data source."
                )

            if gcs_source_uris is not None and not gcs_source_uris[0].startswith(
                "gs://"
            ):
                raise ValueError("`gcs_source_uris` must start with 'gs://'.")

            if bigquery_source_uri is not None and not bigquery_source_uri.startswith(
                "bq://"
            ):
                raise ValueError(
                    "`bigquery_source_uri` and `bigquery_destination_output_uri` must start with 'bq://'"
                )

            if (
                bigquery_destination_output_uri is not None
                and not bigquery_destination_output_uri.startswith("bq://")
            ):
                raise ValueError(
                    "`bigquery_source_uri` and `bigquery_destination_output_uri` must start with 'bq://'"
                )

        SUPPORTED_INSTANCES_FORMAT_FILE_EXTENSIONS = [".jsonl", ".csv"]

        if not evaluation_staging_path and initializer.global_config.staging_bucket:
            evaluation_staging_path = initializer.global_config.staging_bucket
        elif (
            not evaluation_staging_path and not initializer.global_config.staging_bucket
        ):
            raise ValueError(
                "Please provide `evaluation_staging_bucket` when calling evaluate or set one using aiplatform.init(staging_bucket=...)"
            )

        if gcs_source_uris:

            data_file_path_obj = pathlib.Path(gcs_source_uris[0])

            data_file_extension = data_file_path_obj.suffix
            if data_file_extension not in SUPPORTED_INSTANCES_FORMAT_FILE_EXTENSIONS:
                _LOGGER.warning(
                    f"Only the following data file extensions are currently supported: '{SUPPORTED_INSTANCES_FORMAT_FILE_EXTENSIONS}'"
                )
            else:
                instances_format = data_file_extension[1:]

        elif bigquery_source_uri:
            instances_format = "bigquery"

        if (
            model_type == "other"
            and prediction_type == "classification"
            and class_labels is None
        ):
            raise ValueError(
                "Please provide `class_labels` when running evaluation on a custom classification model."
            )

        # TODO: make sure this treats each dict as a separate slice spec
        slice_configs = []
        if sliced_metrics_config:
            for slice_config in sliced_metrics_config:
                slice_config_proto = {}
                for feature_name, slice_value in slice_config.items():
                    if type(slice_value) == dict:
                        if (
                            "range" in slice_value
                            and type(slice_value["range"]) == list
                            and len(slice_value["range"]) == 2
                        ):
                            range_low = slice_value["range"][0]
                            range_high = slice_value["range"][1]

                            gapic_slice_range = gca_model_evaluation_slice_compat.ModelEvaluationSlice.Slice.SliceSpec.Range(
                                low=range_low, high=range_high
                            )
                            slice_config_proto[
                                feature_name
                            ] = gca_model_evaluation_slice_compat.ModelEvaluationSlice.Slice.SliceSpec.SliceConfig(
                                range_=gapic_slice_range
                            )
                        else:
                            raise ValueError(
                                "If a dictionary is provided for a feature's slice config, the dictionary must have a single key named 'range'. The value must be a 2-element list of ints or floats indicating the low (inclusive) and high (exclusive) values for the feature's slice range."
                            )

                    elif type(slice_value) == str:
                        if slice_value == "all_values":
                            slice_config_proto[
                                feature_name
                            ] = gca_model_evaluation_slice_compat.ModelEvaluationSlice.Slice.SliceSpec.SliceConfig(
                                all_values=True
                            )
                        else:
                            gapic_slice_value = gca_model_evaluation_slice_compat.ModelEvaluationSlice.Slice.SliceSpec.Value(
                                string_value=slice_value
                            )
                            slice_config_proto[
                                feature_name
                            ] = gca_model_evaluation_slice_compat.ModelEvaluationSlice.Slice.SliceSpec.SliceConfig(
                                value=gapic_slice_value
                            )
                    elif type(slice_value) == int or type(slice_value) == float:
                        gapic_slice_value = gca_model_evaluation_slice_compat.ModelEvaluationSlice.Slice.SliceSpec.Value(
                            float_value=slice_value
                        )
                        slice_config_proto[
                            feature_name
                        ] = gca_model_evaluation_slice_compat.ModelEvaluationSlice.Slice.SliceSpec.SliceConfig(
                            value=gapic_slice_value
                        )
                    else:
                        raise ValueError(
                            "The slice config for each feature must be either a dict with a 'range' key, string, int, float, or True."
                        )
                slice_configs.append(
                    gca_model_evaluation_slice_compat.ModelEvaluationSlice.Slice.SliceSpec(
                        configs=slice_config_proto
                    )
                )

        return model_evaluation._ModelEvaluationJob.submit(
            model_name=self.versioned_resource_name,
            prediction_type=prediction_type,
            target_field_name=target_field_name,
            gcs_source_uris=gcs_source_uris,
            bigquery_source_uri=bigquery_source_uri,
            batch_predict_bigquery_destination_output_uri=bigquery_destination_output_uri,
            class_labels=class_labels,
            prediction_label_column=prediction_label_column,
            prediction_score_column=prediction_score_column,
            sliced_metrics_config=slice_configs,
            service_account=service_account,
            pipeline_root=evaluation_staging_path,
            model_type=model_type,
            generate_feature_attributions=generate_feature_attributions,
            evaluation_pipeline_display_name=evaluation_pipeline_display_name,
            evaluation_metrics_display_name=evaluation_metrics_display_name,
            network=network,
            encryption_spec_key_name=encryption_spec_key_name,
            credentials=self.credentials,
            experiment=experiment,
            enable_error_analysis=enable_error_analysis,
            test_dataset_resource_name=test_dataset_resource_name,
            test_dataset_annotation_set_name=test_dataset_annotation_set_name,
            training_dataset_resource_name=training_dataset_resource_name,
            training_dataset_annotation_set_name=training_dataset_annotation_set_name,
            test_dataset_storage_source_uris=test_dataset_storage_source_uris,
            training_dataset_storage_source_uris=training_dataset_storage_source_uris,
            instances_format=instances_format,
            batch_predict_predictions_format=batch_predict_predictions_format,
            batch_predict_machine_type=batch_predict_machine_type,
            batch_predict_starting_replica_count=batch_predict_starting_replica_count,
            batch_predict_max_replica_count=batch_predict_max_replica_count,
            batch_predict_accelerator_type=batch_predict_accelerator_type,
            batch_predict_accelerator_count=batch_predict_accelerator_count,
            dataflow_machine_type=dataflow_machine_type,
            dataflow_max_num_workers=dataflow_max_num_workers,
            dataflow_disk_size_gb=dataflow_disk_size_gb,
            dataflow_service_account=dataflow_service_account,
            dataflow_subnetwork=dataflow_subnetwork,
            dataflow_use_public_ips=dataflow_use_public_ips,
        )
