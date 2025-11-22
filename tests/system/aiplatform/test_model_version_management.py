# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

import tempfile
import uuid

import pytest

from google.cloud import aiplatform
from google.cloud import storage
from google.cloud.aiplatform.models import ModelRegistry

from tests.system.aiplatform import e2e_base
from tests.system.aiplatform import test_model_upload
from google.cloud.aiplatform.utils.gcs_utils import blob_from_uri


@pytest.mark.usefixtures("tear_down_resources")
class TestVersionManagement(e2e_base.TestEndToEnd):

    _temp_prefix = "temp_vertex_sdk_e2e_model_upload_test"

    def test_upload_deploy_manage_versioned_model(self, shared_state):
        """Upload XGBoost model from local file and deploy it for prediction. Additionally, update model name, description and labels"""

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        storage_client = storage.Client(project=e2e_base._PROJECT)
        model_blob = blob_from_uri(
            uri=test_model_upload._XGBOOST_MODEL_URI, client=storage_client
        )
        model_path = tempfile.mktemp() + ".my_model.xgb"
        model_blob.download_to_filename(filename=model_path)

        model_id = "my_model_id" + uuid.uuid4().hex
        version_description = "My description"
        version_aliases = ["system-test-model", "testing"]

        model = aiplatform.Model.upload_xgboost_model_file(
            model_file_path=model_path,
            version_aliases=version_aliases,
            model_id=model_id,
            version_description=version_description,
        )
        shared_state["resources"] = [model]

        staging_bucket = blob_from_uri(uri=model.uri, client=storage_client).bucket
        # Checking that the bucket is auto-generated
        assert "-vertex-staging-" in staging_bucket.name

        assert model.version_description == version_description
        assert model.version_aliases == version_aliases
        assert "default" in model.version_aliases

        model2 = aiplatform.Model.upload_xgboost_model_file(
            model_file_path=model_path, parent_model=model_id, is_default_version=False
        )
        shared_state["resources"].append(model2)

        assert model2.version_id == "2"
        assert model2.resource_name == model.resource_name
        assert model2.version_aliases == []

        # Test that VersionInfo properties are correct.
        model_info = model2.versioning_registry.get_version_info("testing")
        version_list = model2.versioning_registry.list_versions()
        assert len(version_list) == 2
        list_info = version_list[0]
        assert model_info.version_id == list_info.version_id == model.version_id
        assert (
            model_info.version_aliases
            == list_info.version_aliases
            == model.version_aliases
        )
        assert (
            model_info.version_description
            == list_info.version_description
            == model.version_description
        )
        assert (
            model_info.model_display_name
            == list_info.model_display_name
            == model.display_name
        )
        assert (
            model_info.version_update_time
            == list_info.version_update_time
            == model.version_update_time
        )

        # Test that get_model yields a new instance of `model`
        model_clone = model2.versioning_registry.get_model()
        assert model.resource_name == model_clone.resource_name
        assert model.version_id == model_clone.version_id
        assert model.name == model_clone.name

        # Test add and removal of aliases
        registry = ModelRegistry(model)
        registry.add_version_aliases(["new-alias"], "default")
        registry.remove_version_aliases(["testing"], "new-alias")
        model = registry.get_model("new-alias")
        assert "testing" not in model.version_aliases

        # Test deletion of a model version
        registry.delete_version("2")
        versions = registry.list_versions()
        assert "2" not in [version.version_id for version in versions]
