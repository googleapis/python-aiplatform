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
from unittest.mock import call, patch
from google.api_core import operation as ga_operation

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from vertexai.resources.preview import (
    FeatureView,
)
import vertexai.resources.preview.feature_store.utils as fs_utils
import pytest
from google.cloud.aiplatform.compat.services import (
    feature_online_store_admin_service_client,
    feature_online_store_service_client,
)
from vertexai.resources.preview.feature_store import (
    feature_view,
)

from feature_store_constants import (
    _TEST_BIGTABLE_FOS1_ID,
    _TEST_BIGTABLE_FOS1_PATH,
    _TEST_EMBEDDING_FV1_PATH,
    _TEST_STRING_FILTER,
    _TEST_FV1_ID,
    _TEST_FV1_LABELS,
    _TEST_FV1_PATH,
    _TEST_FV2_ID,
    _TEST_FV2_LABELS,
    _TEST_FV2_PATH,
    _TEST_FV_FETCH1,
    _TEST_FV_LIST,
    _TEST_FV_SEARCH1,
    _TEST_FV_SYNC1,
    _TEST_FV_SYNC1_ID,
    _TEST_FV_SYNC1_PATH,
    _TEST_FV_SYNC2_ID,
    _TEST_FV_SYNC2_PATH,
    _TEST_FV_SYNC_LIST,
    _TEST_LOCATION,
    _TEST_OPTIMIZED_FV1_PATH,
    _TEST_OPTIMIZED_FV2_PATH,
    _TEST_PROJECT,
    _TEST_FV_SYNC1_RESPONSE,
)


pytestmark = pytest.mark.usefixtures("google_auth_mock")


@pytest.fixture
def fv_logger_mock():
    with patch.object(
        feature_view._LOGGER,
        "info",
        wraps=feature_view._LOGGER.info,
    ) as logger_mock:
        yield logger_mock


@pytest.fixture
def list_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "list_feature_views",
    ) as list_fv:
        list_fv.return_value = _TEST_FV_LIST
        yield list_fv


@pytest.fixture
def delete_fv_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "delete_feature_view",
    ) as delete_fv:
        delete_fv_lro_mock = mock.Mock(ga_operation.Operation)
        delete_fv.return_value = delete_fv_lro_mock
        yield delete_fv


@pytest.fixture
def get_fv_sync_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "get_feature_view_sync",
    ) as get_fv_sync_mock:
        get_fv_sync_mock.return_value = _TEST_FV_SYNC1
        yield get_fv_sync_mock


@pytest.fixture
def list_fv_syncs_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "list_feature_view_syncs",
    ) as list_fv_syncs_mock:
        list_fv_syncs_mock.return_value = _TEST_FV_SYNC_LIST
        yield list_fv_syncs_mock


@pytest.fixture
def sync_fv_sync_mock():
    with patch.object(
        feature_online_store_admin_service_client.FeatureOnlineStoreAdminServiceClient,
        "sync_feature_view",
    ) as sync_fv_sync_mock:
        sync_fv_sync_mock.return_value = _TEST_FV_SYNC1_RESPONSE
        yield sync_fv_sync_mock


@pytest.fixture
def fetch_feature_values_mock():
    with patch.object(
        feature_online_store_service_client.FeatureOnlineStoreServiceClient,
        "fetch_feature_values",
    ) as fetch_feature_values_mock:
        fetch_feature_values_mock.return_value = _TEST_FV_FETCH1
        yield fetch_feature_values_mock


@pytest.fixture
def search_nearest_entities_mock():
    with patch.object(
        feature_online_store_service_client.FeatureOnlineStoreServiceClient,
        "search_nearest_entities",
    ) as search_nearest_entities_mock:
        search_nearest_entities_mock.return_value = _TEST_FV_SEARCH1
        yield search_nearest_entities_mock


def fv_eq(
    fv_to_check: FeatureView,
    name: str,
    resource_name: str,
    project: str,
    location: str,
    labels: Dict[str, str],
):
    """Check if a FeatureView has the appropriate values set."""
    assert fv_to_check.name == name
    assert fv_to_check.resource_name == resource_name
    assert fv_to_check.project == project
    assert fv_to_check.location == location
    assert fv_to_check.labels == labels


def fv_sync_eq(
    fv_sync_to_check: FeatureView.FeatureViewSync,
    name: str,
    resource_name: str,
    project: str,
    location: str,
):
    """Check if a FeatureViewSync has the appropriate values set."""
    assert fv_sync_to_check.name == name
    assert fv_sync_to_check.resource_name == resource_name
    assert fv_sync_to_check.project == project
    assert fv_sync_to_check.location == location


def test_init_with_fv_id_and_no_fos_id_raises_error(get_fv_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Since feature view is not provided as a path, please specify"
            + " feature_online_store_id."
        ),
    ):
        FeatureView(_TEST_FV1_ID)


def test_init_with_fv_id(get_fv_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fv = FeatureView(_TEST_FV1_ID, feature_online_store_id=_TEST_BIGTABLE_FOS1_ID)

    get_fv_mock.assert_called_once_with(
        name=_TEST_FV1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    fv_eq(
        fv_to_check=fv,
        name=_TEST_FV1_ID,
        resource_name=_TEST_FV1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FV1_LABELS,
    )


def test_init_with_fv_path(get_fv_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fv = FeatureView(_TEST_FV1_PATH)

    get_fv_mock.assert_called_once_with(
        name=_TEST_FV1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    fv_eq(
        fv_to_check=fv,
        name=_TEST_FV1_ID,
        resource_name=_TEST_FV1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FV1_LABELS,
    )


def test_list(list_fv_mock, get_fos_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    feature_views = FeatureView.list(feature_online_store_id=_TEST_BIGTABLE_FOS1_ID)

    list_fv_mock.assert_called_once_with(request={"parent": _TEST_BIGTABLE_FOS1_PATH})
    assert len(feature_views) == len(_TEST_FV_LIST)

    fv_eq(
        feature_views[0],
        name=_TEST_FV1_ID,
        resource_name=_TEST_FV1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FV1_LABELS,
    )
    fv_eq(
        feature_views[1],
        name=_TEST_FV2_ID,
        resource_name=_TEST_FV2_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FV2_LABELS,
    )


def test_delete(delete_fv_mock, fv_logger_mock, get_fos_mock, get_fv_mock, sync=True):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fv = FeatureView(name=_TEST_FV1_ID, feature_online_store_id=_TEST_BIGTABLE_FOS1_ID)
    fv.delete()

    if not sync:
        fv.wait()

    delete_fv_mock.assert_called_once_with(name=_TEST_FV1_PATH)

    fv_logger_mock.assert_has_calls(
        [
            call(
                "Deleting FeatureView resource: projects/test-project/locations/us-central1/featureOnlineStores/my_fos1/featureViews/my_fv1"
            ),
            call(
                f"Delete FeatureView backing LRO: {delete_fv_mock.return_value.operation.name}"
            ),
            call(
                "FeatureView resource projects/test-project/locations/us-central1/featureOnlineStores/my_fos1/featureViews/my_fv1 deleted."
            ),
        ]
    )


def test_get_sync(get_fv_mock, get_fv_sync_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fv_sync = FeatureView(_TEST_FV1_PATH).get_sync(_TEST_FV_SYNC1_ID)

    get_fv_mock.assert_called_once_with(
        name=_TEST_FV1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    get_fv_sync_mock.assert_called_once_with(
        name=_TEST_FV_SYNC1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    fv_sync_eq(
        fv_sync_to_check=fv_sync,
        name=_TEST_FV_SYNC1_ID,
        resource_name=_TEST_FV_SYNC1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )


def test_list_syncs(get_fv_mock, list_fv_syncs_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fv_syncs = FeatureView(_TEST_FV1_PATH).list_syncs()

    get_fv_mock.assert_called_once_with(
        name=_TEST_FV1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    list_fv_syncs_mock.assert_called_once_with(request={"parent": _TEST_FV1_PATH})
    assert len(fv_syncs) == len(_TEST_FV_SYNC_LIST)

    fv_sync_eq(
        fv_sync_to_check=fv_syncs[0],
        name=_TEST_FV_SYNC1_ID,
        resource_name=_TEST_FV_SYNC1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )

    fv_sync_eq(
        fv_sync_to_check=fv_syncs[1],
        name=_TEST_FV_SYNC2_ID,
        resource_name=_TEST_FV_SYNC2_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )


def test_on_demand_sync(get_fv_mock, get_fv_sync_mock, sync_fv_sync_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fv_sync = FeatureView(_TEST_FV1_PATH).sync()

    get_fv_mock.assert_called_once_with(
        name=_TEST_FV1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    sync_fv_sync_mock.assert_called_once_with(
        request={"feature_view": _TEST_FV1_PATH},
    )

    get_fv_sync_mock.assert_called_once_with(
        name=_TEST_FV_SYNC1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    fv_sync_eq(
        fv_sync_to_check=fv_sync,
        name=_TEST_FV_SYNC1_ID,
        resource_name=_TEST_FV_SYNC1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
    )


@pytest.mark.parametrize("output_type", ["dict", "proto"])
def test_fetch_feature_values_bigtable(
    get_fos_mock, get_fv_mock, fetch_feature_values_mock, fv_logger_mock, output_type
):
    if output_type == "dict":
        fv_dict = FeatureView(_TEST_FV1_PATH).read(key=["key1"]).to_dict()
        assert fv_dict == {
            "features": [{"name": "key1", "value": {"string_value": "value1"}}]
        }
    elif output_type == "proto":
        fv_proto = FeatureView(_TEST_FV1_PATH).read(key=["key1"]).to_proto()
        assert fv_proto == _TEST_FV_FETCH1

    fv_logger_mock.assert_has_calls(
        [
            call("Connecting to Bigtable online store name my_fos1"),
        ]
    )


@pytest.mark.parametrize("output_type", ["dict", "proto"])
def test_fetch_feature_values_optimized(
    get_esf_optimized_fos_mock,
    get_optimized_fv_mock,
    fetch_feature_values_mock,
    fv_logger_mock,
    output_type,
):
    if output_type == "dict":
        fv_dict = FeatureView(_TEST_OPTIMIZED_FV1_PATH).read(key=["key1"]).to_dict()
        assert fv_dict == {
            "features": [{"name": "key1", "value": {"string_value": "value1"}}]
        }
    elif output_type == "proto":
        fv_proto = FeatureView(_TEST_OPTIMIZED_FV1_PATH).read(key=["key1"]).to_proto()
        assert fv_proto == _TEST_FV_FETCH1

    fv_logger_mock.assert_has_calls(
        [
            call(
                "Public endpoint for the optimized online store my_esf_optimized_fos is test-esf-endpoint"
            ),
        ]
    )


def test_fetch_feature_values_optimized_no_endpoint(
    get_esf_optimized_fos_no_endpoint_mock,
    get_optimized_fv_no_endpointmock,
    fetch_feature_values_mock,
):
    """Tests that the public endpoint is not created for the optimized online store."""
    with pytest.raises(
        fs_utils.PublicEndpointNotFoundError,
        match=re.escape(
            "Public endpoint is not created yet for the optimized online "
            "store:my_esf_optimised_fos2. Please run sync and wait for it "
            "to complete."
        ),
    ):
        FeatureView(_TEST_OPTIMIZED_FV2_PATH).read(key=["key1"]).to_dict()


@pytest.mark.parametrize("output_type", ["dict", "proto"])
def test_search_nearest_entities(
    get_esf_optimized_fos_mock,
    get_embedding_fv_mock,
    search_nearest_entities_mock,
    fv_logger_mock,
    output_type,
):
    if output_type == "dict":
        fv_dict = (
            # Test with entity_id input.
            FeatureView(_TEST_EMBEDDING_FV1_PATH)
            .search(
                entity_id="key1",
                neighbor_count=2,
                string_filters=[_TEST_STRING_FILTER],
                per_crowding_attribute_neighbor_count=1,
                return_full_entity=True,
                approximate_neighbor_candidates=3,
                leaf_nodes_search_fraction=0.5,
            )
            .to_dict()
        )
        assert fv_dict == {
            "neighbors": [{"distance": 0.1, "entity_id": "neighbor_entity_id_1"}]
        }
    elif output_type == "proto":
        fv_proto = (
            # Test with embedding_value input.
            FeatureView(_TEST_EMBEDDING_FV1_PATH)
            .search(embedding_value=[0.1, 0.2, 0.3])
            .to_proto()
        )
        assert fv_proto == _TEST_FV_SEARCH1

    fv_logger_mock.assert_has_calls(
        [
            call(
                "Public endpoint for the optimized online store my_esf_optimized_fos"
                " is test-esf-endpoint"
            ),
        ]
    )


def test_search_nearest_entities_without_entity_id_or_embedding(
    get_esf_optimized_fos_mock,
    get_embedding_fv_mock,
    search_nearest_entities_mock,
    fv_logger_mock,
):
    try:
        FeatureView(_TEST_EMBEDDING_FV1_PATH).search().to_proto()
        assert not search_nearest_entities_mock.called
    except ValueError as e:
        error_msg = (
            "Either entity_id or embedding_value needs to be provided for search."
        )
        assert str(e) == error_msg


def test_search_nearest_entities_no_endpoint(
    get_esf_optimized_fos_no_endpoint_mock,
    get_optimized_fv_no_endpointmock,
    fetch_feature_values_mock,
):
    """Tests that the public endpoint is not created for the optimized online store."""
    try:
        FeatureView(_TEST_OPTIMIZED_FV2_PATH).search(entity_id="key1").to_dict()
        assert not fetch_feature_values_mock.called
    except fs_utils.PublicEndpointNotFoundError as e:
        assert isinstance(e, fs_utils.PublicEndpointNotFoundError)
        error_msg = (
            "Public endpoint is not created yet for the optimized online "
            "store:my_esf_optimised_fos2. Please run sync and wait for it "
            "to complete."
        )
        assert str(e) == error_msg
