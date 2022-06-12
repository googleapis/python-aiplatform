# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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
from collections import namedtuple
from typing import Optional, Dict, NamedTuple, List
from dataclasses import dataclass
from google.cloud.aiplatform.metadata import artifact


@dataclass
class PredictSchemata:
    """A class holding instance, parameter and prediction schema uris.

    Args:
        instance_schema_uri (str):
            Required. Points to a YAML file stored on Google Cloud Storage describing the format of a single instance, which are used in PredictRequest.instances, ExplainRequest.instances and BatchPredictionJob.input_config. The schema is defined as an OpenAPI 3.0.2 `Schema Object.
        parameters_schema_uri (str):
            Required. Points to a YAML file stored on Google Cloud Storage describing the parameters of prediction and explanation via PredictRequest.parameters, ExplainRequest.parameters and BatchPredictionJob.model_parameters. The schema is defined as an OpenAPI 3.0.2 `Schema Object.
        prediction_schema_uri (str):
            Required. Points to a YAML file stored on Google Cloud Storage describing the format of a single prediction produced by this Model, which are returned via PredictResponse.predictions, ExplainResponse.explanations, and BatchPredictionJob.output_config. The schema is defined as an OpenAPI 3.0.2 `Schema Object.
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
            Required. URI of the Docker image to be used as the custom container for serving predictions. This URI must identify an image in Artifact Registry or Container Registry. Learn more about the `container publishing requirements
        command (Sequence[str]):
            Optional. Specifies the command that runs when the container starts. This overrides the container's `ENTRYPOINT
        args (Sequence[str]):
            Optional. Specifies arguments for the command that runs when the container starts. This overrides the container's ```CMD``
        env (Sequence[google.cloud.aiplatform_v1.types.EnvVar]):
            Optional. List of environment variables to set in the container. After the container starts running, code running in the container can read these environment variables. Additionally, the command and args fields can reference these variables. Later entries in this list can also reference earlier entries. For example, the following example sets the variable ``VAR_2`` to have the value ``foo bar``: .. code:: json [ { "name": "VAR_1", "value": "foo" }, { "name": "VAR_2", "value": "$(VAR_1) bar" } ] If you switch the order of the variables in the example, then the expansion does not occur. This field corresponds to the ``env`` field of the Kubernetes Containers `v1 core API.
        ports (Sequence[google.cloud.aiplatform_v1.types.Port]):
            Optional. List of ports to expose from the container. Vertex AI sends any prediction requests that it receives to the first port on this list. Vertex AI also sends `liveness and health checks.
        predict_route (str):
            Optional. HTTP path on the container to send prediction requests to. Vertex AI forwards requests sent using projects.locations.endpoints.predict to this path on the container's IP address and port. Vertex AI then returns the container's response in the API response. For example, if you set this field to ``/foo``, then when Vertex AI receives a prediction request, it forwards the request body in a POST request to the ``/foo`` path on the port of your container specified by the first value of this ``ModelContainerSpec``'s ports field. If you don't specify this field, it defaults to the following value when you [deploy this Model to an Endpoint][google.cloud.aiplatform.v1.EndpointService.DeployModel]: /v1/endpoints/ENDPOINT/deployedModels/DEPLOYED_MODEL:predict The placeholders in this value are replaced as follows: - ENDPOINT: The last segment (following ``endpoints/``)of the Endpoint.name][] field of the Endpoint where this Model has been deployed. (Vertex AI makes this value available to your container code as the ```AIP_ENDPOINT_ID`` environment variable
        health_route (str):
            Optional. HTTP path on the container to send health checks to. Vertex AI intermittently sends GET requests to this path on the container's IP address and port to check that the container is healthy. Read more about `health checks
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
        results["imageUri"] = self.container_image_uri
        if self.container_command:
            results["command"] = self.container_command
        if self.container_args:
            results["args"] = self.container_args
        if self.container_env:
            results["env"] = self.container_env
        if self.container_ports:
            results["ports"] = self.container_ports
        if self.container_predict_route:
            results["predictRoute"] = self.container_predict_route
        if self.container_health_route:
            results["healthRoute"] = self.container_health_route

        return results


class AnnotationSpec(NamedTuple):
    """Named Tuple used for Column header descriptions such as in Confusion Matrix."""

    id: Optional[str]
    display_name: Optional[str]


@dataclass
class ConfusionMatrix:
    """Structure representing a Confusion Matrix.

    Args:
        annotation_specs (List[annotation_spec]):
            List of column annotation specs which are a named tuppled with values
            display_name (str) and id (str)
        matrix_values (List[List[int]]):
            Optional. A 2D array of integers represeting the matrix values.
    """

    annotation_specs: Optional[List[AnnotationSpec]] = None
    matrix_values: Optional[List[List[int]]] = None

    def to_dict(self):
        """ML metadata schema dictionary representation of this DataClass"""
        results = {}
        result_annotation_specs = []
        if self.annotation_specs:
            for item in self.annotation_specs:
                annotation_spec = {}
                annotation_spec["displayName"] = item.display_name or ""
                annotation_spec["id"] = item.id or ""
                result_annotation_specs.append(annotation_spec)

        results["annotationSpecs"] = result_annotation_specs
        results["rows"] = self.matrix_values

        return results


@dataclass
class ConfidenceMetrics:
    """Structure representing a Confidence Metrics.

    Args:
        confidence_threshold (float):
            Optional. Defaults to zero.
        max_predictions (float):
            Optional. Defaults to zero.
        recall (float):
            Optional. Defaults to zero.
        precision (float):
            Optional. Defaults to zero.
        false_positive_rate (float):
            Optional. Defaults to zero.
        f1_score (float):
            Optional. Defaults to zero.
        recall_at1 (float):
            Optional. Defaults to zero.
        precision_at1 (float):
            Optional. Defaults to zero.
        false_positive_rate_at1 (float):
            Optional. Defaults to zero.
        f1_score_at1 (float):
            Optional. Defaults to zero.
        true_positive_count (float):
            Optional. Defaults to zero.
        false_positive_count (float):
            Optional. Defaults to zero.
        false_negative_count (float):
            Optional. Defaults to zero.
        true_negative_count (float):
            Optional. Defaults to zero.
    """

    confidence_threshold: Optional[float] = 0
    max_predictions: Optional[int] = 0
    recall: Optional[float] = 0
    precision: Optional[float] = 0
    false_positive_rate: Optional[float] = 0
    f1_score: Optional[float] = 0
    recall_at1: Optional[float] = 0
    precision_at1: Optional[float] = 0
    false_positive_rate_at1: Optional[float] = 0
    f1_score_at1: Optional[float] = 0
    true_positive_count: Optional[int] = 0
    false_positive_count: Optional[int] = 0
    false_negative_count: Optional[int] = 0
    true_negative_count: Optional[int] = 0

    def to_dict(self):
        """ML metadata schema dictionary representation of this DataClass"""
        results = {}
        results["confidenceThreshold"] = self.confidence_threshold
        results["maxPredictions"] = self.max_predictions
        results["recall"] = self.recall
        results["precision"] = self.precision
        results["falsePositiveRate"] = self.false_positive_rate
        results["f1Score"] = self.f1_score
        results["recallAt1"] = self.recall_at1
        results["precisionAt1"] = self.precision_at1
        results["falsePositiveRateAt1"] = self.false_positive_rate_at1
        results["f1ScoreAt1"] = self.f1_score_at1
        results["truePositiveCount"] = self.true_positive_count
        results["falsePositiveCount"] = self.false_positive_count
        results["falseNegativeCount"] = self.false_negative_count
        results["trueNegativeCount"] = self.true_negative_count
        return results


@dataclass
class ClassificationMetrics:
    """Structure representing a Classification Metrics.

    Args:
        au_prc (float):
            Optional. Defaults to zero.
        au_roc (float):
            Optional. Defaults to zero.
        log_loss (float):
            Optional. Defaults to zero.
        confidence_metrics (ConfidenceMetrics):
            An instance of ConfidenceMetrics data class.
        confusion_metrics (ConfusionMatrix):
            An instance of ConfusionMatrix data class.
    """

    au_prc: Optional[float] = 0
    au_roc: Optional[float] = 0
    log_loss: Optional[float] = 0
    confidence_metrics: ConfidenceMetrics = None
    confusion_metrics: ConfusionMatrix = None

    def to_dict(self):
        """ML metadata schema dictionary representation of this DataClass"""
        results = {}
        results["auPrc"] = self.au_prc
        results["auRoc"] = self.au_roc
        results["logLoss"] = self.log_loss
        if self.confidence_metrics:
            results["confidenceMetrics"] = [self.confidence_metrics.to_dict()]
        if self.confusion_metrics:
            results["confusionMatrix"] = self.confusion_metrics.to_dict()
        return results
