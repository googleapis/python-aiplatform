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

from google.cloud.aiplatform_v1beta1.types import env_var
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "ReasoningEngineSpec",
        "ReasoningEngine",
        "ReasoningEngineContextSpec",
    },
)


class ReasoningEngineSpec(proto.Message):
    r"""ReasoningEngine configurations

    Attributes:
        package_spec (google.cloud.aiplatform_v1beta1.types.ReasoningEngineSpec.PackageSpec):
            Optional. User provided package spec of the ReasoningEngine.
            Ignored when users directly specify a deployment image
            through ``deployment_spec.first_party_image_override``, but
            keeping the field_behavior to avoid introducing breaking
            changes.
        deployment_spec (google.cloud.aiplatform_v1beta1.types.ReasoningEngineSpec.DeploymentSpec):
            Optional. The specification of a Reasoning
            Engine deployment.
        class_methods (MutableSequence[google.protobuf.struct_pb2.Struct]):
            Optional. Declarations for object class
            methods in OpenAPI specification format.
        agent_framework (str):
            Optional. The OSS agent framework used to
            develop the agent. Currently supported values:
            "google-adk", "langchain", "langgraph", "ag2",
            "llama-index", "custom".
    """

    class PackageSpec(proto.Message):
        r"""User provided package spec like pickled object and package
        requirements.

        Attributes:
            pickle_object_gcs_uri (str):
                Optional. The Cloud Storage URI of the
                pickled python object.
            dependency_files_gcs_uri (str):
                Optional. The Cloud Storage URI of the
                dependency files in tar.gz format.
            requirements_gcs_uri (str):
                Optional. The Cloud Storage URI of the ``requirements.txt``
                file
            python_version (str):
                Optional. The Python version. Currently
                support 3.8, 3.9, 3.10, 3.11. If not specified,
                default value is 3.10.
        """

        pickle_object_gcs_uri: str = proto.Field(
            proto.STRING,
            number=1,
        )
        dependency_files_gcs_uri: str = proto.Field(
            proto.STRING,
            number=2,
        )
        requirements_gcs_uri: str = proto.Field(
            proto.STRING,
            number=3,
        )
        python_version: str = proto.Field(
            proto.STRING,
            number=4,
        )

    class DeploymentSpec(proto.Message):
        r"""The specification of a Reasoning Engine deployment.

        Attributes:
            env (MutableSequence[google.cloud.aiplatform_v1beta1.types.EnvVar]):
                Optional. Environment variables to be set
                with the Reasoning Engine deployment. The
                environment variables can be updated through the
                UpdateReasoningEngine API.
            secret_env (MutableSequence[google.cloud.aiplatform_v1beta1.types.SecretEnvVar]):
                Optional. Environment variables where the
                value is a secret in Cloud Secret Manager.
                To use this feature, add 'Secret Manager Secret
                Accessor' role
                (roles/secretmanager.secretAccessor) to AI
                Platform Reasoning Engine Service Agent.
        """

        env: MutableSequence[env_var.EnvVar] = proto.RepeatedField(
            proto.MESSAGE,
            number=1,
            message=env_var.EnvVar,
        )
        secret_env: MutableSequence[env_var.SecretEnvVar] = proto.RepeatedField(
            proto.MESSAGE,
            number=2,
            message=env_var.SecretEnvVar,
        )

    package_spec: PackageSpec = proto.Field(
        proto.MESSAGE,
        number=2,
        message=PackageSpec,
    )
    deployment_spec: DeploymentSpec = proto.Field(
        proto.MESSAGE,
        number=4,
        message=DeploymentSpec,
    )
    class_methods: MutableSequence[struct_pb2.Struct] = proto.RepeatedField(
        proto.MESSAGE,
        number=3,
        message=struct_pb2.Struct,
    )
    agent_framework: str = proto.Field(
        proto.STRING,
        number=5,
    )


class ReasoningEngine(proto.Message):
    r"""ReasoningEngine provides a customizable runtime for models to
    determine which actions to take and in which order.

    Attributes:
        name (str):
            Identifier. The resource name of the ReasoningEngine.
            Format:
            ``projects/{project}/locations/{location}/reasoningEngines/{reasoning_engine}``
        display_name (str):
            Required. The display name of the
            ReasoningEngine.
        description (str):
            Optional. The description of the
            ReasoningEngine.
        spec (google.cloud.aiplatform_v1beta1.types.ReasoningEngineSpec):
            Optional. Configurations of the
            ReasoningEngine
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            ReasoningEngine was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            ReasoningEngine was most recently updated.
        etag (str):
            Optional. Used to perform consistent
            read-modify-write updates. If not set, a blind
            "overwrite" update happens.
        context_spec (google.cloud.aiplatform_v1beta1.types.ReasoningEngineContextSpec):
            Optional. Configuration for how Agent Engine
            sub-resources should manage context.
    """

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
        number=7,
    )
    spec: "ReasoningEngineSpec" = proto.Field(
        proto.MESSAGE,
        number=3,
        message="ReasoningEngineSpec",
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
    etag: str = proto.Field(
        proto.STRING,
        number=6,
    )
    context_spec: "ReasoningEngineContextSpec" = proto.Field(
        proto.MESSAGE,
        number=9,
        message="ReasoningEngineContextSpec",
    )


class ReasoningEngineContextSpec(proto.Message):
    r"""Configuration for how Agent Engine sub-resources should
    manage context.

    Attributes:
        memory_bank_config (google.cloud.aiplatform_v1beta1.types.ReasoningEngineContextSpec.MemoryBankConfig):
            Optional. Specification for a Memory Bank,
            which manages memories for the Agent Engine.
    """

    class MemoryBankConfig(proto.Message):
        r"""Specification for a Memory Bank.

        Attributes:
            generation_config (google.cloud.aiplatform_v1beta1.types.ReasoningEngineContextSpec.MemoryBankConfig.GenerationConfig):
                Optional. Configuration for how to generate
                memories for the Memory Bank.
            similarity_search_config (google.cloud.aiplatform_v1beta1.types.ReasoningEngineContextSpec.MemoryBankConfig.SimilaritySearchConfig):
                Optional. Configuration for how to perform similarity search
                on memories. If not set, the Memory Bank will use the
                default embedding model ``text-embedding-005``.
        """

        class GenerationConfig(proto.Message):
            r"""Configuration for how to generate memories.

            Attributes:
                model (str):
                    Required. The model used to generate memories. Format:
                    ``projects/{project}/locations/{location}/publishers/google/models/{model}``
                    or
                    ``projects/{project}/locations/{location}/endpoints/{endpoint}``.
            """

            model: str = proto.Field(
                proto.STRING,
                number=1,
            )

        class SimilaritySearchConfig(proto.Message):
            r"""Configuration for how to perform similarity search on
            memories.

            Attributes:
                embedding_model (str):
                    Required. The model used to generate embeddings to lookup
                    similar memories. Format:
                    ``projects/{project}/locations/{location}/publishers/google/models/{model}``
                    or
                    ``projects/{project}/locations/{location}/endpoints/{endpoint}``.
            """

            embedding_model: str = proto.Field(
                proto.STRING,
                number=1,
            )

        generation_config: "ReasoningEngineContextSpec.MemoryBankConfig.GenerationConfig" = proto.Field(
            proto.MESSAGE,
            number=1,
            message="ReasoningEngineContextSpec.MemoryBankConfig.GenerationConfig",
        )
        similarity_search_config: "ReasoningEngineContextSpec.MemoryBankConfig.SimilaritySearchConfig" = proto.Field(
            proto.MESSAGE,
            number=2,
            message="ReasoningEngineContextSpec.MemoryBankConfig.SimilaritySearchConfig",
        )

    memory_bank_config: MemoryBankConfig = proto.Field(
        proto.MESSAGE,
        number=1,
        message=MemoryBankConfig,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
