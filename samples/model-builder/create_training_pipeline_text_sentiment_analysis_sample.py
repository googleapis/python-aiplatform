# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional

from google.cloud import aiplatform


#  [START aiplatform_sdk_create_training_pipeline_text_sentiment_analysis_sample]
def create_training_pipeline_text_sentiment_analysis_sample(
    project: str,
    location: str,
    display_name: str,
    dataset_id: int,
    model_display_name: Optional[str] = None,
    sentiment_max: int = 10,
    training_fraction_split: float = 0.8,
    validation_fraction_split: float = 0.1,
    test_fraction_split: float = 0.1,
    budget_milli_node_hours: int = 8000,
    disable_early_stopping: bool = False,
    sync: bool = True,
):
    aiplatform.init(project=project, location=location)

    job = aiplatform.AutoMLTextTrainingJob(
        display_name=display_name,
        prediction_type="sentiment",
        sentiment_max=sentiment_max,
    )

    text_dataset = aiplatform.TextDataset(dataset_id)

    model = job.run(
        dataset=text_dataset,
        model_display_name=model_display_name,
        training_fraction_split=training_fraction_split,
        validation_fraction_split=validation_fraction_split,
        test_fraction_split=test_fraction_split,
        budget_milli_node_hours=budget_milli_node_hours,
        disable_early_stopping=disable_early_stopping,
        sync=sync,
    )

    model.wait()

    print(model.display_name)
    print(model.resource_name)
    print(model.uri)
    return model


#  [END aiplatform_sdk_create_training_pipeline_text_sentiment_analysis_sample]
