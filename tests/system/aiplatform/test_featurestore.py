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

    def test_create_and_get_featurestore(self, shared_state):

        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        list_featurestores = featurestores.Featurestore.list()
        assert len(list_featurestores) >= 0

        list_searched_features = featurestores.Feature.search()
        assert len(list_searched_features) >= 0
