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
import functools
import threading
from typing import Optional

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import initializer

class AiPlatformFuture(metaclass=abc.ABCMeta):

    def __init__(self):
        # future creation is responsible for setting depedency flow
        self.__latest_future_lock = threading.Lock()
        self.__latest_future = None

    def _add_future(self, future):
        with self.__latest_future_lock:
            self.__latest_future = future

    def _clear_future(self, future):
        with self.__latest_future_lock:
            if self.__latest_future is future:
                self.__latest_future = None

    def _are_futures_done(self):
        with self.__latest_future_lock:
            return self.__latest_future is None

    def wait(self):
        while not self._are_futures_done():
            time.sleep(5)

    @property
    def _latest_future(self):
        with self.__latest_future_lock:
            return self.__latest_future

    @classmethod
    @abc.abstractmethod
    def _alternative_constructor(cls):
        pass


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



class AiPlatformResourceNounWithFuture(AiPlatformResourceNoun, AiPlatformFuture):

    @classmethod
    def _alternative_constructor(
            cls,
            project: Optional[str] = None,
            location: Optional[str] = None,
            credentials: Optional[auth_credentials.Credentials] = None,
        ):
        self = cls.__new__(cls)
        AiPlatformResourceNoun.__init__(self, project, location, credentials)
        AiPlatformFuture.__init__(self)
        self._gca_resource = None
        return self

    def _submit_with_gca_resource_sync(self, callable, *args, **kwargs):
        def copy_gca_resource(future, obj):
            result = future.result()
            obj._gca_resource = result._gca_resource

        future = initializer.global_pool.submit(callable, *args, **kwargs)
        self._add_future(future)
        future.add_done_callback(functools.partial(copy_gca_resource, obj=self))
        future.add_done_callback(self._clear_future)

    def _submit_with_dependency_on_future(self, deps, callable, *args, **kwargs):
        def wait_for_dependencies(deps, callable, *args, **kwargs):
            for dep in deps:
                deps.result()
            return callable(*args, **kwargs)

        future = initializer.global_pool.submit(wait_for_dependencies,
            deps, callable, *args, **kwargs)
        self._add_future(future)
        future.add_done_callback(self._clear_future)


    def _submit(self, callable, *args, **kwargs):
        with self.__latest_future_lock:
            deps = [self._latest_future] if self._latest_future else []
            self._submit_with_dependency_on_future(deps, callable, *args, **kwargs)
