# Copyright 2021 Google LLC
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


from typing import Dict, List

from google.cloud import aiplatform


#  [START aiplatform_sdk_predict_tabular_classification_sample]
def predict_tabular_classification_sample(
    project: str,
    location: str,
    endpoint_name: str,
    instances: List[Dict],
):
    """
    Args
        project: Your project ID or project number.
        location: Region where Endpoint is located. For example, 'us-central1'.
        endpoint_name: A fully qualified endpoint name or endpoint ID. Example: "projects/123/locations/us-central1/endpoints/456" or
               "456" when project and location are initialized or passed.
        instances: A list of one or more instances (examples) to return a prediction for.
    """
    aiplatform.init(project=project, location=location)

    endpoint = aiplatform.Endpoint(endpoint_name)

    response = endpoint.predict(instances=instances)

    for prediction_ in response.predictions:
        print(prediction_)


#  [END aiplatform_sdk_predict_tabular_classification_sample]
