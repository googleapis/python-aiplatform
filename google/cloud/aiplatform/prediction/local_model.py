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

from copy import copy

from google.cloud import aiplatform

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
