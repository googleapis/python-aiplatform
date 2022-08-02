# Copyright 2022 Google LLC
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


# [START aiplatform_sdk_create_and_import_dataset_time_series_bigquery_sample]
def create_and_import_dataset_time_series_bigquery_sample(
    display_name: str,
    project: str,
    location: str,
    bigquery_source: str,
):

    aiplatform.init(project=project, location=location)

    dataset = aiplatform.TimeSeriesDataset.create(
        display_name=display_name,
        bigquery_source=bigquery_source,
    )

    dataset.wait()

    print(f'\tDataset: "{dataset.display_name}"')
    print(f'\tname: "{dataset.resource_name}"')


# [END aiplatform_sdk_create_and_import_dataset_time_series_bigquery_sample]
