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

from collections.abc import AsyncIterator
import os
from typing import Any, Callable, Dict, List, Mapping, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    try:
        from a2a.server.request_handlers import RequestHandler
        from a2a.server.tasks import TaskStore
        from a2a.types import AgentCard, AgentSkill
        from a2a.server.agent_execution import AgentExecutor
        from a2a.server.context import ServerCallContext
        from a2a.types import (
            SendMessageRequest,
            CancelTaskRequest,
            GetTaskRequest,
            GetExtendedAgentCardRequest,
            SubscribeToTaskRequest,
            ListTasksRequest,
            ListTasksResponse,
            TaskPushNotificationConfig,
            GetTaskPushNotificationConfigRequest,
            ListTaskPushNotificationConfigsRequest,
            ListTaskPushNotificationConfigsResponse,
            DeleteTaskPushNotificationConfigRequest,
            Message,
            Task,
        )
        from a2a.server.events.event_queue import Event

        RequestHandler = RequestHandler
        TaskStore = TaskStore
        AgentCard = AgentCard
        AgentSkill = AgentSkill
        AgentExecutor = AgentExecutor
        ServerCallContext = ServerCallContext
        SendMessageRequest = SendMessageRequest
        CancelTaskRequest = CancelTaskRequest
        GetTaskRequest = GetTaskRequest
        GetExtendedAgentCardRequest = GetExtendedAgentCardRequest
        SubscribeToTaskRequest = SubscribeToTaskRequest
        ListTasksRequest = ListTasksRequest
        ListTasksResponse = ListTasksResponse
        TaskPushNotificationConfig = TaskPushNotificationConfig
        GetTaskPushNotificationConfigRequest = GetTaskPushNotificationConfigRequest
        ListTaskPushNotificationConfigsRequest = ListTaskPushNotificationConfigsRequest
        ListTaskPushNotificationConfigsResponse = (
            ListTaskPushNotificationConfigsResponse
        )
        DeleteTaskPushNotificationConfigRequest = (
            DeleteTaskPushNotificationConfigRequest
        )
        Message = Message
        Task = Task
        Event = Event
    except (ImportError, AttributeError):
        RequestHandler = Any
        TaskStore = Any
        AgentCard = Any
        AgentSkill = Any
        AgentExecutor = Any
        ServerCallContext = Any
        SendMessageRequest = Any
        CancelTaskRequest = Any
        GetTaskRequest = Any
        GetExtendedAgentCardRequest = Any
        SubscribeToTaskRequest = Any
        ListTasksRequest = Any
        ListTasksResponse = Any
        TaskPushNotificationConfig = Any
        GetTaskPushNotificationConfigRequest = Any
        ListTaskPushNotificationConfigsRequest = Any
        ListTaskPushNotificationConfigsResponse = Any
        DeleteTaskPushNotificationConfigRequest = Any
        Message = Any
        Task = Any
        Event = Any
        AgentExecutor = Any
        ServerCallContext = Any
        SendMessageRequest = Any
        CancelTaskRequest = Any
        GetTaskRequest = Any
        GetExtendedAgentCardRequest = Any
        SubscribeToTaskRequest = Any
        Message = Any
        Task = Any
        Event = Any


def create_agent_card(
    agent_name: Optional[str] = None,
    description: Optional[str] = None,
    skills: Optional[List["AgentSkill"]] = None,
    agent_card: Optional[Dict[str, Any]] = None,
    default_input_modes: Optional[List[str]] = None,
    default_output_modes: Optional[List[str]] = None,
    streaming: bool = False,
) -> "AgentCard":
    """Creates an AgentCard object.

    The function can be called in two ways:
    1. By providing the individual parameters: agent_name, description, and
    skills.
    2. By providing a single dictionary containing all the data.

    If a dictionary is provided, the other parameters are ignored.

    Args:
        agent_name (Optional[str]): The name of the agent.
        description (Optional[str]): A description of the agent.
        skills (Optional[List[AgentSkill]]): A list of AgentSkills.
        agent_card (Optional[Dict[str, Any]]): Agent Card as a dictionary.
        default_input_modes (Optional[List[str]]): A list of input modes, default
          to ["text/plain"].
        default_output_modes (Optional[List[str]]): A list of output modes,
          default to ["application/json"].
        streaming (bool): Whether to enable streaming for the agent. Defaults to
          False.

    Returns:
        AgentCard: A fully constructed AgentCard object.

    Raises:
        ValueError: If neither a dictionary nor the required parameters are
        provided.
    """
    # pylint: disable=g-import-not-at-top
    from a2a.types import AgentCard, AgentCapabilities, AgentInterface
    from a2a.utils.constants import TransportProtocol, PROTOCOL_VERSION_CURRENT

    # Check if a dictionary was provided.
    if agent_card:
        return AgentCard(**agent_card)

    # If no dictionary, use the individual parameters.
    elif agent_name and description and skills:
        return AgentCard(
            name=agent_name,
            description=description,
            version="1.0.0",
            default_input_modes=default_input_modes or ["text/plain"],
            default_output_modes=default_output_modes or ["application/json"],
            capabilities=AgentCapabilities(
                streaming=streaming, extended_agent_card=True
            ),
            skills=skills,
            supported_interfaces=[
                AgentInterface(
                    url="http://localhost:9999/",
                    protocol_binding=TransportProtocol.HTTP_JSON,
                    protocol_version=PROTOCOL_VERSION_CURRENT,
                )
            ],
        )

    # Raise an error if insufficient data is provided.
    else:
        raise ValueError(
            "Please provide either an agent_card or all of the required "
            "parameters (agent_name, description, and skills)."
        )


def default_a2a_agent() -> "A2aAgent":
    """Creates a default A2aAgent instance."""
    # pylint: disable=g-import-not-at-top
    from a2a.server.agent_execution import AgentExecutor, RequestContext
    from a2a.types import AgentSkill
    from a2a.server.events import EventQueue
    from a2a.helpers.proto_helpers import new_text_message

    skill = AgentSkill(
        id="hello_world",
        name="Returns hello world",
        description="just returns hello world",
        tags=["hello world"],
        examples=["hi", "hello world"],
    )
    agent_card = create_agent_card(
        agent_name="Hello World Agent",
        description="Just a hello world agent",
        skills=[skill],
    )

    class HelloWorldAgentExecutor(AgentExecutor):
        """Hello World Agent Executor."""

        def get_agent_response(self) -> str:
            return "Hello World"

        async def execute(
            self,
            context: RequestContext,
            event_queue: EventQueue,
        ) -> None:
            result = self.get_agent_response()
            await event_queue.enqueue_event(new_text_message(result))

        async def cancel(
            self, context: RequestContext, event_queue: EventQueue
        ) -> None:
            raise Exception("cancel not supported")

    return A2aAgent(
        agent_card=agent_card,
        agent_executor_builder=HelloWorldAgentExecutor,
    )


def _is_version_enabled(agent_card: "AgentCard", version: str) -> bool:
    """Checks if a specific version compatibility should be enabled for the A2aAgent."""
    # pylint: disable=g-import-not-at-top
    from a2a.utils.constants import TransportProtocol

    if not getattr(agent_card, "supported_interfaces", None):
        return False
    for interface in agent_card.supported_interfaces:
        if (
            interface.protocol_version == version
            and interface.protocol_binding == TransportProtocol.HTTP_JSON
        ):
            return True
    return False


class A2aAgent:
    """A class to initialize and set up an Agent-to-Agent application."""

    agent_framework = "a2a"

    # TODO: Add instrumentation for the A2A agent.
    def __init__(
        self,
        *,
        agent_card: "AgentCard",
        task_store_builder: Callable[..., "TaskStore"] = None,
        task_store_kwargs: Optional[Mapping[str, Any]] = None,
        agent_executor_kwargs: Optional[Mapping[str, Any]] = None,
        agent_executor_builder: Optional[Callable[..., "AgentExecutor"]] = None,
        request_handler_kwargs: Optional[Mapping[str, Any]] = None,
        request_handler_builder: Optional[Callable[..., "RequestHandler"]] = None,
        extended_agent_card: "AgentCard" = None,
    ):
        """Initializes the A2A agent."""
        # pylint: disable=g-import-not-at-top
        from google.cloud.aiplatform import initializer
        from a2a.utils.constants import TransportProtocol, PROTOCOL_VERSION_CURRENT

        if (
            agent_card.supported_interfaces
            and agent_card.supported_interfaces[0].protocol_binding
            != TransportProtocol.HTTP_JSON
        ):
            raise ValueError(
                "Only HTTP+JSON is supported for the primary interface on agent card "
            )
        if not _is_version_enabled(agent_card, PROTOCOL_VERSION_CURRENT):
            raise ValueError(
                "A2A protocol version 1.0 is required but not enabled on the agent card."
            )

        self._tmpl_attrs: dict[str, Any] = {
            "project": initializer.global_config.project,
            "location": initializer.global_config.location,
            "agent_card": agent_card,
            "agent_executor": None,
            "agent_executor_kwargs": agent_executor_kwargs or {},
            "agent_executor_builder": agent_executor_builder,
            "task_store": None,
            "task_store_kwargs": task_store_kwargs or {},
            "task_store_builder": task_store_builder,
            "request_handler": None,
            "request_handler_kwargs": request_handler_kwargs or {},
            "request_handler_builder": request_handler_builder,
            "extended_agent_card": extended_agent_card,
        }
        self.agent_card = agent_card
        self.request_handler = None
        self.task_store = None
        self.agent_executor = None

    def clone(self) -> "A2aAgent":
        """Clones the A2A agent."""
        import copy

        return A2aAgent(
            agent_card=copy.deepcopy(self.agent_card),
            task_store_builder=self._tmpl_attrs.get("task_store_builder"),
            task_store_kwargs=self._tmpl_attrs.get("task_store_kwargs"),
            agent_executor_kwargs=self._tmpl_attrs.get("agent_executor_kwargs"),
            agent_executor_builder=self._tmpl_attrs.get("agent_executor_builder"),
            request_handler_kwargs=self._tmpl_attrs.get("request_handler_kwargs"),
            request_handler_builder=self._tmpl_attrs.get("request_handler_builder"),
            extended_agent_card=self._tmpl_attrs.get("extended_agent_card"),
        )

    def set_up(self):
        """Sets up the A2A application."""
        # pylint: disable=g-import-not-at-top
        from a2a.server.request_handlers import DefaultRequestHandler
        from a2a.server.routes.rest_routes import create_rest_routes
        from a2a.server.tasks import InMemoryTaskStore

        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
        project = self._tmpl_attrs.get("project")
        os.environ["GOOGLE_CLOUD_PROJECT"] = project
        location = self._tmpl_attrs.get("location")
        os.environ["GOOGLE_CLOUD_LOCATION"] = location
        agent_engine_id = os.getenv("GOOGLE_CLOUD_AGENT_ENGINE_ID", "test-agent-engine")
        version = "v1beta1"

        new_url = f"https://{location}-aiplatform.googleapis.com/{version}/projects/{project}/locations/{location}/reasoningEngines/{agent_engine_id}/a2a"
        if not self.agent_card.supported_interfaces:
            from a2a.types import AgentInterface
            from a2a.utils.constants import TransportProtocol, PROTOCOL_VERSION_CURRENT

            self.agent_card.supported_interfaces.append(
                AgentInterface(
                    url=new_url,
                    protocol_binding=TransportProtocol.HTTP_JSON,
                    protocol_version=PROTOCOL_VERSION_CURRENT,
                )
            )
        else:
            # primary interface must be HTTP+JSON
            self.agent_card.supported_interfaces[0].url = new_url
        self._tmpl_attrs["agent_card"] = self.agent_card

        # Create the agent executor if a builder is provided.
        agent_executor_builder = self._tmpl_attrs.get("agent_executor_builder")
        if agent_executor_builder:
            self._tmpl_attrs["agent_executor"] = agent_executor_builder(
                **self._tmpl_attrs.get("agent_executor_kwargs")
            )
            self.agent_executor = self._tmpl_attrs.get("agent_executor")

        # Create the task store if a builder is provided.
        task_store_builder = self._tmpl_attrs.get("task_store_builder")
        if task_store_builder:
            self.task_store = task_store_builder(
                **self._tmpl_attrs.get("task_store_kwargs")
            )
        else:
            # Use the default task store if not provided. This could potentially
            # lead to unexpected behavior if the agent is running on
            # multiple instances.
            self.task_store = InMemoryTaskStore()

        self._tmpl_attrs["task_store"] = self.task_store

        # Create the request handler if a builder is provided.
        request_handler_builder = self._tmpl_attrs.get("request_handler_builder")
        if request_handler_builder:
            self.request_handler = request_handler_builder(
                **self._tmpl_attrs.get("request_handler_kwargs")
            )
        else:
            # Use the default request handler if not provided.
            self.request_handler = DefaultRequestHandler(
                agent_executor=self._tmpl_attrs.get("agent_executor"),
                task_store=self.task_store,
                agent_card=self.agent_card,
                extended_agent_card=self._tmpl_attrs.get("extended_agent_card"),
            )

        self._tmpl_attrs["request_handler"] = self.request_handler

        # Support native Starlette routes.
        enable_v0_3 = _is_version_enabled(self.agent_card, "0.3")
        self.rest_routes = create_rest_routes(
            request_handler=self,
            enable_v0_3_compat=enable_v0_3,
            path_prefix="/a2a",
        )

    def __getattr__(self, name: str) -> Any:
        """Delegates all missing RequestHandler methods to the underlying request_handler."""
        if not self.request_handler:
            raise AttributeError(
                f"'A2aAgent' has no attribute '{name}' and request_handler is not initialized."
            )
        return getattr(self.request_handler, name)

    async def on_message_send(
        self,
        request: "SendMessageRequest",
        context: "ServerCallContext",
    ) -> "Task | Message":
        if not self.request_handler:
            raise NotImplementedError("request_handler not available.")
        return await self.request_handler.on_message_send(request, context)

    async def on_cancel_task(
        self,
        request: "CancelTaskRequest",
        context: "ServerCallContext",
    ) -> "Task | None":
        if not self.request_handler:
            raise NotImplementedError("request_handler not available.")
        return await self.request_handler.on_cancel_task(request, context)

    async def on_get_task(
        self,
        request: "GetTaskRequest",
        context: "ServerCallContext",
    ) -> "Task | None":
        if not self.request_handler:
            raise NotImplementedError("request_handler not available.")
        return await self.request_handler.on_get_task(request, context)

    async def on_list_tasks(
        self,
        request: "ListTasksRequest",
        context: "ServerCallContext",
    ) -> "ListTasksResponse":
        if not self.request_handler:
            raise NotImplementedError("request_handler not available.")
        return await self.request_handler.on_list_tasks(request, context)

    async def on_create_task_push_notification_config(
        self,
        request: "TaskPushNotificationConfig",
        context: "ServerCallContext",
    ) -> "TaskPushNotificationConfig":
        if not self.request_handler:
            raise NotImplementedError("request_handler not available.")
        return await self.request_handler.on_create_task_push_notification_config(
            request, context
        )

    async def on_get_task_push_notification_config(
        self,
        request: "GetTaskPushNotificationConfigRequest",
        context: "ServerCallContext",
    ) -> "TaskPushNotificationConfig":
        if not self.request_handler:
            raise NotImplementedError("request_handler not available.")
        return await self.request_handler.on_get_task_push_notification_config(
            request, context
        )

    async def on_list_task_push_notification_configs(
        self,
        request: "ListTaskPushNotificationConfigsRequest",
        context: "ServerCallContext",
    ) -> "ListTaskPushNotificationConfigsResponse":
        if not self.request_handler:
            raise NotImplementedError("request_handler not available.")
        return await self.request_handler.on_list_task_push_notification_configs(
            request, context
        )

    async def on_delete_task_push_notification_config(
        self,
        request: "DeleteTaskPushNotificationConfigRequest",
        context: "ServerCallContext",
    ) -> None:
        if not self.request_handler:
            raise NotImplementedError("request_handler not available.")
        return await self.request_handler.on_delete_task_push_notification_config(
            request, context
        )

    async def on_get_extended_agent_card(
        self,
        request: "GetExtendedAgentCardRequest",
        context: "ServerCallContext",
    ) -> "AgentCard":
        if not self.request_handler:
            raise NotImplementedError("request_handler not available.")
        return await self.request_handler.on_get_extended_agent_card(request, context)

    def register_operations(self) -> Dict[str, List[str]]:
        """Registers the operations of the A2A Agent."""
        routes = {
            "a2a_extension": [
                "on_message_send",
                "on_get_task",
                "on_list_tasks",
                "on_cancel_task",
                "on_create_task_push_notification_config",
                "on_get_task_push_notification_config",
                "on_list_task_push_notification_configs",
                "on_delete_task_push_notification_config",
            ]
        }
        if self.agent_card.capabilities and self.agent_card.capabilities.streaming:
            routes["a2a_extension"].append("on_message_send_stream")
            routes["a2a_extension"].append("on_subscribe_to_task")
        if (
            self.agent_card.capabilities
            and self.agent_card.capabilities.extended_agent_card
        ):
            routes["a2a_extension"].append("on_get_extended_agent_card")
        return routes

    async def on_message_send_stream(
        self,
        request: "SendMessageRequest",
        context: "ServerCallContext",
    ) -> AsyncIterator["Event"]:
        """Handles A2A streaming requests via SSE."""
        async for chunk in self.request_handler.on_message_send_stream(
            request, context
        ):
            yield chunk

    async def on_subscribe_to_task(
        self,
        request: "SubscribeToTaskRequest",
        context: "ServerCallContext",
    ) -> AsyncIterator["Event"]:
        """Handles A2A task resubscription requests via SSE."""
        async for chunk in self.request_handler.on_subscribe_to_task(request, context):
            yield chunk

    def __getstate__(self):
        """Serializes AgentCard proto to a dictionary."""
        from google.protobuf import json_format
        import json

        state = self.__dict__.copy()

        def _to_dict_if_proto(obj):
            if hasattr(obj, "DESCRIPTOR"):
                return {
                    "__protobuf_AgentCard__": json.loads(json_format.MessageToJson(obj))
                }
            return obj

        state["agent_card"] = _to_dict_if_proto(state.get("agent_card"))
        if "_tmpl_attrs" in state:
            tmpl_attrs = state["_tmpl_attrs"].copy()
            tmpl_attrs["agent_card"] = _to_dict_if_proto(tmpl_attrs.get("agent_card"))
            tmpl_attrs["extended_agent_card"] = _to_dict_if_proto(
                tmpl_attrs.get("extended_agent_card")
            )
            state["_tmpl_attrs"] = tmpl_attrs

        return state

    def __setstate__(self, state):
        """Deserializes AgentCard proto from a dictionary."""
        from google.protobuf import json_format
        from a2a.types import AgentCard

        def _from_dict_if_proto(obj):
            if isinstance(obj, dict) and "__protobuf_AgentCard__" in obj:
                agent_card = AgentCard()
                json_format.ParseDict(obj["__protobuf_AgentCard__"], agent_card)
                return agent_card
            return obj

        state["agent_card"] = _from_dict_if_proto(state.get("agent_card"))
        if "_tmpl_attrs" in state:
            state["_tmpl_attrs"]["agent_card"] = _from_dict_if_proto(
                state["_tmpl_attrs"].get("agent_card")
            )
            state["_tmpl_attrs"]["extended_agent_card"] = _from_dict_if_proto(
                state["_tmpl_attrs"].get("extended_agent_card")
            )

        self.__dict__.update(state)
