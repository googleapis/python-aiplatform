# Copyright 2023 Google LLC
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

from typing import Optional

from google.cloud import aiplatform


#  [START aiplatform_sdk_upload_tensorboard_log_sample]
def upload_tensorboard_log_continuously_sample(
    tensorboard_experiment_name: str,
    logdir: str,
    tensorboard_id: str,
    project: str,
    location: str,
    experiment_display_name: Optional[str] = None,
    run_name_prefix: Optional[str] = None,
    description: Optional[str] = None,
) -> None:

    aiplatform.init(project=project, location=location)

    # Continuous monitoring
    aiplatform.start_upload_tb_log(
        tensorboard_id=tensorboard_id,
        tensorboard_experiment_name=tensorboard_experiment_name,
        logdir=logdir,
        experiment_display_name=experiment_display_name,
        run_name_prefix=run_name_prefix,
        description=description,
    )
    aiplatform.end_upload_tb_log()


#  [END aiplatform_sdk_upload_tensorboard_log_sample]
