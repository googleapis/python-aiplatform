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


import deploy_model_with_automatic_resources_sample
import test_constants as constants


def test_deploy_model_with_automatic_resources_sample(
    mock_sdk_init,
    mock_model,
    mock_init_model,
    mock_deploy_model,
):

    deploy_model_with_automatic_resources_sample.deploy_model_with_automatic_resources_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        model_name=constants.MODEL_NAME,
        endpoint=constants.ENDPOINT_NAME,
        deployed_model_display_name=constants.DEPLOYED_MODEL_DISPLAY_NAME,
        traffic_percentage=constants.TRAFFIC_PERCENTAGE,
        traffic_split=constants.TRAFFIC_SPLIT,
        min_replica_count=constants.MIN_REPLICA_COUNT,
        max_replica_count=constants.MAX_REPLICA_COUNT,
        metadata=constants.ENDPOINT_DEPLOY_METADATA,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_init_model.assert_called_once_with(model_name=constants.MODEL_NAME)

    mock_deploy_model.assert_called_once_with(
        endpoint=constants.ENDPOINT_NAME,
        deployed_model_display_name=constants.DEPLOYED_MODEL_DISPLAY_NAME,
        traffic_percentage=constants.TRAFFIC_PERCENTAGE,
        traffic_split=constants.TRAFFIC_SPLIT,
        min_replica_count=constants.MIN_REPLICA_COUNT,
        max_replica_count=constants.MAX_REPLICA_COUNT,
        metadata=constants.ENDPOINT_DEPLOY_METADATA,
        sync=True,
    )
