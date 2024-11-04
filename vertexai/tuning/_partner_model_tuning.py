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
# pylint: disable=protected-access
"""Classes for partner model tuning."""

from typing import Any, Dict, Optional

from google.cloud.aiplatform_v1beta1.types import (
    tuning_job as gca_tuning_job_types,
)
from vertexai.tuning import _tuning


def train(
    *,
    base_model: str,
    training_dataset_uri: str,
    validation_dataset_uri: Optional[str] = None,
    tuned_model_display_name: Optional[str] = None,
    hyper_parameters: Optional[Dict[str, Any]] = None,
    labels: Optional[Dict[str, str]] = None,
) -> "PartnerModelTuningJob":
    """Tunes a third party partner model.

    Args:
        base_model: The base model to tune.
        training_dataset_uri: The training dataset uri.
        validation_dataset_uri: The validation dataset uri.
        tuned_model_display_name: The display name of the
          [TunedModel][google.cloud.aiplatform.v1.Model]. The name can be up
          to 128 characters long and can consist of any UTF-8 characters.
        hyper_parameters: The hyper parameters of the tuning job.
        labels: User-defined metadata to be associated with trained models

    Returns:
        A `TuningJob` object.
    """
    partner_model_tuning_spec = gca_tuning_job_types.PartnerModelTuningSpec(
        training_dataset_uri=training_dataset_uri,
        validation_dataset_uri=validation_dataset_uri,
        hyper_parameters=hyper_parameters,
    )
    partner_model_tuning_job = PartnerModelTuningJob._create(
        base_model=base_model,
        tuning_spec=partner_model_tuning_spec,
        tuned_model_display_name=tuned_model_display_name,
        labels=labels,
    )

    return partner_model_tuning_job


class PartnerModelTuningJob(_tuning.TuningJob):
    pass
