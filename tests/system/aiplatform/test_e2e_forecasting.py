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
from google.cloud.aiplatform import training_jobs

from google.cloud.aiplatform.compat.types import job_state
from google.cloud.aiplatform.compat.types import pipeline_state
import pytest
from tests.system.aiplatform import e2e_base

_TRAINING_DATASET_BQ_PATH = (
    "bq://ucaip-sample-tests:ucaip_test_us_central1.2020_sales_train"
)
_PREDICTION_DATASET_BQ_PATH = (
    "bq://ucaip-sample-tests:ucaip_test_us_central1.2021_sales_predict"
)


@pytest.mark.usefixtures("prepare_staging_bucket", "delete_staging_bucket")
class TestEndToEndForecasting(e2e_base.TestEndToEnd):
    """End to end system test of the Vertex SDK with forecasting data."""

    _temp_prefix = "temp-vertex-sdk-e2e-forecasting"

    @pytest.mark.parametrize(
        "training_job",
        [
            training_jobs.AutoMLForecastingTrainingJob,
            training_jobs.SequenceToSequencePlusForecastingTrainingJob,
            training_jobs.TemporalFusionTransformerForecastingTrainingJob,
            training_jobs.TimeSeriesDenseEncoderForecastingTrainingJob,
        ],
    )
    def test_end_to_end_forecasting(self, shared_state, training_job):
        """Builds a dataset, trains models, and gets batch predictions."""
        resources = []

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=shared_state["staging_bucket_name"],
        )
        try:
            ds = aiplatform.TimeSeriesDataset.create(
                display_name=self._make_display_name("dataset"),
                bq_source=[_TRAINING_DATASET_BQ_PATH],
                sync=False,
                create_request_timeout=180.0,
            )
            resources.append(ds)

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

            job = training_job(
                display_name=self._make_display_name("train-housing-forecasting"),
                optimization_objective="minimize-rmse",
                column_specs=column_specs,
            )
            resources.append(job)

            model = job.run(
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
                holiday_regions=["GLOBAL"],
                hierarchy_group_total_weight=1,
                window_stride_length=1,
                model_display_name=self._make_display_name("forecasting-liquor-model"),
                sync=False,
            )
            resources.append(model)

            batch_prediction_job = model.batch_predict(
                job_display_name=self._make_display_name("forecasting-liquor-model"),
                instances_format="bigquery",
                predictions_format="csv",
                machine_type="n1-standard-4",
                bigquery_source=_PREDICTION_DATASET_BQ_PATH,
                gcs_destination_prefix=(
                    f'gs://{shared_state["staging_bucket_name"]}/bp_results/'
                ),
                sync=False,
            )
            resources.append(batch_prediction_job)

            batch_prediction_job.wait()
            model.wait()
            assert job.state == pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            assert batch_prediction_job.state == job_state.JobState.JOB_STATE_SUCCEEDED
        finally:
            for resource in resources:
                resource.delete()
