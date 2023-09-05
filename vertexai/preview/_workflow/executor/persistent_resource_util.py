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

import datetime
import time
from typing import Optional

from google.api_core import exceptions
from google.api_core import gapic_v1
from google.api_core.client_options import ClientOptions
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform_v1beta1.services.persistent_resource_service import (
    PersistentResourceServiceClient,
)
from google.cloud.aiplatform_v1beta1.types import persistent_resource_service
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    PersistentResource,
)
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    ResourcePool,
)
from google.cloud.aiplatform_v1beta1.types.persistent_resource_service import (
    GetPersistentResourceRequest,
)


GAPIC_VERSION = aiplatform.__version__
_LOGGER = base.Logger(__name__)

_DEFAULT_REPLICA_COUNT = 1
_DEFAULT_MACHINE_TYPE = "n1-standard-4"
_DEFAULT_DISK_TYPE = "pd-ssd"
_DEFAULT_DISK_SIZE_GB = 100


def _create_persistent_resource_client(location: Optional[str] = "us-central1"):

    client_info = gapic_v1.client_info.ClientInfo(
        gapic_version=GAPIC_VERSION,
    )

    api_endpoint = f"{location}-aiplatform.googleapis.com"

    return PersistentResourceServiceClient(
        client_options=ClientOptions(api_endpoint=api_endpoint),
        client_info=client_info,
    )


def check_persistent_resource(cluster_resource_name: str) -> bool:
    """Helper method to check if a persistent resource exists or not.

    Args:
        cluster_resource_name: Persistent Resource name. Has the form:
        ``projects/my-project/locations/my-region/persistentResource/cluster-name``.

    Returns:
        True if a Persistent Resource exists.

    Raises:
        ValueError: if existing cluster is not RUNNING.
    """
    # Parse resource name to get the location.
    locataion = cluster_resource_name.split("/")[3]
    client = _create_persistent_resource_client(locataion)
    request = GetPersistentResourceRequest(
        name=cluster_resource_name,
    )
    try:
        response = client.get_persistent_resource(request)
    except exceptions.NotFound:
        return False

    if response.state != PersistentResource.State.RUNNING:
        raise ValueError(
            "The existing cluster `",
            cluster_resource_name,
            "` isn't running, please specify a different cluster_name.",
        )
    return True


def _default_persistent_resource() -> PersistentResource:
    """Default persistent resource."""
    # Currently the service accepts only one resource_pool config and image_uri.
    resource_pools = []
    resource_pool = ResourcePool()
    resource_pool.replica_count = _DEFAULT_REPLICA_COUNT
    resource_pool.machine_spec.machine_type = _DEFAULT_MACHINE_TYPE
    resource_pool.disk_spec.boot_disk_type = _DEFAULT_DISK_TYPE
    resource_pool.disk_spec.boot_disk_size_gb = _DEFAULT_DISK_SIZE_GB
    resource_pools.append(resource_pool)

    return PersistentResource(resource_pools=resource_pools)


# TODO(b/294600649)
def _polling_delay(num_attempts: int, time_scale: float) -> datetime.timedelta:
    """Computes a delay to the next attempt to poll the Vertex service.

    This does bounded exponential backoff, starting with $time_scale.
    If $time_scale == 0, it starts with a small time interval, less than
    1 second.

    Args:
      num_attempts: The number of times have we polled and found that the
        desired result was not yet available.
      time_scale: The shortest polling interval, in seconds, or zero. Zero is
        treated as a small interval, less than 1 second.

    Returns:
      A recommended delay interval, in seconds.
    """
    #  The polling schedule is slow initially , and then gets faster until 4
    #  attempts (after that the sleeping time remains the same).
    small_interval = 30.0  # Seconds
    interval = max(time_scale, small_interval) * 0.76 ** min(num_attempts, 4)
    return datetime.timedelta(seconds=interval)


def _get_persistent_resource(cluster_resource_name: str):
    """Get persistent resource.

    Args:
      cluster_resource_name:
          "projects/<project_num>/locations/<region>/persistentResources/<pr_id>".

    Returns:
      aiplatform_v1beta1.PersistentResource if state is RUNNING.

    Raises:
      ValueError: Invalid cluster resource name.
      RuntimeError: Service returns error.
      RuntimeError: Cluster resource state is STOPPING.
      RuntimeError: Cluster resource state is ERROR.
    """

    # Parse resource name to get the location.
    locataion = cluster_resource_name.split("/")[3]
    client = _create_persistent_resource_client(locataion)
    request = GetPersistentResourceRequest(
        name=cluster_resource_name,
    )

    num_attempts = 0
    while True:
        try:
            response = client.get_persistent_resource(request)
        except exceptions.NotFound as e:
            raise ValueError("Invalid cluster_resource_name (404 not found).") from e
        if response.error.message:
            raise RuntimeError("Cluster returned an error.", response.error.message)

        print("Cluster State =", response.state)
        if response.state == PersistentResource.State.RUNNING:
            return response
        elif response.state == PersistentResource.State.STOPPING:
            raise RuntimeError("The cluster is stopping.")
        elif response.state == PersistentResource.State.ERROR:
            raise RuntimeError("The cluster encountered an error.")
        # Polling decay
        sleep_time = _polling_delay(num_attempts=num_attempts, time_scale=90.0)
        num_attempts += 1
        print(
            "Waiting for cluster provisioning; attempt {}; sleeping for {} seconds".format(
                num_attempts, sleep_time
            )
        )
        time.sleep(sleep_time.total_seconds())


def create_persistent_resource(cluster_resource_name: str):
    """Create a default persistent resource."""
    locataion = cluster_resource_name.split("/")[3]
    parent = "/".join(cluster_resource_name.split("/")[:4])
    cluster_name = cluster_resource_name.split("/")[-1]

    client = _create_persistent_resource_client(locataion)

    persistent_resource = _default_persistent_resource()

    request = persistent_resource_service.CreatePersistentResourceRequest(
        parent=parent,
        persistent_resource=persistent_resource,
        persistent_resource_id=cluster_name,
    )

    try:
        _ = client.create_persistent_resource(request)
    except Exception as e:
        raise ValueError("Failed in cluster creation due to: ", e) from e

    # Check cluster creation progress
    response = _get_persistent_resource(cluster_resource_name)
    _LOGGER.info(response)
