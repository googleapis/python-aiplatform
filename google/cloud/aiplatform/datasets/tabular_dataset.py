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

from typing import Dict, Optional, Sequence, Tuple, Union

from google.auth import credentials as auth_credentials

from google.cloud import bigquery
from google.cloud.aiplatform import base
from google.cloud.aiplatform import datasets
from google.cloud.aiplatform.datasets import _datasources
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import schema
from google.cloud.aiplatform import utils

_AUTOML_TRAINING_MIN_ROWS = 1000

_LOGGER = base.Logger(__name__)


class TabularDataset(datasets._ColumnNamesDataset):
    """Managed tabular dataset resource for Vertex AI."""

    _supported_metadata_schema_uris: Optional[Tuple[str]] = (
        schema.dataset.metadata.tabular,
    )

    @classmethod
    def create(
        cls,
        display_name: Optional[str] = None,
        gcs_source: Optional[Union[str, Sequence[str]]] = None,
        bq_source: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        labels: Optional[Dict[str, str]] = None,
        encryption_spec_key_name: Optional[str] = None,
        sync: bool = True,
        create_request_timeout: Optional[float] = None,
    ) -> "TabularDataset":
        """Creates a new tabular dataset.

        Args:
            display_name (str):
                Optional. The user-defined name of the Dataset.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            gcs_source (Union[str, Sequence[str]]):
                Google Cloud Storage URI(-s) to the
                input file(s).

                Examples:
                    str: "gs://bucket/file.csv"
                    Sequence[str]: ["gs://bucket/file1.csv", "gs://bucket/file2.csv"]
            bq_source (str):
                BigQuery URI to the input table.
                example:
                    "bq://project.dataset.table_name"
            project (str):
                Project to upload this dataset to. Overrides project set in
                aiplatform.init.
            location (str):
                Location to upload this dataset to. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to upload this dataset. Overrides
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
            create_request_timeout (float):
                Optional. The timeout for the create request in seconds.

        Returns:
            tabular_dataset (TabularDataset):
                Instantiated representation of the managed tabular dataset resource.
        """
        if not display_name:
            display_name = cls._generate_display_name()
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
            create_request_timeout=create_request_timeout,
        )

    @classmethod
    def create_from_dataframe(
        cls,
        df_source: "pd.DataFrame",  # noqa: F821 - skip check for undefined name 'pd'
        staging_path: str,
        bq_schema: Optional[Union[str, bigquery.SchemaField]] = None,
        display_name: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "TabularDataset":
        """Creates a new tabular dataset from a Pandas DataFrame.

        Args:
            df_source (pd.DataFrame):
                Required. Pandas DataFrame containing the source data for
                ingestion as a TabularDataset. This method will use the data
                types from the provided DataFrame when creating the dataset.
            staging_path (str):
                Required. The BigQuery table to stage the data
                for Vertex. Because Vertex maintains a reference to this source
                to create the Vertex Dataset, this BigQuery table should
                not be deleted. Example: `bq://my-project.my-dataset.my-table`.
                If the provided BigQuery table doesn't exist, this method will
                create the table. If the provided BigQuery table already exists,
                and the schemas of the BigQuery table and your DataFrame match,
                this method will append the data in your local DataFrame to the table.
                The location of the provided BigQuery table should conform to the location requirements
                specified here: https://cloud.google.com/vertex-ai/docs/general/locations#bq-locations.
            bq_schema (Optional[Union[str, bigquery.SchemaField]]):
                Optional. If not set, BigQuery will autodetect the schema using your DataFrame's column types.
                If set, BigQuery will use the schema you provide when creating the staging table. For more details,
                see: https://cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.job.LoadJobConfig#google_cloud_bigquery_job_LoadJobConfig_schema
            display_name (str):
                Optional. The user-defined name of the Dataset.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 charact
            project (str):
                Optional. Project to upload this dataset to. Overrides project set in
                aiplatform.init.
            location (str):
                Optional. Location to upload this dataset to. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to upload this dataset. Overrides
                credentials set in aiplatform.init.
        Returns:
            tabular_dataset (TabularDataset):
                Instantiated representation of the managed tabular dataset resource.
        """

        if staging_path.startswith("bq://"):
            bq_staging_path = staging_path[len("bq://") :]
        else:
            raise ValueError(
                "Only BigQuery staging paths are supported. Provide a staging path in the format `bq://your-project.your-dataset.your-table`."
            )

        try:
            import pyarrow  # noqa: F401 - skip check for 'pyarrow' which is required when using 'google.cloud.bigquery'
        except ImportError:
            raise ImportError(
                "Pyarrow is not installed, and is required to use the BigQuery client."
                'Please install the SDK using "pip install google-cloud-aiplatform[datasets]"'
            )
        import pandas.api.types as pd_types

        if any(
            [
                pd_types.is_datetime64_any_dtype(df_source[column])
                for column in df_source.columns
            ]
        ):
            _LOGGER.info(
                "Received datetime-like column in the dataframe. Please note that the column could be interpreted differently in BigQuery depending on which major version you are using. For more information, please reference the BigQuery v3 release notes here: https://github.com/googleapis/python-bigquery/releases/tag/v3.0.0"
            )

        if len(df_source) < _AUTOML_TRAINING_MIN_ROWS:
            _LOGGER.info(
                "Your DataFrame has %s rows and AutoML requires %s rows to train on tabular data. You can still train a custom model once your dataset has been uploaded to Vertex, but you will not be able to use AutoML for training."
                % (len(df_source), _AUTOML_TRAINING_MIN_ROWS),
            )

        bigquery_client = bigquery.Client(
            project=project or initializer.global_config.project,
            credentials=credentials or initializer.global_config.credentials,
        )

        try:
            parquet_options = bigquery.format_options.ParquetOptions()
            parquet_options.enable_list_inference = True

            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.PARQUET,
                parquet_options=parquet_options,
            )

            if bq_schema:
                job_config.schema = bq_schema

            job = bigquery_client.load_table_from_dataframe(
                dataframe=df_source, destination=bq_staging_path, job_config=job_config
            )

            job.result()

        finally:
            dataset_from_dataframe = cls.create(
                display_name=display_name,
                bq_source=staging_path,
                project=project,
                location=location,
                credentials=credentials,
            )

        return dataset_from_dataframe

    def import_data(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} class does not support 'import_data'"
        )
