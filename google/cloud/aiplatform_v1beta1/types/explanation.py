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
from google.protobuf import struct_pb2 as struct  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "Explanation",
        "ModelExplanation",
        "Attribution",
        "ExplanationSpec",
        "ExplanationParameters",
        "SampledShapleyAttribution",
    },
)


class Explanation(proto.Message):
    r"""Explanation of a [prediction][ExplainResponse.predictions] produced
    by the Model on a given
    [instance][google.cloud.aiplatform.v1beta1.ExplainRequest.instances].

    Currently, only AutoML tabular Models support explanation.

    Attributes:
        attributions (Sequence[~.explanation.Attribution]):
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
    """

    attributions = proto.RepeatedField(proto.MESSAGE, number=1, message="Attribution",)


class ModelExplanation(proto.Message):
    r"""Aggregated explanation metrics for a Model over a set of
    instances.
    Currently, only AutoML tabular Models support aggregated
    explanation.

    Attributes:
        mean_attributions (Sequence[~.explanation.Attribution]):
            Output only. Aggregated attributions explaning the Model's
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

            If the Model predicted output is a tensor value (for
            example, an ndarray), this is the value in the output
            located by
            [output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index].

            If there are multiple baselines, their output values are
            averaged.
        instance_output_value (float):
            Output only. Model predicted output on the corresponding
            [explanation instance][ExplainRequest.instances]. The field
            name of the output is determined by the key in
            [ExplanationMetadata.outputs][google.cloud.aiplatform.v1beta1.ExplanationMetadata.outputs].

            If the Model predicted output is a tensor value (for
            example, an ndarray), this is the value in the output
            located by
            [output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index].
        feature_attributions (~.struct.Value):
            Output only. Attributions of each explained feature.
            Features are extracted from the [prediction
            instances][google.cloud.aiplatform.v1beta1.ExplainRequest.instances]
            according to [explanation input
            metadata][google.cloud.aiplatform.v1beta1.ExplanationMetadata.inputs].

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
            not populated. If the prediction output is a tensor value
            (for example, an ndarray), the length of output_index is the
            same as the number of dimensions of the output. The i-th
            element in output_index is the element index of the i-th
            dimension of the output vector. Indexes start from 0.
        output_display_name (str):
            Output only. The display name of the output identified by
            [output_index][google.cloud.aiplatform.v1beta1.Attribution.output_index],
            e.g. the predicted class name by a multi-classification
            Model.

            This field is only populated iff the Model predicts display
            names as a separate field along with the explained output.
            The predicted display name must has the same shape of the
            explained output, and can be located using output_index.
        approximation_error (float):
            Output only. Error of
            [feature_attributions][google.cloud.aiplatform.v1beta1.Attribution.feature_attributions]
            caused by approximation used in the explanation method.
            Lower value means more precise attributions.

            For Sampled Shapley
            [attribution][google.cloud.aiplatform.v1beta1.ExplanationParameters.sampled_shapley_attribution],
            increasing
            [path_count][google.cloud.aiplatform.v1beta1.SampledShapleyAttribution.path_count]
            might reduce the error.
    """

    baseline_output_value = proto.Field(proto.DOUBLE, number=1)

    instance_output_value = proto.Field(proto.DOUBLE, number=2)

    feature_attributions = proto.Field(proto.MESSAGE, number=3, message=struct.Value,)

    output_index = proto.RepeatedField(proto.INT32, number=4)

    output_display_name = proto.Field(proto.STRING, number=5)

    approximation_error = proto.Field(proto.DOUBLE, number=6)


class ExplanationSpec(proto.Message):
    r"""Specification of Model explanation.
    Currently, only AutoML tabular Models support explanation.

    Attributes:
        parameters (~.explanation.ExplanationParameters):
            Required. Parameters that configure
            explaining of the Model's predictions.
        metadata (~.explanation_metadata.ExplanationMetadata):
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
        sampled_shapley_attribution (~.explanation.SampledShapleyAttribution):
            An attribution method that approximates
            Shapley values for features that contribute to
            the label being predicted. A sampling strategy
            is used to approximate the value rather than
            considering all subsets of features.
    """

    sampled_shapley_attribution = proto.Field(
        proto.MESSAGE, number=1, message="SampledShapleyAttribution",
    )


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

    path_count = proto.Field(proto.INT32, number=1)


__all__ = tuple(sorted(__protobuf__.manifest))
