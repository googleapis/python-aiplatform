# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import os

import list_model_evaluation_slices_sample

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
MODEL_ID = "5162251072873431040"
EVALUATION_ID = "5615675837586029221"

KNOWN_EVALUATION_SLICE = "/locations/us-central1/models/5162251072873431040/evaluations/5615675837586029221/slices/4322488217836113260"


def test_ucaip_generated_get_model_evaluation_slices_sample(capsys):
    list_model_evaluation_slices_sample.list_model_evaluation_slices_sample(
        project=PROJECT_ID, model_id=MODEL_ID, evaluation_id=EVALUATION_ID
    )
    out, _ = capsys.readouterr()
    assert KNOWN_EVALUATION_SLICE in out
