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
import dataclasses
import inspect
import json
import types
import typing
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Union

import proto

from google.cloud.aiplatform import base
from google.api import httpbody_pb2
from google.protobuf import struct_pb2
from google.protobuf import json_format

try:
    # For LangChain templates, they might not import langchain_core and get
    #   PydanticUserError: `query` is not fully defined; you should define
    #   `RunnableConfig`, then call `query.model_rebuild()`.
    import langchain_core.runnables.config

    RunnableConfig = langchain_core.runnables.config.RunnableConfig
except ImportError:
    RunnableConfig = Any

JsonDict = Dict[str, Any]

_LOGGER = base.Logger(__name__)


def to_proto(
    obj: Union[JsonDict, proto.Message],
    message: Optional[proto.Message] = None,
) -> proto.Message:
    """Parses a JSON-like object into a message.

    If the object is already a message, this will return the object as-is. If
    the object is a JSON Dict, this will parse and merge the object into the
    message.

    Args:
        obj (Union[dict[str, Any], proto.Message]):
            Required. The object to convert to a proto message.
        message (proto.Message):
            Optional. A protocol buffer message to merge the obj into. It
            defaults to Struct() if unspecified.

    Returns:
        proto.Message: The same message passed as argument.
    """
    if message is None:
        message = struct_pb2.Struct()
    if isinstance(obj, (proto.Message, struct_pb2.Struct)):
        return obj
    try:
        json_format.ParseDict(obj, message._pb)
    except AttributeError:
        json_format.ParseDict(obj, message)
    return message


def to_dict(message: proto.Message) -> JsonDict:
    """Converts the contents of the protobuf message to JSON format.

    Args:
        message (proto.Message):
            Required. The proto message to be converted to a JSON dictionary.

    Returns:
        dict[str, Any]: A dictionary containing the contents of the proto.
    """
    try:
        # Best effort attempt to convert the message into a JSON dictionary.
        result: JsonDict = json.loads(json_format.MessageToJson(message._pb))
    except AttributeError:
        result: JsonDict = json.loads(json_format.MessageToJson(message))
    return result


def dataclass_to_dict(obj: dataclasses.dataclass) -> JsonDict:
    """Converts a dataclass to a JSON dictionary.

    Args:
        obj (dataclasses.dataclass):
            Required. The dataclass to be converted to a JSON dictionary.

    Returns:
        dict[str, Any]: A dictionary containing the contents of the dataclass.
    """
    return json.loads(json.dumps(dataclasses.asdict(obj)))


def yield_parsed_json(body: httpbody_pb2.HttpBody) -> Iterable[Any]:
    """Converts the contents of the httpbody message to JSON format.

    Args:
        body (httpbody_pb2.HttpBody):
            Required. The httpbody body to be converted to a JSON.

    Yields:
        Any: A JSON object or the original body if it is not JSON or None.
    """
    content_type = getattr(body, "content_type", None)
    data = getattr(body, "data", None)

    if content_type is None or data is None or "application/json" not in content_type:
        yield body
        return

    try:
        utf8_data = data.decode("utf-8")
    except Exception as e:
        _LOGGER.warning(f"Failed to decode data: {data}. Exception: {e}")
        yield body
        return

    if not utf8_data:
        yield None
        return

    # Handle the case of multiple dictionaries delimited by newlines.
    for line in utf8_data.split("\n"):
        if line:
            try:
                line = json.loads(line)
            except Exception as e:
                _LOGGER.warning(f"failed to parse json: {line}. Exception: {e}")
            yield line


def generate_schema(
    f: Callable[..., Any],
    *,
    schema_name: Optional[str] = None,
    descriptions: Mapping[str, str] = {},
    required: Sequence[str] = [],
) -> JsonDict:
    """Generates the OpenAPI Schema for a callable object.

    Only positional and keyword arguments of the function `f` will be supported
    in the OpenAPI Schema that is generated. I.e. `*args` and `**kwargs` will
    not be present in the OpenAPI schema returned from this function. For those
    cases, you can either include it in the docstring for `f`, or modify the
    OpenAPI schema returned from this function to include additional arguments.

    Args:
        f (Callable):
            Required. The function to generate an OpenAPI Schema for.
        schema_name (str):
            Optional. The name for the OpenAPI schema. If unspecified, the name
            of the Callable will be used.
        descriptions (Mapping[str, str]):
            Optional. A `{name: description}` mapping for annotating input
            arguments of the function with user-provided descriptions. It
            defaults to an empty dictionary (i.e. there will not be any
            description for any of the inputs).
        required (Sequence[str]):
            Optional. For the user to specify the set of required arguments in
            function calls to `f`. If specified, it will be automatically
            inferred from `f`.

    Returns:
        dict[str, Any]: The OpenAPI Schema for the function `f` in JSON format.
    """
    pydantic = _import_pydantic_or_raise()
    defaults = dict(inspect.signature(f).parameters)
    fields_dict = {
        name: (
            # 1. We infer the argument type here: use Any rather than None so
            # it will not try to auto-infer the type based on the default value.
            (param.annotation if param.annotation != inspect.Parameter.empty else Any),
            pydantic.Field(
                # 2. We do not support default values for now.
                # default=(
                #     param.default if param.default != inspect.Parameter.empty
                #     else None
                # ),
                # 3. We support user-provided descriptions.
                description=descriptions.get(name, None),
            ),
        )
        for name, param in defaults.items()
        # We do not support *args or **kwargs
        if param.kind
        in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
            inspect.Parameter.POSITIONAL_ONLY,
        )
    }
    parameters = pydantic.create_model(f.__name__, **fields_dict).schema()
    # Postprocessing
    # 4. Suppress unnecessary title generation:
    #    * https://github.com/pydantic/pydantic/issues/1051
    #    * http://cl/586221780
    parameters.pop("title", "")
    for name, function_arg in parameters.get("properties", {}).items():
        function_arg.pop("title", "")
        annotation = defaults[name].annotation
        # 5. Nullable fields:
        #     * https://github.com/pydantic/pydantic/issues/1270
        #     * https://stackoverflow.com/a/58841311
        #     * https://github.com/pydantic/pydantic/discussions/4872
        if typing.get_origin(annotation) is Union and type(None) in typing.get_args(
            annotation
        ):
            # for "typing.Optional" arguments, function_arg might be a
            # dictionary like
            #
            #   {'anyOf': [{'type': 'integer'}, {'type': 'null'}]
            for schema in function_arg.pop("anyOf", []):
                schema_type = schema.get("type")
                if schema_type and schema_type != "null":
                    function_arg["type"] = schema_type
                    break
            function_arg["nullable"] = True
    # 6. Annotate required fields.
    if required:
        # We use the user-provided "required" fields if specified.
        parameters["required"] = required
    else:
        # Otherwise we infer it from the function signature.
        parameters["required"] = [
            k
            for k in defaults
            if (
                defaults[k].default == inspect.Parameter.empty
                and defaults[k].kind
                in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY,
                    inspect.Parameter.POSITIONAL_ONLY,
                )
            )
        ]
    schema = dict(name=f.__name__, description=f.__doc__, parameters=parameters)
    if schema_name:
        schema["name"] = schema_name
    return schema


def is_noop_or_proxy_tracer_provider(tracer_provider) -> bool:
    """Returns True if the tracer_provider is Proxy or NoOp."""
    opentelemetry = _import_opentelemetry_or_warn()
    ProxyTracerProvider = opentelemetry.trace.ProxyTracerProvider
    NoOpTracerProvider = opentelemetry.trace.NoOpTracerProvider
    return isinstance(tracer_provider, (NoOpTracerProvider, ProxyTracerProvider))


def _import_cloud_storage_or_raise() -> types.ModuleType:
    """Tries to import the Cloud Storage module."""
    try:
        from google.cloud import storage
    except ImportError as e:
        raise ImportError(
            "Cloud Storage is not installed. Please call "
            "'pip install google-cloud-aiplatform[reasoningengine]'."
        ) from e
    return storage


def _import_cloudpickle_or_raise() -> types.ModuleType:
    """Tries to import the cloudpickle module."""
    try:
        import cloudpickle  # noqa:F401
    except ImportError as e:
        raise ImportError(
            "cloudpickle is not installed. Please call "
            "'pip install google-cloud-aiplatform[reasoningengine]'."
        ) from e
    return cloudpickle


def _import_pydantic_or_raise() -> types.ModuleType:
    """Tries to import the pydantic module."""
    try:
        import pydantic

        _ = pydantic.Field
    except AttributeError:
        from pydantic import v1 as pydantic
    except ImportError as e:
        raise ImportError(
            "pydantic is not installed. Please call "
            "'pip install google-cloud-aiplatform[reasoningengine]'."
        ) from e
    return pydantic


def _import_opentelemetry_or_warn() -> Optional[types.ModuleType]:
    """Tries to import the opentelemetry module."""
    try:
        import opentelemetry  # noqa:F401

        return opentelemetry
    except ImportError:
        _LOGGER.warning(
            "opentelemetry-sdk is not installed. Please call "
            "'pip install google-cloud-aiplatform[reasoningengine]'."
        )
    return None


def _import_opentelemetry_sdk_trace_or_warn() -> Optional[types.ModuleType]:
    """Tries to import the opentelemetry.sdk.trace module."""
    try:
        import opentelemetry.sdk.trace  # noqa:F401

        return opentelemetry.sdk.trace
    except ImportError:
        _LOGGER.warning(
            "opentelemetry-sdk is not installed. Please call "
            "'pip install google-cloud-aiplatform[reasoningengine]'."
        )
    return None


def _import_cloud_trace_v2_or_warn() -> Optional[types.ModuleType]:
    """Tries to import the google.cloud.trace_v2 module."""
    try:
        import google.cloud.trace_v2

        return google.cloud.trace_v2
    except ImportError:
        _LOGGER.warning(
            "google-cloud-trace is not installed. Please call "
            "'pip install google-cloud-aiplatform[reasoningengine]'."
        )
    return None


def _import_cloud_trace_exporter_or_warn() -> Optional[types.ModuleType]:
    """Tries to import the opentelemetry.exporter.cloud_trace module."""
    try:
        import opentelemetry.exporter.cloud_trace  # noqa:F401

        return opentelemetry.exporter.cloud_trace
    except ImportError:
        _LOGGER.warning(
            "opentelemetry-exporter-gcp-trace is not installed. Please "
            "call 'pip install google-cloud-aiplatform[langchain]'."
        )
    return None


def _import_openinference_langchain_or_warn() -> Optional[types.ModuleType]:
    """Tries to import the openinference.instrumentation.langchain module."""
    try:
        import openinference.instrumentation.langchain  # noqa:F401

        return openinference.instrumentation.langchain
    except ImportError:
        _LOGGER.warning(
            "openinference-instrumentation-langchain is not installed. Please "
            "call 'pip install google-cloud-aiplatform[langchain]'."
        )
    return None


def _import_openinference_autogen_or_warn() -> Optional[types.ModuleType]:
    """Tries to import the openinference.instrumentation.autogen module."""
    try:
        import openinference.instrumentation.autogen  # noqa:F401

        return openinference.instrumentation.autogen
    except ImportError:
        _LOGGER.warning(
            "openinference-instrumentation-autogen is not installed. Please "
            "call 'pip install openinference-instrumentation-autogen'."
        )
    return None


def _import_autogen_tools_or_warn() -> Optional[types.ModuleType]:
    """Tries to import the autogen.tools module."""
    try:
        from autogen import tools

        return tools
    except ImportError:
        _LOGGER.warning(
            "autogen.tools is not installed. Please call: `pip install ag2[tools]`"
        )
    return None
