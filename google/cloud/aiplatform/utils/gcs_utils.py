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


import datetime
import glob
import logging
import pathlib
from typing import Optional

from google.auth import credentials as auth_credentials
from google.cloud import storage

from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.utils import resource_manager_utils

_logger = logging.getLogger(__name__)


def upload_to_gcs(
    source_path: str,
    destination_uri: str,
    project: Optional[str] = None,
    credentials: Optional[auth_credentials.Credentials] = None,
):
    """Uploads local files to GCS.

    After upload the `destination_uri` will contain the same data as the `source_path`.

    Args:
        source_path: Required. Path of the local data to copy to GCS.
        destination_uri: Required. GCS URI where the data should be uploaded.
        project: Optional. Google Cloud Project that contains the staging bucket.
        credentials: The custom credentials to use when making API calls.
            If not provided, default credentials will be used.

    Raises:
        RuntimeError: When source_path does not exist.
        GoogleCloudError: When the upload process fails.
    """
    source_path_obj = pathlib.Path(source_path)
    if not source_path_obj.exists():
        raise RuntimeError(f"Source path does not exist: {source_path}")

    project = project or initializer.global_config.project
    credentials = credentials or initializer.global_config.credentials

    storage_client = storage.Client(project=project, credentials=credentials)
    if source_path_obj.is_dir():
        source_file_paths = glob.glob(
            pathname=str(source_path_obj / "**"), recursive=True
        )
        for source_file_path in source_file_paths:
            source_file_path_obj = pathlib.Path(source_file_path)
            if source_file_path_obj.is_dir():
                continue
            source_file_relative_path_obj = source_file_path_obj.relative_to(
                source_path_obj
            )
            source_file_relative_posix_path = source_file_relative_path_obj.as_posix()
            destination_file_uri = (
                destination_uri.rstrip("/") + "/" + source_file_relative_posix_path
            )
            _logger.debug(f'Uploading "{source_file_path}" to "{destination_file_uri}"')
            destination_blob = storage.Blob.from_string(
                destination_file_uri, client=storage_client
            )
            destination_blob.upload_from_filename(filename=source_file_path)
    else:
        source_file_path = source_path
        destination_file_uri = destination_uri
        _logger.debug(f'Uploading "{source_file_path}" to "{destination_file_uri}"')
        destination_blob = storage.Blob.from_string(
            destination_file_uri, client=storage_client
        )
        destination_blob.upload_from_filename(filename=source_file_path)


def stage_local_data_in_gcs(
    data_path: str,
    staging_gcs_dir: Optional[str] = None,
    project: Optional[str] = None,
    location: Optional[str] = None,
    credentials: Optional[auth_credentials.Credentials] = None,
) -> str:
    """Stages a local data in GCS.

    The file copied to GCS is the name of the local file prepended with an
    "aiplatform-{timestamp}-" string.

    Args:
        data_path: Required. Path of the local data to copy to GCS.
        staging_gcs_dir:
            Optional. Google Cloud Storage bucket to be used for data staging.
        project: Optional. Google Cloud Project that contains the staging bucket.
        location: Optional. Google Cloud location to use for the staging bucket.
        credentials: The custom credentials to use when making API calls.
            If not provided, default credentials will be used.

    Returns:
        Google Cloud Storage URI of the staged data.

    Raises:
        RuntimeError: When source_path does not exist.
        GoogleCloudError: When the upload process fails.
    """
    data_path_obj = pathlib.Path(data_path)

    if not data_path_obj.exists():
        raise RuntimeError(f"Local data does not exist: data_path='{data_path}'")

    staging_gcs_dir = staging_gcs_dir or initializer.global_config.staging_bucket
    if not staging_gcs_dir:
        project = project or initializer.global_config.project
        location = location or initializer.global_config.location
        credentials = credentials or initializer.global_config.credentials
        # Creating the bucket if it does not exist.
        # Currently we only do this when staging_gcs_dir is not specified.
        # The buckets that we create are regional.
        # This prevents errors when some service required regional bucket.
        # E.g. "FailedPrecondition: 400 The Cloud Storage bucket of `gs://...` is in location `us`. It must be in the same regional location as the service location `us-central1`."
        # We are making the bucket name region-specific since the bucket is regional.
        staging_bucket_name = project + "-vertex-staging-" + location
        client = storage.Client(project=project, credentials=credentials)
        staging_bucket = storage.Bucket(client=client, name=staging_bucket_name)
        if not staging_bucket.exists():
            _logger.info(f'Creating staging GCS bucket "{staging_bucket_name}"')
            staging_bucket = client.create_bucket(
                bucket_or_name=staging_bucket,
                project=project,
                location=location,
            )
        staging_gcs_dir = "gs://" + staging_bucket_name

    timestamp = datetime.datetime.now().isoformat(sep="-", timespec="milliseconds")
    staging_gcs_subdir = (
        staging_gcs_dir.rstrip("/") + "/vertex_ai_auto_staging/" + timestamp
    )

    staged_data_uri = staging_gcs_subdir
    if data_path_obj.is_file():
        staged_data_uri = staging_gcs_subdir + "/" + data_path_obj.name

    _logger.info(f'Uploading "{data_path}" to "{staged_data_uri}"')
    upload_to_gcs(
        source_path=data_path,
        destination_uri=staged_data_uri,
        project=project,
        credentials=credentials,
    )

    return staged_data_uri


def generate_gcs_directory_for_pipeline_artifacts(
    project: Optional[str] = None,
    location: Optional[str] = None,
):
    """Gets or creates the GCS directory for Vertex Pipelines artifacts.

    Args:
        service_account: Optional. Google Cloud service account that will be used
            to run the pipelines. If this function creates a new bucket it will give
            permission to the specified service account to access the bucket.
            If not provided, the Google Cloud Compute Engine service account will be used.
        project: Optional. Google Cloud Project that contains the staging bucket.
        location: Optional. Google Cloud location to use for the staging bucket.

    Returns:
        Google Cloud Storage URI of the staged data.
    """
    project = project or initializer.global_config.project
    location = location or initializer.global_config.location

    pipelines_bucket_name = project + "-vertex-pipelines-" + location
    output_artifacts_gcs_dir = "gs://" + pipelines_bucket_name + "/output_artifacts/"
    return output_artifacts_gcs_dir


def create_gcs_bucket_for_pipeline_artifacts_if_it_does_not_exist(
    output_artifacts_gcs_dir: Optional[str] = None,
    service_account: Optional[str] = None,
    project: Optional[str] = None,
    location: Optional[str] = None,
    credentials: Optional[auth_credentials.Credentials] = None,
):
    """Gets or creates the GCS directory for Vertex Pipelines artifacts.

    Args:
        output_artifacts_gcs_dir: Optional. The GCS location for the pipeline outputs.
            It will be generated if not specified.
        service_account: Optional. Google Cloud service account that will be used
            to run the pipelines. If this function creates a new bucket it will give
            permission to the specified service account to access the bucket.
            If not provided, the Google Cloud Compute Engine service account will be used.
        project: Optional. Google Cloud Project that contains the staging bucket.
        location: Optional. Google Cloud location to use for the staging bucket.
        credentials: The custom credentials to use when making API calls.
            If not provided, default credentials will be used.

    Returns:
        Google Cloud Storage URI of the staged data.
    """
    project = project or initializer.global_config.project
    location = location or initializer.global_config.location
    credentials = credentials or initializer.global_config.credentials

    output_artifacts_gcs_dir = (
        output_artifacts_gcs_dir
        or generate_gcs_directory_for_pipeline_artifacts(
            project=project,
            location=location,
        )
    )

    # Creating the bucket if needed
    storage_client = storage.Client(
        project=project,
        credentials=credentials,
    )

    pipelines_bucket = storage.Blob.from_string(
        uri=output_artifacts_gcs_dir,
        client=storage_client,
    ).bucket

    if not pipelines_bucket.exists():
        _logger.info(
            f'Creating GCS bucket for Vertex Pipelines: "{pipelines_bucket.name}"'
        )
        pipelines_bucket = storage_client.create_bucket(
            bucket_or_name=pipelines_bucket,
            project=project,
            location=location,
        )
        # Giving the service account read and write access to the new bucket
        # Workaround for error: "Failed to create pipeline job. Error: Service account `NNNNNNNN-compute@developer.gserviceaccount.com`
        # does not have `[storage.objects.get, storage.objects.create]` IAM permission(s) to the bucket `xxxxxxxx-vertex-pipelines-us-central1`.
        # Please either copy the files to the Google Cloud Storage bucket owned by your project, or grant the required IAM permission(s) to the service account."
        if not service_account:
            # Getting the project number to use in service account
            project_number = resource_manager_utils.get_project_number(project)
            service_account = f"{project_number}-compute@developer.gserviceaccount.com"
        bucket_iam_policy = pipelines_bucket.get_iam_policy()
        bucket_iam_policy.setdefault("roles/storage.objectCreator", set()).add(
            f"serviceAccount:{service_account}"
        )
        bucket_iam_policy.setdefault("roles/storage.objectViewer", set()).add(
            f"serviceAccount:{service_account}"
        )
        pipelines_bucket.set_iam_policy(bucket_iam_policy)
    return output_artifacts_gcs_dir
