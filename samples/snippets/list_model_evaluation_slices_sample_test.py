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


import list_model_evaluation_slices_sample

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
MODEL_ID = "3512561418744365056"
EVALUATION_ID = "9035588644970168320"

KNOWN_EVALUATION_SLICE = "projects/580378083368/locations/us-central1/models/3512561418744365056/evaluations/9035588644970168320/slices/6481571820677004173"


def test_ucaip_generated_get_model_evaluation_slices_sample(capsys):
    list_model_evaluation_slices_sample.list_model_evaluation_slices_sample(
        project=PROJECT_ID, model_id=MODEL_ID, evaluation_id=EVALUATION_ID
    )
    out, _ = capsys.readouterr()
    assert KNOWN_EVALUATION_SLICE in out
