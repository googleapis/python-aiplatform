# Copyright 2020 Google LLC
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

def make_parent(parent: str) -> str:
    # Sample function parameter parent in create_training_pipeline_video_classification_sample
    parent = parent

    return parent

def make_training_pipeline(display_name: str, dataset_id: str, model_display_name: str) -> google.cloud.aiplatform_v1alpha1.types.training_pipeline.TrainingPipeline:
    training_task_inputs_dict = {
        "modelType": "CLOUD"
    }
    training_task_inputs = to_protobuf_value(training_task_inputs_dict)

    training_pipeline = {
        'display_name': display_name,
        'training_task_definition': "gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_video_object_tracking_1.0.0.yaml",
        'training_task_inputs': training_task_inputs,
        'input_data_config': {
            'dataset_id': dataset_id
        },
        'model_to_upload': {
            'display_name': model_display_name
        }
    }

    return training_pipeline

