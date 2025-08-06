# -*- coding: utf-8 -*-

# Copyright 2025 Google LLC
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

from google.cloud import aiplatform
from google.cloud.aiplatform import vertex_ray
from ray.job_submission import JobSubmissionClient
from tests.system.aiplatform import e2e_base
import datetime
import os
import pytest
import ray
import time
import tempfile

# Local ray version will always be 2.4 regardless of cluster version due to
# depenency conflicts. Remote job execution's Ray version is >2.9.
RAY_VERSION = "2.4.0"
SDK_VERSION = aiplatform.__version__
PROJECT_ID = "ucaip-sample-tests"


def create_bigquery_script(version: str):
    """Creates a bigquery script for the given Ray version.

    Args:
        version: The Ray version.

    Returns:
        The bigquery script.
    """
    if version == "2.9":
        num_blocks_arg = "parallelism"
    else:
        num_blocks_arg = "override_num_blocks"
    version_without_dot = version.replace(".", "")

    return f"""
import ray
import vertex_ray

{num_blocks_arg} = 10
query = "SELECT * FROM `bigquery-public-data.ml_datasets.ulb_fraud_detection` LIMIT 10000000"

ds = vertex_ray.data.read_bigquery(
    {num_blocks_arg}={num_blocks_arg},
    query=query,
)

# The reads are lazy, so the end time cannot be captured until ds.materialize() is called
ds.materialize()

# Write
vertex_ray.data.write_bigquery(
    ds,
    dataset="bugbashbq1.system_test_ray{version_without_dot}_write",
)
"""


my_script = {
    version: create_bigquery_script(version)
    for version in ["2.9", "2.33", "2.42", "2.47"]
}


class TestRayData(e2e_base.TestEndToEnd):
    _temp_prefix = "temp-ray-data"

    @pytest.mark.parametrize("cluster_ray_version", ["2.33", "2.42", "2.47"])
    def test_ray_data(self, cluster_ray_version):
        head_node_type = vertex_ray.Resources()
        worker_node_types = [
            vertex_ray.Resources(),
            vertex_ray.Resources(),
            vertex_ray.Resources(),
        ]

        assert ray.__version__ == RAY_VERSION
        aiplatform.init(project=PROJECT_ID, location="us-central1")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        # Create cluster, get dashboard address
        cluster_resource_name = vertex_ray.create_ray_cluster(
            head_node_type=head_node_type,
            worker_node_types=worker_node_types,
            cluster_name=f"ray-cluster-{timestamp}-test-ray-data",
            ray_version=cluster_ray_version,
        )

        cluster_details = vertex_ray.get_ray_cluster(cluster_resource_name)

        # Connect to cluster
        client = JobSubmissionClient(
            "google.cloud.aiplatform.vertex_ray://{}".format(
                cluster_details.dashboard_address
            )
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            fp = os.path.join(temp_dir, "my_script.py")
            f = open(fp, "w")
            f.write(my_script[cluster_ray_version])
            f.close()

            job_id = client.submit_job(
                # Entrypoint shell command to execute
                entrypoint="python my_script.py",
                # Path to the local directory that contains the my_script.py file
                runtime_env={
                    "working_dir": temp_dir,
                    "pip": [
                        "pandas==2.1.4",
                        "google-cloud-aiplatform[ray]==" + SDK_VERSION,
                    ],
                },
            )

            job_status = None
            while job_status != ray.job_submission.JobStatus.SUCCEEDED:
                job_status = client.get_job_info(job_id).status
                print(job_id, "has status:", job_status)
                if (
                    job_status == ray.job_submission.JobStatus.PENDING
                    or job_status == ray.job_submission.JobStatus.RUNNING
                ):
                    time.sleep(10)
                elif (
                    job_status == ray.job_submission.JobStatus.FAILED
                    or job_status == ray.job_submission.JobStatus.STOPPED
                ):
                    print(job_id, "job logs:")
                    print(client.get_job_info(job_id).message)
                    raise RuntimeError("The Ray Job encountered an error and failed")

        vertex_ray.delete_ray_cluster(cluster_resource_name)
        # Ensure cluster was deleted
        for cluster in vertex_ray.list_ray_clusters():
            assert cluster.cluster_resource_name != cluster_resource_name
