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

from google.cloud.aiplatform_v1beta1.types import content as gca_content
from google.cloud.aiplatform_v1beta1.types import openapi
import google.protobuf.duration_pb2 as duration_pb2  # type: ignore
import google.protobuf.struct_pb2 as struct_pb2  # type: ignore
import google.protobuf.timestamp_pb2 as timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "MemoryType",
        "Memory",
        "MemoryTopicId",
        "MemoryBankCustomizationConfig",
        "StructuredMemoryConfig",
        "MemoryRevision",
        "IntermediateExtractedMemory",
        "MemoryMetadataValue",
        "MemoryConjunctionFilter",
        "MemoryFilter",
        "MemoryGenerationTriggerConfig",
        "MemoryProfile",
    },
)


class MemoryType(proto.Enum):
    r"""The type of Memory.

    Values:
        MEMORY_TYPE_UNSPECIFIED (0):
            Represents an unspecified memory type. This
            value should not be used.
        NATURAL_LANGUAGE_COLLECTION (1):
            Indicates belonging to a collection of
            natural language memories.
        STRUCTURED_PROFILE (3):
            Indicates belonging to a structured profile.
    """

    MEMORY_TYPE_UNSPECIFIED = 0
    NATURAL_LANGUAGE_COLLECTION = 1
    STRUCTURED_PROFILE = 3


class Memory(proto.Message):
    r"""A memory.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        expire_time (google.protobuf.timestamp_pb2.Timestamp):
            Optional. Represents the timestamp of when this resource is
            considered expired. This is *always* provided on output when
            ``expiration`` is set on input, regardless of whether
            ``expire_time`` or ``ttl`` was provided.

            This field is a member of `oneof`_ ``expiration``.
        ttl (google.protobuf.duration_pb2.Duration):
            Optional. Input only. Represents the TTL for
            this resource. The expiration time is computed:
            now + TTL.

            This field is a member of `oneof`_ ``expiration``.
        revision_expire_time (google.protobuf.timestamp_pb2.Timestamp):
            Optional. Input only. Represents the
            timestamp of when the revision is considered
            expired. If not set, the memory revision will be
            kept until manually deleted.

            This field is a member of `oneof`_ ``revision_expiration``.
        revision_ttl (google.protobuf.duration_pb2.Duration):
            Optional. Input only. Represents the TTL for
            the revision. The expiration time is computed:
            now + TTL.

            This field is a member of `oneof`_ ``revision_expiration``.
        disable_memory_revisions (bool):
            Optional. Input only. Indicates whether no
            revision will be created for this request.

            This field is a member of `oneof`_ ``revision_expiration``.
        name (str):
            Identifier. Represents the resource name of the Memory.
            Format:
            ``projects/{project}/locations/{location}/reasoningEngines/{reasoning_engine}/memories/{memory}``
        display_name (str):
            Optional. Represents the display name of the
            Memory.
        description (str):
            Optional. Represents the description of the
            Memory.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Represents the timestamp when
            this Memory was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Represents the timestamp when
            this Memory was most recently updated.
        fact (str):
            Optional. Represents semantic knowledge
            extracted from the source content.
        scope (MutableMapping[str, str]):
            Required. Immutable. Represents the scope of the Memory.
            Memories are isolated within their scope. The scope is
            defined when creating or generating memories. Scope values
            cannot contain the wildcard character '\*'.
        topics (MutableSequence[google.cloud.aiplatform_v1beta1.types.MemoryTopicId]):
            Optional. Represents the Topics of the
            Memory.
        revision_labels (MutableMapping[str, str]):
            Optional. Input only. Represents the labels
            to apply to the Memory Revision created as a
            result of this request.
        metadata (MutableMapping[str, google.cloud.aiplatform_v1beta1.types.MemoryMetadataValue]):
            Optional. Represents user-provided metadata
            for the Memory. This information was provided
            when creating, updating, or generating the
            Memory. It was not generated by Memory Bank.
        memory_type (google.cloud.aiplatform_v1beta1.types.MemoryType):
            Optional. Represents the type of the memory. If not set, the
            ``NATURAL_LANGUAGE_COLLECTION`` type is used. If
            ``STRUCTURED_COLLECTION`` or ``STRUCTURED_PROFILE`` is used,
            then ``structured_data`` must be provided.
        structured_content (google.cloud.aiplatform_v1beta1.types.Memory.StructuredContent):
            Optional. Represents the structured content
            of the memory.
        context (str):
            Optional. Represents the context of the
            memory.
    """

    class StructuredContent(proto.Message):
        r"""Represents the structured value of the memory.

        Attributes:
            data (google.protobuf.struct_pb2.Struct):
                Required. Represents the structured value of
                the memory.
            schema_id (str):
                Required. Represents the schema ID for which
                this structured memory belongs to.
        """

        data: struct_pb2.Struct = proto.Field(
            proto.MESSAGE,
            number=1,
            message=struct_pb2.Struct,
        )
        schema_id: str = proto.Field(
            proto.STRING,
            number=2,
        )

    expire_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=13,
        oneof="expiration",
        message=timestamp_pb2.Timestamp,
    )
    ttl: duration_pb2.Duration = proto.Field(
        proto.MESSAGE,
        number=14,
        oneof="expiration",
        message=duration_pb2.Duration,
    )
    revision_expire_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=16,
        oneof="revision_expiration",
        message=timestamp_pb2.Timestamp,
    )
    revision_ttl: duration_pb2.Duration = proto.Field(
        proto.MESSAGE,
        number=17,
        oneof="revision_expiration",
        message=duration_pb2.Duration,
    )
    disable_memory_revisions: bool = proto.Field(
        proto.BOOL,
        number=18,
        oneof="revision_expiration",
    )
    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    display_name: str = proto.Field(
        proto.STRING,
        number=2,
    )
    description: str = proto.Field(
        proto.STRING,
        number=3,
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=4,
        message=timestamp_pb2.Timestamp,
    )
    update_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=5,
        message=timestamp_pb2.Timestamp,
    )
    fact: str = proto.Field(
        proto.STRING,
        number=10,
    )
    scope: MutableMapping[str, str] = proto.MapField(
        proto.STRING,
        proto.STRING,
        number=11,
    )
    topics: MutableSequence["MemoryTopicId"] = proto.RepeatedField(
        proto.MESSAGE,
        number=15,
        message="MemoryTopicId",
    )
    revision_labels: MutableMapping[str, str] = proto.MapField(
        proto.STRING,
        proto.STRING,
        number=19,
    )
    metadata: MutableMapping[str, "MemoryMetadataValue"] = proto.MapField(
        proto.STRING,
        proto.MESSAGE,
        number=21,
        message="MemoryMetadataValue",
    )
    memory_type: "MemoryType" = proto.Field(
        proto.ENUM,
        number=22,
        enum="MemoryType",
    )
    structured_content: StructuredContent = proto.Field(
        proto.MESSAGE,
        number=24,
        message=StructuredContent,
    )
    context: str = proto.Field(
        proto.STRING,
        number=25,
    )


class MemoryTopicId(proto.Message):
    r"""A memory topic identifier.
    This will be used to label a Memory and to restrict which topics
    are eligible for generation or retrieval.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        custom_memory_topic_label (str):
            Optional. Represents the custom memory topic
            label.

            This field is a member of `oneof`_ ``topic_id``.
        managed_memory_topic (google.cloud.aiplatform_v1beta1.types.MemoryBankCustomizationConfig.MemoryTopic.ManagedMemoryTopic.ManagedTopicEnum):
            Optional. Represents the managed memory
            topic.

            This field is a member of `oneof`_ ``topic_id``.
    """

    custom_memory_topic_label: str = proto.Field(
        proto.STRING,
        number=1,
        oneof="topic_id",
    )
    managed_memory_topic: (
        "MemoryBankCustomizationConfig.MemoryTopic.ManagedMemoryTopic.ManagedTopicEnum"
    ) = proto.Field(
        proto.ENUM,
        number=2,
        oneof="topic_id",
        enum="MemoryBankCustomizationConfig.MemoryTopic.ManagedMemoryTopic.ManagedTopicEnum",
    )


class MemoryBankCustomizationConfig(proto.Message):
    r"""Represents configuration for organizing natural language
    memories for a particular scope.

    Attributes:
        scope_keys (MutableSequence[str]):
            Optional. Represents the scope keys (i.e. 'user_id') for
            which to use this config. A request's scope must include all
            of the provided keys for the config to be used (order does
            not matter). If empty, then the config will be used for all
            requests that do not have a more specific config. Only one
            default config is allowed per Memory Bank.
        memory_topics (MutableSequence[google.cloud.aiplatform_v1beta1.types.MemoryBankCustomizationConfig.MemoryTopic]):
            Optional. Represents topics of information
            that should be extracted from conversations and
            stored as memories. If not set, then Memory
            Bank's default topics will be used.
        generate_memories_examples (MutableSequence[google.cloud.aiplatform_v1beta1.types.MemoryBankCustomizationConfig.GenerateMemoriesExample]):
            Optional. Provides examples of how to
            generate memories for a particular scope.
        enable_third_person_memories (bool):
            Optional. Indicates whether the memories will
            be generated in the third person (i.e. "The user
            generates memories with Memory Bank."). By
            default, the memories will be generated in the
            first person (i.e. "I generate memories with
            Memory Bank.")
        consolidation_config (google.cloud.aiplatform_v1beta1.types.MemoryBankCustomizationConfig.ConsolidationConfig):
            Optional. Represents configuration for
            customizing how memories are consolidated
            together.
        disable_natural_language_memories (bool):
            Optional. Indicates whether natural language memory
            generation should be disabled for all requests. By default,
            natural language memory generation is enabled. Set this to
            ``true`` when you only want to generate structured memories.
    """

    class MemoryTopic(proto.Message):
        r"""A topic of information that should be extracted from
        conversations and stored as memories.

        This message has `oneof`_ fields (mutually exclusive fields).
        For each oneof, at most one member field can be set at the same time.
        Setting any member of the oneof automatically clears all other
        members.

        .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

        Attributes:
            custom_memory_topic (google.cloud.aiplatform_v1beta1.types.MemoryBankCustomizationConfig.MemoryTopic.CustomMemoryTopic):
                A custom memory topic defined by the
                developer.

                This field is a member of `oneof`_ ``topic_type``.
            managed_memory_topic (google.cloud.aiplatform_v1beta1.types.MemoryBankCustomizationConfig.MemoryTopic.ManagedMemoryTopic):
                A managed memory topic defined by Memory
                Bank.

                This field is a member of `oneof`_ ``topic_type``.
        """

        class CustomMemoryTopic(proto.Message):
            r"""A custom memory topic defined by the developer.

            Attributes:
                label (str):
                    Required. Represents the label of the topic.
                description (str):
                    Required. Represents the description of the
                    memory topic. This should explain what
                    information should be extracted for this topic.
            """

            label: str = proto.Field(
                proto.STRING,
                number=1,
            )
            description: str = proto.Field(
                proto.STRING,
                number=2,
            )

        class ManagedMemoryTopic(proto.Message):
            r"""A managed memory topic defined by the system.

            Attributes:
                managed_topic_enum (google.cloud.aiplatform_v1beta1.types.MemoryBankCustomizationConfig.MemoryTopic.ManagedMemoryTopic.ManagedTopicEnum):
                    Required. Represents the managed topic.
            """

            class ManagedTopicEnum(proto.Enum):
                r"""Represents managed topics.

                Values:
                    MANAGED_TOPIC_ENUM_UNSPECIFIED (0):
                        Represents an unspecified topic. This value
                        should not be used.
                    USER_PERSONAL_INFO (1):
                        Represents significant personal information
                        about the User like first names, relationships,
                        hobbies, important dates.
                    USER_PREFERENCES (2):
                        Represents stated or implied likes, dislikes,
                        preferred styles, or patterns.
                    KEY_CONVERSATION_DETAILS (3):
                        Represents important milestones or
                        conclusions within the dialogue.
                    EXPLICIT_INSTRUCTIONS (4):
                        Represents information that the user
                        explicitly requested to remember or forget.
                """

                MANAGED_TOPIC_ENUM_UNSPECIFIED = 0
                USER_PERSONAL_INFO = 1
                USER_PREFERENCES = 2
                KEY_CONVERSATION_DETAILS = 3
                EXPLICIT_INSTRUCTIONS = 4

            managed_topic_enum: "MemoryBankCustomizationConfig.MemoryTopic.ManagedMemoryTopic.ManagedTopicEnum" = proto.Field(
                proto.ENUM,
                number=1,
                enum="MemoryBankCustomizationConfig.MemoryTopic.ManagedMemoryTopic.ManagedTopicEnum",
            )

        custom_memory_topic: (
            "MemoryBankCustomizationConfig.MemoryTopic.CustomMemoryTopic"
        ) = proto.Field(
            proto.MESSAGE,
            number=3,
            oneof="topic_type",
            message="MemoryBankCustomizationConfig.MemoryTopic.CustomMemoryTopic",
        )
        managed_memory_topic: (
            "MemoryBankCustomizationConfig.MemoryTopic.ManagedMemoryTopic"
        ) = proto.Field(
            proto.MESSAGE,
            number=4,
            oneof="topic_type",
            message="MemoryBankCustomizationConfig.MemoryTopic.ManagedMemoryTopic",
        )

    class GenerateMemoriesExample(proto.Message):
        r"""An example of how to generate memories for a particular
        scope.


        .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

        Attributes:
            conversation_source (google.cloud.aiplatform_v1beta1.types.MemoryBankCustomizationConfig.GenerateMemoriesExample.ConversationSource):
                A conversation source for the example.

                This field is a member of `oneof`_ ``source``.
            generated_memories (MutableSequence[google.cloud.aiplatform_v1beta1.types.MemoryBankCustomizationConfig.GenerateMemoriesExample.GeneratedMemory]):
                Optional. Represents the memories that are
                expected to be generated from the input
                conversation. An empty list indicates that no
                memories are expected to be generated for the
                input conversation.
        """

        class ConversationSource(proto.Message):
            r"""A conversation source for the example. This is similar to
            ``DirectContentsSource``.

            Attributes:
                events (MutableSequence[google.cloud.aiplatform_v1beta1.types.MemoryBankCustomizationConfig.GenerateMemoriesExample.ConversationSource.Event]):
                    Optional. Represents the input conversation
                    events for the example.
            """

            class Event(proto.Message):
                r"""A single conversation event.

                Attributes:
                    content (google.cloud.aiplatform_v1beta1.types.Content):
                        Required. Represents the content of the
                        event.
                """

                content: gca_content.Content = proto.Field(
                    proto.MESSAGE,
                    number=1,
                    message=gca_content.Content,
                )

            events: MutableSequence[
                "MemoryBankCustomizationConfig.GenerateMemoriesExample.ConversationSource.Event"
            ] = proto.RepeatedField(
                proto.MESSAGE,
                number=1,
                message="MemoryBankCustomizationConfig.GenerateMemoriesExample.ConversationSource.Event",
            )

        class GeneratedMemory(proto.Message):
            r"""A memory generated by the operation.

            Attributes:
                fact (str):
                    Required. Represents the fact to generate a
                    memory from.
                topics (MutableSequence[google.cloud.aiplatform_v1beta1.types.MemoryTopicId]):
                    Optional. Represents the list of topics that the memory
                    should be associated with. For example, use
                    ``custom_memory_topic_label = "jargon"`` if the extracted
                    memory is an example of memory extraction for the custom
                    topic ``jargon``.
            """

            fact: str = proto.Field(
                proto.STRING,
                number=1,
            )
            topics: MutableSequence["MemoryTopicId"] = proto.RepeatedField(
                proto.MESSAGE,
                number=2,
                message="MemoryTopicId",
            )

        conversation_source: (
            "MemoryBankCustomizationConfig.GenerateMemoriesExample.ConversationSource"
        ) = proto.Field(
            proto.MESSAGE,
            number=3,
            oneof="source",
            message="MemoryBankCustomizationConfig.GenerateMemoriesExample.ConversationSource",
        )
        generated_memories: MutableSequence[
            "MemoryBankCustomizationConfig.GenerateMemoriesExample.GeneratedMemory"
        ] = proto.RepeatedField(
            proto.MESSAGE,
            number=4,
            message="MemoryBankCustomizationConfig.GenerateMemoriesExample.GeneratedMemory",
        )

    class ConsolidationConfig(proto.Message):
        r"""Represents configuration for customizing how memories are
        consolidated.

        Attributes:
            revisions_per_candidate_count (int):
                Optional. Represents the maximum number of
                revisions to consider for each candidate memory.
                If not set, then the default value (1) will be
                used, which means that only the latest revision
                will be considered.
        """

        revisions_per_candidate_count: int = proto.Field(
            proto.INT32,
            number=1,
        )

    scope_keys: MutableSequence[str] = proto.RepeatedField(
        proto.STRING,
        number=1,
    )
    memory_topics: MutableSequence[MemoryTopic] = proto.RepeatedField(
        proto.MESSAGE,
        number=2,
        message=MemoryTopic,
    )
    generate_memories_examples: MutableSequence[GenerateMemoriesExample] = (
        proto.RepeatedField(
            proto.MESSAGE,
            number=3,
            message=GenerateMemoriesExample,
        )
    )
    enable_third_person_memories: bool = proto.Field(
        proto.BOOL,
        number=4,
    )
    consolidation_config: ConsolidationConfig = proto.Field(
        proto.MESSAGE,
        number=5,
        message=ConsolidationConfig,
    )
    disable_natural_language_memories: bool = proto.Field(
        proto.BOOL,
        number=6,
    )


class StructuredMemoryConfig(proto.Message):
    r"""Represents configuration for organizing structured memories
    for a particular scope.

    Attributes:
        scope_keys (MutableSequence[str]):
            Optional. Represents the scope keys (i.e. 'user_id') for
            which to use this config. A request's scope must include all
            of the provided keys for the config to be used (order does
            not matter). If empty, then the config will be used for all
            requests that do not have a more specific config. Only one
            default config is allowed per Memory Bank.
        schema_configs (MutableSequence[google.cloud.aiplatform_v1beta1.types.StructuredMemoryConfig.SchemaConfig]):
            Optional. Represents configuration of the
            structured memories' schemas.
    """

    class SchemaConfig(proto.Message):
        r"""Schema configuration for structured memories.

        Attributes:
            id (str):
                Required. Represents the ID of the schema.
                Must be 1-63 characters, start with a lowercase
                letter, and consist of lowercase letters,
                numbers, and hyphens.
            schema (google.cloud.aiplatform_v1beta1.types.Schema):
                Required. Represents the OpenAPI schema of the structured
                memories. The schema ``type`` cannot be ``ARRAY`` when
                ``memory_type`` is ``STRUCTURED_PROFILE``.
            memory_type (google.cloud.aiplatform_v1beta1.types.MemoryType):
                Optional. Represents the type of the structured memories
                associated with the schema. If not set, then
                ``STRUCTURED_PROFILE`` will be used.
            json_schema (google.protobuf.struct_pb2.Value):
                Optional. Represents the JSON Schema of the
                structured memories.
        """

        id: str = proto.Field(
            proto.STRING,
            number=1,
        )
        schema: openapi.Schema = proto.Field(
            proto.MESSAGE,
            number=2,
            message=openapi.Schema,
        )
        memory_type: "MemoryType" = proto.Field(
            proto.ENUM,
            number=3,
            enum="MemoryType",
        )
        json_schema: struct_pb2.Value = proto.Field(
            proto.MESSAGE,
            number=5,
            message=struct_pb2.Value,
        )

    scope_keys: MutableSequence[str] = proto.RepeatedField(
        proto.STRING,
        number=1,
    )
    schema_configs: MutableSequence[SchemaConfig] = proto.RepeatedField(
        proto.MESSAGE,
        number=2,
        message=SchemaConfig,
    )


class MemoryRevision(proto.Message):
    r"""A revision of a Memory.

    Attributes:
        name (str):
            Identifier. Represents the resource name of the Memory
            Revision. Format:
            ``projects/{project}/locations/{location}/reasoningEngines/{reasoning_engine}/memories/{memory}/revisions/{memory_revision}``
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Represents the timestamp when
            this Memory Revision was created.
        expire_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Represents the timestamp of when
            this resource is considered expired.
        fact (str):
            Output only. Represents the fact of the Memory Revision.
            This corresponds to the ``fact`` field of the parent Memory
            at the time of revision creation.
        labels (MutableMapping[str, str]):
            Output only. Represents the labels of the Memory Revision.
            These labels are applied to the MemoryRevision when it is
            created based on
            ``GenerateMemoriesRequest.revision_labels``.
        extracted_memories (MutableSequence[google.cloud.aiplatform_v1beta1.types.IntermediateExtractedMemory]):
            Output only. Represents the extracted
            memories from the source content before
            consolidation when the memory was updated via
            GenerateMemories. This information was used to
            modify an existing Memory via Consolidation.
        structured_data (google.protobuf.struct_pb2.Struct):
            Output only. Represents the structured value
            of the memory at the time of revision creation.
        context (str):
            Output only. Represents the context of the
            Memory Revision. The context may include context
            from both the historical revisions and the
            extracted content.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=2,
        message=timestamp_pb2.Timestamp,
    )
    expire_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=3,
        message=timestamp_pb2.Timestamp,
    )
    fact: str = proto.Field(
        proto.STRING,
        number=4,
    )
    labels: MutableMapping[str, str] = proto.MapField(
        proto.STRING,
        proto.STRING,
        number=5,
    )
    extracted_memories: MutableSequence["IntermediateExtractedMemory"] = (
        proto.RepeatedField(
            proto.MESSAGE,
            number=6,
            message="IntermediateExtractedMemory",
        )
    )
    structured_data: struct_pb2.Struct = proto.Field(
        proto.MESSAGE,
        number=7,
        message=struct_pb2.Struct,
    )
    context: str = proto.Field(
        proto.STRING,
        number=8,
    )


class IntermediateExtractedMemory(proto.Message):
    r"""An extracted memory that is the intermediate result before
    consolidation.

    Attributes:
        fact (str):
            Output only. Represents the fact of the
            extracted memory.
        structured_data (google.protobuf.struct_pb2.Struct):
            Output only. Represents the structured value
            of the extracted memory.
        context (str):
            Output only. Represents the explanation of
            why the information was extracted from the
            source content.
    """

    fact: str = proto.Field(
        proto.STRING,
        number=1,
    )
    structured_data: struct_pb2.Struct = proto.Field(
        proto.MESSAGE,
        number=3,
        message=struct_pb2.Struct,
    )
    context: str = proto.Field(
        proto.STRING,
        number=4,
    )


class MemoryMetadataValue(proto.Message):
    r"""Memory metadata.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        string_value (str):
            Represents a string value.

            This field is a member of `oneof`_ ``value``.
        double_value (float):
            Represents a double value.

            This field is a member of `oneof`_ ``value``.
        bool_value (bool):
            Represents a boolean value.

            This field is a member of `oneof`_ ``value``.
        timestamp_value (google.protobuf.timestamp_pb2.Timestamp):
            Represents a timestamp value. When filtering
            on timestamp values, only the seconds field will
            be compared.

            This field is a member of `oneof`_ ``value``.
    """

    string_value: str = proto.Field(
        proto.STRING,
        number=1,
        oneof="value",
    )
    double_value: float = proto.Field(
        proto.DOUBLE,
        number=2,
        oneof="value",
    )
    bool_value: bool = proto.Field(
        proto.BOOL,
        number=3,
        oneof="value",
    )
    timestamp_value: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=4,
        oneof="value",
        message=timestamp_pb2.Timestamp,
    )


class MemoryConjunctionFilter(proto.Message):
    r"""A conjunction of filters that will be combined using AND
    logic.

    Attributes:
        filters (MutableSequence[google.cloud.aiplatform_v1beta1.types.MemoryFilter]):
            Represents filters that will be combined
            using AND logic.
    """

    filters: MutableSequence["MemoryFilter"] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message="MemoryFilter",
    )


class MemoryFilter(proto.Message):
    r"""Filter to apply when retrieving memories.

    Attributes:
        key (str):
            Represents the key of the filter. For example, "author"
            would apply to ``metadata`` entries with the key "author".
        op (google.cloud.aiplatform_v1beta1.types.MemoryFilter.Operator):
            Represents the operator to apply to the
            filter. If not set, then EQUAL will be used.
        value (google.cloud.aiplatform_v1beta1.types.MemoryMetadataValue):
            Represents the value to compare to.
        negate (bool):
            Indicates whether the filter will be negated.
    """

    class Operator(proto.Enum):
        r"""Represents the operator to apply to the filter.

        Values:
            OPERATOR_UNSPECIFIED (0):
                Represents an unspecified operator. Defaults
                to EQUAL.
            EQUAL (1):
                Equal to.
            GREATER_THAN (2):
                Greater than.
            LESS_THAN (3):
                Less than.
        """

        OPERATOR_UNSPECIFIED = 0
        EQUAL = 1
        GREATER_THAN = 2
        LESS_THAN = 3

    key: str = proto.Field(
        proto.STRING,
        number=1,
    )
    op: Operator = proto.Field(
        proto.ENUM,
        number=2,
        enum=Operator,
    )
    value: "MemoryMetadataValue" = proto.Field(
        proto.MESSAGE,
        number=3,
        message="MemoryMetadataValue",
    )
    negate: bool = proto.Field(
        proto.BOOL,
        number=4,
    )


class MemoryGenerationTriggerConfig(proto.Message):
    r"""Represents configuration for triggering generation.

    Attributes:
        generation_rule (google.cloud.aiplatform_v1beta1.types.MemoryGenerationTriggerConfig.GenerationTriggerRule):
            Optional. Represents the active rule that
            determines when to flush the buffer. If not set,
            then the stream will be force flushed
            immediately.
    """

    class GenerationTriggerRule(proto.Message):
        r"""Represents the active rule that determines when to flush the
        buffer.

        This message has `oneof`_ fields (mutually exclusive fields).
        For each oneof, at most one member field can be set at the same time.
        Setting any member of the oneof automatically clears all other
        members.

        .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

        Attributes:
            idle_duration (google.protobuf.duration_pb2.Duration):
                Optional. Specifies to trigger generation if
                the stream is inactive for the specified
                duration after the most recent event. The
                duration must have a minute-level granularity.

                This field is a member of `oneof`_ ``time_based_condition``.
            fixed_interval (google.protobuf.duration_pb2.Duration):
                Optional. Specifies to trigger generation at
                a fixed interval. The duration must have a
                minute-level granularity.

                This field is a member of `oneof`_ ``time_based_condition``.
            overlap_event_count (int):
                Optional. Re-include the last N
                already-processed events in the next window.

                This field is a member of `oneof`_ ``overlap_window``.
            event_count (int):
                Optional. Specifies to trigger generation
                when the event count reaches this limit.
        """

        idle_duration: duration_pb2.Duration = proto.Field(
            proto.MESSAGE,
            number=1,
            oneof="time_based_condition",
            message=duration_pb2.Duration,
        )
        fixed_interval: duration_pb2.Duration = proto.Field(
            proto.MESSAGE,
            number=2,
            oneof="time_based_condition",
            message=duration_pb2.Duration,
        )
        overlap_event_count: int = proto.Field(
            proto.INT32,
            number=5,
            oneof="overlap_window",
        )
        event_count: int = proto.Field(
            proto.INT32,
            number=4,
        )

    generation_rule: GenerationTriggerRule = proto.Field(
        proto.MESSAGE,
        number=1,
        message=GenerationTriggerRule,
    )


class MemoryProfile(proto.Message):
    r"""A memory profile.

    Attributes:
        schema_id (str):
            Represents the ID of the schema. This ID corresponds to the
            ``schema_id`` defined inside the SchemaConfig, under
            StructuredMemoryCustomizationConfig.
        profile (google.protobuf.struct_pb2.Struct):
            Represents the profile data.
    """

    schema_id: str = proto.Field(
        proto.STRING,
        number=1,
    )
    profile: struct_pb2.Struct = proto.Field(
        proto.MESSAGE,
        number=2,
        message=struct_pb2.Struct,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
