# Copyright 2025 Google LLC
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

import json
from typing import Dict, Any

from google.cloud import aiplatform


#  [START aiplatform_sdk_invoke_tabular_sample]
def invoke_tabular_sample(
    project: str,
    location: str,
    endpoint_id: str,
    request_path: str,
    http_request_body: Dict[str, Any],
    stream: bool = False,
):
    aiplatform.init(project=project, location=location)

    dedicated_endpoint = aiplatform.Endpoint(endpoint_id)
    if stream:
        for chunk in dedicated_endpoint.invoke(
            request_path=request_path,
            body=json.dumps(http_request_body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            stream=True,
        ):
            print(chunk)
    else:
        response = dedicated_endpoint.invoke(
            request_path=request_path,
            body=json.dumps(http_request_body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        print(response)


#  [END aiplatform_sdk_invoke_tabular_sample]
