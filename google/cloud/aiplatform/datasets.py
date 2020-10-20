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
from google.cloud.aiplatform.utils import validate_id
from google.cloud.aiplatform.utils import extract_fields_from_resource_name

from google.cloud.aiplatform_v1beta1 import GcsSource
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

        # Fully qualified dataset name, i.e. "projects/.../locations/.../datasets/12345"
        valid_name = extract_fields_from_resource_name(
            resource_name=dataset_name, resource_noun="datasets"
        )

        # Partial dataset name (i.e. "12345") with known project and location
        if (
            not valid_name
            and validate_id(dataset_name)
            and (project or initializer.global_config.project)
            and (location or initializer.global_config.location)
        ):
            dataset_name = DatasetServiceClient.dataset_path(
                project=project or initializer.global_config.project,
                location=location or initializer.global_config.location,
                dataset=dataset_name,
            )

        # Invalid dataset_name parameter
        elif not valid_name:
            raise ValueError("Please provide a valid dataset name or ID")

        super().__init__(project=project, location=location, credentials=credentials)
        self._gca_resource = self.api_client.get_dataset(name=dataset_name)

    @classmethod
    def create(
        cls,
        display_name: str,
        metadata_schema_uri: str,
        source: Optional[Sequence[str]] = None,
        import_schema_uri: Optional[str] = None,
        metadata: Sequence[Tuple[str, str]] = (),
        labels: Optional[Dict] = None,
        data_items_labels: Optional[Dict] = None,
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
            metadata_schema_uri (str):
                Required. Points to a YAML file stored on Google Cloud Storage
                describing additional information about the Dataset. The schema
                is defined as an OpenAPI 3.0.2 Schema Object. The schema files
                that can be used here are found in gs://google-cloud-
                aiplatform/schema/dataset/metadata/.
            source: Optional[Sequence[str]]=None:
                Google Cloud Storage URI(-s) to the
                input file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
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
            data_items_labels: Optional[Dict] = None
                Labels that will be applied to newly imported DataItems. If
                an identical DataItem as one being imported already exists
                in the Dataset, then these labels will be appended to these
                of the already existing one, and if labels with identical
                key is imported before, the old label value will be
                overwritten. If two DataItems are identical in the same
                import data operation, the labels will be combined and if
                key collision happens in this case, one of the values will
                be picked randomly. Two DataItems are considered identical
                if their content bytes are identical (e.g. image bytes or
                pdf bytes). These labels will be overridden by Annotation
                labels specified inside index file refenced by
                [import_schema_uri][google.cloud.aiplatform.v1beta1.ImportDataConfig.import_schema_uri],
                e.g. jsonl file.
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

        # Validate that source and import schema are passed together or not at all
        if bool(source) ^ bool(import_schema_uri):
            raise ValueError(
                "Please provide both source and import_schema_uri to import data or omit both."
            )

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        create_dataset_lro = cls._create(
            display_name=display_name,
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            metadata_schema_uri=metadata_schema_uri,
            request_metadata=metadata,
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

        # If an import source was not provided, return empty created Dataset.
        if not source:
            return dataset_obj

        return dataset_obj.import_data(
            gcs_source=source,
            import_schema_uri=import_schema_uri,
            data_items_labels=data_items_labels,
        )

    @classmethod
    def _create(
        cls,
        api_client: DatasetServiceClient,
        parent: str,
        display_name: str,
        metadata_schema_uri: str,
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
            labels=labels,
        )

        return api_client.create_dataset(
            parent=parent, dataset=gapic_dataset, metadata=request_metadata
        )

    def _import(
        self,
        source: Sequence[str],
        import_schema_uri: str,
        data_items_labels: Optional[Dict] = None,
    ) -> Optional[operation.Operation]:
        """Imports data into managed dataset by directly calling API client.

        Args:
            gcs_source (Sequence[str]):
                Required. Google Cloud Storage URI(-s) to the
                input file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
            import_schema_uri (str):
                Required. Points to a YAML file stored on Google Cloud
                Storage describing the import format. Validation will be
                done against the schema. The schema is defined as an
                `OpenAPI 3.0.2 Schema
                Object <https://tinyurl.com/y538mdwt>`__.
            data_item_labels: (Optional[Dict]) = None
                Labels that will be applied to newly imported DataItems. If
                an identical DataItem as one being imported already exists
                in the Dataset, then these labels will be appended to these
                of the already existing one, and if labels with identical
                key is imported before, the old label value will be
                overwritten. If two DataItems are identical in the same
                import data operation, the labels will be combined and if
                key collision happens in this case, one of the values will
                be picked randomly. Two DataItems are considered identical
                if their content bytes are identical (e.g. image bytes or
                pdf bytes). These labels will be overridden by Annotation
                labels specified inside index file refenced by
                [import_schema_uri][google.cloud.aiplatform.v1beta1.ImportDataConfig.import_schema_uri],
                e.g. jsonl file.
        Returns:
            operation (Operation):
                An object representing a long-running operation.
        """
        # TODO(b/171311614): Add support for BiqQuery import source
        import_config = ImportDataConfig(
            gcs_source=GcsSource(uris=[source] if type(source) == str else source),
            import_schema_uri=import_schema_uri,
            data_item_labels=data_items_labels,
        )

        return self.api_client.import_data(
            name=self.resource_name, import_configs=[import_config]
        )

    def import_data(
        self,
        gcs_source: Sequence[str],
        import_schema_uri: str,
        data_items_labels: Optional[Dict] = None,
    ) -> "Dataset":
        """Upload data to existing managed dataset.

        Args:
            gcs_source (Sequence[str]):
                Required. Google Cloud Storage URI(-s) to the
                input file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
            import_schema_uri (str):
                Required. Points to a YAML file stored on Google Cloud
                Storage describing the import format. Validation will be
                done against the schema. The schema is defined as an
                `OpenAPI 3.0.2 Schema
                Object <https://tinyurl.com/y538mdwt>`__.
            data_item_labels (Optional[Dict]):
                Labels that will be applied to newly imported DataItems. If
                an identical DataItem as one being imported already exists
                in the Dataset, then these labels will be appended to these
                of the already existing one, and if labels with identical
                key is imported before, the old label value will be
                overwritten. If two DataItems are identical in the same
                import data operation, the labels will be combined and if
                key collision happens in this case, one of the values will
                be picked randomly. Two DataItems are considered identical
                if their content bytes are identical (e.g. image bytes or
                pdf bytes). These labels will be overridden by Annotation
                labels specified inside index file refenced by
                [import_schema_uri][google.cloud.aiplatform.v1beta1.ImportDataConfig.import_schema_uri],
                e.g. jsonl file.
        Returns:
            dataset (Dataset):
                Instantiated representation of the managed dataset resource.
        """

        import_lro = self._import(
            source=gcs_source,
            import_schema_uri=import_schema_uri,
            data_items_labels=data_items_labels,
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
