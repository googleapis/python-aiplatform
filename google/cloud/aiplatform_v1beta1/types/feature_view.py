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

from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "FeatureView",
    },
)


class FeatureView(proto.Message):
    r"""FeatureView is representation of values that the
    FeatureOnlineStore will serve based on its syncConfig.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        big_query_source (google.cloud.aiplatform_v1beta1.types.FeatureView.BigQuerySource):
            Optional. Configures how data is supposed to
            be extracted from a BigQuery source to be loaded
            onto the FeatureOnlineStore.

            This field is a member of `oneof`_ ``source``.
        feature_registry_source (google.cloud.aiplatform_v1beta1.types.FeatureView.FeatureRegistrySource):
            Optional. Configures the features from a
            Feature Registry source that need to be loaded
            onto the FeatureOnlineStore.

            This field is a member of `oneof`_ ``source``.
        name (str):
            Output only. Name of the FeatureView. Format:
            ``projects/{project}/locations/{location}/featureOnlineStores/{feature_online_store}/featureViews/{feature_view}``
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this FeatureView
            was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this FeatureView
            was last updated.
        etag (str):
            Optional. Used to perform consistent
            read-modify-write updates. If not set, a blind
            "overwrite" update happens.
        labels (MutableMapping[str, str]):
            Optional. The labels with user-defined
            metadata to organize your FeatureViews.

            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.

            See https://goo.gl/xmQnxf for more information
            on and examples of labels. No more than 64 user
            labels can be associated with one
            FeatureOnlineStore(System labels are excluded)."
            System reserved label keys are prefixed with
            "aiplatform.googleapis.com/" and are immutable.
        sync_config (google.cloud.aiplatform_v1beta1.types.FeatureView.SyncConfig):
            Configures when data is to be synced/updated
            for this FeatureView. At the end of the sync the
            latest featureValues for each entityId of this
            FeatureView are made ready for online serving.
        vector_search_config (google.cloud.aiplatform_v1beta1.types.FeatureView.VectorSearchConfig):
            Optional. Configuration for vector search. It
            contains the required configurations to create
            an index from source data, so that approximate
            nearest neighbor (a.k.a ANN) algorithms search
            can be performed during online serving.
    """

    class BigQuerySource(proto.Message):
        r"""

        Attributes:
            uri (str):
                Required. The BigQuery view URI that will be
                materialized on each sync trigger based on
                FeatureView.SyncConfig.
            entity_id_columns (MutableSequence[str]):
                Required. Columns to construct entity_id / row keys. Start
                by supporting 1 only.
        """

        uri: str = proto.Field(
            proto.STRING,
            number=1,
        )
        entity_id_columns: MutableSequence[str] = proto.RepeatedField(
            proto.STRING,
            number=2,
        )

    class SyncConfig(proto.Message):
        r"""

        Attributes:
            cron (str):
                Cron schedule (https://en.wikipedia.org/wiki/Cron) to launch
                scheduled runs. To explicitly set a timezone to the cron
                tab, apply a prefix in the cron tab:
                "CRON_TZ=${IANA_TIME_ZONE}" or "TZ=${IANA_TIME_ZONE}". The
                ${IANA_TIME_ZONE} may only be a valid string from IANA time
                zone database. For example, "CRON_TZ=America/New_York 1 \*
                \* \* \*", or "TZ=America/New_York 1 \* \* \* \*".
        """

        cron: str = proto.Field(
            proto.STRING,
            number=1,
        )

    class VectorSearchConfig(proto.Message):
        r"""Configuration for vector search.

        This message has `oneof`_ fields (mutually exclusive fields).
        For each oneof, at most one member field can be set at the same time.
        Setting any member of the oneof automatically clears all other
        members.

        .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

        Attributes:
            tree_ah_config (google.cloud.aiplatform_v1beta1.types.FeatureView.VectorSearchConfig.TreeAHConfig):
                Optional. Configuration options for the
                tree-AH algorithm (Shallow tree
                + Asymmetric Hashing). Please refer to this
                  paper for more details:

                https://arxiv.org/abs/1908.10396

                This field is a member of `oneof`_ ``algorithm_config``.
            brute_force_config (google.cloud.aiplatform_v1beta1.types.FeatureView.VectorSearchConfig.BruteForceConfig):
                Optional. Configuration options for using
                brute force search, which simply implements the
                standard linear search in the database for each
                query. It is primarily meant for benchmarking
                and to generate the ground truth for approximate
                search.

                This field is a member of `oneof`_ ``algorithm_config``.
            embedding_column (str):
                Optional. Column of embedding. This column contains the
                source data to create index for vector search.
                embedding_column must be set when using vector search.
            filter_columns (MutableSequence[str]):
                Optional. Columns of features that're used to
                filter vector search results.
            crowding_column (str):
                Optional. Column of crowding. This column contains crowding
                attribute which is a constraint on a neighbor list produced
                by nearest neighbor search requiring that no more than some
                value k' of the k neighbors returned have the same value of
                crowding_attribute.
            embedding_dimension (int):
                Optional. The number of dimensions of the
                input embedding.

                This field is a member of `oneof`_ ``_embedding_dimension``.
            distance_measure_type (google.cloud.aiplatform_v1beta1.types.FeatureView.VectorSearchConfig.DistanceMeasureType):
                Optional. The distance measure used in
                nearest neighbor search.
        """

        class DistanceMeasureType(proto.Enum):
            r"""

            Values:
                DISTANCE_MEASURE_TYPE_UNSPECIFIED (0):
                    Should not be set.
                SQUARED_L2_DISTANCE (1):
                    Euclidean (L_2) Distance.
                COSINE_DISTANCE (2):
                    Cosine Distance. Defined as 1 - cosine similarity.

                    We strongly suggest using DOT_PRODUCT_DISTANCE +
                    UNIT_L2_NORM instead of COSINE distance. Our algorithms have
                    been more optimized for DOT_PRODUCT distance which, when
                    combined with UNIT_L2_NORM, is mathematically equivalent to
                    COSINE distance and results in the same ranking.
                DOT_PRODUCT_DISTANCE (3):
                    Dot Product Distance. Defined as a negative
                    of the dot product.
            """
            DISTANCE_MEASURE_TYPE_UNSPECIFIED = 0
            SQUARED_L2_DISTANCE = 1
            COSINE_DISTANCE = 2
            DOT_PRODUCT_DISTANCE = 3

        class BruteForceConfig(proto.Message):
            r""" """

        class TreeAHConfig(proto.Message):
            r"""

            .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

            Attributes:
                leaf_node_embedding_count (int):
                    Optional. Number of embeddings on each leaf
                    node. The default value is 1000 if not set.

                    This field is a member of `oneof`_ ``_leaf_node_embedding_count``.
            """

            leaf_node_embedding_count: int = proto.Field(
                proto.INT64,
                number=1,
                optional=True,
            )

        tree_ah_config: "FeatureView.VectorSearchConfig.TreeAHConfig" = proto.Field(
            proto.MESSAGE,
            number=8,
            oneof="algorithm_config",
            message="FeatureView.VectorSearchConfig.TreeAHConfig",
        )
        brute_force_config: "FeatureView.VectorSearchConfig.BruteForceConfig" = (
            proto.Field(
                proto.MESSAGE,
                number=9,
                oneof="algorithm_config",
                message="FeatureView.VectorSearchConfig.BruteForceConfig",
            )
        )
        embedding_column: str = proto.Field(
            proto.STRING,
            number=3,
        )
        filter_columns: MutableSequence[str] = proto.RepeatedField(
            proto.STRING,
            number=4,
        )
        crowding_column: str = proto.Field(
            proto.STRING,
            number=5,
        )
        embedding_dimension: int = proto.Field(
            proto.INT32,
            number=6,
            optional=True,
        )
        distance_measure_type: "FeatureView.VectorSearchConfig.DistanceMeasureType" = (
            proto.Field(
                proto.ENUM,
                number=7,
                enum="FeatureView.VectorSearchConfig.DistanceMeasureType",
            )
        )

    class FeatureRegistrySource(proto.Message):
        r"""A Feature Registry source for features that need to be synced
        to Online Store.

        Attributes:
            feature_groups (MutableSequence[google.cloud.aiplatform_v1beta1.types.FeatureView.FeatureRegistrySource.FeatureGroup]):
                Required. List of features that need to be
                synced to Online Store.
        """

        class FeatureGroup(proto.Message):
            r"""Features belonging to a single feature group that will be
            synced to Online Store.

            Attributes:
                feature_group_id (str):
                    Required. Identifier of the feature group.
                feature_ids (MutableSequence[str]):
                    Required. Identifiers of features under the
                    feature group.
            """

            feature_group_id: str = proto.Field(
                proto.STRING,
                number=1,
            )
            feature_ids: MutableSequence[str] = proto.RepeatedField(
                proto.STRING,
                number=2,
            )

        feature_groups: MutableSequence[
            "FeatureView.FeatureRegistrySource.FeatureGroup"
        ] = proto.RepeatedField(
            proto.MESSAGE,
            number=1,
            message="FeatureView.FeatureRegistrySource.FeatureGroup",
        )

    big_query_source: BigQuerySource = proto.Field(
        proto.MESSAGE,
        number=6,
        oneof="source",
        message=BigQuerySource,
    )
    feature_registry_source: FeatureRegistrySource = proto.Field(
        proto.MESSAGE,
        number=9,
        oneof="source",
        message=FeatureRegistrySource,
    )
    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=2,
        message=timestamp_pb2.Timestamp,
    )
    update_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=3,
        message=timestamp_pb2.Timestamp,
    )
    etag: str = proto.Field(
        proto.STRING,
        number=4,
    )
    labels: MutableMapping[str, str] = proto.MapField(
        proto.STRING,
        proto.STRING,
        number=5,
    )
    sync_config: SyncConfig = proto.Field(
        proto.MESSAGE,
        number=7,
        message=SyncConfig,
    )
    vector_search_config: VectorSearchConfig = proto.Field(
        proto.MESSAGE,
        number=8,
        message=VectorSearchConfig,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
