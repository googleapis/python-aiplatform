# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

from abc import abstractclassmethod
from typing import Iterable, Optional, Union

from google.cloud import storage
from google.cloud import bigquery

from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import base
from google.cloud.aiplatform.gapic import JobState
from google.cloud.aiplatform.gapic import JobServiceClient
from google.cloud.aiplatform.utils import full_resource_name


class _Job(base.AiPlatformResourceNoun):
    """
    Class that represents a general Job resource in AI Platform (Unified).
    Cannot be directly instantiated.

    Serves as base class to specific Job types, i.e. BatchPredictionJob or
    DataLabelingJob to re-use shared functionality.

    Subclasses requires one class attribute:

    getter_method (str): The name of JobServiceClient getter method for specific
    Job type, i.e. 'get_custom_job' for CustomJob
    """

    client_class = JobServiceClient
    _is_client_prediction_client = False

    @property
    @abstractclassmethod
    def getter_method(cls) -> str:
        """Name of getter method of Job subclass, i.e. 'get_custom_job' for CustomJob"""
        pass

    def __init__(
        self,
        valid_job_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """
        Retrives Job subclass resource by calling a subclass-specific getter method.

        Args:
             valid_job_name (str):
                A validated, fully-qualified Job resource name. For example:
                'projects/.../locations/.../batchPredictionJobs/456' or
                'projects/.../locations/.../customJobs/789'
            project: Optional[str] = None,
                Optional project to retrieve Job subclass from. If not set,
                project set in aiplatform.init will be used.
            location: Optional[str] = None,
                Optional location to retrieve Job subclass from. If not set,
                location set in aiplatform.init will be used.
            credentials: Optional[auth_credentials.Credentials] = None,
                Custom credentials to use. If not set, credentials set in
                aiplatform.init will be used.
        """
        super().__init__(project=project, location=location, credentials=credentials)
        self.job_subclass_getter_method = getattr(self.api_client, self.getter_method)
        self._gca_resource = self.job_subclass_getter_method(name=valid_job_name)

    def status(self) -> JobState:
        """Fetch Job again and return the current JobState.

        Returns:
            state (JobState):
                Enum that describes the state of a AI Platform job.
        """

        # Fetch the Job again for most up-to-date job state
        self._gca_resource = self.job_subclass_getter_method(
            name=self._gca_resource.name
        )

        return self._gca_resource.state


class BatchPredictionJob(_Job):

    getter_method = "get_batch_prediction_job"

    def __init__(
        self,
        batch_prediction_job_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """
        Retrieves a BatchPredictionJob resource and instantiates its representation.

        Args:
            batch_prediction_job_name (str):
                Required. A fully-qualified BatchPredictionJob resource name or ID.
                Example: "projects/.../locations/.../batchPredictionJobs/456" or
                "456" when project and location are initialized or passed.
            project: Optional[str] = None,
                Optional project to retrieve BatchPredictionJob from. If not set,
                project set in aiplatform.init will be used.
            location: Optional[str] = None,
                Optional location to retrieve BatchPredictionJob from. If not set,
                location set in aiplatform.init will be used.
            credentials: Optional[auth_credentials.Credentials] = None,
                Custom credentials to use. If not set, credentials set in
                aiplatform.init will be used.
        """
        valid_batch_prediction_job_name = full_resource_name(
            resource_name=batch_prediction_job_name,
            resource_noun="batchPredictionJobs",
            project=project,
            location=location,
        )

        super().__init__(
            valid_job_name=valid_batch_prediction_job_name,
            project=project,
            location=location,
            credentials=credentials,
        )

    def iter_outputs(
        self, bq_query_limit: Optional[int] = 100
    ) -> Iterable[Union[storage.Blob, bigquery.job.QueryJob]]:
        """Returns an Iterable object to traverse the output files, either a list
        of GCS Blobs or a BigQuery QueryJob depending on the output config set
        when the BatchPredictionJob was created.

        Args:
            bq_query_limit: Optional[int] = 100
                Limit on rows to select from prediction table in BigQuery dataset.
                Only used when retrieving predictions from a bigquery_destination_prefix.
                Default is 100.

        Returns:
            Iterable[Union[storage.Blob, bigquery.job.QueryJob]]:
                Either a list of GCS Blob objects within the prediction output
                directory or an iterable QueryJob with predictions.

        Raises:
            RuntimeError:
                If BatchPredictionJob is in a JobState other than SUCCEEDED,
                since outputs cannot be retrieved until the Job has finished.
            NotImplementedError:
                If BatchPredictionJob succeeded and output_info does not have a
                GCS or BQ output provided.
        """

        job_status = self.status()

        if job_status != JobState.JOB_STATE_SUCCEEDED:
            raise RuntimeError(
                f"Cannot read outputs until BatchPredictionJob has succeeded, "
                f"current status: {job_status}"
            )

        output_info = self._gca_resource.output_info

        # GCS Destination, return Blobs
        if output_info.gcs_output_directory not in ("", None):
            storage_client = storage.Client()
            blobs = storage_client.list_blobs(output_info.gcs_output_directory)
            return blobs

        # BigQuery Destination, return QueryJob
        elif output_info.bigquery_output_dataset not in ("", None):
            bq_client = bigquery.Client()
            bigquery.Client

            # Format from service is `bq://projectId.bqDatasetId`
            bq_dataset = output_info.bigquery_output_dataset

            if bq_dataset.startswith("bq://"):
                bq_dataset = bq_dataset[5:]
            if bq_dataset.endswith(("/", ".")):
                bq_dataset = bq_dataset[:-1]

            # # Split project ID and BQ dataset ID
            _, bq_dataset_id = bq_dataset.split(".", 1)

            query_limit = f"LIMIT {bq_query_limit}" if bq_query_limit else ""
            query = f"SELECT * FROM {bq_dataset_id}.predictions {query_limit}"
            query_job = bq_client.query(query)

            return query_job

        # Unknown Destination type
        else:
            raise NotImplementedError(
                f"Unsupported batch prediction output location, here are details"
                f"on your prediction output:\n{output_info}"
            )


class CustomJob(_Job):
    getter_method = "get_custom_job"
    pass


class DataLabelingJob(_Job):
    getter_method = "get_data_labeling_job"
    pass


class HyperparameterTuningJob(_Job):
    getter_method = "get_hyperparameter_tuning_job"
    pass
