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

from google.cloud import aiplatform
from google.cloud.aiplatform.preview import vertex_ray
from ray.job_submission import JobSubmissionClient
from tests.system.aiplatform import e2e_base
import datetime
import os
import ray
import time
import tempfile

RAY_VERSION = "2.4.0"
CLUSTER_RAY_VERSION = "2_4"
SDK_VERSION = aiplatform.__version__
PROJECT_ID = "ucaip-sample-tests"


class TestRayData(e2e_base.TestEndToEnd):
    _temp_prefix = "temp-ray-data"

    def test_ray_data(self):
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
        )

        cluster_details = vertex_ray.get_ray_cluster(cluster_resource_name)

        # Connect to cluster
        client = JobSubmissionClient(
            "google.cloud.aiplatform.preview.vertex_ray://{}".format(
                cluster_details.dashboard_address
            )
        )

        my_script = """
import ray
from vertex_ray import BigQueryDatasource

parallelism = 10
query = "SELECT * FROM `bigquery-public-data.ml_datasets.ulb_fraud_detection` LIMIT 10000000"

ds = ray.data.read_datasource(
    BigQueryDatasource(),
    parallelism=parallelism,
    query=query
)
# The reads are lazy, so the end time cannot be captured until ds.fully_executed() is called
ds.fully_executed()

# Write
ds.write_datasource(
    BigQueryDatasource(),
    dataset='bugbashbq1.system_test_write',
)
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            fp = os.path.join(temp_dir, "my_script.py")
            f = open(fp, "w")
            f.write(my_script)
            f.close()

            job_id = client.submit_job(
                # Entrypoint shell command to execute
                entrypoint="python my_script.py",
                # Path to the local directory that contains the my_script.py file
                runtime_env={
                    "working_dir": temp_dir,
                    "pip": ["google-cloud-aiplatform[ray]==" + SDK_VERSION],
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
