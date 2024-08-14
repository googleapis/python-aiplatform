# Copyright 2022 Google LLC
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


import create_training_pipeline_forecasting_sample
import test_constants as constants


def test_create_training_pipeline_forecasting_sample(
    mock_sdk_init,
    mock_time_series_dataset,
    mock_get_automl_forecasting_training_job,
    mock_run_automl_forecasting_training_job,
    mock_get_time_series_dataset,
):

    create_training_pipeline_forecasting_sample.create_training_pipeline_forecasting_sample(
        project=constants.PROJECT,
        display_name=constants.DISPLAY_NAME,
        dataset_id=constants.RESOURCE_ID,
        model_display_name=constants.DISPLAY_NAME_2,
        target_column=constants.TABULAR_TARGET_COLUMN,
        training_fraction_split=constants.TRAINING_FRACTION_SPLIT,
        validation_fraction_split=constants.VALIDATION_FRACTION_SPLIT,
        test_fraction_split=constants.TEST_FRACTION_SPLIT,
        budget_milli_node_hours=constants.BUDGET_MILLI_NODE_HOURS_8000,
        timestamp_split_column_name=constants.TIMESTAMP_SPLIT_COLUMN_NAME,
        weight_column=constants.WEIGHT_COLUMN,
        time_series_attribute_columns=constants.TIME_SERIES_ATTRIBUTE_COLUMNS,
        context_window=constants.CONTEXT_WINDOW,
        export_evaluated_data_items=constants.EXPORT_EVALUATED_DATA_ITEMS,
        export_evaluated_data_items_bigquery_destination_uri=constants.EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
        export_evaluated_data_items_override_destination=constants.EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
        quantiles=constants.QUANTILES,
        enable_probabilistic_inference=constants.ENABLE_PROBABILISTIC_INFERENCE,
        validation_options=constants.VALIDATION_OPTIONS,
        predefined_split_column_name=constants.PREDEFINED_SPLIT_COLUMN_NAME,
    )

    mock_get_time_series_dataset.assert_called_once_with(constants.RESOURCE_ID)

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )
    mock_get_automl_forecasting_training_job.assert_called_once_with(
        display_name=constants.DISPLAY_NAME,
        optimization_objective="minimize-rmse",
    )
    mock_run_automl_forecasting_training_job.assert_called_once_with(
        dataset=mock_time_series_dataset,
        target_column=constants.TABULAR_TARGET_COLUMN,
        time_column=constants.FORECASTNG_TIME_COLUMN,
        time_series_identifier_column=constants.FORECASTNG_TIME_SERIES_IDENTIFIER_COLUMN,
        unavailable_at_forecast_columns=constants.FORECASTNG_UNAVAILABLE_AT_FORECAST_COLUMNS,
        available_at_forecast_columns=constants.FORECASTNG_AVAILABLE_AT_FORECAST_COLUMNS,
        forecast_horizon=constants.FORECASTNG_FORECAST_HORIZON,
        data_granularity_unit=constants.DATA_GRANULARITY_UNIT,
        data_granularity_count=constants.DATA_GRANULARITY_COUNT,
        training_fraction_split=constants.TRAINING_FRACTION_SPLIT,
        validation_fraction_split=constants.VALIDATION_FRACTION_SPLIT,
        test_fraction_split=constants.TEST_FRACTION_SPLIT,
        budget_milli_node_hours=constants.BUDGET_MILLI_NODE_HOURS_8000,
        model_display_name=constants.DISPLAY_NAME_2,
        timestamp_split_column_name=constants.TIMESTAMP_SPLIT_COLUMN_NAME,
        weight_column=constants.WEIGHT_COLUMN,
        time_series_attribute_columns=constants.TIME_SERIES_ATTRIBUTE_COLUMNS,
        context_window=constants.CONTEXT_WINDOW,
        export_evaluated_data_items=constants.EXPORT_EVALUATED_DATA_ITEMS,
        export_evaluated_data_items_bigquery_destination_uri=constants.EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
        export_evaluated_data_items_override_destination=constants.EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
        quantiles=constants.QUANTILES,
        enable_probabilistic_inference=constants.ENABLE_PROBABILISTIC_INFERENCE,
        validation_options=constants.VALIDATION_OPTIONS,
        predefined_split_column_name=constants.PREDEFINED_SPLIT_COLUMN_NAME,
        sync=True,
    )
