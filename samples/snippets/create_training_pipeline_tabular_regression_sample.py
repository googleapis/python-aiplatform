# Copyright 2020 Google LLC
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

# [START aiplatform_create_training_pipeline_tabular_regression_sample]
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


def create_training_pipeline_tabular_regression_sample(
    project: str,
    display_name: str,
    dataset_id: str,
    model_display_name: str,
    target_column: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PipelineServiceClient(client_options=client_options)
    # set the columns used for training and their data types
    transformations = [
        {"auto": {"column_name": "STRING_5000unique_NULLABLE"}},
        {"auto": {"column_name": "INTEGER_5000unique_NULLABLE"}},
        {"auto": {"column_name": "FLOAT_5000unique_NULLABLE"}},
        {"auto": {"column_name": "FLOAT_5000unique_REPEATED"}},
        {"auto": {"column_name": "NUMERIC_5000unique_NULLABLE"}},
        {"auto": {"column_name": "BOOLEAN_2unique_NULLABLE"}},
        {
            "timestamp": {
                "column_name": "TIMESTAMP_1unique_NULLABLE",
                "invalid_values_allowed": True,
            }
        },
        {"auto": {"column_name": "DATE_1unique_NULLABLE"}},
        {"auto": {"column_name": "TIME_1unique_NULLABLE"}},
        {
            "timestamp": {
                "column_name": "DATETIME_1unique_NULLABLE",
                "invalid_values_allowed": True,
            }
        },
        {"auto": {"column_name": "STRUCT_NULLABLE.STRING_5000unique_NULLABLE"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.INTEGER_5000unique_NULLABLE"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.FLOAT_5000unique_NULLABLE"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.FLOAT_5000unique_REQUIRED"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.FLOAT_5000unique_REPEATED"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.NUMERIC_5000unique_NULLABLE"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.BOOLEAN_2unique_NULLABLE"}},
        {"auto": {"column_name": "STRUCT_NULLABLE.TIMESTAMP_1unique_NULLABLE"}},
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
    training_task_inputs = json_format.ParseDict(training_task_inputs_dict, Value())

    training_pipeline = {
        "display_name": display_name,
        "training_task_definition": "gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_tabular_1.0.0.yaml",
        "training_task_inputs": training_task_inputs,
        "input_data_config": {
            "dataset_id": dataset_id,
            "fraction_split": {
                "training_fraction": 0.8,
                "validation_fraction": 0.1,
                "test_fraction": 0.1,
            },
        },
        "model_to_upload": {"display_name": model_display_name},
    }
    parent = f"projects/{project}/locations/{location}"
    response = client.create_training_pipeline(
        parent=parent, training_pipeline=training_pipeline
    )
    print("response:", response)


# [END aiplatform_create_training_pipeline_tabular_regression_sample]
