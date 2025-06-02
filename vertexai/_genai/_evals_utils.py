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
"""Utility functions for evals."""
import io
import json
import logging
import os
import time
from typing import Any, Union
from google.cloud import bigquery
from google.cloud import storage
from google.genai._api_client import BaseApiClient
import pandas as pd

logger = logging.getLogger(__name__)


GCS_PREFIX = "gs://"
BQ_PREFIX = "bq://"


class GcsUtils:
    """Handles File I/O operations with Google Cloud Storage (GCS)"""

    def __init__(self, api_client: BaseApiClient):
        self.api_client = api_client
        self.storage_client = storage.Client(
            project=self.api_client.project,
            credentials=self.api_client._credentials,
        )

    def parse_gcs_path(self, gcs_path: str) -> tuple[str, str]:
        """Helper to parse gs://bucket/path into (bucket_name, blob_path)."""
        if not gcs_path.startswith(GCS_PREFIX):
            raise ValueError(
                f"Invalid GCS path: '{gcs_path}'. It must start with '{GCS_PREFIX}'."
            )
        path_without_prefix = gcs_path[len(GCS_PREFIX) :]
        if "/" not in path_without_prefix:
            return path_without_prefix, ""
        bucket_name, blob_path = path_without_prefix.split("/", 1)
        return bucket_name, blob_path

    def upload_file_to_gcs(self, upload_gcs_path: str, filename: str) -> None:
        """Uploads the provided file to a Google Cloud Storage location."""

        storage.Blob.from_string(
            uri=upload_gcs_path, client=self.storage_client
        ).upload_from_filename(filename)

    def upload_dataframe(
        self,
        df: "pd.DataFrame",
        gcs_destination_blob_path: str,
        file_type: str = "jsonl",
    ) -> None:
        """Uploads a Pandas DataFrame to a Google Cloud Storage location.

        Args:
          df: The Pandas DataFrame to upload.
          gcs_destination_blob_path: The full GCS path for the destination blob
            (e.g., 'gs://bucket/data/my_dataframe.jsonl').
          file_type: The format to save the DataFrame ('jsonl' or 'csv'). Defaults
            to 'jsonl'.
        """
        bucket_name, blob_name = self.parse_gcs_path(gcs_destination_blob_path)
        if not blob_name:
            raise ValueError(
                f"Invalid GCS path for blob: '{gcs_destination_blob_path}'. "
                "It must include the object name (e.g., gs://bucket/file.csv)."
            )
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        buffer = io.StringIO()
        if file_type == "csv":
            df.to_csv(buffer, index=False)
            content_type = "text/csv"
        elif file_type == "jsonl":
            df.to_json(buffer, orient="records", lines=True)
            content_type = "application/jsonl"
        else:
            raise ValueError(
                f"Unsupported file type: '{file_type}'. "
                "Please provide 'jsonl' or 'csv'."
            )
        blob.upload_from_string(buffer.getvalue(), content_type=content_type)

        logger.info(
            f"DataFrame successfully uploaded to: gs://{bucket.name}/{blob.name}"
        )

    def upload_json(self, data: dict[str, Any], gcs_destination_blob_path: str) -> None:
        """Uploads a dictionary as a JSON file to Google Cloud Storage."""
        bucket_name, blob_name = self.parse_gcs_path(gcs_destination_blob_path)
        if not blob_name:
            raise ValueError(
                f"Invalid GCS path for blob: '{gcs_destination_blob_path}'. "
                "It must include the object name (e.g., gs://bucket/file.json)."
            )
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        json_data = json.dumps(data, indent=2)
        blob.upload_from_string(json_data, content_type="application/json")

        logger.info(
            f"JSON data successfully uploaded to: gs://{bucket_name}/{blob_name}"
        )

    def upload_json_to_prefix(
        self,
        data: dict[str, Any],
        gcs_dest_prefix: str,
        filename_prefix: str = "data",
    ) -> str:
        """Uploads a dictionary to a GCS prefix with a timestamped JSON filename.

        Args:
          data: The dictionary to upload.
          gcs_dest_prefix: The GCS prefix (e.g., 'gs://bucket/path/prefix/').
          filename_prefix: Prefix for the generated filename. Defaults to 'data'.

        Returns:
          The full GCS path where the file was uploaded.

        Raises:
          ValueError: If the gcs_dest_prefix is not a valid GCS path.
        """
        if not gcs_dest_prefix.startswith(GCS_PREFIX):
            raise ValueError(
                f"Invalid GCS destination prefix: '{gcs_dest_prefix}'. Must start"
                f" with '{GCS_PREFIX}'."
            )

        gcs_path_without_scheme = gcs_dest_prefix[len(GCS_PREFIX) :]
        bucket_name, *path_parts = gcs_path_without_scheme.split("/")

        user_prefix_path = "/".join(path_parts)
        if user_prefix_path and not user_prefix_path.endswith("/"):
            user_prefix_path += "/"

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"

        blob_name = f"{user_prefix_path}{filename}"

        full_gcs_path = f"{GCS_PREFIX}{bucket_name}/{blob_name}"

        self.upload_json(data, full_gcs_path)
        return full_gcs_path

    def read_file_contents(self, gcs_filepath: str) -> str:
        """Reads the contents of a file from Google Cloud Storage."""

        bucket_name, blob_path = self.parse_gcs_path(gcs_filepath)
        if not blob_path:
            raise ValueError(
                f"Invalid GCS file path: '{gcs_filepath}'. Path must point to a file,"
                " not just a bucket."
            )
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        content = blob.download_as_string().decode("utf-8")
        logger.info(f"Successfully read content from '{gcs_filepath}'")
        return content

    def read_gcs_file_to_dataframe(
        self, gcs_filepath: str, file_type: str
    ) -> "pd.DataFrame":
        """Reads a file from Google Cloud Storage into a Pandas DataFrame."""
        file_contents = self.read_file_contents(gcs_filepath)
        if file_type == "csv":
            return pd.read_csv(io.StringIO(file_contents), encoding="utf-8")
        elif file_type == "jsonl":
            return pd.read_json(io.StringIO(file_contents), lines=True)
        else:
            raise ValueError(
                f"Unsupported file type: '{file_type}'. Please provide 'jsonl' or"
                " 'csv'."
            )


class BigQueryUtils:
    """Handles BigQuery operations."""

    def __init__(self, api_client: BaseApiClient):
        self.api_client = api_client
        self.bigquery_client = bigquery.Client(
            project=self.api_client.project,
            credentials=self.api_client._credentials,
        )

    def load_bigquery_to_dataframe(self, table_uri: str) -> "pd.DataFrame":
        """Loads data from a BigQuery table into a DataFrame."""
        table = self.bigquery_client.get_table(table_uri)
        return self.bigquery_client.list_rows(table).to_dataframe()

    def upload_dataframe_to_bigquery(
        self, df: "pd.DataFrame", bq_table_uri: str
    ) -> None:
        """Uploads a Pandas DataFrame to a BigQuery table."""
        job = self.bigquery_client.load_table_from_dataframe(df, bq_table_uri)
        job.result()
        logger.info(
            f"DataFrame successfully uploaded to BigQuery table: {bq_table_uri}"
        )


class EvalDatasetLoader:
    """A loader for datasets from various sources, using a shared client."""

    def __init__(self, api_client: BaseApiClient):
        self.api_client = api_client
        self.gcs_utils = GcsUtils(self.api_client)
        self.bigquery_utils = BigQueryUtils(self.api_client)

    def _load_file(self, filepath: str, file_type: str) -> list[dict[str, Any]]:
        """Loads data from a file into a list of dictionaries."""
        if filepath.startswith(GCS_PREFIX):
            df = self.gcs_utils.read_gcs_file_to_dataframe(filepath, file_type)
            return df.to_dict(orient="records")
        else:
            if file_type == "jsonl":
                df = pd.read_json(filepath, lines=True)
                return df.to_dict(orient="records")
            elif file_type == "csv":
                df = pd.read_csv(filepath, encoding="utf-8")
                return df.to_dict(orient="records")
            else:
                raise ValueError(
                    f"Unsupported file type: '{file_type}'. Please provide 'jsonl' or"
                    " 'csv'."
                )

    def load(self, source: Union[str, "pd.DataFrame"]) -> list[dict[str, Any]]:
        """Loads dataset from various sources into a list of dictionaries."""
        if isinstance(source, pd.DataFrame):
            return source.to_dict(orient="records")
        elif isinstance(source, str):
            if source.startswith(BQ_PREFIX):
                df = self.bigquery_utils.load_bigquery_to_dataframe(
                    source[len(BQ_PREFIX) :]
                )
                return df.to_dict(orient="records")

            _, extension = os.path.splitext(source)
            file_type = extension.lower()[1:]

            if file_type == "jsonl":
                return self._load_file(source, "jsonl")
            elif file_type == "csv":
                return self._load_file(source, "csv")
            else:
                raise TypeError(
                    f"Unsupported file type: {file_type} from {source}. Please"
                    " provide a valid GCS path with `jsonl` or `csv` suffix, "
                    "a local file path, or a valid BigQuery table URI."
                )
        else:
            raise TypeError(
                "Unsupported dataset type. Must be a `pd.DataFrame`, Python"
                " a valid GCS path with `jsonl` or `csv` suffix, a local"
                " file path, or a valid BigQuery table URI."
            )
