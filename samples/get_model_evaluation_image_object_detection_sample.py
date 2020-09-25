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

# [START aiplatform_get_model_evaluation_image_object_detection_sample]
from google.cloud import aiplatform
from google.protobuf import json_format


def get_model_evaluation_image_object_detection_sample(
    project: str, model_id: str, evaluation_id: str
):
    client_options = dict(api_endpoint="us-central1-aiplatform.googleapis.com")
    client = aiplatform.ModelServiceClient(client_options=client_options)
    location = "us-central1"
    name = "projects/{project}/locations/{location}/models/{model}/evaluations/{evaluation}".format(
        project=project, location=location, model=model_id, evaluation=evaluation_id
    )
    response = client.get_model_evaluation(name=name)
    print("response")
    print(" name:", response.name)
    print(" metrics_schema_uri:", response.metrics_schema_uri)
    print(" metrics:", json_format.MessageToDict(response._pb.metrics))
    print(" create_time:", response.create_time)
    print(" slice_dimensions:", response.slice_dimensions)
    model_explanation = response.model_explanation
    print(" model_explanation")
    mean_attributions = model_explanation.mean_attributions
    for mean_attribution in mean_attributions:
        print("  mean_attribution")
        print("   baseline_output_value:", mean_attribution.baseline_output_value)
        print("   instance_output_value:", mean_attribution.instance_output_value)
        print(
            "   feature_attributions:",
            json_format.MessageToDict(mean_attribution._pb.feature_attributions),
        )
        print("   output_index:", mean_attribution.output_index)
        print("   output_display_name:", mean_attribution.output_display_name)
        print("   approximation_error:", mean_attribution.approximation_error)


# [END aiplatform_get_model_evaluation_image_object_detection_sample]
