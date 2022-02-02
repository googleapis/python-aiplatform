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


#  [START aiplatform_sdk_create_featurestore_sample]
from google.cloud import aiplatform


def create_featurestore_sample(
    project: str,
    location: str,
    featurestore_id: str,
    online_store_fixed_node_count: int = 1,
    sync: bool = True,
):

    aiplatform.init(project=project, location=location)

    fs = aiplatform.Featurestore.create(
        featurestore_id=featurestore_id,
        online_store_fixed_node_count=online_store_fixed_node_count,
        sync=sync,
    )

    fs.wait()

    return fs


#  [END aiplatform_sdk_create_featurestore_sample]
