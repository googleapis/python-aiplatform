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

# [START aiplatform_predict_image_classification_sample]
import base64
from google.cloud import aiplatform
from google.cloud.aiplatform.v1beta1.schema.predict import instance
from google.cloud.aiplatform.v1beta1.schema.predict import params
from google.cloud.aiplatform.v1beta1.schema.predict import prediction


def predict_image_classification_sample(
    project: str,
    endpoint_id: str,
    filename: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-prediction-aiplatform.googleapis.com",
):
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    with open(filename, "rb") as f:
        file_content = f.read()

    # The format of each instance should conform to the deployed model's prediction input schema.
    encoded_content = base64.b64encode(file_content).decode("utf-8")

    instance_obj = instance.ImageClassificationPredictionInstance({
        "content": encoded_content})

    instance_val = instance_obj.to_value()
    instances = [instance_val]

    params_obj = params.ImageClassificationPredictionParams({
        "confidence_threshold": 0.5, "max_predictions": 5})

    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=params_obj
    )
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    # See gs://google-cloud-aiplatform/schema/predict/prediction/classification.yaml for the format of the predictions.
    predictions = response.predictions
    for prediction_ in predictions:
        print(" prediction:", dict(prediction_))
        prediction_obj = prediction.ClassificationPredictionResult.from_map(prediction_)
        print(prediction_obj)


# [END aiplatform_predict_image_classification_sample]
