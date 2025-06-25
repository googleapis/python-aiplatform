# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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

from google.cloud.aiplatform.compat import types

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

# Test feature online store 1
_TEST_BIGTABLE_FOS1_ID = "my_fos1"
_TEST_BIGTABLE_FOS1_PATH = (
    f"{_TEST_PARENT}/featureOnlineStores/{_TEST_BIGTABLE_FOS1_ID}"
)
_TEST_BIGTABLE_FOS1_LABELS = {"my_key": "my_fos1"}
_TEST_BIGTABLE_FOS1 = types.feature_online_store.FeatureOnlineStore(
    name=_TEST_BIGTABLE_FOS1_PATH,
    bigtable=types.feature_online_store.FeatureOnlineStore.Bigtable(
        auto_scaling=types.feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
            min_node_count=1,
            max_node_count=2,
            cpu_utilization_target=50,
        )
    ),
    labels=_TEST_BIGTABLE_FOS1_LABELS,
)

# Test feature online store 2
_TEST_BIGTABLE_FOS2_ID = "my_fos2"
_TEST_BIGTABLE_FOS2_PATH = (
    f"{_TEST_PARENT}/featureOnlineStores/{_TEST_BIGTABLE_FOS2_ID}"
)
_TEST_BIGTABLE_FOS2_LABELS = {"my_key": "my_fos2"}
_TEST_BIGTABLE_FOS2 = types.feature_online_store.FeatureOnlineStore(
    name=_TEST_BIGTABLE_FOS2_PATH,
    bigtable=types.feature_online_store.FeatureOnlineStore.Bigtable(
        auto_scaling=types.feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
            min_node_count=2,
            max_node_count=3,
            cpu_utilization_target=60,
        )
    ),
    labels=_TEST_BIGTABLE_FOS2_LABELS,
)

# Test feature online store 3
_TEST_BIGTABLE_FOS3_ID = "my_fos3"
_TEST_BIGTABLE_FOS3_PATH = (
    f"{_TEST_PARENT}/featureOnlineStores/{_TEST_BIGTABLE_FOS3_ID}"
)
_TEST_BIGTABLE_FOS3_LABELS = {"my_key": "my_fos3"}
_TEST_BIGTABLE_FOS3 = types.feature_online_store.FeatureOnlineStore(
    name=_TEST_BIGTABLE_FOS3_PATH,
    bigtable=types.feature_online_store.FeatureOnlineStore.Bigtable(
        auto_scaling=types.feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
            min_node_count=3,
            max_node_count=4,
            cpu_utilization_target=70,
        )
    ),
    labels=_TEST_BIGTABLE_FOS3_LABELS,
)

# Test feature online store for optimized with esf endpoint
_TEST_ESF_OPTIMIZED_FOS_ID = "my_esf_optimized_fos"
_TEST_ESF_OPTIMIZED_FOS_PATH = (
    f"{_TEST_PARENT}/featureOnlineStores/{_TEST_ESF_OPTIMIZED_FOS_ID}"
)
_TEST_ESF_OPTIMIZED_FOS_LABELS = {"my_key": "my_esf_optimized_fos"}
_TEST_ESF_OPTIMIZED_FOS = types.feature_online_store.FeatureOnlineStore(
    name=_TEST_ESF_OPTIMIZED_FOS_PATH,
    optimized=types.feature_online_store.FeatureOnlineStore.Optimized(),
    dedicated_serving_endpoint=types.feature_online_store_v1.FeatureOnlineStore.DedicatedServingEndpoint(
        public_endpoint_domain_name="test-esf-endpoint",
    ),
    labels=_TEST_ESF_OPTIMIZED_FOS_LABELS,
)

# Test feature online store for optimized with psc endpoint
_TEST_PSC_OPTIMIZED_FOS_ID = "my_psc_optimized_fos"
_TEST_PSC_OPTIMIZED_FOS_PATH = (
    f"{_TEST_PARENT}/featureOnlineStores/{_TEST_PSC_OPTIMIZED_FOS_ID}"
)
_TEST_PSC_OPTIMIZED_FOS_LABELS = {"my_key": "my_psc_optimized_fos"}
_TEST_PSC_PROJECT_ALLOWLIST = ["project-1", "project-2"]
_TEST_PSC_OPTIMIZED_FOS = types.feature_online_store_v1.FeatureOnlineStore(
    name=_TEST_PSC_OPTIMIZED_FOS_PATH,
    optimized=types.feature_online_store_v1.FeatureOnlineStore.Optimized(),
    dedicated_serving_endpoint=types.feature_online_store_v1.FeatureOnlineStore.DedicatedServingEndpoint(
        private_service_connect_config=types.service_networking_v1.PrivateServiceConnectConfig(
            enable_private_service_connect=True,
            project_allowlist=_TEST_PSC_PROJECT_ALLOWLIST,
        ),
    ),
    labels=_TEST_PSC_OPTIMIZED_FOS_LABELS,
)

_TEST_FOS_LIST = [_TEST_BIGTABLE_FOS1, _TEST_BIGTABLE_FOS2, _TEST_BIGTABLE_FOS3]

# Test feature online store for optimized with esf endpoint but sync has not run yet.
_TEST_ESF_OPTIMIZED_FOS2_ID = "my_esf_optimised_fos2"
_TEST_ESF_OPTIMIZED_FOS2_PATH = (
    f"{_TEST_PARENT}/featureOnlineStores/{_TEST_ESF_OPTIMIZED_FOS2_ID}"
)
_TEST_ESF_OPTIMIZED_FOS2_LABELS = {"my_key": "my_esf_optimized_fos2"}
_TEST_ESF_OPTIMIZED_FOS2 = types.feature_online_store_v1.FeatureOnlineStore(
    name=_TEST_ESF_OPTIMIZED_FOS2_PATH,
    optimized=types.feature_online_store_v1.FeatureOnlineStore.Optimized(),
    dedicated_serving_endpoint=types.feature_online_store_v1.FeatureOnlineStore.DedicatedServingEndpoint(),
    labels=_TEST_ESF_OPTIMIZED_FOS_LABELS,
)


# Test feature view 1
_TEST_FV1_ID = "my_fv1"
_TEST_FV1_PATH = f"{_TEST_BIGTABLE_FOS1_PATH}/featureViews/my_fv1"
_TEST_FV1_LABELS = {"my_key": "my_fv1"}
_TEST_FV1_BQ_URI = f"bq://{_TEST_PROJECT}.my_dataset.my_table"
_TEST_FV1_ENTITY_ID_COLUMNS = ["entity_id"]
_TEST_FV1 = types.feature_view.FeatureView(
    name=_TEST_FV1_PATH,
    big_query_source=types.feature_view.FeatureView.BigQuerySource(
        uri=_TEST_FV1_BQ_URI,
        entity_id_columns=_TEST_FV1_ENTITY_ID_COLUMNS,
    ),
    labels=_TEST_FV1_LABELS,
)

# Test feature view 2
_TEST_FV2_ID = "my_fv2"
_TEST_FV2_PATH = f"{_TEST_BIGTABLE_FOS1_PATH}/featureViews/my_fv2"
_TEST_FV2_LABELS = {"my_key": "my_fv2"}
_TEST_FV2_BQ_URI = f"bq://{_TEST_PROJECT}.my_dataset.my_table"
_TEST_FV2_ENTITY_ID_COLUMNS = ["entity_id"]
_TEST_FV2 = types.feature_view.FeatureView(
    name=_TEST_FV2_PATH,
    big_query_source=types.feature_view.FeatureView.BigQuerySource(
        uri=_TEST_FV2_BQ_URI,
        entity_id_columns=_TEST_FV2_ENTITY_ID_COLUMNS,
    ),
    labels=_TEST_FV2_LABELS,
)

# Test feature view 3
_TEST_FV3_ID = "my_fv3"
_TEST_FV3_PATH = f"{_TEST_BIGTABLE_FOS1_PATH}/featureViews/my_fv3"
_TEST_FV3_LABELS = {"my_key": "my_fv3"}
_TEST_FV3_BQ_URI = f"bq://{_TEST_PROJECT}.my_dataset.my_table"
_TEST_FV3 = types.feature_view.FeatureView(
    name=_TEST_FV3_PATH,
    vertex_rag_source=types.feature_view.FeatureView.VertexRagSource(
        uri=_TEST_FV3_BQ_URI,
    ),
    labels=_TEST_FV3_LABELS,
)


# Test feature view sync 1
_TEST_FV_SYNC1_ID = "my_fv_sync1"
_TEST_FV_SYNC1_PATH = f"{_TEST_FV1_PATH}/featureViewSyncs/my_fv_sync1"
_TEST_FV_SYNC1 = types.feature_view_sync.FeatureViewSync(
    name=_TEST_FV_SYNC1_PATH,
)
_TEST_FV_SYNC1_RESPONSE = (
    types.feature_online_store_admin_service.SyncFeatureViewResponse(
        feature_view_sync=_TEST_FV_SYNC1_PATH,
    )
)

# Test feature view sync 2
_TEST_FV_SYNC2_ID = "my_fv_sync2"
_TEST_FV_SYNC2_PATH = f"{_TEST_FV2_PATH}/featureViewSyncs/my_fv_sync2"
_TEST_FV_SYNC2 = types.feature_view_sync.FeatureViewSync(
    name=_TEST_FV_SYNC2_PATH,
)

_TEST_FV_SYNC_LIST = [_TEST_FV_SYNC1, _TEST_FV_SYNC2]

# Test optimized feature view 1
_TEST_OPTIMIZED_FV1_ID = "optimized_fv1"
_TEST_OPTIMIZED_FV1_PATH = f"{_TEST_ESF_OPTIMIZED_FOS_PATH}/featureViews/optimized_fv1"
_TEST_OPTIMIZED_FV1 = types.feature_view.FeatureView(
    name=_TEST_OPTIMIZED_FV1_PATH,
    big_query_source=types.feature_view.FeatureView.BigQuerySource(
        uri=_TEST_FV1_BQ_URI,
        entity_id_columns=_TEST_FV1_ENTITY_ID_COLUMNS,
    ),
    labels=_TEST_FV1_LABELS,
)

# Test optimized feature view 2
_TEST_OPTIMIZED_FV2_ID = "optimized_fv2"
_TEST_OPTIMIZED_FV2_PATH = f"{_TEST_ESF_OPTIMIZED_FOS2_PATH}/featureViews/optimized_fv2"
_TEST_OPTIMIZED_FV2 = types.feature_view.FeatureView(
    name=_TEST_OPTIMIZED_FV2_PATH,
    big_query_source=types.feature_view.FeatureView.BigQuerySource(
        uri=_TEST_FV1_BQ_URI,
        entity_id_columns=_TEST_FV1_ENTITY_ID_COLUMNS,
    ),
    labels=_TEST_FV1_LABELS,
)

# Test embedding feature view 1
_TEST_EMBEDDING_FV1_ID = "embedding_fv1"
_TEST_EMBEDDING_FV1_PATH = f"{_TEST_ESF_OPTIMIZED_FOS_PATH}/featureViews/embedding_fv1"
_TEST_EMBEDDING_FV1 = types.feature_view.FeatureView(
    name=_TEST_EMBEDDING_FV1_PATH,
    big_query_source=types.feature_view.FeatureView.BigQuerySource(
        uri=_TEST_FV1_BQ_URI,
        entity_id_columns=_TEST_FV1_ENTITY_ID_COLUMNS,
    ),
    labels=_TEST_FV1_LABELS,
)

_TEST_STRING_FILTER = (
    types.feature_online_store_service.NearestNeighborQuery.StringFilter(
        name="filter_name",
        allow_tokens=["allow_token_1", "allow_token_2"],
    )
)

# Test optimized embedding feature view
_TEST_OPTIMIZED_EMBEDDING_FV_ID = "optimized_embedding_fv"
_TEST_OPTIMIZED_EMBEDDING_FV_PATH = (
    f"{_TEST_ESF_OPTIMIZED_FOS_PATH}/featureViews/{_TEST_OPTIMIZED_EMBEDDING_FV_ID}"
)
_TEST_OPTIMIZED_EMBEDDING_FV = types.feature_view.FeatureView(
    name=_TEST_OPTIMIZED_EMBEDDING_FV_PATH,
    big_query_source=types.feature_view.FeatureView.BigQuerySource(
        uri=_TEST_FV1_BQ_URI,
        entity_id_columns=_TEST_FV1_ENTITY_ID_COLUMNS,
    ),
    labels=_TEST_FV1_LABELS,
    index_config=types.feature_view.FeatureView.IndexConfig(
        embedding_column="embedding_column",
        filter_columns=["col1", "col2"],
        crowding_column="crowding_column",
        embedding_dimension=123,
        distance_measure_type=types.feature_view.FeatureView.IndexConfig.DistanceMeasureType.DOT_PRODUCT_DISTANCE,
    ),
)

# Response for FetchFeatureValues
_TEST_FV_FETCH1 = types.feature_online_store_service_v1.FetchFeatureValuesResponse(
    key_values=types.feature_online_store_service_v1.FetchFeatureValuesResponse.FeatureNameValuePairList(
        features=[
            types.feature_online_store_service_v1.FetchFeatureValuesResponse.FeatureNameValuePairList.FeatureNameValuePair(
                name="key1",
                value=types.featurestore_online_service.FeatureValue(
                    string_value="value1",
                ),
            ),
        ]
    )
)

# Response for SearchNearestEntitiesResponse
_TEST_FV_SEARCH1 = types.feature_online_store_service_v1.SearchNearestEntitiesResponse(
    nearest_neighbors=types.feature_online_store_service_v1.NearestNeighbors(
        neighbors=[
            types.feature_online_store_service_v1.NearestNeighbors.Neighbor(
                entity_id="neighbor_entity_id_1",
                distance=0.1,
            ),
        ]
    )
)

_TEST_FG1_ID = "my_fg1"
_TEST_FG1_PATH = f"{_TEST_PARENT}/featureGroups/{_TEST_FG1_ID}"
_TEST_FG1_BQ_URI = f"bq://{_TEST_PROJECT}.my_dataset.my_table_for_fg1"
_TEST_FG1_ENTITY_ID_COLUMNS = ["entity_id"]
_TEST_FG1_LABELS = {"my_key": "my_fg1"}
_TEST_FG1 = types.feature_group.FeatureGroup(
    name=_TEST_FG1_PATH,
    big_query=types.feature_group.FeatureGroup.BigQuery(
        big_query_source=types.io.BigQuerySource(
            input_uri=_TEST_FG1_BQ_URI,
        ),
        entity_id_columns=_TEST_FG1_ENTITY_ID_COLUMNS,
    ),
    labels=_TEST_FG1_LABELS,
)


_TEST_FG2_ID = "my_fg2"
_TEST_FG2_F1_ID = "my_fg2_f1"
_TEST_FG2_F2_ID = "my_fg2_f2"
_TEST_FG2_PATH = f"{_TEST_PARENT}/featureGroups/{_TEST_FG2_ID}"
_TEST_FG2_BQ_URI = f"bq://{_TEST_PROJECT}.my_dataset.my_table_for_fg2"
_TEST_FG2_ENTITY_ID_COLUMNS = ["entity_id1", "entity_id2"]
_TEST_FG2_LABELS = {"my_key2": "my_fg2"}
_TEST_FG2 = types.feature_group.FeatureGroup(
    name=_TEST_FG2_PATH,
    big_query=types.feature_group.FeatureGroup.BigQuery(
        big_query_source=types.io.BigQuerySource(
            input_uri=_TEST_FG2_BQ_URI,
        ),
        entity_id_columns=_TEST_FG2_ENTITY_ID_COLUMNS,
    ),
    labels=_TEST_FG2_LABELS,
)


_TEST_FG3_ID = "my_fg3"
_TEST_FG3_PATH = f"{_TEST_PARENT}/featureGroups/{_TEST_FG3_ID}"
_TEST_FG3_BQ_URI = f"bq://{_TEST_PROJECT}.my_dataset.my_table_for_fg3"
_TEST_FG3_ENTITY_ID_COLUMNS = ["entity_id1", "entity_id2", "entity_id3"]
_TEST_FG3_LABELS = {"my_key3": "my_fg3"}
_TEST_FG3 = types.feature_group.FeatureGroup(
    name=_TEST_FG3_PATH,
    big_query=types.feature_group.FeatureGroup.BigQuery(
        big_query_source=types.io.BigQuerySource(
            input_uri=_TEST_FG3_BQ_URI,
        ),
        entity_id_columns=_TEST_FG3_ENTITY_ID_COLUMNS,
    ),
    labels=_TEST_FG3_LABELS,
)

_TEST_FG_LIST = [_TEST_FG1, _TEST_FG2, _TEST_FG3]

_TEST_FG1_F1_ID = "my_fg1_f1"
_TEST_FG1_F1_PATH = (
    f"{_TEST_PARENT}/featureGroups/{_TEST_FG1_ID}/features/{_TEST_FG1_F1_ID}"
)
_TEST_FG1_F1_DESCRIPTION = "My feature 1 in feature group 1"
_TEST_FG1_F1_LABELS = {"my_fg1_feature": "f1"}
_TEST_FG1_F1_POINT_OF_CONTACT = "fg1-f1-announce-list"
_TEST_FG1_F1 = types.feature.Feature(
    name=_TEST_FG1_F1_PATH,
    description=_TEST_FG1_F1_DESCRIPTION,
    labels=_TEST_FG1_F1_LABELS,
    point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
)


_TEST_FG1_F2_ID = "my_fg1_f2"
_TEST_FG1_F2_PATH = (
    f"{_TEST_PARENT}/featureGroups/{_TEST_FG1_ID}/features/{_TEST_FG1_F2_ID}"
)
_TEST_FG1_F2_DESCRIPTION = "My feature 2 in feature group 1"
_TEST_FG1_F2_LABELS = {"my_fg1_feature": "f2"}
_TEST_FG1_F2_POINT_OF_CONTACT = "fg1-f2-announce-list"
_TEST_FG1_F2_VERSION_COLUMN_NAME = "specific_column_for_feature_2"
_TEST_FG1_F2 = types.feature.Feature(
    name=_TEST_FG1_F2_PATH,
    version_column_name=_TEST_FG1_F2_VERSION_COLUMN_NAME,
    description=_TEST_FG1_F2_DESCRIPTION,
    labels=_TEST_FG1_F2_LABELS,
    point_of_contact=_TEST_FG1_F2_POINT_OF_CONTACT,
)

_TEST_FG1_FEATURE_LIST = [_TEST_FG1_F1, _TEST_FG1_F2]

_TEST_FG1_FM1_ID = "my_fg1_fm1"
_TEST_FG1_FM1_PATH = (
    f"{_TEST_PARENT}/featureGroups/{_TEST_FG1_ID}/featureMonitors/{_TEST_FG1_FM1_ID}"
)
_TEST_FG1_FM1_DESCRIPTION = "My feature monitor 1 in feature group 1"
_TEST_FG1_FM1_LABELS = {"my_fg1_feature_monitor": "fm1"}
_TEST_FG1_FM1 = types.feature_monitor.FeatureMonitor(
    name=_TEST_FG1_FM1_PATH,
    description=_TEST_FG1_FM1_DESCRIPTION,
    labels=_TEST_FG1_FM1_LABELS,
    schedule_config=types.feature_monitor.ScheduleConfig(cron="0 0 * * *"),
    feature_selection_config=types.feature_monitor.FeatureSelectionConfig(
        feature_configs=[
            types.feature_monitor.FeatureSelectionConfig.FeatureConfig(
                feature_id="my_fg1_f1",
                drift_threshold=0.3,
            ),
            types.feature_monitor.FeatureSelectionConfig.FeatureConfig(
                feature_id="my_fg1_f2",
                drift_threshold=0.4,
            ),
        ]
    ),
)
_TEST_FG1_FM1_FEATURE_SELECTION_CONFIGS = [("my_fg1_f1", 0.3), ("my_fg1_f2", 0.4)]
_TEST_FG1_FM1_SCHEDULE_CONFIG = "0 0 * * *"
_TEST_FG1_FM2_ID = "my_fg1_fm2"
_TEST_FG1_FM2_PATH = (
    f"{_TEST_PARENT}/featureGroups/{_TEST_FG1_ID}/featureMonitors/{_TEST_FG1_FM2_ID}"
)
_TEST_FG1_FM2_DESCRIPTION = "My feature monitor 2 in feature group 1"
_TEST_FG1_FM2_LABELS = {"my_fg1_feature_monitor": "fm2"}
_TEST_FG1_FM2_FEATURE_SELECTION_CONFIGS = [("my_fg1_f2", 0.5)]
_TEST_FG1_FM2_SCHEDULE_CONFIG = "8 0 * * *"
_TEST_FG1_FM2 = types.feature_monitor.FeatureMonitor(
    name=_TEST_FG1_FM2_PATH,
    description=_TEST_FG1_FM2_DESCRIPTION,
    labels=_TEST_FG1_FM2_LABELS,
    schedule_config=types.feature_monitor.ScheduleConfig(cron="8 0 * * *"),
    feature_selection_config=types.feature_monitor.FeatureSelectionConfig(
        feature_configs=[
            types.feature_monitor.FeatureSelectionConfig.FeatureConfig(
                feature_id="my_fg1_f2",
                drift_threshold=0.5,
            ),
        ]
    ),
)
_TEST_FG1_FM_LIST = [_TEST_FG1_FM1, _TEST_FG1_FM2]

_TEST_FG1_FMJ1_ID = "1234567890"
_TEST_FG1_FMJ1_PATH = f"{_TEST_PARENT}/featureGroups/{_TEST_FG1_ID}/featureMonitors/{_TEST_FG1_FM1_ID}/featureMonitorJobs/{_TEST_FG1_FMJ1_ID}"
_TEST_FG1_FMJ1_DESCRIPTION = "My feature monitor job 1 in feature monitor 1"
_TEST_FG1_FMJ1_LABELS = {"my_fg1_feature_monitor_job": "fmj1"}
_TEST_FG1_F1_FEATURE_STATS_AND_ANOMALY = types.feature_monitor.FeatureStatsAndAnomaly(
    feature_id="my_fg1_f1",
    distribution_deviation=0.5,
    drift_detection_threshold=0.4,
    drift_detected=True,
    feature_monitor_job_id=_TEST_FG1_FMJ1_ID,
    feature_monitor_id=_TEST_FG1_FM1_ID,
)
_TEST_FG1_F2_FEATURE_STATS_AND_ANOMALY = types.feature_monitor.FeatureStatsAndAnomaly(
    feature_id="my_fg1_f2",
    distribution_deviation=0.2,
    drift_detection_threshold=0.4,
    drift_detected=False,
    feature_monitor_job_id=_TEST_FG1_FMJ1_ID,
    feature_monitor_id=_TEST_FG1_FM1_ID,
)
_TEST_FG1_FMJ1_FEATURE_STATS_AND_ANOMALIES = [
    _TEST_FG1_F1_FEATURE_STATS_AND_ANOMALY,
    _TEST_FG1_F2_FEATURE_STATS_AND_ANOMALY,
]
_TEST_FG1_FMJ1 = types.feature_monitor_job.FeatureMonitorJob(
    name=_TEST_FG1_FMJ1_PATH,
    description=_TEST_FG1_FMJ1_DESCRIPTION,
    labels=_TEST_FG1_FMJ1_LABELS,
    job_summary=types.feature_monitor_job.FeatureMonitorJob.JobSummary(
        feature_stats_and_anomalies=_TEST_FG1_FMJ1_FEATURE_STATS_AND_ANOMALIES
    ),
)
_TEST_FG1_FMJ2_ID = "1234567891"
_TEST_FG1_FMJ2_PATH = f"{_TEST_PARENT}/featureGroups/{_TEST_FG1_ID}/featureMonitors/{_TEST_FG1_FM1_ID}/featureMonitorJobs/{_TEST_FG1_FMJ2_ID}"
_TEST_FG1_FMJ2_DESCRIPTION = "My feature monitor job 2 in feature monitor 1"
_TEST_FG1_FMJ2_LABELS = {"my_fg1_feature_monitor_job": "fmj2"}
_TEST_FG1_FMJ2 = types.feature_monitor_job.FeatureMonitorJob(
    name=_TEST_FG1_FMJ2_PATH,
    description=_TEST_FG1_FMJ2_DESCRIPTION,
    labels=_TEST_FG1_FMJ2_LABELS,
)
_TEST_FG1_FMJ_LIST = [_TEST_FG1_FMJ1, _TEST_FG1_FMJ2]

_TEST_FG1_F1_FEATURE_STATS_AND_ANOMALY = types.feature_monitor.FeatureStatsAndAnomaly(
    feature_id="my_fg1_f1",
    distribution_deviation=0.5,
    drift_detection_threshold=0.4,
    drift_detected=True,
    feature_monitor_job_id="1234567890",
    feature_monitor_id="1234567891",
)
_TEST_FG1_F1_WITH_STATS = types.feature_v1beta1.Feature(
    name=_TEST_FG1_F1_PATH,
    description=_TEST_FG1_F1_DESCRIPTION,
    labels=_TEST_FG1_F1_LABELS,
    point_of_contact=_TEST_FG1_F1_POINT_OF_CONTACT,
    feature_stats_and_anomaly=[_TEST_FG1_F1_FEATURE_STATS_AND_ANOMALY],
)

# Test feature view 4
_TEST_FV4_ID = "my_fv4"
_TEST_FV4_PATH = f"{_TEST_BIGTABLE_FOS1_PATH}/featureViews/my_fv4"
_TEST_FV4_LABELS = {"my_key": "my_fv4"}
_TEST_FV4 = types.feature_view.FeatureView(
    name=_TEST_FV4_PATH,
    feature_registry_source=types.feature_view.FeatureView.FeatureRegistrySource(
        feature_groups=[
            types.feature_view.FeatureView.FeatureRegistrySource.FeatureGroup(
                feature_group_id=_TEST_FG1_ID,
                feature_ids=[_TEST_FG1_F1_ID, _TEST_FG1_F2_ID],
            ),
            types.feature_view.FeatureView.FeatureRegistrySource.FeatureGroup(
                feature_group_id=_TEST_FG2_ID,
                feature_ids=[_TEST_FG2_F1_ID, _TEST_FG2_F2_ID],
            ),
        ],
    ),
    labels=_TEST_FV4_LABELS,
)

_TEST_FV_LIST = [_TEST_FV1, _TEST_FV2, _TEST_FV3, _TEST_FV4]
