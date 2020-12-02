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

from typing import Optional, Sequence, Dict, Tuple

from google.api_core import operation
from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import schema
from google.cloud.aiplatform.data_source import DataSource, DataImportable, GCSNonTabularDataSource, GCSNonTabularImportDataSource

from google.cloud.aiplatform_v1beta1 import GcsDestination
from google.cloud.aiplatform_v1beta1 import ExportDataConfig
from google.cloud.aiplatform_v1beta1 import ImportDataConfig
from google.cloud.aiplatform_v1beta1 import Dataset as GapicDataset
from google.cloud.aiplatform_v1beta1 import DatasetServiceClient


# TODO(b/171275584): Add async support to Dataset class
class Dataset(base.AiPlatformResourceNoun):
    """Managed dataset resource for AI Platform"""

    client_class = DatasetServiceClient
    _is_client_prediction_client = False

    def __init__(
        self,
        dataset_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing managed dataset given a dataset name or ID.

        Args:
            dataset_name (str):
                Required. A fully-qualified dataset resource name or dataset ID.
                Example: "projects/123/locations/us-central1/datasets/456" or
                "456" when project and location are initialized or passed.
            project (str):
                Optional project to retrieve dataset from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional location to retrieve dataset from. If not set, location
                set in aiplatform.init will be used.
            credentials: Optional[auth_credentials.Credentials]=None,
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
        """

        dataset_name = utils.full_resource_name(
            resource_name=dataset_name,
            resource_noun="datasets",
            project=project,
            location=location,
        )

        super().__init__(project=project, location=location, credentials=credentials)
        self._gca_resource = self.api_client.get_dataset(name=dataset_name)

    @classmethod
    def create(
        cls,
        display_name: str,
        source: DataSource,
        request_metadata: Sequence[Tuple[str, str]] = (),
        labels: Optional[Dict] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "Dataset":
        """Creates a new dataset and optionally imports data into dataset when
        source and import_schema_uri are passed.

        Args:
            display_name (str):
                Required. The user-defined name of the Dataset.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            source: TODO
            bq_source: Optional[str]=None:
                BigQuery URI to the input table.
            import_schema_uri: Optional[str] = None
                Points to a YAML file stored on Google Cloud
                Storage describing the import format. Validation will be
                done against the schema. The schema is defined as an
                `OpenAPI 3.0.2 Schema
                Object <https://tinyurl.com/y538mdwt>`__.
            metadata: Sequence[Tuple[str, str]]=()
                Strings which should be sent along with the request as metadata.
            labels: (Optional[Dict]) = None
                The labels with user-defined metadata to organize your
                Datasets.

                Label keys and values can be no longer than 64 characters
                (Unicode codepoints), can only contain lowercase letters,
                numeric characters, underscores and dashes. International
                characters are allowed. No more than 64 user labels can be
                associated with one Dataset (System labels are excluded).

                See https://goo.gl/xmQnxf for more information and examples
                of labels. System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            project: Optional[str]=None,
                Project to upload this model to. Overrides project set in
                aiplatform.init.
            location: Optional[str]=None,
                Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials: Optional[auth_credentials.Credentials]=None,
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
        Returns:
            dataset (Dataset):
                Instantiated representation of the managed dataset resource.
        """
        utils.validate_display_name(display_name)

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        create_dataset_lro = cls._create(
            display_name=display_name,
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            metadata_schema_uri=source.metadata_schema_uri,
            dataset_metadata=source.metadata,
            request_metadata=request_metadata,
            labels=labels,
            api_client=api_client,
        )

        created_dataset = create_dataset_lro.result()

        dataset_obj = cls(
            dataset_name=created_dataset.name,
            project=project,
            location=location,
            credentials=credentials,
        )

        # Import if source is an importable type
        if isinstance(source, DataImportable):
            return dataset_obj.import_data(source=source)
        else:
            return dataset_obj

    @classmethod
    def _create(
        cls,
        api_client: DatasetServiceClient,
        parent: str,
        display_name: str,
        metadata_schema_uri: str,
        dataset_metadata: Dict,
        labels: Optional[Dict] = {},
        request_metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation.Operation:
        """Creates a new managed dataset by directly calling API client.

        Args:
            api_client (DatasetServiceClient):
                An instance of DatasetServiceClient with the correct api_endpoint
                already set based on user's preferences.
            parent (str):
                Also known as common location path, that usually contains the
                project and location that the user provided to the upstream method.
                Example: "projects/my-prj/locations/us-central1"
            display_name (str):
                Required. The user-defined name of the Dataset.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            metadata_schema_uri (str):
                Required. Points to a YAML file stored on Google Cloud Storage
                describing additional information about the Dataset. The schema
                is defined as an OpenAPI 3.0.2 Schema Object. The schema files
                that can be used here are found in gs://google-cloud-
                aiplatform/schema/dataset/metadata/.
            dataset_metadata (dict):
                Required. Additional information about the Dataset.
            labels: (Optional[Dict]) = None
                The labels with user-defined metadata to organize your
                Datasets.

                Label keys and values can be no longer than 64 characters
                (Unicode codepoints), can only contain lowercase letters,
                numeric characters, underscores and dashes. International
                characters are allowed. No more than 64 user labels can be
                associated with one Dataset (System labels are excluded).

                See https://goo.gl/xmQnxf for more information and examples
                of labels. System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            request_metadata: Sequence[Tuple[str, str]] = ()
                Strings which should be sent along with the create_dataset
                request as metadata. Usually to specify special dataset config.
        Returns:
            operation (Operation):
                An object representing a long-running operation.
        """
        gapic_dataset = GapicDataset(
            display_name=display_name,
            metadata_schema_uri=metadata_schema_uri,
            metadata=dataset_metadata,
            labels=labels,
        )

        return api_client.create_dataset(
            parent=parent, dataset=gapic_dataset, metadata=request_metadata
        )

    def import_data(
        self,
        source: DataImportable
    ) -> "Dataset":
        """Upload data to existing managed dataset.

        Args:
            source: TODO
        Returns:
            dataset (Dataset):
                Instantiated representation of the managed dataset resource.
        """

        import_lro = self.api_client.import_data(
            name=self.resource_name, import_configs=[source.import_data_config]
        )

        import_lro.result()  # An empty response upon successful import

        return self

    def export_data(self, output_dir: str) -> Sequence[str]:
        """Exports data to output dir to GCS.

        Args:
            output_dir (str):
                Required. The Google Cloud Storage location where the output is to
                be written to. In the given directory a new directory will be
                created with name:
                ``export-data-<dataset-display-name>-<timestamp-of-export-call>``
                where timestamp is in YYYYMMDDHHMMSS format. All export
                output will be written into that directory. Inside that
                directory, annotations with the same schema will be grouped
                into sub directories which are named with the corresponding
                annotations' schema title. Inside these sub directories, a
                schema.yaml will be created to describe the output format.

                If the uri doesn't end with '/', a '/' will be automatically
                appended. The directory is created if it doesn't exist.

        Returns:
            exported_files (Sequence[str]):
                All of the files that are exported in this export operation.
        """
        # TODO(b/171311614): Add support for BiqQuery export path
        export_data_config = ExportDataConfig(
            gcs_destination=GcsDestination(output_uri_prefix=output_dir)
        )

        export_lro = self.api_client.export_data(
            name=self.resource_name, export_config=export_data_config
        )

        export_data_response = export_lro.result()

        return export_data_response.exported_files

    def update(self):
        raise NotImplementedError("Update dataset has not been implemented yet")
