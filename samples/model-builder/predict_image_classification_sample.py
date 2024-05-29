# Copyright 2022 Google LLC
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


#  [START aiplatform_sdk_predict_image_classification_sample]
import base64

from typing import List

from google.cloud import aiplatform


def predict_image_classification_sample(
    project: str,
    location: str,
    endpoint_name: str,
    images: List,
):
    '''
    Args
        project: Your project ID or project number.
        location: Region where Endpoint is located. For example, 'us-central1'.
        endpoint_name: A fully qualified endpoint name or endpoint ID. Example: "projects/123/locations/us-central1/endpoints/456" or
               "456" when project and location are initialized or passed.
        images: A list of one or more images to return a prediction for.
    '''
    aiplatform.init(project=project, location=location)

    endpoint = aiplatform.Endpoint(endpoint_name)

    instances = []
    for image in images:
        with open(image, "rb") as f:
            content = f.read()
        instances.append({"content": base64.b64encode(content).decode("utf-8")})

    response = endpoint.predict(instances=instances)

    for prediction_ in response.predictions:
        print(prediction_)


#  [END aiplatform_sdk_predict_image_classification_sample]
