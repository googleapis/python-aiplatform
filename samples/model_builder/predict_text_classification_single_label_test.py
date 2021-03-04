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


import predict_text_classification_single_label

ENDPOINT_ID = "65372563341049856"  # text_classification_single_label
PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")

content = "My local greasy spoon diner has great food, even if the service is a bit slow"


def test_ucaip_generated_predict_text_classification_single_label_sample(capsys):

    predict_text_classification_single_label.predict_text_classification_single_label_mbsdk(
        project=PROJECT_ID, location='us-central1', endpoint_id=ENDPOINT_ID, content=content, 
    )

    out, _ = capsys.readouterr()
    assert "Prediction" in out