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


from concurrent import futures
import logging
import pkg_resources
import os
from typing import Optional, Type, Union

from google.api_core import client_options
from google.api_core import gapic_v1
import google.auth
from google.auth import credentials as auth_credentials
from google.auth.exceptions import GoogleAuthError

from google.cloud.aiplatform import compat
from google.cloud.aiplatform import constants
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.metadata import metadata

from google.cloud.aiplatform.compat.types import (
    encryption_spec as gca_encryption_spec_compat,
    encryption_spec_v1 as gca_encryption_spec_v1,
    encryption_spec_v1beta1 as gca_encryption_spec_v1beta1,
)


class _Config:
    """Stores common parameters and options for API calls."""

    def __init__(self):
        self._project = None
        self._location = None
        self._staging_bucket = None
        self._credentials = None
        self._encryption_spec_key_name = None

    def init(
        self,
        *,
        project: Optional[str] = None,
        location: Optional[str] = None,
        experiment: Optional[str] = None,
        experiment_description: Optional[str] = None,
        staging_bucket: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec_key_name: Optional[str] = None,
    ):
        """Updates common initialization parameters with provided options.

        Args:
            project (str): The default project to use when making API calls.
            location (str): The default location to use when making API calls. If not
                set defaults to us-central-1.
            experiment (str): The experiment name.
            experiment_description (str): The description of the experiment.
            staging_bucket (str): The default staging bucket to use to stage artifacts
                when making API calls. In the form gs://...
            credentials (google.auth.credentials.Credentials): The default custom
                credentials to use when making API calls. If not provided credentials
                will be ascertained from the environment.
            encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect a resource. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this resource and all sub-resources will be secured by this key.
        """

        # reset metadata_service config if project or location is updated.
        if (project and project != self._project) or (
            location and location != self._location
        ):
            if metadata.metadata_service.experiment_name:
                logging.info("project/location updated, reset Metadata config.")
            metadata.metadata_service.reset()

        if project:
            self._project = project
        if location:
            utils.validate_region(location)
            self._location = location
        if staging_bucket:
            self._staging_bucket = staging_bucket
        if credentials:
            self._credentials = credentials
        if encryption_spec_key_name:
            self._encryption_spec_key_name = encryption_spec_key_name

        if experiment:
            metadata.metadata_service.set_experiment(
                experiment=experiment, description=experiment_description
            )
        if experiment_description and experiment is None:
            raise ValueError(
                "Experiment name needs to be set in `init` in order to add experiment descriptions."
            )

    def get_encryption_spec(
        self,
        encryption_spec_key_name: Optional[str],
        select_version: Optional[str] = compat.DEFAULT_VERSION,
    ) -> Optional[
        Union[
            gca_encryption_spec_v1.EncryptionSpec,
            gca_encryption_spec_v1beta1.EncryptionSpec,
        ]
    ]:
        """Creates a gca_encryption_spec.EncryptionSpec instance from the given
        key name. If the provided key name is None, it uses the default key
        name if provided.

        Args:
            encryption_spec_key_name (Optional[str]): The default encryption key name to use when creating resources.
            select_version: The default version is set to compat.DEFAULT_VERSION
        """
        kms_key_name = encryption_spec_key_name or self.encryption_spec_key_name
        encryption_spec = None
        if kms_key_name:
            gca_encryption_spec = gca_encryption_spec_compat
            if select_version == compat.V1BETA1:
                gca_encryption_spec = gca_encryption_spec_v1beta1
            encryption_spec = gca_encryption_spec.EncryptionSpec(
                kms_key_name=kms_key_name
            )
        return encryption_spec

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
        return self._location or constants.DEFAULT_REGION

    @property
    def staging_bucket(self) -> Optional[str]:
        """Default staging bucket, if provided."""
        return self._staging_bucket

    @property
    def credentials(self) -> Optional[auth_credentials.Credentials]:
        """Default credentials."""
        if self._credentials:
            return self._credentials
        logger = logging.getLogger("google.auth._default")
        logging_warning_filter = utils.LoggingFilter(logging.WARNING)
        logger.addFilter(logging_warning_filter)
        credentials, _ = google.auth.default()
        logger.removeFilter(logging_warning_filter)
        return credentials

    @property
    def encryption_spec_key_name(self) -> Optional[str]:
        """Default encryption spec key name, if provided."""
        return self._encryption_spec_key_name

    def get_client_options(
        self, location_override: Optional[str] = None, prediction_client: bool = False
    ) -> client_options.ClientOptions:
        """Creates GAPIC client_options using location and type.

        Args:
            location_override (str):
                Set this parameter to get client options for a location different from
                location set by initializer. Must be a GCP region supported by AI
                Platform (Unified).
            prediction_client (str): Optional flag to use a prediction endpoint.


        Returns:
            clients_options (google.api_core.client_options.ClientOptions):
                A ClientOptions object set with regionalized API endpoint, i.e.
                { "api_endpoint": "us-central1-aiplatform.googleapis.com" } or
                { "api_endpoint": "asia-east1-aiplatform.googleapis.com" }
        """
        if not (self.location or location_override):
            raise ValueError(
                "No location found. Provide or initialize SDK with a location."
            )

        region = location_override or self.location
        region = region.lower()

        utils.validate_region(region)

        service_base_path = (
            constants.PREDICTION_API_BASE_PATH
            if prediction_client
            else constants.API_BASE_PATH
        )

        return client_options.ClientOptions(
            api_endpoint=f"{region}-{service_base_path}"
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
        client_class: Type[utils.VertexAiServiceClientWithOverride],
        credentials: Optional[auth_credentials.Credentials] = None,
        location_override: Optional[str] = None,
        prediction_client: bool = False,
    ) -> utils.VertexAiServiceClientWithOverride:
        """Instantiates a given VertexAiServiceClient with optional
        overrides.

        Args:
            client_class (utils.VertexAiServiceClientWithOverride):
                (Required) A Vertex AI Service Client with optional overrides.
            credentials (auth_credentials.Credentials):
                Custom auth credentials. If not provided will use the current config.
            location_override (str): Optional location override.
            prediction_client (str): Optional flag to use a prediction endpoint.
        Returns:
            client: Instantiated Vertex AI Service client with optional overrides
        """
        gapic_version = pkg_resources.get_distribution(
            "google-cloud-aiplatform",
        ).version
        client_info = gapic_v1.client_info.ClientInfo(
            gapic_version=gapic_version,
            user_agent=f"{constants.USER_AGENT_PRODUCT}/{gapic_version}",
        )

        kwargs = {
            "credentials": credentials or self.credentials,
            "client_options": self.get_client_options(
                location_override=location_override,
                prediction_client=prediction_client,
            ),
            "client_info": client_info,
        }

        return client_class(**kwargs)


# global config to store init parameters: ie, aiplatform.init(project=..., location=...)
global_config = _Config()

global_pool = futures.ThreadPoolExecutor(
    max_workers=min(32, max(4, (os.cpu_count() or 0) * 5))
)
