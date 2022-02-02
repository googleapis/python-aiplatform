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
_TEST_INDEX_METADATA_SCHEMA_URI_UPDATE = f"gs://metadata_schema_uri/new_file"


class TestFeaturestore(e2e_base.TestEndToEnd):

    _temp_prefix = "temp_vertex_sdk_e2e_featurestore_test"

    def test_create_get_list_matching_engine_index(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        existing_index_count = len(aiplatform.MatchingEngineIndex.list())

        # Create an index
        index_id = self._make_display_name(key=_TEST_MATCHING_ENGINE_INDEX_ID).replace(
            "-", "_"
        )[:60]
        index = aiplatform.MatchingEngineIndex.create(
            index_id=index_id,
            display_name=_TEST_MATCHING_ENGINE_INDEX_DISPLAY_NAME,
            metadata_schema_uri=_TEST_INDEX_METADATA_SCHEMA_URI_UPDATE,
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

        # Delete index and check that count has returned to the starting value
        index.delete()
        list_indexes = aiplatform.MatchingEngineIndex.list()
        assert len(list_indexes) == existing_index_count
