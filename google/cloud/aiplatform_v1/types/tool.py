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
from __future__ import annotations

from typing import MutableMapping, MutableSequence

import proto  # type: ignore

from google.cloud.aiplatform_v1.types import openapi
from google.protobuf import struct_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "Tool",
        "FunctionDeclaration",
        "FunctionCall",
        "FunctionResponse",
        "Retrieval",
        "VertexAISearch",
        "GoogleSearchRetrieval",
        "ToolConfig",
        "FunctionCallingConfig",
    },
)


class Tool(proto.Message):
    r"""Tool details that the model may use to generate response.

    A ``Tool`` is a piece of code that enables the system to interact
    with external systems to perform an action, or set of actions,
    outside of knowledge and scope of the model. A Tool object should
    contain exactly one type of Tool (e.g FunctionDeclaration, Retrieval
    or GoogleSearchRetrieval).

    Attributes:
        function_declarations (MutableSequence[google.cloud.aiplatform_v1.types.FunctionDeclaration]):
            Optional. Function tool type. One or more function
            declarations to be passed to the model along with the
            current user query. Model may decide to call a subset of
            these functions by populating
            [FunctionCall][content.part.function_call] in the response.
            User should provide a
            [FunctionResponse][content.part.function_response] for each
            function call in the next turn. Based on the function
            responses, Model will generate the final response back to
            the user. Maximum 64 function declarations can be provided.
        retrieval (google.cloud.aiplatform_v1.types.Retrieval):
            Optional. Retrieval tool type.
            System will always execute the provided
            retrieval tool(s) to get external knowledge to
            answer the prompt. Retrieval results are
            presented to the model for generation.
        google_search_retrieval (google.cloud.aiplatform_v1.types.GoogleSearchRetrieval):
            Optional. GoogleSearchRetrieval tool type.
            Specialized retrieval tool that is powered by
            Google search.
    """

    function_declarations: MutableSequence["FunctionDeclaration"] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message="FunctionDeclaration",
    )
    retrieval: "Retrieval" = proto.Field(
        proto.MESSAGE,
        number=2,
        message="Retrieval",
    )
    google_search_retrieval: "GoogleSearchRetrieval" = proto.Field(
        proto.MESSAGE,
        number=3,
        message="GoogleSearchRetrieval",
    )


class FunctionDeclaration(proto.Message):
    r"""Structured representation of a function declaration as defined by
    the `OpenAPI 3.0
    specification <https://spec.openapis.org/oas/v3.0.3>`__. Included in
    this declaration are the function name and parameters. This
    FunctionDeclaration is a representation of a block of code that can
    be used as a ``Tool`` by the model and executed by the client.

    Attributes:
        name (str):
            Required. The name of the function to call.
            Must start with a letter or an underscore.
            Must be a-z, A-Z, 0-9, or contain underscores,
            dots and dashes, with a maximum length of 64.
        description (str):
            Optional. Description and purpose of the
            function. Model uses it to decide how and
            whether to call the function.
        parameters (google.cloud.aiplatform_v1.types.Schema):
            Optional. Describes the parameters to this
            function in JSON Schema Object format. Reflects
            the Open API 3.03 Parameter Object. string Key:
            the name of the parameter. Parameter names are
            case sensitive. Schema Value: the Schema
            defining the type used for the parameter. For
            function with no parameters, this can be left
            unset. Parameter names must start with a letter
            or an underscore and must only contain chars
            a-z, A-Z, 0-9, or underscores with a maximum
            length of 64. Example with 1 required and 1
            optional parameter: type: OBJECT properties:

             param1:

               type: STRING
             param2:

               type: INTEGER
            required:

             - param1
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    description: str = proto.Field(
        proto.STRING,
        number=2,
    )
    parameters: openapi.Schema = proto.Field(
        proto.MESSAGE,
        number=3,
        message=openapi.Schema,
    )


class FunctionCall(proto.Message):
    r"""A predicted [FunctionCall] returned from the model that contains a
    string representing the [FunctionDeclaration.name] and a structured
    JSON object containing the parameters and their values.

    Attributes:
        name (str):
            Required. The name of the function to call. Matches
            [FunctionDeclaration.name].
        args (google.protobuf.struct_pb2.Struct):
            Optional. Required. The function parameters and values in
            JSON object format. See [FunctionDeclaration.parameters] for
            parameter details.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    args: struct_pb2.Struct = proto.Field(
        proto.MESSAGE,
        number=2,
        message=struct_pb2.Struct,
    )


class FunctionResponse(proto.Message):
    r"""The result output from a [FunctionCall] that contains a string
    representing the [FunctionDeclaration.name] and a structured JSON
    object containing any output from the function is used as context to
    the model. This should contain the result of a [FunctionCall] made
    based on model prediction.

    Attributes:
        name (str):
            Required. The name of the function to call. Matches
            [FunctionDeclaration.name] and [FunctionCall.name].
        response (google.protobuf.struct_pb2.Struct):
            Required. The function response in JSON
            object format.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    response: struct_pb2.Struct = proto.Field(
        proto.MESSAGE,
        number=2,
        message=struct_pb2.Struct,
    )


class Retrieval(proto.Message):
    r"""Defines a retrieval tool that model can call to access
    external knowledge.


    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        vertex_ai_search (google.cloud.aiplatform_v1.types.VertexAISearch):
            Set to use data source powered by Vertex AI
            Search.

            This field is a member of `oneof`_ ``source``.
        disable_attribution (bool):
            Optional. Deprecated. This option is no
            longer supported.
    """

    vertex_ai_search: "VertexAISearch" = proto.Field(
        proto.MESSAGE,
        number=2,
        oneof="source",
        message="VertexAISearch",
    )
    disable_attribution: bool = proto.Field(
        proto.BOOL,
        number=3,
    )


class VertexAISearch(proto.Message):
    r"""Retrieve from Vertex AI Search datastore for grounding.
    See https://cloud.google.com/vertex-ai-search-and-conversation

    Attributes:
        datastore (str):
            Required. Fully-qualified Vertex AI Search's datastore
            resource ID. Format:
            ``projects/{project}/locations/{location}/collections/{collection}/dataStores/{dataStore}``
    """

    datastore: str = proto.Field(
        proto.STRING,
        number=1,
    )


class GoogleSearchRetrieval(proto.Message):
    r"""Tool to retrieve public web data for grounding, powered by
    Google.

    """


class ToolConfig(proto.Message):
    r"""Tool config. This config is shared for all tools provided in
    the request.

    Attributes:
        function_calling_config (google.cloud.aiplatform_v1.types.FunctionCallingConfig):
            Optional. Function calling config.
    """

    function_calling_config: "FunctionCallingConfig" = proto.Field(
        proto.MESSAGE,
        number=1,
        message="FunctionCallingConfig",
    )


class FunctionCallingConfig(proto.Message):
    r"""Function calling config.

    Attributes:
        mode (google.cloud.aiplatform_v1.types.FunctionCallingConfig.Mode):
            Optional. Function calling mode.
        allowed_function_names (MutableSequence[str]):
            Optional. Function names to call. Only set when the Mode is
            ANY. Function names should match [FunctionDeclaration.name].
            With mode set to ANY, model will predict a function call
            from the set of function names provided.
    """

    class Mode(proto.Enum):
        r"""Function calling mode.

        Values:
            MODE_UNSPECIFIED (0):
                Unspecified function calling mode. This value
                should not be used.
            AUTO (1):
                Default model behavior, model decides to
                predict either a function call or a natural
                language response.
            ANY (2):
                Model is constrained to always predicting a function call
                only. If "allowed_function_names" are set, the predicted
                function call will be limited to any one of
                "allowed_function_names", else the predicted function call
                will be any one of the provided "function_declarations".
            NONE (3):
                Model will not predict any function call.
                Model behavior is same as when not passing any
                function declarations.
        """
        MODE_UNSPECIFIED = 0
        AUTO = 1
        ANY = 2
        NONE = 3

    mode: Mode = proto.Field(
        proto.ENUM,
        number=1,
        enum=Mode,
    )
    allowed_function_names: MutableSequence[str] = proto.RepeatedField(
        proto.STRING,
        number=2,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
