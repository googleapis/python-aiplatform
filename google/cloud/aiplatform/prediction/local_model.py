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
from pathlib import Path
from typing import Dict, Optional, Sequence, Type

from google.auth import credentials as auth_credentials

from google.cloud import aiplatform
from google.cloud.aiplatform import explain
from google.cloud.aiplatform import helpers
from google.cloud.aiplatform import models

from google.cloud.aiplatform.compat.types import (
    model as gca_model_compat,
    env_var as gca_env_var_compat,
)

from google.cloud.aiplatform.docker_utils import build
from google.cloud.aiplatform.docker_utils import errors
from google.cloud.aiplatform.docker_utils import local_util
from google.cloud.aiplatform.prediction import LocalEndpoint
from google.cloud.aiplatform.prediction.handler import Handler
from google.cloud.aiplatform.prediction.handler import PredictionHandler
from google.cloud.aiplatform.prediction.predictor import Predictor
from google.cloud.aiplatform.utils import prediction_utils

DEFAULT_PREDICT_ROUTE = "/predict"
DEFAULT_HEALTH_ROUTE = "/health"
DEFAULT_HTTP_PORT = 8080

_DEFAULT_SDK_REQUIREMENTS = [
    (
        "google-cloud-aiplatform[prediction] @ "
        "git+https://github.com/googleapis/python-aiplatform.git@custom-prediction-routine"
    )
]


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

    @classmethod
    def create(
        cls,
        serving_container_image_uri: str,
        serving_container_predict_route: Optional[str] = None,
        serving_container_health_route: Optional[str] = None,
        serving_container_command: Optional[Sequence[str]] = None,
        serving_container_args: Optional[Sequence[str]] = None,
        serving_container_environment_variables: Optional[Dict[str, str]] = None,
        serving_container_ports: Optional[Sequence[int]] = None,
    ) -> "LocalModel":
        """Creates a local model from an existing image and given container spec.

        Args:
            serving_container_image_uri (str):
                Required. The URI of the Model serving container.
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

        Returns:
            local model: Instantiated representation of the local model.
        """
        env = None
        ports = None

        if serving_container_environment_variables:
            env = [
                gca_env_var_compat.EnvVar(name=str(key), value=str(value))
                for key, value in serving_container_environment_variables.items()
            ]
        if serving_container_ports:
            ports = [
                gca_model_compat.Port(container_port=port)
                for port in serving_container_ports
            ]

        container_spec = gca_model_compat.ModelContainerSpec(
            image_uri=serving_container_image_uri,
            command=serving_container_command,
            args=serving_container_args,
            env=env,
            ports=ports,
            predict_route=serving_container_predict_route,
            health_route=serving_container_health_route,
        )

        return cls(container_spec)

    @classmethod
    def create_cpr_model(
        cls,
        src_dir: str,
        output_image_uri: str,
        predictor: Optional[Type[Predictor]] = None,
        handler: Type[Handler] = PredictionHandler,
        base_image: str = "python:3.7",
        requirements_path: Optional[str] = None,
    ) -> "LocalModel":
        """Creates a local model from a custom predictor.

        This method creates a docker image to include user-provided predictor, and handler.
        It populates the entrypoint, entrypoint.py, right under the specified directory, src_dir,
        if it doesn't exist and generates a Dockerfile to build the image.

        An example src_dir (e.g. "./user_src_dir") provided looks like:
        .
        |-- user_src_dir/
            |-- predictor.py
            |-- requirements.txt
            |-- user_code/
            |   |-- utils.py
            |   |-- custom_package.tar.gz
            |   |-- ...
            |-- ...
            |-- entrypoint.py (generated by SDK if it does not exist)

        In the built image, it will look like:
        container_workdir/
        |-- requirements.txt
        |-- user_src_dir/
            |-- predictor.py
            |-- requirements.txt
            |-- user_code/
            |   |-- utils.py
            |   |-- custom_package.tar.gz
            |   |-- ...
            |-- ...
            |-- entrypoint.py

        Note: If you want to install packages from *.tar.gz, you need to specify the
        path relative to container workdir in requirements.txt. In this case you need
        to in requirements.txt, specify `./user_src_dir/user_code/custom_package.tar.gz`.

        Args:
            src_dir (str):
                Required. The path to the local directory including all needed files such as
                predictor. The whole directory will be copied to the image.
            output_image_uri (str):
                Required. The image uri of the built image.
            predictor (Type[Predictor]):
                Optional. The custom predictor class consumed by handler to do prediction.
            handler (Type[Handler]):
                Required. The handler class to handle requests in the model server.
            base_image (str):
                Required. The base image used to build the custom images. The base image must
                have python and pip installed where the two commands `python` and `pip` must be
                available.
            requirements_path (str):
                Optional. The path to the local requirements.txt file. This file will be copied
                to the image and the needed packages listed in it will be installed.

        Returns:
            local model: Instantiated representation of the local model.
        """
        entrypoint_file = "entrypoint.py"

        prediction_utils.populate_entrypoint_if_not_exists(
            src_dir, entrypoint_file, predictor=predictor, handler=handler,
        )

        is_prebuilt_prediction_image = helpers.is_prebuilt_prediction_container_uri(
            base_image
        )
        _ = build.build_image(
            base_image,
            src_dir,
            Path(src_dir).joinpath(entrypoint_file).as_posix(),
            output_image_uri,
            requirements=_DEFAULT_SDK_REQUIREMENTS,
            requirements_path=requirements_path,
            exposed_ports=[DEFAULT_HTTP_PORT],
            pip_command="pip3" if is_prebuilt_prediction_image else "pip",
            python_command="python3" if is_prebuilt_prediction_image else "python",
        )

        container_spec = gca_model_compat.ModelContainerSpec(
            image_uri=output_image_uri,
            predict_route=DEFAULT_PREDICT_ROUTE,
            health_route=DEFAULT_HEALTH_ROUTE,
        )

        return cls(container_spec)

    def upload(
        self,
        display_name: str,
        artifact_uri: Optional[str] = None,
        description: Optional[str] = None,
        instance_schema_uri: Optional[str] = None,
        parameters_schema_uri: Optional[str] = None,
        prediction_schema_uri: Optional[str] = None,
        explanation_metadata: Optional[explain.ExplanationMetadata] = None,
        explanation_parameters: Optional[explain.ExplanationParameters] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        labels: Optional[Dict[str, str]] = None,
        encryption_spec_key_name: Optional[str] = None,
        staging_bucket: Optional[str] = None,
        sync=True,
    ) -> models.Model:
        """Uploads a model with the container spec and returns a Model
        representing the uploaded Model resource.

        Example usage:

        my_model = local_model.upload(
            display_name='my-model',
            artifact_uri='gs://my-model/saved-model'
        )

        Args:
            display_name (str):
                Required. The display name of the Model. The name can be up to 128
                characters long and can be consist of any UTF-8 characters.
            artifact_uri (str):
                Optional. The path to the directory containing the Model artifact and
                any of its supporting files. Not present for AutoML Models.
            description (str):
                The description of the model.
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
            explanation_metadata (explain.ExplanationMetadata):
                Optional. Metadata describing the Model's input and output for explanation.
                Both `explanation_metadata` and `explanation_parameters` must be
                passed together when used. For more details, see
                `Ref docs <http://tinyurl.com/1igh60kt>`
            explanation_parameters (explain.ExplanationParameters):
                Optional. Parameters to configure explaining for Model's predictions.
                For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            project (str):
                Optional. Project to upload this model to. Overrides project set in
                aiplatform.init.
            location (str):
                Optional. Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this model. Overrides credentials
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
            encryption_spec_key_name (str):
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

        Returns:
            model: Instantiated representation of the uploaded model resource.

        Raises:
            ValueError: If only `explanation_metadata` or `explanation_parameters`
                is specified.
                Also if model directory does not contain a supported model file.
        """
        envs = {env.name: env.value for env in self.serving_container_spec.env}
        ports = [port.container_port for port in self.serving_container_spec.ports]

        return models.Model.upload(
            display_name=display_name,
            serving_container_image_uri=self.serving_container_spec.image_uri,
            artifact_uri=artifact_uri,
            serving_container_predict_route=self.serving_container_spec.predict_route,
            serving_container_health_route=self.serving_container_spec.health_route,
            description=description,
            serving_container_command=self.serving_container_spec.command,
            serving_container_args=self.serving_container_spec.args,
            serving_container_environment_variables=envs,
            serving_container_ports=ports,
            instance_schema_uri=instance_schema_uri,
            parameters_schema_uri=parameters_schema_uri,
            prediction_schema_uri=prediction_schema_uri,
            explanation_metadata=explanation_metadata,
            explanation_parameters=explanation_parameters,
            project=project,
            location=location,
            credentials=credentials,
            labels=labels,
            encryption_spec_key_name=encryption_spec_key_name,
            staging_bucket=staging_bucket,
            sync=sync,
        )

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
