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
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Mapping,
    Optional,
    Sequence,
    Union,
)

if TYPE_CHECKING:
    try:
        from langchain_core import runnables
        from langchain_core import tools as lc_tools
        from langchain_core.language_models import base as lc_language_models

        BaseTool = lc_tools.BaseTool
        BaseLanguageModel = lc_language_models.BaseLanguageModel
        GetSessionHistoryCallable = runnables.history.GetSessionHistoryCallable
        RunnableConfig = runnables.RunnableConfig
        RunnableSerializable = runnables.RunnableSerializable
    except ImportError:
        BaseTool = Any
        BaseLanguageModel = Any
        GetSessionHistoryCallable = Any
        RunnableConfig = Any
        RunnableSerializable = Any

    try:
        from langchain_google_vertexai.functions_utils import _ToolsType

        _ToolLike = _ToolsType
    except ImportError:
        _ToolLike = Any


def _default_runnable_kwargs(has_history: bool) -> Mapping[str, Any]:
    # https://github.com/langchain-ai/langchain/blob/5784dfed001730530637793bea1795d9d5a7c244/libs/core/langchain_core/runnables/history.py#L237-L241
    runnable_kwargs = {
        # input_messages_key (str): Must be specified if the underlying
        # agent accepts a dict as input.
        "input_messages_key": "input",
        # output_messages_key (str): Must be specified if the underlying
        # agent returns a dict as output.
        "output_messages_key": "output",
    }
    if has_history:
        # history_messages_key (str): Must be specified if the underlying
        # agent accepts a dict as input and a separate key for historical
        # messages.
        runnable_kwargs["history_messages_key"] = "history"
    return runnable_kwargs


def _default_output_parser():
    try:
        from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
    except (ModuleNotFoundError, ImportError):
        # Fallback to an older version if needed.
        from langchain.agents.output_parsers.openai_tools import (
            OpenAIToolsAgentOutputParser as ToolsAgentOutputParser,
        )

    return ToolsAgentOutputParser()


def _default_model_builder(
    model_name: str,
    *,
    project: str,
    location: str,
    model_kwargs: Optional[Mapping[str, Any]] = None,
) -> "BaseLanguageModel":
    import vertexai
    from google.cloud.aiplatform import initializer
    from langchain_google_vertexai import ChatVertexAI

    model_kwargs = model_kwargs or {}
    current_project = initializer.global_config.project
    current_location = initializer.global_config.location
    vertexai.init(project=project, location=location)
    model = ChatVertexAI(model_name=model_name, **model_kwargs)
    vertexai.init(project=current_project, location=current_location)
    return model


def _default_runnable_builder(
    model: "BaseLanguageModel",
    *,
    tools: Optional[Sequence["_ToolLike"]] = None,
    prompt: Optional["RunnableSerializable"] = None,
    output_parser: Optional["RunnableSerializable"] = None,
    chat_history: Optional["GetSessionHistoryCallable"] = None,
    model_tool_kwargs: Optional[Mapping[str, Any]] = None,
    agent_executor_kwargs: Optional[Mapping[str, Any]] = None,
    runnable_kwargs: Optional[Mapping[str, Any]] = None,
) -> "RunnableSerializable":
    from langchain_core import tools as lc_tools
    from langchain.agents import AgentExecutor
    from langchain.tools.base import StructuredTool

    # The prompt template and runnable_kwargs needs to be customized depending
    # on whether the user intends for the agent to have history. The way the
    # user would reflect that is by setting chat_history (which defaults to
    # None).
    has_history: bool = chat_history is not None
    prompt = prompt or _default_prompt(has_history)
    output_parser = output_parser or _default_output_parser()
    model_tool_kwargs = model_tool_kwargs or {}
    agent_executor_kwargs = agent_executor_kwargs or {}
    runnable_kwargs = runnable_kwargs or _default_runnable_kwargs(has_history)
    if tools:
        model = model.bind_tools(tools=tools, **model_tool_kwargs)
    else:
        tools = []
    agent_executor = AgentExecutor(
        agent=prompt | model | output_parser,
        tools=[
            tool
            if isinstance(tool, lc_tools.BaseTool)
            else StructuredTool.from_function(tool)
            for tool in tools
            if isinstance(tool, (Callable, lc_tools.BaseTool))
        ],
        **agent_executor_kwargs,
    )
    if has_history:
        from langchain_core.runnables.history import RunnableWithMessageHistory

        return RunnableWithMessageHistory(
            runnable=agent_executor,
            get_session_history=chat_history,
            **runnable_kwargs,
        )
    return agent_executor


def _default_prompt(has_history: bool) -> "RunnableSerializable":
    from langchain_core import prompts

    try:
        from langchain.agents.format_scratchpad.tools import format_to_tool_messages
    except (ModuleNotFoundError, ImportError):
        # Fallback to an older version if needed.
        from langchain.agents.format_scratchpad.openai_tools import (
            format_to_openai_tool_messages as format_to_tool_messages,
        )

    if has_history:
        return {
            "history": lambda x: x["history"],
            "input": lambda x: x["input"],
            "agent_scratchpad": (
                lambda x: format_to_tool_messages(x["intermediate_steps"])
            ),
        } | prompts.ChatPromptTemplate.from_messages(
            [
                prompts.MessagesPlaceholder(variable_name="history"),
                ("user", "{input}"),
                prompts.MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
    else:
        return {
            "input": lambda x: x["input"],
            "agent_scratchpad": (
                lambda x: format_to_tool_messages(x["intermediate_steps"])
            ),
        } | prompts.ChatPromptTemplate.from_messages(
            [
                ("user", "{input}"),
                prompts.MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )


def _validate_callable_parameters_are_annotated(callable: Callable):
    """Validates that the parameters of the callable have type annotations.

    This ensures that they can be used for constructing LangChain tools that are
    usable with Gemini function calling.
    """
    import inspect

    parameters = dict(inspect.signature(callable).parameters)
    for name, parameter in parameters.items():
        if parameter.annotation == inspect.Parameter.empty:
            raise TypeError(
                f"Callable={callable.__name__} has untyped input_arg={name}. "
                f"Please specify a type when defining it, e.g. `{name}: str`."
            )


def _validate_tools(tools: Sequence["_ToolLike"]):
    """Validates that the tools are usable for tool calling."""
    for tool in tools:
        if isinstance(tool, Callable):
            _validate_callable_parameters_are_annotated(tool)


class LangchainAgent:
    """A Langchain Agent.

    Reference:
    *   Agent: https://python.langchain.com/docs/modules/agents/concepts
    *   Memory: https://python.langchain.com/docs/expression_language/how_to/message_history
    """

    def __init__(
        self,
        model: str,
        *,
        prompt: Optional["RunnableSerializable"] = None,
        tools: Optional[Sequence["_ToolLike"]] = None,
        output_parser: Optional["RunnableSerializable"] = None,
        chat_history: Optional["GetSessionHistoryCallable"] = None,
        model_kwargs: Optional[Mapping[str, Any]] = None,
        model_tool_kwargs: Optional[Mapping[str, Any]] = None,
        agent_executor_kwargs: Optional[Mapping[str, Any]] = None,
        runnable_kwargs: Optional[Mapping[str, Any]] = None,
        model_builder: Optional[Callable] = None,
        runnable_builder: Optional[Callable] = None,
    ):
        """Initializes the LangchainAgent.

        Under-the-hood, assuming .set_up() is called, this will correspond to

        ```
        model = model_builder(model_name=model, model_kwargs=model_kwargs)
        runnable = runnable_builder(
            prompt=prompt,
            model=model,
            tools=tools,
            output_parser=output_parser,
            chat_history=chat_history,
            agent_executor_kwargs=agent_executor_kwargs,
            runnable_kwargs=runnable_kwargs,
        )
        ```

        When everything is based on their default values, this corresponds to
        ```
        # model_builder
        from langchain_google_vertexai import ChatVertexAI
        llm = ChatVertexAI(model_name=model, **model_kwargs)

        # runnable_builder
        from langchain import agents
        from langchain_core.runnables.history import RunnableWithMessageHistory
        llm_with_tools = llm.bind_tools(tools=tools, **model_tool_kwargs)
        agent_executor = agents.AgentExecutor(
            agent=prompt | llm_with_tools | output_parser,
            tools=tools,
            **agent_executor_kwargs,
        )
        runnable = RunnableWithMessageHistory(
            runnable=agent_executor,
            get_session_history=chat_history,
            **runnable_kwargs,
        )
        ```

        Args:
            model (str):
                Optional. The name of the model (e.g. "gemini-1.0-pro").
            prompt (langchain_core.runnables.RunnableSerializable):
                Optional. The prompt template for the model. Defaults to a
                ChatPromptTemplate.
            tools (Sequence[langchain_core.tools.BaseTool, Callable]):
                Optional. The tools for the agent to be able to use. All input
                callables (e.g. function or class method) will be converted
                to a langchain.tools.base.StructuredTool. Defaults to None.
            output_parser (langchain_core.runnables.RunnableSerializable):
                Optional. The output parser for the model. Defaults to an
                output parser that works with Gemini function-calling.
            chat_history (langchain_core.runnables.history.GetSessionHistoryCallable):
                Optional. Callable that returns a new BaseChatMessageHistory.
                Defaults to None, i.e. chat_history is not preserved.
            model_kwargs (Mapping[str, Any]):
                Optional. Additional keyword arguments for the constructor of
                chat_models.ChatVertexAI. An example would be
                ```
                {
                    # temperature (float): Sampling temperature, it controls the
                    # degree of randomness in token selection.
                    "temperature": 0.28,
                    # max_output_tokens (int): Token limit determines the
                    # maximum amount of text output from one prompt.
                    "max_output_tokens": 1000,
                    # top_p (float): Tokens are selected from most probable to
                    # least, until the sum of their probabilities equals the
                    # top_p value.
                    "top_p": 0.95,
                    # top_k (int): How the model selects tokens for output, the
                    # next token is selected from among the top_k most probable
                    # tokens.
                    "top_k": 40,
                }
                ```
            model_tool_kwargs (Mapping[str, Any]):
                Optional. Additional keyword arguments when binding tools to the
                model using `model.bind_tools()`.
            agent_executor_kwargs (Mapping[str, Any]):
                Optional. Additional keyword arguments for the constructor of
                langchain.agents.AgentExecutor. An example would be
                ```
                {
                    # Whether to return the agent's trajectory of intermediate
                    # steps at the end in addition to the final output.
                    "return_intermediate_steps": False,
                    # The maximum number of steps to take before ending the
                    # execution loop.
                    "max_iterations": 15,
                    # The method to use for early stopping if the agent never
                    # returns `AgentFinish`. Either 'force' or 'generate'.
                    "early_stopping_method": "force",
                    # How to handle errors raised by the agent's output parser.
                    # Defaults to `False`, which raises the error.
                    "handle_parsing_errors": False,
                }
                ```
            runnable_kwargs (Mapping[str, Any]):
                Optional. Additional keyword arguments for the constructor of
                langchain.runnables.history.RunnableWithMessageHistory if
                chat_history is specified. If chat_history is None, this will be
                ignored.
            model_builder (Callable):
                Optional. Callable that returns a new language model. Defaults
                to a a callable that returns ChatVertexAI based on `model`,
                `model_kwargs` and the parameters in `vertexai.init`.
            runnable_builder (Callable):
                Optional. Callable that returns a new runnable. This can be used
                for customizing the orchestration logic of the Agent based on
                the model returned by `model_builder` and the rest of the input
                arguments.

        Raises:
            TypeError: If there is an invalid tool (e.g. function with an input
            that did not specify its type).
        """
        from google.cloud.aiplatform import initializer

        self._project = initializer.global_config.project
        self._location = initializer.global_config.location
        self._tools = []
        if tools:
            # We validate tools at initialization for actionable feedback before
            # they are deployed.
            _validate_tools(tools)
            self._tools = tools
        self._model_name = model
        self._prompt = prompt
        self._output_parser = output_parser
        self._chat_history = chat_history
        self._model_kwargs = model_kwargs
        self._model_tool_kwargs = model_tool_kwargs
        self._agent_executor_kwargs = agent_executor_kwargs
        self._runnable_kwargs = runnable_kwargs
        self._model = None
        self._model_builder = model_builder
        self._runnable = None
        self._runnable_builder = runnable_builder

    def set_up(self):
        """Sets up the agent for execution of queries at runtime.

        It initializes the model, binds the model with tools, and connects it
        with the prompt template and output parser.

        This method should not be called for an object that being passed to
        the ReasoningEngine service for deployment, as it initializes clients
        that can not be serialized.
        """
        model_builder = self._model_builder or _default_model_builder
        self._model = model_builder(
            model_name=self._model_name,
            model_kwargs=self._model_kwargs,
            project=self._project,
            location=self._location,
        )
        runnable_builder = self._runnable_builder or _default_runnable_builder
        self._runnable = runnable_builder(
            prompt=self._prompt,
            model=self._model,
            tools=self._tools,
            output_parser=self._output_parser,
            chat_history=self._chat_history,
            model_tool_kwargs=self._model_tool_kwargs,
            agent_executor_kwargs=self._agent_executor_kwargs,
            runnable_kwargs=self._runnable_kwargs,
        )

    def clone(self) -> "LangchainAgent":
        """Returns a clone of the LangchainAgent."""
        import copy

        return LangchainAgent(
            model=self._model_name,
            prompt=copy.deepcopy(self._prompt),
            tools=copy.deepcopy(self._tools),
            output_parser=copy.deepcopy(self._output_parser),
            chat_history=copy.deepcopy(self._chat_history),
            model_kwargs=copy.deepcopy(self._model_kwargs),
            model_tool_kwargs=copy.deepcopy(self._model_tool_kwargs),
            agent_executor_kwargs=copy.deepcopy(self._agent_executor_kwargs),
            runnable_kwargs=copy.deepcopy(self._runnable_kwargs),
            model_builder=self._model_builder,
            runnable_builder=self._runnable_builder,
        )

    def query(
        self,
        *,
        input: Union[str, Mapping[str, Any]],
        config: Optional["RunnableConfig"] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Queries the Agent with the given input and config.

        Args:
            input (Union[str, Mapping[str, Any]]):
                Required. The input to be passed to the Agent.
            config (langchain_core.runnables.RunnableConfig):
                Optional. The config (if any) to be used for invoking the Agent.
            **kwargs:
                Optional. Any additional keyword arguments to be passed to the
                `.invoke()` method of the corresponding AgentExecutor.

        Returns:
            The output of querying the Agent with the given input and config.
        """
        from langchain.load import dump as langchain_load_dump

        if isinstance(input, str):
            input = {"input": input}
        if not self._runnable:
            self.set_up()
        return langchain_load_dump.dumpd(
            self._runnable.invoke(input=input, config=config, **kwargs)
        )
