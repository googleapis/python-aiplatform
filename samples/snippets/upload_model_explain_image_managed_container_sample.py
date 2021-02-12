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

# [START aiplatform_upload_model_explain_image_managed_container_sample]
from google.cloud import aiplatform_v1beta1


def upload_model_explain_image_managed_container_sample(
    project: str,
    display_name: str,
    container_spec_image_uri: str,
    artifact_uri: str,
    input_tensor_name: str,
    output_tensor_name: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
    timeout: int = 300,
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform_v1beta1.ModelServiceClient(client_options=client_options)

    # Container specification for deploying the model
    container_spec = {"image_uri": container_spec_image_uri, "command": [], "args": []}

    # The explainabilty method and corresponding parameters
    parameters = aiplatform_v1beta1.ExplanationParameters(
        {"xrai_attribution": {"step_count": 1}}
    )

    # The input tensor for feature attribution to the output
    # For single input model, y = f(x), this will be the serving input layer.
    input_metadata = aiplatform_v1beta1.ExplanationMetadata.InputMetadata(
        {
            "input_tensor_name": input_tensor_name,
            # Input is image data
            "modality": "image",
        }
    )

    # The output tensor to explain
    # For single output model, y = f(x), this will be the serving output layer.
    output_metadata = aiplatform_v1beta1.ExplanationMetadata.OutputMetadata(
        {"output_tensor_name": output_tensor_name}
    )

    # Assemble the explanation metadata
    metadata = aiplatform_v1beta1.ExplanationMetadata(
        inputs={"image": input_metadata}, outputs={"prediction": output_metadata}
    )

    # Assemble the explanation specification
    explanation_spec = aiplatform_v1beta1.ExplanationSpec(
        parameters=parameters, metadata=metadata
    )

    model = aiplatform_v1beta1.Model(
        display_name=display_name,
        # The Cloud Storage location of the custom model
        artifact_uri=artifact_uri,
        explanation_spec=explanation_spec,
        container_spec=container_spec,
    )
    parent = f"projects/{project}/locations/{location}"
    response = client.upload_model(parent=parent, model=model)
    print("Long running operation:", response.operation.name)
    upload_model_response = response.result(timeout=timeout)
    print("upload_model_response:", upload_model_response)


# [END aiplatform_upload_model_explain_image_managed_container_sample]
