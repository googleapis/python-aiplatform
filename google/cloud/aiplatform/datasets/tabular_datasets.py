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


from typing import Optional, Sequence, Dict

from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import schema
from google.cloud.aiplatform.datasets import datasets


class TabularDataset(datasets._Dataset):
    """Managed tabular dataset resource for AI Platform"""

    _types = [
        schema.dataset.metadata.tabular,
    ]

    def __init__(
        self,
        dataset_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing managed tabular dataset given a dataset name or ID.

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

        Raises:
            Exception if the retrieved dataset type is not supported by
            'TabularDataset' class.
        """

        super().__init__(
            dataset_name=dataset_name,
            project=project,
            location=location,
            credentials=credentials,
        )

        if self.metadata_schema_uri not in self._types:
            raise Exception(
                f"{self.resource_name} can not be retrieved using "
                f"'TabularDataset' class, check the dataset type"
            )

    @staticmethod
    def set_dataset_metadata(gcs_source: str, bq_source: str) -> Dict:

        dataset_metadata = dict()

        if gcs_source and bq_source:
            raise Exception(
                "'gcs_source' and 'bq_source' should not be set the same time."
            )

        if not gcs_source and not bq_source:
            raise Exception("Either 'gcs_source' or 'bq_source' should be set.")

        if gcs_source:
            dataset_metadata = {"input_config": {"gcs_source": {"uri": gcs_source}}}
        elif bq_source:
            dataset_metadata = {"input_config": {"bigquery_source": {"uri": bq_source}}}
        return dataset_metadata

    @classmethod
    def create(
        cls,
        display_name: str,
        gcs_source: Optional[Sequence[str]] = None,
        bq_source: Optional[str] = None,
        labels: Optional[Dict] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "TabularDataset":
        """Creates a new tabular dataset.

        Args:
            display_name (str):
                Required. The user-defined name of the Dataset.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            gcs_source: Optional[Sequence[str]]=None:
                Google Cloud Storage URI(-s) to the
                input file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
            bq_source: Optional[str]=None:
                BigQuery URI to the input table.
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
            tabular_dataset (TabularDataset):
                Instantiated representation of the managed tabular dataset resource.
        """

        metadata_schema_uri = schema.dataset.metadata.tabular
        dataset_metadata = cls.set_dataset_metadata(gcs_source, bq_source)

        dataset_obj = super().create(
            display_name=display_name,
            metadata_schema_uri=metadata_schema_uri,
            dataset_metadata=dataset_metadata,
            labels=labels,
            project=project,
            location=location,
            credentials=credentials,
        )

        return dataset_obj
