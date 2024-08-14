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
"""Library for Metrics Computation with Evaluation Service Client."""

from typing import Any, Dict, Union

from google import api_core
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1beta1.services import (
    evaluation_service as gapic_evaluation_services,
)
from google.cloud.aiplatform_v1beta1.types import (
    evaluation_service as gapic_eval_service_types,
)
from vertexai.preview.evaluation import _base as eval_base
from vertexai.preview.evaluation import constants
from vertexai.preview.evaluation import utils
from vertexai.preview.evaluation.metrics import (
    _base as metrics_base,
)
from vertexai.preview.evaluation.metrics import _rouge
from google.protobuf import json_format


_LOGGER = base.Logger(__name__)
_METRIC_NAME_TO_METRIC_SPEC = {
    # Automatic Metrics.
    constants.Metric.EXACT_MATCH: (gapic_eval_service_types.ExactMatchSpec()),
    constants.Metric.BLEU: gapic_eval_service_types.BleuSpec(),
    constants.Metric.ROUGE: gapic_eval_service_types.RougeSpec(),
    constants.Metric.ROUGE_1: gapic_eval_service_types.RougeSpec(rouge_type="rouge1"),
    constants.Metric.ROUGE_2: gapic_eval_service_types.RougeSpec(rouge_type="rouge2"),
    constants.Metric.ROUGE_L: gapic_eval_service_types.RougeSpec(rouge_type="rougeL"),
    constants.Metric.ROUGE_L_SUM: gapic_eval_service_types.RougeSpec(
        rouge_type="rougeLsum"
    ),
    constants.Metric.TOOL_CALL_VALID: (gapic_eval_service_types.ToolCallValidSpec()),
    constants.Metric.TOOL_NAME_MATCH: (gapic_eval_service_types.ToolNameMatchSpec()),
    constants.Metric.TOOL_PARAMETER_KV_MATCH: (
        gapic_eval_service_types.ToolParameterKVMatchSpec()
    ),
    constants.Metric.TOOL_PARAMETER_KEY_MATCH: (
        gapic_eval_service_types.ToolParameterKeyMatchSpec()
    ),
    # Model-based Pointwise Metrics.
    constants.Metric.FLUENCY: gapic_eval_service_types.FluencySpec(),
    constants.Metric.COHERENCE: gapic_eval_service_types.CoherenceSpec(),
    constants.Metric.SAFETY: gapic_eval_service_types.SafetySpec(),
    constants.Metric.GROUNDEDNESS: (gapic_eval_service_types.GroundednessSpec()),
    constants.Metric.FULFILLMENT: (gapic_eval_service_types.FulfillmentSpec()),
    constants.Metric.SUMMARIZATION_QUALITY: (
        gapic_eval_service_types.SummarizationQualitySpec()
    ),
    constants.Metric.SUMMARIZATION_HELPFULNESS: (
        gapic_eval_service_types.SummarizationHelpfulnessSpec()
    ),
    constants.Metric.SUMMARIZATION_VERBOSITY: (
        gapic_eval_service_types.SummarizationVerbositySpec()
    ),
    constants.Metric.QUESTION_ANSWERING_QUALITY: (
        gapic_eval_service_types.QuestionAnsweringQualitySpec()
    ),
    constants.Metric.QUESTION_ANSWERING_RELEVANCE: (
        gapic_eval_service_types.QuestionAnsweringRelevanceSpec()
    ),
    constants.Metric.QUESTION_ANSWERING_CORRECTNESS: (
        gapic_eval_service_types.QuestionAnsweringCorrectnessSpec(use_reference=True)
    ),
    constants.Metric.QUESTION_ANSWERING_HELPFULNESS: (
        gapic_eval_service_types.QuestionAnsweringHelpfulnessSpec()
    ),
    # Side-by-side(SxS) Pairwise Metrics.
    constants.Metric.PAIRWISE_SUMMARIZATION_QUALITY: (
        gapic_eval_service_types.PairwiseSummarizationQualitySpec()
    ),
    constants.Metric.PAIRWISE_QUESTION_ANSWERING_QUALITY: (
        gapic_eval_service_types.PairwiseQuestionAnsweringQualitySpec()
    ),
}


def build_request(
    metric: Union[str, metrics_base._Metric],
    row_dict: Dict[str, Any],
    evaluation_run_config: eval_base.EvaluationRunConfig,
) -> gapic_eval_service_types.EvaluateInstancesRequest:
    """Builds a metric instance and form the request for the evaluation service.

    Args:
        metric: The name of the metric to evaluate.
        row_dict: An eval dataset instance in a dictionary.
        evaluation_run_config: Evaluation Run Configurations.

    Returns:
        A single EvaluateInstancesRequest.
    """
    project = initializer.global_config.project
    location = initializer.global_config.location
    if not project or not location:
        raise ValueError(
            "No project or location specified. Please run `vertexai.init()` to"
            " provide these parameters."
        )
    location_path = (
        gapic_evaluation_services.EvaluationServiceClient.common_location_path(
            project, location
        )
    )

    metric_name = str(metric)
    if metric_name not in _METRIC_NAME_TO_METRIC_SPEC:
        raise ValueError(f"Metric name: {metric_name} not supported.")

    metric_spec = _METRIC_NAME_TO_METRIC_SPEC[metric_name]
    if isinstance(metric, metrics_base.PairwiseMetric) or isinstance(
        metric, metrics_base._ModelBasedMetric
    ):
        metric_spec.use_reference = metric.use_reference
        metric_spec.version = metric.version
    if isinstance(metric, _rouge.Rouge):
        metric_spec.rouge_type = metric.rouge_type
        metric_spec.use_stemmer = metric.use_stemmer
        metric_spec.split_summaries = metric.split_summaries

    column_map = evaluation_run_config.column_map
    prediction = row_dict.get(
        column_map.get(constants.Dataset.MODEL_RESPONSE_COLUMN), ""
    )
    baseline_prediction = row_dict.get(
        constants.Dataset.BASELINE_MODEL_RESPONSE_COLUMN, ""
    )
    reference = row_dict.get(column_map.get(constants.Dataset.REFERENCE_COLUMN), "")
    context = row_dict.get(column_map.get(constants.Dataset.CONTEXT_COLUMN), "")
    instruction = row_dict.get(column_map.get(constants.Dataset.INSTRUCTION_COLUMN), "")

    if "use_reference" in json_format.MessageToDict(
        metric_spec._pb, preserving_proto_field_name=True
    ):
        evaluation_run_config.validate_dataset_column(
            constants.Dataset.REFERENCE_COLUMN
        )

    # Automatic Metrics.
    if metric_name == constants.Metric.EXACT_MATCH:
        instance = gapic_eval_service_types.ExactMatchInput(
            metric_spec=metric_spec,
            instances=[
                gapic_eval_service_types.ExactMatchInstance(
                    prediction=prediction,
                    reference=reference,
                )
            ],
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            exact_match_input=instance,
        )
    if metric_name == constants.Metric.BLEU:
        instance = gapic_eval_service_types.BleuInput(
            metric_spec=metric_spec,
            instances=[
                gapic_eval_service_types.BleuInstance(
                    prediction=prediction,
                    reference=reference,
                )
            ],
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            bleu_input=instance,
        )
    if metric_name in (
        constants.Metric.ROUGE,
        constants.Metric.ROUGE_1,
        constants.Metric.ROUGE_2,
        constants.Metric.ROUGE_L,
        constants.Metric.ROUGE_L_SUM,
    ):
        instance = gapic_eval_service_types.RougeInput(
            metric_spec=metric_spec,
            instances=[
                gapic_eval_service_types.RougeInstance(
                    prediction=prediction,
                    reference=reference,
                )
            ],
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            rouge_input=instance,
        )
    if metric_name == constants.Metric.TOOL_CALL_VALID:
        instance = gapic_eval_service_types.ToolCallValidInput(
            metric_spec=metric_spec,
            instances=[
                gapic_eval_service_types.ToolCallValidInstance(
                    prediction=prediction,
                    reference=reference,
                )
            ],
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            tool_call_valid_input=instance,
        )
    if metric_name == constants.Metric.TOOL_NAME_MATCH:
        instance = gapic_eval_service_types.ToolNameMatchInput(
            metric_spec=metric_spec,
            instances=[
                gapic_eval_service_types.ToolNameMatchInstance(
                    prediction=prediction,
                    reference=reference,
                )
            ],
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            tool_name_match_input=instance,
        )
    if metric_name == constants.Metric.TOOL_PARAMETER_KEY_MATCH:
        instance = gapic_eval_service_types.ToolParameterKeyMatchInput(
            metric_spec=metric_spec,
            instances=[
                gapic_eval_service_types.ToolParameterKeyMatchInstance(
                    prediction=prediction,
                    reference=reference,
                )
            ],
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            tool_parameter_key_match_input=instance,
        )
    if metric_name == constants.Metric.TOOL_PARAMETER_KV_MATCH:
        instance = gapic_eval_service_types.ToolParameterKVMatchInput(
            metric_spec=metric_spec,
            instances=[
                gapic_eval_service_types.ToolParameterKVMatchInstance(
                    prediction=prediction,
                    reference=reference,
                )
            ],
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            tool_parameter_kv_match_input=instance,
        )
    # Model-based Pointwise Metrics.
    if metric_name == constants.Metric.COHERENCE:
        coherence_input = gapic_eval_service_types.CoherenceInput(
            metric_spec=metric_spec,
            instance=gapic_eval_service_types.CoherenceInstance(prediction=prediction),
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            coherence_input=coherence_input,
        )
    if metric_name == constants.Metric.FLUENCY:
        fluency_input = gapic_eval_service_types.FluencyInput(
            metric_spec=metric_spec,
            instance=gapic_eval_service_types.FluencyInstance(prediction=prediction),
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            fluency_input=fluency_input,
        )
    if metric_name == constants.Metric.SAFETY:
        safety_input = gapic_eval_service_types.SafetyInput(
            metric_spec=metric_spec,
            instance=gapic_eval_service_types.SafetyInstance(prediction=prediction),
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            safety_input=safety_input,
        )
    if metric_name == constants.Metric.GROUNDEDNESS:
        groundedness_input = gapic_eval_service_types.GroundednessInput(
            metric_spec=metric_spec,
            instance=gapic_eval_service_types.GroundednessInstance(
                prediction=prediction, context=context
            ),
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            groundedness_input=groundedness_input,
        )
    if metric_name == constants.Metric.FULFILLMENT:
        fulfillment_input = gapic_eval_service_types.FulfillmentInput(
            metric_spec=metric_spec,
            instance=gapic_eval_service_types.FulfillmentInstance(
                prediction=prediction, instruction=instruction
            ),
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            fulfillment_input=fulfillment_input,
        )
    if metric_name == constants.Metric.RESPONSE_RECALL:
        raise NotImplementedError("Response recall is not implemented.")
    if metric_name == constants.Metric.SUMMARIZATION_QUALITY:
        summarization_quality_input = (
            gapic_eval_service_types.SummarizationQualityInput(
                metric_spec=metric_spec,
                instance=gapic_eval_service_types.SummarizationQualityInstance(
                    prediction=prediction, context=context, instruction=instruction
                ),
            )
        )
        if metric_spec.use_reference:
            summarization_quality_input.instance.reference = reference
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            summarization_quality_input=summarization_quality_input,
        )
    if metric_name == constants.Metric.SUMMARIZATION_HELPFULNESS:
        summarization_helpfulness_input = (
            gapic_eval_service_types.SummarizationHelpfulnessInput(
                metric_spec=metric_spec,
                instance=gapic_eval_service_types.SummarizationHelpfulnessInstance(
                    prediction=prediction, context=context, instruction=instruction
                ),
            )
        )
        if metric_spec.use_reference:
            summarization_helpfulness_input.instance.reference = reference
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            summarization_helpfulness_input=summarization_helpfulness_input,
        )
    if metric_name == constants.Metric.SUMMARIZATION_VERBOSITY:
        summarization_verbosity_input = (
            gapic_eval_service_types.SummarizationVerbosityInput(
                metric_spec=metric_spec,
                instance=gapic_eval_service_types.SummarizationVerbosityInstance(
                    prediction=prediction, context=context, instruction=instruction
                ),
            )
        )
        if metric_spec.use_reference:
            summarization_verbosity_input.instance.reference = reference
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            summarization_verbosity_input=summarization_verbosity_input,
        )
    if metric_name == constants.Metric.QUESTION_ANSWERING_QUALITY:
        question_answering_quality_input = (
            gapic_eval_service_types.QuestionAnsweringQualityInput(
                metric_spec=metric_spec,
                instance=gapic_eval_service_types.QuestionAnsweringQualityInstance(
                    prediction=prediction, context=context, instruction=instruction
                ),
            )
        )
        if metric_spec.use_reference:
            question_answering_quality_input.instance.reference = reference
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            question_answering_quality_input=question_answering_quality_input,
        )
    if metric_name == constants.Metric.QUESTION_ANSWERING_HELPFULNESS:
        question_answering_helpfulness_input = (
            gapic_eval_service_types.QuestionAnsweringHelpfulnessInput(
                metric_spec=metric_spec,
                instance=gapic_eval_service_types.QuestionAnsweringHelpfulnessInstance(
                    prediction=prediction,
                    context=context,
                    instruction=instruction,
                ),
            )
        )
        if metric_spec.use_reference:
            question_answering_helpfulness_input.instance.reference = reference
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            question_answering_helpfulness_input=question_answering_helpfulness_input,
        )
    if metric_name == constants.Metric.QUESTION_ANSWERING_RELEVANCE:
        question_answering_relevance_input = (
            gapic_eval_service_types.QuestionAnsweringRelevanceInput(
                metric_spec=metric_spec,
                instance=gapic_eval_service_types.QuestionAnsweringRelevanceInstance(
                    prediction=prediction,
                    context=context,
                    instruction=instruction,
                ),
            )
        )
        if metric_spec.use_reference:
            question_answering_relevance_input.instance.reference = reference
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            question_answering_relevance_input=question_answering_relevance_input,
        )
    if metric_name == constants.Metric.QUESTION_ANSWERING_CORRECTNESS:
        question_answering_correctness_input = (
            gapic_eval_service_types.QuestionAnsweringCorrectnessInput(
                metric_spec=metric_spec,
                instance=gapic_eval_service_types.QuestionAnsweringCorrectnessInstance(
                    prediction=prediction,
                    context=context,
                    instruction=instruction,
                    reference=reference,
                ),
            )
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            question_answering_correctness_input=question_answering_correctness_input,
        )
    if metric_name == constants.Metric.RAG_CONTEXT_RECALL:
        raise NotImplementedError("RAG context recall is not implemented.")
    # Side-by-side(SxS) Pairwise Metrics.
    if metric_name == constants.Metric.PAIRWISE_SUMMARIZATION_QUALITY:
        instance = gapic_eval_service_types.PairwiseSummarizationQualityInstance(
            prediction=prediction,
            baseline_prediction=baseline_prediction,
            context=context,
            instruction=instruction,
        )
        if metric_spec.use_reference:
            instance.reference = reference
        pairwise_summarization_quality_input = (
            gapic_eval_service_types.PairwiseSummarizationQualityInput(
                metric_spec=metric_spec,
                instance=instance,
            )
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            pairwise_summarization_quality_input=pairwise_summarization_quality_input,
        )
    if metric_name == constants.Metric.PAIRWISE_QUESTION_ANSWERING_QUALITY:
        instance = gapic_eval_service_types.PairwiseQuestionAnsweringQualityInstance(
            prediction=prediction,
            baseline_prediction=baseline_prediction,
            context=context,
            instruction=instruction,
        )
        if metric_spec.use_reference:
            instance.reference = reference
        pairwise_question_answering_quality_input = (
            gapic_eval_service_types.PairwiseQuestionAnsweringQualityInput(
                metric_spec=metric_spec,
                instance=instance,
            )
        )
        return gapic_eval_service_types.EvaluateInstancesRequest(
            location=location_path,
            pairwise_question_answering_quality_input=pairwise_question_answering_quality_input,
        )


def _parse_autometric_results(
    metric_result_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """Parses the automatic metric results from the evaluation results.

    Args:
        metric_result_dict: The metric results dictionary.

    Returns:
        A dictionary containing metric score of the metric.
    """
    for value in metric_result_dict.values():
        # Only single instance requests are used by SDK.
        return {
            constants.MetricResult.SCORE_KEY: value[0].get(
                constants.MetricResult.SCORE_KEY
            )
        }


def _parse_model_based_pointwise_results(
    metric_result_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """Parses the model-based pointwise metric results from the evaluation results.

    Args:
        metric_result_dict: The metric results dictionary.

    Returns:
        A dictionary containing metric score, explanation, confidence of the
        metric.
    """
    return {
        constants.MetricResult.SCORE_KEY: metric_result_dict.get(
            constants.MetricResult.SCORE_KEY
        ),
        constants.MetricResult.EXPLANATION_KEY: metric_result_dict.get(
            constants.MetricResult.EXPLANATION_KEY
        ),
        constants.MetricResult.CONFIDENCE_KEY: metric_result_dict.get(
            constants.MetricResult.CONFIDENCE_KEY
        ),
    }


def _parse_pairwise_results(
    metric_result_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """Parses the pairwise metric results from the evaluation results.

    Args:
        metric_result_dict: The metric results dictionary.

    Returns:
        A dictionary containing metric score, explanation, confidence of the
        metric.
    """
    return {
        constants.MetricResult.PAIRWISE_CHOICE_KEY: metric_result_dict.get(
            constants.MetricResult.PAIRWISE_CHOICE_KEY,
        ),
        constants.MetricResult.EXPLANATION_KEY: metric_result_dict.get(
            constants.MetricResult.EXPLANATION_KEY
        ),
        constants.MetricResult.CONFIDENCE_KEY: metric_result_dict.get(
            constants.MetricResult.CONFIDENCE_KEY
        ),
    }


def handle_response(
    response: Union[str, gapic_eval_service_types.EvaluateInstancesResponse],
) -> Union[str, Dict[str, Any]]:
    """Handles the response from the evaluation service.

    Args:
        response: The response from the evaluation service.

    Returns:
        A parsed metric result dictionary, or an error message string.
    """
    if isinstance(response, str):
        return response

    metric_type = response._pb.WhichOneof("evaluation_results")

    # Automatic Metrics.
    if metric_type == constants.MetricResult.EXACT_MATCH_RESULTS:
        metric_result = response.exact_match_results
    elif metric_type == constants.MetricResult.BLEU_RESULTS:
        metric_result = response.bleu_results
    elif metric_type == constants.MetricResult.ROUGE_RESULTS:
        metric_result = response.rouge_results
    elif metric_type == constants.MetricResult.TOOL_CALL_VALID_RESULTS:
        metric_result = response.tool_call_valid_results
    elif metric_type == constants.MetricResult.TOOL_NAME_MATCH_RESULTS:
        metric_result = response.tool_name_match_results
    elif metric_type == constants.MetricResult.TOOL_PARAMETER_KEY_MATCH_RESULTS:
        metric_result = response.tool_parameter_key_match_results
    elif metric_type == constants.MetricResult.TOOL_PARAMETER_KV_MATCH_RESULTS:
        metric_result = response.tool_parameter_kv_match_results
    # Model-based Pointwise Metrics.
    elif metric_type == constants.MetricResult.COHERENCE_RESULT:
        metric_result = response.coherence_result
    elif metric_type == constants.MetricResult.FULFILLMENT_RESULT:
        metric_result = response.fulfillment_result
    elif metric_type == constants.MetricResult.FLUENCY_RESULT:
        metric_result = response.fluency_result
    elif metric_type == constants.MetricResult.SAFETY_RESULT:
        metric_result = response.safety_result
    elif metric_type == constants.MetricResult.GROUNDEDNESS_RESULT:
        metric_result = response.groundedness_result
    elif metric_type == constants.MetricResult.RESPONSE_RECALL_RESULT:
        metric_result = response.response_recall_result
    elif metric_type == constants.MetricResult.SUMMARIZATION_QUALITY_RESULT:
        metric_result = response.summarization_quality_result
    elif metric_type == constants.MetricResult.SUMMARIZATION_HELPFULNESS_RESULT:
        metric_result = response.summarization_helpfulness_result
    elif metric_type == constants.MetricResult.SUMMARIZATION_VERBOSITY_RESULT:
        metric_result = response.summarization_verbosity_result
    elif metric_type == constants.MetricResult.QUESTION_ANSWERING_QUALITY_RESULT:
        metric_result = response.question_answering_quality_result
    elif metric_type == constants.MetricResult.QUESTION_ANSWERING_RELEVANCE_RESULT:
        metric_result = response.question_answering_relevance_result
    elif metric_type == constants.MetricResult.QUESTION_ANSWERING_HELPFULNESS_RESULT:
        metric_result = response.question_answering_helpfulness_result
    elif metric_type == constants.MetricResult.QUESTION_ANSWERING_CORRECTNESS_RESULT:
        metric_result = response.question_answering_correctness_result
    elif metric_type == constants.MetricResult.RAG_CONTEXT_RECALL_RESULT:
        metric_result = response.rag_context_recall_result
    # Side-by-side(SxS) Pairwise Metrics.
    elif metric_type == constants.MetricResult.PAIRWISE_SUMMARIZATION_QUALITY_RESULT:
        metric_result = response.pairwise_summarization_quality_result
    elif (
        metric_type == constants.MetricResult.PAIRWISE_QUESTION_ANSWERING_QUALITY_RESULT
    ):
        metric_result = response.pairwise_question_answering_quality_result
    else:
        raise ValueError(f"Unknown metric type: {metric_type}")

    metric_result_dict = json_format.MessageToDict(
        metric_result._pb, preserving_proto_field_name=True
    )

    if metric_type in constants.MetricResult.AUTOMATIC_METRIC_RESULTS_LIST:
        result = _parse_autometric_results(metric_result_dict)
    elif metric_type in constants.MetricResult.MODEL_BASED_METRIC_RESULT_LIST:
        result = _parse_model_based_pointwise_results(metric_result_dict)
    elif metric_type in constants.MetricResult.PAIRWISE_METRIC_RESULT_LIST:
        result = _parse_pairwise_results(metric_result_dict)
    else:
        raise ValueError(f"Unknown metric type: {metric_type}")
    return result


def evaluate_instances(
    client: gapic_evaluation_services.EvaluationServiceClient,
    request: gapic_eval_service_types.EvaluateInstancesRequest,
    rate_limiter: utils.RateLimiter,
    retry_timeout: float,
) -> gapic_eval_service_types.EvaluateInstancesResponse:
    """Evaluates an instance.

    Args:
        client: The client to use for evaluation.
        request: An EvaluateInstancesRequest.
        rate_limiter: The rate limiter to use for evaluation service requests.
        retry_timeout: How long to keep retrying the evaluation requests, in seconds.

    Returns:
        A response from the evaluation service.
    """
    rate_limiter.sleep_and_advance()
    return client.evaluate_instances(
        request=request,
        retry=api_core.retry.Retry(
            initial=0.250,
            maximum=90.0,
            multiplier=1.45,
            timeout=retry_timeout,
            predicate=api_core.retry.if_exception_type(
                api_core.exceptions.Aborted,
                api_core.exceptions.DeadlineExceeded,
                api_core.exceptions.ResourceExhausted,
                api_core.exceptions.ServiceUnavailable,
                api_core.exceptions.Cancelled,
            ),
        ),
    )
