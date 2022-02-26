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

from contextlib import contextmanager
from copy import copy
from typing import Optional

from google.cloud import aiplatform

from google.cloud.aiplatform.prediction import LocalEndpoint
from google.cloud.aiplatform.docker_utils import errors
from google.cloud.aiplatform.docker_utils import local_util
from google.cloud.aiplatform.utils import prediction_utils


class LocalModel:
    """Class that represents a local model."""

    def __init__(
        self, serving_container_spec: aiplatform.gapic.ModelContainerSpec,
    ):
        """Creates a local model instance.

        Args:
            serving_container_spec (aiplatform.gapic.ModelContainerSpec):
                Required. The container spec of the LocalModel instance.
        """
        self.serving_container_spec = serving_container_spec

    @contextmanager
    def deploy_to_local_endpoint(
        self,
        artifact_uri: Optional[str] = None,
        credential_path: Optional[str] = None,
        host_port: Optional[str] = None,
        container_ready_timeout: Optional[int] = None,
        container_ready_check_interval: Optional[int] = None,
    ):
        """Deploys the local model instance to a local endpoint.

        Args:
            artifact_uri (str):
                Optional. The path to the directory containing the Model artifact and
                any of its supporting files. Not present for AutoML Models.
            credential_path (str):
                Optional. The path to the credential key that will be mounted to the container.
                If it's unset, the environment variable, GOOGLE_APPLICATION_CREDENTIALS, will
                be used if set.
            host_port (str):
                Optional. The port on the host that the port, AIP_HTTP_PORT, inside the container
                will be exposed as. If it's unset, a random host port will be assigned.
            container_ready_timeout (int):
                Optional. The timeout in second used for starting the container or succeeding the
                first health check.
            container_ready_check_interval (int):
                Optional. The time interval in second to check if the container is ready or the
                first health check succeeds.

        Returns:
            A context manager of the local endpoint.
        """
        envs = {env.name: env.value for env in self.serving_container_spec.env}
        ports = [port.container_port for port in self.serving_container_spec.ports]

        try:
            with LocalEndpoint(
                serving_container_image_uri=self.serving_container_spec.image_uri,
                artifact_uri=artifact_uri,
                serving_container_predict_route=self.serving_container_spec.predict_route,
                serving_container_health_route=self.serving_container_spec.health_route,
                serving_container_command=self.serving_container_spec.command,
                serving_container_args=self.serving_container_spec.args,
                serving_container_environment_variables=envs,
                serving_container_ports=ports,
                credential_path=credential_path,
                host_port=host_port,
                container_ready_timeout=container_ready_timeout,
                container_ready_check_interval=container_ready_check_interval,
            ) as local_endpoint:
                yield local_endpoint
        finally:
            pass

    def get_serving_container_spec(self) -> aiplatform.gapic.ModelContainerSpec:
        """Returns the container spec for the image.

        Returns:
            The serving container spec of this local model instance.
        """
        return self.serving_container_spec

    def copy_image(self, dst_image_uri: str) -> "LocalModel":
        """Copies the image to another image uri.

        Args:
            dst_image_uri (str):
                The destination image uri to copy the image to.

        Returns:
            local model: Instantiated representation of the local model with the copied
            image.

        Raises:
            DockerError: If the command fails.
        """
        command = [
            "docker",
            "tag",
            f"{self.serving_container_spec.image_uri}",
            f"{dst_image_uri}",
        ]
        return_code = local_util.execute_command(command)
        if return_code != 0:
            errors.raise_docker_error_with_command(command, return_code)

        new_container_spec = copy(self.serving_container_spec)
        new_container_spec.image_uri = dst_image_uri

        return LocalModel(new_container_spec)

    def push_image(self):
        """Pushes the image to a registry.

        If you hit permission errors while calling this function, please refer to
        https://cloud.google.com/artifact-registry/docs/docker/authentication to set
        up the authentication.

        For Artifact Registry, the repository must be created before you are able to
        push images to it. Otherwise, you will hit the error, "Repository {REPOSITORY} not found".
        To create Artifact Registry repositories, use UI or call gcloud command. An
        example of gcloud command:
            gcloud artifacts repositories create {REPOSITORY} \
                --project {PROJECT} \
                --location {REGION} \
                --repository-format docker
        See https://cloud.google.com/artifact-registry/docs/manage-repos#create for more details.

        Raises:
            ValueError: If the image uri is not a container registry or artifact registry
                uri.
            DockerError: If the command fails.
        """
        if (
            prediction_utils.is_registry_uri(self.serving_container_spec.image_uri)
            is False
        ):
            raise ValueError(
                "The image uri must be a container registry or artifact registry "
                f"uri but it is: {self.serving_container_spec.image_uri}."
            )

        command = ["docker", "push", f"{self.serving_container_spec.image_uri}"]
        return_code = local_util.execute_command(command)
        if return_code != 0:
            errors.raise_docker_error_with_command(command, return_code)
