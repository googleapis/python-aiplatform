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

# [START aiplatform_predict_tabular_forecasting_sample]
from google.cloud import aiplatform
from google.protobuf.struct_pb2 import Value


def predict_tabular_forecasting_sample(
    endpoint: str,
    instances: typing.Sequence[google.protobuf.struct_pb2.Value],
    parameters: google.protobuf.struct_pb2.Value,
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    print("response:", response)


# [END aiplatform_predict_tabular_forecasting_sample]
