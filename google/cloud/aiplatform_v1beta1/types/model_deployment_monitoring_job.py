# -*- coding: utf-8 -*-
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
import proto  # type: ignore

from google.cloud.aiplatform_v1beta1.types import encryption_spec as gca_encryption_spec
from google.cloud.aiplatform_v1beta1.types import feature_monitoring_stats
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import job_state
from google.cloud.aiplatform_v1beta1.types import model_monitoring
from google.protobuf import duration_pb2  # type: ignore
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "ModelDeploymentMonitoringObjectiveType",
        "ModelDeploymentMonitoringJob",
        "ModelDeploymentMonitoringBigQueryTable",
        "ModelDeploymentMonitoringObjectiveConfig",
        "ModelDeploymentMonitoringScheduleConfig",
        "ModelMonitoringStatsAnomalies",
    },
)


class ModelDeploymentMonitoringObjectiveType(proto.Enum):
    r"""The Model Monitoring Objective types."""
    MODEL_DEPLOYMENT_MONITORING_OBJECTIVE_TYPE_UNSPECIFIED = 0
    RAW_FEATURE_SKEW = 1
    RAW_FEATURE_DRIFT = 2
    FEATURE_ATTRIBUTION_SKEW = 3
    FEATURE_ATTRIBUTION_DRIFT = 4


class ModelDeploymentMonitoringJob(proto.Message):
    r"""Represents a job that runs periodically to monitor the
    deployed models in an endpoint. It will analyze the logged
    training & prediction data to detect any abnormal behaviors.

    Attributes:
        name (str):
            Output only. Resource name of a
            ModelDeploymentMonitoringJob.
        display_name (str):
            Required. The user-defined name of the
            ModelDeploymentMonitoringJob. The name can be up
            to 128 characters long and can be consist of any
            UTF-8 characters.
            Display name of a ModelDeploymentMonitoringJob.
        endpoint (str):
            Required. Endpoint resource name. Format:
            ``projects/{project}/locations/{location}/endpoints/{endpoint}``
        state (google.cloud.aiplatform_v1beta1.types.JobState):
            Output only. The detailed state of the
            monitoring job. When the job is still creating,
            the state will be 'PENDING'. Once the job is
            successfully created, the state will be
            'RUNNING'. Pause the job, the state will be
            'PAUSED'.
            Resume the job, the state will return to
            'RUNNING'.
        schedule_state (google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringJob.MonitoringScheduleState):
            Output only. Schedule state when the
            monitoring job is in Running state.
        model_deployment_monitoring_objective_configs (Sequence[google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringObjectiveConfig]):
            Required. The config for monitoring
            objectives. This is a per DeployedModel config.
            Each DeployedModel needs to be configured
            separately.
        model_deployment_monitoring_schedule_config (google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringScheduleConfig):
            Required. Schedule config for running the
            monitoring job.
        logging_sampling_strategy (google.cloud.aiplatform_v1beta1.types.SamplingStrategy):
            Required. Sample Strategy for logging.
        model_monitoring_alert_config (google.cloud.aiplatform_v1beta1.types.ModelMonitoringAlertConfig):
            Alert config for model monitoring.
        predict_instance_schema_uri (str):
            YAML schema file uri describing the format of
            a single instance, which are given to format
            this Endpoint's prediction (and explanation). If
            not set, we will generate predict schema from
            collected predict requests.
        sample_predict_instance (google.protobuf.struct_pb2.Value):
            Sample Predict instance, same format as
            [PredictRequest.instances][google.cloud.aiplatform.v1beta1.PredictRequest.instances],
            this can be set as a replacement of
            [ModelDeploymentMonitoringJob.predict_instance_schema_uri][google.cloud.aiplatform.v1beta1.ModelDeploymentMonitoringJob.predict_instance_schema_uri].
            If not set, we will generate predict schema from collected
            predict requests.
        analysis_instance_schema_uri (str):
            YAML schema file uri describing the format of a single
            instance that you want Tensorflow Data Validation (TFDV) to
            analyze.

            If this field is empty, all the feature data types are
            inferred from
            [predict_instance_schema_uri][google.cloud.aiplatform.v1beta1.ModelDeploymentMonitoringJob.predict_instance_schema_uri],
            meaning that TFDV will use the data in the exact format(data
            type) as prediction request/response. If there are any data
            type differences between predict instance and TFDV instance,
            this field can be used to override the schema. For models
            trained with Vertex AI, this field must be set as all the
            fields in predict instance formatted as string.
        bigquery_tables (Sequence[google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringBigQueryTable]):
            Output only. The created bigquery tables for
            the job under customer project. Customer could
            do their own query & analysis. There could be 4
            log tables in maximum:
            1. Training data logging predict
            request/response 2. Serving data logging predict
            request/response
        log_ttl (google.protobuf.duration_pb2.Duration):
            The TTL of BigQuery tables in user projects
            which stores logs. A day is the basic unit of
            the TTL and we take the ceil of TTL/86400(a
            day). e.g. { second: 3600} indicates ttl = 1
            day.
        labels (Sequence[google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringJob.LabelsEntry]):
            The labels with user-defined metadata to
            organize your ModelDeploymentMonitoringJob.

            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            and examples of labels.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            ModelDeploymentMonitoringJob was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            ModelDeploymentMonitoringJob was updated most
            recently.
        next_schedule_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this monitoring
            pipeline will be scheduled to run for the next
            round.
        stats_anomalies_base_directory (google.cloud.aiplatform_v1beta1.types.GcsDestination):
            Stats anomalies base folder path.
        encryption_spec (google.cloud.aiplatform_v1beta1.types.EncryptionSpec):
            Customer-managed encryption key spec for a
            ModelDeploymentMonitoringJob. If set, this
            ModelDeploymentMonitoringJob and all sub-
            resources of this ModelDeploymentMonitoringJob
            will be secured by this key.
        error (google.rpc.status_pb2.Status):
            Output only. Only populated when the job's state is
            ``JOB_STATE_FAILED`` or ``JOB_STATE_CANCELLED``.
    """

    class MonitoringScheduleState(proto.Enum):
        r"""The state to Specify the monitoring pipeline."""
        MONITORING_SCHEDULE_STATE_UNSPECIFIED = 0
        PENDING = 1
        OFFLINE = 2
        RUNNING = 3

    name = proto.Field(proto.STRING, number=1,)
    display_name = proto.Field(proto.STRING, number=2,)
    endpoint = proto.Field(proto.STRING, number=3,)
    state = proto.Field(proto.ENUM, number=4, enum=job_state.JobState,)
    schedule_state = proto.Field(proto.ENUM, number=5, enum=MonitoringScheduleState,)
    model_deployment_monitoring_objective_configs = proto.RepeatedField(
        proto.MESSAGE, number=6, message="ModelDeploymentMonitoringObjectiveConfig",
    )
    model_deployment_monitoring_schedule_config = proto.Field(
        proto.MESSAGE, number=7, message="ModelDeploymentMonitoringScheduleConfig",
    )
    logging_sampling_strategy = proto.Field(
        proto.MESSAGE, number=8, message=model_monitoring.SamplingStrategy,
    )
    model_monitoring_alert_config = proto.Field(
        proto.MESSAGE, number=15, message=model_monitoring.ModelMonitoringAlertConfig,
    )
    predict_instance_schema_uri = proto.Field(proto.STRING, number=9,)
    sample_predict_instance = proto.Field(
        proto.MESSAGE, number=19, message=struct_pb2.Value,
    )
    analysis_instance_schema_uri = proto.Field(proto.STRING, number=16,)
    bigquery_tables = proto.RepeatedField(
        proto.MESSAGE, number=10, message="ModelDeploymentMonitoringBigQueryTable",
    )
    log_ttl = proto.Field(proto.MESSAGE, number=17, message=duration_pb2.Duration,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=11,)
    create_time = proto.Field(
        proto.MESSAGE, number=12, message=timestamp_pb2.Timestamp,
    )
    update_time = proto.Field(
        proto.MESSAGE, number=13, message=timestamp_pb2.Timestamp,
    )
    next_schedule_time = proto.Field(
        proto.MESSAGE, number=14, message=timestamp_pb2.Timestamp,
    )
    stats_anomalies_base_directory = proto.Field(
        proto.MESSAGE, number=20, message=io.GcsDestination,
    )
    encryption_spec = proto.Field(
        proto.MESSAGE, number=21, message=gca_encryption_spec.EncryptionSpec,
    )
    error = proto.Field(proto.MESSAGE, number=23, message=status_pb2.Status,)


class ModelDeploymentMonitoringBigQueryTable(proto.Message):
    r"""ModelDeploymentMonitoringBigQueryTable specifies the BigQuery
    table name as well as some information of the logs stored in
    this table.

    Attributes:
        log_source (google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringBigQueryTable.LogSource):
            The source of log.
        log_type (google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringBigQueryTable.LogType):
            The type of log.
        bigquery_table_path (str):
            The created BigQuery table to store logs. Customer could do
            their own query & analysis. Format:
            ``bq://<project_id>.model_deployment_monitoring_<endpoint_id>.<tolower(log_source)>_<tolower(log_type)>``
    """

    class LogSource(proto.Enum):
        r"""Indicates where does the log come from."""
        LOG_SOURCE_UNSPECIFIED = 0
        TRAINING = 1
        SERVING = 2

    class LogType(proto.Enum):
        r"""Indicates what type of traffic does the log belong to."""
        LOG_TYPE_UNSPECIFIED = 0
        PREDICT = 1
        EXPLAIN = 2

    log_source = proto.Field(proto.ENUM, number=1, enum=LogSource,)
    log_type = proto.Field(proto.ENUM, number=2, enum=LogType,)
    bigquery_table_path = proto.Field(proto.STRING, number=3,)


class ModelDeploymentMonitoringObjectiveConfig(proto.Message):
    r"""ModelDeploymentMonitoringObjectiveConfig contains the pair of
    deployed_model_id to ModelMonitoringObjectiveConfig.

    Attributes:
        deployed_model_id (str):
            The DeployedModel ID of the objective config.
        objective_config (google.cloud.aiplatform_v1beta1.types.ModelMonitoringObjectiveConfig):
            The objective config of for the
            modelmonitoring job of this deployed model.
    """

    deployed_model_id = proto.Field(proto.STRING, number=1,)
    objective_config = proto.Field(
        proto.MESSAGE,
        number=2,
        message=model_monitoring.ModelMonitoringObjectiveConfig,
    )


class ModelDeploymentMonitoringScheduleConfig(proto.Message):
    r"""The config for scheduling monitoring job.
    Attributes:
        monitor_interval (google.protobuf.duration_pb2.Duration):
            Required. The model monitoring job running
            interval. It will be rounded up to next full
            hour.
    """

    monitor_interval = proto.Field(
        proto.MESSAGE, number=1, message=duration_pb2.Duration,
    )


class ModelMonitoringStatsAnomalies(proto.Message):
    r"""Statistics and anomalies generated by Model Monitoring.
    Attributes:
        objective (google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringObjectiveType):
            Model Monitoring Objective those stats and
            anomalies belonging to.
        deployed_model_id (str):
            Deployed Model ID.
        anomaly_count (int):
            Number of anomalies within all stats.
        feature_stats (Sequence[google.cloud.aiplatform_v1beta1.types.ModelMonitoringStatsAnomalies.FeatureHistoricStatsAnomalies]):
            A list of historical Stats and Anomalies
            generated for all Features.
    """

    class FeatureHistoricStatsAnomalies(proto.Message):
        r"""Historical Stats (and Anomalies) for a specific Feature.
        Attributes:
            feature_display_name (str):
                Display Name of the Feature.
            threshold (google.cloud.aiplatform_v1beta1.types.ThresholdConfig):
                Threshold for anomaly detection.
            training_stats (google.cloud.aiplatform_v1beta1.types.FeatureStatsAnomaly):
                Stats calculated for the Training Dataset.
            prediction_stats (Sequence[google.cloud.aiplatform_v1beta1.types.FeatureStatsAnomaly]):
                A list of historical stats generated by
                different time window's Prediction Dataset.
        """

        feature_display_name = proto.Field(proto.STRING, number=1,)
        threshold = proto.Field(
            proto.MESSAGE, number=3, message=model_monitoring.ThresholdConfig,
        )
        training_stats = proto.Field(
            proto.MESSAGE,
            number=4,
            message=feature_monitoring_stats.FeatureStatsAnomaly,
        )
        prediction_stats = proto.RepeatedField(
            proto.MESSAGE,
            number=5,
            message=feature_monitoring_stats.FeatureStatsAnomaly,
        )

    objective = proto.Field(
        proto.ENUM, number=1, enum="ModelDeploymentMonitoringObjectiveType",
    )
    deployed_model_id = proto.Field(proto.STRING, number=2,)
    anomaly_count = proto.Field(proto.INT32, number=3,)
    feature_stats = proto.RepeatedField(
        proto.MESSAGE, number=4, message=FeatureHistoricStatsAnomalies,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
