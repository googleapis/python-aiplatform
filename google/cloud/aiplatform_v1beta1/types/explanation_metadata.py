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

from google.protobuf import struct_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1", manifest={"ExplanationMetadata",},
)


class ExplanationMetadata(proto.Message):
    r"""Metadata describing the Model's input and output for
    explanation.

    Attributes:
        inputs (Sequence[google.cloud.aiplatform_v1beta1.types.ExplanationMetadata.InputsEntry]):
            Required. Map from feature names to feature input metadata.
            Keys are the name of the features. Values are the
            specification of the feature.

            An empty InputMetadata is valid. It describes a text feature
            which has the name specified as the key in
            [ExplanationMetadata.inputs][google.cloud.aiplatform.v1beta1.ExplanationMetadata.inputs].
            The baseline of the empty feature is chosen by AI Platform.

            For AI Platform provided Tensorflow images, the key can be
            any friendly name of the feature. Once specified,
            [featureAttributions][google.cloud.aiplatform.v1beta1.Attribution.feature_attributions]
            are keyed by this key (if not grouped with another feature).

            For custom images, the key must match with the key in
            [instance][google.cloud.aiplatform.v1beta1.ExplainRequest.instances].
        outputs (Sequence[google.cloud.aiplatform_v1beta1.types.ExplanationMetadata.OutputsEntry]):
            Required. Map from output names to output
            metadata.
            For AI Platform provided Tensorflow images, keys
            can be any user defined string that consists of
            any UTF-8 characters.
            For custom images, keys are the name of the
            output field in the prediction to be explained.

            Currently only one key is allowed.
        feature_attributions_schema_uri (str):
            Points to a YAML file stored on Google Cloud Storage
            describing the format of the [feature
            attributions][google.cloud.aiplatform.v1beta1.Attribution.feature_attributions].
            The schema is defined as an OpenAPI 3.0.2 `Schema
            Object <https://tinyurl.com/y538mdwt#schema-object>`__.
            AutoML tabular Models always have this field populated by AI
            Platform. Note: The URI given on output may be different,
            including the URI scheme, than the one given on input. The
            output URI will point to a location where the user only has
            a read access.
    """

    class InputMetadata(proto.Message):
        r"""Metadata of the input of a feature.

        Fields other than
        [InputMetadata.input_baselines][google.cloud.aiplatform.v1beta1.ExplanationMetadata.InputMetadata.input_baselines]
        are applicable only for Models that are using AI Platform-provided
        images for Tensorflow.

        Attributes:
            input_baselines (Sequence[google.protobuf.struct_pb2.Value]):
                Baseline inputs for this feature.

                If no baseline is specified, AI Platform chooses the
                baseline for this feature. If multiple baselines are
                specified, AI Platform returns the average attributions
                across them in [Attributions.baseline_attribution][].

                For AI Platform provided Tensorflow images (both 1.x and
                2.x), the shape of each baseline must match the shape of the
                input tensor. If a scalar is provided, we broadcast to the
                same shape as the input tensor.

                For custom images, the element of the baselines must be in
                the same format as the feature's input in the
                [instance][google.cloud.aiplatform.v1beta1.ExplainRequest.instances][].
                The schema of any single instance may be specified via
                Endpoint's DeployedModels'
                [Model's][google.cloud.aiplatform.v1beta1.DeployedModel.model]
                [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
                [instance_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri].
            input_tensor_name (str):
                Name of the input tensor for this feature.
                Required and is only applicable to AI Platform
                provided images for Tensorflow.
            encoding (google.cloud.aiplatform_v1beta1.types.ExplanationMetadata.InputMetadata.Encoding):
                Defines how the feature is encoded into the
                input tensor. Defaults to IDENTITY.
            modality (str):
                Modality of the feature. Valid values are:
                numeric, image. Defaults to numeric.
            feature_value_domain (google.cloud.aiplatform_v1beta1.types.ExplanationMetadata.InputMetadata.FeatureValueDomain):
                The domain details of the input feature
                value. Like min/max, original mean or standard
                deviation if normalized.
            indices_tensor_name (str):
                Specifies the index of the values of the input tensor.
                Required when the input tensor is a sparse representation.
                Refer to Tensorflow documentation for more details:
                https://www.tensorflow.org/api_docs/python/tf/sparse/SparseTensor.
            dense_shape_tensor_name (str):
                Specifies the shape of the values of the input if the input
                is a sparse representation. Refer to Tensorflow
                documentation for more details:
                https://www.tensorflow.org/api_docs/python/tf/sparse/SparseTensor.
            index_feature_mapping (Sequence[str]):
                A list of feature names for each index in the input tensor.
                Required when the input
                [InputMetadata.encoding][google.cloud.aiplatform.v1beta1.ExplanationMetadata.InputMetadata.encoding]
                is BAG_OF_FEATURES, BAG_OF_FEATURES_SPARSE, INDICATOR.
            encoded_tensor_name (str):
                Encoded tensor is a transformation of the input tensor. Must
                be provided if choosing [Integrated Gradients
                attribution][ExplanationParameters.integrated_gradients_attribution]
                or [XRAI
                attribution][google.cloud.aiplatform.v1beta1.ExplanationParameters.xrai_attribution]
                and the input tensor is not differentiable.

                An encoded tensor is generated if the input tensor is
                encoded by a lookup table.
            encoded_baselines (Sequence[google.protobuf.struct_pb2.Value]):
                A list of baselines for the encoded tensor.
                The shape of each baseline should match the
                shape of the encoded tensor. If a scalar is
                provided, AI Platform broadcast to the same
                shape as the encoded tensor.
            visualization (google.cloud.aiplatform_v1beta1.types.ExplanationMetadata.InputMetadata.Visualization):
                Visualization configurations for image
                explanation.
            group_name (str):
                Name of the group that the input belongs to. Features with
                the same group name will be treated as one feature when
                computing attributions. Features grouped together can have
                different shapes in value. If provided, there will be one
                single attribution generated in [
                featureAttributions][Attribution.feature_attributions],
                keyed by the group name.
        """

        class Encoding(proto.Enum):
            r"""Defines how the feature is encoded to [encoded_tensor][]. Defaults
            to IDENTITY.
            """
            ENCODING_UNSPECIFIED = 0
            IDENTITY = 1
            BAG_OF_FEATURES = 2
            BAG_OF_FEATURES_SPARSE = 3
            INDICATOR = 4
            COMBINED_EMBEDDING = 5
            CONCAT_EMBEDDING = 6

        class FeatureValueDomain(proto.Message):
            r"""Domain details of the input feature value. Provides numeric
            information about the feature, such as its range (min, max). If the
            feature has been pre-processed, for example with z-scoring, then it
            provides information about how to recover the original feature. For
            example, if the input feature is an image and it has been
            pre-processed to obtain 0-mean and stddev = 1 values, then
            original_mean, and original_stddev refer to the mean and stddev of
            the original feature (e.g. image tensor) from which input feature
            (with mean = 0 and stddev = 1) was obtained.

            Attributes:
                min_value (float):
                    The minimum permissible value for this
                    feature.
                max_value (float):
                    The maximum permissible value for this
                    feature.
                original_mean (float):
                    If this input feature has been normalized to a mean value of
                    0, the original_mean specifies the mean value of the domain
                    prior to normalization.
                original_stddev (float):
                    If this input feature has been normalized to a standard
                    deviation of 1.0, the original_stddev specifies the standard
                    deviation of the domain prior to normalization.
            """

            min_value = proto.Field(proto.FLOAT, number=1,)
            max_value = proto.Field(proto.FLOAT, number=2,)
            original_mean = proto.Field(proto.FLOAT, number=3,)
            original_stddev = proto.Field(proto.FLOAT, number=4,)

        class Visualization(proto.Message):
            r"""Visualization configurations for image explanation.
            Attributes:
                type_ (google.cloud.aiplatform_v1beta1.types.ExplanationMetadata.InputMetadata.Visualization.Type):
                    Type of the image visualization. Only applicable to
                    [Integrated Gradients attribution]
                    [ExplanationParameters.integrated_gradients_attribution].
                    OUTLINES shows regions of attribution, while PIXELS shows
                    per-pixel attribution. Defaults to OUTLINES.
                polarity (google.cloud.aiplatform_v1beta1.types.ExplanationMetadata.InputMetadata.Visualization.Polarity):
                    Whether to only highlight pixels with
                    positive contributions, negative or both.
                    Defaults to POSITIVE.
                color_map (google.cloud.aiplatform_v1beta1.types.ExplanationMetadata.InputMetadata.Visualization.ColorMap):
                    The color scheme used for the highlighted areas.

                    Defaults to PINK_GREEN for [Integrated Gradients
                    attribution][ExplanationParameters.integrated_gradients_attribution],
                    which shows positive attributions in green and negative in
                    pink.

                    Defaults to VIRIDIS for [XRAI
                    attribution][google.cloud.aiplatform.v1beta1.ExplanationParameters.xrai_attribution],
                    which highlights the most influential regions in yellow and
                    the least influential in blue.
                clip_percent_upperbound (float):
                    Excludes attributions above the specified percentile from
                    the highlighted areas. Using the clip_percent_upperbound and
                    clip_percent_lowerbound together can be useful for filtering
                    out noise and making it easier to see areas of strong
                    attribution. Defaults to 99.9.
                clip_percent_lowerbound (float):
                    Excludes attributions below the specified
                    percentile, from the highlighted areas. Defaults
                    to 62.
                overlay_type (google.cloud.aiplatform_v1beta1.types.ExplanationMetadata.InputMetadata.Visualization.OverlayType):
                    How the original image is displayed in the
                    visualization. Adjusting the overlay can help
                    increase visual clarity if the original image
                    makes it difficult to view the visualization.
                    Defaults to NONE.
            """

            class Type(proto.Enum):
                r"""Type of the image visualization. Only applicable to [Integrated
                Gradients attribution]
                [ExplanationParameters.integrated_gradients_attribution].
                """
                TYPE_UNSPECIFIED = 0
                PIXELS = 1
                OUTLINES = 2

            class Polarity(proto.Enum):
                r"""Whether to only highlight pixels with positive contributions,
                negative or both. Defaults to POSITIVE.
                """
                POLARITY_UNSPECIFIED = 0
                POSITIVE = 1
                NEGATIVE = 2
                BOTH = 3

            class ColorMap(proto.Enum):
                r"""The color scheme used for highlighting areas."""
                COLOR_MAP_UNSPECIFIED = 0
                PINK_GREEN = 1
                VIRIDIS = 2
                RED = 3
                GREEN = 4
                RED_GREEN = 6
                PINK_WHITE_GREEN = 5

            class OverlayType(proto.Enum):
                r"""How the original image is displayed in the visualization."""
                OVERLAY_TYPE_UNSPECIFIED = 0
                NONE = 1
                ORIGINAL = 2
                GRAYSCALE = 3
                MASK_BLACK = 4

            type_ = proto.Field(
                proto.ENUM,
                number=1,
                enum="ExplanationMetadata.InputMetadata.Visualization.Type",
            )
            polarity = proto.Field(
                proto.ENUM,
                number=2,
                enum="ExplanationMetadata.InputMetadata.Visualization.Polarity",
            )
            color_map = proto.Field(
                proto.ENUM,
                number=3,
                enum="ExplanationMetadata.InputMetadata.Visualization.ColorMap",
            )
            clip_percent_upperbound = proto.Field(proto.FLOAT, number=4,)
            clip_percent_lowerbound = proto.Field(proto.FLOAT, number=5,)
            overlay_type = proto.Field(
                proto.ENUM,
                number=6,
                enum="ExplanationMetadata.InputMetadata.Visualization.OverlayType",
            )

        input_baselines = proto.RepeatedField(
            proto.MESSAGE, number=1, message=struct_pb2.Value,
        )
        input_tensor_name = proto.Field(proto.STRING, number=2,)
        encoding = proto.Field(
            proto.ENUM, number=3, enum="ExplanationMetadata.InputMetadata.Encoding",
        )
        modality = proto.Field(proto.STRING, number=4,)
        feature_value_domain = proto.Field(
            proto.MESSAGE,
            number=5,
            message="ExplanationMetadata.InputMetadata.FeatureValueDomain",
        )
        indices_tensor_name = proto.Field(proto.STRING, number=6,)
        dense_shape_tensor_name = proto.Field(proto.STRING, number=7,)
        index_feature_mapping = proto.RepeatedField(proto.STRING, number=8,)
        encoded_tensor_name = proto.Field(proto.STRING, number=9,)
        encoded_baselines = proto.RepeatedField(
            proto.MESSAGE, number=10, message=struct_pb2.Value,
        )
        visualization = proto.Field(
            proto.MESSAGE,
            number=11,
            message="ExplanationMetadata.InputMetadata.Visualization",
        )
        group_name = proto.Field(proto.STRING, number=12,)

    class OutputMetadata(proto.Message):
        r"""Metadata of the prediction output to be explained.
        Attributes:
            index_display_name_mapping (google.protobuf.struct_pb2.Value):
                Static mapping between the index and display name.

                Use this if the outputs are a deterministic n-dimensional
                array, e.g. a list of scores of all the classes in a
                pre-defined order for a multi-classification Model. It's not
                feasible if the outputs are non-deterministic, e.g. the
                Model produces top-k classes or sort the outputs by their
                values.

                The shape of the value must be an n-dimensional array of
                strings. The number of dimensions must match that of the
                outputs to be explained. The
                [Attribution.output_display_name][google.cloud.aiplatform.v1beta1.Attribution.output_display_name]
                is populated by locating in the mapping with
                [Attribution.output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index].
            display_name_mapping_key (str):
                Specify a field name in the prediction to look for the
                display name.

                Use this if the prediction contains the display names for
                the outputs.

                The display names in the prediction must have the same shape
                of the outputs, so that it can be located by
                [Attribution.output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index]
                for a specific output.
            output_tensor_name (str):
                Name of the output tensor. Required and is
                only applicable to AI Platform provided images
                for Tensorflow.
        """

        index_display_name_mapping = proto.Field(
            proto.MESSAGE,
            number=1,
            oneof="display_name_mapping",
            message=struct_pb2.Value,
        )
        display_name_mapping_key = proto.Field(
            proto.STRING, number=2, oneof="display_name_mapping",
        )
        output_tensor_name = proto.Field(proto.STRING, number=3,)

    inputs = proto.MapField(
        proto.STRING, proto.MESSAGE, number=1, message=InputMetadata,
    )
    outputs = proto.MapField(
        proto.STRING, proto.MESSAGE, number=2, message=OutputMetadata,
    )
    feature_attributions_schema_uri = proto.Field(proto.STRING, number=3,)


__all__ = tuple(sorted(__protobuf__.manifest))
