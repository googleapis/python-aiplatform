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
import pathlib


import predict_image_classification_sample

ENDPOINT_ID = "71213169107795968"  # permanent_50_flowers_endpoint
PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")

PATH_TO_IMG = pathlib.Path(__file__).parent.absolute() / "resources/daisy.jpg"


def test_ucaip_generated_predict_image_classification_sample(capsys):

    predict_image_classification_sample.predict_image_classification_sample(
        filename=PATH_TO_IMG, project=PROJECT_ID, endpoint_id=ENDPOINT_ID
    )

    out, _ = capsys.readouterr()
    assert "deployed_model_id:" in out
