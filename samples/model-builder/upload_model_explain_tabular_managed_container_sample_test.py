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

import test_constants as constants

import upload_model_explain_tabular_managed_container_sample


def test_upload_model_explain_tabular_managed_container_sample(
    mock_sdk_init, mock_model, mock_init_model, mock_upload_model
):

    upload_model_explain_tabular_managed_container_sample.upload_model_explain_tabular_managed_container_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        model_display_name=constants.MODEL_NAME,
        serving_container_image_uri=constants.SERVING_CONTAINER_IMAGE_URI,
        artifact_uri=constants.MODEL_ARTIFACT_URI,
        serving_container_predict_route=constants.SERVING_CONTAINER_PREDICT_ROUTE,
        serving_container_health_route=constants.SERVING_CONTAINER_HEALTH_ROUTE,
        description=constants.DESCRIPTION,
        serving_container_command=constants.SERVING_CONTAINER_COMMAND,
        serving_container_args=constants.SERVING_CONTAINER_ARGS,
        serving_container_environment_variables=constants.SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
        serving_container_ports=constants.SERVING_CONTAINER_PORTS,
        instance_schema_uri=constants.INSTANCE_SCHEMA_URI,
        parameters_schema_uri=constants.PARAMETERS_SCHEMA_URI,
        prediction_schema_uri=constants.PREDICTION_SCHEMA_URI,
        explanation_metadata=constants.EXPLANATION_METADATA,
        explanation_parameters=constants.EXPLANATION_PARAMETERS,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_upload_model.assert_called_once_with(
        display_name=constants.MODEL_NAME,
        serving_container_image_uri=constants.SERVING_CONTAINER_IMAGE_URI,
        artifact_uri=constants.MODEL_ARTIFACT_URI,
        serving_container_predict_route=constants.SERVING_CONTAINER_PREDICT_ROUTE,
        serving_container_health_route=constants.SERVING_CONTAINER_HEALTH_ROUTE,
        description=constants.DESCRIPTION,
        serving_container_command=constants.SERVING_CONTAINER_COMMAND,
        serving_container_args=constants.SERVING_CONTAINER_ARGS,
        serving_container_environment_variables=constants.SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
        serving_container_ports=constants.SERVING_CONTAINER_PORTS,
        instance_schema_uri=constants.INSTANCE_SCHEMA_URI,
        parameters_schema_uri=constants.PARAMETERS_SCHEMA_URI,
        prediction_schema_uri=constants.PREDICTION_SCHEMA_URI,
        explanation_metadata=constants.EXPLANATION_METADATA,
        explanation_parameters=constants.EXPLANATION_PARAMETERS,
        sync=True,
    )
