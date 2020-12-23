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

from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import Dataset, schema
from google.cloud.aiplatform.data_source import NonTabularDatasource

from typing import Optional, Sequence, Dict, Tuple


class ImageDataset(Dataset):
    @classmethod
    def create(
        cls,
        display_name: str,
        gcs_source_uris: Sequence[str],
        import_schema_uri: str,
        data_items_labels: Optional[Dict] = None,
        metadata: Sequence[Tuple[str, str]] = (),
        labels: Optional[Dict] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        sync=True,
    ) -> "Dataset":

        # Validate import_schema_uri
        if not import_schema_uri in [
            schema.dataset.import_metadata.image.multi_label_classification,
            schema.dataset.import_metadata.image.single_label_classification,
            schema.dataset.import_metadata.image.bounding_box,
            schema.dataset.import_metadata.image.image_segmentation,
        ]:
            raise ValueError("Invalid import_schema_uri provided")

        cls.create(
            cls,
            display_name=display_name,
            metadata_schema_uri=schema.dataset.metadata.image,
            datasource=NonTabularDatasource(
                gcs_source_uris=gcs_source_uris,
                import_schema_uri=import_schema_uri,
                data_items_labels=data_items_labels,
            ),
            metadata=metadata,
            labels=labels,
            project=project,
            location=location,
            credentials=credentials,
            sync=sync,
        )
