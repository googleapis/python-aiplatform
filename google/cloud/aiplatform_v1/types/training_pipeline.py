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

from google.cloud.aiplatform_v1.types import encryption_spec as gca_encryption_spec
from google.cloud.aiplatform_v1.types import io
from google.cloud.aiplatform_v1.types import model
from google.cloud.aiplatform_v1.types import pipeline_state
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "TrainingPipeline",
        "InputDataConfig",
        "FractionSplit",
        "FilterSplit",
        "PredefinedSplit",
        "TimestampSplit",
    },
)


class TrainingPipeline(proto.Message):
    r"""The TrainingPipeline orchestrates tasks associated with training a
    Model. It always executes the training task, and optionally may also
    export data from Vertex AI's Dataset which becomes the training
    input, [upload][google.cloud.aiplatform.v1.ModelService.UploadModel]
    the Model to Vertex AI, and evaluate the Model.

    Attributes:
        name (str):
            Output only. Resource name of the
            TrainingPipeline.
        display_name (str):
            Required. The user-defined name of this
            TrainingPipeline.
        input_data_config (google.cloud.aiplatform_v1.types.InputDataConfig):
            Specifies Vertex AI owned input data that may be used for
            training the Model. The TrainingPipeline's
            [training_task_definition][google.cloud.aiplatform.v1.TrainingPipeline.training_task_definition]
            should make clear whether this config is used and if there
            are any special requirements on how it should be filled. If
            nothing about this config is mentioned in the
            [training_task_definition][google.cloud.aiplatform.v1.TrainingPipeline.training_task_definition],
            then it should be assumed that the TrainingPipeline does not
            depend on this configuration.
        training_task_definition (str):
            Required. A Google Cloud Storage path to the
            YAML file that defines the training task which
            is responsible for producing the model artifact,
            and may also include additional auxiliary work.
            The definition files that can be used here are
            found in gs://google-cloud-
            aiplatform/schema/trainingjob/definition/. Note:
            The URI given on output will be immutable and
            probably different, including the URI scheme,
            than the one given on input. The output URI will
            point to a location where the user only has a
            read access.
        training_task_inputs (google.protobuf.struct_pb2.Value):
            Required. The training task's parameter(s), as specified in
            the
            [training_task_definition][google.cloud.aiplatform.v1.TrainingPipeline.training_task_definition]'s
            ``inputs``.
        training_task_metadata (google.protobuf.struct_pb2.Value):
            Output only. The metadata information as specified in the
            [training_task_definition][google.cloud.aiplatform.v1.TrainingPipeline.training_task_definition]'s
            ``metadata``. This metadata is an auxiliary runtime and
            final information about the training task. While the
            pipeline is running this information is populated only at a
            best effort basis. Only present if the pipeline's
            [training_task_definition][google.cloud.aiplatform.v1.TrainingPipeline.training_task_definition]
            contains ``metadata`` object.
        model_to_upload (google.cloud.aiplatform_v1.types.Model):
            Describes the Model that may be uploaded (via
            [ModelService.UploadModel][google.cloud.aiplatform.v1.ModelService.UploadModel])
            by this TrainingPipeline. The TrainingPipeline's
            [training_task_definition][google.cloud.aiplatform.v1.TrainingPipeline.training_task_definition]
            should make clear whether this Model description should be
            populated, and if there are any special requirements
            regarding how it should be filled. If nothing is mentioned
            in the
            [training_task_definition][google.cloud.aiplatform.v1.TrainingPipeline.training_task_definition],
            then it should be assumed that this field should not be
            filled and the training task either uploads the Model
            without a need of this information, or that training task
            does not support uploading a Model as part of the pipeline.
            When the Pipeline's state becomes
            ``PIPELINE_STATE_SUCCEEDED`` and the trained Model had been
            uploaded into Vertex AI, then the model_to_upload's resource
            [name][google.cloud.aiplatform.v1.Model.name] is populated.
            The Model is always uploaded into the Project and Location
            in which this pipeline is.
        state (google.cloud.aiplatform_v1.types.PipelineState):
            Output only. The detailed state of the
            pipeline.
        error (google.rpc.status_pb2.Status):
            Output only. Only populated when the pipeline's state is
            ``PIPELINE_STATE_FAILED`` or ``PIPELINE_STATE_CANCELLED``.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the TrainingPipeline
            was created.
        start_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the TrainingPipeline for the first
            time entered the ``PIPELINE_STATE_RUNNING`` state.
        end_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the TrainingPipeline entered any of
            the following states: ``PIPELINE_STATE_SUCCEEDED``,
            ``PIPELINE_STATE_FAILED``, ``PIPELINE_STATE_CANCELLED``.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the TrainingPipeline
            was most recently updated.
        labels (Sequence[google.cloud.aiplatform_v1.types.TrainingPipeline.LabelsEntry]):
            The labels with user-defined metadata to
            organize TrainingPipelines.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            and examples of labels.
        encryption_spec (google.cloud.aiplatform_v1.types.EncryptionSpec):
            Customer-managed encryption key spec for a TrainingPipeline.
            If set, this TrainingPipeline will be secured by this key.

            Note: Model trained by this TrainingPipeline is also secured
            by this key if
            [model_to_upload][google.cloud.aiplatform.v1.TrainingPipeline.encryption_spec]
            is not set separately.
    """

    name = proto.Field(proto.STRING, number=1,)
    display_name = proto.Field(proto.STRING, number=2,)
    input_data_config = proto.Field(proto.MESSAGE, number=3, message="InputDataConfig",)
    training_task_definition = proto.Field(proto.STRING, number=4,)
    training_task_inputs = proto.Field(
        proto.MESSAGE, number=5, message=struct_pb2.Value,
    )
    training_task_metadata = proto.Field(
        proto.MESSAGE, number=6, message=struct_pb2.Value,
    )
    model_to_upload = proto.Field(proto.MESSAGE, number=7, message=model.Model,)
    state = proto.Field(proto.ENUM, number=9, enum=pipeline_state.PipelineState,)
    error = proto.Field(proto.MESSAGE, number=10, message=status_pb2.Status,)
    create_time = proto.Field(
        proto.MESSAGE, number=11, message=timestamp_pb2.Timestamp,
    )
    start_time = proto.Field(proto.MESSAGE, number=12, message=timestamp_pb2.Timestamp,)
    end_time = proto.Field(proto.MESSAGE, number=13, message=timestamp_pb2.Timestamp,)
    update_time = proto.Field(
        proto.MESSAGE, number=14, message=timestamp_pb2.Timestamp,
    )
    labels = proto.MapField(proto.STRING, proto.STRING, number=15,)
    encryption_spec = proto.Field(
        proto.MESSAGE, number=18, message=gca_encryption_spec.EncryptionSpec,
    )


class InputDataConfig(proto.Message):
    r"""Specifies Vertex AI owned input data to be used for training,
    and possibly evaluating, the Model.

    Attributes:
        fraction_split (google.cloud.aiplatform_v1.types.FractionSplit):
            Split based on fractions defining the size of
            each set.
        filter_split (google.cloud.aiplatform_v1.types.FilterSplit):
            Split based on the provided filters for each
            set.
        predefined_split (google.cloud.aiplatform_v1.types.PredefinedSplit):
            Supported only for tabular Datasets.
            Split based on a predefined key.
        timestamp_split (google.cloud.aiplatform_v1.types.TimestampSplit):
            Supported only for tabular Datasets.
            Split based on the timestamp of the input data
            pieces.
        gcs_destination (google.cloud.aiplatform_v1.types.GcsDestination):
            The Cloud Storage location where the training data is to be
            written to. In the given directory a new directory is
            created with name:
            ``dataset-<dataset-id>-<annotation-type>-<timestamp-of-training-call>``
            where timestamp is in YYYY-MM-DDThh:mm:ss.sssZ ISO-8601
            format. All training input data is written into that
            directory.

            The Vertex AI environment variables representing Cloud
            Storage data URIs are represented in the Cloud Storage
            wildcard format to support sharded data. e.g.:
            "gs://.../training-*.jsonl"

            -  AIP_DATA_FORMAT = "jsonl" for non-tabular data, "csv" for
               tabular data

            -  AIP_TRAINING_DATA_URI =
               "gcs_destination/dataset---/training-*.${AIP_DATA_FORMAT}"

            -  AIP_VALIDATION_DATA_URI =
               "gcs_destination/dataset---/validation-*.${AIP_DATA_FORMAT}"

            -  AIP_TEST_DATA_URI =
               "gcs_destination/dataset---/test-*.${AIP_DATA_FORMAT}".
        bigquery_destination (google.cloud.aiplatform_v1.types.BigQueryDestination):
            Only applicable to custom training with tabular Dataset with
            BigQuery source.

            The BigQuery project location where the training data is to
            be written to. In the given project a new dataset is created
            with name
            ``dataset_<dataset-id>_<annotation-type>_<timestamp-of-training-call>``
            where timestamp is in YYYY_MM_DDThh_mm_ss_sssZ format. All
            training input data is written into that dataset. In the
            dataset three tables are created, ``training``,
            ``validation`` and ``test``.

            -  AIP_DATA_FORMAT = "bigquery".

            -  AIP_TRAINING_DATA_URI =
               "bigquery_destination.dataset\_\ **\ .training"

            -  AIP_VALIDATION_DATA_URI =
               "bigquery_destination.dataset\_\ **\ .validation"

            -  AIP_TEST_DATA_URI =
               "bigquery_destination.dataset\_\ **\ .test".
        dataset_id (str):
            Required. The ID of the Dataset in the same Project and
            Location which data will be used to train the Model. The
            Dataset must use schema compatible with Model being trained,
            and what is compatible should be described in the used
            TrainingPipeline's [training_task_definition]
            [google.cloud.aiplatform.v1.TrainingPipeline.training_task_definition].
            For tabular Datasets, all their data is exported to
            training, to pick and choose from.
        annotations_filter (str):
            Applicable only to Datasets that have DataItems and
            Annotations.

            A filter on Annotations of the Dataset. Only Annotations
            that both match this filter and belong to DataItems not
            ignored by the split method are used in respectively
            training, validation or test role, depending on the role of
            the DataItem they are on (for the auto-assigned that role is
            decided by Vertex AI). A filter with same syntax as the one
            used in
            [ListAnnotations][google.cloud.aiplatform.v1.DatasetService.ListAnnotations]
            may be used, but note here it filters across all Annotations
            of the Dataset, and not just within a single DataItem.
        annotation_schema_uri (str):
            Applicable only to custom training with Datasets that have
            DataItems and Annotations.

            Cloud Storage URI that points to a YAML file describing the
            annotation schema. The schema is defined as an OpenAPI 3.0.2
            `Schema
            Object <https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md#schemaObject>`__.
            The schema files that can be used here are found in
            gs://google-cloud-aiplatform/schema/dataset/annotation/ ,
            note that the chosen schema must be consistent with
            [metadata][google.cloud.aiplatform.v1.Dataset.metadata_schema_uri]
            of the Dataset specified by
            [dataset_id][google.cloud.aiplatform.v1.InputDataConfig.dataset_id].

            Only Annotations that both match this schema and belong to
            DataItems not ignored by the split method are used in
            respectively training, validation or test role, depending on
            the role of the DataItem they are on.

            When used in conjunction with
            [annotations_filter][google.cloud.aiplatform.v1.InputDataConfig.annotations_filter],
            the Annotations used for training are filtered by both
            [annotations_filter][google.cloud.aiplatform.v1.InputDataConfig.annotations_filter]
            and
            [annotation_schema_uri][google.cloud.aiplatform.v1.InputDataConfig.annotation_schema_uri].
    """

    fraction_split = proto.Field(
        proto.MESSAGE, number=2, oneof="split", message="FractionSplit",
    )
    filter_split = proto.Field(
        proto.MESSAGE, number=3, oneof="split", message="FilterSplit",
    )
    predefined_split = proto.Field(
        proto.MESSAGE, number=4, oneof="split", message="PredefinedSplit",
    )
    timestamp_split = proto.Field(
        proto.MESSAGE, number=5, oneof="split", message="TimestampSplit",
    )
    gcs_destination = proto.Field(
        proto.MESSAGE, number=8, oneof="destination", message=io.GcsDestination,
    )
    bigquery_destination = proto.Field(
        proto.MESSAGE, number=10, oneof="destination", message=io.BigQueryDestination,
    )
    dataset_id = proto.Field(proto.STRING, number=1,)
    annotations_filter = proto.Field(proto.STRING, number=6,)
    annotation_schema_uri = proto.Field(proto.STRING, number=9,)


class FractionSplit(proto.Message):
    r"""Assigns the input data to training, validation, and test sets as per
    the given fractions. Any of ``training_fraction``,
    ``validation_fraction`` and ``test_fraction`` may optionally be
    provided, they must sum to up to 1. If the provided ones sum to less
    than 1, the remainder is assigned to sets as decided by Vertex AI.
    If none of the fractions are set, by default roughly 80% of data is
    used for training, 10% for validation, and 10% for test.

    Attributes:
        training_fraction (float):
            The fraction of the input data that is to be
            used to train the Model.
        validation_fraction (float):
            The fraction of the input data that is to be
            used to validate the Model.
        test_fraction (float):
            The fraction of the input data that is to be
            used to evaluate the Model.
    """

    training_fraction = proto.Field(proto.DOUBLE, number=1,)
    validation_fraction = proto.Field(proto.DOUBLE, number=2,)
    test_fraction = proto.Field(proto.DOUBLE, number=3,)


class FilterSplit(proto.Message):
    r"""Assigns input data to training, validation, and test sets
    based on the given filters, data pieces not matched by any
    filter are ignored. Currently only supported for Datasets
    containing DataItems.
    If any of the filters in this message are to match nothing, then
    they can be set as '-' (the minus sign).

    Supported only for unstructured Datasets.

    Attributes:
        training_filter (str):
            Required. A filter on DataItems of the Dataset. DataItems
            that match this filter are used to train the Model. A filter
            with same syntax as the one used in
            [DatasetService.ListDataItems][google.cloud.aiplatform.v1.DatasetService.ListDataItems]
            may be used. If a single DataItem is matched by more than
            one of the FilterSplit filters, then it is assigned to the
            first set that applies to it in the training, validation,
            test order.
        validation_filter (str):
            Required. A filter on DataItems of the Dataset. DataItems
            that match this filter are used to validate the Model. A
            filter with same syntax as the one used in
            [DatasetService.ListDataItems][google.cloud.aiplatform.v1.DatasetService.ListDataItems]
            may be used. If a single DataItem is matched by more than
            one of the FilterSplit filters, then it is assigned to the
            first set that applies to it in the training, validation,
            test order.
        test_filter (str):
            Required. A filter on DataItems of the Dataset. DataItems
            that match this filter are used to test the Model. A filter
            with same syntax as the one used in
            [DatasetService.ListDataItems][google.cloud.aiplatform.v1.DatasetService.ListDataItems]
            may be used. If a single DataItem is matched by more than
            one of the FilterSplit filters, then it is assigned to the
            first set that applies to it in the training, validation,
            test order.
    """

    training_filter = proto.Field(proto.STRING, number=1,)
    validation_filter = proto.Field(proto.STRING, number=2,)
    test_filter = proto.Field(proto.STRING, number=3,)


class PredefinedSplit(proto.Message):
    r"""Assigns input data to training, validation, and test sets
    based on the value of a provided key.

    Supported only for tabular Datasets.

    Attributes:
        key (str):
            Required. The key is a name of one of the Dataset's data
            columns. The value of the key (either the label's value or
            value in the column) must be one of {``training``,
            ``validation``, ``test``}, and it defines to which set the
            given piece of data is assigned. If for a piece of data the
            key is not present or has an invalid value, that piece is
            ignored by the pipeline.
    """

    key = proto.Field(proto.STRING, number=1,)


class TimestampSplit(proto.Message):
    r"""Assigns input data to training, validation, and test sets
    based on a provided timestamps. The youngest data pieces are
    assigned to training set, next to validation set, and the oldest
    to the test set.
    Supported only for tabular Datasets.

    Attributes:
        training_fraction (float):
            The fraction of the input data that is to be
            used to train the Model.
        validation_fraction (float):
            The fraction of the input data that is to be
            used to validate the Model.
        test_fraction (float):
            The fraction of the input data that is to be
            used to evaluate the Model.
        key (str):
            Required. The key is a name of one of the Dataset's data
            columns. The values of the key (the values in the column)
            must be in RFC 3339 ``date-time`` format, where
            ``time-offset`` = ``"Z"`` (e.g. 1985-04-12T23:20:50.52Z). If
            for a piece of data the key is not present or has an invalid
            value, that piece is ignored by the pipeline.
    """

    training_fraction = proto.Field(proto.DOUBLE, number=1,)
    validation_fraction = proto.Field(proto.DOUBLE, number=2,)
    test_fraction = proto.Field(proto.DOUBLE, number=3,)
    key = proto.Field(proto.STRING, number=4,)


__all__ = tuple(sorted(__protobuf__.manifest))
