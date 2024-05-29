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

def make_name(name: str) -> str:
    # Sample function parameter name in export_model_video_action_recognition_sample
    name = name

    return name


def make_output_config(
    gcs_destination_output_uri_prefix: str,
    export_format: str
) -> google.cloud.aiplatform_v1beta1.types.model_service.OutputConfig:
    gcs_destination = {"output_uri_prefix": gcs_destination_output_uri_prefix}
    output_config = {
        "artifact_destination": gcs_destination,
        "export_format_id": export_format,
    }

    return output_config
