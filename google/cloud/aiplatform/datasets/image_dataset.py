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
from google.cloud.aiplatform.datasets import datasources
from google.cloud.aiplatform.datasets import Dataset

class ImageDataset(Dataset):
    """Managed image dataset resource for AI Platform"""

    _support_metadata_schema_uris = (schema.dataset.metadata.image,)

    @classmethod
    def create(
        cls,
        display_name: str,
        gcs_source: Optional[Union[str, Sequence[str]]] = None,
        labels: Optional[Dict] = None,
        import_schema_uri: Optional[str] = None,
        data_item_labels: Optional[Dict] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "ImageDataset":
        """Creates a new image dataset and optionally imports data into dataset when
        source and import_schema_uri are passed.

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
            labels: Optional[Dict] = None
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
            import_schema_uri: Optional[str] = None
                Points to a YAML file stored on Google Cloud
                Storage describing the import format. Validation will be
                done against the schema. The schema is defined as an
                `OpenAPI 3.0.2 Schema
                Object <https://tinyurl.com/y538mdwt>`__.
            data_item_labels: Optional[Dict] = None
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
            image_dataset: ImageDataset
                Instantiated representation of the managed image dataset resource.

        """

        utils.validate_display_name(display_name)

        datasource = datasources.NonTabularDatasource()

        return cls._create_encapsulated(
            display_name=display_name,
            metadata_schema_uri=schema.dataset.metadata.image,
            datasource=datasource,
            labels=labels,
            project=project,
            location=location,
            credentials=credentials,
            request_metadata=request_metadata,
            sync=sync,
        )
