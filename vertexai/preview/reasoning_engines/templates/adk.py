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

import asyncio
import queue
import threading


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
        from google.adk.sessions import BaseSessionService

        BaseSessionService = BaseSessionService
    except (ImportError, AttributeError):
        BaseSessionService = Any

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


def get_adk_major_version() -> int:
    """Get the major version of google-adk."""
    try:
        from google.adk import version

        return int(version.__version__.split(".")[0])
    except ImportError:
        return 0


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
        result = {}
        if self.events:
            result["events"] = []
            for event in self.events:
                event_dict = event.model_dump(exclude_none=True)
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


class AdkApp:
    """An ADK Application."""

    agent_framework = "google-adk"

    def __init__(
        self,
        *,
        agent: "BaseAgent",
        enable_tracing: bool = False,
        session_service_builder: Optional[Callable[..., "BaseSessionService"]] = None,
        artifact_service_builder: Optional[Callable[..., "BaseArtifactService"]] = None,
        memory_service_builder: Optional[Callable[..., "BaseMemoryService"]] = None,
        env_vars: Optional[Dict[str, str]] = None,
    ):
        """An ADK Application."""
        from google.cloud.aiplatform import initializer

        adk_major_version = get_adk_major_version()
        if adk_major_version < 1:
            msg = (
                f"Unsupported google-adk major version: {adk_major_version}, "
                "please use google-adk>=1.0.0 for AdkApp deployment."
            )
            raise ValueError(msg)

        self._tmpl_attrs: Dict[str, Any] = {
            "project": initializer.global_config.project,
            "location": initializer.global_config.location,
            "agent": agent,
            "enable_tracing": enable_tracing,
            "session_service_builder": session_service_builder,
            "artifact_service_builder": artifact_service_builder,
            "memory_service_builder": memory_service_builder,
            "app_name": _DEFAULT_APP_NAME,
            "env_vars": env_vars or {},
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

        return AdkApp(
            agent=copy.deepcopy(self._tmpl_attrs.get("agent")),
            enable_tracing=self._tmpl_attrs.get("enable_tracing"),
            session_service_builder=self._tmpl_attrs.get("session_service_builder"),
            artifact_service_builder=self._tmpl_attrs.get("artifact_service_builder"),
            memory_service_builder=self._tmpl_attrs.get("memory_service_builder"),
            env_vars=self._tmpl_attrs.get("env_vars"),
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
            self._tmpl_attrs["instrumentor"] = _default_instrumentor_builder(
                project_id=project
            )
        for key, value in self._tmpl_attrs.get("env_vars").items():
            os.environ[key] = value
        if "GOOGLE_CLOUD_AGENT_ENGINE_ID" in os.environ:
            self._tmpl_attrs["app_name"] = os.environ.get(
                "GOOGLE_CLOUD_AGENT_ENGINE_ID",
                self._tmpl_attrs.get("app_name"),
            )

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
            )
        else:
            self._tmpl_attrs["session_service"] = InMemorySessionService()

        memory_service_builder = self._tmpl_attrs.get("memory_service_builder")
        if memory_service_builder:
            self._tmpl_attrs["memory_service"] = memory_service_builder()
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
            agent=self._tmpl_attrs.get("agent"),
            session_service=self._tmpl_attrs.get("in_memory_session_service"),
            artifact_service=self._tmpl_attrs.get("in_memory_artifact_service"),
            memory_service=self._tmpl_attrs.get("in_memory_memory_service"),
            app_name=self._tmpl_attrs.get("app_name"),
        )

    def stream_query(
        self,
        *,
        message: Union[str, Dict[str, Any]],
        user_id: str,
        session_id: Optional[str] = None,
        **kwargs,
    ):
        """Streams responses from the ADK application in response to a message.

        Args:
            message (Union[str, Dict[str, Any]]):
                Required. The message to stream responses for.
            user_id (str):
                Required. The ID of the user.
            session_id (str):
                Optional. The ID of the session. If not provided, a new
                session will be created for the user.
            **kwargs (dict[str, Any]):
                Optional. Additional keyword arguments to pass to the
                runner.

        Yields:
            The output of querying the ADK application.
        """
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
            session = self.create_session(user_id=user_id)
            session_id = session.id
        for event in self._tmpl_attrs.get("runner").run(
            user_id=user_id, session_id=session_id, new_message=content, **kwargs
        ):
            yield event.model_dump(exclude_none=True)

    async def async_stream_query(
        self,
        *,
        message: Union[str, Dict[str, Any]],
        user_id: str,
        session_id: Optional[str] = None,
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
            **kwargs (dict[str, Any]):
                Optional. Additional keyword arguments to pass to the
                runner.

        Yields:
            Event dictionaries asynchronously.
        """
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

        events_async = self._tmpl_attrs.get("runner").run_async(
            user_id=user_id, session_id=session_id, new_message=content, **kwargs
        )

        async for event in events_async:
            # Yield the event data as a dictionary
            yield event.model_dump(exclude_none=True)

    def streaming_agent_run_with_events(self, request_json: str):
        import json
        from google.genai import types

        event_queue = queue.Queue(maxsize=1)

        async def _invoke_agent_async():
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
                for event in self._tmpl_attrs.get("in_memory_runner").run(
                    user_id=request.user_id,
                    session_id=session.id,
                    new_message=message_for_agent,
                ):
                    converted_event = await self._convert_response_events(
                        user_id=request.user_id,
                        session_id=session.id,
                        events=[event],
                        artifact_service=self._tmpl_attrs.get(
                            "in_memory_artifact_service"
                        ),
                    )
                    event_queue.put(converted_event)
            finally:
                await self._tmpl_attrs.get("in_memory_session_service").delete_session(
                    app_name=self._tmpl_attrs.get("app_name"),
                    user_id=request.user_id,
                    session_id=session.id,
                )

        def _asyncio_thread_main():
            try:
                asyncio.run(_invoke_agent_async())
            except RuntimeError as e:
                event_queue.put(e)
            finally:
                # Use None as a sentinel to stop the main thread.
                event_queue.put(None)

        thread = threading.Thread(target=_asyncio_thread_main)
        thread.start()

        try:
            while True:
                event = event_queue.get()
                if event is None:
                    break
                if isinstance(event, RuntimeError):
                    raise event
                yield event
        finally:
            thread.join()

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

    def get_session(
        self,
        *,
        user_id: str,
        session_id: str,
        **kwargs,
    ):
        """Get a session for the given user."""
        event_queue = queue.Queue(maxsize=1)

        async def _invoke_async_get_session():
            return await self.async_get_session(
                user_id=user_id, session_id=session_id, **kwargs
            )

        def _asyncio_thread_main():
            try:
                result = asyncio.run(_invoke_async_get_session())
                event_queue.put(result)
            except RuntimeError as e:
                event_queue.put(e)

        thread = threading.Thread(target=_asyncio_thread_main)
        thread.start()

        # Wait for the thread to finish
        thread.join()
        try:
            outcome = event_queue.get(timeout=10)
        except queue.Empty:
            raise RuntimeError(
                "Session not found. Please create it using .create_session()"
            ) from None
        if isinstance(outcome, RuntimeError):
            raise outcome from None
        return outcome

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

    def list_sessions(self, *, user_id: str, **kwargs):
        """List sessions for the given user."""
        event_queue = queue.Queue()

        async def _invoke_async_list_sessions():
            try:
                response = await self.async_list_sessions(user_id=user_id, **kwargs)
                event_queue.put(response)
            except RuntimeError as e:
                event_queue.put(e)

        def _asyncio_thread_main():
            try:
                asyncio.run(_invoke_async_list_sessions())
            finally:
                event_queue.put(None)

        thread = threading.Thread(target=_asyncio_thread_main)
        thread.start()
        # Wait for the thread to finish
        thread.join()
        try:
            return event_queue.get(timeout=10)
        except queue.Empty:
            raise RuntimeError("Failed to list sessions.") from None

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

    def create_session(
        self,
        *,
        user_id: str,
        session_id: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Creates a new session."""
        event_queue = queue.Queue(maxsize=1)

        async def _invoke_async_create_session():
            return await self.async_create_session(
                user_id=user_id,
                session_id=session_id,
                state=state,
                **kwargs,
            )

        def _asyncio_thread_main():
            try:
                result = asyncio.run(_invoke_async_create_session())
                event_queue.put(result)
            except RuntimeError as e:
                event_queue.put(e)

        thread = threading.Thread(target=_asyncio_thread_main)
        thread.start()
        # Wait for the thread to finish
        thread.join()

        try:
            outcome = event_queue.get(timeout=10)
        except queue.Empty:
            raise RuntimeError("Failed to create session.") from None
        if isinstance(outcome, RuntimeError):
            raise outcome from None
        return outcome

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

    def delete_session(
        self,
        *,
        user_id: str,
        session_id: str,
        **kwargs,
    ):
        """Deletes a session for the given user."""
        event_queue = queue.Queue(maxsize=1)

        async def _invoke_async_delete_session():
            await self.async_delete_session(
                user_id=user_id, session_id=session_id, **kwargs
            )

        def _asyncio_thread_main():
            try:
                asyncio.run(_invoke_async_delete_session())
                event_queue.put(None)
            except RuntimeError as e:
                event_queue.put(e)

        thread = threading.Thread(target=_asyncio_thread_main)
        thread.start()
        # Wait for the thread to finish
        thread.join()

        outcome = event_queue.get(timeout=10)
        if isinstance(outcome, RuntimeError):
            raise outcome from None

    def register_operations(self) -> Dict[str, List[str]]:
        """Registers the operations of the ADK application."""
        return {
            "": [
                "get_session",
                "list_sessions",
                "create_session",
                "delete_session",
            ],
            "async": [
                "async_get_session",
                "async_list_sessions",
                "async_create_session",
                "async_delete_session",
            ],
            "stream": ["stream_query", "streaming_agent_run_with_events"],
            "async_stream": ["async_stream_query"],
        }
