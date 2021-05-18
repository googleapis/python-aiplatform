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

from google.protobuf import duration_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={"FeaturestoreMonitoringConfig",},
)


class FeaturestoreMonitoringConfig(proto.Message):
    r"""Configuration of how features in Featurestore are monitored.
    Attributes:
        snapshot_analysis (google.cloud.aiplatform_v1beta1.types.FeaturestoreMonitoringConfig.SnapshotAnalysis):
            The config for Snapshot Analysis Based
            Feature Monitoring.
    """

    class SnapshotAnalysis(proto.Message):
        r"""Configuration of the Featurestore's Snapshot Analysis Based
        Monitoring. This type of analysis generates statistics for each
        Feature based on a snapshot of the latest feature value of each
        entities every monitoring_interval.

        Attributes:
            disabled (bool):
                The monitoring schedule for snapshot analysis. For
                EntityType-level config: unset / disabled = true indicates
                disabled by default for Features under it; otherwise by
                default enable snapshot analysis monitoring with
                monitoring_interval for Features under it. Feature-level
                config: disabled = true indicates disabled regardless of the
                EntityType-level config; unset monitoring_interval indicates
                going with EntityType-level config; otherwise run snapshot
                analysis monitoring with monitoring_interval regardless of
                the EntityType-level config. Explicitly Disable the snapshot
                analysis based monitoring.
            monitoring_interval (google.protobuf.duration_pb2.Duration):
                Configuration of the snapshot analysis based
                monitoring pipeline running interval. The value
                is rolled up to full day.
        """

        disabled = proto.Field(proto.BOOL, number=1,)
        monitoring_interval = proto.Field(
            proto.MESSAGE, number=2, message=duration_pb2.Duration,
        )

    snapshot_analysis = proto.Field(proto.MESSAGE, number=1, message=SnapshotAnalysis,)


__all__ = tuple(sorted(__protobuf__.manifest))
