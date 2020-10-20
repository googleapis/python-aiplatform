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


from google.protobuf import struct_pb2 as struct  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1", manifest={"ExplanationMetadata",},
)


class ExplanationMetadata(proto.Message):
    r"""Metadata describing the Model's input and output for
    explanation.

    Attributes:
        inputs (Sequence[~.explanation_metadata.ExplanationMetadata.InputsEntry]):
            Required. Map from feature names to feature input metadata.
            Keys are the name of the features. Values are the
            specification of the feature.

            An empty InputMetadata is valid. It describes a text feature
            which has the name specified as the key in
            ``ExplanationMetadata.inputs``.
            The baseline of the empty feature is chosen by AI Platform.
        outputs (Sequence[~.explanation_metadata.ExplanationMetadata.OutputsEntry]):
            Required. Map from output names to output
            metadata.
            Keys are the name of the output field in the
            prediction to be explained. Currently only one
            key is allowed.
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

        Attributes:
            input_baselines (Sequence[~.struct.Value]):
                Baseline inputs for this feature.

                If no baseline is specified, AI Platform chooses the
                baseline for this feature. If multiple baselines are
                specified, AI Platform returns the average attributions
                across them in [Attributions.baseline_attribution][].

                The element of the baselines must be in the same format as
                the feature's input in the
                ``instance``[].
                The schema of any single instance may be specified via
                Endpoint's DeployedModels'
                [Model's][google.cloud.aiplatform.v1beta1.DeployedModel.model]
                [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
                ``instance_schema_uri``.
        """

        input_baselines = proto.RepeatedField(
            proto.MESSAGE, number=1, message=struct.Value,
        )

    class OutputMetadata(proto.Message):
        r"""Metadata of the prediction output to be explained.

        Attributes:
            index_display_name_mapping (~.struct.Value):
                Static mapping between the index and display name.

                Use this if the outputs are a deterministic n-dimensional
                array, e.g. a list of scores of all the classes in a
                pre-defined order for a multi-classification Model. It's not
                feasible if the outputs are non-deterministic, e.g. the
                Model produces top-k classes or sort the outputs by their
                values.

                The shape of the value must be an n-dimensional array of
                strings. The number of dimentions must match that of the
                outputs to be explained. The
                ``Attribution.output_display_name``
                is populated by locating in the mapping with
                ``Attribution.output_index``.
            display_name_mapping_key (str):
                Specify a field name in the prediction to look for the
                display name.

                Use this if the prediction contains the display names for
                the outputs.

                The display names in the prediction must have the same shape
                of the outputs, so that it can be located by
                ``Attribution.output_index``
                for a specific output.
        """

        index_display_name_mapping = proto.Field(
            proto.MESSAGE, number=1, message=struct.Value,
        )
        display_name_mapping_key = proto.Field(proto.STRING, number=2)

    inputs = proto.MapField(
        proto.STRING, proto.MESSAGE, number=1, message=InputMetadata,
    )
    outputs = proto.MapField(
        proto.STRING, proto.MESSAGE, number=2, message=OutputMetadata,
    )
    feature_attributions_schema_uri = proto.Field(proto.STRING, number=3)


__all__ = tuple(sorted(__protobuf__.manifest))
