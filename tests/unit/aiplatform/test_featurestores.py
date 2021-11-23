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

import pytest

from unittest import mock
from importlib import reload
from unittest.mock import patch

from google.api_core import operation
from google.protobuf import field_mask_pb2

from google.cloud import aiplatform
from google.cloud.aiplatform import _featurestores as featurestores
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer

from google.cloud.aiplatform.utils import featurestore_utils

from google.cloud.aiplatform_v1.services.featurestore_service import (
    client as featurestore_service_client,
)

from google.cloud.aiplatform_v1.types import (
    featurestore as gca_featurestore,
    entity_type as gca_entity_type,
    feature as gca_feature,
    encryption_spec as gca_encryption_spec,
)

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

# featurestore
_TEST_FEATURESTORE_ID = "featurestore_id"
_TEST_FEATURESTORE_NAME = f"{_TEST_PARENT}/featurestores/{_TEST_FEATURESTORE_ID}"
_TEST_FEATURESTORE_INVALID = f"{_TEST_PARENT}/featurestore/{_TEST_FEATURESTORE_ID}"

# featurestore online
_TEST_ONLINE_SERVING_CONFIG = 1
_TEST_ONLINE_SERVING_CONFIG_UPDATE = 2

# entity_type
_TEST_ENTITY_TYPE_ID = "entity_type_id"
_TEST_ENTITY_TYPE_NAME = f"{_TEST_FEATURESTORE_NAME}/entityTypes/{_TEST_ENTITY_TYPE_ID}"
_TEST_ENTITY_TYPE_INVALID = (
    f"{_TEST_FEATURESTORE_NAME}/entityType/{_TEST_ENTITY_TYPE_ID}"
)

# feature
_TEST_FEATURE_ID = "feature_id"
_TEST_FEATURE_NAME = f"{_TEST_ENTITY_TYPE_NAME}/features/{_TEST_FEATURE_ID}"
_TEST_FEATURE_INVALID = f"{_TEST_ENTITY_TYPE_NAME}/feature/{_TEST_FEATURE_ID}"
_TEST_FEATURE_VALUE_TYPE = "INT64"
_TEST_FEATURE_VALUE_TYPE_ENUM = 9
_TEST_FEATURE_ID_INVALID = "1feature_id"

# misc
_TEST_DESCRIPTION = "my description"
_TEST_LABELS = {"my_key": "my_value"}
_TEST_DESCRIPTION_UPDATE = "my description update"
_TEST_LABELS_UPDATE = {"my_key_update": "my_value_update"}

# request_metadata
_TEST_REQUEST_METADATA = ()

# CMEK encryption
_TEST_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_ENCRYPTION_KEY_NAME
)

# Lists
_TEST_FEATURESTORE_LIST = [
    gca_featurestore.Featurestore(
        name=_TEST_FEATURESTORE_NAME,
        online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
            fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
        ),
        encryption_spec=_TEST_ENCRYPTION_SPEC,
    ),
    gca_featurestore.Featurestore(
        name=_TEST_FEATURESTORE_NAME,
        online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
            fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
        ),
    ),
    gca_featurestore.Featurestore(
        name=_TEST_FEATURESTORE_NAME,
        online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
            fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
        ),
        encryption_spec=_TEST_ENCRYPTION_SPEC,
    ),
]

_TEST_ENTITY_TYPE_LIST = [
    gca_entity_type.EntityType(name=_TEST_ENTITY_TYPE_NAME,),
    gca_entity_type.EntityType(name=_TEST_ENTITY_TYPE_NAME,),
    gca_entity_type.EntityType(name=_TEST_ENTITY_TYPE_NAME,),
]

_TEST_FEATURE_LIST = [
    gca_feature.Feature(name=_TEST_FEATURE_NAME,),
    gca_feature.Feature(name=_TEST_FEATURE_NAME,),
    gca_feature.Feature(name=_TEST_FEATURE_NAME,),
]

_TEST_FEATURE_CONFIGS = {
    "my_feature_id_1": {"value_type": _TEST_FEATURE_VALUE_TYPE},
    "my_feature_id_2": {
        "value_type": _TEST_FEATURE_VALUE_TYPE,
        "description": _TEST_DESCRIPTION,
    },
    "my_feature_id_3": {
        "value_type": _TEST_FEATURE_VALUE_TYPE,
        "labels": _TEST_LABELS,
    },
}


# All Featurestore Mocks
@pytest.fixture
def get_featurestore_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "get_featurestore"
    ) as get_featurestore_mock:
        get_featurestore_mock.return_value = gca_featurestore.Featurestore(
            name=_TEST_FEATURESTORE_NAME,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
                fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
            ),
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_featurestore_mock


@pytest.fixture
def update_featurestore_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "update_featurestore"
    ) as update_featurestore_mock:
        update_featurestore_lro_mock = mock.Mock(operation.Operation)
        update_featurestore_mock.return_value = update_featurestore_lro_mock
        yield update_featurestore_mock


@pytest.fixture
def list_featurestores_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "list_featurestores"
    ) as list_featurestores_mock:
        list_featurestores_mock.return_value = _TEST_FEATURESTORE_LIST
        yield list_featurestores_mock


@pytest.fixture
def delete_featurestore_mock():
    with mock.patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "delete_featurestore"
    ) as delete_featurestore_mock:
        delete_featurestore_lro_mock = mock.Mock(operation.Operation)
        delete_featurestore_mock.return_value = delete_featurestore_lro_mock
        yield delete_featurestore_mock


@pytest.fixture
def search_features_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "search_features"
    ) as search_features_mock:
        search_features_mock.return_value = _TEST_FEATURE_LIST
        yield search_features_mock


@pytest.fixture
def create_featurestore_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "create_featurestore"
    ) as create_featurestore_mock:
        create_featurestore_lro_mock = mock.Mock(operation.Operation)
        create_featurestore_lro_mock.result.return_value = gca_featurestore.Featurestore(
            name=_TEST_FEATURESTORE_NAME,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
                fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
            ),
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_featurestore_mock.return_value = create_featurestore_lro_mock
        yield create_featurestore_mock


# ALL EntityType Mocks
@pytest.fixture
def get_entity_type_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "get_entity_type"
    ) as get_entity_type_mock:
        get_entity_type_mock.return_value = gca_entity_type.EntityType(
            name=_TEST_ENTITY_TYPE_NAME,
        )
        yield get_entity_type_mock


@pytest.fixture
def update_entity_type_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "update_entity_type"
    ) as update_entity_type_mock:
        update_entity_type_lro_mock = mock.Mock(operation.Operation)
        update_entity_type_mock.return_value = update_entity_type_lro_mock
        yield update_entity_type_mock


@pytest.fixture
def list_entity_types_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "list_entity_types"
    ) as list_entity_types_mock:
        list_entity_types_mock.return_value = _TEST_ENTITY_TYPE_LIST
        yield list_entity_types_mock


@pytest.fixture
def delete_entity_type_mock():
    with mock.patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "delete_entity_type"
    ) as delete_entity_type_mock:
        delete_entity_type_lro_mock = mock.Mock(operation.Operation)
        delete_entity_type_mock.return_value = delete_entity_type_lro_mock
        yield delete_entity_type_mock


@pytest.fixture
def create_entity_type_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "create_entity_type"
    ) as create_entity_type_mock:
        create_entity_type_lro_mock = mock.Mock(operation.Operation)
        create_entity_type_lro_mock.result.return_value = gca_entity_type.EntityType(
            name=_TEST_ENTITY_TYPE_NAME
        )
        create_entity_type_mock.return_value = create_entity_type_lro_mock
        yield create_entity_type_mock


# ALL Feature Mocks
@pytest.fixture
def get_feature_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "get_feature"
    ) as get_feature_mock:
        get_feature_mock.return_value = gca_feature.Feature(name=_TEST_FEATURE_NAME,)
        yield get_feature_mock


@pytest.fixture
def update_feature_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "update_feature"
    ) as update_feature_mock:
        update_feature_lro_mock = mock.Mock(operation.Operation)
        update_feature_mock.return_value = update_feature_lro_mock
        yield update_feature_mock


@pytest.fixture
def list_features_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "list_features"
    ) as list_features_mock:
        list_features_mock.return_value = _TEST_FEATURE_LIST
        yield list_features_mock


@pytest.fixture
def delete_feature_mock():
    with mock.patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "delete_feature"
    ) as delete_feature_mock:
        delete_feature_lro_mock = mock.Mock(operation.Operation)
        delete_feature_mock.return_value = delete_feature_lro_mock
        yield delete_feature_mock


@pytest.fixture
def create_feature_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "create_feature"
    ) as create_feature_mock:
        create_feature_lro_mock = mock.Mock(operation.Operation)
        create_feature_lro_mock.result.return_value = gca_feature.Feature(
            name=_TEST_FEATURE_NAME, value_type=_TEST_FEATURE_VALUE_TYPE_ENUM,
        )
        create_feature_mock.return_value = create_feature_lro_mock
        yield create_feature_mock


@pytest.fixture
def batch_create_features_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "batch_create_features"
    ) as batch_create_features_mock:
        batch_create_features_lro_mock = mock.Mock(operation.Operation)
        batch_create_features_mock.return_value = batch_create_features_lro_mock
        yield batch_create_features_mock


class TestFeaturestoreUtils:
    @pytest.mark.parametrize(
        "resource_id, expected",
        [
            ("resource_id", True),
            ("resource_id12345", True),
            ("12345resource_id", False),
            ("_resource_id", True),
            ("resource_id/1234", False),
            ("_resource_id/1234", False),
            ("resource-id-1234", False),
            ("123456", False),
            ("c" * 61, False),
            ("_123456", True),
        ],
    )
    def test_validate_resource_id(self, resource_id: str, expected: bool):
        assert expected == featurestore_utils.validate_id(resource_id)

    @pytest.mark.parametrize(
        "feature_name, featurestore_id, entity_type_id",
        [
            (_TEST_FEATURE_NAME, None, None,),
            (_TEST_FEATURE_ID, _TEST_FEATURESTORE_ID, _TEST_ENTITY_TYPE_ID,),
        ],
    )
    def test_validate_and_get_feature_resource_ids(
        self, feature_name: str, featurestore_id: str, entity_type_id: str,
    ):
        assert (
            _TEST_FEATURESTORE_ID,
            _TEST_ENTITY_TYPE_ID,
            _TEST_FEATURE_ID,
        ) == featurestore_utils.validate_and_get_feature_resource_ids(
            feature_name=feature_name,
            featurestore_id=featurestore_id,
            entity_type_id=entity_type_id,
        )

    @pytest.mark.parametrize(
        "feature_name, featurestore_id, entity_type_id",
        [
            (_TEST_FEATURE_INVALID, None, None,),
            (_TEST_FEATURE_ID, None, _TEST_ENTITY_TYPE_ID,),
            (_TEST_FEATURE_ID, None, None,),
            (_TEST_FEATURE_ID, _TEST_FEATURESTORE_NAME, None,),
        ],
    )
    def test_validate_and_get_feature_resource_ids_with_raise(
        self, feature_name: str, featurestore_id: str, entity_type_id: str,
    ):
        with pytest.raises(ValueError):
            featurestore_utils.validate_and_get_feature_resource_ids(
                feature_name=feature_name,
                featurestore_id=featurestore_id,
                entity_type_id=entity_type_id,
            )

    @pytest.mark.parametrize(
        "entity_type_name, featurestore_id",
        [
            (_TEST_ENTITY_TYPE_NAME, None,),
            (_TEST_ENTITY_TYPE_ID, _TEST_FEATURESTORE_ID,),
        ],
    )
    def test_validate_and_get_entity_type_resource_ids(
        self, entity_type_name: str, featurestore_id: str
    ):
        assert (
            _TEST_FEATURESTORE_ID,
            _TEST_ENTITY_TYPE_ID,
        ) == featurestore_utils.validate_and_get_entity_type_resource_ids(
            entity_type_name=entity_type_name, featurestore_id=featurestore_id
        )

    @pytest.mark.parametrize(
        "entity_type_name, featurestore_id",
        [
            (_TEST_ENTITY_TYPE_INVALID, None,),
            (_TEST_ENTITY_TYPE_ID, None,),
            (_TEST_ENTITY_TYPE_ID, _TEST_FEATURESTORE_NAME,),
        ],
    )
    def test_validate_and_get_entity_type_resource_ids_with_raise(
        self, entity_type_name: str, featurestore_id: str,
    ):
        with pytest.raises(ValueError):
            featurestore_utils.validate_and_get_entity_type_resource_ids(
                entity_type_name=entity_type_name, featurestore_id=featurestore_id
            )

    @pytest.mark.parametrize(
        "value_type",
        [
            "BOOL",
            "BOOL_ARRAY",
            "DOUBLE",
            "DOUBLE_ARRAY",
            "INT64",
            "INT64_ARRAY",
            "STRING",
            "STRING_ARRAY",
            "BYTES",
        ],
    )
    def test_validate_value_type(self, value_type: str):
        assert featurestore_utils.validate_value_type(value_type=value_type) is True

    @pytest.mark.parametrize(
        "value_type",
        [
            "INT",
            "INT_array",
            "STR",
            "double",
            "bool",
            "array",
            "INT32",
            "VALUE_TYPE_UNSPECIFIED",
        ],
    )
    def test_validate_value_type_with_raise(self, value_type: str):
        with pytest.raises(ValueError):
            featurestore_utils.validate_value_type(value_type=value_type)

    def validate_and_get_batch_create_features_requests(self):
        expected_batch_create_feature_requests = [
            {
                "feature": gca_feature.Feature(
                    value_type=_TEST_FEATURE_VALUE_TYPE_ENUM
                ),
                "feature_id": "my_feature_id_1",
            },
            {
                "feature": gca_feature.Feature(
                    value_type=_TEST_FEATURE_VALUE_TYPE_ENUM,
                    description=_TEST_DESCRIPTION,
                ),
                "feature_id": "my_feature_id_2",
            },
            {
                "feature": gca_feature.Feature(
                    value_type=_TEST_FEATURE_VALUE_TYPE_ENUM, labels=_TEST_LABELS
                ),
                "feature_id": "my_feature_id_3",
            },
        ]

        assert (
            featurestore_utils.validate_and_get_batch_create_features_requests(
                featureConfigs=_TEST_FEATURE_CONFIGS
            )
            == expected_batch_create_feature_requests
        )


class Test_FeatureConfig:
    def test_feature_config_return_request_dict(self):

        featureConfig = featurestore_utils._FeatureConfig(
            feature_id=_TEST_FEATURE_ID,
            value_type=_TEST_FEATURE_VALUE_TYPE,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        gapic_feature = gca_feature.Feature(
            description=_TEST_DESCRIPTION,
            value_type=_TEST_FEATURE_VALUE_TYPE_ENUM,
            labels=_TEST_LABELS,
        )

        true_request_dict = {
            "feature": gapic_feature,
            "feature_id": _TEST_FEATURE_ID,
        }

        assert featureConfig.request_dict == true_request_dict

    def test_feature_config_request_dict_raises_invalid_feature_id(self):
        featureConfig = featurestore_utils._FeatureConfig(
            feature_id=_TEST_FEATURE_ID_INVALID,
            value_type=_TEST_FEATURE_VALUE_TYPE,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )
        with pytest.raises(ValueError):
            featureConfig.request_dict

    @pytest.mark.parametrize("value_type", ["INT", "VALUE_TYPE_UNSPECIFIED"])
    def test_feature_config_request_dict_raises_invalid_value_type(self, value_type):
        featureConfig = featurestore_utils._FeatureConfig(
            feature_id=_TEST_FEATURE_ID,
            value_type=value_type,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )
        with pytest.raises(ValueError):
            featureConfig.request_dict


class TestFeaturestore:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "featurestore_name", [_TEST_FEATURESTORE_ID, _TEST_FEATURESTORE_NAME]
    )
    def test_init_featurestore(self, featurestore_name, get_featurestore_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = featurestores.Featurestore(
            featurestore_name=featurestore_name
        )

        get_featurestore_mock.assert_called_once_with(
            name=my_featurestore.resource_name, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_get_entity_type(self, get_entity_type_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = featurestores.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_entity_type = my_featurestore.get_entity_type(
            entity_type_id=_TEST_ENTITY_TYPE_ID
        )

        get_entity_type_mock.assert_called_once_with(
            name=_TEST_ENTITY_TYPE_NAME, retry=base._DEFAULT_RETRY
        )
        assert type(my_entity_type) == featurestores.EntityType

    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_update_featurestore(self, update_featurestore_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = featurestores.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_featurestore.update(labels=_TEST_LABELS_UPDATE)

        expected_featurestore = gca_featurestore.Featurestore(
            name=_TEST_FEATURESTORE_NAME,
            labels=_TEST_LABELS_UPDATE,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(),
        )
        update_featurestore_mock.assert_called_once_with(
            featurestore=expected_featurestore,
            update_mask=field_mask_pb2.FieldMask(paths=["labels"]),
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_update_featurestore_online(self, update_featurestore_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = featurestores.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_featurestore.update_online_store(
            fixed_node_count=_TEST_ONLINE_SERVING_CONFIG_UPDATE
        )

        expected_featurestore = gca_featurestore.Featurestore(
            name=_TEST_FEATURESTORE_NAME,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
                fixed_node_count=_TEST_ONLINE_SERVING_CONFIG_UPDATE
            ),
        )
        update_featurestore_mock.assert_called_once_with(
            featurestore=expected_featurestore,
            update_mask=field_mask_pb2.FieldMask(
                paths=["online_serving_config.fixed_node_count"]
            ),
            metadata=_TEST_REQUEST_METADATA,
        )

    def test_list_featurestores(self, list_featurestores_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore_list = featurestores.Featurestore.list()

        list_featurestores_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT, "filter": None}
        )
        assert len(my_featurestore_list) == len(_TEST_FEATURESTORE_LIST)
        for my_featurestore in my_featurestore_list:
            assert type(my_featurestore) == featurestores.Featurestore

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_delete_featurestore(self, delete_featurestore_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = featurestores.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_featurestore.delete(sync=sync)

        if not sync:
            my_featurestore.wait()

        delete_featurestore_mock.assert_called_once_with(
            name=my_featurestore.resource_name
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_list_entity_types(self, list_entity_types_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = featurestores.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_entity_type_list = my_featurestore.list_entity_types()

        list_entity_types_mock.assert_called_once_with(
            request={"parent": _TEST_FEATURESTORE_NAME, "filter": None}
        )
        assert len(my_entity_type_list) == len(_TEST_ENTITY_TYPE_LIST)
        for my_entity_type in my_entity_type_list:
            assert type(my_entity_type) == featurestores.EntityType

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_featurestore_mock", "get_entity_type_mock")
    def test_delete_entity_types(self, delete_entity_type_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = featurestores.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_featurestore.delete_entity_types(
            entity_type_ids=[_TEST_ENTITY_TYPE_ID, _TEST_ENTITY_TYPE_ID], sync=sync
        )

        if not sync:
            my_featurestore.wait()

        delete_entity_type_mock.assert_has_calls(
            calls=[
                mock.call(name=_TEST_ENTITY_TYPE_NAME),
                mock.call(name=_TEST_ENTITY_TYPE_NAME),
            ],
            any_order=True,
        )

    @pytest.mark.usefixtures("get_featurestore_mock", "get_entity_type_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_entity_type(self, create_entity_type_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = featurestores.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_NAME
        )
        my_entity_type = my_featurestore.create_entity_type(
            entity_type_id=_TEST_ENTITY_TYPE_ID,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
            sync=sync,
        )

        if not sync:
            my_entity_type.wait()

        expected_entity_type = gca_entity_type.EntityType(
            labels=_TEST_LABELS, description=_TEST_DESCRIPTION,
        )
        create_entity_type_mock.assert_called_once_with(
            request={
                "parent": _TEST_FEATURESTORE_NAME,
                "entity_type": expected_entity_type,
                "entity_type_id": _TEST_ENTITY_TYPE_ID,
            },
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_featurestore(self, create_featurestore_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = featurestores.Featurestore.create(
            featurestore_id=_TEST_FEATURESTORE_ID,
            online_store_fixed_node_count=_TEST_ONLINE_SERVING_CONFIG,
            labels=_TEST_LABELS,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        if not sync:
            my_featurestore.wait()

        expected_featurestore = gca_featurestore.Featurestore(
            labels=_TEST_LABELS,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
                fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
            ),
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_featurestore_mock.assert_called_once_with(
            request={
                "parent": _TEST_PARENT,
                "featurestore": expected_featurestore,
                "featurestore_id": _TEST_FEATURESTORE_ID,
            },
            metadata=_TEST_REQUEST_METADATA,
        )


class TestEntityType:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "entity_type_name, featurestore_id",
        [
            (_TEST_ENTITY_TYPE_NAME, None),
            (_TEST_ENTITY_TYPE_ID, _TEST_FEATURESTORE_ID),
        ],
    )
    def test_init_entity_type(
        self, entity_type_name, featurestore_id, get_entity_type_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        featurestores.EntityType(
            entity_type_name=entity_type_name, featurestore_id=featurestore_id
        )

        get_entity_type_mock.assert_called_once_with(
            name=_TEST_ENTITY_TYPE_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_get_featurestore(self, get_featurestore_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = featurestores.EntityType(
            entity_type_name=_TEST_ENTITY_TYPE_NAME
        )
        my_featurestore = my_entity_type.get_featurestore()

        get_featurestore_mock.assert_called_once_with(
            name=my_featurestore.resource_name, retry=base._DEFAULT_RETRY
        )
        assert type(my_featurestore) == featurestores.Featurestore

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_get_feature(self, get_feature_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = featurestores.EntityType(
            entity_type_name=_TEST_ENTITY_TYPE_NAME
        )
        my_feature = my_entity_type.get_feature(feature_id=_TEST_FEATURE_ID)

        get_feature_mock.assert_called_once_with(
            name=my_feature.resource_name, retry=base._DEFAULT_RETRY
        )
        assert type(my_feature) == featurestores.Feature

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_update_entity_type(self, update_entity_type_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = featurestores.EntityType(
            entity_type_name=_TEST_ENTITY_TYPE_NAME
        )
        my_entity_type.update(labels=_TEST_LABELS_UPDATE)

        expected_entity_type = gca_entity_type.EntityType(
            name=_TEST_ENTITY_TYPE_NAME, labels=_TEST_LABELS_UPDATE,
        )
        update_entity_type_mock.assert_called_once_with(
            entity_type=expected_entity_type,
            update_mask=field_mask_pb2.FieldMask(paths=["labels"]),
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.parametrize(
        "featurestore_name", [_TEST_FEATURESTORE_NAME, _TEST_FEATURESTORE_ID]
    )
    def test_list_entity_types(self, featurestore_name, list_entity_types_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type_list = featurestores.EntityType.list(
            featurestore_name=featurestore_name
        )

        list_entity_types_mock.assert_called_once_with(
            request={"parent": _TEST_FEATURESTORE_NAME, "filter": None}
        )
        assert len(my_entity_type_list) == len(_TEST_ENTITY_TYPE_LIST)
        for my_entity_type in my_entity_type_list:
            assert type(my_entity_type) == featurestores.EntityType

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_list_features(self, list_features_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = featurestores.EntityType(
            entity_type_name=_TEST_ENTITY_TYPE_NAME
        )
        my_feature_list = my_entity_type.list_features()

        list_features_mock.assert_called_once_with(
            request={"parent": _TEST_ENTITY_TYPE_NAME, "filter": None}
        )
        assert len(my_feature_list) == len(_TEST_FEATURE_LIST)
        for my_feature in my_feature_list:
            assert type(my_feature) == featurestores.Feature

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_entity_type_mock", "get_feature_mock")
    def test_delete_features(self, delete_feature_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = featurestores.EntityType(
            entity_type_name=_TEST_ENTITY_TYPE_NAME
        )
        my_entity_type.delete_features(
            feature_ids=[_TEST_FEATURE_ID, _TEST_FEATURE_ID], sync=sync
        )

        if not sync:
            my_entity_type.wait()

        delete_feature_mock.assert_has_calls(
            calls=[
                mock.call(name=_TEST_FEATURE_NAME),
                mock.call(name=_TEST_FEATURE_NAME),
            ],
            any_order=True,
        )

    @pytest.mark.usefixtures("get_entity_type_mock", "get_feature_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_feature(self, create_feature_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = featurestores.EntityType(
            entity_type_name=_TEST_ENTITY_TYPE_NAME
        )
        my_feature = my_entity_type.create_feature(
            feature_id=_TEST_FEATURE_ID,
            value_type=_TEST_FEATURE_VALUE_TYPE,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        if not sync:
            my_feature.wait()

        expected_feature = gca_feature.Feature(
            value_type=_TEST_FEATURE_VALUE_TYPE_ENUM,
            labels=_TEST_LABELS,
            description=_TEST_DESCRIPTION,
        )
        create_feature_mock.assert_called_once_with(
            request={
                "parent": _TEST_ENTITY_TYPE_NAME,
                "feature": expected_feature,
                "feature_id": _TEST_FEATURE_ID,
            },
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_entity_type_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_entity_type(self, create_entity_type_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = featurestores.EntityType.create(
            entity_type_id=_TEST_ENTITY_TYPE_ID,
            featurestore_name=_TEST_FEATURESTORE_NAME,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        if not sync:
            my_entity_type.wait()

        expected_entity_type = gca_entity_type.EntityType(
            description=_TEST_DESCRIPTION, labels=_TEST_LABELS,
        )
        create_entity_type_mock.assert_called_once_with(
            request={
                "parent": _TEST_FEATURESTORE_NAME,
                "entity_type": expected_entity_type,
                "entity_type_id": _TEST_ENTITY_TYPE_ID,
            },
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_entity_type_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_batch_create_features(self, batch_create_features_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = featurestores.EntityType(
            entity_type_name=_TEST_ENTITY_TYPE_NAME
        )
        my_entity_type.batch_create_features(feature_configs=_TEST_FEATURE_CONFIGS)

        if not sync:
            my_entity_type.wait()

        expected_batch_create_feature_requests = [
            {
                "feature": gca_feature.Feature(
                    value_type=_TEST_FEATURE_VALUE_TYPE_ENUM
                ),
                "feature_id": "my_feature_id_1",
            },
            {
                "feature": gca_feature.Feature(
                    value_type=_TEST_FEATURE_VALUE_TYPE_ENUM,
                    description=_TEST_DESCRIPTION,
                ),
                "feature_id": "my_feature_id_2",
            },
            {
                "feature": gca_feature.Feature(
                    value_type=_TEST_FEATURE_VALUE_TYPE_ENUM, labels=_TEST_LABELS
                ),
                "feature_id": "my_feature_id_3",
            },
        ]
        batch_create_features_mock.assert_called_once_with(
            parent=_TEST_ENTITY_TYPE_NAME,
            requests=expected_batch_create_feature_requests,
            metadata=_TEST_REQUEST_METADATA,
        )


class TestFeature:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "feature_name, entity_type_id, featurestore_id",
        [
            (_TEST_FEATURE_NAME, None, None),
            (_TEST_FEATURE_ID, _TEST_ENTITY_TYPE_ID, _TEST_FEATURESTORE_ID),
        ],
    )
    def test_init_feature(
        self, feature_name, entity_type_id, featurestore_id, get_feature_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        featurestores.Feature(
            feature_name=feature_name,
            entity_type_id=entity_type_id,
            featurestore_id=featurestore_id,
        )
        get_feature_mock.assert_called_once_with(
            name=_TEST_FEATURE_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_feature_mock")
    def test_get_featurestore(self, get_featurestore_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature = featurestores.Feature(feature_name=_TEST_FEATURE_NAME)
        my_featurestore = my_feature.get_featurestore()

        get_featurestore_mock.assert_called_once_with(
            name=my_featurestore.resource_name, retry=base._DEFAULT_RETRY
        )
        assert type(my_featurestore) == featurestores.Featurestore

    @pytest.mark.usefixtures("get_feature_mock")
    def test_get_entity_type(self, get_entity_type_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature = featurestores.Feature(feature_name=_TEST_FEATURE_NAME)
        my_entity_type = my_feature.get_entity_type()

        get_entity_type_mock.assert_called_once_with(
            name=my_entity_type.resource_name, retry=base._DEFAULT_RETRY
        )
        assert type(my_entity_type) == featurestores.EntityType

    @pytest.mark.usefixtures("get_feature_mock")
    def test_update_feature(self, update_feature_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature = featurestores.Feature(feature_name=_TEST_FEATURE_NAME)
        my_feature.update(labels=_TEST_LABELS_UPDATE)

        expected_feature = gca_feature.Feature(
            name=_TEST_FEATURE_NAME, labels=_TEST_LABELS_UPDATE,
        )
        update_feature_mock.assert_called_once_with(
            feature=expected_feature,
            update_mask=field_mask_pb2.FieldMask(paths=["labels"]),
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.parametrize(
        "entity_type_name, featurestore_id",
        [
            (_TEST_ENTITY_TYPE_NAME, None),
            (_TEST_ENTITY_TYPE_ID, _TEST_FEATURESTORE_ID),
        ],
    )
    def test_list_features(self, entity_type_name, featurestore_id, list_features_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature_list = featurestores.Feature.list(
            entity_type_name=entity_type_name, featurestore_id=featurestore_id
        )

        list_features_mock.assert_called_once_with(
            request={"parent": _TEST_ENTITY_TYPE_NAME, "filter": None}
        )
        assert len(my_feature_list) == len(_TEST_FEATURE_LIST)
        for my_feature in my_feature_list:
            assert type(my_feature) == featurestores.Feature

    @pytest.mark.usefixtures("get_feature_mock")
    def test_search_features(self, search_features_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature_list = featurestores.Feature.search()

        search_features_mock.assert_called_once_with(
            request={"location": _TEST_PARENT, "query": None}
        )
        assert len(my_feature_list) == len(_TEST_FEATURE_LIST)
        for my_feature in my_feature_list:
            assert type(my_feature) == featurestores.Feature

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_feature(self, create_feature_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature = featurestores.Feature.create(
            feature_id=_TEST_FEATURE_ID,
            value_type=_TEST_FEATURE_VALUE_TYPE,
            entity_type_name=_TEST_ENTITY_TYPE_ID,
            featurestore_id=_TEST_FEATURESTORE_ID,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        if not sync:
            my_feature.wait()

        expected_feature = gca_feature.Feature(
            value_type=_TEST_FEATURE_VALUE_TYPE_ENUM,
            labels=_TEST_LABELS,
            description=_TEST_DESCRIPTION,
        )
        create_feature_mock.assert_called_once_with(
            request={
                "parent": _TEST_ENTITY_TYPE_NAME,
                "feature": expected_feature,
                "feature_id": _TEST_FEATURE_ID,
            },
            metadata=_TEST_REQUEST_METADATA,
        )
