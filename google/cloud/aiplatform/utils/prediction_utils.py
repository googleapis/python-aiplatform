# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

import re
from typing import Optional, Sequence

from google.cloud.aiplatform.constants import prediction


REGISTRY_REGEX = re.compile(r"^([\w\-]+\-docker\.pkg\.dev|([\w]+\.|)gcr\.io)")


def is_registry_uri(image_uri: str) -> bool:
    """Checks whether the image uri is in container registry or artifact registry.

    Args:
        image_uri (str):
            The image uri to check if it is in container registry or artifact registry.

    Returns:
        True if the image uri is in container registry or artifact registry.
    """
    return REGISTRY_REGEX.match(image_uri) is not None


def get_prediction_aip_http_port(
    serving_container_ports: Optional[Sequence[int]] = None,
):
    """Gets the used prediction container port from serving container ports.

    When you create a Model, set the containerSpec.ports field. The first entry in this
    field becomes the value of AIP_HTTP_PORT. Default value is 8080.
    See https://cloud.google.com/vertex-ai/docs/predictions/custom-container-requirements
    for more details.

    Args:
        serving_container_ports (Sequence[int]):
            Optional. Declaration of ports that are exposed by the container. This field is
            primarily informational, it gives Vertex AI information about the
            network connections the container uses. Listing or not a port here has
            no impact on whether the port is actually exposed, any port listening on
            the default "0.0.0.0" address inside a container will be accessible from
            the network.
    """
    return (
        serving_container_ports[0]
        if serving_container_ports is not None and len(serving_container_ports) > 0
        else prediction.DEFAULT_AIP_HTTP_PORT
    )
