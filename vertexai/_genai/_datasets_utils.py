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
"""Utility functions for multimodal dataset."""

from typing import Any, Type, TypeVar
import uuid

import google.auth.credentials
from vertexai._genai.types import common
from pydantic import BaseModel

METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/multimodal_1.0.0.yaml"
)
_BQ_MULTIREGIONS = {"us", "eu"}
_DEFAULT_BQ_DATASET_PREFIX = "vertex_datasets"
_DEFAULT_BQ_TABLE_PREFIX = "multimodal_dataset"

T = TypeVar("T", bound=BaseModel)


def create_from_response(model_type: Type[T], response: dict[str, Any]) -> T:
    """Creates a model from a response."""
    model_field_names = model_type.model_fields.keys()
    filtered_response = {}
    for key, value in response.items():
        snake_key = common.camel_to_snake(key)
        if snake_key in model_field_names:
            filtered_response[snake_key] = value
    return model_type(**filtered_response)


def multimodal_dataset_get_bigquery_uri(
    multimodal_dataset: common.MultimodalDataset,
) -> str:
    """Gets the bigquery uri from a multimodal dataset or raises ValueError."""
    if (
        not hasattr(multimodal_dataset, "metadata")
        or multimodal_dataset.metadata is None
    ):
        raise ValueError("Multimodal dataset metadata is required.")
    if (
        not hasattr(multimodal_dataset.metadata, "input_config")
        or multimodal_dataset.metadata.input_config is None
    ):
        raise ValueError("Multimodal dataset input config is required.")
    if (
        not hasattr(multimodal_dataset.metadata.input_config, "bigquery_source")
        or multimodal_dataset.metadata.input_config.bigquery_source is None
    ):
        raise ValueError("Multimodal dataset input config bigquery source is required.")
    if (
        not hasattr(multimodal_dataset.metadata.input_config.bigquery_source, "uri")
        or multimodal_dataset.metadata.input_config.bigquery_source.uri is None
    ):
        raise ValueError(
            "Multimodal dataset input config bigquery source uri is required."
        )
    return str(multimodal_dataset.metadata.input_config.bigquery_source.uri)


def multimodal_dataset_set_bigquery_uri(
    multimodal_dataset: common.MultimodalDataset,
    bigquery_uri: str,
) -> None:
    """Sets the bigquery uri from a multimodal dataset or raises ValueError."""
    metadata = (
        common.SchemaTablesDatasetMetadata()
        if multimodal_dataset.metadata is None
        else multimodal_dataset.metadata
    )
    input_config = (
        common.SchemaTablesDatasetMetadataInputConfig()
        if metadata.input_config is None
        else metadata.input_config
    )
    bigquery_source = (
        common.SchemaTablesDatasetMetadataBigQuerySource()
        if input_config.bigquery_source is None
        else input_config.bigquery_source
    )
    bigquery_source.uri = bigquery_uri
    input_config.bigquery_source = bigquery_source
    metadata.input_config = input_config
    multimodal_dataset.metadata = metadata


def _try_import_bigframes() -> Any:
    """Tries to import `bigframes`."""
    try:
        import bigframes
        import bigframes.pandas
        import bigframes.bigquery

        return bigframes
    except ImportError as exc:
        raise ImportError(
            "`bigframes` is not installed. Please call 'pip install bigframes'."
        ) from exc


def _try_import_bigquery() -> Any:
    """Tries to import `bigquery`."""
    try:
        from google.cloud import bigquery

        return bigquery
    except ImportError as exc:
        raise ImportError(
            "`bigquery` is not installed. Please call 'pip install"
            " google-cloud-bigquery'."
        ) from exc


def _bq_dataset_location_allowed(
    vertex_location: str, bq_dataset_location: str
) -> bool:
    if bq_dataset_location == vertex_location:
        return True
    if bq_dataset_location in _BQ_MULTIREGIONS:
        return vertex_location.startswith(bq_dataset_location)
    return False


def _normalize_and_validate_table_id(
    *,
    table_id: str,
    project: str,
    location: str,
    credentials: google.auth.credentials.Credentials,
) -> str:
    bigquery = _try_import_bigquery()

    table_ref = bigquery.TableReference.from_string(table_id, default_project=project)
    if table_ref.project != project:
        raise ValueError(
            "The BigQuery table "
            f"`{table_ref.project}.{table_ref.dataset_id}.{table_ref.table_id}`"
            " must be in the same project as the multimodal dataset."
            f" The multimodal dataset is in `{project}`, but the BigQuery table"
            f" is in `{table_ref.project}`."
        )

    dataset_ref = bigquery.DatasetReference(
        project=table_ref.project, dataset_id=table_ref.dataset_id
    )
    client = bigquery.Client(project=project, credentials=credentials)
    bq_dataset = client.get_dataset(dataset_ref=dataset_ref)
    if not _bq_dataset_location_allowed(location, bq_dataset.location):
        raise ValueError(
            "The BigQuery dataset"
            f" `{dataset_ref.project}.{dataset_ref.dataset_id}` must be in the"
            " same location as the multimodal dataset. The multimodal dataset"
            f" is in `{location}`, but the BigQuery dataset is in"
            f" `{bq_dataset.location}`."
        )
    return f"{table_ref.project}.{table_ref.dataset_id}.{table_ref.table_id}"


def _create_default_bigquery_dataset_if_not_exists(
    *,
    project: str,
    location: str,
    credentials: google.auth.credentials.Credentials,
) -> str:
    # Loading bigquery lazily to avoid auto-loading it when importing vertexai
    from google.cloud import bigquery  # pylint: disable=g-import-not-at-top

    bigquery_client = bigquery.Client(project=project, credentials=credentials)
    location_str = location.lower().replace("-", "_")
    dataset_id = bigquery.DatasetReference(
        project, f"{_DEFAULT_BQ_DATASET_PREFIX}_{location_str}"
    )
    dataset = bigquery.Dataset(dataset_ref=dataset_id)
    dataset.location = location
    bigquery_client.create_dataset(dataset, exists_ok=True)
    return f"{dataset_id.project}.{dataset_id.dataset_id}"


def _generate_target_table_id(dataset_id: str) -> str:
    return f"{dataset_id}.{_DEFAULT_BQ_TABLE_PREFIX}_{str(uuid.uuid4())}"
