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

from typing import Optional

from google.cloud.aiplatform_v1.types import tuning_job as gca_tuning_job_types

from vertexai.tuning import _tuning


def tune_model(
    source_model: str,
    training_data: str,
    validation_data: Optional[str] = None,
    tuned_model_display_name: Optional[str] = None,
    number_of_epochs: Optional[int] = None,
    learning_rate_multiplier: Optional[float] = None,
) -> _tuning.TuningJob:
    supervised_training_data = gca_tuning_job_types.SupervisedTuningSpec(
        training_dataset_uri=training_data,
        validation_dataset_uri=validation_data,
        hyper_parameters=gca_tuning_job_types.SupervisedHyperParameters(
            epoch_count=number_of_epochs,
            learning_rate_multiplier=learning_rate_multiplier,
        ),
    )
    return _tuning.TuningJob.submit(
        base_model=source_model,
        tuning_spec=supervised_training_data,
        tuned_model_display_name=tuned_model_display_name,
    )
