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

from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base

_TEST_MATCHING_ENGINE_INDEX_ID = "index_id"
_TEST_MATCHING_ENGINE_INDEX_DISPLAY_NAME = "display_name"
_TEST_MATCHING_ENGINE_INDEX_DESCRIPTION = "description"
_TEST_INDEX_METADATA_SCHEMA_URI_UPDATE = f"gs://metadata_schema_uri/new_file"


_TEST_CONTENTS_DELTA_URI = f"gs://contents"
_TEST_IS_COMPLETE_OVERWRITE = False
_TEST_INDEX_DISTANCE_MEASURE_TYPE = "SQUARED_L2_DISTANCE"
_TEST_INDEX_CONFIG = aiplatform.MatchingEngineIndexConfig(
    dimensions=100,
    algorithm_config=aiplatform.MatchingEngineBruteForceAlgorithmConfig(),
    approximate_neighbors_count=150,
    distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
)


_TEST_LABELS = {"my_key": "my_value"}
_TEST_DISPLAY_NAME_UPDATE = "my new display name"
_TEST_DESCRIPTION_UPDATE = "my description update"
_TEST_INDEX_METADATA_SCHEMA_URI_UPDATE = f"gs://metadata_schema_uri/new_file"
_TEST_LABELS_UPDATE = {"my_key_update": "my_value_update"}


class TestFeaturestore(e2e_base.TestEndToEnd):

    _temp_prefix = "temp_vertex_sdk_e2e_featurestore_test"

    def test_create_get_list_matching_engine_index(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        existing_index_count = len(aiplatform.MatchingEngineIndex.list())

        # Create an index
        index = aiplatform.MatchingEngineIndex.create(
            index_id=_TEST_MATCHING_ENGINE_INDEX_ID,
            display_name=_TEST_MATCHING_ENGINE_INDEX_DISPLAY_NAME,
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
            config=_TEST_INDEX_CONFIG,
            description=_TEST_MATCHING_ENGINE_INDEX_DESCRIPTION,
            metadata_schema_uri=_TEST_INDEX_METADATA_SCHEMA_URI_UPDATE,
            labels=_TEST_LABELS,
        )

        shared_state["resources"] = [index]
        shared_state["index"] = index
        shared_state["index_name"] = index.resource_name

        # Verify that the retrieved index is the same
        get_index = aiplatform.MatchingEngineIndex(index_name=index.resource_name)
        assert index.resource_name == get_index.resource_name

        # Verify that the index count has increased
        list_indexes = aiplatform.MatchingEngineIndex.list()
        assert (len(list_indexes) - existing_index_count) == 1

        # Update the index
        updated_index = get_index.update(
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
            config=_TEST_INDEX_CONFIG,
            is_complete_overwrite=_TEST_IS_COMPLETE_OVERWRITE,
            description=_TEST_DESCRIPTION_UPDATE,
            metadata_schema_uri=_TEST_INDEX_METADATA_SCHEMA_URI_UPDATE,
            labels=_TEST_LABELS_UPDATE,
        )

        assert updated_index.display_name == _TEST_DISPLAY_NAME_UPDATE
        assert updated_index.description == _TEST_DESCRIPTION_UPDATE
        assert updated_index.labels == _TEST_LABELS

        # Delete index and check that count has returned to the starting value
        index.delete()
        list_indexes = aiplatform.MatchingEngineIndex.list()
        assert len(list_indexes) == existing_index_count
