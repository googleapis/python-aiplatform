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


from google.cloud import aiplatform
from typing import Dict

#  [START aiplatform_sdk_explain_tabular_sample]
def explain_tabular_sample(project: str, location: str, endpoint_id: str, instance_dict: Dict):

    aiplatform.init(project=project, location=location)

    endpoint = aiplatform.Endpoint(endpoint_id)

    response = endpoint.explain(instances=[instance_dict], parameters={})

    for prediction_ in response.predictions:
        print(prediction_)


#  [END aiplatform_sdk_explain_tabular_sample]
