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


import predict_tabular_classification_sample

ENDPOINT_ID = "4966625964059525120"  # iris 1000
PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")

INSTANCE = {
    "petal_length": "1.4",
    "petal_width": "1.3",
    "sepal_length": "5.1",
    "sepal_width": "2.8",
}


def test_ucaip_generated_predict_tabular_classification_sample(capsys):

    predict_tabular_classification_sample.predict_tabular_classification_sample(
        instance_dict=INSTANCE, project=PROJECT_ID, endpoint_id=ENDPOINT_ID
    )

    out, _ = capsys.readouterr()
    assert "setosa" in out
