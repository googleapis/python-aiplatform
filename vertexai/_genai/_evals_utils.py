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
"""Utility functions for evals."""

import io
import json
import logging
import os
import re
import time
from typing import Any, Optional, Union

from google.cloud import bigquery
from google.cloud import storage
from google.genai._api_client import BaseApiClient
from google.genai._common import get_value_by_path as getv
from google.genai._common import set_value_by_path as setv
import pandas as pd
import yaml

from . import types


logger = logging.getLogger(__name__)


GCS_PREFIX = "gs://"
BQ_PREFIX = "bq://"


class GcsUtils:
    """Handles File I/O operations with Google Cloud Storage (GCS)"""

    def __init__(self, api_client: BaseApiClient):
        self.api_client = api_client
        self.storage_client = storage.Client(  # type: ignore[attr-defined]
            project=self.api_client.project,
            credentials=self.api_client._credentials,
        )

    def parse_gcs_path(self, gcs_path: str) -> tuple[str, str]:
        """Helper to parse gs://bucket/path into (bucket_name, blob_path)."""
        if not gcs_path.startswith(GCS_PREFIX):
            raise ValueError(
                f"Invalid GCS path: '{gcs_path}'. It must start with '{GCS_PREFIX}'."
            )
        path_without_prefix = gcs_path[len(GCS_PREFIX) :]
        if "/" not in path_without_prefix:
            return path_without_prefix, ""
        bucket_name, blob_path = path_without_prefix.split("/", 1)
        return bucket_name, blob_path

    def upload_file_to_gcs(self, upload_gcs_path: str, filename: str) -> None:
        """Uploads the provided file to a Google Cloud Storage location."""

        storage.Blob.from_string(  # type: ignore[attr-defined]
            uri=upload_gcs_path, client=self.storage_client
        ).upload_from_filename(filename)

    def upload_dataframe(
        self,
        df: "pd.DataFrame",
        gcs_destination_blob_path: str,
        file_type: str = "jsonl",
    ) -> None:
        """Uploads a Pandas DataFrame to a Google Cloud Storage location.

        Args:
          df: The Pandas DataFrame to upload.
          gcs_destination_blob_path: The full GCS path for the destination blob
            (e.g., 'gs://bucket/data/my_dataframe.jsonl').
          file_type: The format to save the DataFrame ('jsonl' or 'csv'). Defaults
            to 'jsonl'.
        """
        bucket_name, blob_name = self.parse_gcs_path(gcs_destination_blob_path)
        if not blob_name:
            raise ValueError(
                f"Invalid GCS path for blob: '{gcs_destination_blob_path}'. "
                "It must include the object name (e.g., gs://bucket/file.csv)."
            )
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        buffer = io.StringIO()
        if file_type == "csv":
            df.to_csv(buffer, index=False)
            content_type = "text/csv"
        elif file_type == "jsonl":
            df.to_json(buffer, orient="records", lines=True)
            content_type = "application/jsonl"
        else:
            raise ValueError(
                f"Unsupported file type: '{file_type}'. "
                "Please provide 'jsonl' or 'csv'."
            )
        blob.upload_from_string(buffer.getvalue(), content_type=content_type)

        logger.info(
            f"DataFrame successfully uploaded to: gs://{bucket.name}/{blob.name}"
        )

    def upload_json(self, data: dict[str, Any], gcs_destination_blob_path: str) -> None:
        """Uploads a dictionary as a JSON file to Google Cloud Storage."""
        bucket_name, blob_name = self.parse_gcs_path(gcs_destination_blob_path)
        if not blob_name:
            raise ValueError(
                f"Invalid GCS path for blob: '{gcs_destination_blob_path}'. "
                "It must include the object name (e.g., gs://bucket/file.json)."
            )
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        json_data = json.dumps(data, indent=2)
        blob.upload_from_string(json_data, content_type="application/json")

        logger.info(
            f"JSON data successfully uploaded to: gs://{bucket_name}/{blob_name}"
        )

    def upload_json_to_prefix(
        self,
        data: dict[str, Any],
        gcs_dest_prefix: str,
        filename_prefix: str = "data",
    ) -> str:
        """Uploads a dictionary to a GCS prefix with a timestamped JSON filename.

        Args:
          data: The dictionary to upload.
          gcs_dest_prefix: The GCS prefix (e.g., 'gs://bucket/path/prefix/').
          filename_prefix: Prefix for the generated filename. Defaults to 'data'.

        Returns:
          The full GCS path where the file was uploaded.

        Raises:
          ValueError: If the gcs_dest_prefix is not a valid GCS path.
        """
        if not gcs_dest_prefix.startswith(GCS_PREFIX):
            raise ValueError(
                f"Invalid GCS destination prefix: '{gcs_dest_prefix}'. Must start"
                f" with '{GCS_PREFIX}'."
            )

        gcs_path_without_scheme = gcs_dest_prefix[len(GCS_PREFIX) :]
        bucket_name, *path_parts = gcs_path_without_scheme.split("/")

        user_prefix_path = "/".join(path_parts)
        if user_prefix_path and not user_prefix_path.endswith("/"):
            user_prefix_path += "/"

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"

        blob_name = f"{user_prefix_path}{filename}"

        full_gcs_path = f"{GCS_PREFIX}{bucket_name}/{blob_name}"

        self.upload_json(data, full_gcs_path)
        return full_gcs_path

    def read_file_contents(self, gcs_filepath: str) -> Union[str, Any]:
        """Reads the contents of a file from Google Cloud Storage."""

        bucket_name, blob_path = self.parse_gcs_path(gcs_filepath)
        if not blob_path:
            raise ValueError(
                f"Invalid GCS file path: '{gcs_filepath}'. Path must point to a file,"
                " not just a bucket."
            )
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        content = blob.download_as_bytes().decode("utf-8")
        logger.info(f"Successfully read content from '{gcs_filepath}'")
        return content

    def read_gcs_file_to_dataframe(
        self, gcs_filepath: str, file_type: str
    ) -> "pd.DataFrame":
        """Reads a file from Google Cloud Storage into a Pandas DataFrame."""
        file_contents = self.read_file_contents(gcs_filepath)
        if file_type == "csv":
            return pd.read_csv(io.StringIO(file_contents), encoding="utf-8")
        elif file_type == "jsonl":
            return pd.read_json(io.StringIO(file_contents), lines=True)
        else:
            raise ValueError(
                f"Unsupported file type: '{file_type}'. Please provide 'jsonl' or"
                " 'csv'."
            )


class BigQueryUtils:
    """Handles BigQuery operations."""

    def __init__(self, api_client: BaseApiClient):
        self.api_client = api_client
        self.bigquery_client = bigquery.Client(
            project=self.api_client.project,
            credentials=self.api_client._credentials,
        )

    def load_bigquery_to_dataframe(self, table_uri: str) -> "pd.DataFrame":
        """Loads data from a BigQuery table into a DataFrame."""
        table = self.bigquery_client.get_table(table_uri)
        return self.bigquery_client.list_rows(table).to_dataframe()

    def upload_dataframe_to_bigquery(
        self, df: "pd.DataFrame", bq_table_uri: str
    ) -> None:
        """Uploads a Pandas DataFrame to a BigQuery table."""
        job = self.bigquery_client.load_table_from_dataframe(df, bq_table_uri)
        job.result()
        logger.info(
            f"DataFrame successfully uploaded to BigQuery table: {bq_table_uri}"
        )


class EvalDatasetLoader:
    """A loader for datasets from various sources, using a shared client."""

    def __init__(self, api_client: BaseApiClient):
        self.api_client = api_client
        self.gcs_utils = GcsUtils(self.api_client)
        self.bigquery_utils = BigQueryUtils(self.api_client)

    def _load_file(
        self, filepath: str, file_type: str
    ) -> Union[list[dict[str, Any]], Any]:
        """Loads data from a file into a list of dictionaries."""
        if filepath.startswith(GCS_PREFIX):
            df = self.gcs_utils.read_gcs_file_to_dataframe(filepath, file_type)
            return df.to_dict(orient="records")
        else:
            if file_type == "jsonl":
                df = pd.read_json(filepath, lines=True)
                return df.to_dict(orient="records")
            elif file_type == "csv":
                df = pd.read_csv(filepath, encoding="utf-8")
                return df.to_dict(orient="records")
            else:
                raise ValueError(
                    f"Unsupported file type: '{file_type}'. Please provide 'jsonl' or"
                    " 'csv'."
                )

    def load(
        self, source: Union[str, "pd.DataFrame"]
    ) -> Union[list[dict[str, Any]], Any]:
        """Loads dataset from various sources into a list of dictionaries."""
        if isinstance(source, pd.DataFrame):
            return source.to_dict(orient="records")
        elif isinstance(source, str):
            if source.startswith(BQ_PREFIX):
                df = self.bigquery_utils.load_bigquery_to_dataframe(
                    source[len(BQ_PREFIX) :]
                )
                return df.to_dict(orient="records")

            _, extension = os.path.splitext(source)
            file_type = extension.lower()[1:]

            if file_type == "jsonl":
                return self._load_file(source, "jsonl")
            elif file_type == "csv":
                return self._load_file(source, "csv")
            else:
                raise TypeError(
                    f"Unsupported file type: {file_type} from {source}. Please"
                    " provide a valid GCS path with `jsonl` or `csv` suffix, "
                    "a local file path, or a valid BigQuery table URI."
                )
        else:
            raise TypeError(
                "Unsupported dataset type. Must be a `pd.DataFrame`, Python"
                " a valid GCS path with `jsonl` or `csv` suffix, a local"
                " file path, or a valid BigQuery table URI."
            )


class LazyLoadedPrebuiltMetric:
    """A proxy object representing a prebuilt metric that will be loaded on demand."""

    _cache: dict[str, types.LLMMetric] = {}
    _base_gcs_path = (
        "gs://vertex-ai-generative-ai-eval-sdk-resources/metrics/{metric_name}/"
    )

    def __init__(self, name: str, version: Optional[str] = None):
        self.name = name.lower()
        self.version = version or "latest"
        self._resolved_metric: Optional[types.LLMMetric] = None

    def _get_latest_version_uri(self, api_client: Any, metric_gcs_dir: str) -> str:
        """Lists files in GCS directory and determines the latest version URI."""
        gcs_utils = GcsUtils(api_client)
        bucket_name, prefix = gcs_utils.parse_gcs_path(metric_gcs_dir)

        blobs = gcs_utils.storage_client.list_blobs(bucket_name, prefix=prefix)

        version_files: list[
            dict[str, Union[list[int], str]]
        ] = []  # {'version_parts': [1,0,0], 'filename': 'v1.0.0.yaml'}

        # Regex to capture versions like v1, v1.0, v1.0.0 (supports .yaml and .json)
        # It prioritizes more specific versions (e.g., v1.2.3 over v1.2)
        version_pattern = re.compile(
            r"v(\d+)(?:\.(\d+))?(?:\.(\d+))?\.(yaml|yml|json)$", re.IGNORECASE
        )

        for blob in blobs:
            match = version_pattern.match(os.path.basename(blob.name))
            if match:
                major = int(match.group(1))
                minor = int(match.group(2)) if match.group(2) else 0
                patch = int(match.group(3)) if match.group(3) else 0
                version_files.append(
                    {
                        "version_parts": [major, minor, patch],
                        "filename": os.path.basename(blob.name),
                    }
                )

        if not version_files:
            raise IOError(f"No versioned metric files found in {metric_gcs_dir}")

        version_files.sort(key=lambda x: x["version_parts"], reverse=True)

        latest_filename = version_files[0]["filename"]
        return os.path.join(metric_gcs_dir, latest_filename)

    def _fetch_and_parse(self, api_client: Any) -> types.LLMMetric:
        """Fetches and parses the metric definition from the URI."""
        metric_gcs_dir = self._base_gcs_path.format(metric_name=self.name)
        uri: str
        if self.version == "latest":
            uri = self._get_latest_version_uri(api_client, metric_gcs_dir)
            resolved_version_match = re.match(
                r"(v\d+(?:\.\d+)*)\.(?:yaml|yml|json)",
                os.path.basename(uri),
                re.IGNORECASE,
            )
            if resolved_version_match:
                self.version = resolved_version_match.group(1)
            else:
                self.version = os.path.splitext(
                    os.path.splitext(os.path.basename(uri))[0]
                )[0]
        else:
            yaml_uri = os.path.join(metric_gcs_dir, f"{self.version}.yaml")
            json_uri = os.path.join(metric_gcs_dir, f"{self.version}.json")

            gcs_utils = GcsUtils(api_client)
            try:
                bucket_name, blob_path = gcs_utils.parse_gcs_path(yaml_uri)
                if (
                    gcs_utils.storage_client.bucket(bucket_name)
                    .blob(blob_path)
                    .exists()
                ):
                    uri = yaml_uri
                else:
                    bucket_name_json, blob_path_json = gcs_utils.parse_gcs_path(
                        json_uri
                    )
                    if (
                        gcs_utils.storage_client.bucket(bucket_name_json)
                        .blob(blob_path_json)
                        .exists()
                    ):
                        uri = json_uri
                    else:
                        raise IOError(
                            f"Metric file for version '{self.version}' not found as .yaml"
                            f" or .json in {metric_gcs_dir}"
                        )
            except Exception as e:
                raise IOError(
                    f"Error checking for metric file version '{self.version}' in"
                    f" {metric_gcs_dir}: {e}"
                ) from e

        logger.info(
            "Fetching predefined metric '%s@%s' from %s...",
            self.name,
            self.version,
            uri,
        )

        gcs_utils = GcsUtils(api_client)
        content_str = gcs_utils.read_file_contents(uri)

        file_extension = os.path.splitext(uri)[1].lower()
        data: dict[str, Any]
        if file_extension == ".yaml" or file_extension == ".yml":
            if yaml is None:
                raise ImportError(
                    "YAML parsing requires the pyyaml library. Please install it"
                    " using 'pip install google-cloud-aiplatform[evaluation]'."
                )
            data = yaml.safe_load(content_str)
        elif file_extension == ".json":
            data = json.loads(content_str)
        else:
            raise ValueError(
                f"Unsupported file extension for metric config: {file_extension}."
                " Must be .yaml, .yml, or .json"
            )

        if not isinstance(data, dict):
            raise ValueError("Metric config content did not parse into a dictionary.")

        if "prompt_template" in data and isinstance(data["prompt_template"], dict):
            data["prompt_template"] = types.MetricPromptBuilder.model_validate(
                data["prompt_template"]
            )

        metric_obj = types.LLMMetric.model_validate(data)

        metric_obj._is_predefined = True
        metric_obj._config_source = uri
        metric_obj._version = self.version
        return metric_obj

    def resolve(self, api_client: Any) -> types.LLMMetric:
        """Resolves the metric by loading it from the cache or fetching it if necessary."""
        if self._resolved_metric is None:
            temp_version_for_key = self.version

            cache_key = f"{self.name}@{temp_version_for_key}"

            if (
                cache_key in LazyLoadedPrebuiltMetric._cache
                and temp_version_for_key != "latest"
            ):
                self._resolved_metric = LazyLoadedPrebuiltMetric._cache[cache_key]
                logger.debug(f"Metric '{cache_key}' found in cache.")
            else:
                logger.debug(
                    f"Metric '{self.name}@{self.version}' not in cache or version is"
                    " 'latest'. Fetching..."
                )
                try:
                    fetched_metric = self._fetch_and_parse(api_client)
                    final_cache_key = f"{self.name}@{self.version}"
                    LazyLoadedPrebuiltMetric._cache[final_cache_key] = fetched_metric
                    self._resolved_metric = fetched_metric
                except Exception as e:
                    logger.error(
                        f"Error loading predefined metric {self.name} (requested version:"
                        f" {self.version}): {e}"
                    )
                    raise
        return self._resolved_metric

    def __call__(self, version: Optional[str] = None) -> "LazyLoadedPrebuiltMetric":
        """Allows setting a specific version."""
        if version is not None:
            return LazyLoadedPrebuiltMetric(name=self.name, version=version)
        return self


class PrebuiltMetricLoader:
    """Provides access to predefined evaluation metrics via attributes.

    This class provides a set of predefined LLM-based metrics (Autorater recipes)
    for evaluation. These metrics are lazily loaded from a GCS repository
    when they are first accessed.

    Example:
      metric = PrebuiltMetric.TEXT_QUALITY
      metric = PrebuiltMetric.TEXT_QUALITY(version="v1")
    """

    def __getattr__(self, name: str) -> LazyLoadedPrebuiltMetric:
        return LazyLoadedPrebuiltMetric(name=name)

    @property
    def TEXT_QUALITY(self) -> LazyLoadedPrebuiltMetric:
        return self.__getattr__("TEXT_QUALITY")

    @property
    def INSTRUCTION_FOLLOWING(self) -> LazyLoadedPrebuiltMetric:
        return self.__getattr__("INSTRUCTION_FOLLOWING")

    @property
    def COHERENCE(self) -> LazyLoadedPrebuiltMetric:
        return self.__getattr__("COHERENCE")

    @property
    def FLUENCY(self) -> LazyLoadedPrebuiltMetric:
        return self.__getattr__("FLUENCY")

    @property
    def GROUNDEDNESS(self) -> LazyLoadedPrebuiltMetric:
        return self.__getattr__("GROUNDEDNESS")

    @property
    def SAFETY(self) -> LazyLoadedPrebuiltMetric:
        return self.__getattr__("SAFETY")

    @property
    def VERBOSITY(self) -> LazyLoadedPrebuiltMetric:
        return self.__getattr__("VERBOSITY")

    @property
    def SUMMARIZATION_QUALITY(self) -> LazyLoadedPrebuiltMetric:
        return self.__getattr__("SUMMARIZATION_QUALITY")

    @property
    def QUESTION_ANSWERING_QUALITY(self) -> LazyLoadedPrebuiltMetric:
        return self.__getattr__("QUESTION_ANSWERING_QUALITY")

    @property
    def MULTI_TURN_CHAT_QUALITY(self) -> LazyLoadedPrebuiltMetric:
        return self.__getattr__("MULTI_TURN_CHAT_QUALITY")

    @property
    def MULTI_TURN_SAFETY(self) -> LazyLoadedPrebuiltMetric:
        return self.__getattr__("MULTI_TURN_SAFETY")


PrebuiltMetric = PrebuiltMetricLoader()


class BatchEvaluateRequestPreparer:
    """Prepares data for requests."""

    @staticmethod
    def _EvaluationDataset_to_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}

        if getv(from_object, ["gcs_source"]) is not None:
            setv(
                to_object,
                ["gcs_source"],
                getv(from_object, ["gcs_source"]),
            )

        if getv(from_object, ["bigquery_source"]) is not None:
            setv(
                to_object,
                ["bigquery_source"],
                getv(from_object, ["bigquery_source"]),
            )

        return to_object

    @staticmethod
    def _Metric_to_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}

        if getv(from_object, ["prompt_template"]) is not None:
            setv(
                to_object,
                ["pointwise_metric_spec", "prompt_template"],
                getv(from_object, ["prompt_template"]),
            )

        if getv(from_object, ["judge_model"]) is not None:
            setv(
                parent_object,
                ["autorater_config", "autorater_model"],
                getv(from_object, ["judge_model"]),
            )

        if getv(from_object, ["judge_model_sampling_count"]) is not None:
            setv(
                parent_object,
                ["autorater_config", "sampling_count"],
                getv(from_object, ["judge_model_sampling_count"]),
            )

        if getv(from_object, ["judge_model_system_instruction"]) is not None:
            setv(
                to_object,
                ["pointwise_metric_spec", "system_instruction"],
                getv(from_object, ["judge_model_system_instruction"]),
            )

        if getv(from_object, ["return_raw_output"]) is not None:
            setv(
                to_object,
                [
                    "pointwise_metric_spec",
                    "custom_output_format_config",
                    "return_raw_output",
                ],
                getv(from_object, ["return_raw_output"]),
            )

        return to_object

    @staticmethod
    def _OutputConfig_to_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}
        if getv(from_object, ["gcs_destination"]) is not None:
            setv(
                to_object,
                ["gcsDestination"],
                getv(from_object, ["gcs_destination"]),
            )

        return to_object

    @staticmethod
    def _EvaluationDataset_from_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}

        if getv(from_object, ["dataset", "gcs_source"]) is not None:
            setv(
                to_object,
                ["gcs_source"],
                getv(from_object, ["dataset", "gcs_source"]),
            )

        if getv(from_object, ["dataset", "bigquery_source"]) is not None:
            setv(
                to_object,
                ["bigquery_source"],
                getv(from_object, ["dataset", "bigquery_source"]),
            )

        return to_object

    @staticmethod
    def _AutoraterConfig_to_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}
        if getv(from_object, ["sampling_count"]) is not None:
            setv(to_object, ["samplingCount"], getv(from_object, ["sampling_count"]))

        if getv(from_object, ["flip_enabled"]) is not None:
            setv(to_object, ["flipEnabled"], getv(from_object, ["flip_enabled"]))

        if getv(from_object, ["autorater_model"]) is not None:
            setv(
                to_object,
                ["autoraterModel"],
                getv(from_object, ["autorater_model"]),
            )

        return to_object

    @staticmethod
    def EvaluateDatasetOperation_from_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}
        if getv(from_object, ["name"]) is not None:
            setv(to_object, ["name"], getv(from_object, ["name"]))

        if getv(from_object, ["metadata"]) is not None:
            setv(to_object, ["metadata"], getv(from_object, ["metadata"]))

        if getv(from_object, ["done"]) is not None:
            setv(to_object, ["done"], getv(from_object, ["done"]))

        if getv(from_object, ["error"]) is not None:
            setv(to_object, ["error"], getv(from_object, ["error"]))

        if getv(from_object, ["response"]) is not None:
            setv(
                to_object,
                ["response"],
                BatchEvaluateRequestPreparer._EvaluationDataset_from_vertex(
                    getv(from_object, ["response"]), to_object
                ),
            )

        return to_object

    @staticmethod
    def EvaluateDatasetRequestParameters_to_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}
        if getv(from_object, ["dataset"]) is not None:
            setv(
                to_object,
                ["dataset"],
                BatchEvaluateRequestPreparer._EvaluationDataset_to_vertex(
                    getv(from_object, ["dataset"]), to_object
                ),
            )

        if getv(from_object, ["metrics"]) is not None:
            setv(
                to_object,
                ["metrics"],
                [
                    BatchEvaluateRequestPreparer._Metric_to_vertex(item, to_object)
                    for item in getv(from_object, ["metrics"])
                ],
            )

        if getv(from_object, ["output_config"]) is not None:
            setv(
                to_object,
                ["outputConfig"],
                BatchEvaluateRequestPreparer._OutputConfig_to_vertex(
                    getv(from_object, ["output_config"]), to_object
                ),
            )

        if getv(from_object, ["autorater_config"]) is not None:
            setv(
                to_object,
                ["autoraterConfig"],
                BatchEvaluateRequestPreparer._AutoraterConfig_to_vertex(
                    getv(from_object, ["autorater_config"]), to_object
                ),
            )

        if getv(from_object, ["config"]) is not None:
            setv(to_object, ["config"], getv(from_object, ["config"]))

        return to_object

    @staticmethod
    def prepare_metric_payload(
        request_dict: dict[str, Any], resolved_metrics: list[types.MetricSubclass]
    ) -> dict[str, Any]:
        """Prepares the metric payload for the evaluation request.

        Args:
            request_dict: The dictionary containing the request details.
            resolved_metrics: A list of resolved metric objects.

        Returns:
            The updated request dictionary with the prepared metric payload.
        """
        metrics_payload = []

        for metric in resolved_metrics:
            metric_payload_item = {}
            metric_payload_item["aggregation_metrics"] = [
                "AVERAGE",
                "STANDARD_DEVIATION",
            ]

            metric_name = getv(metric, ["name"]).lower()

            if metric_name == "exact_match":
                metric_payload_item["exact_match_spec"] = {}
            elif metric_name == "bleu":
                metric_payload_item["bleu_spec"] = {}
            elif metric_name.startswith("rouge"):
                rouge_type = metric_name.replace("_", "")
                metric_payload_item["rouge_spec"] = {"rouge_type": rouge_type}

            elif hasattr(metric, "prompt_template") and metric.prompt_template:
                pointwise_spec = {"metric_prompt_template": metric.prompt_template}
                system_instruction = getv(metric, ["judge_model_system_instruction"])
                if system_instruction:
                    pointwise_spec["system_instruction"] = system_instruction
                metric_payload_item["pointwise_metric_spec"] = pointwise_spec
            else:
                raise ValueError(
                    "Unsupported metric type or invalid metric name:" f" {metric_name}"
                )

            metrics_payload.append(metric_payload_item)
        request_dict["metrics"] = metrics_payload
        return request_dict
