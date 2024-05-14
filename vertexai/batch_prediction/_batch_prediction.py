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
"""Class to support Batch Prediction with GenAI models."""
# pylint: disable=protected-access

import logging
import re
from typing import List, Optional, Union

from google.cloud.aiplatform import base as aiplatform_base
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform import jobs
from google.cloud.aiplatform import utils as aiplatform_utils
from vertexai import generative_models


_LOGGER = aiplatform_base.Logger(__name__)

_GEMINI_MODEL_PATTERN = r"publishers/google/models/gemini"


class BatchPredictionJob(aiplatform_base._VertexAiResourceNounPlus):
    """Represents a BatchPredictionJob that runs with GenAI models."""

    _resource_noun = "batchPredictionJobs"
    _getter_method = "get_batch_prediction_job"
    _list_method = "list_batch_prediction_jobs"
    _cancel_method = "cancel_batch_prediction_job"
    _delete_method = "delete_batch_prediction_job"
    _job_type = "batch-predictions"
    _parse_resource_name_method = "parse_batch_prediction_job_path"
    _format_resource_name_method = "batch_prediction_job_path"

    client_class = aiplatform_utils.JobClientWithOverride

    def __init__(self, batch_prediction_job_name: str):
        """Retrieves a BatchPredictionJob resource that runs with a GenAI model.

        Args:
            batch_prediction_job_name (str):
                Required. A fully-qualified BatchPredictionJob resource name or
                ID. Example: "projects/.../locations/.../batchPredictionJobs/456"
                or "456" when project and location are initialized.

        Raises:
            ValueError: If batch_prediction_job_name represents a BatchPredictionJob
            resource that runs with another type of model.
        """
        super().__init__(resource_name=batch_prediction_job_name)
        self._gca_resource = self._get_gca_resource(
            resource_name=batch_prediction_job_name
        )
        # TODO(b/338452508) Support tuned GenAI models.
        if not re.search(_GEMINI_MODEL_PATTERN, self._gca_resource.model):
            raise ValueError(
                f"BatchPredictionJob '{batch_prediction_job_name}' "
                f"runs with the model '{self._gca_resource.model}', "
                "which is not a GenAI model."
            )

    @classmethod
    def submit(
        cls,
        source_model: Union[str, generative_models.GenerativeModel],
        input_dataset: Union[str, List[str]],
        *,
        output_uri_prefix: Optional[str] = None,
    ) -> "BatchPredictionJob":
        """Submits a batch prediction job for a GenAI model.

        Args:
            source_model (Union[str, generative_models.GenerativeModel]):
                Model name or a GenerativeModel instance for batch prediction.
                Supported formats: "gemini-1.0-pro", "models/gemini-1.0-pro",
                and "publishers/google/models/gemini-1.0-pro"
            input_dataset (Union[str,List[str]]):
                GCS URI(-s) or Bigquery URI to your input data to run batch
                prediction on. Example: "gs://path/to/input/data.jsonl" or
                "bq://projectId.bqDatasetId.bqTableId"
            output_uri_prefix (str):
                GCS or Bigquery URI prefix for the output predictions. Example:
                "gs://path/to/output/data" or "bq://projectId.bqDatasetId"
                If not specified, f"{STAGING_BUCKET}/gen-ai-batch-prediction" will
                be used for GCS source and
                f"bq://projectId.gen_ai_batch_prediction.predictions_{TIMESTAMP}"
                will be used for Bigquery source.

        Returns:
            Instantiated BatchPredictionJob.

        Raises:
            ValueError: If source_model is not a GenAI model.
            Or if input_dataset or output_uri_prefix are not in supported formats.
            Or if output_uri_prefix is not specified and staging_bucket is not
            set in vertexai.init().
        """
        # Handle model name
        # TODO(b/338452508) Support tuned GenAI models.
        model_name = cls._reconcile_model_name(
            source_model._model_name
            if isinstance(source_model, generative_models.GenerativeModel)
            else source_model
        )

        # Handle input URI
        gcs_source = None
        bigquery_source = None
        first_input_uri = (
            input_dataset if isinstance(input_dataset, str) else input_dataset[0]
        )
        if first_input_uri.startswith("gs://"):
            gcs_source = input_dataset
        elif first_input_uri.startswith("bq://"):
            if not isinstance(input_dataset, str):
                raise ValueError("Multiple Bigquery input datasets are not supported.")
            bigquery_source = input_dataset
        else:
            raise ValueError(
                f"Unsupported input URI: {input_dataset}. "
                "Supported formats: 'gs://path/to/input/data.jsonl' and "
                "'bq://projectId.bqDatasetId.bqTableId'"
            )

        # Handle output URI
        gcs_destination_prefix = None
        bigquery_destination_prefix = None
        if output_uri_prefix:
            if output_uri_prefix.startswith("gs://"):
                gcs_destination_prefix = output_uri_prefix
            elif output_uri_prefix.startswith("bq://"):
                # Temporarily handle this in SDK, will remove once b/338423462 is fixed.
                bigquery_destination_prefix = cls._complete_bq_uri(output_uri_prefix)
            else:
                raise ValueError(
                    f"Unsupported output URI: {output_uri_prefix}. "
                    "Supported formats: 'gs://path/to/output/data' and "
                    "'bq://projectId.bqDatasetId'"
                )
        else:
            if first_input_uri.startswith("gs://"):
                if not aiplatform_initializer.global_config.staging_bucket:
                    raise ValueError(
                        "Please either specify output_uri_prefix or "
                        "set staging_bucket in vertexai.init()."
                    )
                gcs_destination_prefix = (
                    aiplatform_initializer.global_config.staging_bucket.rstrip("/")
                    + "/gen-ai-batch-prediction"
                )
            else:
                bigquery_destination_prefix = cls._complete_bq_uri()

        # Reuse aiplatform class to submit the job (override _LOGGER)
        logging.getLogger("google.cloud.aiplatform.jobs").disabled = True
        try:
            aiplatform_job = jobs.BatchPredictionJob.submit(
                model_name=model_name,
                gcs_source=gcs_source,
                bigquery_source=bigquery_source,
                gcs_destination_prefix=gcs_destination_prefix,
                bigquery_destination_prefix=bigquery_destination_prefix,
            )
            job = cls._empty_constructor()
            job._gca_resource = aiplatform_job._gca_resource

            _LOGGER.log_create_complete(
                cls, job._gca_resource, "job", module_name="batch_prediction"
            )
            _LOGGER.info(
                "View Batch Prediction Job:\n%s" % aiplatform_job._dashboard_uri()
            )

            return job
        finally:
            logging.getLogger("google.cloud.aiplatform.jobs").disabled = False

    @classmethod
    def _reconcile_model_name(cls, model_name: str) -> str:
        """Reconciles model name to a publisher model resource name."""
        if not model_name:
            raise ValueError("model_name must not be empty")
        if "/" not in model_name:
            model_name = "publishers/google/models/" + model_name
        elif model_name.startswith("models/"):
            model_name = "publishers/google/" + model_name
        elif not model_name.startswith("publishers/google/models/") and not re.search(
            r"^projects/.*?/locations/.*?/publishers/google/models/.*$", model_name
        ):
            raise ValueError(f"Invalid format for model name: {model_name}.")

        if not re.search(_GEMINI_MODEL_PATTERN, model_name):
            raise ValueError(f"Model '{model_name}' is not a GenAI model.")

        return model_name

    @classmethod
    def _complete_bq_uri(cls, uri: Optional[str] = None):
        """Completes a BigQuery uri to a BigQuery table uri."""
        uri_parts = uri.split(".") if uri else []
        uri_len = len(uri_parts)
        if len(uri_parts) > 3:
            raise ValueError(
                f"Invalid URI: {uri}. "
                "Supported formats: 'bq://projectId.bqDatasetId.bqTableId'"
            )

        schema_and_project = (
            uri_parts[0]
            if uri_len >= 1
            else f"bq://{aiplatform_initializer.global_config.project}"
        )
        if not schema_and_project.startswith("bq://"):
            raise ValueError("URI must start with 'bq://'")

        dataset = uri_parts[1] if uri_len >= 2 else "gen_ai_batch_prediction"

        table = (
            uri_parts[2]
            if uri_len >= 3
            else f"predictions_{aiplatform_utils.timestamped_unique_name()}"
        )

        return f"{schema_and_project}.{dataset}.{table}"
