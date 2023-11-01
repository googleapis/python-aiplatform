# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
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

import google.auth
import google.auth.transport.requests
import logging
import re

from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.utils import resource_manager_utils


# Artifact Repository available regions.
_AVAILABLE_REGIONS = ["us", "europe", "asia"]
# If region is not available, assume using the default region.
_DEFAULT_REGION = "us"

_PERSISTENT_RESOURCE_NAME_PATTERN = "projects/{}/locations/{}/persistentResources/{}"
_VALID_RESOURCE_NAME_REGEX = "[a-z][a-zA-Z0-9._-]{0,127}"
_DASHBOARD_URI_SUFFIX = "aiplatform-training.googleusercontent.com"


def valid_resource_name(resource_name):
    """Check if address is a valid resource name."""
    resource_name_split = resource_name.split("/")
    if not (
        len(resource_name_split) == 6
        and resource_name_split[0] == "projects"
        and resource_name_split[2] == "locations"
        and resource_name_split[4] == "persistentResources"
    ):
        raise ValueError(
            "[Ray on Vertex AI]: Address must be in the following "
            "format: vertex_ray://projects/<project_num>/locations/<region>/persistentResources/<pr_id> "
            "or vertex_ray://<pr_id>."
        )


def maybe_reconstruct_resource_name(address) -> str:
    """Reconstruct full persistent resource name if only id was given."""
    if re.match("^{}$".format(_VALID_RESOURCE_NAME_REGEX), address):
        # Assume only cluster name (persistent resource id) was given.
        logging.info(
            "[Ray on Vertex AI]: Cluster name was given as address, reconstructing full resource name"
        )
        return _PERSISTENT_RESOURCE_NAME_PATTERN.format(
            resource_manager_utils.get_project_number(
                initializer.global_config.project
            ),
            initializer.global_config.location,
            address,
        )

    return address


def get_image_uri(ray_version, python_version, enable_cuda):
    """Image uri for a given ray version and python version."""
    if ray_version not in ["2_4"]:
        raise ValueError("[Ray on Vertex AI]: The supported Ray version is 2_4.")
    if python_version not in ["3_10"]:
        raise ValueError("[Ray on Vertex AI]: The supported Python version is 3_10.")

    location = initializer.global_config.location
    region = location.split("-")[0]
    if region not in _AVAILABLE_REGIONS:
        region = _DEFAULT_REGION

    if enable_cuda:
        # TODO(b/292003337) update eligible image uris
        return f"{region}-docker.pkg.dev/vertex-ai/training/ray-gpu.2-4.py310:latest"
    else:
        return f"{region}-docker.pkg.dev/vertex-ai/training/ray-cpu.2-4.py310:latest"


def get_versions_from_image_uri(image_uri):
    """Get ray version and python version from image uri."""
    logging.info(f"[Ray on Vertex AI]: Getting versions from image uri: {image_uri}")
    image_label = image_uri.split("/")[-1].split(":")[0]
    py_version = image_label[-3] + "_" + image_label[-2:]
    ray_version = image_label.split(".")[1].replace("-", "_")
    return py_version, ray_version


def valid_dashboard_address(address):
    """Check if address is a valid dashboard uri."""
    return address.endswith(_DASHBOARD_URI_SUFFIX)


def get_bearer_token():
    """Get bearer token through Application Default Credentials."""
    creds, _ = google.auth.default()

    # creds.valid is False, and creds.token is None
    # Need to refresh credentials to populate those
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    return creds.token
