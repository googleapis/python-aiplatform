# -*- coding: utf-8 -*-
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
from __future__ import annotations

from typing import MutableMapping, MutableSequence

import proto  # type: ignore

from google.cloud.aiplatform_v1.types import featurestore_online_service
from google.protobuf import struct_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "FeatureViewDataFormat",
        "FeatureViewDataKey",
        "FetchFeatureValuesRequest",
        "FetchFeatureValuesResponse",
    },
)


class FeatureViewDataFormat(proto.Enum):
    r"""Format of the data in the Feature View.

    Values:
        FEATURE_VIEW_DATA_FORMAT_UNSPECIFIED (0):
            Not set. Will be treated as the KeyValue
            format.
        KEY_VALUE (1):
            Return response data in key-value format.
        PROTO_STRUCT (2):
            Return response data in proto Struct format.
    """
    FEATURE_VIEW_DATA_FORMAT_UNSPECIFIED = 0
    KEY_VALUE = 1
    PROTO_STRUCT = 2


class FeatureViewDataKey(proto.Message):
    r"""Lookup key for a feature view.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        key (str):
            String key to use for lookup.

            This field is a member of `oneof`_ ``key_oneof``.
    """

    key: str = proto.Field(
        proto.STRING,
        number=1,
        oneof="key_oneof",
    )


class FetchFeatureValuesRequest(proto.Message):
    r"""Request message for
    [FeatureOnlineStoreService.FetchFeatureValues][google.cloud.aiplatform.v1.FeatureOnlineStoreService.FetchFeatureValues].
    All the features under the requested feature view will be returned.

    Attributes:
        feature_view (str):
            Required. FeatureView resource format
            ``projects/{project}/locations/{location}/featureOnlineStores/{featureOnlineStore}/featureViews/{featureView}``
        data_key (google.cloud.aiplatform_v1.types.FeatureViewDataKey):
            Optional. The request key to fetch feature
            values for.
        data_format (google.cloud.aiplatform_v1.types.FeatureViewDataFormat):
            Optional. Response data format. If not set,
            [FeatureViewDataFormat.KEY_VALUE][google.cloud.aiplatform.v1.FeatureViewDataFormat.KEY_VALUE]
            will be used.
    """

    feature_view: str = proto.Field(
        proto.STRING,
        number=1,
    )
    data_key: "FeatureViewDataKey" = proto.Field(
        proto.MESSAGE,
        number=6,
        message="FeatureViewDataKey",
    )
    data_format: "FeatureViewDataFormat" = proto.Field(
        proto.ENUM,
        number=7,
        enum="FeatureViewDataFormat",
    )


class FetchFeatureValuesResponse(proto.Message):
    r"""Response message for
    [FeatureOnlineStoreService.FetchFeatureValues][google.cloud.aiplatform.v1.FeatureOnlineStoreService.FetchFeatureValues]

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        key_values (google.cloud.aiplatform_v1.types.FetchFeatureValuesResponse.FeatureNameValuePairList):
            Feature values in KeyValue format.

            This field is a member of `oneof`_ ``format``.
        proto_struct (google.protobuf.struct_pb2.Struct):
            Feature values in proto Struct format.

            This field is a member of `oneof`_ ``format``.
    """

    class FeatureNameValuePairList(proto.Message):
        r"""Response structure in the format of key (feature name) and
        (feature) value pair.

        Attributes:
            features (MutableSequence[google.cloud.aiplatform_v1.types.FetchFeatureValuesResponse.FeatureNameValuePairList.FeatureNameValuePair]):
                List of feature names and values.
        """

        class FeatureNameValuePair(proto.Message):
            r"""Feature name & value pair.

            .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

            Attributes:
                value (google.cloud.aiplatform_v1.types.FeatureValue):
                    Feature value.

                    This field is a member of `oneof`_ ``data``.
                name (str):
                    Feature short name.
            """

            value: featurestore_online_service.FeatureValue = proto.Field(
                proto.MESSAGE,
                number=2,
                oneof="data",
                message=featurestore_online_service.FeatureValue,
            )
            name: str = proto.Field(
                proto.STRING,
                number=1,
            )

        features: MutableSequence[
            "FetchFeatureValuesResponse.FeatureNameValuePairList.FeatureNameValuePair"
        ] = proto.RepeatedField(
            proto.MESSAGE,
            number=1,
            message="FetchFeatureValuesResponse.FeatureNameValuePairList.FeatureNameValuePair",
        )

    key_values: FeatureNameValuePairList = proto.Field(
        proto.MESSAGE,
        number=3,
        oneof="format",
        message=FeatureNameValuePairList,
    )
    proto_struct: struct_pb2.Struct = proto.Field(
        proto.MESSAGE,
        number=2,
        oneof="format",
        message=struct_pb2.Struct,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
