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

from google.cloud.aiplatform_v1beta1.types import content as gca_content
from google.cloud.aiplatform_v1beta1.types import tool
import google.protobuf.struct_pb2 as struct_pb2  # type: ignore
import google.protobuf.timestamp_pb2 as timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "AgentData",
        "AgentConfig",
        "ConversationTurn",
        "AgentEvent",
    },
)


class AgentData(proto.Message):
    r"""Represents data specific to multi-turn agent evaluations.

    Attributes:
        agents (MutableMapping[str, google.cloud.aiplatform_v1beta1.types.AgentConfig]):
            Optional. A map containing the static configurations for
            each agent in the system. Key: agent_id (matches the
            ``author`` field in events). Value: The static configuration
            of the agent.
        turns (MutableSequence[google.cloud.aiplatform_v1beta1.types.ConversationTurn]):
            Optional. A chronological list of
            conversation turns. Each turn represents a
            logical execution cycle (e.g., User Input ->
            Agent Response).
    """

    agents: MutableMapping[str, "AgentConfig"] = proto.MapField(
        proto.STRING,
        proto.MESSAGE,
        number=1,
        message="AgentConfig",
    )
    turns: MutableSequence["ConversationTurn"] = proto.RepeatedField(
        proto.MESSAGE,
        number=2,
        message="ConversationTurn",
    )


class AgentConfig(proto.Message):
    r"""Represents configuration for an Agent.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        agent_id (str):
            Required. Unique identifier of the agent. This ID is used to
            refer to this agent, e.g., in AgentEvent.author, or in the
            ``sub_agents`` field. It must be unique within the
            ``agents`` map.

            This field is a member of `oneof`_ ``_agent_id``.
        agent_type (str):
            Optional. The type or class of the agent
            (e.g., "LlmAgent", "RouterAgent",
            "ToolUseAgent"). Useful for the autorater to
            understand the expected behavior of the agent.
        description (str):
            Optional. A high-level description of the
            agent's role and responsibilities. Critical for
            evaluating if the agent is routing tasks
            correctly.
        instruction (str):
            Optional. Provides instructions for the LLM model, guiding
            the agent's behavior. Can be static or dynamic. Dynamic
            instructions can contain placeholders like {variable_name}
            that will be resolved at runtime using the
            ``AgentEvent.state_delta`` field.
        tools (MutableSequence[google.cloud.aiplatform_v1beta1.types.Tool]):
            Optional. The list of tools available to this
            agent.
        sub_agents (MutableSequence[str]):
            Optional. The list of valid agent IDs that
            this agent can delegate to. This defines the
            directed edges in the multi-agent system graph
            topology.
    """

    agent_id: str = proto.Field(
        proto.STRING,
        number=1,
        optional=True,
    )
    agent_type: str = proto.Field(
        proto.STRING,
        number=2,
    )
    description: str = proto.Field(
        proto.STRING,
        number=3,
    )
    instruction: str = proto.Field(
        proto.STRING,
        number=4,
    )
    tools: MutableSequence[tool.Tool] = proto.RepeatedField(
        proto.MESSAGE,
        number=5,
        message=tool.Tool,
    )
    sub_agents: MutableSequence[str] = proto.RepeatedField(
        proto.STRING,
        number=6,
    )


class ConversationTurn(proto.Message):
    r"""Represents a single turn/invocation in the conversation.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        turn_index (int):
            Required. The 0-based index of the turn in
            the conversation sequence.

            This field is a member of `oneof`_ ``_turn_index``.
        turn_id (str):
            Optional. A unique identifier for the turn.
            Useful for referencing specific turns across
            systems.
        events (MutableSequence[google.cloud.aiplatform_v1beta1.types.AgentEvent]):
            Optional. The list of events that occurred
            during this turn.
    """

    turn_index: int = proto.Field(
        proto.INT32,
        number=1,
        optional=True,
    )
    turn_id: str = proto.Field(
        proto.STRING,
        number=2,
    )
    events: MutableSequence["AgentEvent"] = proto.RepeatedField(
        proto.MESSAGE,
        number=3,
        message="AgentEvent",
    )


class AgentEvent(proto.Message):
    r"""Represents a single event in the execution trace.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        author (str):
            Required. The ID of the agent or entity that
            generated this event. Use "user" to denote
            events generated by the end-user.

            This field is a member of `oneof`_ ``_author``.
        content (google.cloud.aiplatform_v1beta1.types.Content):
            Required. The content of the event (e.g.,
            text response, tool call, tool response).

            This field is a member of `oneof`_ ``_content``.
        event_time (google.protobuf.timestamp_pb2.Timestamp):
            Optional. The timestamp when the event
            occurred.
        state_delta (google.protobuf.struct_pb2.Struct):
            Optional. The change in the session state
            caused by this event. This is a key-value map of
            fields that were modified or added by the event.
        active_tools (MutableSequence[google.cloud.aiplatform_v1beta1.types.Tool]):
            Optional. The list of tools that were active/available to
            the agent at the time of this event. This overrides the
            ``AgentConfig.tools`` if set.
    """

    author: str = proto.Field(
        proto.STRING,
        number=1,
        optional=True,
    )
    content: gca_content.Content = proto.Field(
        proto.MESSAGE,
        number=2,
        optional=True,
        message=gca_content.Content,
    )
    event_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=3,
        message=timestamp_pb2.Timestamp,
    )
    state_delta: struct_pb2.Struct = proto.Field(
        proto.MESSAGE,
        number=4,
        message=struct_pb2.Struct,
    )
    active_tools: MutableSequence[tool.Tool] = proto.RepeatedField(
        proto.MESSAGE,
        number=5,
        message=tool.Tool,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
