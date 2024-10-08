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

#  [START aiplatform_sdk_get_experiment_backing_tensorboard_sample]
from google.cloud import aiplatform


def get_experiment_backing_tensorboard_sample(
    experiment_name: str,
    project: str,
    location: str,
):
    backing_tensorboard = aiplatform.Experiment(
        project=project,
        location=location,
        experiment_name=experiment_name
    ).get_backing_tensorboard_resource()

    return backing_tensorboard.name


#  [END aiplatform_sdk_get_experiment_backing_tensorboard_sample]
