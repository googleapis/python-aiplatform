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

import create_custom_job_psci_sample
from google.cloud import aiplatform_v1beta1
import test_constants as constants


def test_create_custom_job_psci_sample(
    mock_sdk_init,
    mock_get_job_service_client_v1beta1,
    mock_get_create_custom_job_request_v1beta1,
    mock_create_custom_job_v1beta1,
):
    """Custom training job sample with PSC-I through aiplatform_v1beta1."""
    create_custom_job_psci_sample.create_custom_job_psci_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        bucket=constants.STAGING_BUCKET,
        display_name=constants.DISPLAY_NAME,
        machine_type=constants.MACHINE_TYPE,
        replica_count=1,
        image_uri=constants.TRAIN_IMAGE,
        network_attachment_name=constants.NETWORK_ATTACHMENT_NAME,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
        staging_bucket=constants.STAGING_BUCKET,
    )

    mock_get_job_service_client_v1beta1.assert_called_once_with(
        client_options={
            "api_endpoint": f"{constants.LOCATION}-aiplatform.googleapis.com"
        }
    )

    mock_get_create_custom_job_request_v1beta1.assert_called_once_with(
        parent=f"projects/{constants.PROJECT}/locations/{constants.LOCATION}",
        custom_job=aiplatform_v1beta1.CustomJob(
            display_name=constants.DISPLAY_NAME,
            job_spec=aiplatform_v1beta1.CustomJobSpec(
                worker_pool_specs=[
                    aiplatform_v1beta1.WorkerPoolSpec(
                        machine_spec=aiplatform_v1beta1.MachineSpec(
                            machine_type=constants.MACHINE_TYPE,
                        ),
                        replica_count=constants.REPLICA_COUNT,
                        container_spec=aiplatform_v1beta1.ContainerSpec(
                            image_uri=constants.TRAIN_IMAGE,
                        ),
                    )
                ],
                psc_interface_config=aiplatform_v1beta1.PscInterfaceConfig(
                    network_attachment=constants.NETWORK_ATTACHMENT_NAME,
                ),
            ),
        ),
    )

    request = aiplatform_v1beta1.CreateCustomJobRequest(
        mock_get_create_custom_job_request_v1beta1.return_value
    )

    mock_create_custom_job_v1beta1.assert_called_once_with(request=request)
