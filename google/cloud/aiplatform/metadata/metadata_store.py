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
from typing import Optional

import logging
from google.auth import credentials as auth_credentials
from google.api_core import exceptions

from google.cloud.aiplatform import base, initializer
from google.cloud.aiplatform_v1beta1.types import metadata_store as gca_metadata_store
from google.cloud.aiplatform_v1beta1.services.metadata_service import (
    client as metadata_service_client,
)


class MetadataStore(base.AiPlatformResourceNounWithFutureManager):
    """Managed MetadataStore resource for AI Platform"""

    client_class = metadata_service_client.MetadataServiceClient
    _is_client_prediction_client = False
    _resource_noun = "metadataStores"
    _getter_method = "get_metadata_store"
    _delete_method = "delete_metadata_store"

    def __init__(
        self,
        metadata_store_name: str = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing MetadataStore given a MetadataStore name or ID.

        Args:
            metadata_store_name (str):
                A fully-qualified MetadataStore resource name or metadataStore ID.
                Example: "projects/123/locations/us-central1/metadataStores/my-store" or
                "my-store" when project and location are initialized or passed.
                If not set, metadata_store_name will be set to "default".
            project (str):
                Optional project to retrieve resource from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional location to retrieve resource from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.

        """

        super().__init__(
            project=project, location=location, credentials=credentials,
        )
        self._gca_resource = self._get_gca_resource(resource_name=metadata_store_name)

    @classmethod
    def create(
        cls,
        metadata_store_id: str = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        encryption_spec_key_name: Optional[str] = None,
    ) -> "MetadataStore":
        f"""Creates a new MetadataStore if it does not exist.

        Args:
            metadata_store_id (str):
                The {metadata_store_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}
                If not provided, the MetadataStore's ID will be set to "default" to create a default MetadataStore.
            project (str):
                Project to upload this model to. Overrides project set in
                aiplatform.init.
            location (str):
                Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
            encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the metadata store. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this MetadataStore and all sub-resources of this MetadataStore will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.


        Returns:
            metadata_store (MetadataStore):
                Instantiated representation of the managed metadata store resource.

        """
        api_client = cls._instantiate_client(location=location, credentials=credentials)
        gapic_metadata_store = gca_metadata_store.MetadataStore(
            encryption_spec=initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name
            )
        )

        try:
            api_client.create_metadata_store(
                parent=initializer.global_config.common_location_path(
                    project=project, location=location
                ),
                metadata_store=gapic_metadata_store,
                metadata_store_id=metadata_store_id,
            )
        except exceptions.AlreadyExists:
            logging.info(f"MetadataStore '{metadata_store_id}' already exists")

        return cls(
            metadata_store_name=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )
