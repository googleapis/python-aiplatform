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
import uuid

from unittest import mock
from importlib import reload
from unittest.mock import patch

from google.api_core import operation
from google.protobuf import field_mask_pb2

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1.services.index_service import (
    client as index_service_client,
)

from google.cloud.aiplatform_v1.types import index as gca_index

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"


# index
_TEST_INDEX_ID = "index_id"
_TEST_INDEX_NAME = f"{_TEST_PARENT}/indexes/{_TEST_INDEX_ID}"
_TEST_INDEX_DISPLAY_NAME = f"index_display_name"
_TEST_CONTENTS_DELTA_URI = f"gs://contents"
_TEST_IS_COMPLETE_OVERWRITE = False
_TEST_INDEX_DISTANCE_MEASURE_TYPE = "SQUARED_L2_DISTANCE"
_TEST_INDEX_CONFIG = aiplatform.MatchingEngineIndexConfig(
    dimensions=100,
    algorithm_config=aiplatform.MatchingEngineBruteForceAlgorithmConfig(),
    approximate_neighbors_count=150,
    distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
)

_TEST_INDEX_DESCRIPTION = f"index_description"


_TEST_LABELS = {"my_key": "my_value"}
_TEST_DISPLAY_NAME_UPDATE = "my new display name"
_TEST_DESCRIPTION_UPDATE = "my description update"
_TEST_LABELS_UPDATE = {"my_key_update": "my_value_update"}

# request_metadata
_TEST_REQUEST_METADATA = ()

# Lists
_TEST_INDEX_LIST = [
    gca_index.Index(
        name=_TEST_INDEX_NAME,
        display_name=_TEST_INDEX_DISPLAY_NAME,
        description=_TEST_INDEX_DESCRIPTION,
    ),
    gca_index.Index(
        name=_TEST_INDEX_NAME,
        display_name=_TEST_INDEX_DISPLAY_NAME,
        description=_TEST_INDEX_DESCRIPTION,
    ),
    gca_index.Index(
        name=_TEST_INDEX_NAME,
        display_name=_TEST_INDEX_DISPLAY_NAME,
        description=_TEST_INDEX_DESCRIPTION,
    ),
]


def uuid_mock():
    return uuid.UUID(int=1)


# All Index Mocks
@pytest.fixture
def get_index_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "get_index"
    ) as get_index_mock:
        get_index_mock.return_value = gca_index.Index(
            name=_TEST_INDEX_NAME,
            display_name=_TEST_INDEX_DISPLAY_NAME,
            description=_TEST_INDEX_DESCRIPTION,
        )
        yield get_index_mock


@pytest.fixture
def update_index_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "update_index"
    ) as update_index_mock:
        update_index_lro_mock = mock.Mock(operation.Operation)
        update_index_mock.return_value = update_index_lro_mock
        yield update_index_mock


@pytest.fixture
def list_indexes_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "list_indexes"
    ) as list_indexes_mock:
        list_indexes_mock.return_value = _TEST_INDEX_LIST
        yield list_indexes_mock


@pytest.fixture
def delete_index_mock():
    with mock.patch.object(
        index_service_client.IndexServiceClient, "delete_index"
    ) as delete_index_mock:
        delete_index_lro_mock = mock.Mock(operation.Operation)
        delete_index_mock.return_value = delete_index_lro_mock
        yield delete_index_mock


@pytest.fixture
def create_index_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "create_index"
    ) as create_index_mock:
        create_index_lro_mock = mock.Mock(operation.Operation)
        create_index_lro_mock.result.return_value = gca_index.Index(
            name=_TEST_INDEX_NAME,
            display_name=_TEST_INDEX_DISPLAY_NAME,
            description=_TEST_INDEX_DESCRIPTION,
        )
        create_index_mock.return_value = create_index_lro_mock
        yield create_index_mock


class TestMatchingEngineIndex:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize("index_name", [_TEST_INDEX_ID, _TEST_INDEX_NAME])
    def test_init_index(self, index_name, get_index_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=index_name)

        get_index_mock.assert_called_once_with(
            name=my_index.resource_name, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_index_mock")
    def test_update_index(self, update_index_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=_TEST_INDEX_ID)
        my_index.update(
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
            config=_TEST_INDEX_CONFIG,
            is_complete_overwrite=_TEST_IS_COMPLETE_OVERWRITE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
        )

        expected = gca_index.Index(
            name=_TEST_INDEX_NAME,
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            metadata={
                "config": _TEST_INDEX_CONFIG.as_dict(),
                "contentsDeltaUri": _TEST_CONTENTS_DELTA_URI,
                "isCompleteOverwrite": _TEST_IS_COMPLETE_OVERWRITE,
            },
            description=_TEST_DESCRIPTION_UPDATE,
        )

        update_index_mock.assert_called_once_with(
            index=expected,
            update_mask=field_mask_pb2.FieldMask(
                paths=["labels", "display_name", "description"]
            ),
            metadata=_TEST_REQUEST_METADATA,
        )

    def test_list_indexes(self, list_indexes_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_indexes_list = aiplatform.MatchingEngineIndex.list()

        list_indexes_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT, "filter": None}
        )
        assert len(my_indexes_list) == len(_TEST_INDEX_LIST)
        for my_index in my_indexes_list:
            assert type(my_index) == aiplatform.MatchingEngineIndex

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_index_mock")
    def test_delete_index(self, delete_index_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=_TEST_INDEX_ID)
        my_index.delete(sync=sync)

        if not sync:
            my_index.wait()

        delete_index_mock.assert_called_once_with(name=my_index.resource_name)

    @pytest.mark.usefixtures("get_index_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_index(self, create_index_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex.create(
            index_id=_TEST_INDEX_ID,
            display_name=_TEST_INDEX_DISPLAY_NAME,
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
            config=_TEST_INDEX_CONFIG,
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        if not sync:
            my_index.wait()

        expected = gca_index.Index(
            name=_TEST_INDEX_ID,
            display_name=_TEST_INDEX_DISPLAY_NAME,
            metadata={
                "config": _TEST_INDEX_CONFIG.as_dict(),
                "contentsDeltaUri": _TEST_CONTENTS_DELTA_URI,
            },
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
        )
        create_index_mock.assert_called_once_with(
            parent=_TEST_PARENT, index=expected, metadata=_TEST_REQUEST_METADATA,
        )
