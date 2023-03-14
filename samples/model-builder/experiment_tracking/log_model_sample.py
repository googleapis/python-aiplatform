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

from typing import Optional, Union

from google.cloud import aiplatform


#  [START aiplatform_sdk_log_model_sample]
def log_model_sample(
    experiment_name: str,
    run_name: str,
    project: str,
    location: str,
    model: Union[
        "sklearn.base.BaseEstimator", "xgb.Booster", "tf.Module"  # noqa: F821
    ],
    artifact_id: Optional[str] = None,
    uri: Optional[str] = None,
    input_example: Optional[
        Union[list, dict, "pd.DataFrame", "np.ndarray"]  # noqa: F821
    ] = None,  # noqa: F821
    display_name: Optional[str] = None,
) -> None:
    aiplatform.init(experiment=experiment_name, project=project, location=location)

    aiplatform.start_run(run=run_name, resume=True)

    aiplatform.log_model(
        model=model,
        artifact_id=artifact_id,
        uri=uri,
        input_example=input_example,
        display_name=display_name,
    )


#  [END aiplatform_sdk_log_model_sample]
