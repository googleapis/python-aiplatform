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
from concurrent import futures
import functools
import inspect
import threading
import time
from typing import Any, Callable, Optional, Sequence, Union

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import initializer


POLLING_SLEEP = 5

class FutureCache(metaclass=abc.ABCMeta):

    def __init__(self):
        # future creation is responsible for setting depedency flow
        self.__latest_future_lock = threading.Lock()
        self.__latest_future = None
        self._exception = None

    def _raise_future_exception(self):
        with self.__latest_future_lock:
            if self._exception:
                raise self._exception

    def _complete_future(self, future):
        with self.__latest_future_lock:
            try:
                future.result() # raises
            except Exception as e:
                self._exception = e

            if self.__latest_future is future:
                self.__latest_future = None

    def _are_futures_done(self):
        with self.__latest_future_lock:
            return self.__latest_future is None

    def wait(self):
        while not self._are_futures_done():
            time.sleep(POLLING_SLEEP)

        self._raise_future_exception()

    @property
    def _latest_future(self):
        with self.__latest_future_lock:
            return self.__latest_future

    @_latest_future.setter
    def _latest_future(self, future: Optional[futures.Future]):
        with self.__latest_future_lock:
            self.__latest_future = future
            if future:
                future.add_done_callback(self._complete_future)

    @_latest_future.deleter
    def _latest_future(self):
        with self.__latest_future_lock:
            self.__latest_future = None


    def _submit(self,
        fn: Callable,
        args: Sequence,
        kwargs: dict,
        additional_dependencies: Optional[Sequence[futures.Future]]=None,
        callbacks: Optional[Sequence[Callable[[futures.Future], Any]]] =None,
        bind_future_to_self: bool=True):

        def wait_for_dependencies_and_invoke(deps, fn, args, kwargs):
            while True:
                if all(dep.done() for dep in deps):
                    break
                # unblock this thread
                time.sleep(POLLING_SLEEP)

            # check for raised exceptions before moving forward
            for dep in deps:
                dep.result()

            return fn(*args, **kwargs)

        # Retrieves any dependencies from arguments.
        deps = [arg._latest_future for arg in list(args) + list(kwargs.values()) if
                isinstance(arg, FutureCache) and arg._latest_future]

        if additional_dependencies:
            deps.extend(additional_dependencies)

        with self.__latest_future_lock:

            # If this instance already has a future, add that future as a dependency

            if self.__latest_future:
                deps.append(self.__latest_future)


            future = initializer.global_pool.submit(wait_for_dependencies_and_invoke,
                deps=deps, fn=fn, args=args, kwargs=kwargs)

            if bind_future_to_self:
                self.__latest_future = future

        if bind_future_to_self:
            # Clean up callback captures exception as well as removes future.
            future.add_done_callback(self._complete_future)

        if callbacks:
            for c in callbacks:
                future.add_done_callback(c)

        return future

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


class AiPlatformResourceNounWithFuture(AiPlatformResourceNoun, FutureCache):

    def __init__(self, project, location, credentials):
        AiPlatformResourceNoun.__init__(self, project=project, location=location,
            credentials=credentials)
        FutureCache.__init__(self)

    @classmethod
    def _alternative_constructor(
            cls,
            project: Optional[str] = None,
            location: Optional[str] = None,
            credentials: Optional[auth_credentials.Credentials] = None,
        ):
        self = cls.__new__(cls)
        AiPlatformResourceNoun.__init__(self, project, location, credentials)
        FutureCache.__init__(self)
        self._gca_resource = None
        return self


def sync_future_object_with_realized(future, empty_returned_object):
    result = future.result()
    sync_attributes = ['project', 'location', 'api_client', '_gca_resource']
    optional_sync_attributes = ['_prediction_client']

    for attribute in sync_attributes:
        setattr(empty_returned_object, attribute, getattr(result, attribute))

    for attribute in optional_sync_attributes:
        value = getattr(result, attribute, None)
        if value:
            setattr(empty_returned_object, attribute, value)


def get_annotation_class(annotation):
    # typing.Optional
    if getattr(annotation, '__origin__', None) is Union:
        return annotation.__dict__['__args__'][0]
    else:
        return annotation

def optional_async_wrapper(
    predicate_return_on_arg =None, # ie: incase Model is None in TrainingJob.run
    return_input_arg=None, # pass through ie: Endpoint in Model.deploy
    bind_future_to_self=True, # set to false to not bind future Model.deploy (only need to bind to output arg)
    ):

    def optional_run_in_thread(method):

        functools.wraps(method)
        def wrapper(*args, **kwargs):
            sync = kwargs.pop('sync', True)

            if sync:
                return method(*args, **kwargs)

            callbacks=[]

            # all method should have type signatures
            return_type = get_annotation_class(
                inspect.getfullargspec(method).annotations['return'])

            # Case 1: is a classmethod that creates the object and returns it
            if args and inspect.isclass(args[0]):
                # the class method returns None then return None
                if not return_type:
                    self = None
                else:
                    # assumes classmethod is our resource noun
                    self = args[0]._alternative_constructor()
                    # sync the objects after future completes
                    callbacks.append(functools.partial(sync_future_object_with_realized,
                                                        empty_returned_object=self))

                self._submit(method, callbacks=callbacks, args=args, kwargs=kwargs)

                # we assume classmethod return an instance of itself or None
                return self

            # Case 2: is instance method and return a different class object
            self = args[0]


            # check to make sure any previous async call hasn't thrown
            if self._exception:
                raise self._exception


            # object produced by the method
            returned_object = None

            bound_args = inspect.signature(method).bind(*args, **kwargs)

            print(bound_args)

            if return_input_arg:
                returned_object = bound_args.arguments.get(return_input_arg)

            should_construct = not returned_object and ((not predicate_return_on_arg) or
                (predicate_return_on_arg and bound_args.arguments.get(predicate_return_on_arg)))

            if should_construct:
                # if this method acts on the object itself
                if return_type is not None:
                    returned_object = return_type._alternative_constructor()

                    callbacks.extend([functools.partial(
                        sync_future_object_with_realized,
                        empty_returned_object=returned_object)])

            future = self._submit(fn=method, callbacks=callbacks, args=[],
                kwargs=bound_args.arguments, bind_future_to_self=bind_future_to_self)

            if returned_object and returned_object is not self:
                returned_object._latest_future = future

            return returned_object

        return wrapper
    return optional_run_in_thread








