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

from typing import Optional, Sequence, Dict, Tuple, Union

from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import schema
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.datasets import (
    Dataset,
    TabularDatasource,
)


class TabularDataset(Dataset):
    """Managed tabular dataset resource for AI Platform"""

    _support_metadata_schema_uris = schema.dataset.metadata.tabular

    _support_import_schema_uris = None

    @classmethod
    def create(
        cls,
        display_name: str,
        gcs_source: Optional[Union[str, Sequence[str]]] = None,
        bq_source: Optional[str] = None,
        labels: Optional[Dict] = {},
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "TabularDataset":
        """Creates a new tabular dataset.

        Args:
            display_name: (str)
                Required. The user-defined name of the Dataset.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            gcs_source: Optional[Union[str, Sequence[str]]] = None:
                Google Cloud Storage URI(-s) to the
                input file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
            bq_source: Optional[str] = None:
                BigQuery URI to the input table.
            labels: Optional[Dict] = {}
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
            project: Optional[str] = None,
                Project to upload this model to. Overrides project set in
                aiplatform.init.
            location: Optional[str] = None,
                Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials: Optional[auth_credentials.Credentials] = None,
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
            request_metadata: Optional[Sequence[Tuple[str, str]]] = ()
                Strings which should be sent along with the request as metadata.
            sync: (bool) = True
                Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            tabular_dataset: TabularDataset
                Instantiated representation of the managed tabular dataset resource.

        """

        utils.validate_display_name(display_name)

        datasource = TabularDatasource(gcs_source, bq_source)

        return cls._create_encapsulated(
            display_name=display_name,
            metadata_schema_uri=schema.dataset.metadata.tabular,
            datasource=datasource,
            labels=labels,
            project=project,
            location=location,
            credentials=credentials,
            request_metadata=request_metadata,
            sync=sync,
        )

    def import_data(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} class does not support 'import_data'"
        )
