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
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterable,
    Callable,
    Dict,
    List,
    Optional,
    Union,
)

if TYPE_CHECKING:
    try:
        from google.adk.events.event import Event

        Event = Event
    except (ImportError, AttributeError):
        Event = Any

    try:
        from google.adk.agents import BaseAgent

        BaseAgent = BaseAgent
    except (ImportError, AttributeError):
        BaseAgent = Any

    try:
        from google.adk.plugins.base_plugin import BasePlugin

        BasePlugin = BasePlugin
    except (ImportError, AttributeError):
        BasePlugin = Any

    try:
        from google.adk.sessions import BaseSessionService

        BaseSessionService = BaseSessionService
    except (ImportError, AttributeError):
        BaseSessionService = Any

    try:
        from google.adk.sessions.session import Session

        Session = Session
    except (ImportError, AttributeError):
        Session = Any

    try:
        from google.adk.artifacts import BaseArtifactService

        BaseArtifactService = BaseArtifactService
    except (ImportError, AttributeError):
        BaseArtifactService = Any

    try:
        from google.adk.memory import BaseMemoryService

        BaseMemoryService = BaseMemoryService
    except (ImportError, AttributeError):
        BaseMemoryService = Any

    try:
        from opentelemetry.sdk import trace

        TracerProvider = trace.TracerProvider
        SpanProcessor = trace.SpanProcessor
        SynchronousMultiSpanProcessor = trace.SynchronousMultiSpanProcessor
    except ImportError:
        TracerProvider = Any
        SpanProcessor = Any
        SynchronousMultiSpanProcessor = Any


_DEFAULT_APP_NAME = "default-app-name"
_DEFAULT_USER_ID = "default-user-id"


def get_adk_version() -> Optional[str]:
    """Returns the version of the ADK package."""
    try:
        from google.adk import version

        return version.__version__
    except ImportError:
        return None


def is_version_sufficient(version_to_check: str) -> bool:
    """Compares the existing version of ADK with the required version.

    Args:
        version_to_check: The version string to check.

    Returns:
        True if the existing version is sufficient, False otherwise.
    """
    try:
        from packaging.version import parse

        return parse(get_adk_version()) >= parse(version_to_check)
    except (AttributeError, ImportError):
        return False


class _ArtifactVersion:
    def __init__(self, **kwargs):
        self.version: Optional[str] = kwargs.get("version")
        self.data = kwargs.get("data")

    def dump(self) -> Dict[str, Any]:
        result = {}
        if self.version:
            result["version"] = self.version
        if self.data:
            result["data"] = self.data
        return result


class _Artifact:
    def __init__(self, **kwargs):
        self.file_name: Optional[str] = kwargs.get("file_name")
        self.versions: List[_ArtifactVersion] = kwargs.get("versions")

    def dump(self) -> Dict[str, Any]:
        result = {}
        if self.file_name:
            result["file_name"] = self.file_name
        if self.versions:
            result["versions"] = [version.dump() for version in self.versions]
        return result


class _Authorization:
    def __init__(self, **kwargs):
        self.access_token: Optional[str] = kwargs.get("access_token") or kwargs.get(
            "accessToken"
        )


class _StreamRunRequest:
    """Request object for `streaming_agent_run_with_events` method."""

    def __init__(self, **kwargs):
        from google.adk.events.event import Event
        from google.genai import types

        self.message: Optional[types.Content] = kwargs.get("message")
        # The new message to be processed by the agent.

        self.events: Optional[List[Event]] = kwargs.get("events")
        # List of preceding events happened in the same session.

        self.artifacts: Optional[List[_Artifact]] = kwargs.get("artifacts")
        # List of artifacts belonging to the session.

        self.authorizations: Dict[str, _Authorization] = kwargs.get(
            "authorizations", {}
        )
        # The authorizations of the user, keyed by authorization ID.

        self.user_id: Optional[str] = kwargs.get("user_id", _DEFAULT_USER_ID)
        # The user ID.


class _StreamingRunResponse:
    """Response object for `streaming_agent_run_with_events` method.

    It contains the generated events together with the belonging artifacts.
    """

    def __init__(self, **kwargs):
        self.events: Optional[List["Event"]] = kwargs.get("events")
        # List of generated events.
        self.artifacts: Optional[List[_Artifact]] = kwargs.get("artifacts")
        # List of artifacts belonging to the session.

    def dump(self) -> Dict[str, Any]:
        from vertexai.agent_engines import _utils

        result = {}
        if self.events:
            result["events"] = []
            for event in self.events:
                event_dict = _utils.dump_event_for_json(event)
                event_dict["invocation_id"] = event_dict.get("invocation_id", "")
                result["events"].append(event_dict)
        if self.artifacts:
            result["artifacts"] = [artifact.dump() for artifact in self.artifacts]
        return result


def _default_instrumentor_builder(project_id: str):
    from vertexai.agent_engines import _utils

    cloud_trace_exporter = _utils._import_cloud_trace_exporter_or_warn()
    cloud_trace_v2 = _utils._import_cloud_trace_v2_or_warn()
    opentelemetry = _utils._import_opentelemetry_or_warn()
    opentelemetry_sdk_trace = _utils._import_opentelemetry_sdk_trace_or_warn()
    if all(
        (
            cloud_trace_exporter,
            cloud_trace_v2,
            opentelemetry,
            opentelemetry_sdk_trace,
        )
    ):
        import google.auth

        credentials, _ = google.auth.default()
        span_exporter = cloud_trace_exporter.CloudTraceSpanExporter(
            project_id=project_id,
            client=cloud_trace_v2.TraceServiceClient(
                credentials=credentials.with_quota_project(project_id),
            ),
        )
        span_processor = opentelemetry_sdk_trace.export.BatchSpanProcessor(
            span_exporter=span_exporter,
        )
        tracer_provider = opentelemetry.trace.get_tracer_provider()
        # Get the appropriate tracer provider:
        # 1. If _TRACER_PROVIDER is already set, use that.
        # 2. Otherwise, if the OTEL_PYTHON_TRACER_PROVIDER environment
        # variable is set, use that.
        # 3. As a final fallback, use _PROXY_TRACER_PROVIDER.
        # If none of the above is set, we log a warning, and
        # create a tracer provider.
        if not tracer_provider:
            from google.cloud.aiplatform import base

            _LOGGER = base.Logger(__name__)
            _LOGGER.warning(
                "No tracer provider. By default, "
                "we should get one of the following providers: "
                "OTEL_PYTHON_TRACER_PROVIDER, _TRACER_PROVIDER, "
                "or _PROXY_TRACER_PROVIDER."
            )
            tracer_provider = opentelemetry_sdk_trace.TracerProvider()
            opentelemetry.trace.set_tracer_provider(tracer_provider)
        # Avoids AttributeError:
        # 'ProxyTracerProvider' and 'NoOpTracerProvider' objects has no
        # attribute 'add_span_processor'.
        if _utils.is_noop_or_proxy_tracer_provider(tracer_provider):
            tracer_provider = opentelemetry_sdk_trace.TracerProvider()
            opentelemetry.trace.set_tracer_provider(tracer_provider)
        # Avoids OpenTelemetry client already exists error.
        _override_active_span_processor(
            tracer_provider,
            opentelemetry_sdk_trace.SynchronousMultiSpanProcessor(),
        )
        tracer_provider.add_span_processor(span_processor)
        return None
    else:
        from google.cloud.aiplatform import base

        _LOGGER = base.Logger(__name__)
        _LOGGER.warning(
            "enable_tracing=True but proceeding with tracing disabled "
            "because not all packages (i.e. `google-cloud-trace`, `opentelemetry-sdk`, "
            "`opentelemetry-exporter-gcp-trace`) for tracing have been installed"
        )
        return None


def _override_active_span_processor(
    tracer_provider: "TracerProvider",
    active_span_processor: "SynchronousMultiSpanProcessor",
):
    """Overrides the active span processor.

    When working with multiple LangchainAgents in the same environment,
    it's crucial to manage trace exports carefully.
    Each agent needs its own span processor tied to a unique project ID.
    While we add a new span processor for each agent, this can lead to
    unexpected behavior.
    For instance, with two agents linked to different projects, traces from the
    second agent might be sent to both projects.
    To prevent this and guarantee traces go to the correct project, we overwrite
    the active span processor whenever a new LangchainAgent is created.

    Args:
        tracer_provider (TracerProvider):
            The tracer provider to use for the project.
        active_span_processor (SynchronousMultiSpanProcessor):
            The active span processor overrides the tracer provider's
            active span processor.
    """
    if tracer_provider._active_span_processor:
        tracer_provider._active_span_processor.shutdown()
    tracer_provider._active_span_processor = active_span_processor


def _validate_run_config(run_config: Optional[Dict[str, Any]]):
    """Validates the run config."""
    from google.adk.agents.run_config import RunConfig

    if run_config is None:
        return None
    elif isinstance(run_config, Dict):
        return RunConfig.model_validate(run_config)
    raise TypeError("run_config must be a dictionary representing a RunConfig object.")


class AdkApp:
    """An ADK Application."""

    agent_framework = "google-adk"

    def __init__(
        self,
        *,
        agent: "BaseAgent",
        app_name: Optional[str] = None,
        plugins: Optional[List["BasePlugin"]] = None,
        enable_tracing: bool = False,
        session_service_builder: Optional[Callable[..., "BaseSessionService"]] = None,
        artifact_service_builder: Optional[Callable[..., "BaseArtifactService"]] = None,
        memory_service_builder: Optional[Callable[..., "BaseMemoryService"]] = None,
        instrumentor_builder: Optional[Callable[..., Any]] = None,
    ):
        """An ADK Application.

        See https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/develop/adk
        for details on how to develop ADK applications on Agent Engine.

        Args:
            agent (google.adk.agents.BaseAgent):
                Required. The ADK agent to run.
            app_name (str):
                Optional. The name of the ADK application. Defaults to
                "default-app-name" when running locally, and to the
                corresponding agent engine ID when deployed on Agent Engine.
            plugins (List[BasePlugin]):
                Optional. The plugins to use for the ADK application.
                Defaults to an empty list.
            enable_tracing (bool):
                Optional. Whether to enable tracing in Cloud Trace. Defaults to
                False.
            session_service_builder (Callable[..., BaseSessionService]):
                Optional. A callable that returns an ADK session service.
                Defaults to a callable that returns InMemorySessionService
                when running locally and VertexAiSessionService when running
                on Agent Engine.
            artifact_service_builder (Callable[..., BaseArtifactService]):
                Optional. A callable that returns an ADK artifact service.
                Defaults to a callable that returns InMemoryArtifactService.
            memory_service_builder (Callable[..., BaseMemoryService]):
                Optional. A callable that returns an ADK memory service.
                Defaults to a callable that returns InMemoryMemoryService
                when running locally and VertexAiMemoryBankService when running
                on Agent Engine.
            instrumentor_builder (Callable[..., Any]):
                Optional. Callable that returns a new instrumentor. This can be
                used for customizing the instrumentation logic of the Agent.
                If not provided, a default instrumentor builder will be used.
                This parameter is ignored if `enable_tracing` is False.
        """
        from google.cloud.aiplatform import initializer

        adk_version = get_adk_version()
        if not is_version_sufficient("1.5.0"):
            msg = (
                f"Unsupported google-adk version: {adk_version}, please use "
                "google-adk>=1.5.0 for AdkApp deployment on Agent Engine."
            )
            raise ValueError(msg)

        self._tmpl_attrs: Dict[str, Any] = {
            "project": initializer.global_config.project,
            "location": initializer.global_config.location,
            "agent": agent,
            "app_name": app_name,
            "plugins": plugins,
            "enable_tracing": enable_tracing,
            "session_service_builder": session_service_builder,
            "artifact_service_builder": artifact_service_builder,
            "memory_service_builder": memory_service_builder,
            "instrumentor_builder": instrumentor_builder,
        }

    async def _init_session(
        self,
        session_service: "BaseSessionService",
        artifact_service: "BaseArtifactService",
        request: _StreamRunRequest,
    ):
        """Initializes the session, and returns the session id."""
        from google.adk.events.event import Event
        import random

        session_state = None
        if request.authorizations:
            session_state = {}
            for auth_id, auth in request.authorizations.items():
                auth = _Authorization(**auth)
                session_state[f"temp:{auth_id}"] = auth.access_token

        session_id = f"temp_session_{random.randbytes(8).hex()}"
        session = await session_service.create_session(
            app_name=self._tmpl_attrs.get("app_name"),
            user_id=request.user_id,
            session_id=session_id,
            state=session_state,
        )
        if not session:
            raise RuntimeError("Create session failed.")
        if request.events:
            for event in request.events:
                await session_service.append_event(session, Event(**event))
        if request.artifacts:
            for artifact in request.artifacts:
                artifact = _Artifact(**artifact)
                for version_data in sorted(
                    artifact.versions, key=lambda x: x["version"]
                ):
                    version_data = _ArtifactVersion(**version_data)
                    saved_version = await artifact_service.save_artifact(
                        app_name=self._tmpl_attrs.get("app_name"),
                        user_id=request.user_id,
                        session_id=session_id,
                        filename=artifact.file_name,
                        artifact=version_data.data,
                    )
                    if saved_version != version_data.version:
                        from google.cloud.aiplatform import base

                        _LOGGER = base.Logger(__name__)
                        _LOGGER.debug(
                            "Artifact '%s' saved at version %s instead of %s",
                            artifact.file_name,
                            saved_version,
                            version_data.version,
                        )
        return session

    async def _convert_response_events(
        self,
        user_id: str,
        session_id: str,
        events: List["Event"],
        artifact_service: Optional["BaseArtifactService"],
    ) -> _StreamingRunResponse:
        """Converts the events to the streaming run response object."""
        import collections

        result = _StreamingRunResponse(events=events, artifacts=[])

        # Save the generated artifacts into the result object.
        artifact_versions = collections.defaultdict(list)
        for event in events:
            if event.actions and event.actions.artifact_delta:
                for key, version in event.actions.artifact_delta.items():
                    artifact_versions[key].append(version)

        for key, versions in artifact_versions.items():
            result.artifacts.append(
                _Artifact(
                    file_name=key,
                    versions=[
                        _ArtifactVersion(
                            version=version,
                            data=await artifact_service.load_artifact(
                                app_name=self._tmpl_attrs.get("app_name"),
                                user_id=user_id,
                                session_id=session_id,
                                filename=key,
                                version=version,
                            ),
                        )
                        for version in versions
                    ],
                )
            )

        return result.dump()

    def clone(self):
        """Returns a clone of the ADK application."""
        import copy

        return self.__class__(
            agent=copy.deepcopy(self._tmpl_attrs.get("agent")),
            enable_tracing=self._tmpl_attrs.get("enable_tracing"),
            app_name=self._tmpl_attrs.get("app_name"),
            plugins=self._tmpl_attrs.get("plugins"),
            session_service_builder=self._tmpl_attrs.get("session_service_builder"),
            artifact_service_builder=self._tmpl_attrs.get("artifact_service_builder"),
            memory_service_builder=self._tmpl_attrs.get("memory_service_builder"),
            instrumentor_builder=self._tmpl_attrs.get("instrumentor_builder"),
        )

    def set_up(self):
        """Sets up the ADK application."""
        import os
        from google.adk.runners import Runner
        from google.adk.sessions.in_memory_session_service import InMemorySessionService
        from google.adk.artifacts.in_memory_artifact_service import (
            InMemoryArtifactService,
        )
        from google.adk.memory.in_memory_memory_service import InMemoryMemoryService

        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
        project = self._tmpl_attrs.get("project")
        os.environ["GOOGLE_CLOUD_PROJECT"] = project
        location = self._tmpl_attrs.get("location")
        os.environ["GOOGLE_CLOUD_LOCATION"] = location
        if self._tmpl_attrs.get("enable_tracing"):
            instrumentor_builder = (
                self._tmpl_attrs.get("instrumentor_builder")
                or _default_instrumentor_builder
            )
            self._tmpl_attrs["instrumentor"] = instrumentor_builder(
                project_id=self._tmpl_attrs.get("project")
            )
        if not self._tmpl_attrs.get("app_name"):
            if "GOOGLE_CLOUD_AGENT_ENGINE_ID" in os.environ:
                self._tmpl_attrs["app_name"] = os.environ.get(
                    "GOOGLE_CLOUD_AGENT_ENGINE_ID",
                )
            else:
                self._tmpl_attrs["app_name"] = _DEFAULT_APP_NAME

        artifact_service_builder = self._tmpl_attrs.get("artifact_service_builder")
        if artifact_service_builder:
            self._tmpl_attrs["artifact_service"] = artifact_service_builder()
        else:
            self._tmpl_attrs["artifact_service"] = InMemoryArtifactService()

        session_service_builder = self._tmpl_attrs.get("session_service_builder")
        if session_service_builder:
            self._tmpl_attrs["session_service"] = session_service_builder()
        elif "GOOGLE_CLOUD_AGENT_ENGINE_ID" in os.environ:
            from google.adk.sessions.vertex_ai_session_service import (
                VertexAiSessionService,
            )

            self._tmpl_attrs["session_service"] = VertexAiSessionService(
                project=project,
                location=location,
                agent_engine_id=os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ID"),
            )
        else:
            self._tmpl_attrs["session_service"] = InMemorySessionService()

        memory_service_builder = self._tmpl_attrs.get("memory_service_builder")
        if memory_service_builder:
            self._tmpl_attrs["memory_service"] = memory_service_builder()
        elif "GOOGLE_CLOUD_AGENT_ENGINE_ID" in os.environ and is_version_sufficient(
            "1.5.0"
        ):
            from google.adk.memory.vertex_ai_memory_bank_service import (
                VertexAiMemoryBankService,
            )

            self._tmpl_attrs["memory_service"] = VertexAiMemoryBankService(
                project=project,
                location=location,
                agent_engine_id=os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ID"),
            )
        else:
            self._tmpl_attrs["memory_service"] = InMemoryMemoryService()

        self._tmpl_attrs["runner"] = Runner(
            agent=self._tmpl_attrs.get("agent"),
            session_service=self._tmpl_attrs.get("session_service"),
            artifact_service=self._tmpl_attrs.get("artifact_service"),
            memory_service=self._tmpl_attrs.get("memory_service"),
            app_name=self._tmpl_attrs.get("app_name"),
        )
        self._tmpl_attrs["in_memory_session_service"] = InMemorySessionService()
        self._tmpl_attrs["in_memory_artifact_service"] = InMemoryArtifactService()
        self._tmpl_attrs["in_memory_memory_service"] = InMemoryMemoryService()
        self._tmpl_attrs["in_memory_runner"] = Runner(
            app_name=self._tmpl_attrs.get("app_name"),
            agent=self._tmpl_attrs.get("agent"),
            plugins=self._tmpl_attrs.get("plugins"),
            session_service=self._tmpl_attrs.get("in_memory_session_service"),
            artifact_service=self._tmpl_attrs.get("in_memory_artifact_service"),
            memory_service=self._tmpl_attrs.get("in_memory_memory_service"),
        )

    async def async_stream_query(
        self,
        *,
        message: Union[str, Dict[str, Any]],
        user_id: str,
        session_id: Optional[str] = None,
        run_config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> AsyncIterable[Dict[str, Any]]:
        """Streams responses asynchronously from the ADK application.

        Args:
            message (str):
                Required. The message to stream responses for.
            user_id (str):
                Required. The ID of the user.
            session_id (str):
                Optional. The ID of the session. If not provided, a new
                session will be created for the user.
            run_config (Optional[Dict[str, Any]]):
                Optional. The run config to use for the query. If you want to
                pass in a `run_config` pydantic object, you can pass in a dict
                representing it as `run_config.model_dump(mode="json")`.
            **kwargs (dict[str, Any]):
                Optional. Additional keyword arguments to pass to the
                runner.

        Yields:
            Event dictionaries asynchronously.
        """
        from vertexai.agent_engines import _utils
        from google.genai import types

        if isinstance(message, Dict):
            content = types.Content.model_validate(message)
        elif isinstance(message, str):
            content = types.Content(role="user", parts=[types.Part(text=message)])
        else:
            raise TypeError(
                "message must be a string or a dictionary representing"
                " a Content object."
            )

        if not self._tmpl_attrs.get("runner"):
            self.set_up()
        if not session_id:
            session = await self.async_create_session(user_id=user_id)
            session_id = session.id

        run_config = _validate_run_config(run_config)
        if run_config:
            events_async = self._tmpl_attrs.get("runner").run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
                run_config=run_config,
                **kwargs,
            )
        else:
            events_async = self._tmpl_attrs.get("runner").run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
                **kwargs,
            )

        async for event in events_async:
            # Yield the event data as a dictionary
            yield _utils.dump_event_for_json(event)

    async def streaming_agent_run_with_events(self, request_json: str):
        """Streams responses asynchronously from the ADK application.

        In general, you should use `async_stream_query` instead, as it has a
        more structured API and works with the respective ADK services that
        you have defined for the AdkApp. This method is primarily meant for
        invocation from AgentSpace.

        Args:
            request_json (str):
                Required. The request to stream responses for.
        """

        import json
        from google.genai import types

        request = _StreamRunRequest(**json.loads(request_json))
        if not self._tmpl_attrs.get("in_memory_runner"):
            self.set_up()
        if not self._tmpl_attrs.get("artifact_service"):
            self.set_up()
        # Prepare the in-memory session.
        if not self._tmpl_attrs.get("in_memory_artifact_service"):
            self.set_up()
        if not self._tmpl_attrs.get("in_memory_session_service"):
            self.set_up()
        session = await self._init_session(
            session_service=self._tmpl_attrs.get("in_memory_session_service"),
            artifact_service=self._tmpl_attrs.get("in_memory_artifact_service"),
            request=request,
        )
        if not session:
            raise RuntimeError("Session initialization failed.")

        # Run the agent.
        message_for_agent = types.Content(**request.message)
        try:
            async for event in self._tmpl_attrs.get("in_memory_runner").run_async(
                user_id=request.user_id,
                session_id=session.id,
                new_message=message_for_agent,
            ):
                converted_event = await self._convert_response_events(
                    user_id=request.user_id,
                    session_id=session.id,
                    events=[event],
                    artifact_service=self._tmpl_attrs.get("in_memory_artifact_service"),
                )
                yield converted_event
        finally:
            await self._tmpl_attrs.get("in_memory_session_service").delete_session(
                app_name=self._tmpl_attrs.get("app_name"),
                user_id=request.user_id,
                session_id=session.id,
            )

    async def async_get_session(
        self,
        *,
        user_id: str,
        session_id: str,
        **kwargs,
    ):
        """Get a session for the given user.

        Args:
            user_id (str):
                Required. The ID of the user.
            session_id (str):
                Required. The ID of the session.
            **kwargs (dict[str, Any]):
                Optional. Additional keyword arguments to pass to the
                session service.

        Returns:
            Session: The session instance (if any). It returns None if the
            session is not found.

        Raises:
            RuntimeError: If the session is not found.
        """
        if not self._tmpl_attrs.get("session_service"):
            self.set_up()
        session = await self._tmpl_attrs.get("session_service").get_session(
            app_name=self._tmpl_attrs.get("app_name"),
            user_id=user_id,
            session_id=session_id,
            **kwargs,
        )
        if not session:
            raise RuntimeError(
                "Session not found. Please create it using .create_session()"
            )
        return session

    async def async_list_sessions(self, *, user_id: str, **kwargs):
        """List sessions for the given user.

        Args:
            user_id (str):
                Required. The ID of the user.
            **kwargs (dict[str, Any]):
                Optional. Additional keyword arguments to pass to the
                session service.

        Returns:
            ListSessionsResponse: The list of sessions.
        """
        if not self._tmpl_attrs.get("session_service"):
            self.set_up()
        return await self._tmpl_attrs.get("session_service").list_sessions(
            app_name=self._tmpl_attrs.get("app_name"),
            user_id=user_id,
            **kwargs,
        )

    async def async_create_session(
        self,
        *,
        user_id: str,
        session_id: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Creates a new session.

        Args:
            user_id (str):
                Required. The ID of the user.
            session_id (str):
                Optional. The ID of the session. If not provided, an ID
                will be be generated for the session.
            state (dict[str, Any]):
                Optional. The initial state of the session.
            **kwargs (dict[str, Any]):
                Optional. Additional keyword arguments to pass to the
                session service.

        Returns:
            Session: The newly created session instance.
        """
        if not self._tmpl_attrs.get("session_service"):
            self.set_up()
        session = await self._tmpl_attrs.get("session_service").create_session(
            app_name=self._tmpl_attrs.get("app_name"),
            user_id=user_id,
            session_id=session_id,
            state=state,
            **kwargs,
        )
        return session

    async def async_delete_session(
        self,
        *,
        user_id: str,
        session_id: str,
        **kwargs,
    ):
        """Deletes a session for the given user.

        Args:
            user_id (str):
                Required. The ID of the user.
            session_id (str):
                Required. The ID of the session.
            **kwargs (dict[str, Any]):
                Optional. Additional keyword arguments to pass to the
                session service.
        """
        if not self._tmpl_attrs.get("session_service"):
            self.set_up()
        await self._tmpl_attrs.get("session_service").delete_session(
            app_name=self._tmpl_attrs.get("app_name"),
            user_id=user_id,
            session_id=session_id,
            **kwargs,
        )

    async def async_add_session_to_memory(
        self,
        *,
        session: Union["Session", Dict[str, Any]],
    ):
        """Generates memories.

        Args:
            session (Union[Session, Dict[str, Any]]):
                Required. The session to use for generating memories.
        """
        from google.adk.sessions.session import Session

        if isinstance(session, Dict):
            session = Session.model_validate(session)
        elif not isinstance(session, Session):
            raise TypeError("session must be a Session object.")
        if not session.events:
            # Get the latest version of the session in case it was updated.
            session = await self.async_get_session(
                user_id=session.user_id,
                session_id=session.id,
            )
        if not self._tmpl_attrs.get("memory_service"):
            self.set_up()
        return await self._tmpl_attrs.get("memory_service").add_session_to_memory(
            session=session,
        )

    async def async_search_memory(self, *, user_id: str, query: str):
        """Searches memories for the given user.

        Args:
            user_id: The id of the user.
            query: The query to match the memories on.

        Returns:
            A SearchMemoryResponse containing the matching memories.
        """
        if not self._tmpl_attrs.get("memory_service"):
            self.set_up()
        return await self._tmpl_attrs.get("memory_service").search_memory(
            app_name=self._tmpl_attrs.get("app_name"),
            user_id=user_id,
            query=query,
        )

    def register_operations(self) -> Dict[str, List[str]]:
        """Registers the operations of the ADK application."""
        return {
            "async": [
                "async_get_session",
                "async_list_sessions",
                "async_create_session",
                "async_delete_session",
                "async_add_session_to_memory",
                "async_search_memory",
            ],
            "async_stream": [
                "async_stream_query",
                "streaming_agent_run_with_events",
            ],
        }
