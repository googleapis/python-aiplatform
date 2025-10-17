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

import abc
import logging
from typing import Any, Optional, Union

from google.genai._common import get_value_by_path as getv
from google.genai._common import set_value_by_path as setv

from . import _transformers
from . import types


logger = logging.getLogger(__name__)


GCS_PREFIX = "gs://"
BQ_PREFIX = "bq://"


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
        request_dict: dict[str, Any], resolved_metrics: list["types.MetricSubclass"]
    ) -> dict[str, Any]:
        """Prepares the metric payload for the evaluation request.

        Args:
            request_dict: The dictionary containing the request details.
            resolved_metrics: A list of resolved metric objects.

        Returns:
            The updated request dictionary with the prepared metric payload.
        """
        request_dict["metrics"] = _transformers.t_metrics(
            resolved_metrics, set_default_aggregation_metrics=True
        )
        return request_dict


class EvalDataConverter(abc.ABC):
    """Abstract base class for dataset converters."""

    @abc.abstractmethod
    def convert(self, raw_data: Any) -> "types.EvaluationDataset":
        """Converts a loaded raw dataset into an EvaluationDataset."""
        raise NotImplementedError()
