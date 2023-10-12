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

import logging
import os
import tempfile
import time
from typing import Any, Dict, List, Optional
import uuid
import pyarrow.parquet as pq

from google.api_core import client_info
from google.api_core import exceptions
from google.api_core.gapic_v1 import client_info as v1_client_info
from google.cloud import bigquery
from google.cloud import bigquery_storage
from google.cloud.aiplatform import initializer

from ray.data._internal.execution.interfaces import TaskContext
from ray.data.block import Block
from ray.data.block import BlockAccessor
from ray.data.block import BlockMetadata
from ray.data.datasource.datasource import Datasource
from ray.data.datasource.datasource import Reader
from ray.data.datasource.datasource import ReadTask
from ray.data.datasource.datasource import WriteResult
from ray.types import ObjectRef


_BQ_GAPIC_VERSION = bigquery.__version__ + "+vertex_ray"
_BQS_GAPIC_VERSION = bigquery_storage.__version__ + "+vertex_ray"
bq_info = client_info.ClientInfo(
    gapic_version=_BQ_GAPIC_VERSION, user_agent=f"ray-on-vertex/{_BQ_GAPIC_VERSION}"
)
bqstorage_info = v1_client_info.ClientInfo(
    gapic_version=_BQS_GAPIC_VERSION, user_agent=f"ray-on-vertex/{_BQS_GAPIC_VERSION}"
)

MAX_RETRY_CNT = 10
RATE_LIMIT_EXCEEDED_SLEEP_TIME = 11


class _BigQueryDatasourceReader(Reader):
    def __init__(
        self,
        project_id: Optional[str] = None,
        dataset: Optional[str] = None,
        query: Optional[str] = None,
        parallelism: Optional[int] = -1,
        **kwargs: Optional[Dict[str, Any]],
    ):
        self._project_id = project_id or initializer.global_config.project
        self._dataset = dataset
        self._query = query
        self._kwargs = kwargs

        if query is not None and dataset is not None:
            raise ValueError(
                "[Ray on Vertex AI]: Query and dataset kwargs cannot both "
                + "be provided (must be mutually exclusive)."
            )

    def get_read_tasks(self, parallelism: int) -> List[ReadTask]:
        def _read_single_partition(stream) -> Block:
            client = bigquery_storage.BigQueryReadClient()
            reader = client.read_rows(stream.name)
            return reader.to_arrow()

        if self._query:
            job_config = bigquery.QueryJobConfig(create_session=True)

            # Make sure the session is a new one, not one associated with another query.
            job_config.use_query_cache = False

            query_client = bigquery.Client(
                project=self._project_id, client_info=bq_info
            )
            query_job = query_client.query(self._query, job_config=job_config)
            query_job.result()
            destination = str(query_job.destination)
            dataset_id = destination.split(".")[-2]
            table_id = destination.split(".")[-1]
        else:
            self._validate_dataset_table_exist(self._project_id, self._dataset)
            dataset_id = self._dataset.split(".")[0]
            table_id = self._dataset.split(".")[1]

        bqs_client = bigquery_storage.BigQueryReadClient(client_info=bqstorage_info)
        table = f"projects/{self._project_id}/datasets/{dataset_id}/tables/{table_id}"

        if parallelism == -1:
            parallelism = None
        requested_session = bigquery_storage.types.ReadSession(
            table=table,
            data_format=bigquery_storage.types.DataFormat.ARROW,
        )
        read_session = bqs_client.create_read_session(
            parent=f"projects/{self._project_id}",
            read_session=requested_session,
            max_stream_count=parallelism,
        )

        read_tasks = []
        logging.info(f"Created streams: {len(read_session.streams)}")
        if len(read_session.streams) < parallelism:
            logging.info(
                "[Ray on Vertex AI]: The number of streams created by the "
                + "BigQuery Storage Read API is less than the requested "
                + "parallelism due to the size of the dataset."
            )

        for stream in read_session.streams:
            # Create a metadata block object to store schema, etc.
            metadata = BlockMetadata(
                num_rows=None,
                size_bytes=None,
                schema=None,
                input_files=None,
                exec_stats=None,
            )

            # Create the read task and pass the no-arg wrapper and metadata in
            read_task = ReadTask(
                lambda stream=stream: [_read_single_partition(stream)],
                metadata,
            )
            read_tasks.append(read_task)

        return read_tasks

    def estimate_inmemory_data_size(self) -> Optional[int]:
        # TODO(b/281891467): Implement this method
        return None

    def _validate_dataset_table_exist(self, project_id: str, dataset: str) -> None:
        client = bigquery.Client(project=project_id, client_info=bq_info)
        dataset_id = dataset.split(".")[0]
        try:
            client.get_dataset(dataset_id)
        except exceptions.NotFound:
            raise ValueError(
                "[Ray on Vertex AI]: Dataset {} is not found. Please ensure that it exists.".format(
                    dataset_id
                )
            )

        try:
            client.get_table(dataset)
        except exceptions.NotFound:
            raise ValueError(
                "[Ray on Vertex AI]: Table {} is not found. Please ensure that it exists.".format(
                    dataset
                )
            )


class BigQueryDatasource(Datasource):
    def create_reader(self, **kwargs) -> Reader:
        return _BigQueryDatasourceReader(**kwargs)

    def write(
        self,
        blocks: List[ObjectRef[Block]],
        ctx: TaskContext,
        project_id: Optional[str] = None,
        dataset: Optional[str] = None,
    ) -> WriteResult:
        def _write_single_block(block: Block, project_id: str, dataset: str):
            block = BlockAccessor.for_block(block).to_arrow()

            client = bigquery.Client(project=project_id, client_info=bq_info)
            job_config = bigquery.LoadJobConfig(autodetect=True)
            job_config.source_format = bigquery.SourceFormat.PARQUET
            job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

            with tempfile.TemporaryDirectory() as temp_dir:
                fp = os.path.join(temp_dir, f"block_{uuid.uuid4()}.parquet")
                pq.write_table(block, fp, compression="SNAPPY")

                retry_cnt = 0
                while retry_cnt < MAX_RETRY_CNT:
                    with open(fp, "rb") as source_file:
                        job = client.load_table_from_file(
                            source_file, dataset, job_config=job_config
                        )
                    retry_cnt += 1
                    try:
                        logging.info(job.result())
                        break
                    except exceptions.Forbidden as e:
                        logging.info(
                            "[Ray on Vertex AI]: Rate limit exceeded... Sleeping to try again"
                        )
                        logging.debug(e)
                        time.sleep(RATE_LIMIT_EXCEEDED_SLEEP_TIME)

        project_id = project_id or initializer.global_config.project

        if dataset is None:
            raise ValueError(
                "[Ray on Vertex AI]: Dataset is required when writing to BigQuery."
            )

        # Set up datasets to write
        client = bigquery.Client(project=project_id, client_info=bq_info)
        dataset_id = dataset.split(".", 1)[0]
        try:
            client.create_dataset(f"{project_id}.{dataset_id}", timeout=30)
            logging.info(f"[Ray on Vertex AI]: Created dataset {dataset_id}.")
        except exceptions.Conflict:
            logging.info(
                f"[Ray on Vertex AI]: Dataset {dataset_id} already exists. "
                + "The table will be overwritten if it already exists."
            )

        # Delete table if it already exists
        client.delete_table(f"{project_id}.{dataset}", not_found_ok=True)

        for block in blocks:
            _write_single_block(block, project_id, dataset)
        return "ok"
