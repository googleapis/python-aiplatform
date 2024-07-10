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
from typing import Dict, List
from unittest import mock
from unittest.mock import call, patch

from google.auth import credentials as auth_credentials
from google.api_core import operation as ga_operation
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from vertexai.resources.preview.feature_store import (
    feature_group,
)
from vertexai.resources.preview import (
    FeatureGroup,
)
from vertexai.resources.preview.feature_store import (
    FeatureGroupBigQuerySource,
)
import pytest
from google.cloud.aiplatform.compat.services import (
    feature_registry_service_client,
)
from google.cloud.aiplatform.compat import types


from feature_store_constants import (
    _TEST_PARENT,
    _TEST_PROJECT,
    _TEST_LOCATION,
    _TEST_FG1,
    _TEST_FG1_ID,
    _TEST_FG1_PATH,
    _TEST_FG1_BQ_URI,
    _TEST_FG1_ENTITY_ID_COLUMNS,
    _TEST_FG1_LABELS,
    _TEST_FG2_ID,
    _TEST_FG2_PATH,
    _TEST_FG2_BQ_URI,
    _TEST_FG2_ENTITY_ID_COLUMNS,
    _TEST_FG2_LABELS,
    _TEST_FG3_ID,
    _TEST_FG3_PATH,
    _TEST_FG3_BQ_URI,
    _TEST_FG3_ENTITY_ID_COLUMNS,
    _TEST_FG3_LABELS,
    _TEST_FG_LIST,
    _TEST_FG1_F1,
    _TEST_FG1_F1_ID,
    _TEST_FG1_F1_PATH,
    _TEST_FG1_F1_DESCRIPTION,
    _TEST_FG1_F1_LABELS,
    _TEST_FG1_F1_POINT_OF_CONTACT,
    _TEST_FG1_F2,
    _TEST_FG1_F2_ID,
    _TEST_FG1_F2_PATH,
    _TEST_FG1_F2_DESCRIPTION,
    _TEST_FG1_F2_LABELS,
    _TEST_FG1_F2_POINT_OF_CONTACT,
    _TEST_FG1_F2_VERSION_COLUMN_NAME,
    _TEST_FG1_FEATURE_LIST,
)
from test_feature import feature_eq


pytestmark = pytest.mark.usefixtures("google_auth_mock")


@pytest.fixture
def fg_logger_mock():
    with patch.object(
        feature_group._LOGGER,
        "info",
        wraps=feature_group._LOGGER.info,
    ) as logger_mock:
        yield logger_mock


@pytest.fixture
def create_fg_mock():
    with patch.object(
        feature_registry_service_client.FeatureRegistryServiceClient,
        "create_feature_group",
    ) as create_fg_mock:
        create_fg_lro_mock = mock.Mock(ga_operation.Operation)
        create_fg_lro_mock.result.return_value = _TEST_FG1
        create_fg_mock.return_value = create_fg_lro_mock
        yield create_fg_mock


@pytest.fixture
def list_fg_mock():
    with patch.object(
        feature_registry_service_client.FeatureRegistryServiceClient,
        "list_feature_groups",
    ) as list_fg_mock:
        list_fg_mock.return_value = _TEST_FG_LIST
        yield list_fg_mock


@pytest.fixture
def delete_fg_mock():
    with patch.object(
        feature_registry_service_client.FeatureRegistryServiceClient,
        "delete_feature_group",
    ) as delete_fg_mock:
        delete_fg_lro_mock = mock.Mock(ga_operation.Operation)
        delete_fg_mock.return_value = delete_fg_lro_mock
        yield delete_fg_mock


@pytest.fixture
def create_feature_mock():
    with patch.object(
        feature_registry_service_client.FeatureRegistryServiceClient,
        "create_feature",
    ) as create_feature_mock:
        create_feature_lro_mock = mock.Mock(ga_operation.Operation)
        create_feature_lro_mock.result.return_value = _TEST_FG1_F1
        create_feature_mock.return_value = create_feature_lro_mock
        yield create_feature_mock


@pytest.fixture
def create_feature_with_version_column_mock():
    with patch.object(
        feature_registry_service_client.FeatureRegistryServiceClient,
        "create_feature",
    ) as create_feature_mock:
        create_feature_lro_mock = mock.Mock(ga_operation.Operation)
        create_feature_lro_mock.result.return_value = _TEST_FG1_F2
        create_feature_mock.return_value = create_feature_lro_mock
        yield create_feature_mock


@pytest.fixture
def list_features_mock():
    with patch.object(
        feature_registry_service_client.FeatureRegistryServiceClient,
        "list_features",
    ) as list_features_mock:
        list_features_mock.return_value = _TEST_FG1_FEATURE_LIST
        yield list_features_mock


@pytest.fixture()
def mock_base_instantiate_client():
    with patch.object(
        aiplatform.base.VertexAiResourceNoun,
        "_instantiate_client",
    ) as base_instantiate_client_mock:
        base_instantiate_client_mock.return_value = mock.MagicMock()
        yield base_instantiate_client_mock


def fg_eq(
    fg_to_check: FeatureGroup,
    name: str,
    resource_name: str,
    source_uri: str,
    entity_id_columns: List[str],
    project: str,
    location: str,
    labels: Dict[str, str],
):
    """Check if a FeatureGroup has the appropriate values set."""
    assert fg_to_check.name == name
    assert fg_to_check.resource_name == resource_name
    assert fg_to_check.source == FeatureGroupBigQuerySource(
        uri=source_uri,
        entity_id_columns=entity_id_columns,
    )
    assert fg_to_check.project == project
    assert fg_to_check.location == location
    assert fg_to_check.labels == labels


@pytest.mark.parametrize(
    "feature_group_name",
    [_TEST_FG1_ID, _TEST_FG1_PATH],
)
def test_init(feature_group_name, get_fg_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fg = FeatureGroup(feature_group_name)

    get_fg_mock.assert_called_once_with(
        name=_TEST_FG1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    fg_eq(
        fg,
        name=_TEST_FG1_ID,
        resource_name=_TEST_FG1_PATH,
        source_uri=_TEST_FG1_BQ_URI,
        entity_id_columns=_TEST_FG1_ENTITY_ID_COLUMNS,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FG1_LABELS,
    )


def test_create_fg_no_source_raises_error():
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    with pytest.raises(
        ValueError,
        match=re.escape("Please specify a valid source."),
    ):
        FeatureGroup.create("fg")


def test_create_fg_bad_source_raises_error():
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    with pytest.raises(
        ValueError,
        match=re.escape("Only FeatureGroupBigQuerySource is a supported source."),
    ):
        FeatureGroup.create("fg", source=int(1))


def test_create_fg_no_source_bq_uri_raises_error():
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    with pytest.raises(
        ValueError,
        match=re.escape("Please specify URI in BigQuery source."),
    ):
        FeatureGroup.create(
            "fg", source=FeatureGroupBigQuerySource(uri=None, entity_id_columns=None)
        )


@pytest.mark.parametrize("create_request_timeout", [None, 1.0])
@pytest.mark.parametrize("sync", [True, False])
def test_create_fg(
    create_fg_mock, get_fg_mock, fg_logger_mock, create_request_timeout, sync
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fg = FeatureGroup.create(
        _TEST_FG1_ID,
        source=FeatureGroupBigQuerySource(
            uri=_TEST_FG1_BQ_URI,
            entity_id_columns=_TEST_FG1_ENTITY_ID_COLUMNS,
        ),
        labels=_TEST_FG1_LABELS,
        create_request_timeout=create_request_timeout,
        sync=sync,
    )

    if not sync:
        fg.wait()

    # When creating, the FeatureOnlineStore object doesn't have the path set.
    expected_fg = types.feature_group.FeatureGroup(
        name=_TEST_FG1_ID,
        big_query=types.feature_group.FeatureGroup.BigQuery(
            big_query_source=types.io.BigQuerySource(
                input_uri=_TEST_FG1_BQ_URI,
            ),
            entity_id_columns=_TEST_FG1_ENTITY_ID_COLUMNS,
        ),
        labels=_TEST_FG1_LABELS,
    )
    create_fg_mock.assert_called_once_with(
        parent=_TEST_PARENT,
        feature_group=expected_fg,
        feature_group_id=_TEST_FG1_ID,
        metadata=(),
        timeout=create_request_timeout,
    )

    fg_logger_mock.assert_has_calls(
        [
            call("Creating FeatureGroup"),
            call(
                f"Create FeatureGroup backing LRO: {create_fg_mock.return_value.operation.name}"
            ),
            call(
                "FeatureGroup created. Resource name: projects/test-project/locations/us-central1/featureGroups/my_fg1"
            ),
            call("To use this FeatureGroup in another session:"),
            call(
                "feature_group = aiplatform.FeatureGroup('projects/test-project/locations/us-central1/featureGroups/my_fg1')"
            ),
        ]
    )

    fg_eq(
        fg,
        name=_TEST_FG1_ID,
        resource_name=_TEST_FG1_PATH,
        source_uri=_TEST_FG1_BQ_URI,
        entity_id_columns=_TEST_FG1_ENTITY_ID_COLUMNS,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FG1_LABELS,
    )


def test_list(list_fg_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    feature_groups = FeatureGroup.list()

    list_fg_mock.assert_called_once_with(request={"parent": _TEST_PARENT})
    assert len(feature_groups) == len(_TEST_FG_LIST)
    fg_eq(
        feature_groups[0],
        name=_TEST_FG1_ID,
        resource_name=_TEST_FG1_PATH,
        source_uri=_TEST_FG1_BQ_URI,
        entity_id_columns=_TEST_FG1_ENTITY_ID_COLUMNS,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FG1_LABELS,
    )
    fg_eq(
        feature_groups[1],
        name=_TEST_FG2_ID,
        resource_name=_TEST_FG2_PATH,
        source_uri=_TEST_FG2_BQ_URI,
        entity_id_columns=_TEST_FG2_ENTITY_ID_COLUMNS,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FG2_LABELS,
    )
    fg_eq(
        feature_groups[2],
        name=_TEST_FG3_ID,
        resource_name=_TEST_FG3_PATH,
        source_uri=_TEST_FG3_BQ_URI,
        entity_id_columns=_TEST_FG3_ENTITY_ID_COLUMNS,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        labels=_TEST_FG3_LABELS,
    )


@pytest.mark.parametrize("force", [True, False])
@pytest.mark.parametrize("sync", [True])
def test_delete(delete_fg_mock, get_fg_mock, fg_logger_mock, force, sync):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fg = FeatureGroup(_TEST_FG1_ID)
    fg.delete(force=force, sync=sync)

    if not sync:
        fg.wait()

    delete_fg_mock.assert_called_once_with(
        name=_TEST_FG1_PATH,
        force=force,
    )

    fg_logger_mock.assert_has_calls(
        [
            call(
                "Deleting FeatureGroup resource: projects/test-project/locations/us-central1/featureGroups/my_fg1"
            ),
            call(
                f"Delete FeatureGroup backing LRO: {delete_fg_mock.return_value.operation.name}"
            ),
            call(
                "FeatureGroup resource projects/test-project/locations/us-central1/featureGroups/my_fg1 deleted."
            ),
        ]
    )


def test_get_feature(get_fg_mock, get_feature_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fg = FeatureGroup(_TEST_FG1_ID)
    feature = fg.get_feature(_TEST_FG1_F1_ID)

    get_feature_mock.assert_called_once_with(
        name=_TEST_FG1_F1_PATH,
        retry=base._DEFAULT_RETRY,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )


def test_get_feature_credentials_set_in_init(mock_base_instantiate_client):
    credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    aiplatform.init(
        project=_TEST_PROJECT, location=_TEST_LOCATION, credentials=credentials
    )

    mock_base_instantiate_client.return_value.get_feature_group.return_value = _TEST_FG1
    mock_base_instantiate_client.return_value.get_feature.return_value = _TEST_FG1_F1

    fg = FeatureGroup(_TEST_FG1_ID)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=credentials,
        appended_user_agent=None,
    )

    feature = fg.get_feature(_TEST_FG1_F1_ID)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=credentials,
        appended_user_agent=None,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )


def test_get_feature_from_feature_group_with_explicit_credentials(
    mock_base_instantiate_client,
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    mock_base_instantiate_client.return_value.get_feature_group.return_value = _TEST_FG1
    mock_base_instantiate_client.return_value.get_feature.return_value = _TEST_FG1_F1

    credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    fg = FeatureGroup(_TEST_FG1_ID, credentials=credentials)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=credentials,
        appended_user_agent=None,
    )

    feature = fg.get_feature(_TEST_FG1_F1_ID)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=credentials,
        appended_user_agent=None,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )


def test_get_feature_from_feature_group_with_explicit_credentials_overrides_init_credentials(
    mock_base_instantiate_client,
):
    init_credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    aiplatform.init(
        project=_TEST_PROJECT, location=_TEST_LOCATION, credentials=init_credentials
    )

    mock_base_instantiate_client.return_value.get_feature_group.return_value = _TEST_FG1
    mock_base_instantiate_client.return_value.get_feature.return_value = _TEST_FG1_F1

    credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    fg = FeatureGroup(_TEST_FG1_ID, credentials=credentials)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=credentials,
        appended_user_agent=None,
    )

    feature = fg.get_feature(_TEST_FG1_F1_ID)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=credentials,
        appended_user_agent=None,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )


def test_get_feature_with_explicit_credentials(mock_base_instantiate_client):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    mock_base_instantiate_client.return_value.get_feature_group.return_value = _TEST_FG1
    mock_base_instantiate_client.return_value.get_feature.return_value = _TEST_FG1_F1

    fg = FeatureGroup(_TEST_FG1_ID)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=mock.ANY,
        appended_user_agent=None,
    )

    credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    feature = fg.get_feature(_TEST_FG1_F1_ID, credentials=credentials)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=credentials,
        appended_user_agent=None,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )


def test_get_feature_with_explicit_credentials_overrides_init_credentials(
    mock_base_instantiate_client,
):
    init_credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    aiplatform.init(
        project=_TEST_PROJECT, location=_TEST_LOCATION, credentials=init_credentials
    )

    mock_base_instantiate_client.return_value.get_feature_group.return_value = _TEST_FG1
    mock_base_instantiate_client.return_value.get_feature.return_value = _TEST_FG1_F1

    fg = FeatureGroup(_TEST_FG1_ID)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=init_credentials,
        appended_user_agent=None,
    )

    credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    feature = fg.get_feature(_TEST_FG1_F1_ID, credentials=credentials)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=credentials,
        appended_user_agent=None,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )


def test_get_feature_with_explicit_credentials_overrides_feature_group_credentials(
    mock_base_instantiate_client,
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    mock_base_instantiate_client.return_value.get_feature_group.return_value = _TEST_FG1
    mock_base_instantiate_client.return_value.get_feature.return_value = _TEST_FG1_F1

    feature_group_credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    fg = FeatureGroup(_TEST_FG1_ID, credentials=feature_group_credentials)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=feature_group_credentials,
        appended_user_agent=None,
    )

    credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    feature = fg.get_feature(_TEST_FG1_F1_ID, credentials=credentials)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=credentials,
        appended_user_agent=None,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )


def test_get_feature_with_explicit_credentials_overrides_init_and_feature_group_credentials(
    mock_base_instantiate_client,
):
    init_credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    aiplatform.init(
        project=_TEST_PROJECT, location=_TEST_LOCATION, credentials=init_credentials
    )

    mock_base_instantiate_client.return_value.get_feature_group.return_value = _TEST_FG1
    mock_base_instantiate_client.return_value.get_feature.return_value = _TEST_FG1_F1

    feature_group_credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    fg = FeatureGroup(_TEST_FG1_ID, credentials=feature_group_credentials)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=feature_group_credentials,
        appended_user_agent=None,
    )

    credentials = mock.MagicMock(spec=auth_credentials.Credentials)
    feature = fg.get_feature(_TEST_FG1_F1_ID, credentials=credentials)
    mock_base_instantiate_client.assert_called_with(
        location=_TEST_LOCATION,
        credentials=credentials,
        appended_user_agent=None,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )


@pytest.mark.parametrize("create_request_timeout", [None, 1.0])
@pytest.mark.parametrize("sync", [True, False])
def test_create_feature(
    get_fg_mock,
    create_feature_mock,
    get_feature_mock,
    fg_logger_mock,
    create_request_timeout,
    sync,
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fg = FeatureGroup(_TEST_FG1_ID)
    feature = fg.create_feature(
        _TEST_FG1_F1_ID,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
        create_request_timeout=create_request_timeout,
        sync=sync,
    )

    if not sync:
        feature.wait()

    expected_feature = types.feature.Feature(
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )
    create_feature_mock.assert_called_once_with(
        parent=_TEST_FG1_PATH,
        feature=expected_feature,
        feature_id=_TEST_FG1_F1_ID,
        metadata=(),
        timeout=create_request_timeout,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )

    fg_logger_mock.assert_has_calls(
        [
            call("Creating Feature"),
            call(
                f"Create Feature backing LRO: {create_feature_mock.return_value.operation.name}"
            ),
            call(
                "Feature created. Resource name: projects/test-project/locations/us-central1/featureGroups/my_fg1/features/my_fg1_f1"
            ),
            call("To use this Feature in another session:"),
            call(
                "feature = aiplatform.Feature('projects/test-project/locations/us-central1/featureGroups/my_fg1/features/my_fg1_f1')"
            ),
        ]
    )


@pytest.mark.parametrize("create_request_timeout", [None, 1.0])
@pytest.mark.parametrize("sync", [True, False])
def test_create_feature_with_version_feature_column(
    get_fg_mock,
    create_feature_with_version_column_mock,
    get_feature_with_version_column_mock,
    fg_logger_mock,
    create_request_timeout,
    sync,
):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    fg = FeatureGroup(_TEST_FG1_ID)
    feature = fg.create_feature(
        _TEST_FG1_F2_ID,
        version_column_name=_TEST_FG1_F2_VERSION_COLUMN_NAME,
        description=_TEST_FG1_F2_DESCRIPTION,
        labels=_TEST_FG1_F2_LABELS,
        point_of_contact=_TEST_FG1_F2_POINT_OF_CONTACT,
        create_request_timeout=create_request_timeout,
        sync=sync,
    )

    if not sync:
        feature.wait()

    expected_feature = types.feature.Feature(
        version_column_name=_TEST_FG1_F2_VERSION_COLUMN_NAME,
        description=_TEST_FG1_F2_DESCRIPTION,
        labels=_TEST_FG1_F2_LABELS,
        point_of_contact=_TEST_FG1_F2_POINT_OF_CONTACT,
    )
    create_feature_with_version_column_mock.assert_called_once_with(
        parent=_TEST_FG1_PATH,
        feature=expected_feature,
        feature_id=_TEST_FG1_F2_ID,
        metadata=(),
        timeout=create_request_timeout,
    )

    feature_eq(
        feature,
        name=_TEST_FG1_F2_ID,
        resource_name=_TEST_FG1_F2_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F2_DESCRIPTION,
        labels=_TEST_FG1_F2_LABELS,
        point_of_contact=_TEST_FG1_F2_POINT_OF_CONTACT,
        version_column_name=_TEST_FG1_F2_VERSION_COLUMN_NAME,
    )

    fg_logger_mock.assert_has_calls(
        [
            call("Creating Feature"),
            call(
                f"Create Feature backing LRO: {create_feature_with_version_column_mock.return_value.operation.name}"
            ),
            call(
                "Feature created. Resource name: projects/test-project/locations/us-central1/featureGroups/my_fg1/features/my_fg1_f2"
            ),
            call("To use this Feature in another session:"),
            call(
                "feature = aiplatform.Feature('projects/test-project/locations/us-central1/featureGroups/my_fg1/features/my_fg1_f2')"
            ),
        ]
    )


def test_list_features(get_fg_mock, list_features_mock):
    aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    features = FeatureGroup(_TEST_FG1_ID).list_features()

    list_features_mock.assert_called_once_with(request={"parent": _TEST_FG1_PATH})
    assert len(features) == len(_TEST_FG1_FEATURE_LIST)
    feature_eq(
        features[0],
        name=_TEST_FG1_F1_ID,
        resource_name=_TEST_FG1_F1_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F1_DESCRIPTION,
        labels=_TEST_FG1_F1_LABELS,
        point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    )
    feature_eq(
        features[1],
        name=_TEST_FG1_F2_ID,
        resource_name=_TEST_FG1_F2_PATH,
        project=_TEST_PROJECT,
        location=_TEST_LOCATION,
        description=_TEST_FG1_F2_DESCRIPTION,
        labels=_TEST_FG1_F2_LABELS,
        point_of_contact=_TEST_FG1_F2_POINT_OF_CONTACT,
        version_column_name=_TEST_FG1_F2_VERSION_COLUMN_NAME,
    )
