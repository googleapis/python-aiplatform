# Copyright 2026 Google LLC
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

import os
from typing import Dict, List, Optional, Sequence, Tuple, Union

from google.cloud.aiplatform import v1 as aip_types

def _update_deployment_spec_with_env_vars_dict_or_raise(
    deployment_spec: aip_types.ReasoningEngineSpec.DeploymentSpec,
    env_vars: Dict[str, Union[str, aip_types.SecretRef]],
):
    """Updates deployment spec with environment variables from a dictionary."""
    for key, value in env_vars.items():
        if isinstance(value, str):
            deployment_spec.env.append(aip_types.EnvVar(name=key, value=value))
        elif isinstance(value, aip_types.SecretRef):
            deployment_spec.secret_env.append(
                aip_types.ReasoningEngineSpec.DeploymentSpec.SecretEnvVar(
                    name=key, secret_ref=value
                )
            )
        else:
            raise TypeError(
                f"env_vars values must be a string or SecretRef, but got {type(value)}."
            )

def _update_deployment_spec_with_env_vars_list_or_raise(
    deployment_spec: aip_types.ReasoningEngineSpec.DeploymentSpec,
    env_vars: Sequence[str],
):
    """Updates deployment spec with environment variables from a list."""
    for key in env_vars:
        if key not in os.environ:
            raise ValueError(f"Environment variable '{key}' not found in os.environ.")
        deployment_spec.env.append(aip_types.EnvVar(name=key, value=os.environ[key]))

def _generate_deployment_spec_or_raise(
    *,
    env_vars: Optional[
        Union[Sequence[str], Dict[str, Union[str, aip_types.SecretRef]]]
    ] = None,
    psc_interface_config: Optional[aip_types.PscInterfaceConfig] = None,
    min_instances: Optional[int] = None,
    max_instances: Optional[int] = None,
    resource_limits: Optional[Dict[str, str]] = None,
    container_concurrency: Optional[int] = None,
) -> Tuple[aip_types.ReasoningEngineSpec.DeploymentSpec, List[str]]:
    """Generates a DeploymentSpec based on the provided parameters."""
    deployment_spec = aip_types.ReasoningEngineSpec.DeploymentSpec()
    update_masks = []
    if env_vars:
        deployment_spec.env = []
        deployment_spec.secret_env = []
        if isinstance(env_vars, dict):
            _update_deployment_spec_with_env_vars_dict_or_raise(
                deployment_spec=deployment_spec,
                env_vars=env_vars,
            )
        elif isinstance(env_vars, (list, tuple)):
            _update_deployment_spec_with_env_vars_list_or_raise(
                deployment_spec=deployment_spec,
                env_vars=env_vars,
            )
        else:
            raise TypeError(
                f"env_vars must be a list, tuple or a dict, but got {type(env_vars)}."
            )
        if deployment_spec.env:
            update_masks.append("spec.deployment_spec.env")
        if deployment_spec.secret_env:
            update_masks.append("spec.deployment_spec.secret_env")
    if psc_interface_config:
        deployment_spec.psc_interface_config = psc_interface_config
        update_masks.append("spec.deployment_spec.psc_interface_config")
    if min_instances is not None:
        deployment_spec.min_instances = min_instances
        update_masks.append("spec.deployment_spec.min_instances")
    if max_instances is not None:
        deployment_spec.max_instances = max_instances
        update_masks.append("spec.deployment_spec.max_instances")
    if resource_limits:
        deployment_spec.resource_limits = resource_limits
        update_masks.append("spec.deployment_spec.resource_limits")
    if container_concurrency is not None:
        deployment_spec.container_concurrency = container_concurrency
        update_masks.append("spec.deployment_spec.container_concurrency")
    return deployment_spec, update_masks
