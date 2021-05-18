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

from typing import Sequence, Union

from google.cloud import aiplatform


#  [START aiplatform_sdk_create_batch_prediction_job_text_classification_sample]
#  [START aiplatform_sdk_create_batch_prediction_job_text_entity_extraction_sample]
#  [START aiplatform_sdk_create_batch_prediction_job_text_sentiment_analysis_sample]
#  [START aiplatform_sdk_create_batch_prediction_job_sample]
def create_batch_prediction_job_sample(
    project: str,
    location: str,
    model_resource_name: str,
    job_display_name: str,
    gcs_source: Union[str, Sequence[str]],
    gcs_destination: str,
    sync: bool = True,
):
    aiplatform.init(project=project, location=location)

    my_model = aiplatform.Model(model_resource_name)

    batch_prediction_job = my_model.batch_predict(
        job_display_name=job_display_name,
        gcs_source=gcs_source,
        gcs_destination_prefix=gcs_destination,
        sync=sync,
    )

    batch_prediction_job.wait()

    print(batch_prediction_job.display_name)
    print(batch_prediction_job.resource_name)
    print(batch_prediction_job.state)
    return batch_prediction_job


#  [END aiplatform_sdk_create_batch_prediction_job_text_sentiment_analysis_sample]
#  [END aiplatform_sdk_create_batch_prediction_job_text_entity_extraction_sample]
#  [END aiplatform_sdk_create_batch_prediction_job_text_classification_sample]
#  [END aiplatform_sdk_create_batch_prediction_job_sample]
