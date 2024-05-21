# Copyright 2023 Google LLC
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
import importlib
import os
from unittest import mock

from google import auth
from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.services import (
    model_monitoring_service_client_v1beta1 as model_monitoring_service_client,
    schedule_service_client_v1beta1 as schedule_service_client,
)
from google.cloud.aiplatform.compat.types import (
    io_v1beta1 as io,
    model_monitor_v1beta1 as gca_model_monitor,
    model_monitoring_alert_v1beta1 as gca_model_monitoring_alert,
    model_monitoring_job_v1beta1 as gca_model_monitoring_job,
    model_monitoring_service_v1beta1 as gca_model_monitoring_service,
    model_monitoring_spec_v1beta1 as gca_model_monitoring_spec,
    model_monitoring_stats_v1beta1 as gca_model_monitoring_stats,
    schedule_service_v1beta1 as gca_schedule_service,
    schedule_v1beta1 as gca_schedule,
    explanation_v1beta1 as explanation,
)
from vertexai.resources.preview import (
    ml_monitoring,
    ModelMonitor,
    ModelMonitoringJob,
)
import pytest

from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore


# -*- coding: utf-8 -*-

_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_DESCRIPTION = "test description"
_TEST_JSON_CONTENT_TYPE = "application/json"
_TEST_LOCATION = "us-central1"
_TEST_LOCATION_2 = "europe-west4"
_TEST_PROJECT = "test-project"
_TEST_REPLICA_COUNT = 1
_TEST_MODEL_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/123"
_TEST_MODEL_VERSION_ID = "1"
_TEST_MODEL_MONITOR_APP = "ortools-on-vertex-v0.1"
_TEST_MODEL_MONITOR_DISPLAY_NAME = "model-monitor-display-name"
_TEST_MODEL_MONITOR_USER_ID = "user_456"
_TEST_MODEL_MONITOR_ID = "456"
_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME = "job-display-name"
_TEST_MODEL_MONITORING_JOB_USER_ID = "user_789"
_TEST_MODEL_MONITORING_JOB_ID = "789"
_TEST_SCHEDULE_NAME = "000"
_TEST_OUTPUT_PATH = "tests/output_path"
_TEST_NOTIFICATION_EMAIL = "123@test.com"
_TEST_BASELINE_RESOURCE = "tests/baseline"
_TEST_TARGET_RESOURCE = "tests/target"
_TEST_TRAINING_DATASET = gca_model_monitoring_spec.ModelMonitoringInput(
    columnized_dataset=gca_model_monitoring_spec.ModelMonitoringInput.ModelMonitoringDataset(
        vertex_dataset=_TEST_BASELINE_RESOURCE
    ),
)
_TESTDATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata")
_TEST_MODEL_MONITOR_PARENT = initializer.global_config.common_location_path(
    project=_TEST_PROJECT, location=_TEST_LOCATION
)
_TEST_MODEL_MONITORING_JOB_RESOURCE_NAME = model_monitoring_service_client.ModelMonitoringServiceClient.model_monitoring_job_path(
    _TEST_PROJECT,
    _TEST_LOCATION,
    _TEST_MODEL_MONITOR_ID,
    _TEST_MODEL_MONITORING_JOB_ID,
)
_TEST_MODEL_MONITOR_RESOURCE_NAME = (
    model_monitoring_service_client.ModelMonitoringServiceClient.model_monitor_path(
        _TEST_PROJECT, _TEST_LOCATION, _TEST_MODEL_MONITOR_ID
    )
)
_TEST_MODEL_MONITORING_SCHEMA = ml_monitoring.spec.ModelMonitoringSchema(
    feature_fields=[
        ml_monitoring.spec.FieldSchema(
            name="feature1",
            data_type="string",
            repeated=False,
        )
    ],
)
_TEST_CREATE_MODEL_MONITOR_OBJ = gca_model_monitor.ModelMonitor(
    display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
    model_monitoring_target=gca_model_monitor.ModelMonitor.ModelMonitoringTarget(
        vertex_model=gca_model_monitor.ModelMonitor.ModelMonitoringTarget.VertexModelSource(
            model=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
        )
    ),
    training_dataset=gca_model_monitoring_spec.ModelMonitoringInput(
        columnized_dataset=gca_model_monitoring_spec.ModelMonitoringInput.ModelMonitoringDataset(
            vertex_dataset=_TEST_BASELINE_RESOURCE
        ),
    ),
    tabular_objective=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.TabularObjective(
        feature_drift_spec=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.DataDriftSpec(
            categorical_metric_type="l_infinity",
            numeric_metric_type="jensen_shannon_divergence",
            default_categorical_alert_condition=gca_model_monitoring_alert.ModelMonitoringAlertCondition(
                threshold=0.1,
            ),
            default_numeric_alert_condition=gca_model_monitoring_alert.ModelMonitoringAlertCondition(
                threshold=0.2,
            ),
        )
    ),
    output_spec=gca_model_monitoring_spec.ModelMonitoringOutputSpec(
        gcs_base_directory=io.GcsDestination(output_uri_prefix=_TEST_OUTPUT_PATH)
    ),
    notification_spec=gca_model_monitoring_spec.ModelMonitoringNotificationSpec(
        email_config=gca_model_monitoring_spec.ModelMonitoringNotificationSpec.EmailConfig(
            user_emails=[_TEST_NOTIFICATION_EMAIL]
        ),
    ),
)
_TEST_MODEL_MONITOR_OBJ = gca_model_monitor.ModelMonitor(
    name=_TEST_MODEL_MONITOR_RESOURCE_NAME,
    display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
    model_monitoring_target=gca_model_monitor.ModelMonitor.ModelMonitoringTarget(
        vertex_model=gca_model_monitor.ModelMonitor.ModelMonitoringTarget.VertexModelSource(
            model=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
        )
    ),
    training_dataset=gca_model_monitoring_spec.ModelMonitoringInput(
        columnized_dataset=gca_model_monitoring_spec.ModelMonitoringInput.ModelMonitoringDataset(
            vertex_dataset=_TEST_BASELINE_RESOURCE
        ),
    ),
    model_monitoring_schema=gca_model_monitor.ModelMonitoringSchema(
        feature_fields=[
            gca_model_monitor.ModelMonitoringSchema.FieldSchema(
                name="feature1",
                data_type="string",
                repeated=False,
            )
        ],
    ),
    tabular_objective=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.TabularObjective(
        feature_drift_spec=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.DataDriftSpec(
            categorical_metric_type="l_infinity",
            numeric_metric_type="jensen_shannon_divergence",
            default_categorical_alert_condition=gca_model_monitoring_alert.ModelMonitoringAlertCondition(
                threshold=0.1,
            ),
            default_numeric_alert_condition=gca_model_monitoring_alert.ModelMonitoringAlertCondition(
                threshold=0.2,
            ),
        )
    ),
    output_spec=gca_model_monitoring_spec.ModelMonitoringOutputSpec(
        gcs_base_directory=io.GcsDestination(output_uri_prefix=_TEST_OUTPUT_PATH)
    ),
    notification_spec=gca_model_monitoring_spec.ModelMonitoringNotificationSpec(
        email_config=gca_model_monitoring_spec.ModelMonitoringNotificationSpec.EmailConfig(
            user_emails=[_TEST_NOTIFICATION_EMAIL]
        ),
    ),
)
_TEST_UPDATED_MODEL_MONITOR_OBJ = gca_model_monitor.ModelMonitor(
    name=_TEST_MODEL_MONITOR_RESOURCE_NAME,
    display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
    model_monitoring_target=gca_model_monitor.ModelMonitor.ModelMonitoringTarget(
        vertex_model=gca_model_monitor.ModelMonitor.ModelMonitoringTarget.VertexModelSource(
            model=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
        )
    ),
    training_dataset=gca_model_monitoring_spec.ModelMonitoringInput(
        columnized_dataset=gca_model_monitoring_spec.ModelMonitoringInput.ModelMonitoringDataset(
            vertex_dataset=_TEST_BASELINE_RESOURCE
        ),
    ),
    model_monitoring_schema=gca_model_monitor.ModelMonitoringSchema(
        feature_fields=[
            gca_model_monitor.ModelMonitoringSchema.FieldSchema(
                name="feature1",
                data_type="string",
                repeated=False,
            )
        ],
    ),
    tabular_objective=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.TabularObjective(
        feature_drift_spec=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.DataDriftSpec(
            categorical_metric_type="l_infinity",
            numeric_metric_type="jensen_shannon_divergence",
            default_categorical_alert_condition=gca_model_monitoring_spec.model_monitoring_alert.ModelMonitoringAlertCondition(
                threshold=0.1,
            ),
            default_numeric_alert_condition=gca_model_monitoring_spec.model_monitoring_alert.ModelMonitoringAlertCondition(
                threshold=0.2,
            ),
        )
    ),
    output_spec=gca_model_monitoring_spec.ModelMonitoringOutputSpec(
        gcs_base_directory=io.GcsDestination(output_uri_prefix=_TEST_OUTPUT_PATH)
    ),
    notification_spec=gca_model_monitoring_spec.ModelMonitoringNotificationSpec(
        email_config=gca_model_monitoring_spec.ModelMonitoringNotificationSpec.EmailConfig(
            user_emails=[_TEST_NOTIFICATION_EMAIL, "456@test.com"]
        ),
    ),
)
_TEST_CREATE_MODEL_MONITORING_JOB_OBJ = gca_model_monitoring_job.ModelMonitoringJob(
    display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
    model_monitoring_spec=gca_model_monitoring_spec.ModelMonitoringSpec(
        objective_spec=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec(
            tabular_objective=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.TabularObjective(
                feature_drift_spec=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.DataDriftSpec(
                    categorical_metric_type="l_infinity",
                    numeric_metric_type="jensen_shannon_divergence",
                    default_categorical_alert_condition=gca_model_monitoring_alert.ModelMonitoringAlertCondition(
                        threshold=0.1,
                    ),
                    default_numeric_alert_condition=gca_model_monitoring_alert.ModelMonitoringAlertCondition(
                        threshold=0.2,
                    ),
                )
            ),
            baseline_dataset=gca_model_monitoring_spec.ModelMonitoringInput(
                columnized_dataset=gca_model_monitoring_spec.ModelMonitoringInput.ModelMonitoringDataset(
                    vertex_dataset=_TEST_BASELINE_RESOURCE
                ),
            ),
            target_dataset=gca_model_monitoring_spec.ModelMonitoringInput(
                columnized_dataset=gca_model_monitoring_spec.ModelMonitoringInput.ModelMonitoringDataset(
                    vertex_dataset=_TEST_TARGET_RESOURCE
                )
            ),
            explanation_spec=explanation.ExplanationSpec(),
        ),
        output_spec=gca_model_monitoring_spec.ModelMonitoringOutputSpec(
            gcs_base_directory=io.GcsDestination(output_uri_prefix=_TEST_OUTPUT_PATH)
        ),
        notification_spec=gca_model_monitoring_spec.ModelMonitoringNotificationSpec(
            email_config=gca_model_monitoring_spec.ModelMonitoringNotificationSpec.EmailConfig(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            )
        ),
    ),
)
_TEST_MODEL_MONITORING_JOB_OBJ = gca_model_monitoring_job.ModelMonitoringJob(
    name=_TEST_MODEL_MONITORING_JOB_RESOURCE_NAME,
    display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
    model_monitoring_spec=gca_model_monitoring_spec.ModelMonitoringSpec(
        objective_spec=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec(
            tabular_objective=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.TabularObjective(
                feature_drift_spec=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.DataDriftSpec(
                    categorical_metric_type="l_infinity",
                    numeric_metric_type="jensen_shannon_divergence",
                    default_categorical_alert_condition=gca_model_monitoring_alert.ModelMonitoringAlertCondition(
                        threshold=0.1,
                    ),
                    default_numeric_alert_condition=gca_model_monitoring_alert.ModelMonitoringAlertCondition(
                        threshold=0.2,
                    ),
                )
            ),
            baseline_dataset=gca_model_monitoring_spec.ModelMonitoringInput(
                columnized_dataset=gca_model_monitoring_spec.ModelMonitoringInput.ModelMonitoringDataset(
                    vertex_dataset=_TEST_BASELINE_RESOURCE
                ),
            ),
            target_dataset=gca_model_monitoring_spec.ModelMonitoringInput(
                columnized_dataset=gca_model_monitoring_spec.ModelMonitoringInput.ModelMonitoringDataset(
                    vertex_dataset=_TEST_TARGET_RESOURCE
                )
            ),
            explanation_spec=explanation.ExplanationSpec(),
        ),
        output_spec=gca_model_monitoring_spec.ModelMonitoringOutputSpec(
            gcs_base_directory=io.GcsDestination(output_uri_prefix=_TEST_OUTPUT_PATH)
        ),
        notification_spec=gca_model_monitoring_spec.ModelMonitoringNotificationSpec(
            email_config=gca_model_monitoring_spec.ModelMonitoringNotificationSpec.EmailConfig(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            )
        ),
    ),
)
_TEST_CRON = r"America/New_York 1 \* \* \* \*"
_TEST_SCHEDULE_OBJ = gca_schedule.Schedule(
    display_name=_TEST_SCHEDULE_NAME,
    cron=_TEST_CRON,
    create_model_monitoring_job_request=gca_model_monitoring_service.CreateModelMonitoringJobRequest(
        parent=_TEST_MODEL_MONITOR_RESOURCE_NAME,
        model_monitoring_job=_TEST_MODEL_MONITORING_JOB_OBJ,
    ),
    max_concurrent_run_count=1,
)
_TEST_UPDATED_MODEL_MONITORING_JOB_OBJ = gca_model_monitoring_job.ModelMonitoringJob(
    display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
    model_monitoring_spec=gca_model_monitoring_spec.ModelMonitoringSpec(
        objective_spec=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec(
            tabular_objective=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.TabularObjective(
                feature_drift_spec=gca_model_monitoring_spec.ModelMonitoringObjectiveSpec.DataDriftSpec(
                    categorical_metric_type="l_infinity",
                    numeric_metric_type="jensen_shannon_divergence",
                    default_categorical_alert_condition=gca_model_monitoring_alert.ModelMonitoringAlertCondition(
                        threshold=0.1,
                    ),
                    default_numeric_alert_condition=gca_model_monitoring_alert.ModelMonitoringAlertCondition(
                        threshold=0.2,
                    ),
                )
            ),
            baseline_dataset=gca_model_monitoring_spec.ModelMonitoringInput(
                columnized_dataset=gca_model_monitoring_spec.ModelMonitoringInput.ModelMonitoringDataset(
                    vertex_dataset=_TEST_BASELINE_RESOURCE
                ),
            ),
            target_dataset=gca_model_monitoring_spec.ModelMonitoringInput(
                columnized_dataset=gca_model_monitoring_spec.ModelMonitoringInput.ModelMonitoringDataset(
                    vertex_dataset=_TEST_TARGET_RESOURCE
                )
            ),
            explanation_spec=explanation.ExplanationSpec(),
        ),
        output_spec=gca_model_monitoring_spec.ModelMonitoringOutputSpec(
            gcs_base_directory=io.GcsDestination(output_uri_prefix=_TEST_OUTPUT_PATH)
        ),
        notification_spec=gca_model_monitoring_spec.ModelMonitoringNotificationSpec(
            email_config=gca_model_monitoring_spec.ModelMonitoringNotificationSpec.EmailConfig(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            )
        ),
    ),
)
_TEST_UPDATED_SCHEDULE_OBJ = gca_schedule.Schedule(
    display_name=_TEST_SCHEDULE_NAME,
    cron=r"America/New_York 0 \* \* \* \*",
    create_model_monitoring_job_request=gca_model_monitoring_service.CreateModelMonitoringJobRequest(
        parent=_TEST_MODEL_MONITOR_RESOURCE_NAME,
        model_monitoring_job=_TEST_UPDATED_MODEL_MONITORING_JOB_OBJ,
    ),
    max_concurrent_run_count=1,
)
_TEST_SEARCH_REQUEST = gca_model_monitoring_service.SearchModelMonitoringStatsRequest(
    model_monitor=_TEST_MODEL_MONITOR_RESOURCE_NAME,
    stats_filter=(
        gca_model_monitoring_stats.SearchModelMonitoringStatsFilter(
            tabular_stats_filter=(
                gca_model_monitoring_stats.SearchModelMonitoringStatsFilter.TabularStatsFilter(
                    model_monitoring_job=_TEST_MODEL_MONITORING_JOB_RESOURCE_NAME,
                )
            )
        )
    ),
)
_TEST_SEARCH_RESPONSE = (
    gca_model_monitoring_service.SearchModelMonitoringStatsResponse()
)
_TEST_SEARCH_ALERTS_REQUEST = (
    gca_model_monitoring_service.SearchModelMonitoringAlertsRequest(
        model_monitor=_TEST_MODEL_MONITOR_RESOURCE_NAME,
        model_monitoring_job=_TEST_MODEL_MONITORING_JOB_RESOURCE_NAME,
    )
)
_TEST_SEARCH_ALERTS_RESPONSE = (
    gca_model_monitoring_service.SearchModelMonitoringAlertsResponse()
)
_TEST_LIST_REQUEST = gca_model_monitoring_service.ListModelMonitoringJobsRequest(
    parent=_TEST_MODEL_MONITOR_RESOURCE_NAME
)
_TEST_LIST_RESPONSE = gca_model_monitoring_service.ListModelMonitoringJobsResponse(
    model_monitoring_jobs=[
        _TEST_MODEL_MONITORING_JOB_OBJ,
        _TEST_MODEL_MONITORING_JOB_OBJ,
    ],
    next_page_token="1",
)


@pytest.fixture
def authorized_session_mock():
    with mock.patch(
        "google.auth.transport.requests.AuthorizedSession"
    ) as mock_authorized_session:
        mock_auth_session = mock_authorized_session(_TEST_CREDENTIALS)
        yield mock_auth_session


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            "test-project",
        )
        yield google_auth_mock


@pytest.fixture
def create_client_mock():
    with mock.patch.object(
        initializer.global_config, "create_client"
    ) as create_client_mock:
        api_client_mock = mock.Mock(
            spec=model_monitoring_service_client.ModelMonitoringServiceClient
        )
        api_client_mock.get_model_monitor.return_value = _TEST_MODEL_MONITOR_OBJ
        create_client_mock.return_value = api_client_mock
        yield create_client_mock


@pytest.fixture
def create_model_monitor_mock():
    with mock.patch.object(
        model_monitoring_service_client.ModelMonitoringServiceClient,
        "create_model_monitor",
    ) as create_model_monitor_mock:
        create_model_monitor_lro_mock = mock.Mock(ga_operation.Operation)
        create_model_monitor_lro_mock.result.return_value = _TEST_MODEL_MONITOR_OBJ
        create_model_monitor_mock.return_value = create_model_monitor_lro_mock
        yield create_model_monitor_mock


@pytest.fixture
def get_model_monitor_mock():
    with mock.patch.object(
        model_monitoring_service_client.ModelMonitoringServiceClient,
        "get_model_monitor",
    ) as get_model_monitor_mock:
        get_model_monitor_mock.return_value = _TEST_MODEL_MONITOR_OBJ
        yield get_model_monitor_mock


@pytest.fixture
def update_model_monitor_mock():
    with mock.patch.object(
        model_monitoring_service_client.ModelMonitoringServiceClient,
        "update_model_monitor",
    ) as update_model_monitor_mock:
        update_model_monitor_lro_mock = mock.Mock(ga_operation.Operation)
        update_model_monitor_lro_mock.result.return_value = (
            _TEST_UPDATED_MODEL_MONITOR_OBJ
        )
        update_model_monitor_mock.return_value = update_model_monitor_lro_mock
        yield update_model_monitor_mock


@pytest.fixture
def create_schedule_mock():
    with mock.patch.object(
        schedule_service_client.ScheduleServiceClient, "create_schedule"
    ) as create_schedule_mock:
        create_schedule_mock.return_value = _TEST_SCHEDULE_OBJ
        yield create_schedule_mock


@pytest.fixture
def update_schedule_mock():
    with mock.patch.object(
        schedule_service_client.ScheduleServiceClient, "update_schedule"
    ) as update_schedule_mock:
        update_schedule_mock.return_value = _TEST_UPDATED_SCHEDULE_OBJ
        yield update_schedule_mock


@pytest.fixture
def get_schedule_mock():
    with mock.patch.object(
        schedule_service_client.ScheduleServiceClient, "get_schedule"
    ) as get_schedule_mock:
        get_schedule_mock.return_value = _TEST_SCHEDULE_OBJ
        yield get_schedule_mock


@pytest.fixture
def search_metrics_mock():
    with mock.patch.object(
        model_monitoring_service_client.ModelMonitoringServiceClient,
        "search_model_monitoring_stats",
    ) as search_metrics_mock:
        search_metrics_mock.return_value = (
            model_monitoring_service_client.pagers.SearchModelMonitoringStatsPager(
                method=search_metrics_mock,
                request=_TEST_SEARCH_REQUEST,
                response=_TEST_SEARCH_RESPONSE,
            )
        )
        yield search_metrics_mock


@pytest.fixture
def search_alerts_mock():
    with mock.patch.object(
        model_monitoring_service_client.ModelMonitoringServiceClient,
        "search_model_monitoring_alerts",
    ) as search_alerts_mock:
        search_alerts_mock.return_value = (
            model_monitoring_service_client.pagers.SearchModelMonitoringAlertsPager(
                method=search_alerts_mock,
                request=_TEST_SEARCH_ALERTS_REQUEST,
                response=_TEST_SEARCH_ALERTS_RESPONSE,
            )
        )
        yield search_alerts_mock


@pytest.fixture
def list_model_monitoring_jobs_mock():
    with mock.patch.object(
        model_monitoring_service_client.ModelMonitoringServiceClient,
        "list_model_monitoring_jobs",
    ) as list_model_monitoring_jobs_mock:
        list_model_monitoring_jobs_mock.return_value = (
            model_monitoring_service_client.pagers.ListModelMonitoringJobsPager(
                method=list_model_monitoring_jobs_mock,
                request=_TEST_LIST_REQUEST,
                response=_TEST_LIST_RESPONSE,
            )
        )
        yield list_model_monitoring_jobs_mock


@pytest.fixture
def delete_model_monitor_mock():
    with mock.patch.object(
        model_monitoring_service_client.ModelMonitoringServiceClient,
        "delete_model_monitor",
    ) as delete_model_monitor_mock:
        delete_model_monitor_lro_mock = mock.Mock(ga_operation.Operation)
        delete_model_monitor_lro_mock.result.return_value = empty_pb2.Empty
        delete_model_monitor_mock.return_value = delete_model_monitor_lro_mock
        yield delete_model_monitor_mock


@pytest.fixture
def create_model_monitoring_job_mock():
    with mock.patch.object(
        model_monitoring_service_client.ModelMonitoringServiceClient,
        "create_model_monitoring_job",
    ) as create_model_monitoring_job_mock:
        create_model_monitoring_job_mock.return_value = _TEST_MODEL_MONITORING_JOB_OBJ
        yield create_model_monitoring_job_mock


@pytest.fixture
def get_model_monitoring_job_mock():
    with mock.patch.object(
        model_monitoring_service_client.ModelMonitoringServiceClient,
        "get_model_monitoring_job",
    ) as get_model_monitoring_job_mock:
        get_model_monitor_mock.return_value = _TEST_MODEL_MONITORING_JOB_OBJ
        yield get_model_monitoring_job_mock


@pytest.fixture
def delete_model_monitoring_job_mock():
    with mock.patch.object(
        model_monitoring_service_client.ModelMonitoringServiceClient,
        "delete_model_monitoring_job",
    ) as delete_model_monitoring_job_mock:
        delete_model_monitoring_job_lro_mock = mock.Mock(ga_operation.Operation)
        delete_model_monitoring_job_lro_mock.result.return_value = empty_pb2.Empty
        delete_model_monitoring_job_mock.return_value = (
            delete_model_monitoring_job_lro_mock
        )
        yield delete_model_monitoring_job_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestModelMonitor:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_constructor_creates_client(self, create_client_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        ModelMonitor(_TEST_MODEL_MONITOR_ID)
        create_client_mock.assert_any_call(
            client_class=utils.ModelMonitoringClientWithOverride,
            credentials=initializer.global_config.credentials,
            location_override=_TEST_LOCATION,
            appended_user_agent=None,
        )

    def test_constructor_create_client_with_custom_location(self, create_client_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        ModelMonitor(_TEST_MODEL_MONITOR_ID, location=_TEST_LOCATION_2)
        create_client_mock.assert_any_call(
            client_class=utils.ModelMonitoringClientWithOverride,
            credentials=initializer.global_config.credentials,
            location_override=_TEST_LOCATION_2,
            appended_user_agent=None,
        )

    def test_constructor_creates_client_with_custom_credentials(
        self, create_client_mock
    ):
        creds = auth_credentials.AnonymousCredentials()
        ModelMonitor(_TEST_MODEL_MONITOR_ID, credentials=creds)
        create_client_mock.assert_any_call(
            client_class=utils.ModelMonitoringClientWithOverride,
            credentials=creds,
            location_override=_TEST_LOCATION,
            appended_user_agent=None,
        )

    @pytest.mark.usefixtures("create_model_monitor_mock")
    def test_create_model_monitor(self, create_model_monitor_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        ModelMonitor.create(
            training_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            model_name=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
            display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
        )
        create_model_monitor_mock.assert_called_once_with(
            request=gca_model_monitoring_service.CreateModelMonitorRequest(
                parent=_TEST_MODEL_MONITOR_PARENT,
                model_monitor=_TEST_CREATE_MODEL_MONITOR_OBJ,
            ),
        )

    @pytest.mark.usefixtures("create_model_monitor_mock")
    def test_create_model_monitor_with_user_id(self, create_model_monitor_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        ModelMonitor.create(
            training_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            model_name=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
            display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
            model_monitor_id=_TEST_MODEL_MONITOR_USER_ID,
        )
        create_model_monitor_mock.assert_called_once_with(
            request=gca_model_monitoring_service.CreateModelMonitorRequest(
                parent=_TEST_MODEL_MONITOR_PARENT,
                model_monitor=_TEST_CREATE_MODEL_MONITOR_OBJ,
                model_monitor_id=_TEST_MODEL_MONITOR_USER_ID,
            ),
        )

    @pytest.mark.usefixtures(
        "create_model_monitor_mock",
        "get_model_monitor_mock",
        "update_model_monitor_mock",
    )
    def test_update_model_monitor(self, update_model_monitor_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        test_model_monitor = ModelMonitor.create(
            training_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            model_name=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
            display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
        )
        assert isinstance(test_model_monitor, ModelMonitor)
        test_model_monitor.update(
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL, "456@test.com"]
            ),
        )
        update_model_monitor_mock.assert_called_once_with(
            model_monitor=_TEST_UPDATED_MODEL_MONITOR_OBJ,
            update_mask=field_mask_pb2.FieldMask(paths=["notification_spec"]),
        )

    @pytest.mark.usefixtures("create_schedule_mock", "create_model_monitor_mock")
    def test_create_schedule(self, create_schedule_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        test_model_monitor = ModelMonitor.create(
            training_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            model_name=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
            display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
        )
        test_model_monitor.create_schedule(
            display_name=_TEST_SCHEDULE_NAME,
            model_monitoring_job_display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
            cron=_TEST_CRON,
            target_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_TARGET_RESOURCE
            ),
        )
        create_schedule_mock.assert_called_once_with(
            request=gca_schedule_service.CreateScheduleRequest(
                parent=_TEST_MODEL_MONITOR_PARENT,
                schedule=gca_schedule.Schedule(
                    display_name=_TEST_SCHEDULE_NAME,
                    cron=_TEST_CRON,
                    create_model_monitoring_job_request=gca_model_monitoring_service.CreateModelMonitoringJobRequest(
                        parent=_TEST_MODEL_MONITOR_RESOURCE_NAME,
                        model_monitoring_job=_TEST_CREATE_MODEL_MONITORING_JOB_OBJ,
                    ),
                    max_concurrent_run_count=1,
                ),
            )
        )

    @pytest.mark.usefixtures(
        "create_schedule_mock",
        "update_schedule_mock",
        "get_schedule_mock",
        "create_model_monitor_mock",
    )
    def test_update_schedule(self, update_schedule_mock, get_schedule_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        test_model_monitor = ModelMonitor.create(
            training_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            model_name=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
            display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
        )
        test_model_monitor.create_schedule(
            display_name=_TEST_SCHEDULE_NAME,
            model_monitoring_job_display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
            cron=_TEST_CRON,
            target_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_TARGET_RESOURCE
            ),
        )
        test_model_monitor.update_schedule(
            schedule_name=_TEST_SCHEDULE_NAME,
            cron=r"America/New_York 0 \* \* \* \*",
            baseline_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            target_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_TARGET_RESOURCE
            ),
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    categorical_metric_type="l_infinity",
                    numeric_metric_type="jensen_shannon_divergence",
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
        )
        update_schedule_mock.assert_called_once_with(
            schedule=_TEST_UPDATED_SCHEDULE_OBJ,
            update_mask=field_mask_pb2.FieldMask(
                paths=["cron", "create_model_monitoring_job_request"]
            ),
        )
        assert get_schedule_mock.call_count == 1

    @pytest.mark.usefixtures(
        "create_model_monitoring_job_mock", "create_model_monitor_mock"
    )
    def test_run_model_monitoring_job(self, create_model_monitoring_job_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        test_model_monitor = ModelMonitor.create(
            training_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            model_name=_TEST_MODEL_NAME,
            display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
        )
        test_model_monitor.run(
            display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
            target_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_TARGET_RESOURCE
            ),
        )
        create_model_monitoring_job_mock.assert_called_once_with(
            request=gca_model_monitoring_service.CreateModelMonitoringJobRequest(
                parent=_TEST_MODEL_MONITOR_RESOURCE_NAME,
                model_monitoring_job=_TEST_CREATE_MODEL_MONITORING_JOB_OBJ,
            )
        )

    @pytest.mark.usefixtures(
        "create_model_monitoring_job_mock", "create_model_monitor_mock"
    )
    def test_run_model_monitoring_job_with_user_id(
        self, create_model_monitoring_job_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        test_model_monitor = ModelMonitor.create(
            training_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            model_name=_TEST_MODEL_NAME,
            display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
        )
        test_model_monitor.run(
            display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
            target_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_TARGET_RESOURCE
            ),
            model_monitoring_job_id=_TEST_MODEL_MONITORING_JOB_USER_ID,
        )
        create_model_monitoring_job_mock.assert_called_once_with(
            request=gca_model_monitoring_service.CreateModelMonitoringJobRequest(
                parent=_TEST_MODEL_MONITOR_RESOURCE_NAME,
                model_monitoring_job=_TEST_CREATE_MODEL_MONITORING_JOB_OBJ,
                model_monitoring_job_id=_TEST_MODEL_MONITORING_JOB_USER_ID,
            )
        )

    @pytest.mark.usefixtures(
        "create_model_monitoring_job_mock",
        "create_model_monitor_mock",
        "search_metrics_mock",
    )
    def test_search_metrics(self, search_metrics_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        test_model_monitor = ModelMonitor.create(
            training_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            model_name=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
            display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
        )
        test_model_monitor.run(
            display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
            target_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_TARGET_RESOURCE
            ),
        )
        test_model_monitor.search_metrics(
            model_monitoring_job_name=_TEST_MODEL_MONITORING_JOB_RESOURCE_NAME
        )
        search_metrics_mock.assert_called_once_with(request=_TEST_SEARCH_REQUEST)

    @pytest.mark.usefixtures(
        "create_model_monitoring_job_mock",
        "create_model_monitor_mock",
        "search_alerts_mock",
    )
    def test_search_alerts(self, search_alerts_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        test_model_monitor = ModelMonitor.create(
            training_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            model_name=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
            display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
        )
        test_model_monitor.run(
            display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
            target_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_TARGET_RESOURCE
            ),
        )
        test_model_monitor.search_alerts(
            model_monitoring_job_name=_TEST_MODEL_MONITORING_JOB_RESOURCE_NAME
        )
        search_alerts_mock.assert_called_once_with(request=_TEST_SEARCH_ALERTS_REQUEST)

    @pytest.mark.usefixtures("create_model_monitor_mock", "delete_model_monitor_mock")
    @pytest.mark.parametrize("force", [True, False])
    def test_delete_model_monitor(self, delete_model_monitor_mock, force):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        test_model_monitor = ModelMonitor.create(
            training_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            model_name=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
            display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
        )
        test_model_monitor.delete(force=force)
        delete_model_monitor_mock.assert_called_once_with(
            request=gca_model_monitoring_service.DeleteModelMonitorRequest(
                name=_TEST_MODEL_MONITOR_RESOURCE_NAME, force=force
            )
        )

    @pytest.mark.usefixtures("create_model_monitoring_job_mock")
    def test_create_model_monitoring_job(self, create_model_monitoring_job_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        ModelMonitoringJob.create(
            display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
            model_monitor_name=_TEST_MODEL_MONITOR_RESOURCE_NAME,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            baseline_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            target_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_TARGET_RESOURCE
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
            explanation_spec=explanation.ExplanationSpec(),
        )
        create_model_monitoring_job_mock.assert_called_once_with(
            request=gca_model_monitoring_service.CreateModelMonitoringJobRequest(
                parent=_TEST_MODEL_MONITOR_RESOURCE_NAME,
                model_monitoring_job=_TEST_CREATE_MODEL_MONITORING_JOB_OBJ,
            )
        )

    @pytest.mark.usefixtures(
        "create_model_monitor_mock",
        "create_model_monitoring_job_mock",
        "delete_model_monitoring_job_mock",
    )
    def test_delete_model_monitoring_job(self, delete_model_monitoring_job_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        test_job = ModelMonitoringJob.create(
            display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
            model_monitor_name=_TEST_MODEL_MONITOR_RESOURCE_NAME,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            baseline_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            target_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_TARGET_RESOURCE
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
        )
        test_job.delete()
        delete_model_monitoring_job_mock.assert_called_once_with(
            name=_TEST_MODEL_MONITORING_JOB_RESOURCE_NAME
        )

    @pytest.mark.usefixtures(
        "create_model_monitor_mock",
        "get_model_monitoring_job_mock",
        "create_model_monitoring_job_mock",
    )
    def test_get_model_monitoring_job(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        test_model_monitor = ModelMonitor.create(
            training_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_BASELINE_RESOURCE
            ),
            model_name=_TEST_MODEL_NAME,
            model_version_id=_TEST_MODEL_VERSION_ID,
            display_name=_TEST_MODEL_MONITOR_DISPLAY_NAME,
            tabular_objective_spec=ml_monitoring.spec.TabularObjective(
                feature_drift_spec=ml_monitoring.spec.DataDriftSpec(
                    default_categorical_alert_threshold=0.1,
                    default_numeric_alert_threshold=0.2,
                ),
            ),
            output_spec=ml_monitoring.spec.OutputSpec(gcs_base_dir=_TEST_OUTPUT_PATH),
            notification_spec=ml_monitoring.spec.NotificationSpec(
                user_emails=[_TEST_NOTIFICATION_EMAIL]
            ),
        )
        test_model_monitor.run(
            display_name=_TEST_MODEL_MONITORING_JOB_DISPLAY_NAME,
            target_dataset=ml_monitoring.spec.MonitoringInput(
                vertex_dataset=_TEST_TARGET_RESOURCE
            ),
        )
        test_model_monitoring_job = test_model_monitor.get_model_monitoring_job(
            model_monitoring_job_name=_TEST_MODEL_MONITORING_JOB_RESOURCE_NAME
        )
        assert isinstance(test_model_monitoring_job, ModelMonitoringJob)


# TODO: Add unit tests for visualization methods.
