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

# [START aiplatform_predict_tables_classification_sample]
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from typing import Dict


def predict_tables_classification_sample(
    instance_dict: Dict, project: str, endpoint_id: str
):
    client_options = {
        "api_endpoint": "us-central1-prediction-aiplatform.googleapis.com"
    }
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.PredictionServiceClient(client_options=client_options)
    location = "us-central1"
    name = "projects/{project}/locations/{location}/endpoints/{endpoint}".format(
        project=project, location=location, endpoint=endpoint_id
    )
    parameters_dict = {}
    parameters = json_format.ParseDict(parameters_dict, Value())
    # for more info on the instance schema, please use get_model_sample.py
    # and look at the yaml found in instance_schema_uri
    instance = json_format.ParseDict(instance_dict, Value())
    instances = [instance]
    response = client.predict(endpoint=name, instances=instances, parameters=parameters)
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    # See gs://google-cloud-aiplatform/schema/predict/prediction/tables_classification.yaml for the format of the predictions.
    predictions = response.predictions
    print("predictions")
    for prediction in predictions:
        print(" prediction:", dict(prediction))


# [END aiplatform_predict_tables_classification_sample]
