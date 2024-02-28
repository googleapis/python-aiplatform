# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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

import ray.data
from ray.data.dataset import Dataset
from typing import Optional

from google.cloud.aiplatform.preview.vertex_ray.bigquery_datasource import (
    BigQueryDatasource,
)


def read_bigquery(
    project_id: Optional[str] = None,
    dataset: Optional[str] = None,
    query: Optional[str] = None,
    *,
    parallelism: int = -1,
) -> Dataset:
    return ray.data.read_datasource(
        BigQueryDatasource(),
        project_id=project_id,
        dataset=dataset,
        query=query,
        parallelism=parallelism,
    )


def write_bigquery(
    ds: Dataset,
    project_id: Optional[str] = None,
    dataset: Optional[str] = None,
    max_retry_cnt: int = 10,
) -> None:
    return ds.write_datasource(
        BigQueryDatasource(),
        project_id=project_id,
        dataset=dataset,
        max_retry_cnt=max_retry_cnt,
    )
