# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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

import re
from typing import Dict
from unittest import mock
from unittest.mock import call
from unittest.mock import patch

from google.api_core import operation as ga_operation
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat import types
from google.cloud.aiplatform.compat.services import (
    feature_online_store_admin_service_client,
)
from feature_store_constants import (
    _TEST_BIGTABLE_FOS1_ID,
    _TEST_BIGTABLE_FOS1_LABELS,
    _TEST_BIGTABLE_FOS1_PATH,
    _TEST_BIGTABLE_FOS2_ID,
    _TEST_BIGTABLE_FOS2_LABELS,
    _TEST_BIGTABLE_FOS2_PATH,
    _TEST_BIGTABLE_FOS3_ID,
    _TEST_BIGTABLE_FOS3_LABELS,
    _TEST_BIGTABLE_FOS3_PATH,
    _TEST_ESF_OPTIMIZED_FOS_ID,
    _TEST_ESF_OPTIMIZED_FOS_LABELS,
    _TEST_ESF_OPTIMIZED_FOS_PATH,
    _TEST_FOS_LIST,
    _TEST_FV1_BQ_URI,
    _TEST_FV1_ENTITY_ID_COLUMNS,
    _TEST_FV1_ID,
    _TEST_FV1_LABELS,
    _TEST_FV1_PATH,
    _TEST_LOCATION,
    _TEST_OPTIMIZED_EMBEDDING_FV_ID,
    _TEST_OPTIMIZED_EMBEDDING_FV_PATH,
    _TEST_PARENT,
    _TEST_PROJECT,
    _TEST_PSC_OPTIMIZED_FOS_ID,
    _TEST_PSC_OPTIMIZED_FOS_LABELS,
    _TEST_PSC_OPTIMIZED_FOS_PATH,
    _TEST_PSC_PROJECT_ALLOWLIST,
)
from test_feature_view import fv_eq
from vertexai.resources.preview import (
    DistanceMeasureType,
    FeatureOnlineStore,
    FeatureOnlineStoreType,
    FeatureViewBigQuerySource,
    IndexConfig,
    TreeAhConfig,
)
from vertexai.resources.preview.feature_store import (
    feature_online_store,
)
import pytest


@pytest.fixture
def fos_logger_mock():
    with patch.object(
        feature_online_store._LOGGER,
        "info",
        wraps=feature_online_store._LOGGER.info,
    ) as logger_mock:
        yield logger_mock


@pytest.fixture
def list_fos_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "list_feature_online_stores",
    ) as list_fos_mock:
        list_fos_mock.return_value = _TEST_FOS_LIST
        yield list_fos_mock


@pytest.fixture
def delete_fos_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "delete_feature_online_store",
    ) as delete_fos_mock:
        delete_fos_lro_mock = mock.Mock(ga_operation.Operation)
        delete_fos_mock.return_value = delete_fos_lro_mock
        yield delete_fos_mock


def fos_eq(
    fos_to_check: FeatureOnlineStore,
    name: str,
    resource_name: str,
    project: str,
    location: str,
    labels: Dict[str, str],
    type: FeatureOnlineStoreType,
):
    """Check if a FeatureOnlineStore has the appropriate values set."""
    assert fos_to_check.name == name
    assert fos_to_check.resource_name == resource_name
    assert fos_to_check.project == project
    assert fos_to_check.location == location
    assert fos_to_check.labels == labels
    assert fos_to_check.feature_online_store_type == type


pytestmark = pytest.mark.usefixtures("google_auth_mock")


@pytest.mark.parametrize(
    "online_store_name",
    [_TEST_BIGTABLE_FOS1_ID, _TEST_BIGTABLE_FOS1_PATH],
)
def test_init(online_store_name, get_fos_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fos = FeatureOnlineStore(online_store_name)

    get_fos_mock.assert_called_once_with(
        name=_TEST_BIGTABLE_FOS1_PATH, retry=base._DEFAULT_RETRY
    )

    fos_eq(
        fos,
        name=_TEST_BIGTABLE_FOS1_ID,
        resource_name=_TEST_BIGTABLE_FOS1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_BIGTABLE_FOS1_LABELS,
        type=FeatureOnlineStoreType.BIGTABLE,
    )


@pytest.mark.parametrize("create_request_timeout", [None, 1.0])
def test_create(
    create_request_timeout,
    create_bigtable_fos_mock,
    get_fos_mock,
    fos_logger_mock,
    sync=True,
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fos = FeatureOnlineStore.create_bigtable_store(
        _TEST_BIGTABLE_FOS1_ID,
        labels=_TEST_BIGTABLE_FOS1_LABELS,
        create_request_timeout=create_request_timeout,
        sync=sync,
    )

    if not sync:
        fos.wait()

    # When creating, the FeatureOnlineStore object doesn't have the path set.
    expected_feature_online_store = types.feature_online_store_v1.FeatureOnlineStore(
        bigtable=types.feature_online_store_v1.FeatureOnlineStore.Bigtable(
            auto_scaling=types.feature_online_store_v1.FeatureOnlineStore.Bigtable.AutoScaling(
                min_node_count=1,
                max_node_count=1,
                cpu_utilization_target=50,
            )
        ),
        labels=_TEST_BIGTABLE_FOS1_LABELS,
    )
    create_bigtable_fos_mock.assert_called_once_with(
        parent=_TEST_PARENT,
        feature_online_store=expected_feature_online_store,
        feature_online_store_id=_TEST_BIGTABLE_FOS1_ID,
        metadata=(),
        timeout=create_request_timeout,
    )

    fos_logger_mock.assert_has_calls(
        [
            call("Creating FeatureOnlineStore"),
            call(
                f"Create FeatureOnlineStore backing LRO: {create_bigtable_fos_mock.return_value.operation.name}"
            ),
            call(
                "FeatureOnlineStore created. Resource name: projects/test-project/locations/us-central1/featureOnlineStores/my_fos1"
            ),
            call("To use this FeatureOnlineStore in another session:"),
            call(
                "feature_online_store = aiplatform.FeatureOnlineStore('projects/test-project/locations/us-central1/featureOnlineStores/my_fos1')"
            ),
        ]
    )

    fos_eq(
        fos,
        name=_TEST_BIGTABLE_FOS1_ID,
        resource_name=_TEST_BIGTABLE_FOS1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_BIGTABLE_FOS1_LABELS,
        type=FeatureOnlineStoreType.BIGTABLE,
    )


@pytest.mark.parametrize("create_request_timeout", [None, 1.0])
def test_create_esf_optimized_store(
    create_request_timeout,
    create_esf_optimized_fos_mock,
    get_esf_optimized_fos_mock,
    fos_logger_mock,
    sync=True,
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fos = FeatureOnlineStore.create_optimized_store(
        _TEST_ESF_OPTIMIZED_FOS_ID,
        labels=_TEST_ESF_OPTIMIZED_FOS_LABELS,
        create_request_timeout=create_request_timeout,
        sync=sync,
    )

    if not sync:
        fos.wait()

    expected_feature_online_store = types.feature_online_store_v1.FeatureOnlineStore(
        optimized=types.feature_online_store_v1.FeatureOnlineStore.Optimized(),
        dedicated_serving_endpoint=types.feature_online_store_v1.FeatureOnlineStore.DedicatedServingEndpoint(),
        labels=_TEST_ESF_OPTIMIZED_FOS_LABELS,
    )
    create_esf_optimized_fos_mock.assert_called_once_with(
        parent=_TEST_PARENT,
        feature_online_store=expected_feature_online_store,
        feature_online_store_id=_TEST_ESF_OPTIMIZED_FOS_ID,
        metadata=(),
        timeout=create_request_timeout,
    )

    fos_logger_mock.assert_has_calls(
        [
            call("Creating FeatureOnlineStore"),
            call(
                "Create FeatureOnlineStore backing LRO:"
                f" {create_esf_optimized_fos_mock.return_value.operation.name}"
            ),
            call(
                "FeatureOnlineStore created. Resource name:"
                " projects/test-project/locations/us-central1/featureOnlineStores/my_esf_optimized_fos"
            ),
            call("To use this FeatureOnlineStore in another session:"),
            call(
                "feature_online_store ="
                " aiplatform.FeatureOnlineStore('projects/test-project/locations/us-central1/featureOnlineStores/my_esf_optimized_fos')"
            ),
        ]
    )

    fos_eq(
        fos,
        name=_TEST_ESF_OPTIMIZED_FOS_ID,
        resource_name=_TEST_ESF_OPTIMIZED_FOS_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_ESF_OPTIMIZED_FOS_LABELS,
        type=FeatureOnlineStoreType.OPTIMIZED,
    )


def test_create_psc_optimized_store_no_project_allowlist_raises_error():
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    with pytest.raises(
        ValueError,
        match=re.escape(
            "`project_allowlist` cannot be empty when `enable_private_service_connect` is"
            " set to true."
        ),
    ):
        FeatureOnlineStore.create_optimized_store(
            _TEST_PSC_OPTIMIZED_FOS_ID,
            labels=_TEST_PSC_OPTIMIZED_FOS_LABELS,
            enable_private_service_connect=True,
        )


def test_create_psc_optimized_store_empty_project_allowlist_raises_error():
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    with pytest.raises(
        ValueError,
        match=re.escape(
            "`project_allowlist` cannot be empty when `enable_private_service_connect` is"
            " set to true."
        ),
    ):
        FeatureOnlineStore.create_optimized_store(
            _TEST_PSC_OPTIMIZED_FOS_ID,
            enable_private_service_connect=True,
            project_allowlist=[],
        )


@pytest.mark.parametrize("create_request_timeout", [None, 1.0])
@pytest.mark.parametrize("sync", [True, False])
def test_create_psc_optimized_store(
    create_psc_optimized_fos_mock,
    get_psc_optimized_fos_mock,
    fos_logger_mock,
    create_request_timeout,
    sync,
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
    fos = FeatureOnlineStore.create_optimized_store(
        _TEST_PSC_OPTIMIZED_FOS_ID,
        labels=_TEST_PSC_OPTIMIZED_FOS_LABELS,
        create_request_timeout=create_request_timeout,
        enable_private_service_connect=True,
        project_allowlist=_TEST_PSC_PROJECT_ALLOWLIST,
    )

    if not sync:
        fos.wait()

    expected_feature_online_store = types.feature_online_store_v1.FeatureOnlineStore(
        optimized=types.feature_online_store_v1.FeatureOnlineStore.Optimized(),
        dedicated_serving_endpoint=types.feature_online_store_v1.FeatureOnlineStore.DedicatedServingEndpoint(
            private_service_connect_config=types.service_networking_v1.PrivateServiceConnectConfig(
                enable_private_service_connect=True,
                project_allowlist=_TEST_PSC_PROJECT_ALLOWLIST,
            )
        ),
        labels=_TEST_PSC_OPTIMIZED_FOS_LABELS,
    )
    create_psc_optimized_fos_mock.assert_called_once_with(
        parent=_TEST_PARENT,
        feature_online_store=expected_feature_online_store,
        feature_online_store_id=_TEST_PSC_OPTIMIZED_FOS_ID,
        metadata=(),
        timeout=create_request_timeout,
    )

    fos_logger_mock.assert_has_calls(
        [
            call("Creating FeatureOnlineStore"),
            call(
                "Create FeatureOnlineStore backing LRO:"
                f" {create_psc_optimized_fos_mock.return_value.operation.name}"
            ),
            call(
                "FeatureOnlineStore created. Resource name:"
                " projects/test-project/locations/us-central1/featureOnlineStores/my_psc_optimized_fos"
            ),
            call("To use this FeatureOnlineStore in another session:"),
            call(
                "feature_online_store ="
                " aiplatform.FeatureOnlineStore('projects/test-project/locations/us-central1/featureOnlineStores/my_psc_optimized_fos')"
            ),
        ]
    )

    fos_eq(
        fos,
        name=_TEST_PSC_OPTIMIZED_FOS_ID,
        resource_name=_TEST_PSC_OPTIMIZED_FOS_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_PSC_OPTIMIZED_FOS_LABELS,
        type=FeatureOnlineStoreType.OPTIMIZED,
    )


def test_list(list_fos_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    online_stores = FeatureOnlineStore.list()

    list_fos_mock.assert_called_once_with(request={"parent": _TEST_PARENT})
    assert len(online_stores) == len(_TEST_FOS_LIST)
    fos_eq(
        online_stores[0],
        name=_TEST_BIGTABLE_FOS1_ID,
        resource_name=_TEST_BIGTABLE_FOS1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_BIGTABLE_FOS1_LABELS,
        type=FeatureOnlineStoreType.BIGTABLE,
    )
    fos_eq(
        online_stores[1],
        name=_TEST_BIGTABLE_FOS2_ID,
        resource_name=_TEST_BIGTABLE_FOS2_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_BIGTABLE_FOS2_LABELS,
        type=FeatureOnlineStoreType.BIGTABLE,
    )
    fos_eq(
        online_stores[2],
        name=_TEST_BIGTABLE_FOS3_ID,
        resource_name=_TEST_BIGTABLE_FOS3_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_BIGTABLE_FOS3_LABELS,
        type=FeatureOnlineStoreType.BIGTABLE,
    )


@pytest.mark.parametrize("force", [True, False])
def test_delete(force, delete_fos_mock, get_fos_mock, fos_logger_mock, sync=True):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fos = FeatureOnlineStore(_TEST_BIGTABLE_FOS1_ID)
    fos.delete(force=force, sync=sync)

    if not sync:
        fos.wait()

    delete_fos_mock.assert_called_once_with(
        name=_TEST_BIGTABLE_FOS1_PATH,
        force=force,
    )

    fos_logger_mock.assert_has_calls(
        [
            call(
                "Deleting FeatureOnlineStore resource: projects/test-project/locations/us-central1/featureOnlineStores/my_fos1"
            ),
            call(
                f"Delete FeatureOnlineStore backing LRO: {delete_fos_mock.return_value.operation.name}"
            ),
            call(
                "FeatureOnlineStore resource projects/test-project/locations/us-central1/featureOnlineStores/my_fos1 deleted."
            ),
        ]
    )


def test_create_fv_none_source_raises_error(get_fos_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
    fos = FeatureOnlineStore(_TEST_BIGTABLE_FOS1_ID)

    with pytest.raises(
        ValueError,
        match=re.escape("Please specify a valid source."),
    ):
        fos.create_feature_view("bq_fv", None)


def test_create_fv_wrong_object_type_raises_error(get_fos_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
    fos = FeatureOnlineStore(_TEST_BIGTABLE_FOS1_ID)

    with pytest.raises(
        ValueError,
        match=re.escape("Only FeatureViewBigQuerySource is a supported source."),
    ):
        fos.create_feature_view("bq_fv", fos)


def test_create_bq_fv_bad_uri_raises_error(get_fos_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
    fos = FeatureOnlineStore(_TEST_BIGTABLE_FOS1_ID)

    with pytest.raises(
        ValueError,
        match=re.escape("Please specify URI in BigQuery source."),
    ):
        fos.create_feature_view(
            "bq_fv",
            FeatureViewBigQuerySource(uri=None, entity_id_columns=["entity_id"]),
        )


@pytest.mark.parametrize("entity_id_columns", [None, []])
def test_create_bq_fv_bad_entity_id_columns_raises_error(
    entity_id_columns, get_fos_mock
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
    fos = FeatureOnlineStore(_TEST_BIGTABLE_FOS1_ID)

    with pytest.raises(
        ValueError,
        match=re.escape("Please specify entity ID columns in BigQuery source."),
    ):
        fos.create_feature_view(
            "bq_fv",
            FeatureViewBigQuerySource(uri="hi", entity_id_columns=entity_id_columns),
        )


@pytest.mark.parametrize("create_request_timeout", [None, 1.0])
@pytest.mark.parametrize("sync", [True, False])
def test_create_bq_fv(
    create_request_timeout,
    sync,
    get_fos_mock,
    create_bq_fv_mock,
    get_fv_mock,
    fos_logger_mock,
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
    fos = FeatureOnlineStore(_TEST_BIGTABLE_FOS1_ID)

    fv = fos.create_feature_view(
        _TEST_FV1_ID,
        FeatureViewBigQuerySource(
            uri=_TEST_FV1_BQ_URI, entity_id_columns=_TEST_FV1_ENTITY_ID_COLUMNS
        ),
        labels=_TEST_FV1_LABELS,
        create_request_timeout=create_request_timeout,
    )

    if not sync:
        fos.wait()

    # When creating, the FeatureView object doesn't have the path set.
    expected_fv = types.feature_view.FeatureView(
        big_query_source=types.feature_view.FeatureView.BigQuerySource(
            uri=_TEST_FV1_BQ_URI,
            entity_id_columns=_TEST_FV1_ENTITY_ID_COLUMNS,
        ),
        labels=_TEST_FV1_LABELS,
    )
    create_bq_fv_mock.assert_called_with(
        parent=_TEST_BIGTABLE_FOS1_PATH,
        feature_view=expected_fv,
        feature_view_id=_TEST_FV1_ID,
        metadata=(),
        timeout=create_request_timeout,
    )

    fv_eq(
        fv_to_check=fv,
        name=_TEST_FV1_ID,
        resource_name=_TEST_FV1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FV1_LABELS,
    )

    fos_logger_mock.assert_has_calls(
        [
            call("Creating FeatureView"),
            call(
                f"Create FeatureView backing LRO: {create_bq_fv_mock.return_value.operation.name}"
            ),
            call(
                "FeatureView created. Resource name: projects/test-project/locations/us-central1/featureOnlineStores/my_fos1/featureViews/my_fv1"
            ),
            call("To use this FeatureView in another session:"),
            call(
                "feature_view = aiplatform.FeatureView('projects/test-project/locations/us-central1/featureOnlineStores/my_fos1/featureViews/my_fv1')"
            ),
        ]
    )


def test_create_embedding_fv(
    get_esf_optimized_fos_mock,
    create_embedding_fv_from_bq_mock,
    get_optimized_embedding_fv_mock,
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
    fos = FeatureOnlineStore(_TEST_ESF_OPTIMIZED_FOS_ID)

    embedding_fv = fos.create_feature_view(
        _TEST_OPTIMIZED_EMBEDDING_FV_ID,
        FeatureViewBigQuerySource(uri="hi", entity_id_columns=["entity_id"]),
        index_config=IndexConfig(
            embedding_column="embedding",
            dimensions=1536,
            filter_columns=["currency_code", "gender", "shipping_country_codes"],
            crowding_column="crowding",
            distance_measure_type=DistanceMeasureType.SQUARED_L2_DISTANCE,
            algorithm_config=TreeAhConfig(),
        ),
    )
    fv_eq(
        fv_to_check=embedding_fv,
        name=_TEST_OPTIMIZED_EMBEDDING_FV_ID,
        resource_name=_TEST_OPTIMIZED_EMBEDDING_FV_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FV1_LABELS,
    )
