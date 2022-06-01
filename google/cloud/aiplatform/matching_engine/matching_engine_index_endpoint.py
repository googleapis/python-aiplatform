# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import matching_engine
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.types import (
    machine_resources as gca_machine_resources_compat,
    matching_engine_index_endpoint as gca_matching_engine_index_endpoint,
)
from google.cloud.aiplatform.matching_engine._protos import match_service_pb2
from google.cloud.aiplatform.matching_engine._protos import match_service_pb2_grpc
from google.protobuf import field_mask_pb2

import grpc

_LOGGER = base.Logger(__name__)


@dataclass
class MatchNeighbor:
    """The id and distance of a nearest neighbor match for a given query embedding.

    Args:
        id (str):
            Required. The id of the neighbor.
        distance (float):
            Required. The distance to the query embedding.
    """

    id: str
    distance: float


class MatchingEngineIndexEndpoint(base.VertexAiResourceNounWithFutureManager):
    """Matching Engine index endpoint resource for Vertex AI."""

    client_class = utils.IndexEndpointClientWithOverride

    _resource_noun = "indexEndpoints"
    _getter_method = "get_index_endpoint"
    _list_method = "list_index_endpoints"
    _delete_method = "delete_index_endpoint"
    _parse_resource_name_method = "parse_index_endpoint_path"
    _format_resource_name_method = "index_endpoint_path"

    def __init__(
        self,
        index_endpoint_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing index endpoint given a name or ID.

        Example Usage:

            my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
                index_endpoint_name='projects/123/locations/us-central1/index_endpoint/my_index_id'
            )
            or
            my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
                index_endpoint_name='my_index_endpoint_id'
            )

        Args:
            index_endpoint_name (str):
                Required. A fully-qualified index endpoint resource name or a index ID.
                Example: "projects/123/locations/us-central1/index_endpoints/my_index_id"
                or "my_index_id" when project and location are initialized or passed.
            project (str):
                Optional. Project to retrieve index endpoint from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve index endpoint from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this IndexEndpoint. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=index_endpoint_name,
        )
        self._gca_resource = self._get_gca_resource(resource_name=index_endpoint_name)

    @classmethod
    @base.optional_sync()
    def create(
        cls,
        display_name: str,
        network: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "MatchingEngineIndexEndpoint":
        """Creates a MatchingEngineIndexEndpoint resource.

        Example Usage:

            my_index_endpoint = aiplatform.IndexEndpoint.create(
                display_name='my_endpoint',
            )

        Args:
            display_name (str):
                Required. The display name of the IndexEndpoint.
                The name can be up to 128 characters long and
                can be consist of any UTF-8 characters.
            network (str):
                Required. The full name of the Google Compute Engine
                `network <https://cloud.google.com/compute/docs/networks-and-firewalls#networks>`__
                to which the IndexEndpoint should be peered.

                Private services access must already be configured for the
                network. If left unspecified, the Endpoint is not peered
                with any network.

                `Format <https://cloud.google.com/compute/docs/reference/rest/v1/networks/insert>`__:
                projects/{project}/global/networks/{network}. Where
                {project} is a project number, as in '12345', and {network}
                is network name.
            description (str):
                Optional. The description of the IndexEndpoint.
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your IndexEndpoint.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one
                IndexEndpoint (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            project (str):
                Optional. Project to create EntityType in. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to create EntityType in. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to create EntityTypes. Overrides
                credentials set in aiplatform.init.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            sync (bool):
                Optional. Whether to execute this creation synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            MatchingEngineIndexEndpoint - IndexEndpoint resource object

        """
        gapic_index_endpoint = gca_matching_engine_index_endpoint.IndexEndpoint(
            display_name=display_name,
            description=description,
            network=network,
        )

        if labels:
            utils.validate_labels(labels)
            gapic_index_endpoint.labels = labels

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        create_lro = api_client.create_index_endpoint(
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            index_endpoint=gapic_index_endpoint,
            metadata=request_metadata,
        )

        _LOGGER.log_create_with_lro(cls, create_lro)

        created_index = create_lro.result()

        _LOGGER.log_create_complete(cls, created_index, "index_endpoint")

        index_obj = cls(
            index_endpoint_name=created_index.name,
            project=project,
            location=location,
            credentials=credentials,
        )

        return index_obj

    def update(
        self,
        display_name: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "MatchingEngineIndexEndpoint":
        """Updates an existing index endpoint resource.

        Args:
            display_name (str):
                Required. The display name of the IndexEndpoint.
                The name can be up to 128 characters long and
                can be consist of any UTF-8 characters.
            description (str):
                Optional. The description of the IndexEndpoint.
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your Indexs.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one IndexEndpoint
                (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.

        Returns:
            MatchingEngineIndexEndpoint - The updated index endpoint resource object.
        """

        self.wait()

        update_mask = list()

        if labels:
            utils.validate_labels(labels)
            update_mask.append("labels")

        if display_name is not None:
            update_mask.append("display_name")

        if description is not None:
            update_mask.append("description")

        update_mask = field_mask_pb2.FieldMask(paths=update_mask)

        gapic_index_endpoint = gca_matching_engine_index_endpoint.IndexEndpoint(
            name=self.resource_name,
            display_name=display_name,
            description=description,
            labels=labels,
        )

        self._gca_resource = self.api_client.update_index_endpoint(
            index_endpoint=gapic_index_endpoint,
            update_mask=update_mask,
            metadata=request_metadata,
        )

        return self

    @staticmethod
    def _build_deployed_index(
        deployed_index_id: str,
        index_resource_name: Optional[str] = None,
        display_name: Optional[str] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = None,
        max_replica_count: Optional[int] = None,
        enable_access_logging: Optional[bool] = None,
        reserved_ip_ranges: Optional[Sequence[str]] = None,
        deployment_group: Optional[str] = None,
        auth_config_audiences: Optional[Sequence[str]] = None,
        auth_config_allowed_issuers: Optional[Sequence[str]] = None,
    ) -> gca_matching_engine_index_endpoint.DeployedIndex:
        """Builds a DeployedIndex.

        Args:
            deployed_index_id (str):
                Required. The user specified ID of the
                DeployedIndex. The ID can be up to 128
                characters long and must start with a letter and
                only contain letters, numbers, and underscores.
                The ID must be unique within the project it is
                created in.
            index_resource_name (str):
                Optional. A fully-qualified index endpoint resource name or a index ID.
                Example: "projects/123/locations/us-central1/index_endpoints/my_index_id"
            display_name (str):
                Optional. The display name of the DeployedIndex. If not provided upon
                creation, the Index's display_name is used.
            machine_type (str):
                Optional. The type of machine. Not specifying machine type will
                result in model to be deployed with automatic resources.
            min_replica_count (int):
                Optional. The minimum number of machine replicas this deployed
                model will be always deployed on. If traffic against it increases,
                it may dynamically be deployed onto more replicas, and as traffic
                decreases, some of these extra replicas may be freed.

                If this value is not provided, the value of 2 will be used.
            max_replica_count (int):
                Optional. The maximum number of replicas this deployed model may
                be deployed on when the traffic against it increases. If requested
                value is too large, the deployment will error, but if deployment
                succeeds then the ability to scale the model to that many replicas
                is guaranteed (barring service outages). If traffic against the
                deployed model increases beyond what its replicas at maximum may
                handle, a portion of the traffic will be dropped. If this value
                is not provided, the larger value of min_replica_count or 2 will
                be used. If value provided is smaller than min_replica_count, it
                will automatically be increased to be min_replica_count.
            enable_access_logging (bool):
                Optional. If true, private endpoint's access
                logs are sent to StackDriver Logging.
                These logs are like standard server access logs,
                containing information like timestamp and
                latency for each MatchRequest.
                Note that Stackdriver logs may incur a cost,
                especially if the deployed index receives a high
                queries per second rate (QPS). Estimate your
                costs before enabling this option.
            deployed_index_auth_config (google.cloud.aiplatform_v1.types.DeployedIndexAuthConfig):
                Optional. If set, the authentication is
                enabled for the private endpoint.
            reserved_ip_ranges (Sequence[str]):
                Optional. A list of reserved ip ranges under
                the VPC network that can be used for this
                DeployedIndex.
                If set, we will deploy the index within the
                provided ip ranges. Otherwise, the index might
                be deployed to any ip ranges under the provided
                VPC network.

                The value sohuld be the name of the address
                (https://cloud.google.com/compute/docs/reference/rest/v1/addresses)
                Example: 'vertex-ai-ip-range'.
            deployment_group (str):
                Optional. The deployment group can be no longer than 64
                characters (eg: 'test', 'prod'). If not set, we will use the
                'default' deployment group.

                Creating ``deployment_groups`` with ``reserved_ip_ranges``
                is a recommended practice when the peered network has
                multiple peering ranges. This creates your deployments from
                predictable IP spaces for easier traffic administration.
                Also, one deployment_group (except 'default') can only be
                used with the same reserved_ip_ranges which means if the
                deployment_group has been used with reserved_ip_ranges: [a,
                b, c], using it with [a, b] or [d, e] is disallowed.

                Note: we only support up to 5 deployment groups(not
                including 'default').
            auth_config_audiences (Sequence[str]):
                Optional. The list of JWT
                `audiences <https://tools.ietf.org/html/draft-ietf-oauth-json-web-token-32#section-4.1.3>`__.
                that are allowed to access. A JWT containing any of these
                audiences will be accepted.
            auth_config_allowed_issuers (Sequence[str]):
                Optional. A list of allowed JWT issuers. Each entry must be a valid
                Google service account, in the following format:

                ``service-account-name@project-id.iam.gserviceaccount.com``
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
        """

        deployed_index = gca_matching_engine_index_endpoint.DeployedIndex(
            id=deployed_index_id,
            index=index_resource_name,
            display_name=display_name,
            enable_access_logging=enable_access_logging,
            reserved_ip_ranges=reserved_ip_ranges,
            deployment_group=deployment_group,
        )

        if auth_config_audiences and auth_config_allowed_issuers:
            deployed_index.deployed_index_auth_config = gca_matching_engine_index_endpoint.DeployedIndexAuthConfig(
                auth_provider=gca_matching_engine_index_endpoint.DeployedIndexAuthConfig.AuthProvider(
                    audiences=auth_config_audiences,
                    allowed_issuers=auth_config_allowed_issuers,
                )
            )

        if machine_type:
            machine_spec = gca_machine_resources_compat.MachineSpec(
                machine_type=machine_type
            )

            deployed_index.dedicated_resources = (
                gca_machine_resources_compat.DedicatedResources(
                    machine_spec=machine_spec,
                    min_replica_count=min_replica_count,
                    max_replica_count=max_replica_count,
                )
            )

        else:
            deployed_index.automatic_resources = (
                gca_machine_resources_compat.AutomaticResources(
                    min_replica_count=min_replica_count,
                    max_replica_count=max_replica_count,
                )
            )
        return deployed_index

    def deploy_index(
        self,
        index: matching_engine.MatchingEngineIndex,
        deployed_index_id: str,
        display_name: Optional[str] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = None,
        max_replica_count: Optional[int] = None,
        enable_access_logging: Optional[bool] = None,
        reserved_ip_ranges: Optional[Sequence[str]] = None,
        deployment_group: Optional[str] = None,
        auth_config_audiences: Optional[Sequence[str]] = None,
        auth_config_allowed_issuers: Optional[Sequence[str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "MatchingEngineIndexEndpoint":
        """Deploys an existing index resource to this endpoint resource.

        Args:
            index (MatchingEngineIndex):
                Required. The Index this is the
                deployment of. We may refer to this Index as the
                DeployedIndex's "original" Index.
            deployed_index_id (str):
                Required. The user specified ID of the
                DeployedIndex. The ID can be up to 128
                characters long and must start with a letter and
                only contain letters, numbers, and underscores.
                The ID must be unique within the project it is
                created in.
            display_name (str):
                The display name of the DeployedIndex. If not provided upon
                creation, the Index's display_name is used.
            machine_type (str):
                Optional. The type of machine. Not specifying machine type will
                result in model to be deployed with automatic resources.
            min_replica_count (int):
                Optional. The minimum number of machine replicas this deployed
                model will be always deployed on. If traffic against it increases,
                it may dynamically be deployed onto more replicas, and as traffic
                decreases, some of these extra replicas may be freed.

                If this value is not provided, the value of 2 will be used.
            max_replica_count (int):
                Optional. The maximum number of replicas this deployed model may
                be deployed on when the traffic against it increases. If requested
                value is too large, the deployment will error, but if deployment
                succeeds then the ability to scale the model to that many replicas
                is guaranteed (barring service outages). If traffic against the
                deployed model increases beyond what its replicas at maximum may
                handle, a portion of the traffic will be dropped. If this value
                is not provided, the larger value of min_replica_count or 2 will
                be used. If value provided is smaller than min_replica_count, it
                will automatically be increased to be min_replica_count.
            enable_access_logging (bool):
                Optional. If true, private endpoint's access
                logs are sent to StackDriver Logging.
                These logs are like standard server access logs,
                containing information like timestamp and
                latency for each MatchRequest.
                Note that Stackdriver logs may incur a cost,
                especially if the deployed index receives a high
                queries per second rate (QPS). Estimate your
                costs before enabling this option.
            reserved_ip_ranges (Sequence[str]):
                Optional. A list of reserved ip ranges under
                the VPC network that can be used for this
                DeployedIndex.
                If set, we will deploy the index within the
                provided ip ranges. Otherwise, the index might
                be deployed to any ip ranges under the provided
                VPC network.

                The value sohuld be the name of the address
                (https://cloud.google.com/compute/docs/reference/rest/v1/addresses)
                Example: 'vertex-ai-ip-range'.
            deployment_group (str):
                Optional. The deployment group can be no longer than 64
                characters (eg: 'test', 'prod'). If not set, we will use the
                'default' deployment group.

                Creating ``deployment_groups`` with ``reserved_ip_ranges``
                is a recommended practice when the peered network has
                multiple peering ranges. This creates your deployments from
                predictable IP spaces for easier traffic administration.
                Also, one deployment_group (except 'default') can only be
                used with the same reserved_ip_ranges which means if the
                deployment_group has been used with reserved_ip_ranges: [a,
                b, c], using it with [a, b] or [d, e] is disallowed.

                Note: we only support up to 5 deployment groups(not
                including 'default').
            auth_config_audiences (Sequence[str]):
                The list of JWT
                `audiences <https://tools.ietf.org/html/draft-ietf-oauth-json-web-token-32#section-4.1.3>`__.
                that are allowed to access. A JWT containing any of these
                audiences will be accepted.

                auth_config_audiences and auth_config_allowed_issuers must be passed together.
            auth_config_allowed_issuers (Sequence[str]):
                A list of allowed JWT issuers. Each entry must be a valid
                Google service account, in the following format:

                ``service-account-name@project-id.iam.gserviceaccount.com``

                auth_config_audiences and auth_config_allowed_issuers must be passed together.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
        Returns:
            MatchingEngineIndexEndpoint - IndexEndpoint resource object
        """

        self.wait()

        _LOGGER.log_action_start_against_resource(
            "Deploying index",
            "index_endpoint",
            self,
        )

        deployed_index = self._build_deployed_index(
            deployed_index_id=deployed_index_id,
            index_resource_name=index.resource_name,
            display_name=display_name,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            enable_access_logging=enable_access_logging,
            reserved_ip_ranges=reserved_ip_ranges,
            deployment_group=deployment_group,
            auth_config_audiences=auth_config_audiences,
            auth_config_allowed_issuers=auth_config_allowed_issuers,
        )

        deploy_lro = self.api_client.deploy_index(
            index_endpoint=self.resource_name,
            deployed_index=deployed_index,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Deploy index", "index_endpoint", self.__class__, deploy_lro
        )

        deploy_lro.result()

        _LOGGER.log_action_completed_against_resource(
            "index_endpoint", "Deployed index", self
        )

        # update local resource
        self._sync_gca_resource()

        return self

    def undeploy_index(
        self,
        deployed_index_id: str,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "MatchingEngineIndexEndpoint":
        """Undeploy a deployed index endpoint resource.

        Args:
            deployed_index_id (str):
                Required. The ID of the DeployedIndex
                to be undeployed from the IndexEndpoint.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
        Returns:
            MatchingEngineIndexEndpoint - IndexEndpoint resource object
        """

        self.wait()

        _LOGGER.log_action_start_against_resource(
            "Undeploying index",
            "index_endpoint",
            self,
        )

        undeploy_lro = self.api_client.undeploy_index(
            index_endpoint=self.resource_name,
            deployed_index_id=deployed_index_id,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Undeploy index", "index_endpoint", self.__class__, undeploy_lro
        )

        undeploy_lro.result()

        _LOGGER.log_action_completed_against_resource(
            "index_endpoint", "Undeployed index", self
        )

        return self

    def mutate_deployed_index(
        self,
        deployed_index_id: str,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ):
        """Updates an existing deployed index under this endpoint resource.

        Args:
            index_id (str):
                Required. The ID of the MatchingEnginIndex associated with the DeployedIndex.
            deployed_index_id (str):
                Required. The user specified ID of the
                DeployedIndex. The ID can be up to 128
                characters long and must start with a letter and
                only contain letters, numbers, and underscores.
                The ID must be unique within the project it is
                created in.
            min_replica_count (int):
                Optional. The minimum number of machine replicas this deployed
                model will be always deployed on. If traffic against it increases,
                it may dynamically be deployed onto more replicas, and as traffic
                decreases, some of these extra replicas may be freed.
            max_replica_count (int):
                Optional. The maximum number of replicas this deployed model may
                be deployed on when the traffic against it increases. If requested
                value is too large, the deployment will error, but if deployment
                succeeds then the ability to scale the model to that many replicas
                is guaranteed (barring service outages). If traffic against the
                deployed model increases beyond what its replicas at maximum may
                handle, a portion of the traffic will be dropped. If this value
                is not provided, the larger value of min_replica_count or 1 will
                be used. If value provided is smaller than min_replica_count, it
                will automatically be increased to be min_replica_count.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
        """

        self.wait()

        _LOGGER.log_action_start_against_resource(
            "Mutating index",
            "index_endpoint",
            self,
        )

        deployed_index = self._build_deployed_index(
            index_resource_name=None,
            deployed_index_id=deployed_index_id,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
        )

        deploy_lro = self.api_client.mutate_deployed_index(
            index_endpoint=self.resource_name,
            deployed_index=deployed_index,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Mutate index", "index_endpoint", self.__class__, deploy_lro
        )

        deploy_lro.result()

        # update local resource
        self._sync_gca_resource()

        _LOGGER.log_action_completed_against_resource("index_endpoint", "Mutated", self)

        return self

    @property
    def deployed_indexes(
        self,
    ) -> List[gca_matching_engine_index_endpoint.DeployedIndex]:
        """Returns a list of deployed indexes on this endpoint.

        Returns:
            List[gca_matching_engine_index_endpoint.DeployedIndex] - Deployed indexes
        """
        self._assert_gca_resource_is_available()
        return self._gca_resource.deployed_indexes

    @base.optional_sync()
    def _undeploy(
        self,
        deployed_index_id: str,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync=True,
    ) -> None:
        """Undeploys a deployed index.

        Args:
            deployed_index_id (str):
                Required. The ID of the DeployedIndex to be undeployed from the
                Endpoint.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
        """
        self._sync_gca_resource()

        _LOGGER.log_action_start_against_resource("Undeploying", "index_endpoint", self)

        operation_future = self.api_client.undeploy_index(
            index_endpoint=self.resource_name,
            deployed_index_id=deployed_index_id,
            metadata=metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Undeploy", "index_endpoint", self.__class__, operation_future
        )

        # block before returning
        operation_future.result()

        # update local resource
        self._sync_gca_resource()

        _LOGGER.log_action_completed_against_resource(
            "index_endpoint", "undeployed", self
        )

    def undeploy_all(self, sync: bool = True) -> "MatchingEngineIndexEndpoint":
        """Undeploys every index deployed to this MatchingEngineIndexEndpoint.

        Args:
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        """
        self._sync_gca_resource()

        for deployed_index in self.deployed_indexes:
            self._undeploy(deployed_index_id=deployed_index.id, sync=sync)

        return self

    def delete(self, force: bool = False, sync: bool = True) -> None:
        """Deletes this MatchingEngineIndexEndpoint resource. If force is set to True,
        all indexes on this endpoint will be undeployed prior to deletion.

        Args:
            force (bool):
                Required. If force is set to True, all deployed indexes on this
                endpoint will be undeployed first. Default is False.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Raises:
            FailedPrecondition: If indexes are deployed on this MatchingEngineIndexEndpoint and force = False.
        """
        if force:
            self.undeploy_all(sync=sync)

        super().delete(sync=sync)

    @property
    def description(self) -> str:
        """Description of the index endpoint."""
        self._assert_gca_resource_is_available()
        return self._gca_resource.description

    def match(
        self, deployed_index_id: str, queries: List[List[float]], num_neighbors: int = 1
    ) -> List[List[MatchNeighbor]]:
        """Retrieves nearest neighbors for the given embedding queries on the specified deployed index.

        Args:
            deployed_index_id (str):
                Required. The ID of the DeployedIndex to match the queries against.
            queries (List[List[float]]):
                Required. A list of queries. Each query is a list of floats, representing a single embedding.
            num_neighbors (int):
                Required. The number of nearest neighbors to be retrieved from database for
                each query.

        Returns:
            List[List[MatchNeighbor]] - A list of nearest neighbors for each query.
        """

        # Find the deployed index by id
        deployed_indexes = [
            deployed_index
            for deployed_index in self.deployed_indexes
            if deployed_index.id == deployed_index_id
        ]

        if not deployed_indexes:
            raise RuntimeError(f"No deployed index with id '{deployed_index_id}' found")

        # Retrieve server ip from deployed index
        server_ip = deployed_indexes[0].private_endpoints.match_grpc_address

        # Set up channel and stub
        channel = grpc.insecure_channel("{}:10000".format(server_ip))
        stub = match_service_pb2_grpc.MatchServiceStub(channel)

        # Create the batch match request
        batch_request = match_service_pb2.BatchMatchRequest()
        batch_request_for_index = (
            match_service_pb2.BatchMatchRequest.BatchMatchRequestPerIndex()
        )
        batch_request_for_index.deployed_index_id = deployed_index_id
        batch_request_for_index.requests.extend(
            [
                match_service_pb2.MatchRequest(
                    num_neighbors=num_neighbors,
                    deployed_index_id=deployed_index_id,
                    float_val=query,
                )
                for query in queries
            ]
        )
        batch_request.requests.append(batch_request_for_index)

        # Perform the request
        response = stub.BatchMatch(batch_request)

        # Wrap the results in MatchNeighbor objects and return
        return [
            [
                MatchNeighbor(id=neighbor.id, distance=neighbor.distance)
                for neighbor in embedding_neighbors.neighbor
            ]
            for embedding_neighbors in response.responses[0].responses
        ]
