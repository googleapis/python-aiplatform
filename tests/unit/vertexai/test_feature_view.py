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
    _TEST_FV3_ID,
    _TEST_FV3_LABELS,
    _TEST_FV3_PATH,
    _TEST_FV4_ID,
    _TEST_FV4_LABELS,
    _TEST_FV4_PATH,
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


@pytest.fixture
def transport_mock():
    with mock.patch(
        "google.cloud.aiplatform_v1.services.feature_online_store_service.transports.grpc.FeatureOnlineStoreServiceGrpcTransport"
    ) as transport:
        transport.return_value = mock.MagicMock(autospec=True)
        yield transport


@pytest.fixture
def grpc_insecure_channel_mock():
    import grpc

    with mock.patch.object(grpc, "insecure_channel", autospec=True) as channel:
        channel.return_value = mock.MagicMock(autospec=True)
        yield channel


@pytest.fixture
def client_mock():
    with mock.patch(
        "google.cloud.aiplatform_v1.services.feature_online_store_service.FeatureOnlineStoreServiceClient"
    ) as client_mock:
        yield client_mock


@pytest.fixture
def utils_client_with_override_mock():
    with mock.patch(
        "google.cloud.aiplatform.utils.FeatureOnlineStoreClientWithOverride"
    ) as client_mock:
        yield client_mock


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
    fv_eq(
        feature_views[2],
        name=_TEST_FV3_ID,
        resource_name=_TEST_FV3_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FV3_LABELS,
    )
    fv_eq(
        feature_views[3],
        name=_TEST_FV4_ID,
        resource_name=_TEST_FV4_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FV4_LABELS,
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


def test_ffv_optimized_psc_with_no_connection_options_raises_error(
    get_psc_optimized_fos_mock,
    get_optimized_fv_mock,
):
    with pytest.raises(ValueError) as excinfo:
        FeatureView(_TEST_OPTIMIZED_FV1_PATH).read(key=["key1"])

    assert str(excinfo.value) == (
        "Use `connection_options` to specify an IP address. Required for optimized online store with private service connect."
    )


def test_ffv_optimized_psc_with_no_connection_transport_raises_error(
    get_psc_optimized_fos_mock,
    get_optimized_fv_mock,
):
    with pytest.raises(ValueError) as excinfo:
        FeatureView(_TEST_OPTIMIZED_FV1_PATH).read(
            key=["key1"],
            connection_options=fs_utils.ConnectionOptions(
                host="1.2.3.4", transport=None
            ),
        )

    assert str(excinfo.value) == (
        "Unsupported connection transport type, got transport: None"
    )


def test_ffv_optimized_psc_with_bad_connection_transport_raises_error(
    get_psc_optimized_fos_mock,
    get_optimized_fv_mock,
):
    with pytest.raises(ValueError) as excinfo:
        FeatureView(_TEST_OPTIMIZED_FV1_PATH).read(
            key=["key1"],
            connection_options=fs_utils.ConnectionOptions(
                host="1.2.3.4", transport="hi"
            ),
        )

    assert str(excinfo.value) == (
        "Unsupported connection transport type, got transport: hi"
    )


@pytest.mark.parametrize("output_type", ["dict", "proto"])
def test_ffv_optimized_psc(
    get_psc_optimized_fos_mock,
    get_optimized_fv_mock,
    transport_mock,
    grpc_insecure_channel_mock,
    fetch_feature_values_mock,
    output_type,
):
    rsp = FeatureView(_TEST_OPTIMIZED_FV1_PATH).read(
        key=["key1"],
        connection_options=fs_utils.ConnectionOptions(
            host="1.2.3.4",
            transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
        ),
    )

    # Ensure that we create and use insecure channel to the target.
    grpc_insecure_channel_mock.assert_called_once_with("1.2.3.4:10002")
    transport_grpc_channel = transport_mock.call_args.kwargs["channel"]
    assert transport_grpc_channel == grpc_insecure_channel_mock.return_value

    if output_type == "dict":
        assert rsp.to_dict() == {
            "features": [{"name": "key1", "value": {"string_value": "value1"}}]
        }
    elif output_type == "proto":
        assert rsp.to_proto() == _TEST_FV_FETCH1


def test_same_connection_options_are_equal():
    opt1 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
    )
    opt2 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
    )
    assert opt1 == opt2


def test_different_host_in_connection_options_are_not_equal():
    opt1 = fs_utils.ConnectionOptions(
        host="1.1.1.2",
        transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
    )
    opt2 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
    )

    assert opt1 != opt2


def test_bad_transport_in_compared_connection_options_raises_error():
    opt1 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
    )
    opt2 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=None,
    )

    with pytest.raises(ValueError) as excinfo:
        assert opt1 != opt2

    assert str(excinfo.value) == (
        "Transport 'ConnectionOptions.InsecureGrpcChannel()' cannot be compared to transport 'None'."
    )


def test_bad_transport_in_connection_options_raises_error():
    opt1 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=None,
    )
    opt2 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
    )

    with pytest.raises(ValueError) as excinfo:
        assert opt1 != opt2

    assert str(excinfo.value) == ("Unsupported transport supplied: None")


def test_same_connection_options_have_same_hash():
    opt1 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
    )
    opt2 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
    )

    d = {}
    d[opt1] = "hi"
    assert d[opt2] == "hi"


@pytest.mark.parametrize(
    "hosts",
    [
        ("1.1.1.1", "1.1.1.2"),
        ("1.1.1.2", "1.1.1.1"),
        ("10.0.0.1", "9.9.9.9"),
    ],
)
def test_different_host_in_connection_options_have_different_hash(hosts):
    opt1 = fs_utils.ConnectionOptions(
        host=hosts[0],
        transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
    )
    opt2 = fs_utils.ConnectionOptions(
        host=hosts[1],
        transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
    )

    d = {}
    d[opt1] = "hi"
    assert opt2 not in d


@pytest.mark.parametrize(
    "transports",
    [
        (fs_utils.ConnectionOptions.InsecureGrpcChannel(), None),
        (None, fs_utils.ConnectionOptions.InsecureGrpcChannel()),
        (None, "hi"),
        ("hi", None),
    ],
)
def test_bad_transport_in_connection_options_have_different_hash(transports):
    opt1 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=transports[0],
    )
    opt2 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=transports[1],
    )

    d = {}
    d[opt1] = "hi"
    assert opt2 not in d


def test_diff_host_and_bad_transport_in_connection_options_have_different_hash():
    opt1 = fs_utils.ConnectionOptions(
        host="1.1.1.1",
        transport=None,
    )
    opt2 = fs_utils.ConnectionOptions(
        host="9.9.9.9",
        transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
    )

    d = {}
    d[opt1] = "hi"
    assert opt2 not in d


def test_ffv_optimized_psc_reuse_client_for_same_connection_options_in_same_ffv(
    get_psc_optimized_fos_mock,
    get_optimized_fv_mock,
    client_mock,
    transport_mock,
    grpc_insecure_channel_mock,
    fetch_feature_values_mock,
):
    fv = FeatureView(_TEST_OPTIMIZED_FV1_PATH)
    fv.read(
        key=["key1"],
        connection_options=fs_utils.ConnectionOptions(
            host="1.1.1.1",
            transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
        ),
    )
    fv.read(
        key=["key2"],
        connection_options=fs_utils.ConnectionOptions(
            host="1.1.1.1",
            transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
        ),
    )

    # Insecure channel and transport creation should only be done once.
    assert grpc_insecure_channel_mock.call_args_list == [mock.call("1.1.1.1:10002")]
    assert transport_mock.call_args_list == [
        mock.call(channel=grpc_insecure_channel_mock.return_value),
    ]


def test_ffv_optimized_psc_different_client_for_different_connection_options(
    get_psc_optimized_fos_mock,
    get_optimized_fv_mock,
    client_mock,
    transport_mock,
    grpc_insecure_channel_mock,
    fetch_feature_values_mock,
):
    # Return two different grpc channels each time insecure channel is called.
    import grpc

    grpc_chan1 = mock.MagicMock(spec=grpc.Channel)
    grpc_chan2 = mock.MagicMock(spec=grpc.Channel)
    grpc_insecure_channel_mock.side_effect = [grpc_chan1, grpc_chan2]

    fv = FeatureView(_TEST_OPTIMIZED_FV1_PATH)
    fv.read(
        key=["key1"],
        connection_options=fs_utils.ConnectionOptions(
            host="1.1.1.1",
            transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
        ),
    )
    fv.read(
        key=["key2"],
        connection_options=fs_utils.ConnectionOptions(
            host="1.2.3.4",
            transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
        ),
    )

    # Insecure channel and transport creation should be done twice - one for each different connection.
    assert grpc_insecure_channel_mock.call_args_list == [
        mock.call("1.1.1.1:10002"),
        mock.call("1.2.3.4:10002"),
    ]
    assert transport_mock.call_args_list == [
        mock.call(channel=grpc_chan1),
        mock.call(channel=grpc_chan2),
    ]


def test_ffv_optimized_psc_bad_gapic_client_raises_error(
    get_psc_optimized_fos_mock, get_optimized_fv_mock, utils_client_with_override_mock
):
    with pytest.raises(ValueError) as excinfo:
        FeatureView(_TEST_OPTIMIZED_FV1_PATH).read(
            key=["key1"],
            connection_options=fs_utils.ConnectionOptions(
                host="1.1.1.1",
                transport=fs_utils.ConnectionOptions.InsecureGrpcChannel(),
            ),
        )

    assert str(excinfo.value) == (
        f"Unexpected gapic class '{utils_client_with_override_mock.get_gapic_client_class.return_value}' used by internal client."
    )


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
