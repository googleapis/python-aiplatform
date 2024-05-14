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

from google.cloud.aiplatform import base as aiplatform_base
from google.cloud.aiplatform import utils as aiplatform_utils


_LOGGER = aiplatform_base.Logger(__name__)

_GEMINI_MODEL_PREFIX = "publishers/google/models/gemini"


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
        if not self._gca_resource.model.startswith(_GEMINI_MODEL_PREFIX):
            raise ValueError(
                f"BatchPredictionJob '{batch_prediction_job_name}' "
                f"runs with the model '{self._gca_resource.model}', "
                "which is not a GenAI model."
            )
