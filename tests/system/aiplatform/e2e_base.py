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

import abc
import asyncio
import importlib
import logging
import os
import pytest
import uuid

from typing import Any, Dict, Generator

from google.api_core import exceptions
from google.cloud import aiplatform
import vertexai
from google.cloud import bigquery
from google.cloud import resourcemanager
from google.cloud import storage
from google.cloud.aiplatform import initializer

_PROJECT = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
_VPC_NETWORK_URI = os.getenv("_VPC_NETWORK_URI")
_LOCATION = "us-central1"


class TestEndToEnd(metaclass=abc.ABCMeta):
    @property
    @classmethod
    @abc.abstractmethod
    def _temp_prefix(cls) -> str:
        """Prefix to staging bucket and display names created by this end-to-end test.
        Keep the string as short as possible and use kebab case, starting with a lowercase letter.

        Example: `"temp-vertex-hpt-test"`
        """
        pass

    @classmethod
    def _make_display_name(cls, key: str) -> str:
        """Helper method to make unique display_names.

        Args:
            key (str): Required. Identifier for the display name.
        Returns:
            Unique display name.
        """
        return f"{cls._temp_prefix}-{key}-{uuid.uuid4()}"

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)

    @pytest.fixture(scope="class")
    def shared_state(self) -> Generator[Dict[str, Any], None, None]:
        shared_state = {}
        yield shared_state

    @pytest.fixture(scope="class")
    def prepare_staging_bucket(
        self, shared_state: Dict[str, Any]
    ) -> Generator[storage.bucket.Bucket, None, None]:
        """Create a staging bucket and store bucket resource object in shared state."""

        staging_bucket_name = f"{self._temp_prefix.lower()}-{uuid.uuid4()}"[:63]
        shared_state["staging_bucket_name"] = staging_bucket_name

        storage_client = storage.Client(project=_PROJECT)
        shared_state["storage_client"] = storage_client

        bucket = storage_client.create_bucket(
            staging_bucket_name, project=_PROJECT, location=_LOCATION
        )

        # TODO(#1415) Once PR Is merged, use the added utilities to
        # provide create/view access to Pipeline's default service account (compute)
        project_number = (
            resourcemanager.ProjectsClient()
            .get_project(name=f"projects/{_PROJECT}")
            .name.split("/", 1)[1]
        )

        service_account = f"{project_number}-compute@developer.gserviceaccount.com"
        bucket_iam_policy = bucket.get_iam_policy()
        bucket_iam_policy.setdefault("roles/storage.objectCreator", set()).add(
            f"serviceAccount:{service_account}"
        )
        bucket_iam_policy.setdefault("roles/storage.objectViewer", set()).add(
            f"serviceAccount:{service_account}"
        )
        bucket.set_iam_policy(bucket_iam_policy)

        shared_state["bucket"] = bucket
        yield

    @pytest.fixture(scope="class")
    def delete_staging_bucket(self, shared_state: Dict[str, Any]):
        """Delete the staging bucket and all it's contents"""

        yield

        # Get the staging bucket used for testing and wipe it
        bucket = shared_state["bucket"]
        bucket.delete(force=True)

    @pytest.fixture(scope="class")
    def prepare_bigquery_dataset(
        self, shared_state: Dict[str, Any]
    ) -> Generator[bigquery.dataset.Dataset, None, None]:
        """Create a bigquery dataset and store bigquery resource object in shared state."""

        bigquery_client = bigquery.Client(project=_PROJECT)
        shared_state["bigquery_client"] = bigquery_client

        dataset_name = f"{self._temp_prefix.lower()}_{uuid.uuid4()}".replace("-", "_")
        dataset_id = f"{_PROJECT}.{dataset_name}"
        shared_state["bigquery_dataset_id"] = dataset_id

        dataset = bigquery.Dataset(dataset_id)
        dataset.location = _LOCATION
        shared_state["bigquery_dataset"] = bigquery_client.create_dataset(dataset)

        yield

    @pytest.fixture(scope="class")
    def delete_bigquery_dataset(self, shared_state: Dict[str, Any]):
        """Delete the bigquery dataset"""

        yield

        # Get the bigquery dataset id used for testing and wipe it
        bigquery_dataset = shared_state["bigquery_dataset"]
        bigquery_client = shared_state["bigquery_client"]
        bigquery_client.delete_dataset(
            bigquery_dataset.dataset_id, delete_contents=True, not_found_ok=True
        )  # Make an API request.

    @pytest.fixture(scope="class")
    def bigquery_dataset(self) -> Generator[bigquery.dataset.Dataset, None, None]:
        """Create a bigquery dataset and store bigquery resource object in shared state."""

        bigquery_client = bigquery.Client(project=_PROJECT)

        dataset_name = f"{self._temp_prefix.lower()}_{uuid.uuid4()}".replace("-", "_")
        dataset_id = f"{_PROJECT}.{dataset_name}"

        dataset = bigquery.Dataset(dataset_id)
        dataset.location = _LOCATION
        dataset = bigquery_client.create_dataset(dataset)

        yield dataset

        bigquery_client.delete_dataset(
            dataset.dataset_id, delete_contents=True, not_found_ok=True
        )  # Make an API request.

    @pytest.fixture(scope="class")
    def tear_down_resources(self, shared_state: Dict[str, Any]):
        """Delete every Vertex AI resource created during test"""

        yield

        if "resources" not in shared_state:
            return

        # TODO(b/218310362): Add resource deletion system tests
        # Bring all Endpoints to the front of the list
        # Ensures Models are undeployed first before we attempt deletion
        shared_state["resources"].sort(
            key=lambda r: (
                1
                if isinstance(r, aiplatform.Endpoint)
                or isinstance(r, aiplatform.MatchingEngineIndexEndpoint)
                or isinstance(r, aiplatform.Experiment)
                else 2
            )
        )

        for resource in shared_state["resources"]:
            try:
                if isinstance(
                    resource,
                    (
                        aiplatform.Endpoint,
                        aiplatform.Featurestore,
                        aiplatform.MatchingEngineIndexEndpoint,
                    ),
                ):
                    # For endpoint, undeploy model then delete endpoint
                    # For featurestore, force delete its entity_types and features with the featurestore
                    resource.delete(force=True)
                elif isinstance(resource, aiplatform.Experiment):
                    resource.delete(delete_backing_tensorboard_runs=True)
                else:
                    resource.delete()
            except (exceptions.GoogleAPIError, RuntimeError) as e:
                logging.exception(f"Could not delete resource: {resource} due to: {e}")

    @pytest.fixture(scope="session")
    def event_loop(event_loop):
        loop = asyncio.get_event_loop()
        yield loop
        loop.close()
