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
from google.cloud.aiplatform import _featurestores as featurestores
from tests.system.aiplatform import e2e_base


class TestFeaturestore(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertex-sdk-e2e-feature-store-test"

    def _make_resource_id(self, key: str) -> str:
        """Helper method to make unique resource_ids.

        Args:
            key (str): Required. Identifier for the resource id.
        Returns:
            Unique resource id.
        """
        return self._make_display_name(key=key).replace("-", "_")[:60]

    def test_create_and_get_resources(self, shared_state):

        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        # Featurestore
        featurestore_id = self._make_resource_id(key="featurestore")
        featurestore = featurestores.Featurestore.create(
            featurestore_id=featurestore_id
        )
        shared_state["resources"] = [featurestore]

        get_featurestore = featurestores.Featurestore(
            featurestore_name=featurestore.resource_name
        )
        assert featurestore.resource_name == get_featurestore.resource_name

        list_featurestores = featurestores.Featurestore.list()
        assert len(list_featurestores) > 0

        # EntityType
        entity_type_id = self._make_resource_id(key="entity_type")
        entity_type = featurestore.create_entity_type(entity_type_id=entity_type_id)

        get_entity_type = featurestore.get_entity_type(
            entity_type_name=entity_type.resource_name
        )
        assert entity_type.resource_name == get_entity_type.resource_name

        list_entity_types = featurestore.list_entity_types()
        assert len(list_entity_types) > 0

        # Feature
        feature_id = self._make_resource_id(key="feature")
        feature = entity_type.create_feature(feature_id=feature_id, value_type="DOUBLE")

        get_feature = entity_type.get_feature(feature_name=feature.resource_name)
        assert feature.resource_name == get_feature.resource_name

        list_features = entity_type.list_features()
        assert len(list_features) > 0

        batch_feature_id1 = self._make_resource_id(key="batch_feature_id1")
        batch_feature_id2 = self._make_resource_id(key="batch_feature_id2")
        feature_configs = {
            batch_feature_id1: {"value_type": "INT64"},
            batch_feature_id2: {"value_type": "BOOL"},
        }
        entity_type.batch_create_features(feature_configs=feature_configs)

        list_searched_features = featurestores.Feature.search()
        assert len(list_searched_features) >= 1
