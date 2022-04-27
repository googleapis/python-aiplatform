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

from typing import Dict, List, Optional, Sequence, Tuple

from google.auth import credentials as auth_credentials
from google.protobuf import field_mask_pb2

from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat.types import tensorboard as gca_tensorboard
from google.cloud.aiplatform.compat.types import (
    tensorboard_experiment as gca_tensorboard_experiment,
    tensorboard_run as gca_tensorboard_run,
)
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils

_LOGGER = base.Logger(__name__)


class _TensorboardServiceResource(base.VertexAiResourceNounWithFutureManager):
    client_class = utils.TensorboardClientWithOverride


class Tensorboard(_TensorboardServiceResource):
    """Managed tensorboard resource for Vertex AI."""

    _resource_noun = "tensorboards"
    _getter_method = "get_tensorboard"
    _list_method = "list_tensorboards"
    _delete_method = "delete_tensorboard"
    _parse_resource_name_method = "parse_tensorboard_path"
    _format_resource_name_method = "tensorboard_path"

    def __init__(
        self,
        tensorboard_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing managed tensorboard given a tensorboard name or ID.

        Args:
            tensorboard_name (str):
                Required. A fully-qualified tensorboard resource name or tensorboard ID.
                Example: "projects/123/locations/us-central1/tensorboards/456" or
                "456" when project and location are initialized or passed.
            project (str):
                Optional. Project to retrieve tensorboard from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve tensorboard from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this Tensorboard. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=tensorboard_name,
        )
        self._gca_resource = self._get_gca_resource(resource_name=tensorboard_name)

    @classmethod
    def create(
        cls,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
        create_request_timeout: Optional[float] = None,
    ) -> "Tensorboard":
        """Creates a new tensorboard.

        Example Usage:

            tb = aiplatform.Tensorboard.create(
                display_name='my display name',
                description='my description',
                labels={
                    'key1': 'value1',
                    'key2': 'value2'
                }
            )

        Args:
            display_name (str):
                Optional. The user-defined name of the Tensorboard.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            description (str):
                Optional. Description of this Tensorboard.
            labels (Dict[str, str]):
                Optional. Labels with user-defined metadata to organize your Tensorboards.
                Label keys and values can be no longer than 64 characters
                (Unicode codepoints), can only contain lowercase letters, numeric
                characters, underscores and dashes. International characters are allowed.
                No more than 64 user labels can be associated with one Tensorboard
                (System labels are excluded).
                See https://goo.gl/xmQnxf for more information and examples of labels.
                System reserved label keys are prefixed with "aiplatform.googleapis.com/"
                and are immutable.
            project (str):
                Optional. Project to upload this model to. Overrides project set in
                aiplatform.init.
            location (str):
                Optional. Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            encryption_spec_key_name (str):
                Optional. Cloud KMS resource identifier of the customer
                managed encryption key used to protect the tensorboard. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this Tensorboard and all sub-resources of this Tensorboard will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
            create_request_timeout (float):
                Optional. The timeout for the create request in seconds.

        Returns:
            tensorboard (Tensorboard):
                Instantiated representation of the managed tensorboard resource.
        """
        if not display_name:
            display_name = cls._generate_display_name()

        utils.validate_display_name(display_name)
        if labels:
            utils.validate_labels(labels)

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        parent = initializer.global_config.common_location_path(
            project=project, location=location
        )

        encryption_spec = initializer.global_config.get_encryption_spec(
            encryption_spec_key_name=encryption_spec_key_name
        )

        gapic_tensorboard = gca_tensorboard.Tensorboard(
            display_name=display_name,
            description=description,
            labels=labels,
            encryption_spec=encryption_spec,
        )

        create_tensorboard_lro = api_client.create_tensorboard(
            parent=parent,
            tensorboard=gapic_tensorboard,
            metadata=request_metadata,
            timeout=create_request_timeout,
        )

        _LOGGER.log_create_with_lro(cls, create_tensorboard_lro)

        created_tensorboard = create_tensorboard_lro.result()

        _LOGGER.log_create_complete(cls, created_tensorboard, "tb")

        return cls(
            tensorboard_name=created_tensorboard.name,
            credentials=credentials,
        )

    def update(
        self,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
    ) -> "Tensorboard":
        """Updates an existing tensorboard.

        Example Usage:

            tb = aiplatform.Tensorboard(tensorboard_name='123456')
            tb.update(
                display_name='update my display name',
                description='update my description',
            )

        Args:
            display_name (str):
                Optional. User-defined name of the Tensorboard.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            description (str):
                Optional. Description of this Tensorboard.
            labels (Dict[str, str]):
                Optional. Labels with user-defined metadata to organize your Tensorboards.
                Label keys and values can be no longer than 64 characters
                (Unicode codepoints), can only contain lowercase letters, numeric
                characters, underscores and dashes. International characters are allowed.
                No more than 64 user labels can be associated with one Tensorboard
                (System labels are excluded).
                See https://goo.gl/xmQnxf for more information and examples of labels.
                System reserved label keys are prefixed with "aiplatform.googleapis.com/"
                and are immutable.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            encryption_spec_key_name (str):
                Optional. Cloud KMS resource identifier of the customer
                managed encryption key used to protect the tensorboard. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this Tensorboard and all sub-resources of this Tensorboard will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.

        Returns:
            Tensorboard: The managed tensorboard resource.
        """
        update_mask = list()

        if display_name:
            utils.validate_display_name(display_name)
            update_mask.append("display_name")

        if description:
            update_mask.append("description")

        if labels:
            utils.validate_labels(labels)
            update_mask.append("labels")

        encryption_spec = None
        if encryption_spec_key_name:
            encryption_spec = initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name,
            )
            update_mask.append("encryption_spec")

        update_mask = field_mask_pb2.FieldMask(paths=update_mask)

        gapic_tensorboard = gca_tensorboard.Tensorboard(
            name=self.resource_name,
            display_name=display_name,
            description=description,
            labels=labels,
            encryption_spec=encryption_spec,
        )

        _LOGGER.log_action_start_against_resource(
            "Updating",
            "tensorboard",
            self,
        )

        update_tensorboard_lro = self.api_client.update_tensorboard(
            tensorboard=gapic_tensorboard,
            update_mask=update_mask,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Update", "tensorboard", self.__class__, update_tensorboard_lro
        )

        update_tensorboard_lro.result()

        _LOGGER.log_action_completed_against_resource("tensorboard", "updated", self)

        return self


class TensorboardExperiment(_TensorboardServiceResource):
    """Managed tensorboard resource for Vertex AI."""

    _resource_noun = "experiments"
    _getter_method = "get_tensorboard_experiment"
    _list_method = "list_tensorboard_experiments"
    _delete_method = "delete_tensorboard_experiment"
    _parse_resource_name_method = "parse_tensorboard_experiment_path"
    _format_resource_name_method = "tensorboard_experiment_path"

    def __init__(
        self,
        tensorboard_experiment_name: str,
        tensorboard_id: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing tensorboard experiment given a tensorboard experiment name or ID.

        Example Usage:

            tb_exp = aiplatform.TensorboardExperiment(
                tensorboard_experiment_name= "projects/123/locations/us-central1/tensorboards/456/experiments/678"
            )

            tb_exp = aiplatform.TensorboardExperiment(
                tensorboard_experiment_name= "678"
                tensorboard_id = "456"
            )

        Args:
            tensorboard_experiment_name (str):
                Required. A fully-qualified tensorboard experiment resource name or resource ID.
                Example: "projects/123/locations/us-central1/tensorboards/456/experiments/678" or
                "678" when tensorboard_id is passed and project and location are initialized or passed.
            tensorboard_id (str):
                Optional. A tensorboard resource ID.
            project (str):
                Optional. Project to retrieve tensorboard from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve tensorboard from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this Tensorboard. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=tensorboard_experiment_name,
        )
        self._gca_resource = self._get_gca_resource(
            resource_name=tensorboard_experiment_name,
            parent_resource_name_fields={Tensorboard._resource_noun: tensorboard_id}
            if tensorboard_id
            else tensorboard_id,
        )

    @classmethod
    def create(
        cls,
        tensorboard_experiment_id: str,
        tensorboard_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Sequence[Tuple[str, str]] = (),
        create_request_timeout: Optional[float] = None,
    ) -> "TensorboardExperiment":
        """Creates a new TensorboardExperiment.

        Example Usage:

            tb = aiplatform.TensorboardExperiment.create(
                tensorboard_experiment_id='my-experiment'
                tensorboard_id='456'
                display_name='my display name',
                description='my description',
                labels={
                    'key1': 'value1',
                    'key2': 'value2'
                }
            )

        Args:
            tensorboard_experiment_id (str):
                Required. The ID to use for the Tensorboard experiment,
                which will become the final component of the Tensorboard
                experiment's resource name.

                This value should be 1-128 characters, and valid
                characters are /[a-z][0-9]-/.

                This corresponds to the ``tensorboard_experiment_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            tensorboard_name (str):
                Required. The resource name or ID of the Tensorboard to create
                the TensorboardExperiment in. Format of resource name:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}``
            display_name (str):
                Optional. The user-defined name of the Tensorboard Experiment.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            description (str):
                Optional. Description of this Tensorboard Experiment.
            labels (Dict[str, str]):
                Optional. Labels with user-defined metadata to organize your Tensorboards.
                Label keys and values can be no longer than 64 characters
                (Unicode codepoints), can only contain lowercase letters, numeric
                characters, underscores and dashes. International characters are allowed.
                No more than 64 user labels can be associated with one Tensorboard
                (System labels are excluded).
                See https://goo.gl/xmQnxf for more information and examples of labels.
                System reserved label keys are prefixed with "aiplatform.googleapis.com/"
                and are immutable.
            project (str):
                Optional. Project to upload this model to. Overrides project set in
                aiplatform.init.
            location (str):
                Optional. Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            create_request_timeout (float):
                Optional. The timeout for the create request in seconds.
        Returns:
            TensorboardExperiment: The TensorboardExperiment resource.
        """

        if display_name:
            utils.validate_display_name(display_name)

        if labels:
            utils.validate_labels(labels)

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        parent = utils.full_resource_name(
            resource_name=tensorboard_name,
            resource_noun=Tensorboard._resource_noun,
            parse_resource_name_method=Tensorboard._parse_resource_name,
            format_resource_name_method=Tensorboard._format_resource_name,
            project=project,
            location=location,
        )

        gapic_tensorboard_experiment = gca_tensorboard_experiment.TensorboardExperiment(
            display_name=display_name,
            description=description,
            labels=labels,
        )

        _LOGGER.log_create_with_lro(cls)

        tensorboard_experiment = api_client.create_tensorboard_experiment(
            parent=parent,
            tensorboard_experiment=gapic_tensorboard_experiment,
            tensorboard_experiment_id=tensorboard_experiment_id,
            metadata=request_metadata,
            timeout=create_request_timeout,
        )

        _LOGGER.log_create_complete(cls, tensorboard_experiment, "tb experiment")

        return cls(
            tensorboard_experiment_name=tensorboard_experiment.name,
            credentials=credentials,
        )

    @classmethod
    def list(
        cls,
        tensorboard_name: str,
        filter: Optional[str] = None,
        order_by: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["TensorboardExperiment"]:
        """List TensorboardExperiemnts in a Tensorboard resource.

        Example Usage:

            aiplatform.TensorboardExperiment.list(
                tensorboard_name='projects/my-project/locations/us-central1/tensorboards/123'
            )

        Args:
            tensorboard_name(str):
                Required. The resource name or resource ID of the
                Tensorboard to list
                TensorboardExperiments. Format, if resource name:
                'projects/{project}/locations/{location}/tensorboards/{tensorboard}'
            filter (str):
                Optional. An expression for filtering the results of the request.
                For field names both snake_case and camelCase are supported.
            order_by (str):
                Optional. A comma-separated list of fields to order by, sorted in
                ascending order. Use "desc" after a field name for descending.
                Supported fields: `display_name`, `create_time`, `update_time`
            project (str):
                Optional. Project to retrieve list from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve list from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve list. Overrides
                credentials set in aiplatform.init.
        Returns:
            List[TensorboardExperiment] - A list of TensorboardExperiments
        """

        parent = utils.full_resource_name(
            resource_name=tensorboard_name,
            resource_noun=Tensorboard._resource_noun,
            parse_resource_name_method=Tensorboard._parse_resource_name,
            format_resource_name_method=Tensorboard._format_resource_name,
            project=project,
            location=location,
        )

        return super()._list(
            filter=filter,
            order_by=order_by,
            project=project,
            location=location,
            credentials=credentials,
            parent=parent,
        )


class TensorboardRun(_TensorboardServiceResource):
    """Managed tensorboard resource for Vertex AI."""

    _resource_noun = "runs"
    _getter_method = "get_tensorboard_run"
    _list_method = "list_tensorboard_runs"
    _delete_method = "delete_tensorboard_run"
    _parse_resource_name_method = "parse_tensorboard_run_path"
    _format_resource_name_method = "tensorboard_run_path"

    def __init__(
        self,
        tensorboard_run_name: str,
        tensorboard_id: Optional[str] = None,
        tensorboard_experiment_id: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing tensorboard experiment given a tensorboard experiment name or ID.

        Example Usage:

            tb_exp = aiplatform.TensorboardRun(
                tensorboard_run_name= "projects/123/locations/us-central1/tensorboards/456/experiments/678/run/8910"
            )

            tb_exp = aiplatform.TensorboardExperiment(
                tensorboard_experiment_name= "8910",
                tensorboard_id = "456",
                tensorboard_experiment_id = "678"
            )

        Args:
            tensorboard_run_name (str):
                Required. A fully-qualified tensorboard run resource name or resource ID.
                Example: "projects/123/locations/us-central1/tensorboards/456/experiments/678/runs/8910" or
                "8910" when tensorboard_id and tensorboard_experiment_id are passed
                and project and location are initialized or passed.
            tensorboard_id (str):
                Optional. A tensorboard resource ID.
            tensorboard_experiment_id (str):
                Optional. A tensorboard experiment resource ID.
            project (str):
                Optional. Project to retrieve tensorboard from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve tensorboard from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this Tensorboard. Overrides
                credentials set in aiplatform.init.
        Raises:
            ValueError: if only one of tensorboard_id or tensorboard_experiment_id is provided.
        """
        if bool(tensorboard_id) != bool(tensorboard_experiment_id):
            raise ValueError(
                "Both tensorboard_id and tensorboard_experiment_id must be provided or neither should be provided."
            )

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=tensorboard_run_name,
        )
        self._gca_resource = self._get_gca_resource(
            resource_name=tensorboard_run_name,
            parent_resource_name_fields={
                Tensorboard._resource_noun: tensorboard_id,
                TensorboardExperiment._resource_noun: tensorboard_experiment_id,
            }
            if tensorboard_id
            else tensorboard_id,
        )

    @classmethod
    def create(
        cls,
        tensorboard_run_id: str,
        tensorboard_experiment_name: str,
        tensorboard_id: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Sequence[Tuple[str, str]] = (),
        create_request_timeout: Optional[float] = None,
    ) -> "TensorboardRun":
        """Creates a new tensorboard.

        Example Usage:

            tb = aiplatform.TensorboardExperiment.create(
                tensorboard_experiment_id='my-experiment'
                tensorboard_id='456'
                display_name='my display name',
                description='my description',
                labels={
                    'key1': 'value1',
                    'key2': 'value2'
                }
            )

        Args:
            tensorboard_run_id (str):
                Required. The ID to use for the Tensorboard run, which
                will become the final component of the Tensorboard run's
                resource name.

                This value should be 1-128 characters, and valid:
                characters are /[a-z][0-9]-/.
            tensorboard_experiment_name (str):
                Required. The resource name or ID of the TensorboardExperiment
                to create the TensorboardRun in. Resource name format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}``

                If resource ID is provided then tensorboard_id must be provided.
            tensorboard_id (str):
                Optional. The resource ID of the Tensorboard to create
                the TensorboardRun in. Format of resource name.
            display_name (str):
                Optional. The user-defined name of the Tensorboard Run.
                This value must be unique among all TensorboardRuns belonging to the
                same parent TensorboardExperiment.

                If not provided tensorboard_run_id will be used.
            description (str):
                Optional. Description of this Tensorboard Run.
            labels (Dict[str, str]):
                Optional. Labels with user-defined metadata to organize your Tensorboards.
                Label keys and values can be no longer than 64 characters
                (Unicode codepoints), can only contain lowercase letters, numeric
                characters, underscores and dashes. International characters are allowed.
                No more than 64 user labels can be associated with one Tensorboard
                (System labels are excluded).
                See https://goo.gl/xmQnxf for more information and examples of labels.
                System reserved label keys are prefixed with "aiplatform.googleapis.com/"
                and are immutable.
            project (str):
                Optional. Project to upload this model to. Overrides project set in
                aiplatform.init.
            location (str):
                Optional. Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            create_request_timeout (float):
                Optional. The timeout for the create request in seconds.
        Returns:
            TensorboardExperiment: The TensorboardExperiment resource.
        """

        if display_name:
            utils.validate_display_name(display_name)

        if labels:
            utils.validate_labels(labels)

        display_name = display_name or tensorboard_run_id

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        parent = utils.full_resource_name(
            resource_name=tensorboard_experiment_name,
            resource_noun=TensorboardExperiment._resource_noun,
            parse_resource_name_method=TensorboardExperiment._parse_resource_name,
            format_resource_name_method=TensorboardExperiment._format_resource_name,
            parent_resource_name_fields={Tensorboard._resource_noun: tensorboard_id},
            project=project,
            location=location,
        )

        gapic_tensorboard_run = gca_tensorboard_run.TensorboardRun(
            display_name=display_name,
            description=description,
            labels=labels,
        )

        _LOGGER.log_create_with_lro(cls)

        tensorboard_run = api_client.create_tensorboard_run(
            parent=parent,
            tensorboard_run=gapic_tensorboard_run,
            tensorboard_run_id=tensorboard_run_id,
            metadata=request_metadata,
            timeout=create_request_timeout,
        )

        _LOGGER.log_create_complete(cls, tensorboard_run, "tb_run")

        return cls(
            tensorboard_run_name=tensorboard_run.name,
            credentials=credentials,
        )

    @classmethod
    def list(
        cls,
        tensorboard_experiment_name: str,
        tensorboard_id: Optional[str] = None,
        filter: Optional[str] = None,
        order_by: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["TensorboardRun"]:
        """List all instances of TensorboardRun in TensorboardExperiment.

        Example Usage:

            aiplatform.TensorboardRun.list(
                tensorboard_name='projects/my-project/locations/us-central1/tensorboards/123/experiments/456'
            )

        Args:
            tensorboard_experiment_name (str):
                Required. The resource name or resource ID of the
                TensorboardExperiment to list
                TensorboardRun. Format, if resource name:
                'projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}'

                If resource ID is provided then tensorboard_id must be provided.
            tensorboard_id (str):
                Optional. The resource ID of the Tensorboard that contains the TensorboardExperiment
                to list TensorboardRun.
            filter (str):
                Optional. An expression for filtering the results of the request.
                For field names both snake_case and camelCase are supported.
            order_by (str):
                Optional. A comma-separated list of fields to order by, sorted in
                ascending order. Use "desc" after a field name for descending.
                Supported fields: `display_name`, `create_time`, `update_time`
            project (str):
                Optional. Project to retrieve list from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve list from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve list. Overrides
                credentials set in aiplatform.init.
        Returns:
            List[TensorboardRun] - A list of TensorboardRun
        """

        parent = utils.full_resource_name(
            resource_name=tensorboard_experiment_name,
            resource_noun=TensorboardExperiment._resource_noun,
            parse_resource_name_method=TensorboardExperiment._parse_resource_name,
            format_resource_name_method=TensorboardExperiment._format_resource_name,
            parent_resource_name_fields={Tensorboard._resource_noun: tensorboard_id},
            project=project,
            location=location,
        )

        return super()._list(
            filter=filter,
            order_by=order_by,
            project=project,
            location=location,
            credentials=credentials,
            parent=parent,
        )
