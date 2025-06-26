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
import test_constants as constants


def test_create_custom_job_psci_sample(
    mock_sdk_init,
    mock_get_custom_job,
    mock_run_custom_job,
):
  """Custom training job sample with PSC-I through aiplatform_v1beta1."""
  create_custom_job_psci_sample.create_custom_job_psci_sample(
      project=constants.PROJECT,
      location=constants.LOCATION,
      bucket=constants.STAGING_BUCKET,
      display_name=constants.DISPLAY_NAME,
      machine_type=constants.MACHINE_TYPE,
      replica_count=1,
      image_uri=constants.CONTAINER_URI,
      network_attachment=constants.NETWORK_ATTACHMENT_NAME,
      domain=constants.DOMAIN,
      target_project=constants.TARGET_PROJECT,
      target_network=constants.TARGET_NETWORK,
  )

  mock_sdk_init.assert_called_once_with(
      project=constants.PROJECT,
      location=constants.LOCATION,
      staging_bucket=constants.STAGING_BUCKET,
  )

  mock_get_custom_job.assert_called_once_with(
      display_name=constants.DISPLAY_NAME,
      worker_pool_specs=constants.CUSTOM_JOB_WORKER_POOL_SPECS_WITHOUT_ACCELERATOR,
  )

  mock_run_custom_job.assert_called_once_with(
      psc_interface_config=constants.PSC_INTERFACE_CONFIG,
  )
