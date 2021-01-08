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

def make_deployed_model(model_name: str, deployed_model_display_name: str) -> google.cloud.aiplatform_v1alpha1.types.endpoint.DeployedModel:
    deployed_model = {
        # format: 'projects/{project}/locations/{location}/models/{model}'
        'model': model_name,
        'display_name': deployed_model_display_name,

        # `dedicated_resources` must be used for non-AutoML models
        'dedicated_resources': {
            'min_replica_count': 1,
            'machine_spec': {
                'machine_type': 'n1-standard-2',
                # Accelerators can be used only if the model specifies a GPU image.
                # 'accelerator_type': aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_K80, 
                # 'accelerator_count': 1,
            }
        }
    }

    return deployed_model

def make_traffic_split() -> typing.Sequence[google.cloud.aiplatform_v1alpha1.types.endpoint_service.DeployModelRequest.TrafficSplitEntry]:
    # key '0' assigns traffic for the newly deployed model
    # Traffic percentage values must add up to 100
    # Leave dictionary empty if endpoint should not accept any traffic 
    traffic_split = {'0': 100}

    return traffic_split

