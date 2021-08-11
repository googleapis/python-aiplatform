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

import csv
import logging

from typing import Dict, List, Optional, Sequence, Set, Tuple, Union

from google.auth import credentials as auth_credentials

from google.cloud import bigquery
from google.cloud import storage

from google.cloud.aiplatform import datasets
from google.cloud.aiplatform.datasets import _datasources
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import schema
from google.cloud.aiplatform import utils


class TabularDataset(datasets._Dataset):
    """Managed tabular dataset resource for Vertex AI."""

    _supported_metadata_schema_uris: Optional[Tuple[str]] = (
        schema.dataset.metadata.tabular,
    )

    @property
    def column_names(self) -> List[str]:
        """Retrieve the columns for the dataset by extracting it from the Google Cloud Storage or
        Google BigQuery source.

        Returns:
            List[str]
                A list of columns names

        Raises:
            RuntimeError: When no valid source is found.
        """

        self._assert_gca_resource_is_available()

        metadata = self._gca_resource.metadata

        if metadata is None:
            raise RuntimeError("No metadata found for dataset")

        input_config = metadata.get("inputConfig")

        if input_config is None:
            raise RuntimeError("No inputConfig found for dataset")

        gcs_source = input_config.get("gcsSource")
        bq_source = input_config.get("bigquerySource")

        if gcs_source:
            gcs_source_uris = gcs_source.get("uri")

            if gcs_source_uris and len(gcs_source_uris) > 0:
                # Lexicographically sort the files
                gcs_source_uris.sort()

                # Get the first file in sorted list
                # TODO(b/193044977): Return as Set instead of List
                return list(
                    self._retrieve_gcs_source_columns(
                        project=self.project,
                        gcs_csv_file_path=gcs_source_uris[0],
                        credentials=self.credentials,
                    )
                )
        elif bq_source:
            bq_table_uri = bq_source.get("uri")
            if bq_table_uri:
                # TODO(b/193044977): Return as Set instead of List
                return list(
                    self._retrieve_bq_source_columns(
                        project=self.project,
                        bq_table_uri=bq_table_uri,
                        credentials=self.credentials,
                    )
                )

        raise RuntimeError("No valid CSV or BigQuery datasource found.")

    @staticmethod
    def _retrieve_gcs_source_columns(
        project: str,
        gcs_csv_file_path: str,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> Set[str]:
        """Retrieve the columns from a comma-delimited CSV file stored on Google Cloud Storage

        Example Usage:

            column_names = _retrieve_gcs_source_columns(
                "project_id",
                "gs://example-bucket/path/to/csv_file"
            )

            # column_names = {"column_1", "column_2"}

        Args:
            project (str):
                Required. Project to initiate the Google Cloud Storage client with.
            gcs_csv_file_path (str):
                Required. A full path to a CSV files stored on Google Cloud Storage.
                Must include "gs://" prefix.
            credentials (auth_credentials.Credentials):
                Credentials to use to with GCS Client.
        Returns:
            Set[str]
                A set of columns names in the CSV file.

        Raises:
            RuntimeError: When the retrieved CSV file is invalid.
        """

        gcs_bucket, gcs_blob = utils.extract_bucket_and_prefix_from_gcs_path(
            gcs_csv_file_path
        )
        client = storage.Client(project=project, credentials=credentials)
        bucket = client.bucket(gcs_bucket)
        blob = bucket.blob(gcs_blob)

        # Incrementally download the CSV file until the header is retrieved
        first_new_line_index = -1
        start_index = 0
        increment = 1000
        line = ""

        try:
            logger = logging.getLogger("google.resumable_media._helpers")
            logging_warning_filter = utils.LoggingFilter(logging.INFO)
            logger.addFilter(logging_warning_filter)

            while first_new_line_index == -1:
                line += blob.download_as_bytes(
                    start=start_index, end=start_index + increment - 1
                ).decode("utf-8")

                first_new_line_index = line.find("\n")
                start_index += increment

            header_line = line[:first_new_line_index]

            # Split to make it an iterable
            header_line = header_line.split("\n")[:1]

            csv_reader = csv.reader(header_line, delimiter=",")
        except (ValueError, RuntimeError) as err:
            raise RuntimeError(
                "There was a problem extracting the headers from the CSV file at '{}': {}".format(
                    gcs_csv_file_path, err
                )
            )
        finally:
            logger.removeFilter(logging_warning_filter)

        return set(next(csv_reader))

    @staticmethod
    def _get_bq_schema_field_names_recursively(
        schema_field: bigquery.SchemaField,
    ) -> Set[str]:
        """Retrieve the name for a schema field along with ancestor fields.
        Nested schema fields are flattened and concatenated with a ".".
        Schema fields with child fields are not included, but the children are.

        Args:
            project (str):
                Required. Project to initiate the BigQuery client with.
            bq_table_uri (str):
                Required. A URI to a BigQuery table.
                Can include "bq://" prefix but not required.
            credentials (auth_credentials.Credentials):
                Credentials to use with BQ Client.

        Returns:
            Set[str]
                A set of columns names in the BigQuery table.
        """

        ancestor_names = {
            nested_field_name
            for field in schema_field.fields
            for nested_field_name in TabularDataset._get_bq_schema_field_names_recursively(
                field
            )
        }

        # Only return "leaf nodes", basically any field that doesn't have children
        if len(ancestor_names) == 0:
            return {schema_field.name}
        else:
            return {f"{schema_field.name}.{name}" for name in ancestor_names}

    @staticmethod
    def _retrieve_bq_source_columns(
        project: str,
        bq_table_uri: str,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> Set[str]:
        """Retrieve the column names from a table on Google BigQuery
        Nested schema fields are flattened and concatenated with a ".".
        Schema fields with child fields are not included, but the children are.

        Example Usage:

            column_names = _retrieve_bq_source_columns(
                "project_id",
                "bq://project_id.dataset.table"
            )

            # column_names = {"column_1", "column_2", "column_3.nested_field"}

        Args:
            project (str):
                Required. Project to initiate the BigQuery client with.
            bq_table_uri (str):
                Required. A URI to a BigQuery table.
                Can include "bq://" prefix but not required.
            credentials (auth_credentials.Credentials):
                Credentials to use with BQ Client.

        Returns:
            Set[str]
                A set of column names in the BigQuery table.
        """

        # Remove bq:// prefix
        prefix = "bq://"
        if bq_table_uri.startswith(prefix):
            bq_table_uri = bq_table_uri[len(prefix) :]

        client = bigquery.Client(project=project, credentials=credentials)
        table = client.get_table(bq_table_uri)
        schema = table.schema

        return {
            field_name
            for field in schema
            for field_name in TabularDataset._get_bq_schema_field_names_recursively(
                field
            )
        }

    @classmethod
    def create(
        cls,
        display_name: str,
        gcs_source: Optional[Union[str, Sequence[str]]] = None,
        bq_source: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        labels: Optional[Dict[str, str]] = None,
        encryption_spec_key_name: Optional[str] = None,
        sync: bool = True,
    ) -> "TabularDataset":
        """Creates a new tabular dataset.

        Args:
            display_name (str):
                Required. The user-defined name of the Dataset.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            gcs_source (Union[str, Sequence[str]]):
                Google Cloud Storage URI(-s) to the
                input file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
                examples:
                    str: "gs://bucket/file.csv"
                    Sequence[str]: ["gs://bucket/file1.csv", "gs://bucket/file2.csv"]
            bq_source (str):
                BigQuery URI to the input table.
                example:
                    "bq://project.dataset.table_name"
            project (str):
                Project to upload this model to. Overrides project set in
                aiplatform.init.
            location (str):
                Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
            request_metadata (Sequence[Tuple[str, str]]):
                Strings which should be sent along with the request as metadata.
            labels (Dict[str, str]):
                Optional. Labels with user-defined metadata to organize your Tensorboards.
                Label keys and values can be no longer than 64 characters
                (Unicode codepoints), can only contain lowercase letters, numeric
                characters, underscores and dashes. International characters are allowed.
                No more than 64 user labels can be associated with one Tensorboard
                (System labels are excluded).
                See https://goo.gl/xmQnxf for more information and examples of labels.
                System reserved label keys are prefixed with "aiplatform.googleapis.com/"
                and are immutable.
            encryption_spec_key_name (Optional[str]):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the dataset. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If set, this Dataset and all sub-resources of this Dataset will be secured by this key.

                Overrides encryption_spec_key_name set in aiplatform.init.
            sync (bool):
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            tabular_dataset (TabularDataset):
                Instantiated representation of the managed tabular dataset resource.
        """

        utils.validate_display_name(display_name)
        if labels:
            utils.validate_labels(labels)

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        metadata_schema_uri = schema.dataset.metadata.tabular

        datasource = _datasources.create_datasource(
            metadata_schema_uri=metadata_schema_uri,
            gcs_source=gcs_source,
            bq_source=bq_source,
        )

        return cls._create_and_import(
            api_client=api_client,
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            display_name=display_name,
            metadata_schema_uri=metadata_schema_uri,
            datasource=datasource,
            project=project or initializer.global_config.project,
            location=location or initializer.global_config.location,
            credentials=credentials or initializer.global_config.credentials,
            request_metadata=request_metadata,
            labels=labels,
            encryption_spec=initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name
            ),
            sync=sync,
        )

    def import_data(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} class does not support 'import_data'"
        )
