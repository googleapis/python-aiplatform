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

import abc
from typing import Optional

import proto

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import initializer


class AiPlatformResourceNoun(metaclass=abc.ABCMeta):
    """Base class the AI Platform resource nouns.

    Subclasses require two class attributes:

    client_class: The client to instantiate to interact with this resource noun.
    _is_client_prediction_client: Flag to indicate if the client requires a prediction endpoint.

    Subclass is required to populate private attribute _gca_resource which is the
    service representation of the resource noun.
    """

    @property
    @classmethod
    @abc.abstractmethod
    def client_class(cls) -> utils.AiPlatformServiceClient:
        """Client class required to interact with resource."""
        pass

    @property
    @classmethod
    @abc.abstractmethod
    def _is_client_prediction_client(cls) -> bool:
        """Flag to indicate whether to use prediction endpoint with client."""
        pass

    @property
    @abc.abstractmethod
    def _getter_method(cls) -> str:
        """Name of getter method of client class for retrieving the resource."""
        pass

    @property
    @abc.abstractmethod
    def _resource_noun(cls) -> str:
        """Resource noun"""
        pass

    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Initializes class with project, location, and api_client.

        Args:
            project(str): Project of the resource noun.
            location(str): The location of the resource noun.
            credentials(google.auth.crendentials.Crendentials): Optional custom
                credentials to use when accessing interacting with resource noun.
        """

        self.project = project or initializer.global_config.project
        self.location = location or initializer.global_config.location

        self.api_client = self._instantiate_client(self.location, credentials)

    @classmethod
    def _instantiate_client(
        cls,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> utils.AiPlatformServiceClient:
        """Helper method to instantiate service client for resource noun.

        Args:
            project (str): Project of the resource noun.
            location (str): The location of the resource noun.
            credentials (google.auth.credentials.Credentials):
                Optional custom credentials to use when accessing interacting with
                resource noun.
        Returns:
            client (utils.AiPlatformServiceClient):
                Initialized service client for this service noun.
        """
        return initializer.global_config.create_client(
            client_class=cls.client_class,
            credentials=credentials,
            location_override=location,
            prediction_client=cls._is_client_prediction_client,
        )

    def _get_gca_resource(self, resource_name: str) -> proto.Message:
        """Returns GAPIC service representation of client class resource."""
        """
        Args:
            resource_name (str):
            Required. A fully-qualified resource name or ID.
        """

        resource_name = utils.full_resource_name(
            resource_name=resource_name,
            resource_noun=self._resource_noun,
            project=self.project,
            location=self.location,
        )

        return getattr(self.api_client, self._getter_method)(name=resource_name)

    def _sync_gca_resource(self):
        """Sync GAPIC service representation of client class resource."""

        self._gca_resource = self._get_gca_resource(resource_name=self.resource_name)

    @property
    def name(self) -> str:
        """Name of this resource."""
        return self._gca_resource.name.split("/")[-1]

    @property
    def resource_name(self) -> str:
        """Full qualified resource name."""
        return self._gca_resource.name

    @property
    def display_name(self) -> str:
        """Display name of this resource."""
        return self._gca_resource.display_name
