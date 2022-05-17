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

from typing import Dict

from google.cloud import aiplatform


#  [START aiplatform_sdk_explain_tabular_sample]
def explain_tabular_sample(
    project: str, location: str, endpoint_id: str, instance_dict: Dict
):

    aiplatform.init(project=project, location=location)

    endpoint = aiplatform.Endpoint(endpoint_id)

    response = endpoint.explain(instances=[instance_dict], parameters={})

    for explanation in response.explanations:
        print(" explanation")
        # Feature attributions.
        attributions = explanation.attributions
        for attribution in attributions:
            print("  attribution")
            print("   baseline_output_value:", attribution.baseline_output_value)
            print("   instance_output_value:", attribution.instance_output_value)
            print("   output_display_name:", attribution.output_display_name)
            print("   approximation_error:", attribution.approximation_error)
            print("   output_name:", attribution.output_name)
            output_index = attribution.output_index
            for output_index in output_index:
                print("   output_index:", output_index)

    for prediction in response.predictions:
        print(prediction)


#  [END aiplatform_sdk_explain_tabular_sample]
