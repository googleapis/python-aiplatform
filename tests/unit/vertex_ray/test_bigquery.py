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

import importlib

from google.api_core import exceptions
from google.api_core import operation
from google.cloud import bigquery
from google.cloud import bigquery_storage
from google.cloud import aiplatform
from google.cloud.aiplatform.vertex_ray import bigquery_datasource
from google.cloud.aiplatform.vertex_ray.bigquery_datasink import (
    _BigQueryDatasink,
)
import test_constants as tc
from google.cloud.bigquery import job
from google.cloud.bigquery_storage_v1.types import stream as gcbqs_stream
import mock
import pytest
import pyarrow as pa
import ray


_TEST_BQ_DATASET_ID = "mockdataset"
_TEST_BQ_TABLE_ID = "mocktable"
_TEST_BQ_DATASET = _TEST_BQ_DATASET_ID + "." + _TEST_BQ_TABLE_ID
_TEST_BQ_TEMP_DESTINATION = (
    tc.ProjectConstants.TEST_GCP_PROJECT_ID + ".tempdataset.temptable"
)
_TEST_DISPLAY_NAME = "display_name"


@pytest.fixture(autouse=True)
def bq_client_full_mock(monkeypatch):
    client_mock = mock.create_autospec(bigquery.Client)
    client_mock.return_value = client_mock

    def bq_get_dataset_mock(dataset_id):
        if dataset_id != _TEST_BQ_DATASET_ID:
            raise exceptions.NotFound(
                "[Ray on Vertex AI]: Dataset {} is not found. Please ensure that it exists.".format(
                    _TEST_BQ_DATASET
                )
            )

    def bq_get_table_mock(table_id):
        if table_id != _TEST_BQ_DATASET:
            raise exceptions.NotFound(
                "[Ray on Vertex AI]: Table {} is not found. Please ensure that it exists.".format(
                    _TEST_BQ_DATASET
                )
            )

    def bq_create_dataset_mock(dataset_id, **kwargs):
        if dataset_id == "existingdataset":
            raise exceptions.Conflict("Dataset already exists")
        return mock.Mock(operation.Operation)

    def bq_delete_table_mock(table, **kwargs):
        return None

    def bq_query_mock(query):
        fake_job_ref = job._JobReference(
            "fake_job_id",
            tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            "us-central1",
        )
        fake_query_job = job.QueryJob(fake_job_ref, query, None)
        try:
            fake_query_job.configuration.destination = _TEST_BQ_TEMP_DESTINATION
        except AttributeError:
            fake_query_job._configuration.destination = _TEST_BQ_TEMP_DESTINATION
        return fake_query_job

    client_mock.get_dataset = bq_get_dataset_mock
    client_mock.get_table = bq_get_table_mock
    client_mock.create_dataset = bq_create_dataset_mock
    client_mock.delete_table = bq_delete_table_mock
    client_mock.query = bq_query_mock

    monkeypatch.setattr(bigquery, "Client", client_mock)
    client_mock.reset_mock()
    return client_mock


@pytest.fixture(autouse=True)
def bqs_client_full_mock(monkeypatch):
    client_mock = mock.create_autospec(bigquery_storage.BigQueryReadClient)
    client_mock.return_value = client_mock

    def bqs_create_read_session(max_stream_count=0, **kwargs):
        read_session_proto = gcbqs_stream.ReadSession()
        read_session_proto.streams = [
            gcbqs_stream.ReadStream() for _ in range(max_stream_count)
        ]
        return read_session_proto

    client_mock.create_read_session = bqs_create_read_session

    monkeypatch.setattr(bigquery_storage, "BigQueryReadClient", client_mock)
    client_mock.reset_mock()
    return client_mock


@pytest.fixture
def bq_query_result_mock():
    with mock.patch.object(bigquery.job.QueryJob, "result") as query_result_mock:
        yield query_result_mock


@pytest.fixture
def bq_query_result_mock_fail():
    with mock.patch.object(bigquery.job.QueryJob, "result") as query_result_mock_fail:
        query_result_mock_fail.side_effect = exceptions.BadRequest("400 Syntax error")
        yield query_result_mock_fail


@pytest.fixture
def ray_remote_function_mock():
    with mock.patch.object(ray.remote_function.RemoteFunction, "_remote") as remote_fn:
        remote_fn.return_value = 1
        yield remote_fn


@pytest.fixture
def ray_get_mock():
    with mock.patch.object(ray, "get") as ray_get:
        ray_get.return_value = None
        yield ray_get


class TestReadBigQuery:
    """Tests for BigQuery Read."""

    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "parallelism",
        [1, 2, 3, 4, 10, 100],
    )
    def test_create_reader(self, parallelism):
        bq_ds = bigquery_datasource.BigQueryDatasource()
        reader = bq_ds.create_reader(
            project_id=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            dataset=_TEST_BQ_DATASET,
            parallelism=parallelism,
        )
        read_tasks_list = reader.get_read_tasks(parallelism)
        assert len(read_tasks_list) == parallelism

    @pytest.mark.parametrize(
        "parallelism",
        [1, 2, 3, 4, 10, 100],
    )
    def test_create_reader_initialized(self, parallelism):
        """If initialized, create_reader doesn't need to specify project_id."""
        aiplatform.init(
            project=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            staging_bucket=tc.ProjectConstants.TEST_ARTIFACT_URI,
        )
        bq_ds = bigquery_datasource.BigQueryDatasource()
        reader = bq_ds.create_reader(
            dataset=_TEST_BQ_DATASET,
            parallelism=parallelism,
        )
        read_tasks_list = reader.get_read_tasks(parallelism)
        assert len(read_tasks_list) == parallelism

    @pytest.mark.parametrize(
        "parallelism",
        [1, 2, 3, 4, 10, 100],
    )
    def test_create_reader_query(self, parallelism, bq_query_result_mock):
        bq_ds = bigquery_datasource.BigQueryDatasource()
        reader = bq_ds.create_reader(
            project_id=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            parallelism=parallelism,
            query="SELECT * FROM mockdataset.mocktable",
        )
        read_tasks_list = reader.get_read_tasks(parallelism)
        bq_query_result_mock.assert_called_once()
        assert len(read_tasks_list) == parallelism

    @pytest.mark.parametrize(
        "parallelism",
        [1, 2, 3, 4, 10, 100],
    )
    def test_create_reader_query_bad_request(
        self,
        parallelism,
        bq_query_result_mock_fail,
    ):
        bq_ds = bigquery_datasource.BigQueryDatasource()
        reader = bq_ds.create_reader(
            project_id=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            parallelism=parallelism,
            query="SELECT * FROM mockdataset.mocktable",
        )
        with pytest.raises(exceptions.BadRequest):
            reader.get_read_tasks(parallelism)
        bq_query_result_mock_fail.assert_called()

    def test_dataset_query_kwargs_provided(self):
        parallelism = 4
        bq_ds = bigquery_datasource.BigQueryDatasource()
        with pytest.raises(ValueError) as exception:
            bq_ds.create_reader(
                project_id=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
                dataset=_TEST_BQ_DATASET,
                query="SELECT * FROM mockdataset.mocktable",
                parallelism=parallelism,
            )
        expected_message = "[Ray on Vertex AI]: Query and dataset kwargs cannot both be provided (must be mutually exclusive)."
        assert str(exception.value) == expected_message

    def test_create_reader_dataset_not_found(self):
        parallelism = 4
        bq_ds = bigquery_datasource.BigQueryDatasource()
        reader = bq_ds.create_reader(
            project_id=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            dataset="nonexistentdataset.mocktable",
            parallelism=parallelism,
        )
        with pytest.raises(ValueError) as exception:
            reader.get_read_tasks(parallelism)
        expected_message = "[Ray on Vertex AI]: Dataset nonexistentdataset is not found. Please ensure that it exists."
        assert str(exception.value) == expected_message

    def test_create_reader_table_not_found(self):
        parallelism = 4
        bq_ds = bigquery_datasource.BigQueryDatasource()
        reader = bq_ds.create_reader(
            project_id=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            dataset="mockdataset.nonexistenttable",
            parallelism=parallelism,
        )
        with pytest.raises(ValueError) as exception:
            reader.get_read_tasks(parallelism)
        expected_message = "[Ray on Vertex AI]: Table mockdataset.nonexistenttable is not found. Please ensure that it exists."
        assert str(exception.value) == expected_message


@pytest.mark.usefixtures("google_auth_mock")
class TestWriteBigQuery:
    """Tests for BigQuery Write."""

    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    # Ray 2.4.0 only
    def test_do_write(self, ray_remote_function_mock):
        bq_ds = bigquery_datasource.BigQueryDatasource()
        write_tasks_list = bq_ds.do_write(
            blocks=[1, 2, 3, 4],
            metadata=[1, 2, 3, 4],
            ray_remote_args={},
            project_id=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            dataset=_TEST_BQ_DATASET,
        )
        assert len(write_tasks_list) == 4

    # Ray 2.4.0 only
    def test_do_write_initialized(self, ray_remote_function_mock):
        """If initialized, do_write doesn't need to specify project_id."""
        aiplatform.init(
            project=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            staging_bucket=tc.ProjectConstants.TEST_ARTIFACT_URI,
        )
        bq_ds = bigquery_datasource.BigQueryDatasource()
        write_tasks_list = bq_ds.do_write(
            blocks=[1, 2, 3, 4],
            metadata=[1, 2, 3, 4],
            ray_remote_args={},
            dataset=_TEST_BQ_DATASET,
        )
        assert len(write_tasks_list) == 4

    # Ray 2.4.0 only
    def test_do_write_dataset_exists(self, ray_remote_function_mock):
        bq_ds = bigquery_datasource.BigQueryDatasource()
        write_tasks_list = bq_ds.do_write(
            blocks=[1, 2, 3, 4],
            metadata=[1, 2, 3, 4],
            ray_remote_args={},
            project_id=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            dataset="existingdataset" + "." + _TEST_BQ_TABLE_ID,
        )
        assert len(write_tasks_list) == 4

    # Ray 2.9.3 only
    def test_write(self, ray_get_mock, ray_remote_function_mock):
        if _BigQueryDatasink is None:
            return
        bq_datasink = _BigQueryDatasink(
            project_id=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            dataset=_TEST_BQ_DATASET,
        )
        arr = pa.array([2, 4, 5, 100])
        block = pa.Table.from_arrays([arr], names=["data"])
        status = bq_datasink.write(
            blocks=[block],
            ctx=None,
        )
        assert status == "ok"

    # Ray 2.9.3 only
    def test_write_dataset_exists(self, ray_get_mock, ray_remote_function_mock):
        if _BigQueryDatasink is None:
            return
        bq_datasink = _BigQueryDatasink(
            project_id=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            dataset="existingdataset" + "." + _TEST_BQ_TABLE_ID,
        )
        arr = pa.array([2, 4, 5, 100])
        block = pa.Table.from_arrays([arr], names=["data"])
        status = bq_datasink.write(
            blocks=[block],
            ctx=None,
        )
        assert status == "ok"
