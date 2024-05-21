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

from google import auth
from google.api_core import exceptions
from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud import resourcemanager
from google.cloud.aiplatform import vertex_ray
from google.cloud.aiplatform_v1beta1.services.persistent_resource_service import (
    PersistentResourceServiceClient,
)
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    PersistentResource,
)
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    ResourceRuntime,
)
from google.cloud.aiplatform_v1beta1.types.persistent_resource_service import (
    DeletePersistentResourceRequest,
)
import test_constants as tc
import mock
import pytest


# -*- coding: utf-8 -*-

# STOPPING
_TEST_RESPONSE_STOPPING = PersistentResource()
_TEST_RESPONSE_STOPPING.name = tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
resource_runtime = ResourceRuntime()
_TEST_RESPONSE_STOPPING.resource_runtime = resource_runtime
_TEST_RESPONSE_STOPPING.state = "STOPPING"

# ERROR
_TEST_RESPONSE_ERROR = PersistentResource()
_TEST_RESPONSE_ERROR.name = tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
resource_runtime = ResourceRuntime()
_TEST_RESPONSE_ERROR.resource_runtime = resource_runtime
_TEST_RESPONSE_ERROR.state = "ERROR"


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as auth_mock:
        auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            tc.ProjectConstants.TEST_GCP_PROJECT_ID,
        )
        yield auth_mock


@pytest.fixture
def get_project_number_mock():
    with mock.patch.object(
        resourcemanager.ProjectsClient, "get_project"
    ) as get_project_number_mock:
        test_project = resourcemanager.Project(
            project_id=tc.ProjectConstants.TEST_GCP_PROJECT_ID
        )
        test_project.name = f"projects/{tc.ProjectConstants.TEST_GCP_PROJECT_NUMBER}"
        get_project_number_mock.return_value = test_project
        yield get_project_number_mock


@pytest.fixture
def api_client_mock():
    yield mock.create_autospec(
        PersistentResourceServiceClient, spec_set=True, instance=True
    )


@pytest.fixture
def persistent_client_mock(api_client_mock):
    with mock.patch.object(
        vertex_ray.util._gapic_utils,
        "create_persistent_resource_client",
    ) as persistent_client_mock:

        # get_persistent_resource
        api_client_mock.get_persistent_resource.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL
        )
        # delete_persistent_resource
        delete_persistent_resource_lro_mock = mock.Mock(ga_operation.Operation)
        delete_persistent_resource_lro_mock.result.return_value = (
            DeletePersistentResourceRequest()
        )
        api_client_mock.delete_persistent_resource.return_value = (
            delete_persistent_resource_lro_mock
        )

        persistent_client_mock.return_value = api_client_mock
        yield persistent_client_mock


@pytest.fixture
def persistent_client_stopping_mock(api_client_mock):
    with mock.patch.object(
        vertex_ray.util._gapic_utils, "create_persistent_resource_client"
    ) as persistent_client_stopping_mock:
        api_client_mock.get_persistent_resource.return_value = _TEST_RESPONSE_STOPPING
        persistent_client_stopping_mock.return_value = api_client_mock
        yield persistent_client_stopping_mock


@pytest.fixture
def persistent_client_error_mock(api_client_mock):
    with mock.patch.object(
        vertex_ray.util._gapic_utils, "create_persistent_resource_client"
    ) as persistent_client_error_mock:
        # get_persistent_resource
        api_client_mock.get_persistent_resource.return_value = _TEST_RESPONSE_ERROR
        # delete_persistent_resource
        api_client_mock.delete_persistent_resource.side_effect = exceptions.NotFound

        persistent_client_error_mock.return_value = api_client_mock
        yield persistent_client_error_mock
