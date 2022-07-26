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
import re

from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class PredictSchemata:
    """A class holding instance, parameter and prediction schema uris.

    Args:
        instance_schema_uri (str):
            Required. Points to a YAML file stored on Google Cloud Storage
            describing the format of a single instance, which are used in
            PredictRequest.instances, ExplainRequest.instances and
            BatchPredictionJob.input_config. The schema is defined as an
            OpenAPI 3.0.2 `Schema Object.
        parameters_schema_uri (str):
            Required. Points to a YAML file stored on Google Cloud Storage
            describing the parameters of prediction and explanation via
            PredictRequest.parameters, ExplainRequest.parameters and
            BatchPredictionJob.model_parameters. The schema is defined as an
            OpenAPI 3.0.2 `Schema Object.
        prediction_schema_uri (str):
            Required. Points to a YAML file stored on Google Cloud Storage
            describing the format of a single prediction produced by this Model
            , which are returned via PredictResponse.predictions,
            ExplainResponse.explanations, and BatchPredictionJob.output_config.
            The schema is defined as an OpenAPI 3.0.2 `Schema Object.
    """

    instance_schema_uri: str
    parameters_schema_uri: str
    prediction_schema_uri: str

    def to_dict(self):
        """ML metadata schema dictionary representation of this DataClass"""
        results = {}
        results["instanceSchemaUri"] = self.instance_schema_uri
        results["parametersSchemaUri"] = self.parameters_schema_uri
        results["predictionSchemaUri"] = self.prediction_schema_uri

        return results


@dataclass
class ContainerSpec:
    """Container configuration for the model.
    Args:
        image_uri (str):
            Required. URI of the Docker image to be used as the custom
            container for serving predictions. This URI must identify an image
            in Artifact Registry or Container Registry.
        command (Sequence[str]):
            Optional. Specifies the command that runs when the container
            starts. This overrides the container's `ENTRYPOINT`.
        args (Sequence[str]):
            Optional. Specifies arguments for the command that runs when the
            container starts. This overrides the container's `CMD`
        env (Sequence[google.cloud.aiplatform_v1.types.EnvVar]):
            Optional. List of environment variables to set in the container.
            After the container starts running, code running in the container
            can read these environment variables. Additionally, the command
            and args fields can reference these variables. Later entries in
            this list can also reference earlier entries. For example, the
            following example sets the variable ``VAR_2`` to have the value
            ``foo bar``: .. code:: json [ { "name": "VAR_1", "value": "foo" },
            { "name": "VAR_2", "value": "$(VAR_1) bar" } ] If you switch the
            order of the variables in the example, then the expansion does not
            occur. This field corresponds to the ``env`` field of the
            Kubernetes Containers `v1 core API.
        ports (Sequence[google.cloud.aiplatform_v1.types.Port]):
            Optional. List of ports to expose from the container. Vertex AI
            sends any prediction requests that it receives to the first port on
            this list. Vertex AI also sends `liveness and health checks.
        predict_route (str):
            Optional. HTTP path on the container to send prediction requests
            to. Vertex AI forwards requests sent using
            projects.locations.endpoints.predict to this path on the
            container's IP address and port. Vertex AI then returns the
            container's response in the API response. For example, if you set
            this field to ``/foo``, then when Vertex AI receives a prediction
            request, it forwards the request body in a POST request to the
            ``/foo`` path on the port of your container specified by the first
            value of this ``ModelContainerSpec``'s ports field. If you don't
            specify this field, it defaults to the following value when you
            deploy this Model to an Endpoint
            /v1/endpoints/ENDPOINT/deployedModels/DEPLOYED_MODEL:predict
            The placeholders in this value are replaced as follows:
            - ENDPOINT: The last segment (following ``endpoints/``)of the
              Endpoint.name][] field of the Endpoint where this Model has
              been deployed. (Vertex AI makes this value available to your
              container code as the ```AIP_ENDPOINT_ID`` environment variable
        health_route (str):
            Optional. HTTP path on the container to send health checks to.
            Vertex AI intermittently sends GET requests to this path on the
            container's IP address and port to check that the container is
            healthy. Read more about `health checks
        display_name (str):
    """

    image_uri: str
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    env: Optional[List[Dict[str, str]]] = None
    ports: Optional[List[int]] = None
    predict_route: Optional[str] = None
    health_route: Optional[str] = None

    def to_dict(self):
        """ML metadata schema dictionary representation of this DataClass"""
        results = {}
        results["imageUri"] = self.image_uri
        if self.command:
            results["command"] = self.command
        if self.args:
            results["args"] = self.args
        if self.env:
            results["env"] = self.env
        if self.ports:
            results["ports"] = self.ports
        if self.predict_route:
            results["predictRoute"] = self.predict_route
        if self.health_route:
            results["healthRoute"] = self.health_route

        return results


def create_uri_from_resource_name(resource_name: str) -> bool:
    """Construct the service URI for a given resource_name.
    Args:
        resource_name (str):
            The name of the Vertex resource, in a form of
            projects/{project}/locations/{location}/{resource_type}/{resource_id}
    Returns:
        The resource URI in the form of:
        https://{service-endpoint}/v1/{resource_name},
        where {service-endpoint} is one of the supported service endpoints at
        https://cloud.google.com/vertex-ai/docs/reference/rest#rest_endpoints
    Raises:
        ValueError: If resource_name does not match the specified format.
    """
    # TODO: support nested resource names such as models/123/evaluations/456
    match_results = re.match(
        r"^projects\/[A-Za-z0-9-]*\/locations\/([A-Za-z0-9-]*)(\/metadataStores\/[A-Za-z0-9-]*)?(\/[A-Za-z0-9-]*\/[A-Za-z0-9-]*)+$",
        resource_name,
    )
    if not match_results:
        raise ValueError(f"Invalid resource_name format for {resource_name}.")

    location = match_results.group(1)
    return f"https://{location}-aiplatform.googleapis.com/v1/{resource_name}"
