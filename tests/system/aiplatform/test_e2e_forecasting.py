# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

from google.cloud import aiplatform
from google.cloud.aiplatform.compat.types import job_state
from google.cloud.aiplatform.compat.types import pipeline_state
import pytest
from tests.system.aiplatform import e2e_base

_TRAINING_DATASET_BQ_PATH = (
    "bq://bigquery-public-data:iowa_liquor_sales_forecasting.2020_sales_train"
)
_PREDICTION_DATASET_BQ_PATH = (
    "bq://bigquery-public-data:iowa_liquor_sales_forecasting.2021_sales_predict"
)


@pytest.mark.usefixtures("prepare_staging_bucket", "delete_staging_bucket")
class TestEndToEndForecasting(e2e_base.TestEndToEnd):
    """End to end system test of the Vertex SDK with forecasting data."""

    _temp_prefix = "temp-vertex-sdk-e2e-forecasting"

    def test_end_to_end_forecasting(self, shared_state):
        """Builds a dataset, trains models, and gets batch predictions."""
        ds = None
        automl_job = None
        automl_model = None
        automl_batch_prediction_job = None

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=shared_state["staging_bucket_name"],
        )
        try:
            # Create and import to single managed dataset for both training
            # jobs.
            ds = aiplatform.TimeSeriesDataset.create(
                display_name=self._make_display_name("dataset"),
                bq_source=[_TRAINING_DATASET_BQ_PATH],
                sync=False,
                create_request_timeout=180.0,
            )

            time_column = "date"
            time_series_identifier_column = "store_name"
            target_column = "sale_dollars"
            column_specs = {
                time_column: "timestamp",
                target_column: "numeric",
                "city": "categorical",
                "zip_code": "categorical",
                "county": "categorical",
            }

            # Define both training jobs
            # TODO(humichael): Add seq2seq job.
            automl_job = aiplatform.AutoMLForecastingTrainingJob(
                display_name=self._make_display_name("train-housing-automl"),
                optimization_objective="minimize-rmse",
                column_specs=column_specs,
            )

            # Kick off both training jobs, AutoML job will take approx one hour
            # to run.
            automl_model = automl_job.run(
                dataset=ds,
                target_column=target_column,
                time_column=time_column,
                time_series_identifier_column=time_series_identifier_column,
                available_at_forecast_columns=[time_column],
                unavailable_at_forecast_columns=[target_column],
                time_series_attribute_columns=["city", "zip_code", "county"],
                forecast_horizon=30,
                context_window=30,
                data_granularity_unit="day",
                data_granularity_count=1,
                budget_milli_node_hours=1000,
                model_display_name=self._make_display_name("automl-liquor-model"),
                sync=False,
            )

            automl_batch_prediction_job = automl_model.batch_predict(
                job_display_name=self._make_display_name("automl-liquor-model"),
                instances_format="bigquery",
                machine_type="n1-standard-4",
                bigquery_source=_PREDICTION_DATASET_BQ_PATH,
                gcs_destination_prefix=(
                    f'gs://{shared_state["staging_bucket_name"]}/bp_results/'
                ),
                sync=False,
            )

            automl_batch_prediction_job.wait()

            assert (
                automl_job.state
                == pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            )
            assert (
                automl_batch_prediction_job.state
                == job_state.JobState.JOB_STATE_SUCCEEDED
            )
        finally:
            if ds is not None:
                ds.delete()
            if automl_job is not None:
                automl_job.delete()
            if automl_model is not None:
                automl_model.delete()
            if automl_batch_prediction_job is not None:
                automl_batch_prediction_job.delete()
