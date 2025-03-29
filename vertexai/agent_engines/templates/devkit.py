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
from typing import Any, Callable, Dict, List, Mapping, Optional


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
            "because not all packages for tracing have been installed"
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


class DevkitAgent:
    def __init__(
        self,
        runner_builder: Optional[Callable[..., Any]] = None,
        runner_kwargs: Optional[Mapping[str, Any]] = None,
        enable_tracing: bool = False,
        instrumentor_builder: Optional[Callable[..., Any]] = None,
        **kwargs,
    ):
        """An AgentDevkit LLMAgent."""
        from google.cloud.aiplatform import initializer

        self._tmpl_attrs: dict[str, Any] = {
            "project": initializer.global_config.project,
            "location": initializer.global_config.location,
            "runner_builder": runner_builder,
            "runner_kwargs": runner_kwargs or {},
            "enable_tracing": enable_tracing,
            "instrumentor_builder": instrumentor_builder,
            "api_endpoint": initializer.global_config.api_endpoint,
            "agent_kwargs": {},
        }
        for k, v in kwargs.items():
            self._tmpl_attrs["agent_kwargs"][k] = v

    def clone(self):
        return DevkitAgent(
            runner_builder=self._tmpl_attrs.get("runner_builder"),
            runner_kwargs=self._tmpl_attrs.get("runner_kwargs"),
            **self._tmpl_attrs.get("agent_kwargs"),
        )

    def set_up(self):
        """Sets up the DevkitLlmAgent."""
        import os
        from google.adk.runners import Runner
        from google.adk.agents import Agent
        from google.adk.artifacts import InMemoryArtifactService

        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
        os.environ["GOOGLE_CLOUD_PROJECT"] = self._tmpl_attrs.get("project")
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

        self._tmpl_attrs["artifact_service"] = InMemoryArtifactService()
        if "GOOGLE_CLOUD_AGENT_ENGINE_ID" in os.environ:
            from google.adk.sessions import VertexAiSessionService
            self._tmpl_attrs["session_service"] = VertexAiSessionService(
                project=self._tmpl_attrs.get("project"),
                location=location,
            )
            api_endpoint = self._tmpl_attrs.get(
                "api_endpoint",
                f"{location}-aiplatform.googleapis.com",
            )
            self._tmpl_attrs["session_service"].api_client._http_options["base_url"] = (
                f'https://{api_endpoint}'
            )
            self._tmpl_attrs["agent_engine_id"] = os.environ.get(
                "GOOGLE_CLOUD_AGENT_ENGINE_ID"
            )
        else:
            from google.adk.sessions import InMemorySessionService
            self._tmpl_attrs["session_service"] = InMemorySessionService()
        app_name = self._tmpl_attrs.get(
            "agent_engine_id",
            self._tmpl_attrs.get("runner_kwargs", {}).get("app_name", "test-app"),
        )
        self._tmpl_attrs["runner"] = Runner(
            agent=Agent(**self._tmpl_attrs.get("agent_kwargs")),
            session_service=self._tmpl_attrs.get("session_service"),
            artifact_service=self._tmpl_attrs.get("artifact_service"),
            app_name=app_name,
            **self._tmpl_attrs.get("runner_kwargs"),
        )

    def stream_query(
        self,
        *,
        message: str,
        user_id: str,
        session_id: str,
        **kwargs,
    ):
        from google.genai import types
        content = types.Content(role='user', parts=[types.Part(text=message)])
        if not self._tmpl_attrs.get("runner"):
            self.set_up()
        for event in self._tmpl_attrs.get("runner").run(
            user_id=user_id, session_id=session_id, new_message=content, **kwargs
        ):
            if event.content:
                yield event.content.model_dump(exclude_none=True)

    def get_session(
        self,
        *,
        user_id: str,
        session_id: str,
        **kwargs,
    ):
        if not self._tmpl_attrs.get("session_service"):
            self.set_up()
        session = self._tmpl_attrs.get("session_service").get_session(
            app_name=self._tmpl_attrs.get("agent_engine_id", "test-app"),
            user_id=user_id,
            session_id=session_id,
            **kwargs,
        )
        if not session:
            raise Exception("Session not found. Please create it using .create_session()")
        return session

    def list_sessions(self, *, user_id: str, **kwargs):
        if not self._tmpl_attrs.get("session_service"):
            self.set_up()
        return self._tmpl_attrs.get("session_service").list_sessions(
            app_name=self._tmpl_attrs.get("agent_engine_id", "test-app"),
            user_id=user_id,
            **kwargs,
        )

    def create_session(
        self,
        *,
        user_id: str,
        session_id: Optional[str] = None,
        state: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        if not self._tmpl_attrs.get("session_service"):
            self.set_up()
        session = self._tmpl_attrs.get("session_service").create_session(
            app_name=self._tmpl_attrs.get("agent_engine_id", "test-app"),
            user_id=user_id,
            session_id=session_id,
            state=state,
            **kwargs,
        )
        return session

    def delete_session(
        self,
        *,
        user_id: str,
        session_id: str,
        **kwargs,
    ):
        if not self._tmpl_attrs.get("session_service"):
            self.set_up()
        self._tmpl_attrs.get("session_service").delete_session(
            app_name=self._tmpl_attrs.get("agent_engine_id", "test-app"),
            user_id=user_id,
            session_id=session_id,
            **kwargs,
        )

    def list_events(
        self,
        *,
        user_id: str,
        session_id: str,
        **kwargs,
    ):
        if not self._tmpl_attrs.get("session_service"):
            self.set_up()
        events = self._tmpl_attrs.get("session_service").list_events(
            app_name=self._tmpl_attrs.get("agent_engine_id", "test-app"),
            user_id=user_id,
            session_id=session_id,
        )
        return events

    def register_operations(self) -> Dict[str, List[str]]:
        return {
            "": [
                "get_session",
                "list_sessions",
                "create_session",
                "delete_session",
                "list_events",
            ],
            "stream": ["stream_query"],
        }
