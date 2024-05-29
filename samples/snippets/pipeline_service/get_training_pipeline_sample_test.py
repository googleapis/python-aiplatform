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

import get_training_pipeline_sample

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")

# Permanent training pipeline of 50 flowers dataset
TRAINING_PIPELINE_ID = "1419759782528548864"
TRAINING_PIPELINE_DISPLAY_NAME = "permanent_50_flowers_pipeline"


def test_ucaip_generated_get_training_pipeline_sample(capsys):
    get_training_pipeline_sample.get_training_pipeline_sample(
        project=PROJECT_ID, training_pipeline_id=TRAINING_PIPELINE_ID
    )

    out, _ = capsys.readouterr()
    assert TRAINING_PIPELINE_DISPLAY_NAME in out
