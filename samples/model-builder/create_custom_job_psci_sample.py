# Copyright 2024 Google LLC
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

#  [START aiplatform_sdk_create_custom_job_psci_sample]
from google.cloud import aiplatform
from google.cloud import aiplatform_v1beta1


def create_custom_job_psci_sample(
    project: str,
    location: str,
    bucket: str,
    display_name: str,
    machine_type: str,
    replica_count: int,
    image_uri: str,
    network_attachment_name: str,
):
    """Custom training job sample with PSC-I through aiplatform_v1beta1."""
    aiplatform.init(project=project, location=location, staging_bucket=bucket)

    client_options = {"api_endpoint": f"{location}-aiplatform.googleapis.com"}

    client = aiplatform_v1beta1.JobServiceClient(client_options=client_options)

    request = aiplatform_v1beta1.CreateCustomJobRequest(
        parent=f"projects/{project}/locations/{location}",
        custom_job=aiplatform_v1beta1.CustomJob(
            display_name=display_name,
            job_spec=aiplatform_v1beta1.CustomJobSpec(
                worker_pool_specs=[
                    aiplatform_v1beta1.WorkerPoolSpec(
                        machine_spec=aiplatform_v1beta1.MachineSpec(
                            machine_type=machine_type,
                        ),
                        replica_count=replica_count,
                        container_spec=aiplatform_v1beta1.ContainerSpec(
                            image_uri=image_uri,
                        ),
                    )
                ],
                psc_interface_config=aiplatform_v1beta1.PscInterfaceConfig(
                    network_attachment=network_attachment_name,
                ),
            ),
        ),
    )

    response = client.create_custom_job(request=request)

    return response


#  [END aiplatform_sdk_create_custom_job_psci_sample]
