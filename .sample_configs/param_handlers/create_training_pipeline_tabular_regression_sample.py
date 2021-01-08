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
    parent = parent

    return parent

def make_training_pipeline(display_name: str, dataset_id: str, model_display_name: str, target_column: str) -> google.cloud.aiplatform_v1alpha1.types.training_pipeline.TrainingPipeline:
    # set the columns used for training and their data types
    transformations = [
        {"auto": {"column_name": "STRING_5000unique_NULLABLE"}},
        {"auto": {"column_name": "INTEGER_5000unique_NULLABLE"}},
        {"auto": {"column_name": "FLOAT_5000unique_NULLABLE"}},
        {"auto": {"column_name": "FLOAT_5000unique_REPEATED"}},
        {"auto": {"column_name": "NUMERIC_5000unique_NULLABLE"}},
        {"auto": {"column_name": "BOOLEAN_2unique_NULLABLE"}},
        {"timestamp": {"column_name": "TIMESTAMP_1unique_NULLABLE", "invalid_values_allowed": True}},
        {"auto": {"column_name": "DATE_1unique_NULLABLE"}},
        {"auto": {"column_name": "TIME_1unique_NULLABLE"}},
        {"timestamp": {"column_name": "DATETIME_1unique_NULLABLE", "invalid_values_allowed": True}},
        {"auto": {"column_name": "STRUCT_NULLABLE.STRING_5000unique_NULLABLE"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.INTEGER_5000unique_NULLABLE"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.FLOAT_5000unique_NULLABLE"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.FLOAT_5000unique_REQUIRED"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.FLOAT_5000unique_REPEATED"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.NUMERIC_5000unique_NULLABLE"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.BOOLEAN_2unique_NULLABLE"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.TIMESTAMP_1unique_NULLABLE"}}
    ]

    training_task_inputs_dict = {
        # required inputs
        "targetColumn": target_column,
        "predictionType": "regression",
        "transformations": transformations,
        "trainBudgetMilliNodeHours": 8000,

        # optional inputs
        "disableEarlyStopping": False,
        # supported regression optimisation objectives: minimize-rmse, 
        # minimize-mae, minimize-rmsle
        "optimizationObjective": "minimize-rmse",
    }
    training_task_inputs = to_protobuf_value(training_task_inputs_dict)

    training_pipeline = {
        'display_name': display_name,
        'training_task_definition': "gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_tabular_1.0.0.yaml",
        'training_task_inputs': training_task_inputs,
        'input_data_config': {
            'dataset_id': dataset_id,
            'fraction_split': {
                'training_fraction': 0.8,
                'validation_fraction': 0.1,
                'test_fraction': 0.1,
            }
        },
        'model_to_upload': {
            'display_name': model_display_name
        }
    }

    return training_pipeline

