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

import copy
import importlib
from unittest import mock

from google.api_core import operation as ga_operation
from google.cloud import aiplatform
from google.cloud.aiplatform.compat.services import (
    persistent_resource_service_client_v1,
)
from google.cloud.aiplatform.compat.types import encryption_spec_v1
from google.cloud.aiplatform.compat.types import (
    persistent_resource_service_v1,
)
from google.cloud.aiplatform.compat.types import persistent_resource_v1
from google.cloud.aiplatform import persistent_resource
import constants as test_constants
import pytest


_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_PARENT = test_constants.ProjectConstants._TEST_PARENT

_TEST_PERSISTENT_RESOURCE_ID = (
    test_constants.PersistentResourceConstants._TEST_PERSISTENT_RESOURCE_ID
)
_TEST_PERSISTENT_RESOURCE_DISPLAY_NAME = (
    test_constants.PersistentResourceConstants._TEST_PERSISTENT_RESOURCE_DISPLAY_NAME
)
_TEST_LABELS = test_constants.ProjectConstants._TEST_LABELS
_TEST_NETWORK = test_constants.TrainingJobConstants._TEST_NETWORK
_TEST_RESERVED_IP_RANGES = test_constants.TrainingJobConstants._TEST_RESERVED_IP_RANGES
_TEST_KEY_NAME = test_constants.TrainingJobConstants._TEST_DEFAULT_ENCRYPTION_KEY_NAME
_TEST_SERVICE_ACCOUNT = test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT

_TEST_PERSISTENT_RESOURCE_PROTO = persistent_resource_v1.PersistentResource(
    name=_TEST_PERSISTENT_RESOURCE_ID,
    resource_pools=[
        test_constants.PersistentResourceConstants._TEST_RESOURCE_POOL,
    ],
)


def _get_persistent_resource_proto(
    state=None, name=None, error=None
) -> persistent_resource_v1.PersistentResource:
    persistent_resource_proto = copy.deepcopy(_TEST_PERSISTENT_RESOURCE_PROTO)
    persistent_resource_proto.name = name
    persistent_resource_proto.state = state
    persistent_resource_proto.error = error
    return persistent_resource_proto


def _get_resource_name(name=None, project=_TEST_PROJECT, location=_TEST_LOCATION):
    return "projects/{}/locations/{}/persistentResources/{}".format(
        project, location, name
    )


@pytest.fixture
def create_persistent_resource_mock():
    with mock.patch.object(
        (persistent_resource_service_client_v1.PersistentResourceServiceClient),
        "create_persistent_resource",
    ) as create_persistent_resource_mock:
        create_lro = mock.Mock(ga_operation.Operation)
        create_lro.result.return_value = None

        create_persistent_resource_mock.return_value = create_lro
        yield create_persistent_resource_mock


@pytest.fixture
def get_persistent_resource_mock():
    with mock.patch.object(
        (persistent_resource_service_client_v1.PersistentResourceServiceClient),
        "get_persistent_resource",
    ) as get_persistent_resource_mock:
        get_persistent_resource_mock.side_effect = [
            _get_persistent_resource_proto(
                name=_TEST_PERSISTENT_RESOURCE_ID,
                state=(persistent_resource_v1.PersistentResource.State.RUNNING),
            ),
        ]

        yield get_persistent_resource_mock


_TEST_LIST_RESOURCE_1 = _get_persistent_resource_proto(
    name="resource_1",
    state=(persistent_resource_v1.PersistentResource.State.RUNNING),
)
_TEST_LIST_RESOURCE_2 = _get_persistent_resource_proto(
    name="resource_2",
    state=(persistent_resource_v1.PersistentResource.State.PROVISIONING),
)
_TEST_LIST_RESOURCE_3 = _get_persistent_resource_proto(
    name="resource_3",
    state=(persistent_resource_v1.PersistentResource.State.STOPPING),
)
_TEST_LIST_RESOURCE_4 = _get_persistent_resource_proto(
    name="resource_4",
    state=(persistent_resource_v1.PersistentResource.State.ERROR),
)

_TEST_PERSISTENT_RESOURCE_LIST = [
    _TEST_LIST_RESOURCE_1,
    _TEST_LIST_RESOURCE_2,
    _TEST_LIST_RESOURCE_3,
    _TEST_LIST_RESOURCE_4,
]


@pytest.fixture
def list_persistent_resources_mock():
    with mock.patch.object(
        (persistent_resource_service_client_v1.PersistentResourceServiceClient),
        "list_persistent_resources",
    ) as list_persistent_resources_mock:
        list_persistent_resources_mock.return_value = _TEST_PERSISTENT_RESOURCE_LIST

        yield list_persistent_resources_mock


@pytest.fixture
def delete_persistent_resource_mock():
    with mock.patch.object(
        (persistent_resource_service_client_v1.PersistentResourceServiceClient),
        "delete_persistent_resource",
    ) as delete_persistent_resource_mock:
        delete_lro = mock.Mock(ga_operation.Operation)
        delete_lro.result.return_value = (
            persistent_resource_service_v1.DeletePersistentResourceRequest()
        )
        delete_persistent_resource_mock.return_value = delete_lro
        yield delete_persistent_resource_mock


@pytest.fixture
def reboot_persistent_resource_mock():
    with mock.patch.object(
        (persistent_resource_service_client_v1.PersistentResourceServiceClient),
        "reboot_persistent_resource",
    ) as reboot_persistent_resource_mock:
        reboot_lro = mock.Mock(ga_operation.Operation)
        reboot_lro.result.return_value = (
            persistent_resource_service_v1.RebootPersistentResourceRequest()
        )
        reboot_persistent_resource_mock.return_value = reboot_lro
        yield reboot_persistent_resource_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestPersistentResource:
    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_persistent_resource(
        self,
        create_persistent_resource_mock,
        get_persistent_resource_mock,
        sync,
    ):
        my_test_resource = persistent_resource.PersistentResource.create(
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
            display_name=_TEST_PERSISTENT_RESOURCE_DISPLAY_NAME,
            resource_pools=[
                test_constants.PersistentResourceConstants._TEST_RESOURCE_POOL,
            ],
            labels=_TEST_LABELS,
            sync=sync,
        )

        if not sync:
            my_test_resource.wait()

        expected_persistent_resource_arg = _get_persistent_resource_proto(
            name=_TEST_PERSISTENT_RESOURCE_ID,
        )

        expected_persistent_resource_arg.display_name = (
            _TEST_PERSISTENT_RESOURCE_DISPLAY_NAME
        )
        expected_persistent_resource_arg.labels = _TEST_LABELS

        create_persistent_resource_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
            persistent_resource=expected_persistent_resource_arg,
            timeout=None,
        )

        get_persistent_resource_mock.assert_called_once()
        _, mock_kwargs = get_persistent_resource_mock.call_args
        assert mock_kwargs["name"] == _get_resource_name(
            name=_TEST_PERSISTENT_RESOURCE_ID
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_persistent_resource_with_network(
        self,
        create_persistent_resource_mock,
        get_persistent_resource_mock,
        sync,
    ):
        my_test_resource = persistent_resource.PersistentResource.create(
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
            resource_pools=[
                test_constants.PersistentResourceConstants._TEST_RESOURCE_POOL,
            ],
            network=_TEST_NETWORK,
            reserved_ip_ranges=_TEST_RESERVED_IP_RANGES,
            sync=sync,
        )

        if not sync:
            my_test_resource.wait()

        expected_persistent_resource_arg = _get_persistent_resource_proto(
            name=_TEST_PERSISTENT_RESOURCE_ID,
        )

        expected_persistent_resource_arg.network = _TEST_NETWORK
        expected_persistent_resource_arg.reserved_ip_ranges = _TEST_RESERVED_IP_RANGES

        create_persistent_resource_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
            persistent_resource=expected_persistent_resource_arg,
            timeout=None,
        )
        get_persistent_resource_mock.assert_called_once()
        _, mock_kwargs = get_persistent_resource_mock.call_args
        assert mock_kwargs["name"] == _get_resource_name(
            name=_TEST_PERSISTENT_RESOURCE_ID
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_persistent_resource_with_kms_key(
        self,
        create_persistent_resource_mock,
        get_persistent_resource_mock,
        sync,
    ):
        my_test_resource = persistent_resource.PersistentResource.create(
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
            resource_pools=[
                test_constants.PersistentResourceConstants._TEST_RESOURCE_POOL,
            ],
            kms_key_name=_TEST_KEY_NAME,
            sync=sync,
        )

        if not sync:
            my_test_resource.wait()

        expected_persistent_resource_arg = _get_persistent_resource_proto(
            name=_TEST_PERSISTENT_RESOURCE_ID,
        )

        expected_persistent_resource_arg.encryption_spec = (
            encryption_spec_v1.EncryptionSpec(kms_key_name=_TEST_KEY_NAME)
        )

        create_persistent_resource_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
            persistent_resource=expected_persistent_resource_arg,
            timeout=None,
        )
        get_persistent_resource_mock.assert_called_once()
        _, mock_kwargs = get_persistent_resource_mock.call_args
        assert mock_kwargs["name"] == _get_resource_name(
            name=_TEST_PERSISTENT_RESOURCE_ID
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_persistent_resource_with_service_account(
        self,
        create_persistent_resource_mock,
        get_persistent_resource_mock,
        sync,
    ):
        my_test_resource = persistent_resource.PersistentResource.create(
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
            resource_pools=[
                test_constants.PersistentResourceConstants._TEST_RESOURCE_POOL,
            ],
            service_account=_TEST_SERVICE_ACCOUNT,
            sync=sync,
        )

        if not sync:
            my_test_resource.wait()

        expected_persistent_resource_arg = _get_persistent_resource_proto(
            name=_TEST_PERSISTENT_RESOURCE_ID,
        )

        service_account_spec = persistent_resource_v1.ServiceAccountSpec(
            enable_custom_service_account=True, service_account=_TEST_SERVICE_ACCOUNT
        )
        expected_persistent_resource_arg.resource_runtime_spec = (
            persistent_resource_v1.ResourceRuntimeSpec(
                service_account_spec=service_account_spec
            )
        )

        create_persistent_resource_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
            persistent_resource=expected_persistent_resource_arg,
            timeout=None,
        )
        get_persistent_resource_mock.assert_called_once()
        _, mock_kwargs = get_persistent_resource_mock.call_args
        assert mock_kwargs["name"] == _get_resource_name(
            name=_TEST_PERSISTENT_RESOURCE_ID
        )

    def test_list_persistent_resources(self, list_persistent_resources_mock):
        resource_list = persistent_resource.PersistentResource.list()

        list_persistent_resources_mock.assert_called_once()
        assert len(resource_list) == len(_TEST_PERSISTENT_RESOURCE_LIST)

        for i in range(len(resource_list)):
            actual_resource = resource_list[i]
            expected_resource = _TEST_PERSISTENT_RESOURCE_LIST[i]

            assert actual_resource.name == expected_resource.name
            assert actual_resource.state == expected_resource.state

    @pytest.mark.parametrize("sync", [True, False])
    def test_delete_persistent_resource(
        self,
        get_persistent_resource_mock,
        delete_persistent_resource_mock,
        sync,
    ):
        test_resource = persistent_resource.PersistentResource(
            _TEST_PERSISTENT_RESOURCE_ID
        )
        test_resource.delete(sync=sync)

        if not sync:
            test_resource.wait()

        get_persistent_resource_mock.assert_called_once()
        delete_persistent_resource_mock.assert_called_once_with(
            name=_TEST_PERSISTENT_RESOURCE_ID,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_reboot_persistent_resource(
        self,
        get_persistent_resource_mock,
        reboot_persistent_resource_mock,
        sync,
    ):
        test_resource = persistent_resource.PersistentResource(
            _TEST_PERSISTENT_RESOURCE_ID
        )
        test_resource.reboot(sync=sync)

        if not sync:
            test_resource.wait()

        get_persistent_resource_mock.assert_called_once()
        reboot_persistent_resource_mock.assert_called_once_with(
            name=_TEST_PERSISTENT_RESOURCE_ID,
        )
