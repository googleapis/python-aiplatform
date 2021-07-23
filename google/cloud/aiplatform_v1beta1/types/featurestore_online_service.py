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
    feature_selector as gca_feature_selector,
)
from google.cloud.aiplatform_v1beta1.types import types
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "ReadFeatureValuesRequest",
        "ReadFeatureValuesResponse",
        "StreamingReadFeatureValuesRequest",
        "FeatureValue",
        "FeatureValueList",
    },
)


class ReadFeatureValuesRequest(proto.Message):
    r"""Request message for
    [FeaturestoreOnlineServingService.ReadFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreOnlineServingService.ReadFeatureValues].

    Attributes:
        entity_type (str):
            Required. The resource name of the EntityType for the entity
            being read. Value format:
            ``projects/{project}/locations/{location}/featurestores/ {featurestore}/entityTypes/{entityType}``.
            For example, for a machine learning model predicting user
            clicks on a website, an EntityType ID could be "user".
        entity_id (str):
            Required. ID for a specific entity. For example, for a
            machine learning model predicting user clicks on a website,
            an entity ID could be "user_123".
        feature_selector (google.cloud.aiplatform_v1beta1.types.FeatureSelector):
            Required. Selector choosing Features of the
            target EntityType.
    """

    entity_type = proto.Field(proto.STRING, number=1,)
    entity_id = proto.Field(proto.STRING, number=2,)
    feature_selector = proto.Field(
        proto.MESSAGE, number=3, message=gca_feature_selector.FeatureSelector,
    )


class ReadFeatureValuesResponse(proto.Message):
    r"""Response message for
    [FeaturestoreOnlineServingService.ReadFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreOnlineServingService.ReadFeatureValues].

    Attributes:
        header (google.cloud.aiplatform_v1beta1.types.ReadFeatureValuesResponse.Header):
            Response header.
        entity_view (google.cloud.aiplatform_v1beta1.types.ReadFeatureValuesResponse.EntityView):
            Entity view with Feature values. This may be
            the entity in the Featurestore if values for all
            Features were requested, or a projection of the
            entity in the Featurestore if values for only
            some Features were requested.
    """

    class FeatureDescriptor(proto.Message):
        r"""Metadata for requested Features.
        Attributes:
            id (str):
                Feature ID.
        """

        id = proto.Field(proto.STRING, number=1,)

    class Header(proto.Message):
        r"""Response header with metadata for the requested
        [ReadFeatureValuesRequest.entity_type][google.cloud.aiplatform.v1beta1.ReadFeatureValuesRequest.entity_type]
        and Features.

        Attributes:
            entity_type (str):
                The resource name of the EntityType from the
                [ReadFeatureValuesRequest][google.cloud.aiplatform.v1beta1.ReadFeatureValuesRequest].
                Value format:
                ``projects/{project}/locations/{location}/featurestores/ {featurestore}/entityTypes/{entityType}``.
            feature_descriptors (Sequence[google.cloud.aiplatform_v1beta1.types.ReadFeatureValuesResponse.FeatureDescriptor]):
                List of Feature metadata corresponding to each piece of
                [ReadFeatureValuesResponse.data][].
        """

        entity_type = proto.Field(proto.STRING, number=1,)
        feature_descriptors = proto.RepeatedField(
            proto.MESSAGE,
            number=2,
            message="ReadFeatureValuesResponse.FeatureDescriptor",
        )

    class EntityView(proto.Message):
        r"""Entity view with Feature values.
        Attributes:
            entity_id (str):
                ID of the requested entity.
            data (Sequence[google.cloud.aiplatform_v1beta1.types.ReadFeatureValuesResponse.EntityView.Data]):
                Each piece of data holds the k requested values for one
                requested Feature. If no values for the requested Feature
                exist, the corresponding cell will be empty. This has the
                same size and is in the same order as the features from the
                header
                [ReadFeatureValuesResponse.header][google.cloud.aiplatform.v1beta1.ReadFeatureValuesResponse.header].
        """

        class Data(proto.Message):
            r"""Container to hold value(s), successive in time, for one
            Feature from the request.

            Attributes:
                value (google.cloud.aiplatform_v1beta1.types.FeatureValue):
                    Feature value if a single value is requested.
                values (google.cloud.aiplatform_v1beta1.types.FeatureValueList):
                    Feature values list if values, successive in
                    time, are requested. If the requested number of
                    values is greater than the number of existing
                    Feature values, nonexistent values are omitted
                    instead of being returned as empty.
            """

            value = proto.Field(
                proto.MESSAGE, number=1, oneof="data", message="FeatureValue",
            )
            values = proto.Field(
                proto.MESSAGE, number=2, oneof="data", message="FeatureValueList",
            )

        entity_id = proto.Field(proto.STRING, number=1,)
        data = proto.RepeatedField(
            proto.MESSAGE,
            number=2,
            message="ReadFeatureValuesResponse.EntityView.Data",
        )

    header = proto.Field(proto.MESSAGE, number=1, message=Header,)
    entity_view = proto.Field(proto.MESSAGE, number=2, message=EntityView,)


class StreamingReadFeatureValuesRequest(proto.Message):
    r"""Request message for
    [FeaturestoreOnlineServingService.StreamingFeatureValuesRead][].

    Attributes:
        entity_type (str):
            Required. The resource name of the entities' type. Value
            format:
            ``projects/{project}/locations/{location}/featurestores/ {featurestore}/entityTypes/{entityType}``.
            For example, for a machine learning model predicting user
            clicks on a website, an EntityType ID could be "user".
        entity_ids (Sequence[str]):
            Required. IDs of entities to read Feature values of. The
            maximum number of IDs is 100. For example, for a machine
            learning model predicting user clicks on a website, an
            entity ID could be "user_123".
        feature_selector (google.cloud.aiplatform_v1beta1.types.FeatureSelector):
            Required. Selector choosing Features of the
            target EntityType. Feature IDs will be
            deduplicated.
    """

    entity_type = proto.Field(proto.STRING, number=1,)
    entity_ids = proto.RepeatedField(proto.STRING, number=2,)
    feature_selector = proto.Field(
        proto.MESSAGE, number=3, message=gca_feature_selector.FeatureSelector,
    )


class FeatureValue(proto.Message):
    r"""Value for a feature.
    NEXT ID: 15

    Attributes:
        bool_value (bool):
            Bool type feature value.
        double_value (float):
            Double type feature value.
        int64_value (int):
            Int64 feature value.
        string_value (str):
            String feature value.
        bool_array_value (google.cloud.aiplatform_v1beta1.types.BoolArray):
            A list of bool type feature value.
        double_array_value (google.cloud.aiplatform_v1beta1.types.DoubleArray):
            A list of double type feature value.
        int64_array_value (google.cloud.aiplatform_v1beta1.types.Int64Array):
            A list of int64 type feature value.
        string_array_value (google.cloud.aiplatform_v1beta1.types.StringArray):
            A list of string type feature value.
        bytes_value (bytes):
            Bytes feature value.
        metadata (google.cloud.aiplatform_v1beta1.types.FeatureValue.Metadata):
            Metadata of feature value.
    """

    class Metadata(proto.Message):
        r"""Metadata of feature value.
        Attributes:
            generate_time (google.protobuf.timestamp_pb2.Timestamp):
                Feature generation timestamp. Typically, it
                is provided by user at feature ingestion time.
                If not, feature store will use the system
                timestamp when the data is ingested into feature
                store.
        """

        generate_time = proto.Field(
            proto.MESSAGE, number=1, message=timestamp_pb2.Timestamp,
        )

    bool_value = proto.Field(proto.BOOL, number=1, oneof="value",)
    double_value = proto.Field(proto.DOUBLE, number=2, oneof="value",)
    int64_value = proto.Field(proto.INT64, number=5, oneof="value",)
    string_value = proto.Field(proto.STRING, number=6, oneof="value",)
    bool_array_value = proto.Field(
        proto.MESSAGE, number=7, oneof="value", message=types.BoolArray,
    )
    double_array_value = proto.Field(
        proto.MESSAGE, number=8, oneof="value", message=types.DoubleArray,
    )
    int64_array_value = proto.Field(
        proto.MESSAGE, number=11, oneof="value", message=types.Int64Array,
    )
    string_array_value = proto.Field(
        proto.MESSAGE, number=12, oneof="value", message=types.StringArray,
    )
    bytes_value = proto.Field(proto.BYTES, number=13, oneof="value",)
    metadata = proto.Field(proto.MESSAGE, number=14, message=Metadata,)


class FeatureValueList(proto.Message):
    r"""Container for list of values.
    Attributes:
        values (Sequence[google.cloud.aiplatform_v1beta1.types.FeatureValue]):
            A list of feature values. All of them should
            be the same data type.
    """

    values = proto.RepeatedField(proto.MESSAGE, number=1, message="FeatureValue",)


__all__ = tuple(sorted(__protobuf__.manifest))
