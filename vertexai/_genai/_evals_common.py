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
"""Common utilities for evals."""
import concurrent.futures
import json
import logging
import os
import time
from typing import Any, Callable, Literal, Optional, Union

from google.api_core import exceptions as api_exceptions
from google.genai import types as genai_types
from google.genai._api_client import BaseApiClient
from google.genai.models import Models
import pandas as pd
from tqdm import tqdm

from . import _evals_data_converters
from . import _evals_metric_handlers
from . import _evals_utils
from . import evals
from . import types

logger = logging.getLogger(__name__)

MAX_WORKERS = 100


def _generate_content_with_retry(
    api_client: BaseApiClient,
    model: str,
    contents: Union[genai_types.ContentListUnion, genai_types.ContentListUnionDict],
    config: Optional[genai_types.GenerateContentConfig] = None,
    max_retries: int = 3,
) -> Union[genai_types.GenerateContentResponse, dict[str, Any]]:
    """Generates content using the model's generate_content with retries."""
    models_module = Models(api_client_=api_client)

    for attempt in range(max_retries):
        try:
            response = models_module.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            if not response.candidates:
                logger.warning(
                    "Prompt blocked. Attempt %d/%d. Feedback: %s. Prompt: %s.",
                    attempt + 1,
                    max_retries,
                    response.prompt_feedback,
                    contents,
                )
                if attempt == max_retries - 1:
                    feedback_dict = {}
                    if response.prompt_feedback:
                        feedback_dict = response.prompt_feedback.model_dump(
                            mode="json", exclude_none=True
                        )
                    return {
                        "error": "Prompt blocked after retries",
                        "prompt_feedback": feedback_dict,
                    }
            else:
                candidate = response.candidates[0]
                if candidate.finish_reason not in (
                    genai_types.FinishReason.STOP,
                    genai_types.FinishReason.MAX_TOKENS,
                    genai_types.FinishReason.FINISH_REASON_UNSPECIFIED,
                ):
                    logger.warning(
                        "Generate content did not finish successfully."
                        "Finish reason: %s. Finish message: %s."
                        "Retry attempt: %d/%d",
                        candidate.finish_reason,
                        candidate.finish_message,
                        attempt + 1,
                        max_retries,
                    )
                    if attempt == max_retries - 1:
                        return {
                            "error": (
                                "Generate content unsuccessful after retries:"
                                f" {candidate.finish_reason}"
                            ),
                            "finish_reason": str(candidate.finish_reason),
                            "finish_message": candidate.finish_message or "",
                        }
                else:
                    return response
        except api_exceptions.ResourceExhausted as e:
            logger.warning(
                "Resource Exhausted error on attempt %d/%d: %s. Retrying in %s"
                " seconds...",
                attempt + 1,
                max_retries,
                e,
                2**attempt,
            )
            if attempt == max_retries - 1:
                return {"error": f"Resource exhausted after retries: {e}"}
            time.sleep(2**attempt)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Unexpected error during generate_content on attempt %d/%d: %s",
                attempt + 1,
                max_retries,
                e,
            )

            if attempt == max_retries - 1:
                return {"error": f"Failed after retries: {e}"}
            time.sleep(1)
    return {"error": f"Failed to generate content after {max_retries} retries"}


def _build_generate_content_config(
    request_dict: dict[str, Any],
    global_config: Optional[genai_types.GenerateContentConfig] = None,
) -> genai_types.GenerateContentConfig:
    """Builds a GenerateContentConfig from the request dictionary or provided config."""
    if global_config:
        # If a global config is provided, apply it as a base config. Parts of
        # the global config can be overridden by providing configs in the
        # request.
        merged_config_dict = global_config.model_dump(exclude_none=True)
    else:
        merged_config_dict = {}

    for key in [
        "system_instruction",
        "tools",
        "tools_config",
        "safety_settings",
        "labels",
    ]:
        if key in request_dict:
            merged_config_dict[key] = request_dict[key]
    if "generation_config" in request_dict and isinstance(
        request_dict["generation_config"], dict
    ):
        merged_config_dict.update(request_dict["generation_config"])
    if "labels" in request_dict:
        merged_config_dict["labels"] = request_dict["labels"]

    return genai_types.GenerateContentConfig(**merged_config_dict)


def _extract_contents_for_inference(
    request_dict_or_raw_text: Any,
) -> Any:
    """Extracts contents from a request dictionary or returns the raw text."""
    if not request_dict_or_raw_text:
        raise ValueError("Prompt cannot be empty.")
    if isinstance(request_dict_or_raw_text, dict):
        contents_for_fn = request_dict_or_raw_text.get("contents", None)
        if not contents_for_fn:
            raise ValueError("Contents in the request cannot be empty.")
        return contents_for_fn
    else:
        return request_dict_or_raw_text


def _execute_inference_concurrently(
    api_client: BaseApiClient,
    model_or_fn: Union[str, Callable[[Any], Any]],
    prompt_dataset: pd.DataFrame,
    progress_desc: str,
    gemini_config: Optional[genai_types.GenerateContentConfig] = None,
    inference_fn: Optional[Callable[[Any, Any, Any, Any], Any]] = None,
) -> list[Union[genai_types.GenerateContentResponse, dict[str, Any]]]:
    """Internal helper to run inference with concurrency."""
    logger.info(
        "Generating responses for %d prompts using model or function: %s",
        len(prompt_dataset),
        model_or_fn,
    )
    responses: list[
        Union[genai_types.GenerateContentResponse, dict[str, Any], None]
    ] = [None] * len(prompt_dataset)
    tasks = []

    primary_prompt_column = (
        "request" if "request" in prompt_dataset.columns else "prompt"
    )
    if primary_prompt_column not in prompt_dataset.columns:
        raise ValueError(
            "Dataset must contain either 'prompt' or 'request'."
            f" Found: {prompt_dataset.columns.tolist()}"
        )

    with tqdm(total=len(prompt_dataset), desc=progress_desc) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for index, row in prompt_dataset.iterrows():
                request_dict_or_raw_text = row[primary_prompt_column]
                try:
                    contents = _extract_contents_for_inference(request_dict_or_raw_text)
                except ValueError as e:
                    error_message = (
                        f"Failed to extract contents for prompt at index {index}: {e}. "
                        "Skipping prompt."
                    )
                    logger.error(error_message)
                    responses[index] = {"error": error_message}
                    pbar.update(1)
                    continue

                if isinstance(model_or_fn, str):
                    generation_content_config = _build_generate_content_config(
                        request_dict_or_raw_text,
                        gemini_config,
                    )
                    future = executor.submit(
                        inference_fn,
                        api_client=api_client,
                        model=model_or_fn,
                        contents=contents,
                        config=generation_content_config,
                    )
                else:
                    future = executor.submit(model_or_fn, contents)
                future.add_done_callback(lambda _: pbar.update(1))
                tasks.append((future, index))

            for future, index in tasks:
                try:
                    result = future.result()
                    responses[index] = result
                except Exception as e:
                    logger.error(
                        "Error processing prompt at index %d: %s",
                        index,
                        e,
                    )
                    responses[index] = {"error": f"Inference task failed: {e}"}
    return responses


def _run_gemini_inference(
    api_client: BaseApiClient,
    model: str,
    prompt_dataset: pd.DataFrame,
    config: Optional[genai_types.GenerateContentConfig] = None,
) -> list[Union[genai_types.GenerateContentResponse, dict[str, Any]]]:
    """Internal helper to run inference using Gemini model with concurrency."""
    return _execute_inference_concurrently(
        api_client=api_client,
        model_or_fn=model,
        prompt_dataset=prompt_dataset,
        progress_desc="Gemini Inference",
        gemini_config=config,
        inference_fn=_generate_content_with_retry,
    )


def _run_custom_inference(
    model_fn: Callable[[Any], Any],
    prompt_dataset: pd.DataFrame,
) -> list[Any]:
    """Internal helper to run inference using a custom function with concurrency."""
    return _execute_inference_concurrently(
        api_client=None,
        model_or_fn=model_fn,
        prompt_dataset=prompt_dataset,
        progress_desc="Custom Inference",
    )


def _run_inference_internal(
    api_client: BaseApiClient,
    model: Union[Callable[[Any], Any], str],
    prompt_dataset: pd.DataFrame,
    config: Optional[genai_types.GenerateContentConfig] = None,
) -> pd.DataFrame:
    """Runs inference on a given dataset using the specified model or function."""

    if isinstance(model, str):
        logger.info("Running inference with model name: %s", model)
        raw_responses = _run_gemini_inference(
            api_client=api_client,
            model=model,
            prompt_dataset=prompt_dataset,
            config=config,
        )
        processed_responses = []
        for resp_item in raw_responses:
            if isinstance(resp_item, genai_types.GenerateContentResponse):
                text_response = resp_item.text
                processed_responses.append(
                    text_response
                    if text_response is not None
                    else json.dumps({"error": "Empty response text"})
                )
            elif isinstance(resp_item, dict) and "error" in resp_item:
                processed_responses.append(json.dumps(resp_item))
            else:
                error_payload = {
                    "error": "Unexpected response type from Gemini inference",
                    "response_type": str(type(resp_item)),
                    "details": str(resp_item),
                }
                processed_responses.append(json.dumps(error_payload))
        responses = processed_responses

    elif callable(model):
        logger.info("Running inference with custom callable function.")
        custom_responses_raw = _run_custom_inference(
            model_fn=model, prompt_dataset=prompt_dataset
        )
        processed_custom_responses = []
        for resp_item in custom_responses_raw:
            if isinstance(resp_item, str):
                processed_custom_responses.append(resp_item)
            elif isinstance(resp_item, dict) and "error" in resp_item:
                processed_custom_responses.append(json.dumps(resp_item))
            else:
                try:
                    processed_custom_responses.append(json.dumps(resp_item))
                except TypeError:
                    processed_custom_responses.append(str(resp_item))
        responses = processed_custom_responses
    else:
        raise TypeError(
            f"Unsupported model type: {type(model)}. Expecting string (model"
            " name) or Callable."
        )

    if len(responses) != len(prompt_dataset):
        raise RuntimeError(
            "Critical prompt/response count mismatch: %d prompts vs %d"
            " responses. This indicates an issue in response collection."
            % (len(prompt_dataset), len(responses))
        )

    results_df_responses_only = pd.DataFrame(
        {
            "response": responses,
        }
    )

    prompt_dataset_indexed = prompt_dataset.reset_index(drop=True)
    results_df_responses_only_indexed = results_df_responses_only.reset_index(drop=True)

    results_df = pd.concat(
        [prompt_dataset_indexed, results_df_responses_only_indexed], axis=1
    )

    return results_df


def _apply_prompt_template(
    df: pd.DataFrame, prompt_template: types.PromptTemplate
) -> None:
    """Applies a prompt template to a DataFrame.

    The DataFrame is expected to have columns corresponding to the variables
    in the prompt_template_str. The result will be in a new 'request' column.

    Args:
        df: The input DataFrame to modify.
        prompt_template: The prompt template to apply.

    Returns:
        None. The DataFrame is modified in place.
    """
    missing_vars = [var for var in prompt_template.variables if var not in df.columns]
    if missing_vars:
        raise ValueError(
            "Missing columns in DataFrame for prompt template variables:"
            f" {', '.join(missing_vars)}. Available columns:"
            f" {', '.join(df.columns.tolist())}"
        )

    if "prompt" in df.columns:
        logger.info(
            "Templated prompts stored in 'request' and will be used for"
            " inference.Original 'prompt' column is kept but not used for"
            " inference."
        )
    elif "prompt" not in df.columns and "request" in df.columns:
        logger.info("The 'request' column will be replaced with templated prompts.")

    templated_prompts = []
    for _, row in df.iterrows():
        templated_prompts.append(prompt_template.assemble(**row.to_dict()))

    df["request"] = templated_prompts


def _load_dataframe(
    api_client: BaseApiClient, src: Union[str, pd.DataFrame]
) -> pd.DataFrame:
    """Loads and prepares the prompt dataset for inference."""
    logger.info("Loading prompt dataset from: %s", src)
    try:
        loader = _evals_utils.EvalDatasetLoader(api_client=api_client)
        dataset_list_of_dicts = loader.load(src)
        if not dataset_list_of_dicts:
            raise ValueError("Prompt dataset 'prompt_dataset' must not be empty.")
        return pd.DataFrame(dataset_list_of_dicts)
    except Exception as e:
        logger.error("Failed to load prompt dataset from source: %s. Error: %s", src, e)
        raise e


def _execute_inference(
    *,
    api_client: BaseApiClient,
    model: Union[Callable[[Any], Any], str],
    src: Union[str, pd.DataFrame],
    dest: Optional[str] = None,
    config: Optional[genai_types.GenerateContentConfig] = None,
    prompt_template: Optional[Union[str, types.PromptTemplateOrDict]] = None,
) -> pd.DataFrame:
    """Executes inference on a given dataset using the specified model.

    Args:
        api_client: The API client.
        model: The model to use for inference. Can be a callable function or a
          string representing a model.
        src: The source of the dataset to use for inference. Can be a string
          representing a file path or a pandas DataFrame.
        dest: The destination to save the inference results. Can be a string
          representing a file path or a GCS URI.
        config: The generation configuration for the model.
        prompt_template: The prompt template to use for inference.

    Returns:
        A pandas DataFrame containing the inference results.
    """

    if not api_client:
        raise ValueError("'api_client' instance must be provided.")
    prompt_dataset = _load_dataframe(api_client, src)

    if prompt_template:
        logger.info("Applying prompt template...")
        if isinstance(prompt_template, str):
            prompt_template = types.PromptTemplate(text=prompt_template)
        elif isinstance(prompt_template, dict):
            prompt_template = types.PromptTemplate.model_validate(prompt_template)

        _apply_prompt_template(prompt_dataset, prompt_template)

    if (
        "prompt" not in prompt_dataset.columns
        and "request" not in prompt_dataset.columns
    ):
        raise ValueError(
            "Dataset must contain either 'prompt' or 'request' "
            "column for inference after any templating. "
            f"Found columns: {prompt_dataset.columns.tolist()}"
        )

    start_time = time.time()
    logger.debug("Starting inference process ...")
    results_df = _run_inference_internal(
        api_client=api_client,
        model=model,
        prompt_dataset=prompt_dataset,
        config=config,
    )
    end_time = time.time()
    logger.info("Inference completed in %.2f seconds.", end_time - start_time)

    if dest:
        file_name = "inference_results.jsonl"
        full_dest_path = dest
        is_gcs_path = dest.startswith(_evals_utils.GCS_PREFIX)

        if is_gcs_path:
            if not dest.endswith("/"):
                pass
            else:
                full_dest_path = os.path.join(dest, file_name)
        else:
            if os.path.isdir(dest):
                full_dest_path = os.path.join(dest, file_name)

            os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)

        logger.info("Saving inference results to: %s", full_dest_path)
        try:
            if is_gcs_path:
                _evals_utils.GcsUtils(api_client=api_client).upload_dataframe(
                    df=results_df,
                    gcs_destination_blob_path=full_dest_path,
                    file_type="jsonl",
                )
                logger.info("Results saved to GCS: %s", full_dest_path)
            else:
                results_df.to_json(full_dest_path, orient="records", lines=True)
                logger.info("Results saved locally to: %s", full_dest_path)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to save results to %s. Error: %s", full_dest_path, e)

    return types.EvaluationDataset(eval_dataset_df=results_df)


def _get_dataset_source(
    ds_item: types.EvaluationDataset,
) -> Union[str, pd.DataFrame]:
    """Returns the source of the dataset, either a DataFrame, GCS URI, or BigQuery URI."""
    if ds_item.eval_dataset_df is not None:
        return ds_item.eval_dataset_df
    elif ds_item.gcs_source is not None and ds_item.gcs_source.uris:
        if len(ds_item.gcs_source.uris) > 1:
            logger.warning(
                "Multiple GCS URIs in GcsSource. Using the first one: %s",
                ds_item.gcs_source.uris[0],
            )
        return ds_item.gcs_source.uris[0]
    elif ds_item.bigquery_source is not None and ds_item.bigquery_source.input_uri:
        return ds_item.bigquery_source.input_uri
    else:
        raise ValueError(
            "EvaluationDataset item has no valid source"
            " (eval_dataset_df, gcs_source with uris, or bigquery_source with"
            " input_uri)."
        )


def _resolve_dataset_inputs(
    dataset: list[types.EvaluationDataset],
    dataset_schema: Optional[Literal["gemini", "flatten"]],
    loader: _evals_utils.EvalDatasetLoader,
) -> tuple[types.EvaluationDataset, int]:
    """Loads and processes single or multiple datasets for evaluation.

    Args:
      dataset: The dataset(s) to process. Can be a single EvaluationDataset or a
        list of them.
      dataset_schema: The schema to use for the dataset(s). If None, it will be
        auto-detected.
      loader: An instance of EvalDatasetLoader to load data.

    Returns:
      A tuple containing:
        - processed_eval_dataset: The processed EvaluationDataset containing
        evaluation cases.
        - num_response_candidates: The number of response candidates.
    """
    if not dataset:
        raise ValueError("Input dataset list cannot be empty.")

    num_response_candidates = len(dataset)
    datasets_to_process = dataset
    logger.info("Processing %s dataset(s).", num_response_candidates)

    loaded_raw_datasets: list[list[dict[str, Any]]] = []
    schemas_for_merge: list[str] = []

    for i, ds_item in enumerate(datasets_to_process):
        if not isinstance(ds_item, types.EvaluationDataset):
            logger.error(
                "Unexpected item type in dataset list at index %d: %s. Expected"
                " types.EvaluationDataset.",
                i,
                type(ds_item),
            )
            raise TypeError(
                f"Item at index {i} is not an EvaluationDataset: {type(ds_item)}"
            )

        ds_source_for_loader = _get_dataset_source(ds_item)
        current_loaded_data = loader.load(ds_source_for_loader)
        loaded_raw_datasets.append(current_loaded_data)

        if dataset_schema:
            current_schema = _evals_data_converters.EvalDatasetSchema[dataset_schema]
        else:
            current_schema = _evals_data_converters.auto_detect_dataset_schema(
                current_loaded_data
            )
        schemas_for_merge.append(current_schema)

        logger.info(
            "Dataset %d: Schema: %s. Using %s converter.",
            i,
            current_schema,
            _evals_data_converters.get_dataset_converter(
                current_schema
            ).__class__.__name__,
        )

    processed_eval_dataset = (
        _evals_data_converters.merge_response_datasets_into_canonical_format(
            raw_datasets=loaded_raw_datasets, schemas=schemas_for_merge
        )
    )

    if not processed_eval_dataset.eval_cases:
        raise ValueError("No evaluation cases found in the dataset.")
    return processed_eval_dataset, num_response_candidates


def _resolve_metrics(
    metrics: list[types.Metric], api_client: Any
) -> list[types.Metric]:
    """Resolves a list of metric instances, loading prebuilt metrics if necessary."""
    resolved_metrics_list = []
    for metric_instance in metrics:
        if isinstance(metric_instance, _evals_utils.LazyLoadedPrebuiltMetric):
            try:
                resolved_metrics_list.append(
                    metric_instance.resolve(api_client=api_client)
                )
            except Exception as e:
                logger.error(
                    "Failed to resolve prebuilt metric %s@%s: %s",
                    metric_instance.name,
                    metric_instance.version,
                    e,
                )
                raise
        elif isinstance(metric_instance, types.Metric):
            resolved_metrics_list.append(metric_instance)
        else:
            try:
                metric_name_str = str(metric_instance)
                lazy_metric_instance = getattr(
                    _evals_utils.PrebuiltMetric, metric_name_str.upper()
                )
                if isinstance(
                    lazy_metric_instance, _evals_utils.LazyLoadedPrebuiltMetric
                ):
                    resolved_metrics_list.append(
                        lazy_metric_instance.resolve(api_client=api_client)
                    )
                else:
                    raise TypeError(
                        f"PrebuiltMetric.{metric_name_str.upper()} did not return a"
                        " LazyLoadedPrebuiltMetric proxy."
                    )
            except AttributeError as exc:
                raise TypeError(
                    "Unsupported metric type or invalid prebuilt metric name:"
                    f" {metric_instance}"
                ) from exc
    return resolved_metrics_list


def _execute_evaluation(
    *,
    api_client: Any,
    dataset: Union[types.EvaluationDataset, list[types.EvaluationDataset]],
    metrics: list[types.Metric],
    dataset_schema: Optional[Literal["gemini", "flatten"]] = None,
    dest: Optional[str] = None,
) -> types.EvaluationResult:
    """Evaluates a dataset using the provided metrics.

    Args:
        api_client: The API client.
        dataset: The dataset to evaluate.
        metrics: The metrics to evaluate the dataset against.
        dataset_schema: The schema of the dataset.
        dest: The destination to save the evaluation results.

    Returns:
        The evaluation result.
    """

    logger.info("Preparing dataset(s) and metrics...")

    if isinstance(dataset, types.EvaluationDataset):
        dataset_list = [dataset]
    elif isinstance(dataset, list):
        for item in dataset:
            if not isinstance(item, types.EvaluationDataset):
                raise TypeError(
                    f"Unsupported dataset type: {type(item)}. "
                    "Must be EvaluationDataset."
                )
        dataset_list = dataset
    else:
        raise TypeError(
            f"Unsupported dataset type: {type(dataset)}. Must be an"
            " EvaluationDataset or a list of EvaluationDataset."
        )

    loader = _evals_utils.EvalDatasetLoader(api_client=api_client)
    processed_eval_dataset, num_response_candidates = _resolve_dataset_inputs(
        dataset=dataset_list, dataset_schema=dataset_schema, loader=loader
    )

    resolved_metrics = _resolve_metrics(metrics, api_client)

    evaluation_run_config = _evals_metric_handlers.EvaluationRunConfig(
        evals_module=evals.Evals(api_client_=api_client),
        dataset=processed_eval_dataset,
        metrics=resolved_metrics,
        num_response_candidates=num_response_candidates,
    )

    logger.info("Running Metric Computation...")
    t1 = time.perf_counter()
    evaluation_result = _evals_metric_handlers.compute_metrics_and_aggregate(
        evaluation_run_config
    )
    t2 = time.perf_counter()
    logger.info("Evaluation took: %f seconds", t2 - t1)

    evaluation_result.evaluation_dataset = dataset_list
    logger.info("Evaluation run completed.")

    if dest:
        uploaded_path = _evals_utils.GcsUtils(
            api_client=api_client
        ).upload_json_to_prefix(
            data=evaluation_result.model_dump(
                mode="json",
                exclude_none=True,
                exclude={"evaluation_dataset"},
            ),
            gcs_dest_prefix=dest,
            filename_prefix="evaluation_result",
        )
        logger.info(
            "Evaluation results uploaded successfully to GCS: %s", uploaded_path
        )
    return evaluation_result
