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


def create_custom_job_psci_sample(
    project: str,
    location: str,
    bucket: str,
    display_name: str,
    machine_type: str,
    replica_count: int,
    image_uri: str,
    network_attachment: str,
    domain: str,
    target_project: str,
    target_network: str,
):
    """Custom training job sample with PSC Interface Config."""
    aiplatform.init(project=project, location=location, staging_bucket=bucket)

    worker_pool_specs = [{
        "machine_spec": {
            "machine_type": machine_type,
        },
        "replica_count": replica_count,
        "container_spec": {
            "image_uri": image_uri,
            "command": [],
            "args": [],
        },
    }]
    psc_interface_config = {
        "network_attachment": network_attachment,
        "dns_peering_configs": [
            {
                "domain": domain,
                "target_project": target_project,
                "target_network": target_network,
            },
        ],
    }
    job = aiplatform.CustomJob(
        display_name=display_name,
        worker_pool_specs=worker_pool_specs,
    )

    job.run(psc_interface_config=psc_interface_config)


#  [END aiplatform_sdk_create_custom_job_psci_sample]
