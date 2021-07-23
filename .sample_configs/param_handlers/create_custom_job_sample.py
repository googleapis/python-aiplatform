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

def make_parent(parent: str) -> str:
    # Sample function parameter parent in create_custom_job_sample
    parent = parent

    return parent

def make_custom_job(display_name: str, container_image_uri: str) -> google.cloud.aiplatform_v1alpha1.types.custom_job.CustomJob:
    custom_job = {
        'display_name': display_name,
        'job_spec': {
            'worker_pool_specs': [{
                'machine_spec': {
                    'machine_type': 'n1-standard-4',
                    'accelerator_type': aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_K80,
                    'accelerator_count': 1
                },
                'replica_count': 1,
                'container_spec': {
                    'image_uri': container_image_uri,
                    'command': [],
                    'args': []
                }
            }]
        }
    }

    return custom_job

