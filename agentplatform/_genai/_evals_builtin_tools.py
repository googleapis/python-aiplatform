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
"""Built-in tool catalog for Gemini Agent evaluation display.

The Gemini Agents API (``GET agents/{id}``) returns each tool as a bare type
discriminator (e.g. ``{"type": "code_execution"}``) with no parameter schema
or description.  The authoritative, full-fidelity expansion lives server-side
in ``cloud/ai/platform/evaluation/utils/interaction_converter.py``.

This module is a **display-only duplicate** of that server catalog, kept here
so ``show()`` can render tools with full names and descriptions without a
server round-trip.  Parameter schemas are intentionally omitted to avoid
publishing internal tool contract details.

**If the server catalog changes, this SDK-side copy must be updated to match.**

This module also provides sandbox-detection helpers
(``SANDBOX_TOOL_NAMES``, ``is_sandbox_only_turn``) used by the display
path (``_evals_common._interaction_dict_to_agent_data``).
"""

from typing import Any, Optional

from google.genai import types as genai_types


# Maps a built-in Gemini Agent tool type to the concrete FunctionDeclarations
# the agent actually exposes for that type.
#
# Source of truth: interaction_converter.py, _BUILTIN_TOOL_FUNCTION_DECLARATIONS
BUILTIN_TOOL_DECLARATIONS: dict[str, list[genai_types.FunctionDeclaration]] = {
    "code_execution": [
        genai_types.FunctionDeclaration(
            name="run_command",
            description="Runs a shell command on the sandbox VM.",
        ),
    ],
    "filesystem": [
        genai_types.FunctionDeclaration(
            name="view_file",
            description="Reads the content of a workspace file.",
        ),
        genai_types.FunctionDeclaration(
            name="create_file",
            description="Writes content to a new or existing file.",
        ),
        genai_types.FunctionDeclaration(
            name="edit_file",
            description="Replaces a specific block of text in a file.",
        ),
        genai_types.FunctionDeclaration(
            name="list_dir",
            description="Lists the files in a directory.",
        ),
        genai_types.FunctionDeclaration(
            name="delete_file",
            description="Removes a file from the workspace.",
        ),
        genai_types.FunctionDeclaration(
            name="move_file",
            description="Renames or moves a file.",
        ),
    ],
}


# Sandbox-environment orchestration tool declarations.
#
# Source of truth: interaction_converter.py, _SANDBOX_FUNCTION_DECLARATIONS
SANDBOX_DECLARATIONS: list[genai_types.FunctionDeclaration] = [
    genai_types.FunctionDeclaration(
        name="provision_sandbox",
        description="Provisions a sandbox environment.",
    ),
    genai_types.FunctionDeclaration(
        name="load_sandbox",
        description="Loads a previously provisioned sandbox environment.",
    ),
]


# Names of sandbox orchestration tools, derived from ``SANDBOX_DECLARATIONS``
# so there is a single source of truth.
SANDBOX_TOOL_NAMES: frozenset[str] = frozenset(
    decl.name for decl in SANDBOX_DECLARATIONS if decl.name
)


def is_sandbox_only_turn(
    events: list[Any],
) -> bool:
    """Returns True if a turn contains only sandbox initialization events.

    Sandbox provisioning events (``provision_sandbox``, ``load_sandbox``)
    are infrastructure setup steps that happen before the user's first
    real prompt.

    A turn is sandbox-only when every event is either a
    ``function_call`` or ``function_response`` referencing a sandbox
    tool name.  Events with plain text content (model output, user
    input) disqualify the turn.

    Args:
        events: The list of AgentEvents in the turn.

    Returns:
        True if the turn is sandbox-only and should be merged into the
        next real turn for display.
    """
    if not events:
        return True

    for event in events:
        content = getattr(event, "content", None)
        if not content:
            continue
        parts = getattr(content, "parts", None)
        if not parts:
            continue
        for part in parts:
            if getattr(part, "function_call", None):
                if part.function_call.name not in SANDBOX_TOOL_NAMES:
                    return False
            elif getattr(part, "function_response", None):
                if part.function_response.name not in SANDBOX_TOOL_NAMES:
                    return False
            elif getattr(part, "text", None):
                # Text content means this is a real conversational event,
                # not sandbox infrastructure.
                return False
    return True


def agent_tools_to_config_tools(
    agent_tools: Optional[list[Any]],
    has_environment: bool = False,
) -> Optional[list[genai_types.Tool]]:
    """Maps Gemini Agents API tools to ``genai_types.Tool`` for display.

    Expands built-in agent tool types into their concrete function declarations
    using ``BUILTIN_TOOL_DECLARATIONS`` (a display-only duplicate of the
    server-side catalog in ``interaction_converter.py``).

    Mapping rules:
      * ``code_execution`` is expanded to ``run_command``.
      * ``filesystem`` is expanded to ``view_file``, ``create_file``,
        ``edit_file``, ``list_dir``, ``delete_file``, ``move_file``.
      * ``google_search`` and ``url_context`` are mapped to their typed
        ``genai_types.Tool`` variant.
      * ``mcp_server`` is represented as a named declaration with a
        human-readable label.
      * Tools carrying explicit ``function_declarations`` are passed through.
      * When ``has_environment`` is True, sandbox orchestration tools
        (``provision_sandbox``, ``load_sandbox``) are appended.

    Args:
        agent_tools: The ``tools`` list from a fetched Gemini agent dict.
        has_environment: Whether the agent has a sandbox environment configured.

    Returns:
        A list of ``genai_types.Tool``, or ``None`` if there are no mappable
        tools.
    """
    if not agent_tools and not has_environment:
        return None
    tools: list[genai_types.Tool] = []
    for tool in agent_tools or []:
        if not isinstance(tool, dict):
            continue
        tool_type = tool.get("type")
        remainder = {k: v for k, v in tool.items() if k != "type"}

        # Check the built-in catalog first (code_execution, filesystem).
        catalog_decls = BUILTIN_TOOL_DECLARATIONS.get(tool_type or "")
        if catalog_decls:
            tools.append(genai_types.Tool(function_declarations=list(catalog_decls)))
        elif tool_type == "google_search":
            tools.append(genai_types.Tool(google_search=genai_types.GoogleSearch()))
        elif tool_type == "url_context":
            tools.append(genai_types.Tool(url_context=genai_types.UrlContext()))
        elif "function_declarations" in remainder:
            # Real function tool with explicit declarations.
            tools.append(genai_types.Tool.model_validate(remainder))
        elif tool_type == "mcp_server":
            label = remainder.get("name") or remainder.get("url")
            description = f"MCP server: {label}" if label else "MCP server."
            tools.append(
                genai_types.Tool(
                    function_declarations=[
                        genai_types.FunctionDeclaration(
                            name="mcp_server", description=description
                        )
                    ]
                )
            )
        elif tool_type:
            # Unknown built-in: show by name so it isn't silently dropped.
            tools.append(
                genai_types.Tool(
                    function_declarations=[
                        genai_types.FunctionDeclaration(name=tool_type)
                    ]
                )
            )
        elif remainder:
            tools.append(genai_types.Tool.model_validate(remainder))

    if has_environment:
        tools.append(genai_types.Tool(function_declarations=list(SANDBOX_DECLARATIONS)))

    return tools or None
