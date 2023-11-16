# -*- coding: utf-8 -*-

from typing import List

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

from google.api_core import client_options
from google.api_core import gapic_v1
from google.cloud import aiplatform_v1beta1


class PipelineJobsBatchDeleteRunner:
    """Preview module for batch deleting Pipeline Jobs."""

    def __init__(
        self,
        project: str,
        location: str,
    ):
        """Initializes a pipeline client and other common attributes."""
        self.project = project
        self.location = location
        self.client_options = client_options.ClientOptions(
            api_endpoint=location + "-aiplatform.googleapis.com"
        )
        self.client_info = gapic_v1.client_info.ClientInfo(
            user_agent="preview-pipeline-jobs-batch-delete"
        )
        self.pipeline_client = aiplatform_v1beta1.PipelineServiceClient(
            client_options=self.client_options, client_info=self.client_info
        )

    def batch_delete_pieline_jobs(
        self,
        names: List[str],
    ) -> aiplatform_v1beta1.BatchDeletePipelineJobsResponse:
        """
        Example Usage:

          runner = aiplatform.PipelineJobsBatchDeleteRunner(
              project='your_project_id',
              location='your_location',
          )
          runner.batch_delete_pieline_jobs(['pipeline_job_name',
          'pipeline_job_name2'])

        Args:

          names: Required. The names of the PipelineJobs to delete. A
               maximum of 32 PipelineJobs can be deleted in a batch.

        Returns:
          BatchDeletePipelineJobsResponse contains PipelineJobs deleted.
        """
        parent = "projects/{project}/locations/{location}".format(
            project=self.project, location=self.location
        )
        pipeline_jobs_names = [
            "projects/{project}/locations/{location}/"
            "pipelineJobs/{pipelineJob}".format(
                project=self.project, location=self.location, pipelineJob=name
            )
            for name in names
        ]
        request = aiplatform_v1beta1.BatchDeletePipelineJobsRequest(
            parent=parent, names=pipeline_jobs_names
        )
        return self.pipeline_client.batch_delete_pipeline_jobs(request)
