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

from google.cloud.aiplatform_v1beta1.types import feature_monitoring_stats
from google.cloud.aiplatform_v1beta1.types import featurestore_monitoring
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1", manifest={"Feature",},
)


class Feature(proto.Message):
    r"""Feature Metadata information that describes an attribute of
    an entity type. For example, apple is an entity type, and color
    is a feature that describes apple.

    Attributes:
        name (str):
            Immutable. Name of the Feature. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}/features/{feature}``

            The last part feature is assigned by the client. The feature
            can be up to 64 characters long and can consist only of
            ASCII Latin letters A-Z and a-z, underscore(_), and ASCII
            digits 0-9 starting with a letter. The value will be unique
            given an entity type.
        description (str):
            Description of the Feature.
        value_type (google.cloud.aiplatform_v1beta1.types.Feature.ValueType):
            Required. Immutable. Type of Feature value.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this EntityType
            was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this EntityType
            was most recently updated.
        labels (Sequence[google.cloud.aiplatform_v1beta1.types.Feature.LabelsEntry]):
            Optional. The labels with user-defined
            metadata to organize your Features.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            on and examples of labels. No more than 64 user
            labels can be associated with one Feature
            (System labels are excluded)."
            System reserved label keys are prefixed with
            "aiplatform.googleapis.com/" and are immutable.
        etag (str):
            Used to perform a consistent read-modify-
            rite updates. If not set, a blind "overwrite"
            update happens.
        monitoring_config (google.cloud.aiplatform_v1beta1.types.FeaturestoreMonitoringConfig):
            Optional. The custom monitoring configuration for this
            Feature, if not set, use the monitoring_config defined for
            the EntityType this Feature belongs to.

            If this is populated with
            [FeaturestoreMonitoringConfig.disabled][] = true, snapshot
            analysis monitoring is disabled; if
            [FeaturestoreMonitoringConfig.monitoring_interval][]
            specified, snapshot analysis monitoring is enabled.
            Otherwise, snapshot analysis monitoring config is same as
            the EntityType's this Feature belongs to.
        monitoring_stats (Sequence[google.cloud.aiplatform_v1beta1.types.FeatureStatsAnomaly]):
            Output only. A list of historical [Snapshot
            Analysis][google.cloud.aiplatform.master.FeaturestoreMonitoringConfig.SnapshotAnalysis]
            stats requested by user, sorted by
            [FeatureStatsAnomaly.start_time][google.cloud.aiplatform.v1beta1.FeatureStatsAnomaly.start_time]
            descending.
    """

    class ValueType(proto.Enum):
        r"""An enum representing the value type of a feature."""
        VALUE_TYPE_UNSPECIFIED = 0
        BOOL = 1
        BOOL_ARRAY = 2
        DOUBLE = 3
        DOUBLE_ARRAY = 4
        INT64 = 9
        INT64_ARRAY = 10
        STRING = 11
        STRING_ARRAY = 12
        BYTES = 13

    name = proto.Field(proto.STRING, number=1,)
    description = proto.Field(proto.STRING, number=2,)
    value_type = proto.Field(proto.ENUM, number=3, enum=ValueType,)
    create_time = proto.Field(proto.MESSAGE, number=4, message=timestamp_pb2.Timestamp,)
    update_time = proto.Field(proto.MESSAGE, number=5, message=timestamp_pb2.Timestamp,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=6,)
    etag = proto.Field(proto.STRING, number=7,)
    monitoring_config = proto.Field(
        proto.MESSAGE,
        number=9,
        message=featurestore_monitoring.FeaturestoreMonitoringConfig,
    )
    monitoring_stats = proto.RepeatedField(
        proto.MESSAGE, number=10, message=feature_monitoring_stats.FeatureStatsAnomaly,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
