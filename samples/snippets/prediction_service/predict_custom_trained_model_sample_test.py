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

import base64
import os
import pathlib


import predict_custom_trained_model_sample

ENDPOINT_ID = "6119547468666372096"  # permanent_custom_flowers_model
PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")

PATH_TO_IMG = pathlib.Path(__file__).parent.absolute() / "resources/daisy.jpg"


def test_ucaip_generated_predict_custom_trained_model_sample(capsys):
    with open(PATH_TO_IMG, "rb") as f:
        file_content = f.read()
    encoded_content = base64.b64encode(file_content).decode("utf-8")

    instance_dict = {"image_bytes": {"b64": encoded_content}, "key": "0"}

    # Single instance as a dict
    predict_custom_trained_model_sample.predict_custom_trained_model_sample(
        instances=instance_dict, project=PROJECT_ID, endpoint_id=ENDPOINT_ID
    )

    # Multiple instances in a list
    predict_custom_trained_model_sample.predict_custom_trained_model_sample(
        instances=[instance_dict, instance_dict],
        project=PROJECT_ID,
        endpoint_id=ENDPOINT_ID,
    )

    out, _ = capsys.readouterr()
    assert "1.0" in out

    # Two sets of scores for multi-instance, one score for single instance
    assert out.count("scores") == 3
