# -*- coding: utf-8 -*-
# Copyright 2026 Google LLC
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

from google.cloud.aiplatform_v1.types import encryption_spec as gca_encryption_spec
from google.cloud.aiplatform_v1.types import operation
import google.protobuf.timestamp_pb2 as timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package='google.cloud.aiplatform.v1',
    manifest={
        'AnalyzedSessionView',
        'Severity',
        'AgentAnomalyDetectionScope',
        'MonitoredAgent',
        'AgentResource',
        'CreateAgentAnomalyDetectionScopeRequest',
        'CreateAgentAnomalyDetectionScopeOperationMetadata',
        'GetAgentAnomalyDetectionScopeRequest',
        'DeleteAgentAnomalyDetectionScopeRequest',
        'DeleteAgentAnomalyDetectionScopeOperationMetadata',
        'ListAgentAnomalyDetectionScopesRequest',
        'ListAgentAnomalyDetectionScopesResponse',
        'GetMonitoredAgentRequest',
        'ListMonitoredAgentsRequest',
        'ListMonitoredAgentsResponse',
        'EnableMonitoredAgentRequest',
        'EnableMonitoredAgentOperationMetadata',
        'DisableMonitoredAgentRequest',
        'DisableMonitoredAgentOperationMetadata',
        'ClearTrainingDataRequest',
        'ClearTrainingDataResponse',
        'ClearTrainingDataOperationMetadata',
        'Assessment',
        'AnalyzedSession',
        'ListAnalyzedSessionsRequest',
        'ListAnalyzedSessionsResponse',
        'GetAnalyzedSessionRequest',
        'AnalyzedInvocation',
        'GetAnalyzedInvocationRequest',
        'ListAnalyzedInvocationsRequest',
        'ListAnalyzedInvocationsResponse',
        'AggregateAnalyzedSessionsRequest',
        'AggregateAnalyzedSessionsResponse',
    },
)


class AnalyzedSessionView(proto.Enum):
    r"""The view options for AnalyzedSession.

    Values:
        ANALYZED_SESSION_VIEW_UNSPECIFIED (0):
            The default view: BASIC.
        ANALYZED_SESSION_VIEW_BASIC (1):
            Includes every ``AnalyzedSession`` field except
            ``assessment``.
        ANALYZED_SESSION_VIEW_FULL (2):
            Includes all fields, including the detailed ``assessment``.
            [AgentAnomalyDetectionService.ListAnalyzedSessions][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ListAnalyzedSessions]
            omits ``assessment`` in every view. To get it, call
            [AgentAnomalyDetectionService.GetAnalyzedSession][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.GetAnalyzedSession]
            with this view.
    """
    ANALYZED_SESSION_VIEW_UNSPECIFIED = 0
    ANALYZED_SESSION_VIEW_BASIC = 1
    ANALYZED_SESSION_VIEW_FULL = 2


class Severity(proto.Enum):
    r"""Severity levels available for Agent Anomaly Detection findings.
    Numeric values are ordered ascending by severity, so comparisons
    such as ``severity >= SEVERITY_HIGH`` behave as expected. Additional
    values may be added in the future.

    Values:
        SEVERITY_UNSPECIFIED (0):
            Unspecified severity.
        SEVERITY_LOW (1):
            Low severity.
        SEVERITY_MEDIUM (2):
            Medium severity.
        SEVERITY_HIGH (3):
            High severity.
        SEVERITY_CRITICAL (4):
            Critical severity.
    """
    SEVERITY_UNSPECIFIED = 0
    SEVERITY_LOW = 1
    SEVERITY_MEDIUM = 2
    SEVERITY_HIGH = 3
    SEVERITY_CRITICAL = 4


class AgentAnomalyDetectionScope(proto.Message):
    r"""Represents an Agent Anomaly Detection Scope.

    Attributes:
        name (str):
            Identifier. The resource name of the
            AgentAnomalyDetectionScope. Format:
            ``projects/{project}/locations/{location}/agentAnomalyDetectionScopes/{agent_anomaly_detection_scope}``
        display_name (str):
            Optional. User-provided display name of the
            AgentAnomalyDetectionScope.
        log_buckets (MutableSequence[str]):
            Required. Customer-owned Cloud Logging bucket resource names
            attached to this scope. Specify exactly one bucket, in the
            same project as this scope. Format:
            ``projects/{project}/locations/{location}/buckets/{bucket}``.
        observability_buckets (MutableSequence[str]):
            Required. Customer-owned Cloud Observability datasets
            attached to this scope. Each value is the resource name of a
            dataset in an Observability bucket, such as the ``Spans``
            dataset in the ``_Trace`` bucket. Specify exactly one
            dataset, in the same project as this scope. Format:
            ``projects/{project}/locations/{location}/buckets/{bucket}/datasets/{dataset}``.
        auto_enroll (bool):
            Optional. When ``true``, newly discovered agents that share
            log and observability buckets with this scope are
            automatically enrolled as ``ACTIVE`` MonitoredAgents, up to
            the project's monitored agent quota. When ``false``, newly
            discovered agents are added as ``DISABLED`` MonitoredAgents,
            and you must enable them explicitly through MonitoredAgent
            operations.
        state (google.cloud.aiplatform_v1.types.AgentAnomalyDetectionScope.State):
            Output only. The lifecycle state of the
            scope.
        encryption_spec (google.cloud.aiplatform_v1.types.EncryptionSpec):
            Optional. Immutable. Specifies the customer-managed
            encryption key spec for a Scope. If set, this Scope and all
            sub-resources will be secured by this key.

            The key is immutable after the Scope is created and must be
            a multi-region (``us`` or ``eu``) key in the same region as
            the Scope.
    """
    class State(proto.Enum):
        r"""The lifecycle state of an AgentAnomalyDetectionScope.

        Values:
            STATE_UNSPECIFIED (0):
                The default value. This value is unused.
            CREATING (1):
                The scope is being created and is not yet
                usable.
            ACTIVE (2):
                The scope is active and usable.
            DELETING (3):
                The scope is being deleted.
            FAILED (4):
                Creation or deletion failed. The scope is not
                usable and must be deleted before a new scope
                can be created in the same region.
            UPDATING (5):
                The scope is being updated.
        """
        STATE_UNSPECIFIED = 0
        CREATING = 1
        ACTIVE = 2
        DELETING = 3
        FAILED = 4
        UPDATING = 5

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    display_name: str = proto.Field(
        proto.STRING,
        number=2,
    )
    log_buckets: MutableSequence[str] = proto.RepeatedField(
        proto.STRING,
        number=5,
    )
    observability_buckets: MutableSequence[str] = proto.RepeatedField(
        proto.STRING,
        number=6,
    )
    auto_enroll: bool = proto.Field(
        proto.BOOL,
        number=7,
    )
    state: State = proto.Field(
        proto.ENUM,
        number=8,
        enum=State,
    )
    encryption_spec: gca_encryption_spec.EncryptionSpec = proto.Field(
        proto.MESSAGE,
        number=9,
        message=gca_encryption_spec.EncryptionSpec,
    )


class MonitoredAgent(proto.Message):
    r"""Represents a monitored agent in a specific Location.

    Attributes:
        name (str):
            Identifier. The resource name of the
            MonitoredAgent.
        display_name (str):
            Optional. The display name of the
            MonitoredAgent.
        agent_resource (google.cloud.aiplatform_v1.types.AgentResource):
            Required. The configuration for the agent
            being monitored.
        state (google.cloud.aiplatform_v1.types.MonitoredAgent.EnablementState):
            Output only. The current state of the agent's
            enablement.
        status_message (str):
            Output only. A brief message explaining the
            current state.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. The time the MonitoredAgent was
            created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. The time the MonitoredAgent was
            last updated.
    """
    class EnablementState(proto.Enum):
        r"""Represents the detailed status of the MonitoredAgent.

        Values:
            ENABLEMENT_STATE_UNSPECIFIED (0):
                The default value. This value is used if the
                state is omitted.
            ACTIVE (1):
                The agent is successfully enabled and active.
            ENABLING (3):
                The agent is in the process of being enabled.
            DISABLED (6):
                The agent is disabled.
        """
        ENABLEMENT_STATE_UNSPECIFIED = 0
        ACTIVE = 1
        ENABLING = 3
        DISABLED = 6

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    display_name: str = proto.Field(
        proto.STRING,
        number=2,
    )
    agent_resource: 'AgentResource' = proto.Field(
        proto.MESSAGE,
        number=3,
        message='AgentResource',
    )
    state: EnablementState = proto.Field(
        proto.ENUM,
        number=4,
        enum=EnablementState,
    )
    status_message: str = proto.Field(
        proto.STRING,
        number=5,
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=8,
        message=timestamp_pb2.Timestamp,
    )
    update_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=9,
        message=timestamp_pb2.Timestamp,
    )


class AgentResource(proto.Message):
    r"""Defines the identity of an agent being monitored.

    Attributes:
        agent_type (google.cloud.aiplatform_v1.types.AgentResource.AgentType):
            Required. The runtime type of the agent.
        agent (str):
            Required. The resource name or identifier of the agent to
            monitor. The format depends on ``agent_type``:

            - ``REASONING_ENGINE``:
              ``//aiplatform.googleapis.com/projects/{project}/locations/{location}/reasoningEngines/{reasoning_engine}``
            - ``CLOUD_RUN_SERVICE``: the full resource name of the Cloud
              Run service,
              ``//run.googleapis.com/projects/{project}/locations/{location}/services/{service}``
            - ``GKE_WORKLOAD``: the full resource name of the Google
              Kubernetes Engine cluster followed by the agent's
              OpenTelemetry ``service.name``,
              ``//container.googleapis.com/projects/{project}/locations/{location}/clusters/{cluster}/{service}``.
              For a zonal cluster, ``zones/{zone}`` replaces
              ``locations/{location}``. Some names end in
              ``k8s/namespaces/{namespace}/apps/deployments/{deployment}``
              instead of ``{service}``.
            - ``GCE_INSTANCE``: the full resource name of the Compute
              Engine instance followed by the agent's OpenTelemetry
              ``service.name``,
              ``//compute.googleapis.com/projects/{project}/zones/{zone}/instances/{instance}/{service}``,
              where ``{instance}`` is the numeric instance ID.
            - ``AWS`` and ``AZURE``: an identifier built from the
              agent's OpenTelemetry resource attributes, usually
              ``{platform}:{account}:{region}:{name}``. ``{platform}``
              is the ``cloud.platform`` value. ``{account}`` is
              ``cloud.account.id``, or the ID of the Google Cloud
              project that receives the telemetry if
              ``cloud.account.id`` isn't set. ``{region}`` is
              ``cloud.region``. ``{name}`` is ``faas.name``, or the
              Kubernetes cluster name followed by
              ``/k8s/namespaces/{namespace}/apps/deployments/{deployment}``
              or ``/{service}``. For example,
              ``aws_lambda:123456789012:us-east-2:inventory-agent``.
            - ``AGENT_TYPE_OTHER``: a stable identifier for the agent,
              such as the full resource name of its runtime or its
              OpenTelemetry ``service.name``.
        location (str):
            Output only. The region of the agent resource: a Google
            Cloud location (for example, ``us-central1``), or for an
            ``AWS`` or ``AZURE`` agent, the region in that cloud (for
            example, ``us-east-2``).
        agent_framework (google.cloud.aiplatform_v1.types.AgentResource.AgentFramework):
            Optional. The framework used to build the agent, orthogonal
            to the runtime ``agent_type``.
    """
    class AgentType(proto.Enum):
        r"""The runtime type of an agent, describing where the agent is hosted.
        This is orthogonal to the framework the agent is built with; see
        ``AgentFramework``.

        Values:
            AGENT_TYPE_UNSPECIFIED (0):
                The default value, used when the runtime type
                is unspecified.
            REASONING_ENGINE (1):
                The agent runs on the Gemini Enterprise Agent
                Platform Agent Runtime (Reasoning Engine).
            CLOUD_RUN_SERVICE (2):
                The agent runs as a Google Cloud Run service.
            GKE_WORKLOAD (3):
                The agent runs as a workload on Google
                Kubernetes Engine.
            GCE_INSTANCE (4):
                The agent runs on a Compute Engine instance.
            AGENT_TYPE_OTHER (5):
                The agent runs on a runtime that no other
                value represents, such as a self-hosted or
                on-premises environment.
            AWS (8):
                The agent runs on Amazon Web Services (AWS),
                such as on AWS Lambda.
            AZURE (9):
                The agent runs on Microsoft Azure, such as on
                Azure Kubernetes Service (AKS) or as a Microsoft
                Foundry hosted agent.
        """
        AGENT_TYPE_UNSPECIFIED = 0
        REASONING_ENGINE = 1
        CLOUD_RUN_SERVICE = 2
        GKE_WORKLOAD = 3
        GCE_INSTANCE = 4
        AGENT_TYPE_OTHER = 5
        AWS = 8
        AZURE = 9

    class AgentFramework(proto.Enum):
        r"""The framework used to build an agent, such as the Agent Development
        Kit (ADK). This is orthogonal to the runtime the agent is hosted on;
        see ``AgentType``.

        Values:
            AGENT_FRAMEWORK_UNSPECIFIED (0):
                The default value, used when the framework is
                unspecified.
            ADK (1):
                The agent is built with the Agent Development
                Kit (ADK).
        """
        AGENT_FRAMEWORK_UNSPECIFIED = 0
        ADK = 1

    agent_type: AgentType = proto.Field(
        proto.ENUM,
        number=1,
        enum=AgentType,
    )
    agent: str = proto.Field(
        proto.STRING,
        number=2,
    )
    location: str = proto.Field(
        proto.STRING,
        number=3,
    )
    agent_framework: AgentFramework = proto.Field(
        proto.ENUM,
        number=4,
        enum=AgentFramework,
    )


class CreateAgentAnomalyDetectionScopeRequest(proto.Message):
    r"""Request message for
    [AgentAnomalyDetectionService.CreateAgentAnomalyDetectionScope][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.CreateAgentAnomalyDetectionScope].

    Attributes:
        parent (str):
            Required. The resource name of the Location to create the
            AgentAnomalyDetectionScope in. Format:
            ``projects/{project}/locations/{location}``
        agent_anomaly_detection_scope (google.cloud.aiplatform_v1.types.AgentAnomalyDetectionScope):
            Required. The AgentAnomalyDetectionScope to
            create.
        agent_anomaly_detection_scope_id (str):
            Required. The ID to use for the AgentAnomalyDetectionScope,
            which will become the final component of the
            AgentAnomalyDetectionScope's resource name.

            This value should be 1-63 characters, and valid characters
            are /`a-z <[a-z0-9-]{0,61}[a-z0-9]>`__?/.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    agent_anomaly_detection_scope: 'AgentAnomalyDetectionScope' = proto.Field(
        proto.MESSAGE,
        number=2,
        message='AgentAnomalyDetectionScope',
    )
    agent_anomaly_detection_scope_id: str = proto.Field(
        proto.STRING,
        number=3,
    )


class CreateAgentAnomalyDetectionScopeOperationMetadata(proto.Message):
    r"""Metadata information for
    [AgentAnomalyDetectionService.CreateAgentAnomalyDetectionScope][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.CreateAgentAnomalyDetectionScope].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
        done_time (google.protobuf.timestamp_pb2.Timestamp):
            The time the operation was completed.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )
    done_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=2,
        message=timestamp_pb2.Timestamp,
    )


class GetAgentAnomalyDetectionScopeRequest(proto.Message):
    r"""Request message for
    [AgentAnomalyDetectionService.GetAgentAnomalyDetectionScope][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.GetAgentAnomalyDetectionScope].

    Attributes:
        name (str):
            Required. The name of the AgentAnomalyDetectionScope
            resource. Format:
            ``projects/{project}/locations/{location}/agentAnomalyDetectionScopes/{agent_anomaly_detection_scope}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class DeleteAgentAnomalyDetectionScopeRequest(proto.Message):
    r"""Request message for
    [AgentAnomalyDetectionService.DeleteAgentAnomalyDetectionScope][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.DeleteAgentAnomalyDetectionScope].

    Attributes:
        name (str):
            Required. The name of the AgentAnomalyDetectionScope
            resource to be deleted. Format:
            ``projects/{project}/locations/{location}/agentAnomalyDetectionScopes/{agent_anomaly_detection_scope}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class DeleteAgentAnomalyDetectionScopeOperationMetadata(proto.Message):
    r"""Metadata information for
    [AgentAnomalyDetectionService.DeleteAgentAnomalyDetectionScope][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.DeleteAgentAnomalyDetectionScope].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
        done_time (google.protobuf.timestamp_pb2.Timestamp):
            The time the operation was completed.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )
    done_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=2,
        message=timestamp_pb2.Timestamp,
    )


class ListAgentAnomalyDetectionScopesRequest(proto.Message):
    r"""Request message for
    [AgentAnomalyDetectionService.ListAgentAnomalyDetectionScopes][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ListAgentAnomalyDetectionScopes].

    Attributes:
        parent (str):
            Required. The resource name of the Location to list the
            AgentAnomalyDetectionScopes from. Format:
            ``projects/{project}/locations/{location}``
        page_size (int):
            Optional. The standard list page size. The
            maximum value is 100; values above 100 will be
            coerced to 100. If unspecified, at most 10
            AgentAnomalyDetectionScopes will be returned.
        page_token (str):
            Optional. The standard list page token.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=2,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )


class ListAgentAnomalyDetectionScopesResponse(proto.Message):
    r"""Response message for
    [AgentAnomalyDetectionService.ListAgentAnomalyDetectionScopes][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ListAgentAnomalyDetectionScopes].

    Attributes:
        agent_anomaly_detection_scopes (MutableSequence[google.cloud.aiplatform_v1.types.AgentAnomalyDetectionScope]):
            A list of AgentAnomalyDetectionScopes that
            matches the specified filter in the request.
        next_page_token (str):
            A token, which can be sent as ``page_token`` to retrieve the
            next page. If this field is omitted, there are no subsequent
            pages.
    """

    @property
    def raw_page(self):
        return self

    agent_anomaly_detection_scopes: MutableSequence['AgentAnomalyDetectionScope'] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message='AgentAnomalyDetectionScope',
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class GetMonitoredAgentRequest(proto.Message):
    r"""Request message for
    [AgentAnomalyDetectionService.GetMonitoredAgent][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.GetMonitoredAgent].

    Attributes:
        name (str):
            Required. The name of the MonitoredAgent resource. Format:
            ``projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ListMonitoredAgentsRequest(proto.Message):
    r"""Request message for
    [AgentAnomalyDetectionService.ListMonitoredAgents][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ListMonitoredAgents].

    Attributes:
        parent (str):
            Required. The resource name of the Location to list the
            MonitoredAgents from. Format:
            ``projects/{project}/locations/{location}``
        page_size (int):
            Optional. The standard list page size. The
            maximum value is 100; values above 100 will be
            coerced to 100. If unspecified, at most 10
            MonitoredAgents will be returned.
        page_token (str):
            Optional. The standard list page token.
        filter (str):
            Optional. An AIP-160 filter, currently restricted to a
            single equality predicate on ``state``. The value must be
            the exact, case-sensitive name of a
            ``MonitoredAgent.EnablementState`` value: ``ACTIVE``,
            ``DISABLED``, ``ENABLING``, or
            ``ENABLEMENT_STATE_UNSPECIFIED``. A blank or absent filter
            returns every MonitoredAgent in the parent regardless of
            state; any other value returns ``INVALID_ARGUMENT``.

            Example:

            ::

               state = ACTIVE
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=2,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )
    filter: str = proto.Field(
        proto.STRING,
        number=4,
    )


class ListMonitoredAgentsResponse(proto.Message):
    r"""Response message for
    [AgentAnomalyDetectionService.ListMonitoredAgents][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ListMonitoredAgents].

    Attributes:
        monitored_agents (MutableSequence[google.cloud.aiplatform_v1.types.MonitoredAgent]):
            A list of MonitoredAgents that matches the
            specified filter in the request.
        next_page_token (str):
            A token, which can be sent as ``page_token`` to retrieve the
            next page. If this field is omitted, there are no subsequent
            pages.
        total_size (int):
            The total number of MonitoredAgents matching the request,
            after any ``filter`` is applied.
    """

    @property
    def raw_page(self):
        return self

    monitored_agents: MutableSequence['MonitoredAgent'] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message='MonitoredAgent',
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )
    total_size: int = proto.Field(
        proto.INT32,
        number=3,
    )


class EnableMonitoredAgentRequest(proto.Message):
    r"""Request message for
    [AgentAnomalyDetectionService.EnableMonitoredAgent][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.EnableMonitoredAgent].

    Attributes:
        name (str):
            Required. The name of the MonitoredAgent resource to be
            enabled. Format:
            ``projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class EnableMonitoredAgentOperationMetadata(proto.Message):
    r"""Metadata information for
    [AgentAnomalyDetectionService.EnableMonitoredAgent][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.EnableMonitoredAgent].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class DisableMonitoredAgentRequest(proto.Message):
    r"""Request message for
    [AgentAnomalyDetectionService.DisableMonitoredAgent][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.DisableMonitoredAgent].

    Attributes:
        name (str):
            Required. The name of the MonitoredAgent resource to be
            disabled. Format:
            ``projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class DisableMonitoredAgentOperationMetadata(proto.Message):
    r"""Metadata information for
    [AgentAnomalyDetectionService.DisableMonitoredAgent][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.DisableMonitoredAgent].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class ClearTrainingDataRequest(proto.Message):
    r"""Request message for
    [AgentAnomalyDetectionService.ClearTrainingData][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ClearTrainingData].

    Attributes:
        name (str):
            Required. The MonitoredAgent whose trained model artifacts
            to purge. Use the ``-`` wildcard agent segment to purge
            every MonitoredAgent in the scope. Format:
            ``projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ClearTrainingDataResponse(proto.Message):
    r"""Response message for
    [AgentAnomalyDetectionService.ClearTrainingData][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ClearTrainingData].
    Intentionally empty; the purge either succeeds or the operation
    carries an error.

    """


class ClearTrainingDataOperationMetadata(proto.Message):
    r"""Metadata information for
    [AgentAnomalyDetectionService.ClearTrainingData][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ClearTrainingData].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
        done_time (google.protobuf.timestamp_pb2.Timestamp):
            The time the operation was completed.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )
    done_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=2,
        message=timestamp_pb2.Timestamp,
    )


class Assessment(proto.Message):
    r"""Contains the detailed assessment for an analyzed session.

    Attributes:
        detector_findings (MutableSequence[google.cloud.aiplatform_v1.types.Assessment.DetectorFinding]):
            The list of detector findings.
    """

    class DetectorFinding(proto.Message):
        r"""The details of a detector's assessment within an analyzed
        session.

        Attributes:
            detector_id (str):
                The detector ID.
            display_name (str):
                The detector display name.
            severity (google.cloud.aiplatform_v1.types.Severity):
                The severity of the finding.
            explanation (str):
                The explanation of the finding.
            probability (float):
                The probability that this finding is an anomaly, in the
                range [0.0, 1.0].
            recommendations (MutableSequence[str]):
                The list of recommendations for this detector
                finding.
        """

        detector_id: str = proto.Field(
            proto.STRING,
            number=1,
        )
        display_name: str = proto.Field(
            proto.STRING,
            number=2,
        )
        severity: 'Severity' = proto.Field(
            proto.ENUM,
            number=3,
            enum='Severity',
        )
        explanation: str = proto.Field(
            proto.STRING,
            number=4,
        )
        probability: float = proto.Field(
            proto.DOUBLE,
            number=5,
        )
        recommendations: MutableSequence[str] = proto.RepeatedField(
            proto.STRING,
            number=6,
        )

    detector_findings: MutableSequence[DetectorFinding] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=DetectorFinding,
    )


class AnalyzedSession(proto.Message):
    r"""Represents an analyzed session for a monitored agent.

    Attributes:
        name (str):
            Identifier. The resource name of the
            AnalyzedSession.
        session_id (str):
            Output only. The session ID.
        user_id (str):
            Output only. The user ID.
        agent_resource_name (str):
            Output only. The resource name or identifier of the agent
            that ran this session. Matches ``AgentResource.agent`` on
            the corresponding ``MonitoredAgent``, so the format depends
            on that agent's ``AgentResource.agent_type``. For the format
            of each agent type, see
            [AgentResource.agent][google.cloud.aiplatform.v1.AgentResource.agent].
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. The creation time of the
            session.
        latest_analyzed_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. The latest analyzed time of the
            session.
        assessment (google.cloud.aiplatform_v1.types.Assessment):
            Output only. Overall security assessment.
            Populated only in FULL view.
        severities (MutableMapping[str, google.cloud.aiplatform_v1.types.AnalyzedSession.SeveritySummary]):
            Output only. Map of the detectors that flagged this session,
            grouped by severity. The key is the string representation of
            ``Severity``. Populated only for flagged sessions, in both
            views. In
            [AgentAnomalyDetectionService.ListAnalyzedSessions][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ListAnalyzedSessions]
            responses, the map holds only the session's highest
            severity.
        session_state (google.cloud.aiplatform_v1.types.AnalyzedSession.SessionState):
            Output only. The state of the session.
        agent_display_name (str):
            Output only. The human-readable display name of the
            MonitoredAgent that owns this session. May be empty when the
            session's agent is not enrolled as a MonitoredAgent; the
            ``agent_resource_name`` is always present and can be used as
            a fallback identifier.
        agent_state (google.cloud.aiplatform_v1.types.MonitoredAgent.EnablementState):
            Output only. The current enablement state of the
            MonitoredAgent that owns this session (for example, ACTIVE,
            DISABLED, or ENABLING). Defaults to
            ENABLEMENT_STATE_UNSPECIFIED when the agent is not enrolled
            or its state is unknown.
        location (str):
            Output only. The region of the agent that ran this session,
            in the same form as ``AgentResource.location`` (for example,
            ``us-central1``). Empty when the agent is not enrolled or
            its location is unknown.
        agent_type (google.cloud.aiplatform_v1.types.AgentResource.AgentType):
            Output only. The runtime that the agent which ran this
            session is hosted on (for example, ``CLOUD_RUN_SERVICE``).

            ``AGENT_TYPE_UNSPECIFIED`` means the runtime is unknown to
            this service -- the agent is not enrolled as a
            ``MonitoredAgent``, or was enrolled before its runtime was
            recorded. That is distinct from ``AGENT_TYPE_OTHER``, which
            means the runtime is known and is not one of the other
            enumerated runtimes.
    """
    class SessionState(proto.Enum):
        r"""The analysis state of a session.

        Values:
            SESSION_STATE_UNSPECIFIED (0):
                The session state is unspecified.
            SESSION_STATE_UNANALYZED (1):
                The session has not yet been analyzed.
            SESSION_STATE_NOT_FLAGGED (2):
                The session has been analyzed and no
                anomalies were flagged.
            SESSION_STATE_FLAGGED (3):
                The session has been analyzed and at least
                one anomaly was flagged.
            SESSION_STATE_LLM_UNFLAGGED (4):
                The session was analyzed by the LLM judge,
                which did not flag any anomalies.
        """
        SESSION_STATE_UNSPECIFIED = 0
        SESSION_STATE_UNANALYZED = 1
        SESSION_STATE_NOT_FLAGGED = 2
        SESSION_STATE_FLAGGED = 3
        SESSION_STATE_LLM_UNFLAGGED = 4

    class SeveritySummary(proto.Message):
        r"""Breaks down anomalies by severity.

        Attributes:
            detector_ids (MutableSequence[str]):
                The list of detectors summaries for this
                severity level.
            severity_level (google.cloud.aiplatform_v1.types.Severity):
                The severity level of the detector.
            sessions_count (int):
                Output only. The number of distinct sessions whose maximum
                severity equals ``severity_level``. Each session is counted
                in exactly one bucket (its highest severity).

                Scope depends on where this appears: a global count on
                ``AggregateAnalyzedSessionsResponse.summary``, per-agent on
                ``agent_aggregates`` entries, and page-scoped on
                ``ListAnalyzedSessionsResponse``.
        """

        detector_ids: MutableSequence[str] = proto.RepeatedField(
            proto.STRING,
            number=1,
        )
        severity_level: 'Severity' = proto.Field(
            proto.ENUM,
            number=2,
            enum='Severity',
        )
        sessions_count: int = proto.Field(
            proto.INT32,
            number=3,
        )

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    session_id: str = proto.Field(
        proto.STRING,
        number=2,
    )
    user_id: str = proto.Field(
        proto.STRING,
        number=3,
    )
    agent_resource_name: str = proto.Field(
        proto.STRING,
        number=4,
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=5,
        message=timestamp_pb2.Timestamp,
    )
    latest_analyzed_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=6,
        message=timestamp_pb2.Timestamp,
    )
    assessment: 'Assessment' = proto.Field(
        proto.MESSAGE,
        number=7,
        message='Assessment',
    )
    severities: MutableMapping[str, SeveritySummary] = proto.MapField(
        proto.STRING,
        proto.MESSAGE,
        number=8,
        message=SeveritySummary,
    )
    session_state: SessionState = proto.Field(
        proto.ENUM,
        number=9,
        enum=SessionState,
    )
    agent_display_name: str = proto.Field(
        proto.STRING,
        number=10,
    )
    agent_state: 'MonitoredAgent.EnablementState' = proto.Field(
        proto.ENUM,
        number=11,
        enum='MonitoredAgent.EnablementState',
    )
    location: str = proto.Field(
        proto.STRING,
        number=12,
    )
    agent_type: 'AgentResource.AgentType' = proto.Field(
        proto.ENUM,
        number=13,
        enum='AgentResource.AgentType',
    )


class ListAnalyzedSessionsRequest(proto.Message):
    r"""Request to list analyzed sessions.

    Attributes:
        parent (str):
            Required. The parent MonitoredAgent resource. Format:
            ``projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}``
        page_size (int):
            Optional. The maximum number of analyzed
            sessions to return.
        page_token (str):
            Optional. A page token, received from a previous
            ``ListAnalyzedSessions`` call.
        filter (str):
            Optional. Filter expression restricting which
            AnalyzedSessions are returned. Supports a subset of AIP-160:
            a closed ``detection_time`` window (both bounds required),
            an equality on ``severity``, an equality on ``agent_type``,
            and an equality on ``session_id``, joined by ``AND``. Each
            clause is optional, may appear at most once, and may appear
            in any order.

            The ``severity`` value is the **canonical** ``Severity``
            enum name -- ``SEVERITY_CRITICAL``, ``SEVERITY_HIGH``,
            ``SEVERITY_MEDIUM`` or ``SEVERITY_LOW``. Short forms such as
            ``"CRITICAL"`` are rejected, as is ``SEVERITY_UNSPECIFIED``.
            It matches sessions whose *maximum* severity equals that
            bucket: a session that fires at both LOW and CRITICAL
            matches ``severity = "SEVERITY_CRITICAL"``, not
            ``severity = "SEVERITY_LOW"``.

            The ``agent_type`` value is the canonical
            ``AgentResource.AgentType`` enum name --
            ``REASONING_ENGINE``, ``CLOUD_RUN_SERVICE``,
            ``GKE_WORKLOAD``, ``GCE_INSTANCE``, ``AWS``, ``AZURE``,
            ``AGENT_TYPE_OTHER`` or ``AGENT_TYPE_UNSPECIFIED`` -- and
            matches sessions run by an agent on that runtime.

            Unlike ``severity``, ``agent_type`` accepts its
            ``UNSPECIFIED`` value. The two are not analogous: a session
            always has a computed severity bucket, so
            ``SEVERITY_UNSPECIFIED`` is never returned and filtering on
            it could only match nothing. ``AGENT_TYPE_UNSPECIFIED`` *is*
            returned -- it is what ``AnalyzedSession.agent_type``
            reports for an agent whose runtime was never recorded -- so
            it must remain filterable.

            The ``session_id`` value is a case-sensitive exact match (no
            substring or prefix matching) on
            ``AnalyzedSession.session_id``. Unlike ``severity`` and
            ``agent_type`` it is not a closed enum, so any non-empty
            value is accepted; an empty value (``session_id = ""``) is
            rejected rather than treated as "no filter".

            Example (time window, severity and runtime):

            ::

               detection_time >= "2024-01-01T00:00:00Z" AND detection_time <=
               "2024-01-08T00:00:00Z" AND severity = "SEVERITY_CRITICAL" AND agent_type =
               "CLOUD_RUN_SERVICE"

            If empty, results are restricted to the last 7 days with no
            severity, runtime, or session restriction. Other fields,
            additional operators, set membership (``IN``), and boolean
            combinations (``OR``, ``NOT``, parentheses) are not yet
            supported.
        view (google.cloud.aiplatform_v1.types.AnalyzedSessionView):
            Optional. Resource view to control which
            fields are returned.
        order_by (str):
            Optional. Comma-separated list of fields to sort by,
            following AIP-132 syntax. The default sort direction is
            ascending; append " desc" to a field to sort descending.

            Supported fields (any other field yields INVALID_ARGUMENT):

            - ``latest_detection_time`` - the session's most-recent
              flagged detection time. ``latest_detection_time desc``
              puts the newest sessions first.
            - ``max_severity_rank`` - the session's bucketed maximum
              severity, ranked LOW=1 < MEDIUM=2 < HIGH=3 < CRITICAL=4.
              ``max_severity_rank desc`` puts the most-severe sessions
              first.
            - ``agent_display_name`` - the MonitoredAgent's display
              name. Sorted as a STRING (case-sensitive, code-point
              order).

            If empty, defaults to ``latest_detection_time desc``.
            Multi-field sort (for example,
            ``max_severity_rank desc, latest_detection_time desc``) is
            supported.

            The ``order_by`` value MUST match the value used on the call
            that minted any supplied ``page_token`` (AIP-158).
            Mismatches yield INVALID_ARGUMENT.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=2,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )
    filter: str = proto.Field(
        proto.STRING,
        number=4,
    )
    view: 'AnalyzedSessionView' = proto.Field(
        proto.ENUM,
        number=5,
        enum='AnalyzedSessionView',
    )
    order_by: str = proto.Field(
        proto.STRING,
        number=6,
    )


class ListAnalyzedSessionsResponse(proto.Message):
    r"""Response to list analyzed sessions.

    Attributes:
        analyzed_sessions (MutableSequence[google.cloud.aiplatform_v1.types.AnalyzedSession]):
            The list of analyzed sessions.
        next_page_token (str):
            A token to retrieve the next page of results.
        summary (google.cloud.aiplatform_v1.types.ListAnalyzedSessionsResponse.ViewSummary):
            Summary statistics computed across the
            sessions on the current page only. For
            statistics across the entire result set, use
            AggregateAnalyzedSessions.
    """

    class ViewSummary(proto.Message):
        r"""The view summary.

        Attributes:
            severities (MutableMapping[str, google.cloud.aiplatform_v1.types.AnalyzedSession.SeveritySummary]):
                The list of severity summaries for the analyzed sessions.
                The key is the string representation of Severity enum:
                "SEVERITY_UNSPECIFIED", "SEVERITY_CRITICAL",
                "SEVERITY_HIGH", "SEVERITY_MEDIUM", "SEVERITY_LOW".
            anomalous_sessions_count (int):
                Number of anomalous sessions.
            total_sessions_count (int):
                Total number of sessions.
            anomalous_agents_count (int):
                Output only. The number of distinct agents in the request
                scope with at least one anomalous session in the time
                window. On ``AggregateAnalyzedSessionsResponse.summary``
                this is a global count; it is not populated on
                ``ListAnalyzedSessionsResponse.summary``.
            llm_scanned_sessions_count (int):
                Output only. The number of distinct sessions
                in the time window that were scanned by the LLM
                judge.
        """

        severities: MutableMapping[str, 'AnalyzedSession.SeveritySummary'] = proto.MapField(
            proto.STRING,
            proto.MESSAGE,
            number=1,
            message='AnalyzedSession.SeveritySummary',
        )
        anomalous_sessions_count: int = proto.Field(
            proto.INT32,
            number=2,
        )
        total_sessions_count: int = proto.Field(
            proto.INT32,
            number=3,
        )
        anomalous_agents_count: int = proto.Field(
            proto.INT32,
            number=4,
        )
        llm_scanned_sessions_count: int = proto.Field(
            proto.INT32,
            number=5,
        )

    @property
    def raw_page(self):
        return self

    analyzed_sessions: MutableSequence['AnalyzedSession'] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message='AnalyzedSession',
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )
    summary: ViewSummary = proto.Field(
        proto.MESSAGE,
        number=3,
        message=ViewSummary,
    )


class GetAnalyzedSessionRequest(proto.Message):
    r"""Request to get the details of a specific analyzed session.

    Attributes:
        name (str):
            Required. The name of the AnalyzedSession resource. Format:
            ``projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}/analyzedSessions/{analyzed_session}``
        view (google.cloud.aiplatform_v1.types.AnalyzedSessionView):
            Optional. Resource view to control which
            fields are returned.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    view: 'AnalyzedSessionView' = proto.Field(
        proto.ENUM,
        number=2,
        enum='AnalyzedSessionView',
    )


class AnalyzedInvocation(proto.Message):
    r"""Represents an analyzed invocation for a monitored agent's
    session.

    Attributes:
        name (str):
            Identifier. The resource name of the
            AnalyzedInvocation.
        invocation_id (str):
            Output only. The invocation ID.
        assessment (google.cloud.aiplatform_v1.types.Assessment):
            Output only. The assessment of the
            invocation.
        invocation_state (google.cloud.aiplatform_v1.types.AnalyzedInvocation.InvocationState):
            Output only. The state of the invocation.
    """
    class InvocationState(proto.Enum):
        r"""State of the invocation.

        Values:
            INVOCATION_STATE_UNSPECIFIED (0):
                Unspecified state.
            INVOCATION_STATE_ANOMALOUS (1):
                The invocation is anomalous.
            INVOCATION_STATE_NOT_ANOMALOUS (2):
                The invocation is not anomalous.
        """
        INVOCATION_STATE_UNSPECIFIED = 0
        INVOCATION_STATE_ANOMALOUS = 1
        INVOCATION_STATE_NOT_ANOMALOUS = 2

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    invocation_id: str = proto.Field(
        proto.STRING,
        number=2,
    )
    assessment: 'Assessment' = proto.Field(
        proto.MESSAGE,
        number=3,
        message='Assessment',
    )
    invocation_state: InvocationState = proto.Field(
        proto.ENUM,
        number=4,
        enum=InvocationState,
    )


class GetAnalyzedInvocationRequest(proto.Message):
    r"""Request to get the details of a specific analyzed invocation.

    Attributes:
        name (str):
            Required. The name of the AnalyzedInvocation resource.
            Format:
            ``projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}/analyzedSessions/{analyzed_session}/analyzedInvocations/{analyzed_invocation}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ListAnalyzedInvocationsRequest(proto.Message):
    r"""Request to list analyzed invocations.

    Attributes:
        parent (str):
            Required. The parent AnalyzedSession resource. Format:
            ``projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}/analyzedSessions/{analyzed_session}``
        page_size (int):
            Optional. The maximum number of analyzed
            invocations to return.
        page_token (str):
            Optional. A page token, received from a previous
            ``ListAnalyzedInvocations`` call.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=2,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )


class ListAnalyzedInvocationsResponse(proto.Message):
    r"""Response to list analyzed invocations.

    Attributes:
        analyzed_invocations (MutableSequence[google.cloud.aiplatform_v1.types.AnalyzedInvocation]):
            The list of analyzed invocations.
        next_page_token (str):
            A token to retrieve the next page of results.
    """

    @property
    def raw_page(self):
        return self

    analyzed_invocations: MutableSequence['AnalyzedInvocation'] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message='AnalyzedInvocation',
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class AggregateAnalyzedSessionsRequest(proto.Message):
    r"""Request to aggregate AnalyzedSessions across one or more
    MonitoredAgents. Use the ``-`` wildcard in the monitored_agent
    segment of the parent to aggregate across all MonitoredAgents in the
    location.

    Attributes:
        parent (str):
            Required. The parent MonitoredAgent resource. Use the ``-``
            wildcard for the monitored_agent segment to aggregate across
            multiple agents in the location. Format:
            ``projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}``
        filter (str):
            Optional. Filter expression restricting which
            AnalyzedSessions are included in the aggregation. Supports a
            subset of the ``ListAnalyzedSessionsRequest.filter``
            grammar: a closed ``detection_time`` window with both bounds
            required. The ``severity`` clause is not supported here. If
            empty, the aggregation covers the last 3 days.

            Example:

            ::

               detection_time >= "2024-01-01T00:00:00Z" AND detection_time <=
               "2024-01-08T00:00:00Z".
        page_size (int):
            Optional. The standard list page size. The
            maximum value is 100; values above 100 will be
            coerced to 100. If unspecified, at most 10
            MonitoredAgents will be returned.
        page_token (str):
            Optional. The standard list page token.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    filter: str = proto.Field(
        proto.STRING,
        number=2,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=3,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=4,
    )


class AggregateAnalyzedSessionsResponse(proto.Message):
    r"""Contains aggregated AnalyzedSession statistics, grouped by
    MonitoredAgent.

    Attributes:
        agent_aggregates (MutableSequence[google.cloud.aiplatform_v1.types.AggregateAnalyzedSessionsResponse.AgentAggregate]):
            Aggregated statistics — exactly one entry per
            unique MonitoredAgent matched by the request.
        summary (google.cloud.aiplatform_v1.types.ListAnalyzedSessionsResponse.ViewSummary):
            Overall summary across every MonitoredAgent
            included in the response.
        next_page_token (str):
            A token, which can be sent as ``page_token`` to retrieve the
            next page. If this field is omitted, there are no subsequent
            pages.
    """

    class AgentAggregate(proto.Message):
        r"""Contains aggregated statistics for one MonitoredAgent.

        Attributes:
            monitored_agent (str):
                The MonitoredAgent resource name. Format:
                ``projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}``
            agent_resource_name (str):
                The resource name or identifier of the agent. Matches
                ``AgentResource.agent`` on the corresponding
                ``MonitoredAgent``, so the format depends on that agent's
                ``AgentResource.agent_type``. For the format of each agent
                type, see
                [AgentResource.agent][google.cloud.aiplatform.v1.AgentResource.agent].
            agent_display_name (str):
                Output only. The human-readable display name
                of the MonitoredAgent.
            agent_status (google.cloud.aiplatform_v1.types.MonitoredAgent.EnablementState):
                Output only. The enablement state of the
                MonitoredAgent (for example, ACTIVE, DISABLED,
                or ENABLING).
            location (str):
                Output only. The region of the agent, in the same form as
                ``AgentResource.location`` (for example, ``us-central1``).
                Empty when the agent is not enrolled or its location is
                unknown.
            agent_type (google.cloud.aiplatform_v1.types.AgentResource.AgentType):
                Output only. The runtime the agent is hosted on (for
                example, ``CLOUD_RUN_SERVICE``).

                ``AGENT_TYPE_UNSPECIFIED`` means the runtime is unknown to
                this service, which is distinct from ``AGENT_TYPE_OTHER``
                (known, and not one of the other enumerated runtimes).
            total_sessions_count (int):
                The number of analyzed sessions for this
                agent matched by the request.
            anomalous_sessions_count (int):
                The number of anomalous (SESSION_STATE_FLAGGED) sessions for
                this agent.
            latest_session_time (google.protobuf.timestamp_pb2.Timestamp):
                The latest session update_time observed for this agent.
            severities (MutableMapping[str, google.cloud.aiplatform_v1.types.AnalyzedSession.SeveritySummary]):
                Map of severity level (string representation of Severity) to
                detector summaries aggregated across all sessions for this
                agent. The key is the string representation of Severity
                enum: "SEVERITY_UNSPECIFIED", "SEVERITY_CRITICAL",
                "SEVERITY_HIGH", "SEVERITY_MEDIUM", "SEVERITY_LOW".
        """

        monitored_agent: str = proto.Field(
            proto.STRING,
            number=1,
        )
        agent_resource_name: str = proto.Field(
            proto.STRING,
            number=2,
        )
        agent_display_name: str = proto.Field(
            proto.STRING,
            number=7,
        )
        agent_status: 'MonitoredAgent.EnablementState' = proto.Field(
            proto.ENUM,
            number=8,
            enum='MonitoredAgent.EnablementState',
        )
        location: str = proto.Field(
            proto.STRING,
            number=9,
        )
        agent_type: 'AgentResource.AgentType' = proto.Field(
            proto.ENUM,
            number=10,
            enum='AgentResource.AgentType',
        )
        total_sessions_count: int = proto.Field(
            proto.INT32,
            number=3,
        )
        anomalous_sessions_count: int = proto.Field(
            proto.INT32,
            number=4,
        )
        latest_session_time: timestamp_pb2.Timestamp = proto.Field(
            proto.MESSAGE,
            number=5,
            message=timestamp_pb2.Timestamp,
        )
        severities: MutableMapping[str, 'AnalyzedSession.SeveritySummary'] = proto.MapField(
            proto.STRING,
            proto.MESSAGE,
            number=6,
            message='AnalyzedSession.SeveritySummary',
        )

    @property
    def raw_page(self):
        return self

    agent_aggregates: MutableSequence[AgentAggregate] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=AgentAggregate,
    )
    summary: 'ListAnalyzedSessionsResponse.ViewSummary' = proto.Field(
        proto.MESSAGE,
        number=2,
        message='ListAnalyzedSessionsResponse.ViewSummary',
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
