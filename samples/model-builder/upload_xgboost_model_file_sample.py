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

from typing import Dict, Optional

from google.cloud import aiplatform
from google.cloud.aiplatform import explain


#  [START aiplatform_sdk_upload_xgboost_model_file_sample]
def upload_xgboost_model_file_sample(
    model_file_path: str,
    # Optional:
    xgboost_version: Optional[str] = None,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
    instance_schema_uri: Optional[str] = None,
    parameters_schema_uri: Optional[str] = None,
    prediction_schema_uri: Optional[str] = None,
    explanation_metadata: Optional[explain.ExplanationMetadata] = None,
    explanation_parameters: Optional[explain.ExplanationParameters] = None,
    project: Optional[str] = None,
    location: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
    encryption_spec_key_name: Optional[str] = None,
    staging_bucket: Optional[str] = None,
    sync: bool = True,
):
    model = aiplatform.Model.upload_xgboost_model_file(
        model_file_path=model_file_path,
        # Optional:
        xgboost_version=xgboost_version,
        display_name=display_name,
        description=description,
        instance_schema_uri=instance_schema_uri,
        parameters_schema_uri=parameters_schema_uri,
        prediction_schema_uri=prediction_schema_uri,
        explanation_metadata=explanation_metadata,
        explanation_parameters=explanation_parameters,
        project=project,
        location=location,
        labels=labels,
        encryption_spec_key_name=encryption_spec_key_name,
        staging_bucket=staging_bucket,
        sync=sync,
    )

    model.wait()

    print(model.display_name)
    print(model.resource_name)
    print(model.to_dict())
    return model


#  [END aiplatform_sdk_upload_xgboost_model_file_sample]
