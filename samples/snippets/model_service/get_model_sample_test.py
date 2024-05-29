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

import os

import get_model_sample

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
MODEL_ID = "3512561418744365056"  # permanent_50_flowers_model
KNOWN_MODEL = f"/locations/us-central1/models/{MODEL_ID}"


def test_ucaip_generated_get_model_sample(capsys):
    get_model_sample.get_model_sample(project=PROJECT_ID, model_id=MODEL_ID)
    out, _ = capsys.readouterr()
    assert KNOWN_MODEL in out
