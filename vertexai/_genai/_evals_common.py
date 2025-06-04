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
from typing import Any, Callable, Optional, Union

from google.api_core import exceptions as api_exceptions
from google.genai import types as genai_types
from google.genai._api_client import BaseApiClient
from google.genai.models import Models
import pandas as pd
from tqdm import tqdm

from . import _evals_utils
from . import types

logger = logging.getLogger(__name__)

_MAX_WORKERS = 100


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
    config: Optional[genai_types.GenerateContentConfig] = None,
) -> genai_types.GenerateContentConfig:
    """Builds a GenerateContentConfig from the request dictionary or provided config."""
    if config:
        # If a global config is provided, use it.
        # User can still override parts of it if request_dict contains config fields.
        merged_config_dict = config.model_dump(exclude_none=True)
    else:
        merged_config_dict = {}

    # Overlay or set fields from request_dict
    if "system_instruction" in request_dict:
        merged_config_dict["system_instruction"] = request_dict["system_instruction"]
    if "tools" in request_dict:
        merged_config_dict["tools"] = request_dict["tools"]
    if "tools_config" in request_dict:  # Corrected variable name
        merged_config_dict["tools_config"] = request_dict["tools_config"]
    if "safety_settings" in request_dict:
        merged_config_dict["safety_settings"] = request_dict["safety_settings"]
    if "generation_config" in request_dict and isinstance(
        request_dict["generation_config"], dict
    ):
        # Merge generation_config dict into the main config dict
        merged_config_dict.update(request_dict["generation_config"])
    if "labels" in request_dict:
        merged_config_dict["labels"] = request_dict["labels"]

    return genai_types.GenerateContentConfig(**merged_config_dict)


def _run_gemini_inference(
    api_client: BaseApiClient,
    model: str,
    prompt_dataset: "pd.DataFrame",
    config: Optional[genai_types.GenerateContentConfig] = None,
) -> list[Union[genai_types.GenerateContentResponse, dict[str, Any]]]:
    """Internal helper to run inference using Gemini model with concurrency."""
    logger.info(
        "Generating responses for %d prompts using model: %s",
        len(prompt_dataset),
        model,
    )
    responses: list[
        Union[genai_types.GenerateContentResponse, dict[str, Any], None]
    ] = [None] * len(prompt_dataset)
    tasks = []

    # Determine the primary column for prompts
    primary_prompt_column = (
        "request" if "request" in prompt_dataset.columns else "prompt"
    )
    if primary_prompt_column not in prompt_dataset.columns:
        raise ValueError(
            "Dataset must contain either 'prompt' or 'request'."
            f" Found: {prompt_dataset.columns.tolist()}"
        )

    with tqdm(total=len(prompt_dataset), desc="Gemini Inference") as pbar:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=_MAX_WORKERS
        ) as executor:
            for index, row in prompt_dataset.iterrows():
                request_dict = {}
                contents_input = row[primary_prompt_column]

                if isinstance(contents_input, str):
                    try:
                        # Attempt to parse if it's a JSON string representing a complex request
                        parsed_json = json.loads(contents_input)
                        if isinstance(parsed_json, dict):
                            request_dict = parsed_json
                            contents = request_dict.get("contents", None)
                            if (
                                contents is None
                            ):  # If 'contents' not in JSON, assume whole string was the content
                                contents = contents_input
                        else:  # Parsed to something other than dict (e.g. just a string literal in JSON)
                            contents = contents_input
                    except json.JSONDecodeError:
                        # It's a raw text prompt string
                        contents = contents_input
                elif isinstance(contents_input, dict) or isinstance(
                    contents_input, list
                ):
                    # Already in a structure that could be 'contents' or part of a larger request
                    contents = contents_input  # Assume this is the 'contents' part
                    # To extract other configs, we'd need a clearer contract on how full requests are passed in rows
                    # For now, assume if it's dict/list, it's directly the 'contents'
                else:
                    logger.error(
                        f"Unsupported type for prompt/request column at index {index}:"
                        f" {type(contents_input)}"
                    )
                    responses[index] = {
                        "error": (
                            f"Unsupported prompt/request type: {type(contents_input)}"
                        )
                    }
                    pbar.update(1)
                    continue

                if contents is None:
                    logger.error(
                        f"Could not extract 'contents' for inference at index {index}."
                        f" Row data: {row[primary_prompt_column]}"
                    )
                    responses[index] = {
                        "error": "Could not extract 'contents' for inference."
                    }
                    pbar.update(1)
                    continue

                generation_content_config = _build_generate_content_config(
                    request_dict,
                    config,
                )
                future = executor.submit(
                    _generate_content_with_retry,
                    api_client=api_client,
                    model=model,
                    contents=contents,
                    config=generation_content_config,
                )
                future.add_done_callback(lambda _: pbar.update(1))
                tasks.append((future, index))

            for future, index in tasks:
                try:
                    result = future.result()
                    responses[index] = result
                except Exception as e:
                    logger.error("Error processing prompt at index %d: %s", index, e)
                    responses[index] = {"error": f"Gemini Inference task failed: {e}"}
    return responses


def _run_custom_inference(
    model_fn: Callable[[Any], Any],
    prompt_dataset: pd.DataFrame,
) -> list[Any]:
    """Internal helper to run inference using a custom function with concurrency."""
    logger.info(
        "Generating responses for %d prompts using custom function.",
        len(prompt_dataset),
    )
    responses: list[Union[Any, None]] = [None] * len(prompt_dataset)
    tasks = []

    # Determine the primary column for prompts
    if "prompt" in prompt_dataset.columns:
        primary_prompt_column = "prompt"
    elif "request" in prompt_dataset.columns:
        primary_prompt_column = "request"
    else:
        raise ValueError("Dataset must contain either 'prompt' or 'request'.")

    with tqdm(total=len(prompt_dataset), desc="Custom Inference") as pbar:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=_MAX_WORKERS
        ) as executor:
            for index, row in prompt_dataset.iterrows():
                contents_input = row[primary_prompt_column]

                # For custom functions, we pass the content as is, assuming the function knows how to handle it.
                if isinstance(contents_input, str):
                    try:
                        maybe_json = json.loads(contents_input)
                        # If it's a dict and has 'contents', pass that, else pass the parsed object
                        if isinstance(maybe_json, dict) and "contents" in maybe_json:
                            contents_for_fn = maybe_json["contents"]
                        else:
                            contents_for_fn = maybe_json
                    except json.JSONDecodeError:
                        contents_for_fn = contents_input  # Pass as string
                else:
                    contents_for_fn = contents_input

                future = executor.submit(model_fn, contents_for_fn)
                future.add_done_callback(lambda _: pbar.update(1))
                tasks.append((future, index))

            for future, index in tasks:
                try:
                    result = future.result()
                    responses[index] = result
                except Exception as e:
                    logger.error("Error processing prompt at index %d: %s", index, e)
                    responses[index] = {"error": f"Custom Inference task failed: {e}"}
    return responses


def _load_dataframe(
    api_client: BaseApiClient, src: Union[str, pd.DataFrame]
) -> pd.DataFrame:
    """Loads and prepares the prompt dataset for inference."""
    logger.info("Loading prompt dataset from: %s", src)
    try:
        loader = _evals_utils.EvalDatasetLoader(api_client=api_client)
        dataset_list_of_dicts = loader.load(src)
        df = pd.DataFrame(dataset_list_of_dicts)
    except Exception as e:
        logger.error("Failed to load prompt dataset from source: %s. Error: %s", src, e)
        raise e
    return df


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


def _run_inference_internal(
    api_client: BaseApiClient,
    model: Union[Callable[[Any], Any], str],
    prompt_dataset: pd.DataFrame,
    dest: Optional[str] = None,
    config: Optional[genai_types.GenerateContentConfig] = None,
) -> pd.DataFrame:
    """Runs inference on a given dataset using the specified model or function."""
    start_time = time.time()
    logger.debug("Starting inference process ...")

    if prompt_dataset.empty:
        raise ValueError("Prompt dataset 'prompt_dataset' must not be empty.")

    if isinstance(model, str):
        logger.info("Running inference with model name: %s", model)
        responses_raw = _run_gemini_inference(
            api_client=api_client,
            model=model,
            prompt_dataset=prompt_dataset,
            config=config,
        )
        processed_responses = []
        for resp_item in responses_raw:
            if isinstance(resp_item, genai_types.GenerateContentResponse):
                # Ensure text is not None, provide a default or specific error representation
                text_response = resp_item.text
                processed_responses.append(
                    text_response
                    if text_response is not None
                    else json.dumps({"error": "Empty response text"})
                )
            elif isinstance(resp_item, dict) and "error" in resp_item:
                processed_responses.append(json.dumps(resp_item))
            else:  # Fallback for other unexpected types or structures
                error_payload = {
                    "error": "Unexpected response type from Gemini inference",
                    "response_type": str(type(resp_item)),
                }
                if hasattr(resp_item, "model_dump_json"):  # For Pydantic models
                    error_payload["details"] = resp_item.model_dump_json()
                elif isinstance(resp_item, (dict, list)):
                    error_payload["details"] = json.dumps(resp_item)
                else:
                    error_payload["details"] = str(resp_item)
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
                    # Attempt to serialize other types to JSON string
                    processed_custom_responses.append(json.dumps(resp_item))
                except TypeError:
                    # If not serializable, convert to string
                    processed_custom_responses.append(str(resp_item))
        responses = processed_custom_responses
    else:
        raise TypeError(
            f"Unsupported model type: {type(model)}. Expecting string (model"
            " name) or Callable."
        )

    if len(prompt_dataset) != len(responses):
        # This should ideally not happen if responses list is pre-allocated and filled
        logger.error(
            "Critical prompt/response count mismatch: %d prompts vs %d responses."
            " This indicates an issue in response collection.",
            len(prompt_dataset),
            len(responses),
        )
        # Pad responses with error messages if lengths mismatch, to allow DataFrame creation
        if len(responses) < len(prompt_dataset):
            responses.extend(
                [json.dumps({"error": "Missing response"})]
                * (len(prompt_dataset) - len(responses))
            )
        else:
            responses = responses[: len(prompt_dataset)]

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

    end_time = time.time()
    logger.info("Inference completed in %.2f seconds.", end_time - start_time)
    return results_df


def _execute_inference(
    *,
    api_client: BaseApiClient,
    model: Union[Callable[[Any], Any], str],
    src: Union[str, pd.DataFrame],
    dest: Optional[str] = None,
    config: Optional[genai_types.GenerateContentConfig] = None,
    prompt_template: Optional[Union[str, types.PromptTemplateOrDict]] = None,
) -> pd.DataFrame:
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

    results_df = _run_inference_internal(
        api_client=api_client,
        model=model,
        prompt_dataset=prompt_dataset,
        dest=dest,
        config=config,
    )

    return results_df
