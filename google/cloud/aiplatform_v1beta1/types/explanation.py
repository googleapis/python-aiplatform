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

from google.cloud.aiplatform_v1beta1.types import explanation_metadata
from google.protobuf import struct_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "Explanation",
        "ModelExplanation",
        "Attribution",
        "ExplanationSpec",
        "ExplanationParameters",
        "SampledShapleyAttribution",
        "IntegratedGradientsAttribution",
        "XraiAttribution",
        "SmoothGradConfig",
        "FeatureNoiseSigma",
        "ExplanationSpecOverride",
        "ExplanationMetadataOverride",
    },
)


class Explanation(proto.Message):
    r"""Explanation of a prediction (provided in
    [PredictResponse.predictions][google.cloud.aiplatform.v1beta1.PredictResponse.predictions])
    produced by the Model on a given
    [instance][google.cloud.aiplatform.v1beta1.ExplainRequest.instances].

    Attributes:
        attributions (Sequence[google.cloud.aiplatform_v1beta1.types.Attribution]):
            Output only. Feature attributions grouped by predicted
            outputs.

            For Models that predict only one output, such as regression
            Models that predict only one score, there is only one
            attibution that explains the predicted output. For Models
            that predict multiple outputs, such as multiclass Models
            that predict multiple classes, each element explains one
            specific item.
            [Attribution.output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index]
            can be used to identify which output this attribution is
            explaining.

            If users set
            [ExplanationParameters.top_k][google.cloud.aiplatform.v1beta1.ExplanationParameters.top_k],
            the attributions are sorted by
            [instance_output_value][Attributions.instance_output_value]
            in descending order. If
            [ExplanationParameters.output_indices][google.cloud.aiplatform.v1beta1.ExplanationParameters.output_indices]
            is specified, the attributions are stored by
            [Attribution.output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index]
            in the same order as they appear in the output_indices.
    """

    attributions = proto.RepeatedField(proto.MESSAGE, number=1, message="Attribution",)


class ModelExplanation(proto.Message):
    r"""Aggregated explanation metrics for a Model over a set of
    instances.

    Attributes:
        mean_attributions (Sequence[google.cloud.aiplatform_v1beta1.types.Attribution]):
            Output only. Aggregated attributions explaining the Model's
            prediction outputs over the set of instances. The
            attributions are grouped by outputs.

            For Models that predict only one output, such as regression
            Models that predict only one score, there is only one
            attibution that explains the predicted output. For Models
            that predict multiple outputs, such as multiclass Models
            that predict multiple classes, each element explains one
            specific item.
            [Attribution.output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index]
            can be used to identify which output this attribution is
            explaining.

            The
            [baselineOutputValue][google.cloud.aiplatform.v1beta1.Attribution.baseline_output_value],
            [instanceOutputValue][google.cloud.aiplatform.v1beta1.Attribution.instance_output_value]
            and
            [featureAttributions][google.cloud.aiplatform.v1beta1.Attribution.feature_attributions]
            fields are averaged over the test data.

            NOTE: Currently AutoML tabular classification Models produce
            only one attribution, which averages attributions over all
            the classes it predicts.
            [Attribution.approximation_error][google.cloud.aiplatform.v1beta1.Attribution.approximation_error]
            is not populated.
    """

    mean_attributions = proto.RepeatedField(
        proto.MESSAGE, number=1, message="Attribution",
    )


class Attribution(proto.Message):
    r"""Attribution that explains a particular prediction output.
    Attributes:
        baseline_output_value (float):
            Output only. Model predicted output if the input instance is
            constructed from the baselines of all the features defined
            in
            [ExplanationMetadata.inputs][google.cloud.aiplatform.v1beta1.ExplanationMetadata.inputs].
            The field name of the output is determined by the key in
            [ExplanationMetadata.outputs][google.cloud.aiplatform.v1beta1.ExplanationMetadata.outputs].

            If the Model's predicted output has multiple dimensions
            (rank > 1), this is the value in the output located by
            [output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index].

            If there are multiple baselines, their output values are
            averaged.
        instance_output_value (float):
            Output only. Model predicted output on the corresponding
            [explanation instance][ExplainRequest.instances]. The field
            name of the output is determined by the key in
            [ExplanationMetadata.outputs][google.cloud.aiplatform.v1beta1.ExplanationMetadata.outputs].

            If the Model predicted output has multiple dimensions, this
            is the value in the output located by
            [output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index].
        feature_attributions (google.protobuf.struct_pb2.Value):
            Output only. Attributions of each explained feature.
            Features are extracted from the [prediction
            instances][google.cloud.aiplatform.v1beta1.ExplainRequest.instances]
            according to [explanation metadata for
            inputs][google.cloud.aiplatform.v1beta1.ExplanationMetadata.inputs].

            The value is a struct, whose keys are the name of the
            feature. The values are how much the feature in the
            [instance][google.cloud.aiplatform.v1beta1.ExplainRequest.instances]
            contributed to the predicted result.

            The format of the value is determined by the feature's input
            format:

            -  If the feature is a scalar value, the attribution value
               is a [floating
               number][google.protobuf.Value.number_value].

            -  If the feature is an array of scalar values, the
               attribution value is an
               [array][google.protobuf.Value.list_value].

            -  If the feature is a struct, the attribution value is a
               [struct][google.protobuf.Value.struct_value]. The keys in
               the attribution value struct are the same as the keys in
               the feature struct. The formats of the values in the
               attribution struct are determined by the formats of the
               values in the feature struct.

            The
            [ExplanationMetadata.feature_attributions_schema_uri][google.cloud.aiplatform.v1beta1.ExplanationMetadata.feature_attributions_schema_uri]
            field, pointed to by the
            [ExplanationSpec][google.cloud.aiplatform.v1beta1.ExplanationSpec]
            field of the
            [Endpoint.deployed_models][google.cloud.aiplatform.v1beta1.Endpoint.deployed_models]
            object, points to the schema file that describes the
            features and their attribution values (if it is populated).
        output_index (Sequence[int]):
            Output only. The index that locates the explained prediction
            output.

            If the prediction output is a scalar value, output_index is
            not populated. If the prediction output has multiple
            dimensions, the length of the output_index list is the same
            as the number of dimensions of the output. The i-th element
            in output_index is the element index of the i-th dimension
            of the output vector. Indices start from 0.
        output_display_name (str):
            Output only. The display name of the output identified by
            [output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index].
            For example, the predicted class name by a
            multi-classification Model.

            This field is only populated iff the Model predicts display
            names as a separate field along with the explained output.
            The predicted display name must has the same shape of the
            explained output, and can be located using output_index.
        approximation_error (float):
            Output only. Error of
            [feature_attributions][google.cloud.aiplatform.v1beta1.Attribution.feature_attributions]
            caused by approximation used in the explanation method.
            Lower value means more precise attributions.

            -  For Sampled Shapley
               [attribution][google.cloud.aiplatform.v1beta1.ExplanationParameters.sampled_shapley_attribution],
               increasing
               [path_count][google.cloud.aiplatform.v1beta1.SampledShapleyAttribution.path_count]
               might reduce the error.
            -  For Integrated Gradients
               [attribution][google.cloud.aiplatform.v1beta1.ExplanationParameters.integrated_gradients_attribution],
               increasing
               [step_count][google.cloud.aiplatform.v1beta1.IntegratedGradientsAttribution.step_count]
               might reduce the error.
            -  For [XRAI
               attribution][google.cloud.aiplatform.v1beta1.ExplanationParameters.xrai_attribution],
               increasing
               [step_count][google.cloud.aiplatform.v1beta1.XraiAttribution.step_count]
               might reduce the error.

            See `this
            introduction </vertex-ai/docs/explainable-ai/overview>`__
            for more information.
        output_name (str):
            Output only. Name of the explain output. Specified as the
            key in
            [ExplanationMetadata.outputs][google.cloud.aiplatform.v1beta1.ExplanationMetadata.outputs].
    """

    baseline_output_value = proto.Field(proto.DOUBLE, number=1,)
    instance_output_value = proto.Field(proto.DOUBLE, number=2,)
    feature_attributions = proto.Field(
        proto.MESSAGE, number=3, message=struct_pb2.Value,
    )
    output_index = proto.RepeatedField(proto.INT32, number=4,)
    output_display_name = proto.Field(proto.STRING, number=5,)
    approximation_error = proto.Field(proto.DOUBLE, number=6,)
    output_name = proto.Field(proto.STRING, number=7,)


class ExplanationSpec(proto.Message):
    r"""Specification of Model explanation.
    Attributes:
        parameters (google.cloud.aiplatform_v1beta1.types.ExplanationParameters):
            Required. Parameters that configure
            explaining of the Model's predictions.
        metadata (google.cloud.aiplatform_v1beta1.types.ExplanationMetadata):
            Required. Metadata describing the Model's
            input and output for explanation.
    """

    parameters = proto.Field(proto.MESSAGE, number=1, message="ExplanationParameters",)
    metadata = proto.Field(
        proto.MESSAGE, number=2, message=explanation_metadata.ExplanationMetadata,
    )


class ExplanationParameters(proto.Message):
    r"""Parameters to configure explaining for Model's predictions.
    Attributes:
        sampled_shapley_attribution (google.cloud.aiplatform_v1beta1.types.SampledShapleyAttribution):
            An attribution method that approximates
            Shapley values for features that contribute to
            the label being predicted. A sampling strategy
            is used to approximate the value rather than
            considering all subsets of features. Refer to
            this paper for model details:
            https://arxiv.org/abs/1306.4265.
        integrated_gradients_attribution (google.cloud.aiplatform_v1beta1.types.IntegratedGradientsAttribution):
            An attribution method that computes Aumann-
            hapley values taking advantage of the model's
            fully differentiable structure. Refer to this
            paper for more details:
            https://arxiv.org/abs/1703.01365
        xrai_attribution (google.cloud.aiplatform_v1beta1.types.XraiAttribution):
            An attribution method that redistributes
            Integrated Gradients attribution to segmented
            regions, taking advantage of the model's fully
            differentiable structure. Refer to this paper
            for more details:
            https://arxiv.org/abs/1906.02825
            XRAI currently performs better on natural
            images, like a picture of a house or an animal.
            If the images are taken in artificial
            environments, like a lab or manufacturing line,
            or from diagnostic equipment, like x-rays or
            quality-control cameras, use Integrated
            Gradients instead.
        top_k (int):
            If populated, returns attributions for top K
            indices of outputs (defaults to 1). Only applies
            to Models that predicts more than one outputs
            (e,g, multi-class Models). When set to -1,
            returns explanations for all outputs.
        output_indices (google.protobuf.struct_pb2.ListValue):
            If populated, only returns attributions that have
            [output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index]
            contained in output_indices. It must be an ndarray of
            integers, with the same shape of the output it's explaining.

            If not populated, returns attributions for
            [top_k][google.cloud.aiplatform.v1beta1.ExplanationParameters.top_k]
            indices of outputs. If neither top_k nor output_indeices is
            populated, returns the argmax index of the outputs.

            Only applicable to Models that predict multiple outputs
            (e,g, multi-class Models that predict multiple classes).
    """

    sampled_shapley_attribution = proto.Field(
        proto.MESSAGE, number=1, oneof="method", message="SampledShapleyAttribution",
    )
    integrated_gradients_attribution = proto.Field(
        proto.MESSAGE,
        number=2,
        oneof="method",
        message="IntegratedGradientsAttribution",
    )
    xrai_attribution = proto.Field(
        proto.MESSAGE, number=3, oneof="method", message="XraiAttribution",
    )
    top_k = proto.Field(proto.INT32, number=4,)
    output_indices = proto.Field(proto.MESSAGE, number=5, message=struct_pb2.ListValue,)


class SampledShapleyAttribution(proto.Message):
    r"""An attribution method that approximates Shapley values for
    features that contribute to the label being predicted. A
    sampling strategy is used to approximate the value rather than
    considering all subsets of features.

    Attributes:
        path_count (int):
            Required. The number of feature permutations to consider
            when approximating the Shapley values.

            Valid range of its value is [1, 50], inclusively.
    """

    path_count = proto.Field(proto.INT32, number=1,)


class IntegratedGradientsAttribution(proto.Message):
    r"""An attribution method that computes the Aumann-Shapley value
    taking advantage of the model's fully differentiable structure.
    Refer to this paper for more details:
    https://arxiv.org/abs/1703.01365

    Attributes:
        step_count (int):
            Required. The number of steps for approximating the path
            integral. A good value to start is 50 and gradually increase
            until the sum to diff property is within the desired error
            range.

            Valid range of its value is [1, 100], inclusively.
        smooth_grad_config (google.cloud.aiplatform_v1beta1.types.SmoothGradConfig):
            Config for SmoothGrad approximation of
            gradients.
            When enabled, the gradients are approximated by
            averaging the gradients from noisy samples in
            the vicinity of the inputs. Adding noise can
            help improve the computed gradients. Refer to
            this paper for more details:
            https://arxiv.org/pdf/1706.03825.pdf
    """

    step_count = proto.Field(proto.INT32, number=1,)
    smooth_grad_config = proto.Field(
        proto.MESSAGE, number=2, message="SmoothGradConfig",
    )


class XraiAttribution(proto.Message):
    r"""An explanation method that redistributes Integrated Gradients
    attributions to segmented regions, taking advantage of the
    model's fully differentiable structure. Refer to this paper for
    more details: https://arxiv.org/abs/1906.02825

    Supported only by image Models.

    Attributes:
        step_count (int):
            Required. The number of steps for approximating the path
            integral. A good value to start is 50 and gradually increase
            until the sum to diff property is met within the desired
            error range.

            Valid range of its value is [1, 100], inclusively.
        smooth_grad_config (google.cloud.aiplatform_v1beta1.types.SmoothGradConfig):
            Config for SmoothGrad approximation of
            gradients.
            When enabled, the gradients are approximated by
            averaging the gradients from noisy samples in
            the vicinity of the inputs. Adding noise can
            help improve the computed gradients. Refer to
            this paper for more details:
            https://arxiv.org/pdf/1706.03825.pdf
    """

    step_count = proto.Field(proto.INT32, number=1,)
    smooth_grad_config = proto.Field(
        proto.MESSAGE, number=2, message="SmoothGradConfig",
    )


class SmoothGradConfig(proto.Message):
    r"""Config for SmoothGrad approximation of gradients.
    When enabled, the gradients are approximated by averaging the
    gradients from noisy samples in the vicinity of the inputs.
    Adding noise can help improve the computed gradients. Refer to
    this paper for more details:
    https://arxiv.org/pdf/1706.03825.pdf

    Attributes:
        noise_sigma (float):
            This is a single float value and will be used to add noise
            to all the features. Use this field when all features are
            normalized to have the same distribution: scale to range [0,
            1], [-1, 1] or z-scoring, where features are normalized to
            have 0-mean and 1-variance. Learn more about
            `normalization <https://developers.google.com/machine-learning/data-prep/transform/normalization>`__.

            For best results the recommended value is about 10% - 20% of
            the standard deviation of the input feature. Refer to
            section 3.2 of the SmoothGrad paper:
            https://arxiv.org/pdf/1706.03825.pdf. Defaults to 0.1.

            If the distribution is different per feature, set
            [feature_noise_sigma][google.cloud.aiplatform.v1beta1.SmoothGradConfig.feature_noise_sigma]
            instead for each feature.
        feature_noise_sigma (google.cloud.aiplatform_v1beta1.types.FeatureNoiseSigma):
            This is similar to
            [noise_sigma][google.cloud.aiplatform.v1beta1.SmoothGradConfig.noise_sigma],
            but provides additional flexibility. A separate noise sigma
            can be provided for each feature, which is useful if their
            distributions are different. No noise is added to features
            that are not set. If this field is unset,
            [noise_sigma][google.cloud.aiplatform.v1beta1.SmoothGradConfig.noise_sigma]
            will be used for all features.
        noisy_sample_count (int):
            The number of gradient samples to use for approximation. The
            higher this number, the more accurate the gradient is, but
            the runtime complexity increases by this factor as well.
            Valid range of its value is [1, 50]. Defaults to 3.
    """

    noise_sigma = proto.Field(proto.FLOAT, number=1, oneof="GradientNoiseSigma",)
    feature_noise_sigma = proto.Field(
        proto.MESSAGE,
        number=2,
        oneof="GradientNoiseSigma",
        message="FeatureNoiseSigma",
    )
    noisy_sample_count = proto.Field(proto.INT32, number=3,)


class FeatureNoiseSigma(proto.Message):
    r"""Noise sigma by features. Noise sigma represents the standard
    deviation of the gaussian kernel that will be used to add noise
    to interpolated inputs prior to computing gradients.

    Attributes:
        noise_sigma (Sequence[google.cloud.aiplatform_v1beta1.types.FeatureNoiseSigma.NoiseSigmaForFeature]):
            Noise sigma per feature. No noise is added to
            features that are not set.
    """

    class NoiseSigmaForFeature(proto.Message):
        r"""Noise sigma for a single feature.
        Attributes:
            name (str):
                The name of the input feature for which noise sigma is
                provided. The features are defined in [explanation metadata
                inputs][google.cloud.aiplatform.v1beta1.ExplanationMetadata.inputs].
            sigma (float):
                This represents the standard deviation of the Gaussian
                kernel that will be used to add noise to the feature prior
                to computing gradients. Similar to
                [noise_sigma][google.cloud.aiplatform.v1beta1.SmoothGradConfig.noise_sigma]
                but represents the noise added to the current feature.
                Defaults to 0.1.
        """

        name = proto.Field(proto.STRING, number=1,)
        sigma = proto.Field(proto.FLOAT, number=2,)

    noise_sigma = proto.RepeatedField(
        proto.MESSAGE, number=1, message=NoiseSigmaForFeature,
    )


class ExplanationSpecOverride(proto.Message):
    r"""The
    [ExplanationSpec][google.cloud.aiplatform.v1beta1.ExplanationSpec]
    entries that can be overridden at [online
    explanation][PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain]
    time.

    Attributes:
        parameters (google.cloud.aiplatform_v1beta1.types.ExplanationParameters):
            The parameters to be overridden. Note that the
            [method][google.cloud.aiplatform.v1beta1.ExplanationParameters.method]
            cannot be changed. If not specified, no parameter is
            overridden.
        metadata (google.cloud.aiplatform_v1beta1.types.ExplanationMetadataOverride):
            The metadata to be overridden. If not
            specified, no metadata is overridden.
    """

    parameters = proto.Field(proto.MESSAGE, number=1, message="ExplanationParameters",)
    metadata = proto.Field(
        proto.MESSAGE, number=2, message="ExplanationMetadataOverride",
    )


class ExplanationMetadataOverride(proto.Message):
    r"""The
    [ExplanationMetadata][google.cloud.aiplatform.v1beta1.ExplanationMetadata]
    entries that can be overridden at [online
    explanation][google.cloud.aiplatform.v1beta1.PredictionService.Explain]
    time.

    Attributes:
        inputs (Sequence[google.cloud.aiplatform_v1beta1.types.ExplanationMetadataOverride.InputsEntry]):
            Required. Overrides the [input
            metadata][google.cloud.aiplatform.v1beta1.ExplanationMetadata.inputs]
            of the features. The key is the name of the feature to be
            overridden. The keys specified here must exist in the input
            metadata to be overridden. If a feature is not specified
            here, the corresponding feature's input metadata is not
            overridden.
    """

    class InputMetadataOverride(proto.Message):
        r"""The [input
        metadata][google.cloud.aiplatform.v1beta1.ExplanationMetadata.InputMetadata]
        entries to be overridden.

        Attributes:
            input_baselines (Sequence[google.protobuf.struct_pb2.Value]):
                Baseline inputs for this feature.

                This overrides the ``input_baseline`` field of the
                [ExplanationMetadata.InputMetadata][google.cloud.aiplatform.v1beta1.ExplanationMetadata.InputMetadata]
                object of the corresponding feature's input metadata. If
                it's not specified, the original baselines are not
                overridden.
        """

        input_baselines = proto.RepeatedField(
            proto.MESSAGE, number=1, message=struct_pb2.Value,
        )

    inputs = proto.MapField(
        proto.STRING, proto.MESSAGE, number=1, message=InputMetadataOverride,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
