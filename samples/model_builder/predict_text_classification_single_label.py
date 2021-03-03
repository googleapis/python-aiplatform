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

#[START aiplatform_predict_text_classification_single_label_mbsdk_sample]
from google.cloud import aiplatform
from google.cloud.aiplatform.v1beta1.schema.predict.instance import TextClassificationPredictionInstance
from google.cloud.aiplatform.v1beta1.schema.predict.prediction import ClassificationPredictionResult

def predict_text_classification_single_label_mbsdk(project, location, endpoint_id, instance):
    aiplatform.init(project=project, location=location)

    endpoint = aiplatform.Endpoint(endpoint_id)

    instance = TextClassificationPredictionInstance(content=instance)

    response = endpoint.predict(
        instances=[instance], parameters={}
    )

    for prediction_ in response.predictions:
        prediction = ClassificationPredictionResult.from_map(prediction_)
        print(f'Predictions:\n\n')
        for x in range(0, len(prediction.ids)):
            print(f'\tDisplay name: {prediction.display_names[x]}')
            print(f'\tID: {prediction.ids[x]}')
            print(f'\tConfidence: {prediction.confidences[x]}\n\n')
#[END aiplatform_predict_text_classification_single_label_mbsdk_sample]
