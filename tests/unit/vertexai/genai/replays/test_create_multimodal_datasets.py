# Copyright 2025 Google LLC
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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring

import sys
from unittest import mock

from google.cloud import bigquery
from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import _datasets_utils
from vertexai._genai import types
import pandas as pd
import pytest


METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/multimodal_1.0.0.yaml"
)
BIGQUERY_TABLE_NAME = "vertex-sdk-dev.multimodal_dataset.test-table"


@pytest.fixture
def mock_bigquery_client(is_replay_mode):
    if is_replay_mode:
        with mock.patch.object(
            _datasets_utils, "_try_import_bigquery"
        ) as mock_try_import_bigquery:
            mock_dataset = mock.MagicMock()
            mock_dataset.location = "us-central1"

            mock_client = mock.MagicMock()
            mock_client.get_dataset.return_value = mock_dataset

            mock_try_import_bigquery.return_value.Client.return_value = mock_client
            mock_try_import_bigquery.return_value.TableReference = (
                bigquery.TableReference
            )

            yield mock_try_import_bigquery
    else:
        yield None


@pytest.fixture
def mock_import_bigframes(is_replay_mode):
    if is_replay_mode:
        with mock.patch.object(
            _datasets_utils, "_try_import_bigframes"
        ) as mock_import_bigframes:
            session = mock.MagicMock()
            session.read_pandas.return_value = mock.MagicMock()

            bigframes = mock.MagicMock()
            bigframes.connect.return_value = mock.MagicMock()

            mock_import_bigframes.return_value = bigframes

            yield mock_import_bigframes
    else:
        yield None


@pytest.fixture
def mock_generate_multimodal_dataset_display_name():
    with mock.patch.object(
        _datasets_utils, "generate_multimodal_dataset_display_name"
    ) as mock_generate:
        mock_generate.return_value = "test-generated-name"
        yield mock_generate


def test_create_dataset(client):
    create_dataset_operation = client.datasets._create_multimodal_dataset(
        name="projects/vertex-sdk-dev/locations/us-central1",
        display_name="test-display-name",
        metadata_schema_uri=METADATA_SCHEMA_URI,
        metadata={
            "inputConfig": {
                "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
            },
        },
    )
    assert isinstance(create_dataset_operation, types.MultimodalDatasetOperation)
    assert create_dataset_operation


def test_create_dataset_from_bigquery(client):
    dataset = client.datasets.create_from_bigquery(
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "description": "test-description-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        }
    )
    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigquery"
    assert dataset.metadata.input_config.bigquery_source.uri == (
        f"bq://{BIGQUERY_TABLE_NAME}"
    )


@pytest.mark.usefixtures("mock_generate_multimodal_dataset_display_name")
def test_create_dataset_from_bigquery_no_display_name(client):
    dataset = client.datasets.create_from_bigquery(
        multimodal_dataset={
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        }
    )
    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-generated-name"


@pytest.mark.usefixtures("mock_bigquery_client", "mock_import_bigframes")
def test_create_dataset_from_pandas(client, is_replay_mode):
    dataframe = pd.DataFrame(
        {
            "col1": ["col1"],
            "col2": ["col2"],
        }
    )

    dataset = client.datasets.create_from_pandas(
        dataframe=dataframe,
        target_table_id=BIGQUERY_TABLE_NAME,
        multimodal_dataset={
            "display_name": "test-from-pandas",
        },
    )

    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-pandas"
    assert dataset.metadata.input_config.bigquery_source.uri == (
        f"bq://{BIGQUERY_TABLE_NAME}"
    )
    if not is_replay_mode:
        bigquery_client = bigquery.Client(
            project=client._api_client.project,
            location=client._api_client.location,
            credentials=client._api_client._credentials,
        )
        rows = bigquery_client.list_rows(
            dataset.metadata.input_config.bigquery_source.uri[5:]
        )
        pd.testing.assert_frame_equal(rows.to_dataframe(), dataframe)


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="bigframes requires python 3.10 or higher"
)
@pytest.mark.usefixtures("mock_bigquery_client", "mock_import_bigframes")
def test_create_dataset_from_bigframes(client, is_replay_mode):
    import bigframes.pandas

    dataframe = pd.DataFrame(
        {
            "col1": ["col1"],
            "col2": ["col2"],
        }
    )
    if is_replay_mode:
        bf_dataframe = mock.MagicMock()
        bf_dataframe.to_gbq.return_value = "temp_table_id"
    else:
        bf_dataframe = bigframes.pandas.DataFrame(dataframe)

    dataset = client.datasets.create_from_bigframes(
        dataframe=bf_dataframe,
        target_table_id=BIGQUERY_TABLE_NAME,
        multimodal_dataset={
            "display_name": "test-from-bigframes",
        },
    )

    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigframes"
    assert dataset.metadata.input_config.bigquery_source.uri == (
        f"bq://{BIGQUERY_TABLE_NAME}"
    )
    if not is_replay_mode:
        bigquery_client = bigquery.Client(
            project=client._api_client.project,
            location=client._api_client.location,
            credentials=client._api_client._credentials,
        )
        rows = bigquery_client.list_rows(
            dataset.metadata.input_config.bigquery_source.uri[5:]
        )
        pd.testing.assert_frame_equal(
            rows.to_dataframe(), dataframe, check_index_type=False
        )


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="bigframes requires python 3.10 or higher",
)
@pytest.mark.usefixtures("mock_bigquery_client", "mock_import_bigframes")
def test_create_dataset_from_bigframes_preserves_other_metadata(client, is_replay_mode):
    import bigframes.pandas

    dataframe = pd.DataFrame(
        {
            "col1": ["col1"],
            "col2": ["col2"],
        }
    )
    if is_replay_mode:
        bf_dataframe = mock.MagicMock()
        bf_dataframe.to_gbq.return_value = "temp_table_id"
    else:
        bf_dataframe = bigframes.pandas.DataFrame(dataframe)

    dataset = client.datasets.create_from_bigframes(
        dataframe=bf_dataframe,
        target_table_id=BIGQUERY_TABLE_NAME,
        multimodal_dataset={
            "display_name": "test-from-bigframes",
            "metadata": {
                "gemini_request_read_config": {
                    "assembled_request_column_name": "test_column"
                }
            },
        },
    )

    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigframes"
    assert (
        dataset.metadata.gemini_request_read_config.assembled_request_column_name
        == "test_column"
    )
    assert dataset.metadata.input_config.bigquery_source.uri == (
        f"bq://{BIGQUERY_TABLE_NAME}"
    )


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_create_dataset_async(client):
    create_dataset_operation = await client.aio.datasets._create_multimodal_dataset(
        name="projects/vertex-sdk-dev/locations/us-central1",
        display_name="test-display-name",
        metadata_schema_uri=METADATA_SCHEMA_URI,
        metadata={
            "inputConfig": {
                "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
            },
        },
    )
    assert isinstance(create_dataset_operation, types.MultimodalDatasetOperation)
    assert create_dataset_operation


@pytest.mark.asyncio
async def test_create_dataset_from_bigquery_async(client):
    dataset = await client.aio.datasets.create_from_bigquery(
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "description": "test-description-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        }
    )
    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigquery"
    assert dataset.metadata.input_config.bigquery_source.uri == (
        f"bq://{BIGQUERY_TABLE_NAME}"
    )


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_generate_multimodal_dataset_display_name")
async def test_create_dataset_from_bigquery_no_display_name_async(client):
    dataset = await client.aio.datasets.create_from_bigquery(
        multimodal_dataset={
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        }
    )
    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-generated-name"


@pytest.mark.asyncio
async def test_create_dataset_from_bigquery_async_with_timeout(client):
    dataset = await client.aio.datasets.create_from_bigquery(
        config=types.CreateMultimodalDatasetConfig(timeout=120),
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "description": "test-description-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        },
    )
    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigquery"
    assert dataset.metadata.input_config.bigquery_source.uri == (
        f"bq://{BIGQUERY_TABLE_NAME}"
    )


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_bigquery_client", "mock_import_bigframes")
async def test_create_dataset_from_pandas_async(client, is_replay_mode):
    dataframe = pd.DataFrame(
        {
            "col1": ["col1row1", "col1row2"],
            "col2": ["col2row1", "col2row2"],
        }
    )

    dataset = await client.aio.datasets.create_from_pandas(
        dataframe=dataframe,
        target_table_id=BIGQUERY_TABLE_NAME,
        multimodal_dataset={
            "display_name": "test-from-pandas",
        },
    )

    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-pandas"
    assert dataset.metadata.input_config.bigquery_source.uri == (
        f"bq://{BIGQUERY_TABLE_NAME}"
    )
    if not is_replay_mode:
        bigquery_client = bigquery.Client(
            project=client._api_client.project,
            location=client._api_client.location,
            credentials=client._api_client._credentials,
        )
        rows = bigquery_client.list_rows(
            dataset.metadata.input_config.bigquery_source.uri[5:]
        )
        pd.testing.assert_frame_equal(rows.to_dataframe(), dataframe)


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="bigframes requires python 3.10 or higher"
)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_bigquery_client", "mock_import_bigframes")
async def test_create_dataset_from_bigframes_async(client, is_replay_mode):
    import bigframes.pandas

    dataframe = pd.DataFrame(
        {
            "col1": ["col1"],
            "col2": ["col2"],
        }
    )
    if is_replay_mode:
        bf_dataframe = mock.MagicMock()
        bf_dataframe.to_gbq.return_value = "temp_table_id"
    else:
        bf_dataframe = bigframes.pandas.DataFrame(dataframe)

    dataset = await client.aio.datasets.create_from_bigframes(
        dataframe=bf_dataframe,
        target_table_id=BIGQUERY_TABLE_NAME,
        multimodal_dataset={
            "display_name": "test-from-bigframes",
        },
    )

    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigframes"
    assert dataset.metadata.input_config.bigquery_source.uri == (
        f"bq://{BIGQUERY_TABLE_NAME}"
    )
    if not is_replay_mode:
        bigquery_client = bigquery.Client(
            project=client._api_client.project,
            location=client._api_client.location,
            credentials=client._api_client._credentials,
        )
        rows = bigquery_client.list_rows(
            dataset.metadata.input_config.bigquery_source.uri[5:]
        )
        pd.testing.assert_frame_equal(
            rows.to_dataframe(), dataframe, check_index_type=False
        )


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="bigframes requires python 3.10 or higher",
)
@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_bigquery_client", "mock_import_bigframes")
async def test_create_dataset_from_bigframes_preserves_other_metadata_async(
    client, is_replay_mode
):
    import bigframes.pandas

    dataframe = pd.DataFrame(
        {
            "col1": ["col1"],
            "col2": ["col2"],
        }
    )
    if is_replay_mode:
        bf_dataframe = mock.MagicMock()
        bf_dataframe.to_gbq.return_value = "temp_table_id"
    else:
        bf_dataframe = bigframes.pandas.DataFrame(dataframe)

    dataset = await client.aio.datasets.create_from_bigframes(
        dataframe=bf_dataframe,
        target_table_id=BIGQUERY_TABLE_NAME,
        multimodal_dataset={
            "display_name": "test-from-bigframes",
            "metadata": {
                "gemini_request_read_config": {
                    "assembled_request_column_name": "test_column"
                }
            },
        },
    )

    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigframes"
    assert (
        dataset.metadata.gemini_request_read_config.assembled_request_column_name
        == "test_column"
    )
    assert dataset.metadata.input_config.bigquery_source.uri == (
        f"bq://{BIGQUERY_TABLE_NAME}"
    )
