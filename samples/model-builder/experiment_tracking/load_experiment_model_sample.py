# Copyright 2023 Google LLC
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

from typing import Union

from google.cloud import aiplatform


#  [START aiplatform_sdk_load_experiment_model_sample]
def load_experiment_model_sample(
    artifact_id: str,
    project: str,
    location: str,
) -> Union["sklearn.base.BaseEstimator", "xgb.Booster", "tf.Module"]:  # noqa: F821:
    experiment_model = aiplatform.get_experiment_model(
        artifact_id=artifact_id, project=project, location=location
    )

    return experiment_model.load_model()


#  [END aiplatform_sdk_load_experiment_model_sample]
