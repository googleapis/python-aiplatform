# Copyright 2022 Google LLC
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


from google.cloud import aiplatform


#  [START aiplatform_sdk_end_experiment_run_sample]
def end_experiment_run_sample(
    experiment_name: str,
    run_name: str,
    project: str,
    location: str,
):
    aiplatform.init(experiment=experiment_name, project=project, location=location)

    aiplatform.start_run(run=run_name, resume=True)

    aiplatform.end_run()


#  [END aiplatform_sdk_end_experiment_run_sample]
