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
"""Utility functions for prompt optimizer."""

import json
from typing import Any, Optional, Union
from typing_extensions import TypeAlias

from pydantic import ValidationError

from . import types

try:
    import pandas as pd  # pylint: disable=g-import-not-at-top

    PandasDataFrame: TypeAlias = pd.DataFrame
except ImportError:
    pd = None
    PandasDataFrame = Any  # type: ignore[misc]


def _construct_input_prompt(
    example_df: PandasDataFrame,
    *,
    prompt_col_name: str,
    model_response_col_name: str,
    rubrics_col_name: str,
    rubrics_evaluations_col_name: str,
    target_response_col_name: str,
    system_instruction: Optional[str] = None,
) -> str:
    """Construct the input prompt for the few shot prompt optimizer."""

    all_prompts = []
    for row in example_df.to_dict(orient="records"):
        example_data = {
            "prompt": row[prompt_col_name],
            "model_response": row[model_response_col_name],
        }
        if rubrics_col_name:
            example_data["rubrics"] = row[rubrics_col_name]
        if rubrics_evaluations_col_name:
            example_data["rubrics_evaluations"] = row[rubrics_evaluations_col_name]
        if target_response_col_name:
            example_data["target_response"] = row[target_response_col_name]

        json_str = json.dumps(example_data, indent=2)
        all_prompts.append(f"```JSON\n{json_str}\n```")

    all_prompts_str = "\n\n".join(all_prompts)

    if system_instruction is None:
        system_instruction = ""

    return "\n".join(
        [
            "Original System Instructions:\n",
            system_instruction,
            "Examples:\n",
            all_prompts_str,
            "\nNew Output:\n",
        ]
    )


def _get_few_shot_prompt(
    system_instruction: str,
    config: types.OptimizeConfig,
) -> str:
    """Builds the few shot prompt."""

    if config.examples_dataframe is None:
        raise ValueError("The 'examples_dataframe' is required in the config.")

    if "prompt" not in config.examples_dataframe.columns:
        raise ValueError("'prompt' is required in the examples_dataframe.")

    if "prompt" not in config.examples_dataframe.columns:
        raise ValueError("'prompt' is required in the examples_dataframe.")
    prompt_col_name = "prompt"

    if "model_response" not in config.examples_dataframe.columns:
        raise ValueError("'model_response' is required in the example_df.")
    model_response_col_name = "model_response"

    target_response_col_name = ""
    rubrics_col_name = ""
    rubrics_evaluations_col_name = ""

    if (
        config.optimization_target
        == types.OptimizeTarget.OPTIMIZATION_TARGET_FEW_SHOT_TARGET_RESPONSE
    ):
        if "target_response" not in config.examples_dataframe.columns:
            raise ValueError("'target_response' is required in the examples_dataframe.")
        target_response_col_name = "target_response"
        if "rubrics" in config.examples_dataframe.columns:
            raise ValueError(
                "Only 'target_response' should be provided "
                "for OPTIMIZATION_TARGET_FEW_SHOT_TARGET_RESPONSE "
                "but 'rubrics' was provided."
            )

    elif (
        config.optimization_target
        == types.OptimizeTarget.OPTIMIZATION_TARGET_FEW_SHOT_RUBRICS
    ):
        if not {"rubrics", "rubrics_evaluations"}.issubset(
            config.examples_dataframe.columns
        ):
            raise ValueError(
                "rubrics and rubrics_evaluations is required in the"
                "examples_dataframe when rubrics is set."
            )

        rubrics_col_name = "rubrics"
        rubrics_evaluations_col_name = "rubrics_evaluations"
        if "target_response" in config.examples_dataframe.columns:
            raise ValueError(
                "Only 'rubrics' and 'rubrics_evaluations' should be provided "
                "for OPTIMIZATION_TARGET_FEW_SHOT_RUBRICS "
                "but target_response was provided."
            )
    else:
        raise ValueError("One of 'target_response' or 'rubrics' must be provided.")

    return _construct_input_prompt(
        config.examples_dataframe,
        prompt_col_name=prompt_col_name,
        model_response_col_name=model_response_col_name,
        rubrics_col_name=rubrics_col_name,
        rubrics_evaluations_col_name=rubrics_evaluations_col_name,
        target_response_col_name=target_response_col_name,
        system_instruction=system_instruction,
    )


def _get_service_account(
    config: types.PromptOptimizerConfigOrDict,
) -> str:
    """Get the service account from the config for the custom job."""
    if isinstance(config, dict):
        config = types.PromptOptimizerConfig.model_validate(config)

    if (
        config.service_account and config.service_account_project_number
    ):  # pytype: disable=attribute-error
        raise ValueError(
            "Only one of service_account or "
            "service_account_project_number can be provided."
        )
    elif config.service_account:  # pytype: disable=attribute-error
        return config.service_account  # pytype: disable=attribute-error
    elif config.service_account_project_number:  # pytype: disable=attribute-error
        return f"{config.service_account_project_number}-compute@developer.gserviceaccount.com"  # pytype: disable=attribute-error
    else:
        raise ValueError(
            "Either service_account or service_account_project_number " "is required."
        )


def _clean_and_parse_optimized_prompt(output_str: str) -> Optional[Any]:
    """Cleans a string response returned from the prompt optimizer endpoint.

    Args:
        output_str: The optimized prompt string containing the JSON data,
          potentially with markdown formatting like ```json ... ```.

    Returns:
        The parsed JSON data, or None if parsing fails.
    """
    lines = output_str.strip().split("\n")
    # Remove markdown delimiters
    if lines and lines[0].strip().startswith("```"):
        cleaned_string = "\n".join(lines[1:-1])
    else:
        cleaned_string = output_str

    # remove any 'json' labels if they exist on the first line.
    if cleaned_string.strip().startswith("json"):
        cleaned_string = cleaned_string.strip()[4:].strip()

    try:
        return json.loads(cleaned_string)
    except json.JSONDecodeError as e:
        # TODO(b/437144880): raise errors.ClientError here instead
        raise ValueError(
            f"Failed to parse the response from prompt optimizer endpoint. {e}"
        ) from e


def _parse(
    output_str: str,
) -> Union[
    types.prompts.ParsedResponse,
    types.prompts.ParsedResponseFewShot,
]:
    """Parses the output string from the prompt optimizer endpoint."""
    parsed_out = _clean_and_parse_optimized_prompt(output_str)
    try:
        return types.prompts.ParsedResponse(**parsed_out)
    except ValidationError:
        return types.prompts.ParsedResponseFewShot(**parsed_out)
