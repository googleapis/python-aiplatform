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
"""Classes for online prediction."""
import json
import requests
from typing import Dict, List, Optional

from google.auth import credentials as auth_credentials
from google.auth.transport import requests as google_auth_requests
from google.cloud.aiplatform import base
from google.cloud.aiplatform import constants
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import _explanation_utils
from google.cloud.aiplatform import models as aiplatform_models
from google.protobuf import json_format


_LOGGER = base.Logger(__name__)

_RAW_PREDICT_DEPLOYED_MODEL_ID_KEY = "X-Vertex-AI-Deployed-Model-Id"
_RAW_PREDICT_MODEL_RESOURCE_KEY = "X-Vertex-AI-Model"
_RAW_PREDICT_MODEL_VERSION_ID_KEY = "X-Vertex-AI-Model-Version-Id"

Prediction = aiplatform_models.Prediction


class Predictor:
    """Performs online prediction."""

    def __init__(
        self,
        endpoint_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Initializes a Predictor.

        Args:
            endpoint_name (str):
                Required. A fully-qualified endpoint resource name.
                Examples:
                * "projects/123/locations/us-central1/endpoints/456".
                * "publishers/google/models/text-bison".
                * "projects/123/locations/us-central1/publishers/google/models/text-bison".
            project (str):
                Optional. Project to retrieve endpoint or model from.
                If not set, project set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve endpoint or model from.
                If not set, location set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use when calling the API.
                Overrides credentials set in aiplatform.init.
        """
        resource_name_parts = utils.extract_project_and_location_from_parent(
            endpoint_name
        )
        resource_project = resource_name_parts.get("project")
        resource_location = resource_name_parts.get("location")
        if resource_project:
            self.project = resource_project
            if project and project != resource_project:
                raise ValueError(
                    f"Specified project {project} is different from the resource project {resource_project}."
                )
        else:
            self.project = project or initializer.global_config.project

        if resource_location:
            self.location = resource_location
            if location and location != resource_location:
                raise ValueError(
                    f"Specified location {location} is different from the resource location {resource_location}."
                )
        else:
            self.location = location or initializer.global_config.location

        if not resource_name_parts:
            endpoint_name = (
                f"projects/{self.project}/locations/{self.location}/" + endpoint_name
            )

        self.credentials = credentials or initializer.global_config.credentials
        self.resource_name = endpoint_name

        self._full_endpoint_resource_name = endpoint_name

        self._prediction_client = initializer.global_config.create_client(
            client_class=utils.PredictionClientWithOverride,
            credentials=self.credentials,
            location_override=self.location,
            prediction_client=True,
        )
        self.authorized_session = None
        self.raw_predict_request_url = None

    def predict(
        self,
        instances: List,
        parameters: Optional[Dict] = None,
        timeout: Optional[float] = None,
        use_raw_predict: Optional[bool] = False,
    ) -> Prediction:
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
            timeout (float): Optional. The timeout for this request in seconds.
            use_raw_predict (bool):
                Optional. Default value is False. If set to True, the underlying
                prediction call will be made against Endpoint.raw_predict().

        Returns:
            prediction (aiplatform.Prediction):
                Prediction with returned predictions and Model ID.
        """
        # self.wait()
        if use_raw_predict:
            raw_predict_response = self.raw_predict(
                body=json.dumps({"instances": instances, "parameters": parameters}),
                headers={"Content-Type": "application/json"},
            )
            json_response = raw_predict_response.json()
            return Prediction(
                predictions=json_response["predictions"],
                deployed_model_id=raw_predict_response.headers.get(
                    _RAW_PREDICT_DEPLOYED_MODEL_ID_KEY, ""
                ),
                model_resource_name=raw_predict_response.headers.get(
                    _RAW_PREDICT_MODEL_RESOURCE_KEY, None
                ),
                model_version_id=raw_predict_response.headers.get(
                    _RAW_PREDICT_MODEL_VERSION_ID_KEY, None
                ),
            )
        else:
            prediction_response = self._prediction_client.predict(
                endpoint=self._full_endpoint_resource_name,
                instances=instances,
                parameters=parameters,
                timeout=timeout,
            )

            return Prediction(
                predictions=[
                    json_format.MessageToDict(item)
                    for item in prediction_response.predictions.pb
                ],
                deployed_model_id=prediction_response.deployed_model_id,
                model_version_id=prediction_response.model_version_id,
                model_resource_name=prediction_response.model,
            )

    def raw_predict(
        self, body: bytes, headers: Dict[str, str]
    ) -> requests.models.Response:
        """Makes a prediction request using arbitrary headers.

        Example usage:
            my_endpoint = aiplatform.Endpoint(ENDPOINT_ID)
            response = my_endpoint.raw_predict(
                body = b'{"instances":[{"feat_1":val_1, "feat_2":val_2}]}'
                headers = {'Content-Type':'application/json'}
            )
            status_code = response.status_code
            results = json.dumps(response.text)

        Args:
            body (bytes):
                The body of the prediction request in bytes. This must not exceed 1.5 mb per request.
            headers (Dict[str, str]):
                The header of the request as a dictionary. There are no restrictions on the header.

        Returns:
            A requests.models.Response object containing the status code and prediction results.
        """
        if not self.authorized_session:
            self.credentials._scopes = constants.base.DEFAULT_AUTHED_SCOPES
            self.authorized_session = google_auth_requests.AuthorizedSession(
                self.credentials
            )
            self.raw_predict_request_url = f"https://{self.location}-{constants.base.API_BASE_PATH}/v1/{self._full_endpoint_resource_name}:rawPredict"

        return self.authorized_session.post(
            url=self.raw_predict_request_url, data=body, headers=headers
        )

    def explain(
        self,
        instances: List[Dict],
        parameters: Optional[Dict] = None,
        deployed_model_id: Optional[str] = None,
        timeout: Optional[float] = None,
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
            timeout (float): Optional. The timeout for this request in seconds.

        Returns:
            prediction (aiplatform.Prediction):
                Prediction with returned predictions, explanations, and Model ID.
        """
        explain_response = self._prediction_client.explain(
            endpoint=self.resource_name,
            instances=instances,
            parameters=parameters,
            deployed_model_id=deployed_model_id,
            timeout=timeout,
        )

        return Prediction(
            predictions=[
                json_format.MessageToDict(item)
                for item in explain_response.predictions.pb
            ],
            deployed_model_id=explain_response.deployed_model_id,
            explanations=explain_response.explanations,
        )
