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

from google.cloud.aiplatform_v1beta1.types import (
    completion_stats as gca_completion_stats,
)
from google.cloud.aiplatform_v1beta1.types import encryption_spec as gca_encryption_spec
from google.cloud.aiplatform_v1beta1.types import explanation
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import job_state
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import (
    manual_batch_tuning_parameters as gca_manual_batch_tuning_parameters,
)
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1", manifest={"BatchPredictionJob",},
)


class BatchPredictionJob(proto.Message):
    r"""A job that uses a
    [Model][google.cloud.aiplatform.v1beta1.BatchPredictionJob.model] to
    produce predictions on multiple [input
    instances][google.cloud.aiplatform.v1beta1.BatchPredictionJob.input_config].
    If predictions for significant portion of the instances fail, the
    job may finish without attempting predictions for all remaining
    instances.

    Attributes:
        name (str):
            Output only. Resource name of the
            BatchPredictionJob.
        display_name (str):
            Required. The user-defined name of this
            BatchPredictionJob.
        model (str):
            Required. The name of the Model that produces
            the predictions via this job, must share the
            same ancestor Location. Starting this job has no
            impact on any existing deployments of the Model
            and their resources.
        input_config (google.cloud.aiplatform_v1beta1.types.BatchPredictionJob.InputConfig):
            Required. Input configuration of the instances on which
            predictions are performed. The schema of any single instance
            may be specified via the
            [Model's][google.cloud.aiplatform.v1beta1.BatchPredictionJob.model]
            [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
            [instance_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri].
        model_parameters (google.protobuf.struct_pb2.Value):
            The parameters that govern the predictions. The schema of
            the parameters may be specified via the
            [Model's][google.cloud.aiplatform.v1beta1.BatchPredictionJob.model]
            [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
            [parameters_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.parameters_schema_uri].
        output_config (google.cloud.aiplatform_v1beta1.types.BatchPredictionJob.OutputConfig):
            Required. The Configuration specifying where output
            predictions should be written. The schema of any single
            prediction may be specified as a concatenation of
            [Model's][google.cloud.aiplatform.v1beta1.BatchPredictionJob.model]
            [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
            [instance_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri]
            and
            [prediction_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.prediction_schema_uri].
        dedicated_resources (google.cloud.aiplatform_v1beta1.types.BatchDedicatedResources):
            The config of resources used by the Model during the batch
            prediction. If the Model
            [supports][google.cloud.aiplatform.v1beta1.Model.supported_deployment_resources_types]
            DEDICATED_RESOURCES this config may be provided (and the job
            will use these resources), if the Model doesn't support
            AUTOMATIC_RESOURCES, this config must be provided.
        manual_batch_tuning_parameters (google.cloud.aiplatform_v1beta1.types.ManualBatchTuningParameters):
            Immutable. Parameters configuring the batch behavior.
            Currently only applicable when
            [dedicated_resources][google.cloud.aiplatform.v1beta1.BatchPredictionJob.dedicated_resources]
            are used (in other cases AI Platform does the tuning
            itself).
        generate_explanation (bool):
            Generate explanation with the batch prediction results.

            When set to ``true``, the batch prediction output changes
            based on the ``predictions_format`` field of the
            [BatchPredictionJob.output_config][google.cloud.aiplatform.v1beta1.BatchPredictionJob.output_config]
            object:

            -  ``bigquery``: output includes a column named
               ``explanation``. The value is a struct that conforms to
               the
               [Explanation][google.cloud.aiplatform.v1beta1.Explanation]
               object.
            -  ``jsonl``: The JSON objects on each line include an
               additional entry keyed ``explanation``. The value of the
               entry is a JSON object that conforms to the
               [Explanation][google.cloud.aiplatform.v1beta1.Explanation]
               object.
            -  ``csv``: Generating explanations for CSV format is not
               supported.

            If this field is set to true, either the
            [Model.explanation_spec][google.cloud.aiplatform.v1beta1.Model.explanation_spec]
            or
            [explanation_spec][google.cloud.aiplatform.v1beta1.BatchPredictionJob.explanation_spec]
            must be populated.
        explanation_spec (google.cloud.aiplatform_v1beta1.types.ExplanationSpec):
            Explanation configuration for this BatchPredictionJob. Can
            be specified only if
            [generate_explanation][google.cloud.aiplatform.v1beta1.BatchPredictionJob.generate_explanation]
            is set to ``true``.

            This value overrides the value of
            [Model.explanation_spec][google.cloud.aiplatform.v1beta1.Model.explanation_spec].
            All fields of
            [explanation_spec][google.cloud.aiplatform.v1beta1.BatchPredictionJob.explanation_spec]
            are optional in the request. If a field of the
            [explanation_spec][google.cloud.aiplatform.v1beta1.BatchPredictionJob.explanation_spec]
            object is not populated, the corresponding field of the
            [Model.explanation_spec][google.cloud.aiplatform.v1beta1.Model.explanation_spec]
            object is inherited.
        output_info (google.cloud.aiplatform_v1beta1.types.BatchPredictionJob.OutputInfo):
            Output only. Information further describing
            the output of this job.
        state (google.cloud.aiplatform_v1beta1.types.JobState):
            Output only. The detailed state of the job.
        error (google.rpc.status_pb2.Status):
            Output only. Only populated when the job's state is
            JOB_STATE_FAILED or JOB_STATE_CANCELLED.
        partial_failures (Sequence[google.rpc.status_pb2.Status]):
            Output only. Partial failures encountered.
            For example, single files that can't be read.
            This field never exceeds 20 entries.
            Status details fields contain standard GCP error
            details.
        resources_consumed (google.cloud.aiplatform_v1beta1.types.ResourcesConsumed):
            Output only. Information about resources that
            had been consumed by this job. Provided in real
            time at best effort basis, as well as a final
            value once the job completes.

            Note: This field currently may be not populated
            for batch predictions that use AutoML Models.
        completion_stats (google.cloud.aiplatform_v1beta1.types.CompletionStats):
            Output only. Statistics on completed and
            failed prediction instances.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the BatchPredictionJob
            was created.
        start_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the BatchPredictionJob for the first
            time entered the ``JOB_STATE_RUNNING`` state.
        end_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the BatchPredictionJob entered any of
            the following states: ``JOB_STATE_SUCCEEDED``,
            ``JOB_STATE_FAILED``, ``JOB_STATE_CANCELLED``.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the BatchPredictionJob
            was most recently updated.
        labels (Sequence[google.cloud.aiplatform_v1beta1.types.BatchPredictionJob.LabelsEntry]):
            The labels with user-defined metadata to
            organize BatchPredictionJobs.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            and examples of labels.
        encryption_spec (google.cloud.aiplatform_v1beta1.types.EncryptionSpec):
            Customer-managed encryption key options for a
            BatchPredictionJob. If this is set, then all
            resources created by the BatchPredictionJob will
            be encrypted with the provided encryption key.
    """

    class InputConfig(proto.Message):
        r"""Configures the input to
        [BatchPredictionJob][google.cloud.aiplatform.v1beta1.BatchPredictionJob].
        See
        [Model.supported_input_storage_formats][google.cloud.aiplatform.v1beta1.Model.supported_input_storage_formats]
        for Model's supported input formats, and how instances should be
        expressed via any of them.

        Attributes:
            gcs_source (google.cloud.aiplatform_v1beta1.types.GcsSource):
                The Cloud Storage location for the input
                instances.
            bigquery_source (google.cloud.aiplatform_v1beta1.types.BigQuerySource):
                The BigQuery location of the input table.
                The schema of the table should be in the format
                described by the given context OpenAPI Schema,
                if one is provided. The table may contain
                additional columns that are not described by the
                schema, and they will be ignored.
            instances_format (str):
                Required. The format in which instances are given, must be
                one of the
                [Model's][google.cloud.aiplatform.v1beta1.BatchPredictionJob.model]
                [supported_input_storage_formats][google.cloud.aiplatform.v1beta1.Model.supported_input_storage_formats].
        """

        gcs_source = proto.Field(
            proto.MESSAGE, number=2, oneof="source", message=io.GcsSource,
        )
        bigquery_source = proto.Field(
            proto.MESSAGE, number=3, oneof="source", message=io.BigQuerySource,
        )
        instances_format = proto.Field(proto.STRING, number=1,)

    class OutputConfig(proto.Message):
        r"""Configures the output of
        [BatchPredictionJob][google.cloud.aiplatform.v1beta1.BatchPredictionJob].
        See
        [Model.supported_output_storage_formats][google.cloud.aiplatform.v1beta1.Model.supported_output_storage_formats]
        for supported output formats, and how predictions are expressed via
        any of them.

        Attributes:
            gcs_destination (google.cloud.aiplatform_v1beta1.types.GcsDestination):
                The Cloud Storage location of the directory where the output
                is to be written to. In the given directory a new directory
                is created. Its name is
                ``prediction-<model-display-name>-<job-create-time>``, where
                timestamp is in YYYY-MM-DDThh:mm:ss.sssZ ISO-8601 format.
                Inside of it files ``predictions_0001.<extension>``,
                ``predictions_0002.<extension>``, ...,
                ``predictions_N.<extension>`` are created where
                ``<extension>`` depends on chosen
                [predictions_format][google.cloud.aiplatform.v1beta1.BatchPredictionJob.OutputConfig.predictions_format],
                and N may equal 0001 and depends on the total number of
                successfully predicted instances. If the Model has both
                [instance][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri]
                and
                [prediction][google.cloud.aiplatform.v1beta1.PredictSchemata.parameters_schema_uri]
                schemata defined then each such file contains predictions as
                per the
                [predictions_format][google.cloud.aiplatform.v1beta1.BatchPredictionJob.OutputConfig.predictions_format].
                If prediction for any instance failed (partially or
                completely), then an additional ``errors_0001.<extension>``,
                ``errors_0002.<extension>``,..., ``errors_N.<extension>``
                files are created (N depends on total number of failed
                predictions). These files contain the failed instances, as
                per their schema, followed by an additional ``error`` field
                which as value has ```google.rpc.Status`` <Status>`__
                containing only ``code`` and ``message`` fields.
            bigquery_destination (google.cloud.aiplatform_v1beta1.types.BigQueryDestination):
                The BigQuery project or dataset location where the output is
                to be written to. If project is provided, a new dataset is
                created with name
                ``prediction_<model-display-name>_<job-create-time>`` where
                is made BigQuery-dataset-name compatible (for example, most
                special characters become underscores), and timestamp is in
                YYYY_MM_DDThh_mm_ss_sssZ "based on ISO-8601" format. In the
                dataset two tables will be created, ``predictions``, and
                ``errors``. If the Model has both
                [instance][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri]
                and
                [prediction][google.cloud.aiplatform.v1beta1.PredictSchemata.parameters_schema_uri]
                schemata defined then the tables have columns as follows:
                The ``predictions`` table contains instances for which the
                prediction succeeded, it has columns as per a concatenation
                of the Model's instance and prediction schemata. The
                ``errors`` table contains rows for which the prediction has
                failed, it has instance columns, as per the instance schema,
                followed by a single "errors" column, which as values has
                ```google.rpc.Status`` <Status>`__ represented as a STRUCT,
                and containing only ``code`` and ``message``.
            predictions_format (str):
                Required. The format in which AI Platform gives the
                predictions, must be one of the
                [Model's][google.cloud.aiplatform.v1beta1.BatchPredictionJob.model]
                [supported_output_storage_formats][google.cloud.aiplatform.v1beta1.Model.supported_output_storage_formats].
        """

        gcs_destination = proto.Field(
            proto.MESSAGE, number=2, oneof="destination", message=io.GcsDestination,
        )
        bigquery_destination = proto.Field(
            proto.MESSAGE,
            number=3,
            oneof="destination",
            message=io.BigQueryDestination,
        )
        predictions_format = proto.Field(proto.STRING, number=1,)

    class OutputInfo(proto.Message):
        r"""Further describes this job's output. Supplements
        [output_config][google.cloud.aiplatform.v1beta1.BatchPredictionJob.output_config].

        Attributes:
            gcs_output_directory (str):
                Output only. The full path of the Cloud
                Storage directory created, into which the
                prediction output is written.
            bigquery_output_dataset (str):
                Output only. The path of the BigQuery dataset created, in
                ``bq://projectId.bqDatasetId`` format, into which the
                prediction output is written.
        """

        gcs_output_directory = proto.Field(
            proto.STRING, number=1, oneof="output_location",
        )
        bigquery_output_dataset = proto.Field(
            proto.STRING, number=2, oneof="output_location",
        )

    name = proto.Field(proto.STRING, number=1,)
    display_name = proto.Field(proto.STRING, number=2,)
    model = proto.Field(proto.STRING, number=3,)
    input_config = proto.Field(proto.MESSAGE, number=4, message=InputConfig,)
    model_parameters = proto.Field(proto.MESSAGE, number=5, message=struct_pb2.Value,)
    output_config = proto.Field(proto.MESSAGE, number=6, message=OutputConfig,)
    dedicated_resources = proto.Field(
        proto.MESSAGE, number=7, message=machine_resources.BatchDedicatedResources,
    )
    manual_batch_tuning_parameters = proto.Field(
        proto.MESSAGE,
        number=8,
        message=gca_manual_batch_tuning_parameters.ManualBatchTuningParameters,
    )
    generate_explanation = proto.Field(proto.BOOL, number=23,)
    explanation_spec = proto.Field(
        proto.MESSAGE, number=25, message=explanation.ExplanationSpec,
    )
    output_info = proto.Field(proto.MESSAGE, number=9, message=OutputInfo,)
    state = proto.Field(proto.ENUM, number=10, enum=job_state.JobState,)
    error = proto.Field(proto.MESSAGE, number=11, message=status_pb2.Status,)
    partial_failures = proto.RepeatedField(
        proto.MESSAGE, number=12, message=status_pb2.Status,
    )
    resources_consumed = proto.Field(
        proto.MESSAGE, number=13, message=machine_resources.ResourcesConsumed,
    )
    completion_stats = proto.Field(
        proto.MESSAGE, number=14, message=gca_completion_stats.CompletionStats,
    )
    create_time = proto.Field(
        proto.MESSAGE, number=15, message=timestamp_pb2.Timestamp,
    )
    start_time = proto.Field(proto.MESSAGE, number=16, message=timestamp_pb2.Timestamp,)
    end_time = proto.Field(proto.MESSAGE, number=17, message=timestamp_pb2.Timestamp,)
    update_time = proto.Field(
        proto.MESSAGE, number=18, message=timestamp_pb2.Timestamp,
    )
    labels = proto.MapField(proto.STRING, proto.STRING, number=19,)
    encryption_spec = proto.Field(
        proto.MESSAGE, number=24, message=gca_encryption_spec.EncryptionSpec,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
