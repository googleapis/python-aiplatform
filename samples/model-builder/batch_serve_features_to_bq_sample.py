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


#  [START aiplatform_sdk_batch_serve_features_to_bq_sample]
from typing import Dict, List
from google.cloud import aiplatform


def batch_serve_features_to_bq_sample(
    project: str,
    location: str,
    featurestore_name: str,
    bq_destination_output_uri: str,
    serving_feature_ids: Dict[str, List[str]],
    read_instances_uri: str,
    sync: bool = True,
):

    aiplatform.init(project=project, location=location)

    fs = aiplatform.featurestore.Featurestore(featurestore_name=featurestore_name)

    fs.batch_serve_to_bq(
        bq_destination_output_uri=bq_destination_output_uri,
        serving_feature_ids=serving_feature_ids,
        read_instances_uri=read_instances_uri,
        sync=sync,
    )


#  [END aiplatform_sdk_batch_serve_features_to_bq_sample]
