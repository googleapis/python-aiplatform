# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

def make_endpoint(endpoint: str) -> str:
    endpoint = endpoint

    return endpoint

def make_deployed_model_id(deployed_model_id: str) -> str:
    # Sample function parameter deployed_model_id in undeploy_model_sample
    deployed_model_id = deployed_model_id

    return deployed_model_id

def make_traffic_split() -> dict:
    # If after the undeployment there is at least one deployed model remaining in the endpoint, traffic_split should be set to a mapping from remaining deployed models' ids to integer percentages that sum to 100.
    traffic_split = {}

    return traffic_split

