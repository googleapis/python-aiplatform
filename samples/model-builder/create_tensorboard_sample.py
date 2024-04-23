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


#  [START aiplatform_sdk_create_tensorboard_sample]
def create_tensorboard_sample(
    project: str,
    location: str,
    display_name: Optional[str] = None,
):
    aiplatform.init(project=project, location=location)

    tensorboard = aiplatform.Tensorboard.create(
        display_name=display_name,
        project=project,
        location=location,
    )

    aiplatform.init(
        project=project,
        location=location,
        experiment_tensorboard=tensorboard
    )

    return tensorboard


#  [END aiplatform_sdk_create_tensorboard_sample]
