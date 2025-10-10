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
"""System tests for reasoning engines."""
import pytest
import time
import sys
import datetime
from google import auth
import google.cloud.aiplatform
import vertexai
from google.cloud import trace_v1
from google.adk.sessions import in_memory_session_service
from google.protobuf.timestamp_pb2 import Timestamp
from tests.system.aiplatform import e2e_base
from vertexai import agent_engines

_BLOB_FILENAME = agent_engines._agent_engines._BLOB_FILENAME
_CANNED_AGENT_RESPONSE = "Hello agent"


# Class definition needs to be in a function, to not pull in entire testing module as a dependency, when pickling this class.
def adk_agent_no_dependencies():
    from google.adk.agents import base_agent

    class AdkAgentNoDependencies(base_agent.BaseAgent):
        async def _run_async_impl(self, ctx):
            from google.adk.events import event
            from google.genai import types

            yield event.Event(
                invocation_id=ctx.invocation_id,
                author="agent",
                content=types.Content(
                    role="agent", parts=[types.Part(text=_CANNED_AGENT_RESPONSE)]
                ),
            )

    return AdkAgentNoDependencies(name="test_agent")


@pytest.mark.usefixtures(
    "prepare_staging_bucket", "delete_staging_bucket", "tear_down_resources"
)
class TestAgentEngines(e2e_base.TestEndToEnd):
    """System tests for reasoning engines."""

    _temp_prefix = "test-reasoning-engine"

    @pytest.mark.asyncio
    async def test_adk_template(self, shared_state):
        # Avoid import errors template when pickling the template.
        sys.modules["google.cloud.aiplatform.aiplatform"] = google.cloud.aiplatform
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        vertexai.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
            credentials=credentials,
        )

        app = agent_engines.AdkApp(
            agent=adk_agent_no_dependencies(),
            enable_tracing=True,
            session_service_builder=in_memory_session_service.InMemorySessionService,
        )
        agent = agent_engines.AgentEngine.create(
            agent_engine=app,
            requirements=["google-cloud-aiplatform[agent_engines,adk]"],
            display_name="test-display-name",
            description="test-description",
            gcs_dir_name="test-gcs-dir-name",
        )
        shared_state.setdefault("resources", [])
        shared_state["resources"].append(agent)  # Deletion at teardown.

        resp = await agent.async_stream_query(
            message="Hello", user_id="test-user"
        ).__anext__()
        assert resp["content"]["parts"][0]["text"] == _CANNED_AGENT_RESPONSE

        traces = []
        trace_query_attempts = 10
        trace_query_end_time = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(minutes=1)
        trace_query_start_time = trace_query_end_time - datetime.timedelta(minutes=2)
        trace_client = trace_v1.TraceServiceClient()
        for _ in range(trace_query_attempts):
            traces = trace_client.list_traces(
                request=trace_v1.ListTracesRequest(
                    project_id=e2e_base._PROJECT,
                    start_time=Timestamp().FromDatetime(dt=trace_query_start_time),
                    end_time=Timestamp().FromDatetime(dt=trace_query_end_time),
                )
            )
            traces = list(traces)
            if len(traces) > 0:
                break
            time.sleep(5)

        assert len(traces) > 0
