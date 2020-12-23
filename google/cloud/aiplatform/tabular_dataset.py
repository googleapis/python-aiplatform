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
from google.cloud.aiplatform.data_source import TabularDatasource

from typing import Optional, Sequence, Dict, Tuple


class TabularDataset(Dataset):
    @classmethod
    def create(
        cls,
        display_name: str,
        gcs_source_uri: Optional[str],
        bq_source_uri: Optional[str],
        metadata: Sequence[Tuple[str, str]] = (),
        labels: Optional[Dict] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        sync=True,
    ) -> "Dataset":
        cls.create(
            cls,
            display_name=display_name,
            metadata_schema_uri=schema.dataset.metadata.tabular,
            datasource=TabularDatasource(
                gcs_source_uri=gcs_source_uri, bq_source_uri=bq_source_uri
            ),
            metadata=metadata,
            labels=labels,
            project=project,
            location=location,
            credentials=credentials,
            sync=sync,
        )
