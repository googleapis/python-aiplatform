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

from __future__ import annotations
import itertools
from typing import (
    Optional,
    Sequence,
)

from google.auth import credentials as auth_credentials
import proto

from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.services import (
    deployment_resource_pool_service_client_v1beta1,
)
from google.cloud.aiplatform.compat.types import (
    deployed_model_ref_v1beta1 as gca_deployed_model_ref_compat,
    deployment_resource_pool_v1beta1 as gca_deployment_resource_pool_compat,
    machine_resources_v1beta1 as gca_machine_resources_compat,
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
        metadata: Sequence[tuple[str, str]] = (),
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
        metadata: Sequence[tuple[str, str]] = (),
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
    ) -> list[gca_deployed_model_ref_compat.DeployedModelRef]:
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
    ) -> list["models.DeploymentResourcePool"]:
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

    @classmethod
    def _construct_sdk_resource_from_gapic(
        cls,
        gapic_resource: proto.Message,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "models.DeploymentResourcePool":
        drp = cls._empty_constructor(
            project=project, location=location, credentials=credentials
        )
        drp._gca_resource = gapic_resource
        return drp
