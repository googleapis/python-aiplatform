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
import abc
import inspect
import io
import os
import sys
import tarfile
import typing
from typing import Optional, Protocol, Sequence, Union, List

from google.api_core import exceptions
from google.cloud import storage
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils as aip_utils
from google.cloud.aiplatform_v1beta1 import types
from google.cloud.aiplatform_v1beta1.types import reasoning_engine_service
from vertexai.reasoning_engines import _utils
from google.protobuf import field_mask_pb2


_LOGGER = base.Logger(__name__)
_SUPPORTED_PYTHON_VERSIONS = ("3.8", "3.9", "3.10", "3.11")
_DEFAULT_GCS_DIR_NAME = "reasoning_engine"
_BLOB_FILENAME = "reasoning_engine.pkl"
_REQUIREMENTS_FILE = "requirements.txt"
_EXTRA_PACKAGES_FILE = "dependencies.tar.gz"


@typing.runtime_checkable
class Queryable(Protocol):
    """Protocol for Reasoning Engine applications that can be queried."""

    @abc.abstractmethod
    def query(self, **kwargs):
        """Runs the Reasoning Engine to serve the user query."""


@typing.runtime_checkable
class Cloneable(Protocol):
    """Protocol for Reasoning Engine applications that can be cloned."""

    @abc.abstractmethod
    def clone(self):
        """Return a clone of the object."""


class ReasoningEngine(base.VertexAiResourceNounWithFutureManager, Queryable):
    """Represents a Vertex AI Reasoning Engine resource."""

    client_class = aip_utils.ReasoningEngineClientWithOverride
    _resource_noun = "reasoning_engine"
    _getter_method = "get_reasoning_engine"
    _list_method = "list_reasoning_engines"
    _delete_method = "delete_reasoning_engine"
    _parse_resource_name_method = "parse_reasoning_engine_path"
    _format_resource_name_method = "reasoning_engine_path"

    def __init__(self, reasoning_engine_name: str):
        """Retrieves a Reasoning Engine resource.

        Args:
            reasoning_engine_name (str):
                Required. A fully-qualified resource name or ID such as
                "projects/123/locations/us-central1/reasoningEngines/456" or
                "456" when project and location are initialized or passed.
        """
        super().__init__(resource_name=reasoning_engine_name)
        self.execution_api_client = initializer.global_config.create_client(
            client_class=aip_utils.ReasoningEngineExecutionClientWithOverride,
        )
        self._gca_resource = self._get_gca_resource(resource_name=reasoning_engine_name)
        self._operation_schemas = None

    @property
    def resource_name(self) -> str:
        """Fully-qualified resource name."""
        return self._gca_resource.name

    @classmethod
    def create(
        cls,
        reasoning_engine: Queryable,
        *,
        requirements: Optional[Union[str, Sequence[str]]] = None,
        reasoning_engine_name: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        gcs_dir_name: str = _DEFAULT_GCS_DIR_NAME,
        sys_version: Optional[str] = None,
        extra_packages: Optional[Sequence[str]] = None,
    ) -> "ReasoningEngine":
        """Creates a new ReasoningEngine.

        The Reasoning Engine will be an instance of the `reasoning_engine` that
        was passed in, running remotely on Vertex AI.

        Sample ``src_dir`` contents (e.g. ``./user_src_dir``):

        .. code-block:: python

            user_src_dir/
            |-- main.py
            |-- requirements.txt
            |-- user_code/
            |   |-- utils.py
            |   |-- ...
            |-- ...

        To build a Reasoning Engine:

        .. code-block:: python

            remote_app = ReasoningEngine.create(
                local_app,
                requirements=[
                    # I.e. the PyPI dependencies listed in requirements.txt
                    "google-cloud-aiplatform==1.25.0",
                    "langchain==0.0.242",
                    ...
                ],
                extra_packages=[
                    "./user_src_dir/main.py", # a single file
                    "./user_src_dir/user_code", # a directory
                    ...
                ],
            )

        Args:
            reasoning_engine (ReasoningEngineInterface):
                Required. The Reasoning Engine to be created.
            requirements (Union[str, Sequence[str]]):
                Optional. The set of PyPI dependencies needed. It can either be
                the path to a single file (requirements.txt), or an ordered list
                of strings corresponding to each line of the requirements file.
            reasoning_engine_name (str):
                Optional. A fully-qualified resource name or ID such as
                "projects/123/locations/us-central1/reasoningEngines/456" or
                "456" when project and location are initialized or passed. If
                specifying the ID, it should be 4-63 characters. Valid
                characters are lowercase letters, numbers and hyphens ("-"),
                and it should start with a number or a lower-case letter. If not
                provided, Vertex AI will generate a value for this ID.
            display_name (str):
                Optional. The user-defined name of the Reasoning Engine.
                The name can be up to 128 characters long and can comprise any
                UTF-8 character.
            description (str):
                Optional. The description of the Reasoning Engine.
            gcs_dir_name (CreateReasoningEngineOptions):
                Optional. The GCS bucket directory under `staging_bucket` to
                use for staging the artifacts needed.
            sys_version (str):
                Optional. The Python system version used. Currently supports any
                of "3.8", "3.9", "3.10", "3.11". If not specified, it defaults
                to the "{major}.{minor}" attributes of sys.version_info.
            extra_packages (Sequence[str]):
                Optional. The set of extra user-provided packages (if any).

        Returns:
            ReasoningEngine: The Reasoning Engine that was created.

        Raises:
            ValueError: If `sys.version` is not supported by ReasoningEngine.
            ValueError: If the `project` was not set using `vertexai.init`.
            ValueError: If the `location` was not set using `vertexai.init`.
            ValueError: If the `staging_bucket` was not set using vertexai.init.
            ValueError: If the `staging_bucket` does not start with "gs://".
            FileNotFoundError: If `extra_packages` includes a file or directory
            that does not exist.
            IOError: If requirements is a string that corresponds to a
            nonexistent file.
        """
        if not sys_version:
            sys_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        _validate_sys_version_or_raise(sys_version)
        reasoning_engine = _validate_reasoning_engine_or_raise(reasoning_engine)
        requirements = _validate_requirements_or_raise(requirements)
        extra_packages = _validate_extra_packages_or_raise(extra_packages)

        if reasoning_engine_name:
            _LOGGER.warning(
                "ReasoningEngine does not support user-defined resource IDs at "
                f"the moment. Therefore {reasoning_engine_name=} would be "
                "ignored and a random ID will be generated instead."
            )
        sdk_resource = cls.__new__(cls)
        base.VertexAiResourceNounWithFutureManager.__init__(
            sdk_resource,
            resource_name=reasoning_engine_name,
        )
        staging_bucket = initializer.global_config.staging_bucket
        _validate_staging_bucket_or_raise(staging_bucket)
        # Prepares the Reasoning Engine for creation in Vertex AI.
        # This involves packaging and uploading the artifacts for
        # reasoning_engine, requirements and extra_packages to
        # `staging_bucket/gcs_dir_name`.
        _prepare(
            reasoning_engine=reasoning_engine,
            requirements=requirements,
            project=sdk_resource.project,
            location=sdk_resource.location,
            staging_bucket=staging_bucket,
            gcs_dir_name=gcs_dir_name,
            extra_packages=extra_packages,
        )
        # Update the package spec.
        package_spec = types.ReasoningEngineSpec.PackageSpec(
            python_version=sys_version,
            pickle_object_gcs_uri="{}/{}/{}".format(
                staging_bucket,
                gcs_dir_name,
                _BLOB_FILENAME,
            ),
        )
        if extra_packages:
            package_spec.dependency_files_gcs_uri = "{}/{}/{}".format(
                staging_bucket,
                gcs_dir_name,
                _EXTRA_PACKAGES_FILE,
            )
        if requirements:
            package_spec.requirements_gcs_uri = "{}/{}/{}".format(
                staging_bucket,
                gcs_dir_name,
                _REQUIREMENTS_FILE,
            )
        reasoning_engine_spec = types.ReasoningEngineSpec(
            package_spec=package_spec,
        )
        try:
            schema_dict = _utils.generate_schema(
                reasoning_engine.query,
                schema_name=f"{type(reasoning_engine).__name__}_query",
            )
            reasoning_engine_spec.class_methods.append(_utils.to_proto(schema_dict))
        except Exception as e:
            _LOGGER.warning(f"failed to generate schema: {e}")
        operation_future = sdk_resource.api_client.create_reasoning_engine(
            parent=initializer.global_config.common_location_path(
                project=sdk_resource.project, location=sdk_resource.location
            ),
            reasoning_engine=types.ReasoningEngine(
                name=reasoning_engine_name,
                display_name=display_name,
                description=description,
                spec=reasoning_engine_spec,
            ),
        )
        _LOGGER.log_create_with_lro(cls, operation_future)
        created_resource = operation_future.result()
        _LOGGER.log_create_complete(
            cls,
            created_resource,
            cls._resource_noun,
            module_name="vertexai.preview.reasoning_engines",
        )
        # We use `._get_gca_resource(...)` instead of `created_resource` to
        # fully instantiate the attributes of the reasoning engine.
        sdk_resource._gca_resource = sdk_resource._get_gca_resource(
            resource_name=created_resource.name
        )
        sdk_resource.execution_api_client = initializer.global_config.create_client(
            client_class=aip_utils.ReasoningEngineExecutionClientWithOverride,
            credentials=sdk_resource.credentials,
            location_override=sdk_resource.location,
        )
        sdk_resource._operation_schemas = None
        return sdk_resource

    def update(
        self,
        *,
        reasoning_engine: Optional[Queryable] = None,
        requirements: Optional[Union[str, Sequence[str]]] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        gcs_dir_name: str = _DEFAULT_GCS_DIR_NAME,
        sys_version: Optional[str] = None,
        extra_packages: Optional[Sequence[str]] = None,
    ) -> "ReasoningEngine":
        """Updates an existing ReasoningEngine.

        This method updates the configuration of an existing ReasoningEngine
        running remotely, which is identified by its resource name.
        Unlike the `create` function which requires a `reasoning_engine` object,
        all arguments in this method are optional.
        This method allows you to modify individual aspects of the configuration
        by providing any of the optional arguments.
        Note that you must provide at least one argument (except `sys_version`).

        Args:
            reasoning_engine (ReasoningEngineInterface):
                Optional. The Reasoning Engine to be replaced. If it is not
                specified, the existing Reasoning Engine will be used.
            requirements (Union[str, Sequence[str]]):
                Optional. The set of PyPI dependencies needed. It can either be
                the path to a single file (requirements.txt), or an ordered list
                of strings corresponding to each line of the requirements file.
                If it is not specified, the existing requirements will be used.
                If it is set to an empty string or list, the existing
                requirements will be removed.
            display_name (str):
                Optional. The user-defined name of the Reasoning Engine.
                The name can be up to 128 characters long and can comprise any
                UTF-8 character.
            description (str):
                Optional. The description of the Reasoning Engine.
            gcs_dir_name (CreateReasoningEngineOptions):
                Optional. The GCS bucket directory under `staging_bucket` to
                use for staging the artifacts needed.
            sys_version (str):
                Optional. The Python system version used. Currently updating
                sys version is not supported.
            extra_packages (Sequence[str]):
                Optional. The set of extra user-provided packages (if any). If
                it is not specified, the existing extra packages will be used.
                If it is set to an empty list, the existing extra packages will
                be removed.

        Returns:
            ReasoningEngine: The Reasoning Engine that was updated.

        Raises:
            ValueError: If `sys.version` is updated.
            ValueError: If the `staging_bucket` was not set using vertexai.init.
            ValueError: If the `staging_bucket` does not start with "gs://".
            FileNotFoundError: If `extra_packages` includes a file or directory
            that does not exist.
            ValueError: if none of `display_name`, `description`,
            `requirements`, `extra_packages`, or `reasoning_engine` were
            specified.
            IOError: If requirements is a string that corresponds to a
            nonexistent file.
        """
        staging_bucket = initializer.global_config.staging_bucket
        _validate_staging_bucket_or_raise(staging_bucket)

        # Validate the arguments.
        if not any(
            [
                reasoning_engine,
                requirements,
                extra_packages,
                display_name,
                description,
            ]
        ):
            raise ValueError(
                "At least one of `reasoning_engine`, `requirements`, "
                "`extra_packages`, `display_name`, or `description` must be "
                "specified."
            )
        if sys_version:
            _LOGGER.warning("Updated sys_version is not supported.")
        if requirements is not None:
            requirements = _validate_requirements_or_raise(requirements)
        if extra_packages is not None:
            extra_packages = _validate_extra_packages_or_raise(extra_packages)
        if reasoning_engine is not None:
            reasoning_engine = _validate_reasoning_engine_or_raise(reasoning_engine)

        # Prepares the Reasoning Engine for update in Vertex AI.
        # This involves packaging and uploading the artifacts for
        # reasoning_engine, requirements and extra_packages to
        # `staging_bucket/gcs_dir_name`.
        _prepare(
            reasoning_engine=reasoning_engine,
            requirements=requirements,
            project=self.project,
            location=self.location,
            staging_bucket=staging_bucket,
            gcs_dir_name=gcs_dir_name,
            extra_packages=extra_packages,
        )
        update_request = _generate_update_request_or_raise(
            resource_name=self.resource_name,
            staging_bucket=staging_bucket,
            gcs_dir_name=gcs_dir_name,
            reasoning_engine=reasoning_engine,
            requirements=requirements,
            extra_packages=extra_packages,
            display_name=display_name,
            description=description,
        )
        operation_future = self.api_client.update_reasoning_engine(
            request=update_request
        )
        _LOGGER.info(
            f"Update ReasoningEngine backing LRO: {operation_future.operation.name}"
        )
        created_resource = operation_future.result()
        _LOGGER.info(f"ReasoningEngine updated. Resource name: {created_resource.name}")
        self._operation_schemas = None
        return self

    def operation_schemas(self) -> Sequence[_utils.JsonDict]:
        """Returns the (Open)API schemas for the Reasoning Engine."""
        spec = _utils.to_dict(self._gca_resource.spec)
        if self._operation_schemas is None:
            self._operation_schemas = spec.get("class_methods", [])
        return self._operation_schemas

    def query(self, **kwargs) -> _utils.JsonDict:
        """Runs the Reasoning Engine to serve the user query.

        This will be based on the `.query(...)` method of the python object that
        was passed in when creating the Reasoning Engine.

        Args:
            **kwargs:
                Optional. The arguments of the `.query(...)` method.

        Returns:
            dict[str, Any]: The response from serving the user query.
        """
        response = self.execution_api_client.query_reasoning_engine(
            request=types.QueryReasoningEngineRequest(
                name=self.resource_name,
                input=kwargs,
            ),
        )
        output = _utils.to_dict(response)
        if "output" in output:
            return output.get("output")
        return output


def _validate_sys_version_or_raise(sys_version: str) -> None:
    """Tries to validate the python system version."""
    if sys_version not in _SUPPORTED_PYTHON_VERSIONS:
        raise ValueError(
            f"Unsupported python version: {sys_version}. ReasoningEngine "
            f"only supports {_SUPPORTED_PYTHON_VERSIONS} at the moment."
        )
    if sys_version != f"{sys.version_info.major}.{sys.version_info.minor}":
        _LOGGER.warning(
            f"{sys_version=} is inconsistent with {sys.version_info=}. "
            "This might result in issues with deployment, and should only "
            "be used as a workaround for advanced cases."
        )


def _validate_staging_bucket_or_raise(staging_bucket: str) -> str:
    """Tries to validate the staging bucket."""
    if not staging_bucket:
        raise ValueError("Please provide a `staging_bucket` in `vertexai.init(...)`")
    if not staging_bucket.startswith("gs://"):
        raise ValueError(f"{staging_bucket=} must start with `gs://`")


def _validate_reasoning_engine_or_raise(reasoning_engine: Queryable) -> Queryable:
    """Tries to validate the reasoning engine."""
    if not (hasattr(reasoning_engine, "query") and callable(reasoning_engine.query)):
        raise TypeError(
            "reasoning_engine does not have a callable method named `query`"
        )
    try:
        inspect.signature(reasoning_engine.query)
    except ValueError as err:
        raise ValueError(
            "Invalid query signature. This might be due to a missing "
            "`self` argument in the reasoning_engine.query method."
        ) from err
    if isinstance(reasoning_engine, Cloneable):
        # Avoid undeployable ReasoningChain states.
        reasoning_engine = reasoning_engine.clone()
    return reasoning_engine


def _validate_requirements_or_raise(requirements: Sequence[str]) -> Sequence[str]:
    """Tries to validate the requirements."""
    if isinstance(requirements, str):
        try:
            _LOGGER.info(f"Reading requirements from {requirements=}")
            with open(requirements) as f:
                requirements = f.read().splitlines()
                _LOGGER.info(f"Read the following lines: {requirements}")
        except IOError as err:
            raise IOError(f"Failed to read requirements from {requirements=}") from err
    return requirements or []


def _validate_extra_packages_or_raise(extra_packages: Sequence[str]) -> Sequence[str]:
    """Tries to validates the extra packages."""
    extra_packages = extra_packages or []
    for extra_package in extra_packages:
        if not os.path.exists(extra_package):
            raise FileNotFoundError(
                f"Extra package specified but not found: {extra_package=}"
            )
    return extra_packages


def _get_gcs_bucket(project: str, location: str, staging_bucket: str) -> storage.Bucket:
    """Gets or creates the GCS bucket."""
    storage = _utils._import_cloud_storage_or_raise()
    storage_client = storage.Client(project=project)
    staging_bucket = staging_bucket.replace("gs://", "")
    try:
        gcs_bucket = storage_client.get_bucket(staging_bucket)
        _LOGGER.info(f"Using bucket {staging_bucket}")
    except exceptions.NotFound:
        new_bucket = storage_client.bucket(staging_bucket)
        gcs_bucket = storage_client.create_bucket(new_bucket, location=location)
        _LOGGER.info(f"Creating bucket {staging_bucket} in {location=}")
    return gcs_bucket


def _upload_reasoning_engine(
    reasoning_engine: Queryable,
    gcs_bucket: storage.Bucket,
    gcs_dir_name: str,
) -> None:
    """Uploads the reasoning engine to GCS."""
    cloudpickle = _utils._import_cloudpickle_or_raise()
    blob = gcs_bucket.blob(f"{gcs_dir_name}/{_BLOB_FILENAME}")
    with blob.open("wb") as f:
        cloudpickle.dump(reasoning_engine, f)
    dir_name = f"gs://{gcs_bucket.name}/{gcs_dir_name}"
    _LOGGER.info(f"Writing to {dir_name}/{_BLOB_FILENAME}")


def _upload_requirements(
    requirements: Sequence[str],
    gcs_bucket: storage.Bucket,
    gcs_dir_name: str,
) -> None:
    """Uploads the requirements file to GCS."""
    blob = gcs_bucket.blob(f"{gcs_dir_name}/{_REQUIREMENTS_FILE}")
    blob.upload_from_string("\n".join(requirements))
    dir_name = f"gs://{gcs_bucket.name}/{gcs_dir_name}"
    _LOGGER.info(f"Writing to {dir_name}/{_REQUIREMENTS_FILE}")


def _upload_extra_packages(
    extra_packages: Sequence[str],
    gcs_bucket: storage.Bucket,
    gcs_dir_name: str,
) -> None:
    """Uploads extra packages to GCS."""
    _LOGGER.info("Creating in-memory tarfile of extra_packages")
    tar_fileobj = io.BytesIO()
    with tarfile.open(fileobj=tar_fileobj, mode="w|gz") as tar:
        for file in extra_packages:
            tar.add(file)
    tar_fileobj.seek(0)
    blob = gcs_bucket.blob(f"{gcs_dir_name}/{_EXTRA_PACKAGES_FILE}")
    blob.upload_from_string(tar_fileobj.read())
    dir_name = f"gs://{gcs_bucket.name}/{gcs_dir_name}"
    _LOGGER.info(f"Writing to {dir_name}/{_EXTRA_PACKAGES_FILE}")


def _prepare(
    reasoning_engine: Optional[Queryable],
    requirements: Optional[Sequence[str]],
    extra_packages: Optional[Sequence[str]],
    project: str,
    location: str,
    staging_bucket: str,
    gcs_dir_name: str,
) -> None:
    """Prepares the reasoning engine for creation or updates in Vertex AI.

    This involves packaging and uploading artifacts to Cloud Storage. Note that
    1. This does not actually update the Reasoning Engine in Vertex AI.
    2. This will only generate and upload a pickled object if specified.
    3. This will only generate and upload the dependencies.tar.gz file if
    extra_packages is non-empty.

    Args:
        reasoning_engine: The reasoning engine to be prepared.
        requirements (Sequence[str]): The set of PyPI dependencies needed.
        extra_packages (Sequence[str]): The set of extra user-provided packages.
        project (str): The project for the staging bucket.
        location (str): The location for the staging bucket.
        staging_bucket (str): The staging bucket name in the form "gs://...".
        gcs_dir_name (str): The GCS bucket directory under `staging_bucket` to
            use for staging the artifacts needed.
    """
    gcs_bucket = _get_gcs_bucket(project, location, staging_bucket)
    if reasoning_engine is not None:
        _upload_reasoning_engine(reasoning_engine, gcs_bucket, gcs_dir_name)
    if requirements is not None:
        _upload_requirements(requirements, gcs_bucket, gcs_dir_name)
    if extra_packages is not None:
        _upload_extra_packages(extra_packages, gcs_bucket, gcs_dir_name)


def _generate_update_request_or_raise(
    resource_name: str,
    staging_bucket: str,
    gcs_dir_name: str = _DEFAULT_GCS_DIR_NAME,
    reasoning_engine: Optional[Queryable] = None,
    requirements: Optional[Union[str, Sequence[str]]] = None,
    extra_packages: Optional[Sequence[str]] = None,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
) -> reasoning_engine_service.UpdateReasoningEngineRequest:
    """Tries to generates the update request for the reasoning engine."""
    is_spec_update = False
    update_masks: List[str] = []
    reasoning_engine_spec = types.ReasoningEngineSpec()
    package_spec = types.ReasoningEngineSpec.PackageSpec()
    if requirements is not None:
        is_spec_update = True
        update_masks.append("spec.package_spec.requirements_gcs_uri")
        package_spec.requirements_gcs_uri = "{}/{}/{}".format(
            staging_bucket,
            gcs_dir_name,
            _REQUIREMENTS_FILE,
        )
    if extra_packages is not None:
        is_spec_update = True
        update_masks.append("spec.package_spec.dependency_files_gcs_uri")
        package_spec.dependency_files_gcs_uri = "{}/{}/{}".format(
            staging_bucket,
            gcs_dir_name,
            _EXTRA_PACKAGES_FILE,
        )
    if reasoning_engine is not None:
        is_spec_update = True
        update_masks.append("spec.package_spec.pickle_object_gcs_uri")
        package_spec.pickle_object_gcs_uri = "{}/{}/{}".format(
            staging_bucket,
            gcs_dir_name,
            _BLOB_FILENAME,
        )
        try:
            schema_dict = _utils.generate_schema(
                reasoning_engine.query,
                schema_name=f"{type(reasoning_engine).__name__}_query",
            )
            reasoning_engine_spec.class_methods.append(_utils.to_proto(schema_dict))
        except Exception as e:
            _LOGGER.warning(f"failed to generate schema: {e}")
        update_masks.append("spec.class_methods")

    reasoning_engine_message = types.ReasoningEngine(name=resource_name)
    if is_spec_update:
        reasoning_engine_spec.package_spec = package_spec
        reasoning_engine_message.spec = reasoning_engine_spec
    if display_name:
        reasoning_engine_message.display_name = display_name
        update_masks.append("display_name")
    if description:
        reasoning_engine_message.description = description
        update_masks.append("description")
    if not update_masks:
        raise ValueError(
            "At least one of `reasoning_engine`, `requirements`, "
            "`extra_packages`, `display_name`, or `description` must be "
            "specified."
        )
    return reasoning_engine_service.UpdateReasoningEngineRequest(
        reasoning_engine=reasoning_engine_message,
        update_mask=field_mask_pb2.FieldMask(paths=update_masks),
    )
