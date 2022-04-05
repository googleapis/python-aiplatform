# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Sequence

try:
    import docker
except ImportError:
    raise ImportError(
        "Docker is not installed and is required to run containers. "
        'Please install the SDK using "pip install python-aiplatform[prediction]"'
    )

from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.utils import prediction_utils

_logger = logging.getLogger(__name__)

_DEFAULT_CONTAINER_CRED_KEY_PATH = "/tmp/keys/cred_key.json"
_ADC_ENVIRONMENT_VARIABLE = "GOOGLE_APPLICATION_CREDENTIALS"

CONTAINER_RUNNING_STATUS = "running"


def _get_adc_environment_variable():
    """Gets the value of the ADC environment variable.

    Returns:
        The value of the environment variable or None if unset.
    """
    return os.environ.get(_ADC_ENVIRONMENT_VARIABLE)


def run_prediction_container(
    serving_container_image_uri: str,
    artifact_uri: Optional[str] = None,
    serving_container_predict_route: Optional[str] = None,
    serving_container_health_route: Optional[str] = None,
    serving_container_command: Optional[Sequence[str]] = None,
    serving_container_args: Optional[Sequence[str]] = None,
    serving_container_environment_variables: Optional[Dict[str, str]] = None,
    serving_container_ports: Optional[Sequence[int]] = None,
    credential_path: Optional[str] = None,
    host_port: Optional[int] = None,
    gpu_count: Optional[int] = None,
    gpu_device_ids: Optional[List[str]] = None,
    gpu_capabilities: Optional[List[List[str]]] = None,
) -> docker.models.containers.Container:
    """Runs a prediction container locally.

    Args:
        serving_container_image_uri (str):
            Required. The URI of the Model serving container.
        artifact_uri (str):
            Optional. The Cloud Storage path to the directory containing the Model artifact
            and any of its supporting files. The AIP_STORAGE_URI environment variable will
            be set to this uri if given; otherwise, an empty string.
        serving_container_predict_route (str):
            Optional. An HTTP path to send prediction requests to the container, and
            which must be supported by it. If not specified a default HTTP path will
            be used by Vertex AI.
        serving_container_health_route (str):
            Optional. An HTTP path to send health check requests to the container, and which
            must be supported by it. If not specified a standard HTTP path will be
            used by Vertex AI.
        serving_container_command (Sequence[str]):
            Optional. The command with which the container is run. Not executed within a
            shell. The Docker image's ENTRYPOINT is used if this is not provided.
            Variable references $(VAR_NAME) are expanded using the container's
            environment. If a variable cannot be resolved, the reference in the
            input string will be unchanged. The $(VAR_NAME) syntax can be escaped
            with a double $$, ie: $$(VAR_NAME). Escaped references will never be
            expanded, regardless of whether the variable exists or not.
        serving_container_args: (Sequence[str]):
            Optional. The arguments to the command. The Docker image's CMD is used if this is
            not provided. Variable references $(VAR_NAME) are expanded using the
            container's environment. If a variable cannot be resolved, the reference
            in the input string will be unchanged. The $(VAR_NAME) syntax can be
            escaped with a double $$, ie: $$(VAR_NAME). Escaped references will
            never be expanded, regardless of whether the variable exists or not.
        serving_container_environment_variables (Dict[str, str]):
            Optional. The environment variables that are to be present in the container.
            Should be a dictionary where keys are environment variable names
            and values are environment variable values for those names.
        serving_container_ports (Sequence[int]):
            Optional. Declaration of ports that are exposed by the container. This field is
            primarily informational, it gives Vertex AI information about the
            network connections the container uses. Listing or not a port here has
            no impact on whether the port is actually exposed, any port listening on
            the default "0.0.0.0" address inside a container will be accessible from
            the network.
        credential_path (str):
            Optional. The path to the credential key that will be mounted to the container.
            If it's unset, the environment variable, GOOGLE_APPLICATION_CREDENTIALS, will
            be used if set.
        host_port (int):
            Optional. The port on the host that the port, AIP_HTTP_PORT, inside the container
            will be exposed as. If it's unset, a random host port will be assigned.
        gpu_count (int):
            Optional. Number or devices to request. Set to -1 to request all available devices.
            To use GPU, set either `gpu_count` or `gpu_device_ids`.
        gpu_device_ids (List[str]):
            Optional. List of strings for device IDs.
            To use GPU, set either `gpu_count` or `gpu_device_ids`.
        gpu_capabilities (List[List[str]]):
            Optional. List of lists of strings to request capabilities. To use GPU, you need
            to set this. The global list acts like an OR, and the sub-lists are AND. The driver
            will try to satisfy one of the sub-lists.
            Available capabilities for the NVIDIA driver can be found in
            https://github.com/NVIDIA/nvidia-container-runtime.

    Returns:
        The container object running in the background.

    Raises:
        ValueError: If artifact_uri is not a valid GCS path, or if credential_path or the file
            pointed by the environment variable GOOGLE_APPLICATION_CREDENTIALS does not exist.
        docker.errors.ImageNotFound: If the specified image does not exist.
        docker.errors.APIError: If the server returns an error.
    """
    client = docker.from_env()

    envs = (
        {key: value for key, value in serving_container_environment_variables.items()}
        if serving_container_environment_variables is not None
        else {}
    )

    port = prediction_utils.get_prediction_aip_http_port(serving_container_ports)
    envs[prediction.AIP_HTTP_PORT] = port

    envs[prediction.AIP_HEALTH_ROUTE] = serving_container_health_route
    envs[prediction.AIP_PREDICT_ROUTE] = serving_container_predict_route

    if artifact_uri is not None and not artifact_uri.startswith("gs://"):
        raise ValueError(f'artifact_uri must be a GCS path but it is "{artifact_uri}".')
    envs[prediction.AIP_STORAGE_URI] = artifact_uri if artifact_uri is not None else ""

    entrypoint = (
        serving_container_command[:] if serving_container_command is not None else []
    )
    command = serving_container_args[:] if serving_container_args is not None else []

    credential_from_adc_env = credential_path is None
    credential_path = credential_path or _get_adc_environment_variable()
    if credential_path is not None:
        credential_path_on_host = Path(credential_path).expanduser().resolve()
        if not credential_path_on_host.exists() and credential_from_adc_env:
            raise ValueError(
                f"The file from the environment variable {_ADC_ENVIRONMENT_VARIABLE} does "
                f'not exist: "{credential_path}".'
            )
        elif not credential_path_on_host.exists() and not credential_from_adc_env:
            raise ValueError(f'credential_path does not exist: "{credential_path}".')
    credential_mount_path = _DEFAULT_CONTAINER_CRED_KEY_PATH
    volumes = (
        [f"{credential_path_on_host}:{credential_mount_path}"]
        if credential_path is not None
        else []
    )
    envs[_ADC_ENVIRONMENT_VARIABLE] = credential_mount_path

    device_requests = None
    if gpu_count or gpu_device_ids or gpu_capabilities:
        device_requests = [
            docker.types.DeviceRequest(
                count=gpu_count,
                device_ids=gpu_device_ids,
                capabilities=gpu_capabilities,
            )
        ]

    container = client.containers.run(
        serving_container_image_uri,
        command=command if len(command) > 0 else None,
        entrypoint=entrypoint if len(entrypoint) > 0 else None,
        ports={port: host_port},
        environment=envs,
        volumes=volumes,
        device_requests=device_requests,
        detach=True,
    )

    return container


def print_container_logs(
    container: docker.models.containers.Container,
    start_index: Optional[int] = None,
    message: Optional[str] = None,
) -> int:
    """Prints container logs.

    Args:
        container (docker.models.containers.Container):
            Required. The container object to print the logs.
        start_index (int):
            Optional. The index of log entries to start printing.
        message (str):
            Optional. The message to be printed before printing the logs.

    Returns:
        The total number of log entries.
    """
    if message is not None:
        _logger.info(message)

    logs = container.logs().decode("utf-8").strip().split("\n")
    start_index = 0 if start_index is None else start_index
    for i in range(start_index, len(logs)):
        _logger.info(logs[i])
    return len(logs)
