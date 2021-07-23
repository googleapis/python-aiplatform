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


def make_training_pipeline(
    display_name: str,
    dataset_id: str,
    model_display_name: str,
    target_column: str,
    time_series_identifier_column: str,
    time_column: str,
    static_columns: str,
    time_variant_past_only_columns: str,
    time_variant_past_and_future_columns: str,
    forecast_window_end: int,
) -> google.cloud.aiplatform_v1alpha1.types.training_pipeline.TrainingPipeline:
    # set the columns used for training and their data types
    transformations = [
        {"auto": {"column_name": "date"}},
        {"auto": {"column_name": "state_name"}},
        {"auto": {"column_name": "county_fips_code"}},
        {"auto": {"column_name": "confirmed_cases"}},
        {"auto": {"column_name": "deaths"}},
    ]

    period = {"unit": "day", "quantity": 1}

    # the inputs should be formatted according to the training_task_definition yaml file
    training_task_inputs_dict = {
        # required inputs
        "targetColumn": target_column,
        "timeSeriesIdentifierColumn": time_series_identifier_column,
        "timeColumn": time_column,
        "transformations": transformations,
        "period": period,
        "optimizationObjective": "minimize-rmse",
        "trainBudgetMilliNodeHours": 8000,
        "staticColumns": static_columns,
        "timeVariantPastOnlyColumns": time_variant_past_only_columns,
        "timeVariantPastAndFutureColumns": time_variant_past_and_future_columns,
        "forecastWindowEnd": forecast_window_end,
    }

    training_task_inputs = to_protobuf_value(training_task_inputs_dict)

    training_pipeline = {
        "display_name": display_name,
        "training_task_definition": "gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_forecasting_1.0.0.yaml",
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

    return training_pipeline

