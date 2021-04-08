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
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Type, Union

import proto

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils


class FutureManager(metaclass=abc.ABCMeta):
    """Tracks concurrent futures against this object."""

    def __init__(self):
        self.__latest_future_lock = threading.Lock()

        # Always points to the latest future. All submitted futures will always
        # form a dependency on the latest future.
        self.__latest_future = None

        # Caches Exception of any executed future. Once one exception occurs
        # all additional futures should fail and any additional invocations will block.
        self._exception = None

    def _raise_future_exception(self):
        """Raises exception if one of the object's futures has raised."""
        with self.__latest_future_lock:
            if self._exception:
                raise self._exception

    def _complete_future(self, future: futures.Future):
        """Checks for exception of future and removes the pointer if it's still latest.

        Args:
            future (futures.Future): Required. A future to complete.
        """

        with self.__latest_future_lock:
            try:
                future.result()  # raises
            except Exception as e:
                self._exception = e

            if self.__latest_future is future:
                self.__latest_future = None

    def _are_futures_done(self) -> bool:
        """Helper method to check to all futures are complete.

        Returns:
            True if no latest future.
        """
        with self.__latest_future_lock:
            return self.__latest_future is None

    def wait(self):
        """Helper method to that blocks until all futures are complete."""
        future = self.__latest_future
        if future:
            futures.wait([future], return_when=futures.FIRST_EXCEPTION)

        self._raise_future_exception()

    @property
    def _latest_future(self) -> Optional[futures.Future]:
        """Get the latest future if it exists"""
        with self.__latest_future_lock:
            return self.__latest_future

    @_latest_future.setter
    def _latest_future(self, future: Optional[futures.Future]):
        """Optionally set the latest future and add a complete_future callback."""
        with self.__latest_future_lock:
            self.__latest_future = future
        if future:
            future.add_done_callback(self._complete_future)

    def _submit(
        self,
        method: Callable[..., Any],
        args: Sequence[Any],
        kwargs: Dict[str, Any],
        additional_dependencies: Optional[Sequence[futures.Future]] = None,
        callbacks: Optional[Sequence[Callable[[futures.Future], Any]]] = None,
        internal_callbacks=None,
    ) -> futures.Future:
        """Submit a method as a future against this object.

        Args:
            method (Callable): Required. The method to submit.
            args (Sequence): Required. The arguments to call the method with.
            kwargs (dict): Required. The keyword arguments to call the method with.
            additional_dependencies (Optional[Sequence[futures.Future]]):
                Optional. Additional dependent futures to wait on before executing
                method. Note: No validation is done on the dependencies.
            callbacks (Optional[Sequence[Callable[[futures.Future], Any]]]):
                Optional. Additional Future callbacks to execute once this created
                Future is complete.

        Returns:
            future (Future): Future of the submitted method call.
        """

        def wait_for_dependencies_and_invoke(
            deps: Sequence[futures.Future],
            method: Callable[..., Any],
            args: Sequence[Any],
            kwargs: Dict[str, Any],
            internal_callbacks: Callable[[Any], Any],
        ) -> Any:
            """Wrapper method to wait on any dependencies before submitting method.

            Args:
                deps (Sequence[futures.Future]):
                    Required. Dependent futures to wait on before executing method.
                    Note: No validation is done on the dependencies.
                method (Callable): Required. The method to submit.
                args (Sequence[Any]): Required. The arguments to call the method with.
                kwargs (Dict[str, Any]):
                    Required. The keyword arguments to call the method with.
                internal_callbacks: (Callable[[Any], Any]):
                    Callbacks that take the result of method.

            """

            for future in set(deps):
                future.result()

            result = method(*args, **kwargs)

            # call callbacks from within future
            if internal_callbacks:
                for callback in internal_callbacks:
                    callback(result)

            return result

        # Retrieves any dependencies from arguments.
        deps = [
            arg._latest_future
            for arg in list(args) + list(kwargs.values())
            if isinstance(arg, FutureManager)
        ]

        # filter out objects that do not have pending tasks
        deps = [dep for dep in deps if dep]

        if additional_dependencies:
            deps.extend(additional_dependencies)

        with self.__latest_future_lock:

            # form a dependency on the latest future of this object
            if self.__latest_future:
                deps.append(self.__latest_future)

            self.__latest_future = initializer.global_pool.submit(
                wait_for_dependencies_and_invoke,
                deps=deps,
                method=method,
                args=args,
                kwargs=kwargs,
                internal_callbacks=internal_callbacks,
            )

            future = self.__latest_future

        # Clean up callback captures exception as well as removes future.
        # May execute immediately and take lock.

        future.add_done_callback(self._complete_future)

        if callbacks:
            for c in callbacks:
                future.add_done_callback(c)

        return future

    @classmethod
    @abc.abstractmethod
    def _empty_constructor(cls) -> "FutureManager":
        """Should construct object with all non FutureManager attributes as None"""
        pass

    @abc.abstractmethod
    def _sync_object_with_future_result(self, result: "FutureManager"):
        """Should sync the object from _empty_constructor with result of future."""

    def __repr__(self) -> str:
        if self._exception:
            return f"{object.__repr__(self)} failed with {str(self._exception)}"

        if self.__latest_future:
            return f"{object.__repr__(self)} is waiting for upstream dependencies to complete."

        return object.__repr__(self)


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
    def client_class(cls) -> Type[utils.AiPlatformServiceClientWithOverride]:
        """Client class required to interact with resource with optional overrides."""
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
    def _delete_method(cls) -> str:
        """Name of delete method of client class for deleting the resource."""
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
        resource_name: Optional[str] = None,
    ):
        """Initializes class with project, location, and api_client.

        Args:
            project(str): Project of the resource noun.
            location(str): The location of the resource noun.
            credentials(google.auth.crendentials.Crendentials): Optional custom
                credentials to use when accessing interacting with resource noun.
            resource_name(str): A fully-qualified resource name or ID.
        """

        if resource_name:
            project, location = self._get_and_validate_project_location(
                resource_name=resource_name, project=project, location=location
            )

        self.project = project or initializer.global_config.project
        self.location = location or initializer.global_config.location
        self.credentials = credentials or initializer.global_config.credentials

        self.api_client = self._instantiate_client(self.location, self.credentials)

    @classmethod
    def _instantiate_client(
        cls,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> utils.AiPlatformServiceClientWithOverride:
        """Helper method to instantiate service client for resource noun.

        Args:
            location (str): The location of the resource noun.
            credentials (google.auth.credentials.Credentials):
                Optional custom credentials to use when accessing interacting with
                resource noun.
        Returns:
            client (utils.AiPlatformServiceClientWithOverride):
                Initialized service client for this service noun with optional overrides.
        """
        return initializer.global_config.create_client(
            client_class=cls.client_class,
            credentials=credentials,
            location_override=location,
            prediction_client=cls._is_client_prediction_client,
        )

    def _get_and_validate_project_location(
        self,
        resource_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Tuple:

        """Validate the project and location for the resource.

        Args:
            resource_name(str): Required. A fully-qualified resource name or ID.
            project(str): Project of the resource noun.
            location(str): The location of the resource noun.

        Raises:
            RuntimeError if location is different from resource location
        """

        if not project and not location:
            return project, location

        fields = utils.extract_fields_from_resource_name(
            resource_name, self._resource_noun
        )
        if not fields:
            return project, location

        if location and fields.location != location:
            raise RuntimeError(
                f"location {location} is provided, but different from "
                f"the resource location {fields.location}"
            )

        return fields.project, fields.location

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

    def __repr__(self) -> str:
        return f"{object.__repr__(self)} \nresource name: {self.resource_name}"


def optional_sync(
    construct_object_on_arg: Optional[str] = None,
    return_input_arg: Optional[str] = None,
    bind_future_to_self: bool = True,
):
    """Decorator for AiPlatformResourceNounWithFutureManager with optional sync support.

    Methods with this decorator should include a "sync" argument that defaults to
    True. If called with sync=False this decorator will launch the method as a
    concurrent Future in a separate Thread.

    Note that this is only robust enough to support our current end to end patterns
    and may not be suitable for new patterns.

    Args:
        construct_object_on_arg (str):
            Optional. If provided, will only construct output object if arg is present.
            Example: If custom training does not produce a model.
        return_input_arg (str):
            Optional. If provided will return passed in argument instead of
            constructing.
            Example: Model.deploy(Endpoint) returns the passed in Endpoint
        bind_future_to_self (bool):
            Whether to add this future to the calling object.
            Example: Model.deploy(Endpoint) would be set to False because we only
            want the deployment Future to be associated with Endpoint.
    """

    def optional_run_in_thread(method: Callable[..., Any]):
        """Optionally run this method concurrently in separate Thread.

        Args:
            method (Callable[..., Any]): Method to optionally run in separate Thread.
        """

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            """Wraps method."""
            sync = kwargs.pop("sync", True)
            bound_args = inspect.signature(method).bind(*args, **kwargs)
            self = bound_args.arguments.get("self")
            calling_object_latest_future = None

            # check to see if this object has any exceptions
            if self:
                calling_object_latest_future = self._latest_future
                self._raise_future_exception()

            # if sync then wait for any Futures to complete and execute
            if sync:
                if self:
                    self.wait()
                return method(*args, **kwargs)

            # callbacks to call within the Future (in same Thread)
            internal_callbacks = []
            # callbacks to add to the Future (may or may not be in same Thread)
            callbacks = []
            # additional Future dependencies to capture
            dependencies = []

            # all methods should have type signatures
            return_type = get_annotation_class(
                inspect.getfullargspec(method).annotations["return"]
            )

            # is a classmethod that creates the object and returns it
            if args and inspect.isclass(args[0]):
                # assumes classmethod is our resource noun
                returned_object = args[0]._empty_constructor()
                self = returned_object

            else:  # instance method

                # object produced by the method
                returned_object = bound_args.arguments.get(return_input_arg)

                # if we're returning an input object
                if returned_object and returned_object is not self:

                    # make sure the input object doesn't have any exceptions
                    # from previous futures
                    returned_object._raise_future_exception()

                    # if the future will be associated with both the returned object
                    # and calling object then we need to add additional callback
                    # to remove the future from the returned object

                # if we need to construct a new empty returned object
                should_construct = not returned_object and bound_args.arguments.get(
                    construct_object_on_arg, not construct_object_on_arg
                )

                if should_construct:
                    if return_type is not None:
                        returned_object = return_type._empty_constructor()

                # if the future will be associated with both the returned object
                # and calling object then we need to add additional callback
                # to remove the future from the returned object
                if returned_object and bind_future_to_self:
                    callbacks.append(returned_object._complete_future)

            if returned_object:
                # sync objects after future completes
                internal_callbacks.append(
                    returned_object._sync_object_with_future_result
                )

            # If the future is not associated with the calling object
            # then the return object future needs to form a dependency on the
            # the latest future in the calling object.
            if not bind_future_to_self:
                if calling_object_latest_future:
                    dependencies.append(calling_object_latest_future)
                self = returned_object

            future = self._submit(
                method=method,
                callbacks=callbacks,
                internal_callbacks=internal_callbacks,
                additional_dependencies=dependencies,
                args=[],
                kwargs=bound_args.arguments,
            )

            # if the calling object is the one that submitted then add it's future
            # to the returned object
            if returned_object and returned_object is not self:
                returned_object._latest_future = future

            return returned_object

        return wrapper

    return optional_run_in_thread


class AiPlatformResourceNounWithFutureManager(AiPlatformResourceNoun, FutureManager):
    """Allows optional asynchronous calls to this AI Platform Resource Nouns."""

    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        resource_name: Optional[str] = None,
    ):
        """Initializes class with project, location, and api_client.

        Args:
            project (str): Optional. Project of the resource noun.
            location (str): Optional. The location of the resource noun.
            credentials(google.auth.crendentials.Crendentials):
                Optional. custom credentials to use when accessing interacting with
                resource noun.
            resource_name(str): A fully-qualified resource name or ID.
        """
        AiPlatformResourceNoun.__init__(
            self,
            project=project,
            location=location,
            credentials=credentials,
            resource_name=resource_name,
        )
        FutureManager.__init__(self)

    @classmethod
    def _empty_constructor(
        cls,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        resource_name: Optional[str] = None,
    ) -> "AiPlatformResourceNounWithFutureManager":
        """Initializes with all attributes set to None.

        The attributes should be populated after a future is complete. This allows
        scheduling of additional API calls before the resource is created.

        Args:
            project (str): Optional. Project of the resource noun.
            location (str): Optional. The location of the resource noun.
            credentials(google.auth.crendentials.Crendentials):
                Optional. custom credentials to use when accessing interacting with
                resource noun.
            resource_name(str): A fully-qualified resource name or ID.
        Returns:
            An instance of this class with attributes set to None.
        """
        self = cls.__new__(cls)
        AiPlatformResourceNoun.__init__(
            self,
            project=project,
            location=location,
            credentials=credentials,
            resource_name=resource_name,
        )
        FutureManager.__init__(self)
        self._gca_resource = None
        return self

    def _sync_object_with_future_result(
        self, result: "AiPlatformResourceNounWithFutureManager"
    ):
        """Populates attributes from a Future result to this object.

        Args:
            result: AiPlatformResourceNounWithFutureManager
                Required. Result of future with same type as this object.
        """
        sync_attributes = [
            "project",
            "location",
            "api_client",
            "_gca_resource",
            "credentials",
        ]
        optional_sync_attributes = ["_prediction_client"]

        for attribute in sync_attributes:
            setattr(self, attribute, getattr(result, attribute))

        for attribute in optional_sync_attributes:
            value = getattr(result, attribute, None)
            if value:
                setattr(self, attribute, value)

    @optional_sync()
    def delete(self, sync: bool = True) -> None:
        """Deletes this AI Platform resource. WARNING: This deletion is permament.

        Args:
            sync (bool):
                Whether to execute this deletion synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        """
        lro = getattr(self.api_client, self._delete_method)(name=self.resource_name)
        lro.result()

    def __repr__(self) -> str:
        if self._gca_resource:
            return AiPlatformResourceNoun.__repr__(self)

        return FutureManager.__repr__(self)


def get_annotation_class(annotation: type) -> type:
    """Helper method to retrieve type annotation.

    Args:
        annotation (type): Type hint
    """
    # typing.Optional
    if getattr(annotation, "__origin__", None) is Union:
        return annotation.__args__[0]
    else:
        return annotation
