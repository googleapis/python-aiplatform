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

from typing import Dict, Literal, Optional, Union

from google.cloud.aiplatform_v1.types import (
    tuning_job as gca_tuning_job_types,
)
from vertexai import generative_models
from vertexai.tuning import _tuning


def train(
    *,
    source_model: Union[str, generative_models.GenerativeModel],
    train_dataset: str,
    validation_dataset: Optional[str] = None,
    tuned_model_display_name: Optional[str] = None,
    epochs: Optional[int] = None,
    learning_rate_multiplier: Optional[float] = None,
    adapter_size: Optional[Literal[1, 4, 8, 16]] = None,
    labels: Optional[Dict[str, str]] = None,
) -> "SupervisedTuningJob":
    """Tunes a model using supervised training.

    Args:
        source_model (str): Model name for tuning, e.g., "gemini-1.0-pro-002".
        train_dataset: Cloud Storage path to file containing training dataset for
          tuning. The dataset should be in JSONL format.
        validation_dataset: Cloud Storage path to file containing validation
          dataset for tuning. The dataset should be in JSONL format.
        tuned_model_display_name: The display name of the
          [TunedModel][google.cloud.aiplatform.v1.Model]. The name can be up to
          128 characters long and can consist of any UTF-8 characters.
        epochs: Number of training epoches for this tuning job.
        learning_rate_multiplier: Learning rate multiplier for tuning.
        adapter_size: Adapter size for tuning.
        labels: User-defined metadata to be associated with trained models

    Returns:
        A `TuningJob` object.
    """
    if adapter_size is None:
        adapter_size_value = None
    elif adapter_size == 1:
        adapter_size_value = (
            gca_tuning_job_types.SupervisedHyperParameters.AdapterSize.ADAPTER_SIZE_ONE
        )
    elif adapter_size == 4:
        adapter_size_value = (
            gca_tuning_job_types.SupervisedHyperParameters.AdapterSize.ADAPTER_SIZE_FOUR
        )
    elif adapter_size == 8:
        adapter_size_value = (
            gca_tuning_job_types.SupervisedHyperParameters.AdapterSize.ADAPTER_SIZE_EIGHT
        )
    elif adapter_size == 16:
        adapter_size_value = (
            gca_tuning_job_types.SupervisedHyperParameters.AdapterSize.ADAPTER_SIZE_SIXTEEN
        )
    else:
        raise ValueError(
            f"Unsupported adapter size: {adapter_size}. The supported sizes are [1, 4, 8, 16]"
        )
    supervised_tuning_spec = gca_tuning_job_types.SupervisedTuningSpec(
        training_dataset_uri=train_dataset,
        validation_dataset_uri=validation_dataset,
        hyper_parameters=gca_tuning_job_types.SupervisedHyperParameters(
            epoch_count=epochs,
            learning_rate_multiplier=learning_rate_multiplier,
            adapter_size=adapter_size_value,
        ),
    )

    if isinstance(source_model, generative_models.GenerativeModel):
        source_model = source_model._prediction_resource_name.rpartition("/")[-1]

    return SupervisedTuningJob._create(  # pylint: disable=protected-access
        base_model=source_model,
        tuning_spec=supervised_tuning_spec,
        tuned_model_display_name=tuned_model_display_name,
        labels=labels,
    )


class SupervisedTuningJob(_tuning.TuningJob):
    pass
