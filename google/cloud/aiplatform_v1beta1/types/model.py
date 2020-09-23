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


from google.cloud.aiplatform_v1beta1.types import deployed_model_ref
from google.cloud.aiplatform_v1beta1.types import env_var
from google.cloud.aiplatform_v1beta1.types import explanation
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={"Model", "PredictSchemata", "ModelContainerSpec", "Port",},
)


class Model(proto.Message):
    r"""A trained machine learning Model.

    Attributes:
        name (str):
            The resource name of the Model.
        display_name (str):
            Required. The display name of the Model.
            The name can be up to 128 characters long and
            can be consist of any UTF-8 characters.
        description (str):
            The description of the Model.
        predict_schemata (~.model.PredictSchemata):
            The schemata that describe formats of the Model's
            predictions and explanations as given and returned via
            [PredictionService.Predict][google.cloud.aiplatform.v1beta1.PredictionService.Predict]
            and
            [PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain].
        metadata_schema_uri (str):
            Immutable. Points to a YAML file stored on Google Cloud
            Storage describing additional information about the Model,
            that is specific to it. Unset if the Model does not have any
            additional information. The schema is defined as an OpenAPI
            3.0.2 `Schema
            Object <https://tinyurl.com/y538mdwt#schema-object>`__.
            AutoML Models always have this field populated by AI
            Platform, if no additional metadata is needed this field is
            set to an empty string. Note: The URI given on output will
            be immutable and probably different, including the URI
            scheme, than the one given on input. The output URI will
            point to a location where the user only has a read access.
        metadata (~.struct.Value):
            Immutable. An additional information about the Model; the
            schema of the metadata can be found in
            [metadata_schema][google.cloud.aiplatform.v1beta1.Model.metadata_schema_uri].
            Unset if the Model does not have any additional information.
        supported_export_formats (Sequence[~.model.Model.ExportFormat]):
            Output only. The formats in which this Model
            may be exported. If empty, this Model is not
            avaiable for export.
        training_pipeline (str):
            Output only. The resource name of the
            TrainingPipeline that uploaded this Model, if
            any.
        container_spec (~.model.ModelContainerSpec):
            Input only. The specification of the container that is to be
            used when deploying this Model. The specification is
            ingested upon
            [ModelService.UploadModel][google.cloud.aiplatform.v1beta1.ModelService.UploadModel],
            and all binaries it contains are copied and stored
            internally by AI Platform. Not present for AutoML Models.
        artifact_uri (str):
            Immutable. The path to the directory
            containing the Model artifact and any of its
            supporting files. Not present for AutoML Models.
        supported_deployment_resources_types (Sequence[~.model.Model.DeploymentResourcesType]):
            Output only. When this Model is deployed, its prediction
            resources are described by the ``prediction_resources``
            field of the
            [Endpoint.deployed_models][google.cloud.aiplatform.v1beta1.Endpoint.deployed_models]
            object. Because not all Models support all resource
            configuration types, the configuration types this Model
            supports are listed here. If no configuration types are
            listed, the Model cannot be deployed to an
            [Endpoint][google.cloud.aiplatform.v1beta1.Endpoint] and
            does not support online predictions
            ([PredictionService.Predict][google.cloud.aiplatform.v1beta1.PredictionService.Predict]
            or
            [PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain]).
            Such a Model can serve predictions by using a
            [BatchPredictionJob][google.cloud.aiplatform.v1beta1.BatchPredictionJob],
            if it has at least one entry each in
            [supported_input_storage_formats][google.cloud.aiplatform.v1beta1.Model.supported_input_storage_formats]
            and
            [supported_output_storage_formats][google.cloud.aiplatform.v1beta1.Model.supported_output_storage_formats].
        supported_input_storage_formats (Sequence[str]):
            Output only. The formats this Model supports in
            [BatchPredictionJob.input_config][google.cloud.aiplatform.v1beta1.BatchPredictionJob.input_config].
            If
            [PredictSchemata.instance_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri]
            exists, the instances should be given as per that schema.

            The possible formats are:

            -  ``jsonl`` The JSON Lines format, where each instance is a
               single line. Uses
               [GcsSource][google.cloud.aiplatform.v1beta1.BatchPredictionJob.InputConfig.gcs_source].

            -  ``csv`` The CSV format, where each instance is a single
               comma-separated line. The first line in the file is the
               header, containing comma-separated field names. Uses
               [GcsSource][google.cloud.aiplatform.v1beta1.BatchPredictionJob.InputConfig.gcs_source].

            -  ``tf-record`` The TFRecord format, where each instance is
               a single record in tfrecord syntax. Uses
               [GcsSource][google.cloud.aiplatform.v1beta1.BatchPredictionJob.InputConfig.gcs_source].

            -  ``tf-record-gzip`` Similar to ``tf-record``, but the file
               is gzipped. Uses
               [GcsSource][google.cloud.aiplatform.v1beta1.BatchPredictionJob.InputConfig.gcs_source].

            -  ``bigquery`` Each instance is a single row in BigQuery.
               Uses
               [BigQuerySource][google.cloud.aiplatform.v1beta1.BatchPredictionJob.InputConfig.bigquery_source].

            If this Model doesn't support any of these formats it means
            it cannot be used with a
            [BatchPredictionJob][google.cloud.aiplatform.v1beta1.BatchPredictionJob].
            However, if it has
            [supported_deployment_resources_types][google.cloud.aiplatform.v1beta1.Model.supported_deployment_resources_types],
            it could serve online predictions by using
            [PredictionService.Predict][google.cloud.aiplatform.v1beta1.PredictionService.Predict]
            or
            [PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain].
        supported_output_storage_formats (Sequence[str]):
            Output only. The formats this Model supports in
            [BatchPredictionJob.output_config][google.cloud.aiplatform.v1beta1.BatchPredictionJob.output_config].
            If both
            [PredictSchemata.instance_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri]
            and
            [PredictSchemata.prediction_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.prediction_schema_uri]
            exist, the predictions are returned together with their
            instances. In other words, the prediction has the original
            instance data first, followed by the actual prediction
            content (as per the schema).

            The possible formats are:

            -  ``jsonl`` The JSON Lines format, where each prediction is
               a single line. Uses
               [GcsDestination][google.cloud.aiplatform.v1beta1.BatchPredictionJob.OutputConfig.gcs_destination].

            -  ``csv`` The CSV format, where each prediction is a single
               comma-separated line. The first line in the file is the
               header, containing comma-separated field names. Uses
               [GcsDestination][google.cloud.aiplatform.v1beta1.BatchPredictionJob.OutputConfig.gcs_destination].

            -  ``bigquery`` Each prediction is a single row in a
               BigQuery table, uses
               [BigQueryDestination][google.cloud.aiplatform.v1beta1.BatchPredictionJob.OutputConfig.bigquery_destination]
               .

            If this Model doesn't support any of these formats it means
            it cannot be used with a
            [BatchPredictionJob][google.cloud.aiplatform.v1beta1.BatchPredictionJob].
            However, if it has
            [supported_deployment_resources_types][google.cloud.aiplatform.v1beta1.Model.supported_deployment_resources_types],
            it could serve online predictions by using
            [PredictionService.Predict][google.cloud.aiplatform.v1beta1.PredictionService.Predict]
            or
            [PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain].
        create_time (~.timestamp.Timestamp):
            Output only. Timestamp when this Model was
            uploaded into AI Platform.
        update_time (~.timestamp.Timestamp):
            Output only. Timestamp when this Model was
            most recently updated.
        deployed_models (Sequence[~.deployed_model_ref.DeployedModelRef]):
            Output only. The pointers to DeployedModels
            created from this Model. Note that Model could
            have been deployed to Endpoints in different
            Locations.
        explanation_spec (~.explanation.ExplanationSpec):
            Output only. The default explanation specification for this
            Model.

            Model can be used for [requesting
            explanation][google.cloud.aiplatform.v1beta1.PredictionService.Explain]
            after being
            [deployed][google.cloud.aiplatform.v1beta1.EndpointService.DeployModel]
            iff it is populated.

            All fields of the explanation_spec can be overridden by
            [explanation_spec][google.cloud.aiplatform.v1beta1.DeployedModel.explanation_spec]
            of
            [DeployModelRequest.deployed_model][google.cloud.aiplatform.v1beta1.DeployModelRequest.deployed_model].

            This field is populated only for tabular AutoML Models.
            Specifying it with
            [ModelService.UploadModel][google.cloud.aiplatform.v1beta1.ModelService.UploadModel]
            is not supported.
        etag (str):
            Used to perform consistent read-modify-write
            updates. If not set, a blind "overwrite" update
            happens.
        labels (Sequence[~.model.Model.LabelsEntry]):
            The labels with user-defined metadata to
            organize your Models.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            and examples of labels.
    """

    class DeploymentResourcesType(proto.Enum):
        r"""Identifies a type of Model's prediction resources."""
        DEPLOYMENT_RESOURCES_TYPE_UNSPECIFIED = 0
        DEDICATED_RESOURCES = 1
        AUTOMATIC_RESOURCES = 2

    class ExportFormat(proto.Message):
        r"""Represents a supported by the Model export format.
        All formats export to Google Cloud Storage.

        Attributes:
            id (str):
                Output only. The ID of the export format. The possible
                format IDs are:

                -  ``tflite`` Used for Android mobile devices.

                -  ``edgetpu-tflite`` Used for `Edge
                   TPU <https://cloud.google.com/edge-tpu/>`__ devices.

                -  ``tf-saved-model`` A tensorflow model in SavedModel
                   format.

                -  ``tf-js`` A
                   `TensorFlow.js <https://www.tensorflow.org/js>`__ model
                   that can be used in the browser and in Node.js using
                   JavaScript.

                -  ``core-ml`` Used for iOS mobile devices.

                -  ``custom-trained`` A Model that was uploaded or trained
                   by custom code.
            exportable_contents (Sequence[~.model.Model.ExportFormat.ExportableContent]):
                Output only. The content of this Model that
                may be exported.
        """

        class ExportableContent(proto.Enum):
            r"""The Model content that can be exported."""
            EXPORTABLE_CONTENT_UNSPECIFIED = 0
            ARTIFACT = 1
            IMAGE = 2

        id = proto.Field(proto.STRING, number=1)
        exportable_contents = proto.RepeatedField(
            proto.ENUM, number=2, enum="Model.ExportFormat.ExportableContent",
        )

    name = proto.Field(proto.STRING, number=1)
    display_name = proto.Field(proto.STRING, number=2)
    description = proto.Field(proto.STRING, number=3)
    predict_schemata = proto.Field(proto.MESSAGE, number=4, message="PredictSchemata",)
    metadata_schema_uri = proto.Field(proto.STRING, number=5)
    metadata = proto.Field(proto.MESSAGE, number=6, message=struct.Value,)
    supported_export_formats = proto.RepeatedField(
        proto.MESSAGE, number=20, message=ExportFormat,
    )
    training_pipeline = proto.Field(proto.STRING, number=7)
    container_spec = proto.Field(proto.MESSAGE, number=9, message="ModelContainerSpec",)
    artifact_uri = proto.Field(proto.STRING, number=26)
    supported_deployment_resources_types = proto.RepeatedField(
        proto.ENUM, number=10, enum=DeploymentResourcesType,
    )
    supported_input_storage_formats = proto.RepeatedField(proto.STRING, number=11)
    supported_output_storage_formats = proto.RepeatedField(proto.STRING, number=12)
    create_time = proto.Field(proto.MESSAGE, number=13, message=timestamp.Timestamp,)
    update_time = proto.Field(proto.MESSAGE, number=14, message=timestamp.Timestamp,)
    deployed_models = proto.RepeatedField(
        proto.MESSAGE, number=15, message=deployed_model_ref.DeployedModelRef,
    )
    explanation_spec = proto.Field(
        proto.MESSAGE, number=23, message=explanation.ExplanationSpec,
    )
    etag = proto.Field(proto.STRING, number=16)
    labels = proto.MapField(proto.STRING, proto.STRING, number=17)


class PredictSchemata(proto.Message):
    r"""Contains the schemata used in Model's predictions and explanations
    via
    [PredictionService.Predict][google.cloud.aiplatform.v1beta1.PredictionService.Predict],
    [PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain]
    and
    [BatchPredictionJob][google.cloud.aiplatform.v1beta1.BatchPredictionJob].

    Attributes:
        instance_schema_uri (str):
            Immutable. Points to a YAML file stored on Google Cloud
            Storage describing the format of a single instance, which
            are used in
            [PredictRequest.instances][google.cloud.aiplatform.v1beta1.PredictRequest.instances],
            [ExplainRequest.instances][google.cloud.aiplatform.v1beta1.ExplainRequest.instances]
            and
            [BatchPredictionJob.input_config][google.cloud.aiplatform.v1beta1.BatchPredictionJob.input_config].
            The schema is defined as an OpenAPI 3.0.2 `Schema
            Object <https://tinyurl.com/y538mdwt#schema-object>`__.
            AutoML Models always have this field populated by AI
            Platform. Note: The URI given on output will be immutable
            and probably different, including the URI scheme, than the
            one given on input. The output URI will point to a location
            where the user only has a read access.
        parameters_schema_uri (str):
            Immutable. Points to a YAML file stored on Google Cloud
            Storage describing the parameters of prediction and
            explanation via
            [PredictRequest.parameters][google.cloud.aiplatform.v1beta1.PredictRequest.parameters],
            [ExplainRequest.parameters][google.cloud.aiplatform.v1beta1.ExplainRequest.parameters]
            and
            [BatchPredictionJob.model_parameters][google.cloud.aiplatform.v1beta1.BatchPredictionJob.model_parameters].
            The schema is defined as an OpenAPI 3.0.2 `Schema
            Object <https://tinyurl.com/y538mdwt#schema-object>`__.
            AutoML Models always have this field populated by AI
            Platform, if no parameters are supported it is set to an
            empty string. Note: The URI given on output will be
            immutable and probably different, including the URI scheme,
            than the one given on input. The output URI will point to a
            location where the user only has a read access.
        prediction_schema_uri (str):
            Immutable. Points to a YAML file stored on Google Cloud
            Storage describing the format of a single prediction
            produced by this Model, which are returned via
            [PredictResponse.predictions][google.cloud.aiplatform.v1beta1.PredictResponse.predictions],
            [ExplainResponse.explanations][google.cloud.aiplatform.v1beta1.ExplainResponse.explanations],
            and
            [BatchPredictionJob.output_config][google.cloud.aiplatform.v1beta1.BatchPredictionJob.output_config].
            The schema is defined as an OpenAPI 3.0.2 `Schema
            Object <https://tinyurl.com/y538mdwt#schema-object>`__.
            AutoML Models always have this field populated by AI
            Platform. Note: The URI given on output will be immutable
            and probably different, including the URI scheme, than the
            one given on input. The output URI will point to a location
            where the user only has a read access.
    """

    instance_schema_uri = proto.Field(proto.STRING, number=1)
    parameters_schema_uri = proto.Field(proto.STRING, number=2)
    prediction_schema_uri = proto.Field(proto.STRING, number=3)


class ModelContainerSpec(proto.Message):
    r"""Specification of the container to be deployed for this Model. The
    ModelContainerSpec is based on the Kubernetes Container
    `specification <https://tinyurl.com/k8s-io-api/v1.10/#container-v1-core>`__.

    Attributes:
        image_uri (str):
            Required. Immutable. The URI of the Model serving container
            file in the Container Registry. The container image is
            ingested upon
            [ModelService.UploadModel][google.cloud.aiplatform.v1beta1.ModelService.UploadModel],
            stored internally, and this original path is afterwards not
            used.
        command (Sequence[str]):
            Immutable. The command with which the container is run. Not
            executed within a shell. The Docker image's ENTRYPOINT is
            used if this is not provided. Variable references
            $(VAR_NAME) are expanded using the container's environment.
            If a variable cannot be resolved, the reference in the input
            string will be unchanged. The $(VAR_NAME) syntax can be
            escaped with a double $$, ie: $$(VAR_NAME). Escaped
            references will never be expanded, regardless of whether the
            variable exists or not. More info:
            https://tinyurl.com/y42hmlxe
        args (Sequence[str]):
            Immutable. The arguments to the command. The Docker image's
            CMD is used if this is not provided. Variable references
            $(VAR_NAME) are expanded using the container's environment.
            If a variable cannot be resolved, the reference in the input
            string will be unchanged. The $(VAR_NAME) syntax can be
            escaped with a double $$, ie: $$(VAR_NAME). Escaped
            references will never be expanded, regardless of whether the
            variable exists or not. More info:
            https://tinyurl.com/y42hmlxe
        env (Sequence[~.env_var.EnvVar]):
            Immutable. The environment variables that are
            to be present in the container.
        ports (Sequence[~.model.Port]):
            Immutable. Declaration of ports that are
            exposed by the container. This field is
            primarily informational, it gives AI Platform
            information about the network connections the
            container uses. Listing or not a port here has
            no impact on whether the port is actually
            exposed, any port listening on the default
            "0.0.0.0" address inside a container will be
            accessible from the network.
        predict_route (str):
            Immutable. An HTTP path to send prediction
            requests to the container, and which must be
            supported by it. If not specified a default HTTP
            path will be used by AI Platform.
        health_route (str):
            Immutable. An HTTP path to send health check
            requests to the container, and which must be
            supported by it. If not specified a standard
            HTTP path will be used by AI Platform.
    """

    image_uri = proto.Field(proto.STRING, number=1)
    command = proto.RepeatedField(proto.STRING, number=2)
    args = proto.RepeatedField(proto.STRING, number=3)
    env = proto.RepeatedField(proto.MESSAGE, number=4, message=env_var.EnvVar,)
    ports = proto.RepeatedField(proto.MESSAGE, number=5, message="Port",)
    predict_route = proto.Field(proto.STRING, number=6)
    health_route = proto.Field(proto.STRING, number=7)


class Port(proto.Message):
    r"""Represents a network port in a container.

    Attributes:
        container_port (int):
            The number of the port to expose on the pod's
            IP address. Must be a valid port number, between
            1 and 65535 inclusive.
    """

    container_port = proto.Field(proto.INT32, number=3)


__all__ = tuple(sorted(__protobuf__.manifest))
