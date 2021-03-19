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


import create_batch_prediction_job_sample


def test_create_batch_prediction_job_sample(
    mock_sdk_init, mock_create_batch_prediction_job
):

    create_batch_prediction_job_sample.create_batch_prediction_job_sample(
        project="abc",
        location="us-central1",
        model_resource_name="projects/abc/location/us-central1/models/9876345",
        job_display_name="my-first-batch-prediction-job",
        gcs_source=["gs://bucket1/source1.jsonl", "gs://bucket7/source4.jsonl"],
        gcs_destination="gs://bucket3/output-dir/",
    )

    mock_sdk_init.assert_called_once()
    mock_create_batch_prediction_job.assert_called_once()
