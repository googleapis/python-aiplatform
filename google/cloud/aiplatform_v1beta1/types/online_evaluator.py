# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
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

from google.cloud.aiplatform_v1beta1.types import evaluation_service
import google.protobuf.timestamp_pb2 as timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "OnlineEvaluator",
    },
)


class OnlineEvaluator(proto.Message):
    r"""An OnlineEvaluator contains the configuration for an Online
    Evaluation.


    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        cloud_observability (google.cloud.aiplatform_v1beta1.types.OnlineEvaluator.CloudObservability):
            Data source for the OnlineEvaluator, based on
            GCP Observability stack (Cloud Trace & Cloud
            Logging).

            This field is a member of `oneof`_ ``data_source``.
        name (str):
            Identifier. The resource name of the
            OnlineEvaluator. Format:
            projects/{project}/locations/{location}/onlineEvaluators/{id}.
        agent_resource (str):
            Required. Immutable. The name of the agent that the
            OnlineEvaluator evaluates periodically. This value is used
            to filter the traces with a matching cloud.resource_id and
            link the evaluation results with relevant dashboards/UIs.

            This field is immutable. Once set, it cannot be changed.
        metric_sources (MutableSequence[google.cloud.aiplatform_v1beta1.types.MetricSource]):
            Required. A list of metric sources to be used for evaluating
            samples. At least one MetricSource must be provided. Right
            now, only predefined metrics and registered metrics are
            supported.

            Every registered metric must have ``display_name`` (or
            ``title``) and ``score_range`` defined. Otherwise, the
            evaluations will fail.

            The maximum number of ``metric_sources`` is 25.
        config (google.cloud.aiplatform_v1beta1.types.OnlineEvaluator.Config):
            Required. Configuration for the
            OnlineEvaluator.
        state (google.cloud.aiplatform_v1beta1.types.OnlineEvaluator.State):
            Output only. The state of the
            OnlineEvaluator.
        state_details (MutableSequence[google.cloud.aiplatform_v1beta1.types.OnlineEvaluator.StateDetails]):
            Output only. Contains additional information
            about the state of the OnlineEvaluator. This is
            used to provide more details in the event of a
            failure.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when the
            OnlineEvaluator was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when the
            OnlineEvaluator was last updated.
        display_name (str):
            Optional. Human-readable name for the ``OnlineEvaluator``.

            The name doesn't have to be unique.

            The name can consist of any UTF-8 characters. The maximum
            length is ``63`` characters. If the display name exceeds max
            characters, an ``INVALID_ARGUMENT`` error is returned.
    """

    class State(proto.Enum):
        r"""The state of the OnlineEvaluator.

        Values:
            STATE_UNSPECIFIED (0):
                Default value.
            ACTIVE (1):
                Indicates that the OnlineEvaluator is active.
            SUSPENDED (2):
                Indicates that the OnlineEvaluator is
                suspended. In this state, the OnlineEvaluator
                will not evaluate any samples.
            FAILED (3):
                Indicates that the OnlineEvaluator is in a failed state.

                This can happen if, for example, the ``log_view`` or
                ``trace_view`` set on the ``CloudObservability`` does not
                exist.
            WARNING (4):
                Indicates that the OnlineEvaluator is in a warning state.
                This can happen if, for example, some of the metrics in the
                ``metric_sources`` are invalid. Evaluation will still run
                with the remaining valid metrics.
        """

        STATE_UNSPECIFIED = 0
        ACTIVE = 1
        SUSPENDED = 2
        FAILED = 3
        WARNING = 4

    class CloudObservability(proto.Message):
        r"""Data source for the OnlineEvaluator, based on GCP
        Observability stack (Cloud Trace & Cloud Logging).


        .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

        Attributes:
            trace_scope (google.cloud.aiplatform_v1beta1.types.OnlineEvaluator.CloudObservability.TraceScope):
                Scope online evaluation to single traces.

                This field is a member of `oneof`_ ``eval_scope``.
            open_telemetry (google.cloud.aiplatform_v1beta1.types.OnlineEvaluator.CloudObservability.OpenTelemetry):
                Data source follows OpenTelemetry convention.

                This field is a member of `oneof`_ ``convention``.
            log_view (str):
                Optional. Optional log view that will be used to query logs.
                If empty, the ``_Default`` view will be used.
            trace_view (str):
                Optional. Optional trace view that will be used to query
                traces. If empty, the ``_Default`` view will be used.

                NOTE: This field is not supported yet and will be ignored if
                set.
        """

        class NumericPredicate(proto.Message):
            r"""Defines a predicate for filtering based on a numeric value.

            Attributes:
                comparison_operator (google.cloud.aiplatform_v1beta1.types.OnlineEvaluator.CloudObservability.NumericPredicate.ComparisonOperator):
                    Required. The comparison operator to apply.
                value (float):
                    Required. The value to compare against.
            """

            class ComparisonOperator(proto.Enum):
                r"""Comparison operators for numeric predicates.

                Values:
                    COMPARISON_OPERATOR_UNSPECIFIED (0):
                        Unspecified comparison operator. This value
                        should not be used.
                    LESS (1):
                        Less than.
                    LESS_OR_EQUAL (2):
                        Less than or equal to.
                    EQUAL (3):
                        Equal to.
                    NOT_EQUAL (4):
                        Not equal to.
                    GREATER_OR_EQUAL (5):
                        Greater than or equal to.
                    GREATER (6):
                        Greater than.
                """

                COMPARISON_OPERATOR_UNSPECIFIED = 0
                LESS = 1
                LESS_OR_EQUAL = 2
                EQUAL = 3
                NOT_EQUAL = 4
                GREATER_OR_EQUAL = 5
                GREATER = 6

            comparison_operator: (
                "OnlineEvaluator.CloudObservability.NumericPredicate.ComparisonOperator"
            ) = proto.Field(
                proto.ENUM,
                number=1,
                enum="OnlineEvaluator.CloudObservability.NumericPredicate.ComparisonOperator",
            )
            value: float = proto.Field(
                proto.FLOAT,
                number=2,
            )

        class TraceScope(proto.Message):
            r"""If chosen, the online evaluator will evaluate single traces matching
            specified ``filter``.

            Attributes:
                filter (MutableSequence[google.cloud.aiplatform_v1beta1.types.OnlineEvaluator.CloudObservability.TraceScope.Predicate]):
                    Optional. A list of predicates to filter
                    traces. Multiple predicates are combined using
                    AND.

                    The maximum number of predicates is 10.
            """

            class Predicate(proto.Message):
                r"""Defines a single filter predicate.

                This message has `oneof`_ fields (mutually exclusive fields).
                For each oneof, at most one member field can be set at the same time.
                Setting any member of the oneof automatically clears all other
                members.

                .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

                Attributes:
                    duration (google.cloud.aiplatform_v1beta1.types.OnlineEvaluator.CloudObservability.NumericPredicate):
                        Filter on the duration of a trace.

                        This field is a member of `oneof`_ ``predicate``.
                    total_token_usage (google.cloud.aiplatform_v1beta1.types.OnlineEvaluator.CloudObservability.NumericPredicate):
                        Filter on the total token usage within a
                        trace.

                        This field is a member of `oneof`_ ``predicate``.
                """

                duration: "OnlineEvaluator.CloudObservability.NumericPredicate" = (
                    proto.Field(
                        proto.MESSAGE,
                        number=1,
                        oneof="predicate",
                        message="OnlineEvaluator.CloudObservability.NumericPredicate",
                    )
                )
                total_token_usage: (
                    "OnlineEvaluator.CloudObservability.NumericPredicate"
                ) = proto.Field(
                    proto.MESSAGE,
                    number=2,
                    oneof="predicate",
                    message="OnlineEvaluator.CloudObservability.NumericPredicate",
                )

            filter: MutableSequence[
                "OnlineEvaluator.CloudObservability.TraceScope.Predicate"
            ] = proto.RepeatedField(
                proto.MESSAGE,
                number=1,
                message="OnlineEvaluator.CloudObservability.TraceScope.Predicate",
            )

        class OpenTelemetry(proto.Message):
            r"""Configuration for data source following OpenTelemetry.

            Attributes:
                semconv_version (str):
                    Required. Defines which version OTel Semantic
                    Convention the data follows. Can be "1.39.0" or
                    newer.
            """

            semconv_version: str = proto.Field(
                proto.STRING,
                number=1,
            )

        trace_scope: "OnlineEvaluator.CloudObservability.TraceScope" = proto.Field(
            proto.MESSAGE,
            number=3,
            oneof="eval_scope",
            message="OnlineEvaluator.CloudObservability.TraceScope",
        )
        open_telemetry: "OnlineEvaluator.CloudObservability.OpenTelemetry" = (
            proto.Field(
                proto.MESSAGE,
                number=4,
                oneof="convention",
                message="OnlineEvaluator.CloudObservability.OpenTelemetry",
            )
        )
        log_view: str = proto.Field(
            proto.STRING,
            number=1,
        )
        trace_view: str = proto.Field(
            proto.STRING,
            number=2,
        )

    class Config(proto.Message):
        r"""Configuration for sampling behavior of the OnlineEvaluator.
        The OnlineEvaluator runs at a fixed interval of 10 minutes.


        .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

        Attributes:
            random_sampling (google.cloud.aiplatform_v1beta1.types.OnlineEvaluator.Config.RandomSampling):
                Random sampling method.

                This field is a member of `oneof`_ ``sampling_method``.
            max_evaluated_samples_per_run (int):
                Optional. The maximum number of evaluations
                to perform per run. If set to 0, the number is
                unbounded.
        """

        class RandomSampling(proto.Message):
            r"""Configuration for random sampling.

            Attributes:
                percentage (int):
                    Required. The percentage of traces to sample for evaluation.
                    Must be an integer between ``1`` and ``100``.
            """

            percentage: int = proto.Field(
                proto.INT32,
                number=1,
            )

        random_sampling: "OnlineEvaluator.Config.RandomSampling" = proto.Field(
            proto.MESSAGE,
            number=2,
            oneof="sampling_method",
            message="OnlineEvaluator.Config.RandomSampling",
        )
        max_evaluated_samples_per_run: int = proto.Field(
            proto.INT64,
            number=1,
        )

    class StateDetails(proto.Message):
        r"""Contains additional information about the state of the
        OnlineEvaluator.

        Attributes:
            message (str):
                Output only. Human-readable message
                describing the state of the OnlineEvaluator.
        """

        message: str = proto.Field(
            proto.STRING,
            number=1,
        )

    cloud_observability: CloudObservability = proto.Field(
        proto.MESSAGE,
        number=4,
        oneof="data_source",
        message=CloudObservability,
    )
    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    agent_resource: str = proto.Field(
        proto.STRING,
        number=2,
    )
    metric_sources: MutableSequence[evaluation_service.MetricSource] = (
        proto.RepeatedField(
            proto.MESSAGE,
            number=3,
            message=evaluation_service.MetricSource,
        )
    )
    config: Config = proto.Field(
        proto.MESSAGE,
        number=5,
        message=Config,
    )
    state: State = proto.Field(
        proto.ENUM,
        number=6,
        enum=State,
    )
    state_details: MutableSequence[StateDetails] = proto.RepeatedField(
        proto.MESSAGE,
        number=10,
        message=StateDetails,
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=7,
        message=timestamp_pb2.Timestamp,
    )
    update_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=8,
        message=timestamp_pb2.Timestamp,
    )
    display_name: str = proto.Field(
        proto.STRING,
        number=9,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
