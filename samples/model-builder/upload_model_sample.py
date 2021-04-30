# Copyright 2021 Google LLC
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

from typing import Dict, Optional, Sequence

from google.cloud import aiplatform
from google.cloud.aiplatform import explain


#  [START aiplatform_sdk_upload_model_sample]
def upload_model_sample(
    project: str,
    location: str,
    display_name: str,
    serving_container_image_uri: str,
    artifact_uri: Optional[str] = None,
    serving_container_predict_route: Optional[str] = None,
    serving_container_health_route: Optional[str] = None,
    description: Optional[str] = None,
    serving_container_command: Optional[Sequence[str]] = None,
    serving_container_args: Optional[Sequence[str]] = None,
    serving_container_environment_variables: Optional[Dict[str, str]] = None,
    serving_container_ports: Optional[Sequence[int]] = None,
    instance_schema_uri: Optional[str] = None,
    parameters_schema_uri: Optional[str] = None,
    prediction_schema_uri: Optional[str] = None,
    explanation_metadata: Optional[explain.ExplanationMetadata] = None,
    explanation_parameters: Optional[explain.ExplanationParameters] = None,
    sync: bool = True,
):

    aiplatform.init(project=project, location=location)

    model = aiplatform.Model.upload(
        display_name=display_name,
        artifact_uri=artifact_uri,
        serving_container_image_uri=serving_container_image_uri,
        serving_container_predict_route=serving_container_predict_route,
        serving_container_health_route=serving_container_health_route,
        instance_schema_uri=instance_schema_uri,
        parameters_schema_uri=parameters_schema_uri,
        prediction_schema_uri=prediction_schema_uri,
        description=description,
        serving_container_command=serving_container_command,
        serving_container_args=serving_container_args,
        serving_container_environment_variables=serving_container_environment_variables,
        serving_container_ports=serving_container_ports,
        explanation_metadata=explanation_metadata,
        explanation_parameters=explanation_parameters,
        sync=sync,
    )

    model.wait()

    print(model.display_name)
    print(model.resource_name)
    return model


#  [END aiplatform_sdk_upload_model_sample]
