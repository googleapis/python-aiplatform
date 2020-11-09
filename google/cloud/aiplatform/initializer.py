# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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
from typing import Optional, Type

from google.api_core import client_options
import google.auth
from google.auth import credentials as auth_credentials
from google.auth.exceptions import GoogleAuthError
from google.cloud.aiplatform import utils


class _Config:
    """Stores common parameters and options for API calls."""

    def __init__(self):
        self._project = None
        self._experiment = None
        self._location = None
        self._staging_bucket = None
        self._credentials = None

    def init(
        self,
        *,
        project: Optional[str] = None,
        location: Optional[str] = None,
        experiment: Optional[str] = None,
        staging_bucket: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Updates common initalization parameters with provided options.

        Args:
            project (str): The default project to use when making API calls.
            location (str): The default location to use when making API calls. If not
                set defaults to us-central-1
            experiment (str): The experiment to assign
            staging_bucket (str): The default staging bucket to use to stage artifacts
                when making API calls. In the form gs://...
            credentials (google.auth.crendentials.Crendentials): The default custom
                credentials to use when making API calls. If not provided crendentials
                will be ascertained from the environment.
        """
        if project:
            self._project = project
        if location:
            utils.validate_region(location)
            self._location = location
        if experiment:
            logging.warning("Experiments currently not supported.")
            self._experiment = experiment
        if staging_bucket:
            self._staging_bucket = staging_bucket
        if credentials:
            self._credentials = credentials

    @property
    def project(self) -> str:
        """Default project."""
        if self._project:
            return self._project

        project_not_found_exception_str = (
            "Unable to find your project. Please provide a project ID by:"
            "\n- Passing a constructor argument"
            "\n- Using aiplatform.init()"
            "\n- Setting a GCP environment variable"
        )

        try:
            _, project_id = google.auth.default()
        except GoogleAuthError:
            raise GoogleAuthError(project_not_found_exception_str)

        if not project_id:
            raise ValueError(project_not_found_exception_str)

        return project_id

    @property
    def location(self) -> str:
        """Default location."""
        return self._location or utils.DEFAULT_REGION

    @property
    def experiment(self) -> Optional[str]:
        """Default experiment, if provided."""
        return self._experiment

    @property
    def staging_bucket(self) -> Optional[str]:
        """Default staging bucket, if provided."""
        return self._staging_bucket

    @property
    def credentials(self) -> Optional[auth_credentials.Credentials]:
        """Default credentials, if provided."""
        return self._credentials

    def get_client_options(
        self, location_override: Optional[str] = None, prediction_client: bool = False,
    ) -> client_options.ClientOptions:
        """Creates GAPIC client_options using location and type.

        Args:
            location_override (str):
                Set this parameter to get client options for a location different from
                location set by initializer. Must be a GCP region supported by AI
                Platform (Unified).

            prediction_client (bool):
                True if service client is a PredictionServiceClient, otherwise defaults
                to False. This is used to provide a prediction-specific API endpoint.

        Returns:
            clients_options (dict):
                A dictionary containing client_options with one key, for example
                { "api_endpoint": "us-central1-aiplatform.googleapis.com" } or
                { "api_endpoint": "asia-east1-prediction-aiplatform.googleapis.com" }
        """
        if not (self.location or location_override):
            raise ValueError(
                "No location found. Provide or initialize SDK with a location."
            )

        region = location_override or self.location
        region = region.lower()
        prediction = "prediction-" if prediction_client else ""

        utils.validate_region(region)

        return client_options.ClientOptions(
            api_endpoint=f"{region}-{prediction}{utils.PROD_API_ENDPOINT}"
        )

    def common_location_path(
        self, project: Optional[str] = None, location: Optional[str] = None
    ) -> str:
        """Get parent resource with optional project and location override.

        Args:
            project (str): GCP project. If not provided will use the current project.
            location (str): Location. If not provided will use the current location.
        Returns:
            resource_parent: Formatted parent resource string.
        """
        if location:
            utils.validate_region(location)

        return "/".join(
            [
                "projects",
                project or self.project,
                "locations",
                location or self.location,
            ]
        )

    def create_client(
        self,
        client_class: Type[utils.AiPlatformServiceClient],
        credentials: Optional[auth_credentials.Credentials] = None,
        location_override: Optional[str] = None,
        prediction_client: bool = False,
    ) -> utils.AiPlatformServiceClient:
        """Instantiates a given AiPlatformServiceClient with optional overrides.

        Args:
            client_class (utils.AiPlatformServiceClient):
                (Required)An AI Platform Service Client.
            credentials (auth_credentials.Credentials):
                Custom auth credentials. If not provided will use the current config.
            location_override (str): Optional location override.
            prediction_client (str): Optional flag to use a prediction endpoint.
        Returns:
            client: Instantiated AI Platform Service client
        """

        # TODO(b/171202993) add user agent
        return client_class(
            credentials=credentials or self.credentials,
            client_options=self.get_client_options(
                location_override=location_override, prediction_client=prediction_client
            ),
        )


# global config to store init parameters: ie, aiplatform.init(project=..., location=...)
global_config = _Config()
