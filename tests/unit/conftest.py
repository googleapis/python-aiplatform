# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
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

import sys

collect_ignore = []

if sys.version_info > (3, 11):
    collect_ignore = [
        "aiplatform/test_cloud_profiler.py",
        "aiplatform/test_uploader.py",
        "aiplatform/test_uploader_main.py",
        "aiplatform/test_autologging.py",
        "aiplatform/test_explain_lit.py",
        "aiplatform/test_explain_saved_model_metadata_builder_tf2_test.py",
        "aiplatform/test_metadata_models.py",
        "aiplatform/test_endpoints.py",
        "aiplatform/test_model_evaluation.py",
        "aiplatform/test_models.py",
        "aiplatform/test_utils.py",
        "vertexai/test_reasoning_engines.py",
        "vertexai/test_model_utils.py",
        "vertexai/test_remote_training.py",
        "vertexai/test_serializers.py",
        "vertexai/test_vizier_hyperparameter_tuner.py",
    ]
