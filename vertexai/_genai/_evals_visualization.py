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
"""Visualization utilities for GenAI Evaluation SDK."""

import base64
import html
import json
import logging
import textwrap
from typing import Any, Optional

import pandas as pd
from pydantic import errors

from . import types


logger = logging.getLogger(__name__)


def _is_ipython_env() -> bool:
    """Checks if the code is running in an IPython environment."""
    try:
        from IPython import get_ipython

        return get_ipython() is not None
    except ImportError:
        return False


def _pydantic_serializer(obj: Any) -> Any:
    """Custom serializer for Pydantic models."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def _preprocess_df_for_json(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    """Prepares a DataFrame for JSON serialization by converting complex objects to strings."""
    if df is None:
        return None
    df_copy = df.copy()

    for col in df_copy.columns:
        if (
            df_copy[col].dtype == "object"
            or df_copy[col].apply(lambda x: isinstance(x, (dict, list))).any()
        ):

            def stringify_cell(cell: Any) -> Optional[str]:
                if isinstance(cell, (dict, list)):
                    try:
                        return json.dumps(
                            cell, ensure_ascii=False, default=_pydantic_serializer
                        )
                    except TypeError:
                        return str(cell)
                elif pd.isna(cell):
                    return None
                elif not isinstance(cell, (str, int, float, bool)):
                    if hasattr(cell, "model_dump"):
                        return json.dumps(
                            cell.model_dump(mode="json"), ensure_ascii=False
                        )
                    return str(cell)
                return str(cell)

            df_copy[col] = df_copy[col].apply(stringify_cell)
    return df_copy


def _encode_to_base64(data: str) -> str:
    """Encodes a string to a web-safe Base64 string."""
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def _extract_text_and_raw_json(content: Any) -> dict[str, str]:
    """Extracts display text and raw JSON from a content object."""
    if hasattr(content, "model_dump"):
        content = content.model_dump(mode="json", exclude_none=True)

    if not isinstance(content, (str, dict)):
        return {"display_text": str(content or ""), "raw_json": ""}

    try:
        data = json.loads(content) if isinstance(content, str) else content

        if not isinstance(data, dict):
            return {"display_text": str(content), "raw_json": ""}

        pretty_json = json.dumps(data, indent=2, ensure_ascii=False)

        # Gemini format check (API Wrapper format).
        if (
            "contents" in data
            and isinstance(data.get("contents"), list)
            and data["contents"]
        ):
            first_part = data["contents"][0].get("parts", [{}])[0]
            display_text = first_part.get("text", str(data))
            return {"display_text": display_text, "raw_json": pretty_json}

        # Direct Gemini Content Object Check
        elif "parts" in data and isinstance(data.get("parts"), list) and data["parts"]:
            text_parts = [p.get("text", "") for p in data["parts"] if "text" in p]
            display_text = "\n".join(text_parts) if text_parts else str(data)
            return {"display_text": display_text, "raw_json": pretty_json}

        # OpenAI response format check.
        elif (
            "choices" in data
            and isinstance(data.get("choices"), list)
            and data["choices"]
        ):
            message = data["choices"][0].get("message", {})
            display_text = message.get("content", str(data))
            return {"display_text": display_text, "raw_json": pretty_json}

        # OpenAI request format check.
        elif (
            "messages" in data
            and isinstance(data.get("messages"), list)
            and data["messages"]
        ):
            user_messages = [
                message.get("content", "")
                for message in data["messages"]
                if message.get("role") == "user"
            ]
            display_text = user_messages[-1] if user_messages else str(data)
            return {"display_text": display_text, "raw_json": pretty_json}
        else:
            # Not a recognized format.
            return {"display_text": str(content), "raw_json": pretty_json}

    except (json.JSONDecodeError, TypeError, IndexError):
        return {"display_text": str(content), "raw_json": ""}


def _extract_dataset_rows(dataset: types.EvaluationDataset) -> list[dict[str, Any]]:
    """Helper to consistently extract rows from either a dataframe or raw eval_cases list."""
    processed_rows = []

    # Process from DataFrame if available
    if getattr(dataset, "eval_dataset_df", None) is not None:
        processed_df = _preprocess_df_for_json(dataset.eval_dataset_df)
        if processed_df is not None:
            for _, row in processed_df.iterrows():
                prompt_key = "request" if "request" in row else "prompt"
                prompt_info = _extract_text_and_raw_json(row.get(prompt_key))
                response_info = _extract_text_and_raw_json(row.get("response"))
                processed_row = {
                    "prompt_display_text": prompt_info["display_text"],
                    "prompt_raw_json": prompt_info["raw_json"],
                    "reference": row.get("reference", ""),
                    "response_display_text": response_info["display_text"],
                    "response_raw_json": response_info["raw_json"],
                    "intermediate_events": row.get("intermediate_events", None),
                    "agent_data": row.get("agent_data", None),
                }
                processed_rows.append(processed_row)

    # Fallback to pure eval_cases extraction
    elif dataset.eval_cases:
        for case in dataset.eval_cases:
            prompt_info = (
                _extract_text_and_raw_json(case.prompt)
                if case.prompt
                else {"display_text": "", "raw_json": ""}
            )

            response_info = {"display_text": "", "raw_json": ""}
            if case.responses and case.responses[0].response:
                response_info = _extract_text_and_raw_json(case.responses[0].response)

            reference_text = ""
            if case.reference and case.reference.response:
                ref_info = _extract_text_and_raw_json(case.reference.response)
                reference_text = ref_info["display_text"]

            agent_data_json = None
            if case.agent_data:
                agent_data_json = json.dumps(
                    case.agent_data.model_dump(mode="json", exclude_none=True),
                    ensure_ascii=False,
                )

            intermediate_events_json = None
            if case.intermediate_events:
                intermediate_events_json = json.dumps(
                    [
                        e.model_dump(mode="json", exclude_none=True)
                        for e in case.intermediate_events
                    ],
                    ensure_ascii=False,
                )

            processed_row = {
                "prompt_display_text": prompt_info["display_text"],
                "prompt_raw_json": prompt_info["raw_json"],
                "reference": reference_text,
                "response_display_text": response_info["display_text"],
                "response_raw_json": response_info["raw_json"],
                "intermediate_events": intermediate_events_json,
                "agent_data": agent_data_json,
            }
            processed_rows.append(processed_row)

    return processed_rows


def _get_evaluation_html(eval_result_json: str) -> str:
    """Returns a self-contained HTML for single evaluation visualization."""
    payload_b64 = _encode_to_base64(eval_result_json)
    return textwrap.dedent(
        f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Evaluation Report</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>
    <style>
        body {{ font-family: 'Roboto', 'Helvetica', sans-serif; margin: 2em; background-color: #f8f9fa; color: #202124; }}
        .container {{ max-width: 1200px; margin: 20px auto; padding: 20px; background-color: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
        h1, h2, h3 {{ color: #3c4043; }}
        h1 {{ border-bottom: 2px solid #4285F4; padding-bottom: 8px; }}
        h2 {{ border-bottom: 1px solid #dadce0; padding-bottom: 8px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
        th, td {{ border: 1px solid #dadce0; padding: 12px; text-align: left; vertical-align: top; }}
        th {{ background-color: #f2f2f2; font-weight: 500; }}
        details {{ border: 1px solid #dadce0; border-radius: 8px; padding: 16px; margin-bottom: 16px; background: #fff; }}
        summary {{ font-weight: 500; font-size: 1.1em; cursor: pointer; }}
        .prompt-container {{ background-color: #e8f0fe; padding: 16px; margin: 12px 0; border-radius: 8px; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word; }}
        .reference-container {{ background-color: #e6f4ea; padding: 16px; margin: 12px 0; border-radius: 8px; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word; }}
        .agent-info-container {{ background-color: #f1f3f4; padding: 16px; margin: 12px 0; border-radius: 8px; word-wrap: break-word; overflow-wrap: break-word; font-size: 14px; }}
        .agent-info-grid {{ display: grid; grid-template-columns: 120px 1fr; gap: 8px; margin-bottom: 12px; }}
        .agent-info-grid dt {{ font-weight: 500; color: #3c4043; }}
        .agent-info-grid dd {{ margin: 0; white-space: pre-wrap; word-wrap: break-word; }}
        .intermediate-events-container {{ background-color: #f1f3f4; padding: 16px; margin: 12px 0; border-radius: 8px; word-wrap: break-word; overflow-wrap: break-word; max-height: 400px; overflow-y: auto; overflow-x: auto; }}
        .response-container {{ background-color: #f9f9f9; padding: 12px; margin-top: 8px; border-radius: 8px; border: 1px solid #eee; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word; }}
        .explanation {{ color: #5f6368; font-style: italic; font-size: 0.9em; padding-top: 6px; }}
        .raw-json-details summary {{ font-size: 0.9em; cursor: pointer; color: #5f6368;}}
        .raw-json-container {{ white-space: pre-wrap; word-wrap: break-word; max-height: 300px; overflow-y: auto; background-color: #f1f1f1; padding: 10px; border-radius: 4px; margin-top: 8px; }}

        .rubric-bubble-container {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .rubric-details {{ border: none; padding: 0; margin: 0; }}
        .rubric-bubble {{ display: inline-flex; align-items: center; background-color: #e8f0fe; color: #1967d2; border-radius: 16px; padding: 8px 12px; font-size: 0.9em; cursor: pointer; list-style: none; }}
        .rubric-bubble::-webkit-details-marker {{ display: none; }}
        .rubric-bubble::before {{ content: '►'; margin-right: 8px; font-size: 0.8em; transition: transform 0.2s; }}
        .rubric-details[open] > .rubric-bubble::before {{ transform: rotate(90deg); }}
        .pass {{ color: green; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}

        .case-content-wrapper {{ display: flex; gap: 1rem; }}
        .case-content-main {{ flex: 1; }}
        .case-content-sidebar {{ flex: 1; min-width: 0; }}

        /* Tool Declarations */
        .tool-declarations-container {{ background-color: #f1f1f1; padding: 10px; border-radius: 4px; margin-top: 8px; max-height: 300px; overflow-y: auto; }}
        .tool-declaration {{ margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #ddd; }}
        .tool-declaration:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}

        /* Agent Topology UI */
        .system-topology-details {{ background: #fff; border: 1px solid #dadce0; border-radius: 8px; padding: 16px; margin-top: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
        .system-topology-details > summary {{ font-size: 1.1em; font-weight: 500; cursor: pointer; outline: none; margin-bottom: 12px; list-style: none; display: flex; align-items: center; color: #3c4043; }}
        .system-topology-details > summary::-webkit-details-marker {{ display: none; }}
        .system-topology-details > summary::before {{ content: '▼'; font-size: 0.8em; margin-right: 8px; transition: transform 0.2s; }}
        .system-topology-details:not([open]) > summary::before {{ transform: rotate(-90deg); }}

        .topology-container {{ background: #f8f9fa; border-radius: 8px; padding: 16px; margin-top: 8px; border: 1px solid #dadce0; overflow-x: auto; }}
        .agent-node {{ background: #fff; border: 1px solid #dadce0; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); min-width: 300px; max-width: 600px; }}
        .agent-node-header {{ padding: 10px 16px; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 8px; background: #f1f3f4; border-top-left-radius: 8px; border-top-right-radius: 8px; }}
        .agent-name {{ font-weight: 600; color: #1a73e8; }}
        .agent-type {{ font-size: 11px; background: #e8eaed; padding: 2px 8px; border-radius: 12px; color: #5f6368; font-family: monospace; }}
        .agent-node-body {{ padding: 12px 16px; font-size: 13px; color: #3c4043; }}
        .agent-desc {{ margin-bottom: 8px; }}
        .agent-inst details, .agent-tools details {{ margin-bottom: 8px; padding: 8px; }}
        .agent-inst summary, .agent-tools summary {{ cursor: pointer; font-weight: 500; color: #5f6368; font-size: 12px; outline: none; margin-bottom: 0; }}
        .inst-content, .tools-content {{ margin-top: 8px; padding: 8px; background: #f8f9fa; border-radius: 4px; border: 1px solid #eee; white-space: pre-wrap; word-wrap: break-word; font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto; }}
        .sub-agents-container {{ margin-top: 16px; padding-left: 24px; border-left: 2px solid #dadce0; position: relative; }}
        .sub-agents-container::before {{ content: ''; position: absolute; top: -16px; left: -2px; width: 2px; height: 16px; background: #dadce0; }}

        /* Multi-turn Agent Trace UI */
        .conversation-trace-details {{ background: #fff; border: 1px solid #dadce0; border-radius: 8px; padding: 16px; margin-top: 0; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
        .conversation-trace-details > summary {{ font-size: 1.1em; font-weight: 500; cursor: pointer; outline: none; margin-bottom: 8px; list-style: none; display: flex; align-items: center; color: #3c4043; }}
        .conversation-trace-details > summary::-webkit-details-marker {{ display: none; }}
        .conversation-trace-details > summary::before {{ content: '▼'; font-size: 0.8em; margin-right: 8px; transition: transform 0.2s; }}
        .conversation-trace-details:not([open]) > summary::before {{ transform: rotate(-90deg); }}

        .agent-timeline {{ position: relative; padding-left: 32px; margin-top: 16px; font-family: 'Roboto', sans-serif; }}
        .agent-timeline::before {{ content: ''; position: absolute; top: 0; bottom: 0; left: 11px; width: 2px; background: #e8eaed; }}

        .turn-details {{ margin-bottom: 16px; padding: 0; border: none; }}
        .turn-summary {{ list-style: none; outline: none; cursor: pointer; display: block; margin-left: -32px; padding-left: 32px; }}
        .turn-summary::-webkit-details-marker {{ display: none; }}
        .turn-header {{ margin: 16px 0 16px -32px; position: relative; z-index: 1; display: inline-flex; align-items: center; }}

        .turn-badge {{ display: inline-flex; align-items: center; background: #f8f9fa; color: #5f6368; padding: 4px 12px; border-radius: 16px; font-size: 11px; font-weight: 600; border: 1px solid #dadce0; letter-spacing: 0.5px; }}
        .turn-divider {{ color: #dadce0; margin: 0 6px; font-weight: normal; }}
        .turn-badge::before {{ content: '▼'; margin-right: 6px; font-size: 0.8em; display: inline-block; transition: transform 0.2s; }}
        .turn-details:not([open]) .turn-badge::before {{ transform: rotate(-90deg); }}

        .timeline-item {{ position: relative; margin-bottom: 16px; }}
        .timeline-icon {{ position: absolute; left: -32px; top: 0; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #e8f0fe; border: 2px solid #fff; color: #1a73e8; z-index: 1; box-sizing: border-box; margin-left: 0; }}
        .timeline-icon.user {{ background: #f3e8fd; color: #9334e6; }}
        .timeline-icon.tool {{ background: #e6f4ea; color: #1e8e3e; }}
        .timeline-content {{ background: #fff; border: 1px solid #dadce0; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); overflow: hidden; }}
        .event-header {{ padding: 12px 16px 8px; font-size: 12px; font-weight: 600; display: flex; align-items: baseline; gap: 8px; }}
        .event-author {{ color: #1a73e8; letter-spacing: 0.5px; text-transform: uppercase; }}
        .event-author.user {{ color: #9334e6; }}
        .event-author.tool {{ color: #1e8e3e; }}
        .event-role {{ color: #80868b; font-weight: normal; font-size: 11px; font-family: monospace;}}
        .event-body {{ padding: 0 16px 12px; font-size: 14px; color: #202124; line-height: 1.5; }}
        .dark-code-block {{ background: #0e111a; color: #d4d4d4; padding: 12px; border-radius: 6px; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; margin: 8px 0 0 0; overflow-x: auto; border: 1px solid #3c4043; }}
        .function-call-title {{ color: #e37400; font-weight: 600; font-size: 12px; margin-top: 8px; display: flex; align-items: center; gap: 4px; }}
        .function-response-title {{ color: #0f9d58; font-weight: 600; font-size: 12px; margin-top: 8px; display: flex; align-items: center; gap: 4px; }}
        .agent-trace-container {{ max-height: 600px; overflow-x: auto; overflow-y: auto; padding-right: 8px; border: 1px solid #eee; padding: 12px; border-radius: 8px; background: #fafafa; }}

        /* Collapsible Metrics */
        .metric-details {{ background: #fff; border: 1px solid #dadce0; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); overflow: hidden; }}
        .metric-summary {{ list-style: none; cursor: pointer; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; background: #f8f9fa; margin: 0; outline: none; }}
        .metric-summary::-webkit-details-marker {{ display: none; }}
        .metric-details[open] .metric-summary {{ border-bottom: 1px solid #dadce0; }}
        .metric-name-wrapper {{ display: flex; align-items: center; font-weight: 600; color: #3c4043; font-size: 14px; }}
        .metric-name-wrapper::before {{ content: '►'; font-size: 0.8em; margin-right: 8px; transition: transform 0.2s; color: #5f6368; }}
        .metric-details[open] .metric-name-wrapper::before {{ transform: rotate(90deg); }}
        .metric-score {{ font-weight: bold; font-size: 16px; color: #1a73e8; }}
        .metric-body {{ padding: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Evaluation Report</h1>
        <div id="summary-section"></div>
        <div id="details-section"></div>
    </div>
    <script>
        var vizData_vertex_eval_sdk = JSON.parse(new TextDecoder().decode(Uint8Array.from(atob("{payload_b64}"), c => c.charCodeAt(0))));

        function formatDictVals(obj) {{
            if (typeof obj === 'string') return obj;
            if (obj === undefined || obj === null) return '';
            if (typeof obj !== 'object') return String(obj);
            if (Array.isArray(obj)) return JSON.stringify(obj);
            return Object.entries(obj).map(([k,v]) => `${{k}}=${{formatDictVals(v)}}`).join(', ');
        }}

        function formatToolDeclarations(toolDeclarations) {{
            if (!toolDeclarations) return '';
            let functions = [];
            if (Array.isArray(toolDeclarations)) {{
                toolDeclarations.forEach(tool => {{
                    if (tool.function_declarations) {{
                        functions = functions.concat(tool.function_declarations);
                    }} else if (tool.name && tool.parameters) {{
                        functions.push(tool);
                    }}
                }});
            }} else if (typeof toolDeclarations === 'object' && toolDeclarations.function_declarations) {{
                functions = toolDeclarations.function_declarations;
            }}

            if (functions.length === 0) {{
                 return `<pre class="raw-json-container">${{DOMPurify.sanitize(JSON.stringify(toolDeclarations, null, 2))}}</pre>`;
            }}

            let html = '<div class="tool-declarations-container">';
            functions.forEach(func => {{
                html += '<div class="tool-declaration">';
                const params = func.parameters && func.parameters.properties ? func.parameters.properties : {{}};
                const requiredParams = func.parameters && func.parameters.required ? new Set(func.parameters.required) : new Set();
                const paramStrings = Object.keys(params).map(p => `${{DOMPurify.sanitize(p)}}: ${{DOMPurify.sanitize(params[p].type)}}`).join(', ');
                html += `<strong>${{DOMPurify.sanitize(func.name)}}</strong>(${{paramStrings}})<br>`;
                if(func.description) html += `<em>${{DOMPurify.sanitize(func.description)}}</em><br>`;
                if(Object.keys(params).length > 0) html += 'Parameters:<br>';
                Object.keys(params).forEach(p => {{
                    html += `&nbsp;&nbsp;- ${{DOMPurify.sanitize(p)}}: ${{DOMPurify.sanitize(params[p].description || '')}} ${{requiredParams.has(p) ? '<strong>(required)</strong>' : ''}}<br>`;
                }});
                html += '</div>';
            }});
            html += '</div>';
            return html;
        }}

        function formatSystemTopology(agents) {{
            if (!agents || Object.keys(agents).length === 0) return '<p>No agent configurations provided.</p>';

            const allSubAgents = new Set();
            Object.values(agents).forEach(agent => {{
                if (agent.sub_agents) {{
                    agent.sub_agents.forEach(sa => allSubAgents.add(sa));
                }}
            }});

            const roots = Object.keys(agents).filter(id => !allSubAgents.has(id));
            if (roots.length === 0) {{
                roots.push(Object.keys(agents)[0]);
            }}

            let html = '<div class="topology-container">';

            const renderAgent = (agentId, visited) => {{
                if (visited.has(agentId)) return '';
                visited.add(agentId);

                const agent = agents[agentId];
                if (!agent) return '';

                let nodeHtml = `<div class="agent-node">`;
                nodeHtml += `<div class="agent-node-header">
                               <span style="font-size:16px;">🤖</span>
                               <span class="agent-name">${{DOMPurify.sanitize(agentId)}}</span>
                               ${{agent.agent_type ? `<span class="agent-type">${{DOMPurify.sanitize(agent.agent_type)}}</span>` : ''}}
                             </div>`;

                nodeHtml += `<div class="agent-node-body">`;
                if (agent.description) {{
                    nodeHtml += `<div class="agent-desc"><strong>Role:</strong> ${{DOMPurify.sanitize(agent.description)}}</div>`;
                }}
                if (agent.instruction) {{
                    nodeHtml += `<div class="agent-inst">
                                    <details>
                                        <summary>System Instructions</summary>
                                        <div class="inst-content">${{DOMPurify.sanitize(agent.instruction)}}</div>
                                    </details>
                                 </div>`;
                }}
                if (agent.tools && agent.tools.length > 0) {{
                    nodeHtml += `<div class="agent-tools">
                                    <details>
                                        <summary>Tools (${{agent.tools.length}})</summary>
                                        <div class="tools-content" style="padding:0; border:none; background:transparent;">
                                            ${{formatToolDeclarations(agent.tools)}}
                                        </div>
                                    </details>
                                 </div>`;
                }}

                if (agent.sub_agents && agent.sub_agents.length > 0) {{
                    nodeHtml += `<div class="sub-agents-container">`;
                    agent.sub_agents.forEach(sa => {{
                        nodeHtml += renderAgent(sa, new Set(visited));
                    }});
                    nodeHtml += `</div>`;
                }}

                nodeHtml += `</div></div>`;
                return nodeHtml;
            }};

            roots.forEach(rootId => {{
                html += renderAgent(rootId, new Set());
            }});

            html += '</div>';
            return html;
        }}

        function formatAgentData(agentData) {{
            let data = agentData;
            if (typeof data === 'string') {{
                try {{ data = JSON.parse(data); }} catch(e) {{ return ''; }}
            }}
            if (!data || !data.turns) return '';

            let html = '<div class="agent-timeline">';
            data.turns.forEach((turn, idx) => {{
                const tIndex = turn.turn_index !== undefined ? turn.turn_index : (idx + 1);
                const tId = turn.turn_id ? DOMPurify.sanitize(String(turn.turn_id)) : `turn-${{String(tIndex).padStart(3, '0')}}`;

                html += `<details open class="turn-details">`;
                html += `<summary class="turn-summary"><div class="turn-header"><span class="turn-badge">TURN ${{tIndex}} <span class="turn-divider">|</span> ID: ${{tId}}</span></div></summary>`;

                if (turn.events) {{
                    turn.events.forEach(event => {{
                        const role = (event.content && event.content.role) ? event.content.role.toLowerCase() : 'model';
                        const author = event.author ? event.author : role;

                        let iconClass = 'model';
                        if (role === 'user') iconClass = 'user';
                        if (role === 'tool') iconClass = 'tool';

                        let svgIcon = '';
                        if (iconClass === 'user') {{
                            svgIcon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;
                        }} else if (iconClass === 'tool') {{
                            svgIcon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>`;
                        }} else {{
                            svgIcon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8" y2="16"></line><line x1="16" y1="16" x2="16" y2="16"></line></svg>`;
                        }}

                        html += `<div class="timeline-item">
                                    <div class="timeline-icon ${{iconClass}}">${{svgIcon}}</div>
                                    <div class="timeline-content">
                                        <div class="event-header">
                                            <span class="event-author ${{iconClass}}">${{DOMPurify.sanitize(author)}}</span>
                                            <span class="event-role">${{DOMPurify.sanitize(role)}}</span>
                                        </div>
                                        <div class="event-body">`;

                        if (event.content && event.content.parts) {{
                            event.content.parts.forEach(part => {{
                                if (part.text) {{
                                    html += `<div>${{DOMPurify.sanitize(marked.parse(String(part.text)))}}</div>`;
                                }} else if (part.function_call) {{
                                    const fnName = part.function_call.name;
                                    const fnArgs = JSON.stringify(part.function_call.args, null, 2);
                                    html += `<div class="function-call-title">&gt;_ Function Call: ${{DOMPurify.sanitize(fnName)}}</div>
                                             <pre class="dark-code-block">${{DOMPurify.sanitize(fnArgs)}}</pre>`;
                                }} else if (part.function_response) {{
                                    const fnName = part.function_response.name;
                                    let fnRes = part.function_response.response;
                                    if(typeof fnRes === 'object' && fnRes !== null && fnRes.result !== undefined) {{
                                        fnRes = fnRes.result;
                                    }}
                                    const fnResStr = JSON.stringify(fnRes, null, 2);
                                    html += `<div class="function-response-title">
                                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                                                Tool Output: ${{DOMPurify.sanitize(fnName)}}
                                             </div>
                                             <pre class="dark-code-block">${{DOMPurify.sanitize(fnResStr)}}</pre>`;
                                }}
                            }});
                        }} else {{
                             html += `<div><pre class="raw-json-container">${{DOMPurify.sanitize(JSON.stringify(event.content, null, 2))}}</pre></div>`;
                        }}

                        html += `</div></div></div>`;
                    }});
                }}
                html += `</details>`;
            }});
            html += '</div>';
            return html;
        }}

        function renderSummary(summaryMetrics) {{
            const container = document.getElementById('summary-section');
            let content = '<h2>Summary Metrics</h2>';
            if (!summaryMetrics || summaryMetrics.length === 0) {{ container.innerHTML = content + '<p>No summary metrics.</p>'; return; }}
            let table = '<table><thead><tr><th>Metric</th><th>Mean Score</th><th>Std. Dev.</th></tr></thead><tbody>';
            summaryMetrics.forEach(m => {{
                table += `<tr><td>${{m.metric_name || 'N/A'}}</td><td>${{m.mean_score != null ? m.mean_score.toFixed(4) : 'N/A'}}</td><td>${{m.stdev_score != null ? m.stdev_score.toFixed(4) : 'N/A'}}</td></tr>`;
            }});
            container.innerHTML = content + table + '</tbody></table>';
        }}

        function renderDetails(caseResults, metadata) {{
            const container = document.getElementById('details-section');
            container.innerHTML = '<h2>Detailed Results</h2>';
            if (!caseResults || caseResults.length === 0) {{ container.innerHTML += '<p>No detailed results.</p>'; return; }}

            const datasetRows = metadata && metadata.dataset ? metadata.dataset : [];

            caseResults.forEach((caseResult, i) => {{
                const original_case = datasetRows[caseResult.eval_case_index] || {{}};

                const isValEmpty = (val) => !val || val === 'None' || val === 'nan' || String(val).trim() === '';

                const promptText = isValEmpty(original_case.prompt_display_text) ? '' : original_case.prompt_display_text;
                const promptJson = original_case.prompt_raw_json;
                const reference = isValEmpty(original_case.reference) ? '' : original_case.reference;
                const responseText = isValEmpty(original_case.response_display_text) ? '' : original_case.response_display_text;
                const responseJson = original_case.response_raw_json;

                let agentData = original_case.agent_data;
                if (typeof agentData === 'string') {{
                    try {{ agentData = JSON.parse(agentData); }} catch(e) {{}}
                }}
                const isAgentEval = !!agentData;

                let card = `<details open><summary style="font-size: 1.2em;">Case #${{caseResult.eval_case_index != null ? caseResult.eval_case_index : i}}</summary>`;

                if (isAgentEval && agentData.agents && Object.keys(agentData.agents).length > 0) {{
                    card += `<details open class="system-topology-details">
                                <summary>System Topology</summary>
                                ${{formatSystemTopology(agentData.agents)}}
                             </details>`;
                }}

                card += `<div class="case-content-wrapper">`;

                const hasMainContent = promptText || responseText || reference;

                if (hasMainContent) {{
                    card += `<div class="case-content-main">`;
                    if (promptText) {{
                        card += `<div class="prompt-container"><strong>Prompt:</strong><br>${{DOMPurify.sanitize(marked.parse(String(promptText)))}}</div>`;
                    }}
                    if (promptJson && promptJson !== '""' && promptJson !== 'null' && promptJson !== '{{}}') {{
                        card += `<details class="raw-json-details"><summary>View Raw Prompt JSON</summary><pre class="raw-json-container">${{DOMPurify.sanitize(promptJson)}}</pre></details>`;
                    }}

                    if (reference) {{
                        card += `<div class="reference-container"><strong>Reference:</strong><br>${{DOMPurify.sanitize(marked.parse(String(reference)))}}</div>`;
                    }}

                    if (responseText) {{
                        const responseTitle = isAgentEval ? 'Final Response' : 'Candidate Response';
                        card += `<div class="response-container"><h4>${{responseTitle}}</h4>${{DOMPurify.sanitize(marked.parse(String(responseText)))}}</div>`;
                    }}
                    if (responseJson && responseJson !== '""' && responseJson !== 'null' && responseJson !== '{{}}') {{
                        card += `<details class="raw-json-details"><summary>View Raw Response JSON</summary><pre class="raw-json-container">${{DOMPurify.sanitize(responseJson)}}</pre></details>`;
                    }}
                    card += `</div>`;
                }}

                if (isAgentEval && agentData.turns) {{
                    let traceContent = formatAgentData(agentData);
                    const sidebarStyle = hasMainContent ? '' : 'flex: 1 1 100%;';

                    card += `<details open class="case-content-sidebar conversation-trace-details" style="${{sidebarStyle}}">
                                <summary>Conversation Trace</summary>
                                <div style="font-size:13px; color:#5f6368; margin-bottom:12px;">Sequence of multi-agent events across turns</div>
                                <div class="agent-trace-container">${{traceContent}}</div>
                             </details>`;
                }}

                card += `</div>`;

                let metricTable = '<h3 style="margin-top:24px;">Evaluation Metrics</h3><div class="metrics-list">';
                const candidateMetrics = (caseResult.response_candidate_results && caseResult.response_candidate_results[0] && caseResult.response_candidate_results[0].metric_results) || {{}};
                Object.entries(candidateMetrics).forEach(([name, val]) => {{
                    let metricNameCell = `<strong>${{name}}</strong>`;
                    let explanationHandled = false;
                    let bubbles = '';

                    if (name.startsWith('hallucination') && val.explanation) {{
                        try {{
                            const explanationData = typeof val.explanation === 'string' ? JSON.parse(val.explanation) : val.explanation;
                            if (Array.isArray(explanationData) && explanationData.length > 0) {{
                                let sentenceGroups = [];
                                if (explanationData[0].explanation && Array.isArray(explanationData[0].explanation)) {{
                                    explanationData.forEach(item => {{
                                        if(item.explanation && Array.isArray(item.explanation)) {{
                                            sentenceGroups.push(item.explanation);
                                        }}
                                    }});
                                }} else if (explanationData[0].sentence) {{
                                    sentenceGroups.push(explanationData);
                                }}

                                if(sentenceGroups.length > 0) {{
                                    sentenceGroups.forEach(sentenceList => {{
                                        bubbles += '<div class="rubric-bubble-container" style="margin-top: 8px;">';
                                        sentenceList.forEach(item => {{
                                            let sentence = item.sentence || 'N/A';
                                            const label = item.label ? item.label.toLowerCase() : '';
                                            const isPass = label === 'no_rad' || label === 'supported';
                                            const verdictText = isPass ? '<span class="pass">Pass</span>' : '<span class="fail">Fail</span>';
                                            if (isPass) {{
                                                sentence = `"${{sentence}}" is grounded`;
                                            }}
                                            const rationale = item.rationale || 'N/A';
                                            const itemJson = JSON.stringify(item, null, 2);
                                            bubbles += `
                                                <details class="rubric-details">
                                                    <summary class="rubric-bubble">${{verdictText}}: ${{DOMPurify.sanitize(sentence)}}</summary>
                                                    <div class="explanation" style="padding: 10px 0 0 20px;">${{DOMPurify.sanitize(rationale)}}</div>
                                                    <pre class="raw-json-container">${{DOMPurify.sanitize(itemJson)}}</pre>
                                                </details>`;
                                        }});
                                        bubbles += '</div>';
                                    }});
                                    explanationHandled = true;
                                }}
                            }}
                        }} catch (e) {{
                            console.error("Failed to parse hallucination explanation:", e);
                        }}
                    }} else if (name.startsWith('safety') && val.score != null) {{
                        try {{
                            bubbles += '<div class="rubric-bubble-container" style="margin-top: 8px;">';
                            const verdictText = val.score >= 1.0 ? '<span class="pass">Pass</span>' : '<span class="fail">Fail</span>';
                            const explanation = val.explanation || (val.score >= 1.0 ? 'Safety check passed' : 'Safety check failed');
                            const itemJson = JSON.stringify(val, null, 2);
                            bubbles += `
                                <details class="rubric-details">
                                    <summary class="rubric-bubble">${{verdictText}}: ${{DOMPurify.sanitize(explanation)}}</summary>
                                    <pre class="raw-json-container">${{DOMPurify.sanitize(itemJson)}}</pre>
                                </details>`;
                            bubbles += '</div>';
                            explanationHandled = true;
                        }} catch (e) {{
                            console.error("Failed to process safety metric:", e);
                        }}
                    }}

                    if (!bubbles && val.rubric_verdicts && val.rubric_verdicts.length > 0) {{
                        bubbles += '<div class="rubric-bubble-container" style="margin-top: 8px;">';
                        val.rubric_verdicts.forEach(verdict => {{
                            const rubricDescription = verdict.evaluated_rubric && verdict.evaluated_rubric.content && verdict.evaluated_rubric.content.property ? verdict.evaluated_rubric.content.property.description : 'N/A';
                            const verdictText = verdict.verdict ? '<span class="pass">Pass</span>' : '<span class="fail">Fail</span>';
                            const verdictJson = JSON.stringify(verdict, null, 2);
                            bubbles += `
                                <details class="rubric-details">
                                    <summary class="rubric-bubble">${{verdictText}}: ${{DOMPurify.sanitize(rubricDescription)}}</summary>
                                    <pre class="raw-json-container">${{DOMPurify.sanitize(verdictJson)}}</pre>
                                </details>`;
                        }});
                        bubbles += '</div>';
                    }}

                    let scoreDisplay = val.score != null ? val.score.toFixed(2) : 'N/A';
                    let metricContent = '';

                    if (val.explanation && !explanationHandled) {{
                        metricContent += `<div class="explanation" style="margin-top:0; margin-bottom: 12px;">${{DOMPurify.sanitize(marked.parse(String(val.explanation)))}}</div>`;
                    }}
                    if (bubbles) {{
                        metricContent += bubbles;
                    }}
                    if (!metricContent) {{
                        metricContent = `<div style="color: #80868b; font-style: italic; font-size: 13px;">No additional details.</div>`;
                    }}

                    metricTable += `
                        <details class="metric-details" open>
                            <summary class="metric-summary">
                                <div class="metric-name-wrapper">${{DOMPurify.sanitize(name)}}</div>
                                <div class="metric-score">${{DOMPurify.sanitize(scoreDisplay)}}</div>
                            </summary>
                            <div class="metric-body">
                                ${{metricContent}}
                            </div>
                        </details>
                    `;
                }});
                metricTable += '</div>';
                card += metricTable + '</details>';
                container.innerHTML += card;
            }});
        }}

        renderSummary(vizData_vertex_eval_sdk.summary_metrics);
        renderDetails(vizData_vertex_eval_sdk.eval_case_results, vizData_vertex_eval_sdk.metadata);
    </script>
</body>
</html>
"""
    )


def _get_comparison_html(eval_result_json: str) -> str:
    """Returns a self-contained HTML for a side-by-side eval comparison."""
    payload_b64 = _encode_to_base64(eval_result_json)
    return textwrap.dedent(
        f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Eval Comparison Report</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>
    <style>

        body {{ font-family: 'Roboto', 'Helvetica', sans-serif; margin: 2em; background-color: #f8f9fa; color: #202124; }}
        .container {{ max-width: 95%; margin: 20px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
        h1, h2, h3, h4 {{ color: #3c4043; }}
        h1 {{ border-bottom: 2px solid #4285F4; padding-bottom: 8px; }}
        h2 {{ border-bottom: 1px solid #dadce0; padding-bottom: 8px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
        th, td {{ border: 1px solid #dadce0; padding: 12px; text-align: left; vertical-align: top; }}
        th {{ background-color: #f2f2f2; font-weight: 500; }}
        details {{ border: 1px solid #dadce0; border-radius: 8px; padding: 24px; margin-bottom: 24px; background: #fff; }}
        summary {{ font-weight: 500; font-size: 1.2em; cursor: pointer; }}
        .prompt-container {{ background-color: #e8f0fe; padding: 16px; margin-bottom: 16px; border-radius: 8px; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word; }}
        .responses-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-top: 16px;}}
        .response-column {{ border: 1px solid #e0e0e0; padding: 16px; border-radius: 8px; background: #f9f9f9; }}
        .response-text-container {{ background-color: #fff; padding: 12px; margin-top: 8px; border-radius: 4px; border: 1px solid #eee; white-space: pre-wrap; word-wrap: break-word; max-height: 400px; overflow-y: auto; overflow-wrap: break-word; }}
        .explanation {{ color: #5f6368; font-style: italic; font-size: 0.9em; padding-top: 8px; }}
        .raw-json-details summary {{ font-size: 0.9em; cursor: pointer; color: #5f6368;}}
        .raw-json-container {{ white-space: pre-wrap; word-wrap: break-word; max-height: 300px; overflow-y: auto; background-color: #f1f1f1; padding: 10px; border-radius: 4px; margin-top: 8px; }}

        .rubric-bubble-container {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .rubric-details {{ border: none; padding: 0; margin: 0; }}
        .rubric-bubble {{ display: inline-flex; align-items: center; background-color: #e8f0fe; color: #1967d2; border-radius: 16px; padding: 8px 12px; font-size: 0.9em; cursor: pointer; list-style: none; }}
        .rubric-bubble::-webkit-details-marker {{ display: none; }}
        .rubric-bubble::before {{ content: '►'; margin-right: 8px; font-size: 0.8em; transition: transform 0.2s; }}
        .rubric-details[open] > .rubric-bubble::before {{ transform: rotate(90deg); }}
        .pass {{ color: green; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}

        /* Tool Declarations */
        .tool-declarations-container {{ background-color: #f1f1f1; padding: 10px; border-radius: 4px; margin-top: 8px; max-height: 300px; overflow-y: auto; }}
        .tool-declaration {{ margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #ddd; }}
        .tool-declaration:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}

        /* Agent Topology UI */
        .system-topology-details {{ background: #fff; border: 1px solid #dadce0; border-radius: 8px; padding: 16px; margin-top: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
        .system-topology-details > summary {{ font-size: 1.1em; font-weight: 500; cursor: pointer; outline: none; margin-bottom: 12px; list-style: none; display: flex; align-items: center; color: #3c4043; }}
        .system-topology-details > summary::-webkit-details-marker {{ display: none; }}
        .system-topology-details > summary::before {{ content: '▼'; font-size: 0.8em; margin-right: 8px; transition: transform 0.2s; }}
        .system-topology-details:not([open]) > summary::before {{ transform: rotate(-90deg); }}

        .topology-container {{ background: #f8f9fa; border-radius: 8px; padding: 16px; margin-top: 8px; border: 1px solid #dadce0; overflow-x: auto; }}
        .agent-node {{ background: #fff; border: 1px solid #dadce0; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); min-width: 300px; max-width: 600px; }}
        .agent-node-header {{ padding: 10px 16px; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 8px; background: #f1f3f4; border-top-left-radius: 8px; border-top-right-radius: 8px; }}
        .agent-name {{ font-weight: 600; color: #1a73e8; }}
        .agent-type {{ font-size: 11px; background: #e8eaed; padding: 2px 8px; border-radius: 12px; color: #5f6368; font-family: monospace; }}
        .agent-node-body {{ padding: 12px 16px; font-size: 13px; color: #3c4043; }}
        .agent-desc {{ margin-bottom: 8px; }}
        .agent-inst details, .agent-tools details {{ margin-bottom: 8px; padding: 8px; }}
        .agent-inst summary, .agent-tools summary {{ cursor: pointer; font-weight: 500; color: #5f6368; font-size: 12px; outline: none; margin-bottom: 0; }}
        .inst-content, .tools-content {{ margin-top: 8px; padding: 8px; background: #f8f9fa; border-radius: 4px; border: 1px solid #eee; white-space: pre-wrap; word-wrap: break-word; font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto; }}
        .sub-agents-container {{ margin-top: 16px; padding-left: 24px; border-left: 2px solid #dadce0; position: relative; }}
        .sub-agents-container::before {{ content: ''; position: absolute; top: -16px; left: -2px; width: 2px; height: 16px; background: #dadce0; }}

        /* Multi-turn Agent Trace UI */
        .conversation-trace-details {{ background: #fff; border: 1px solid #dadce0; border-radius: 8px; padding: 16px; margin-top: 0; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
        .conversation-trace-details > summary {{ font-size: 1.1em; font-weight: 500; cursor: pointer; outline: none; margin-bottom: 8px; list-style: none; display: flex; align-items: center; color: #3c4043; }}
        .conversation-trace-details > summary::-webkit-details-marker {{ display: none; }}
        .conversation-trace-details > summary::before {{ content: '▼'; font-size: 0.8em; margin-right: 8px; transition: transform 0.2s; }}
        .conversation-trace-details:not([open]) > summary::before {{ transform: rotate(-90deg); }}

        .agent-timeline {{ position: relative; padding-left: 32px; margin-top: 16px; font-family: 'Roboto', sans-serif; }}
        .agent-timeline::before {{ content: ''; position: absolute; top: 0; bottom: 0; left: 11px; width: 2px; background: #e8eaed; }}

        .turn-details {{ margin-bottom: 16px; padding: 0; border: none; }}
        .turn-summary {{ list-style: none; outline: none; cursor: pointer; display: block; margin-left: -32px; padding-left: 32px; }}
        .turn-summary::-webkit-details-marker {{ display: none; }}
        .turn-header {{ margin: 16px 0 16px -32px; position: relative; z-index: 1; display: inline-flex; align-items: center; }}

        .turn-badge {{ display: inline-flex; align-items: center; background: #f8f9fa; color: #5f6368; padding: 4px 12px; border-radius: 16px; font-size: 11px; font-weight: 600; border: 1px solid #dadce0; letter-spacing: 0.5px; }}
        .turn-divider {{ color: #dadce0; margin: 0 6px; font-weight: normal; }}
        .turn-badge::before {{ content: '▼'; margin-right: 6px; font-size: 0.8em; display: inline-block; transition: transform 0.2s; }}
        .turn-details:not([open]) .turn-badge::before {{ transform: rotate(-90deg); }}

        .timeline-item {{ position: relative; margin-bottom: 16px; }}
        .timeline-icon {{ position: absolute; left: -32px; top: 0; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #e8f0fe; border: 2px solid #fff; color: #1a73e8; z-index: 1; box-sizing: border-box; margin-left: 0; }}
        .timeline-icon.user {{ background: #f3e8fd; color: #9334e6; }}
        .timeline-icon.tool {{ background: #e6f4ea; color: #1e8e3e; }}
        .timeline-content {{ background: #fff; border: 1px solid #dadce0; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); overflow: hidden; }}
        .event-header {{ padding: 12px 16px 8px; font-size: 12px; font-weight: 600; display: flex; align-items: baseline; gap: 8px; }}
        .event-author {{ color: #1a73e8; letter-spacing: 0.5px; text-transform: uppercase; }}
        .event-author.user {{ color: #9334e6; }}
        .event-author.tool {{ color: #1e8e3e; }}
        .event-role {{ color: #80868b; font-weight: normal; font-size: 11px; font-family: monospace;}}
        .event-body {{ padding: 0 16px 12px; font-size: 14px; color: #202124; line-height: 1.5; }}
        .dark-code-block {{ background: #0e111a; color: #d4d4d4; padding: 12px; border-radius: 6px; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; margin: 8px 0 0 0; overflow-x: auto; border: 1px solid #3c4043; }}
        .function-call-title {{ color: #e37400; font-weight: 600; font-size: 12px; margin-top: 8px; display: flex; align-items: center; gap: 4px; }}
        .function-response-title {{ color: #0f9d58; font-weight: 600; font-size: 12px; margin-top: 8px; display: flex; align-items: center; gap: 4px; }}
        .agent-trace-container {{ max-height: 600px; overflow-x: auto; overflow-y: auto; padding-right: 8px; border: 1px solid #eee; padding: 12px; border-radius: 8px; background: #fafafa; }}

        /* Collapsible Metrics */
        .metric-details {{ background: #fff; border: 1px solid #dadce0; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); overflow: hidden; }}
        .metric-summary {{ list-style: none; cursor: pointer; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; background: #f8f9fa; margin: 0; outline: none; }}
        .metric-summary::-webkit-details-marker {{ display: none; }}
        .metric-details[open] .metric-summary {{ border-bottom: 1px solid #dadce0; }}
        .metric-name-wrapper {{ display: flex; align-items: center; font-weight: 600; color: #3c4043; font-size: 14px; }}
        .metric-name-wrapper::before {{ content: '►'; font-size: 0.8em; margin-right: 8px; transition: transform 0.2s; color: #5f6368; }}
        .metric-details[open] .metric-name-wrapper::before {{ transform: rotate(90deg); }}
        .metric-score {{ font-weight: bold; font-size: 16px; color: #1a73e8; }}
        .metric-body {{ padding: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Eval Comparison Report</h1>
        <div id="summary-section"></div>
        <div id="details-section"></div>
    </div>
    <script>
        var vizData_vertex_eval_sdk = JSON.parse(new TextDecoder().decode(Uint8Array.from(atob("{payload_b64}"), c => c.charCodeAt(0))));

        function formatToolDeclarations(toolDeclarations) {{
            if (!toolDeclarations) return '';
            let functions = [];
            if (Array.isArray(toolDeclarations)) {{
                toolDeclarations.forEach(tool => {{
                    if (tool.function_declarations) {{
                        functions = functions.concat(tool.function_declarations);
                    }} else if (tool.name && tool.parameters) {{
                        functions.push(tool);
                    }}
                }});
            }} else if (typeof toolDeclarations === 'object' && toolDeclarations.function_declarations) {{
                functions = toolDeclarations.function_declarations;
            }}

            if (functions.length === 0) {{
                 return `<pre class="raw-json-container">${{DOMPurify.sanitize(JSON.stringify(toolDeclarations, null, 2))}}</pre>`;
            }}

            let html = '<div class="tool-declarations-container">';
            functions.forEach(func => {{
                html += '<div class="tool-declaration">';
                const params = func.parameters && func.parameters.properties ? func.parameters.properties : {{}};
                const requiredParams = func.parameters && func.parameters.required ? new Set(func.parameters.required) : new Set();
                const paramStrings = Object.keys(params).map(p => `${{DOMPurify.sanitize(p)}}: ${{DOMPurify.sanitize(params[p].type)}}`).join(', ');
                html += `<strong>${{DOMPurify.sanitize(func.name)}}</strong>(${{paramStrings}})<br>`;
                if(func.description) html += `<em>${{DOMPurify.sanitize(func.description)}}</em><br>`;
                if(Object.keys(params).length > 0) html += 'Parameters:<br>';
                Object.keys(params).forEach(p => {{
                    html += `&nbsp;&nbsp;- ${{DOMPurify.sanitize(p)}}: ${{DOMPurify.sanitize(params[p].description || '')}} ${{requiredParams.has(p) ? '<strong>(required)</strong>' : ''}}<br>`;
                }});
                html += '</div>';
            }});
            html += '</div>';
            return html;
        }}

        function formatSystemTopology(agents) {{
            if (!agents || Object.keys(agents).length === 0) return '<p>No agent configurations provided.</p>';

            const allSubAgents = new Set();
            Object.values(agents).forEach(agent => {{
                if (agent.sub_agents) {{
                    agent.sub_agents.forEach(sa => allSubAgents.add(sa));
                }}
            }});

            const roots = Object.keys(agents).filter(id => !allSubAgents.has(id));
            if (roots.length === 0) {{
                roots.push(Object.keys(agents)[0]);
            }}

            let html = '<div class="topology-container">';

            const renderAgent = (agentId, visited) => {{
                if (visited.has(agentId)) return '';
                visited.add(agentId);

                const agent = agents[agentId];
                if (!agent) return '';

                let nodeHtml = `<div class="agent-node">`;
                nodeHtml += `<div class="agent-node-header">
                               <span style="font-size:16px;">🤖</span>
                               <span class="agent-name">${{DOMPurify.sanitize(agentId)}}</span>
                               ${{agent.agent_type ? `<span class="agent-type">${{DOMPurify.sanitize(agent.agent_type)}}</span>` : ''}}
                             </div>`;

                nodeHtml += `<div class="agent-node-body">`;
                if (agent.description) {{
                    nodeHtml += `<div class="agent-desc"><strong>Role:</strong> ${{DOMPurify.sanitize(agent.description)}}</div>`;
                }}
                if (agent.instruction) {{
                    nodeHtml += `<div class="agent-inst">
                                    <details>
                                        <summary>System Instructions</summary>
                                        <div class="inst-content">${{DOMPurify.sanitize(agent.instruction)}}</div>
                                    </details>
                                 </div>`;
                }}
                if (agent.tools && agent.tools.length > 0) {{
                    nodeHtml += `<div class="agent-tools">
                                    <details>
                                        <summary>Tools (${{agent.tools.length}})</summary>
                                        <div class="tools-content" style="padding:0; border:none; background:transparent;">
                                            ${{formatToolDeclarations(agent.tools)}}
                                        </div>
                                    </details>
                                 </div>`;
                }}

                if (agent.sub_agents && agent.sub_agents.length > 0) {{
                    nodeHtml += `<div class="sub-agents-container">`;
                    agent.sub_agents.forEach(sa => {{
                        nodeHtml += renderAgent(sa, new Set(visited));
                    }});
                    nodeHtml += `</div>`;
                }}

                nodeHtml += `</div></div>`;
                return nodeHtml;
            }};

            roots.forEach(rootId => {{
                html += renderAgent(rootId, new Set());
            }});

            html += '</div>';
            return html;
        }}

        function formatAgentData(agentData) {{
            let data = agentData;
            if (typeof data === 'string') {{
                try {{ data = JSON.parse(data); }} catch(e) {{ return ''; }}
            }}
            if (!data || !data.turns) return '';

            let html = '<div class="agent-timeline">';
            data.turns.forEach((turn, idx) => {{
                const tIndex = turn.turn_index !== undefined ? turn.turn_index : (idx + 1);
                const tId = turn.turn_id ? DOMPurify.sanitize(String(turn.turn_id)) : `turn-${{String(tIndex).padStart(3, '0')}}`;

                html += `<details open class="turn-details">`;
                html += `<summary class="turn-summary"><div class="turn-header"><span class="turn-badge">TURN ${{tIndex}} <span class="turn-divider">|</span> ID: ${{tId}}</span></div></summary>`;

                if (turn.events) {{
                    turn.events.forEach(event => {{
                        const role = (event.content && event.content.role) ? event.content.role.toLowerCase() : 'model';
                        const author = event.author ? event.author : role;

                        let iconClass = 'model';
                        if (role === 'user') iconClass = 'user';
                        if (role === 'tool') iconClass = 'tool';

                        let svgIcon = '';
                        if (iconClass === 'user') {{
                            svgIcon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;
                        }} else if (iconClass === 'tool') {{
                            svgIcon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>`;
                        }} else {{
                            svgIcon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8" y2="16"></line><line x1="16" y1="16" x2="16" y2="16"></line></svg>`;
                        }}

                        html += `<div class="timeline-item">
                                    <div class="timeline-icon ${{iconClass}}">${{svgIcon}}</div>
                                    <div class="timeline-content">
                                        <div class="event-header">
                                            <span class="event-author ${{iconClass}}">${{DOMPurify.sanitize(author)}}</span>
                                            <span class="event-role">${{DOMPurify.sanitize(role)}}</span>
                                        </div>
                                        <div class="event-body">`;

                        if (event.content && event.content.parts) {{
                            event.content.parts.forEach(part => {{
                                if (part.text) {{
                                    html += `<div>${{DOMPurify.sanitize(marked.parse(String(part.text)))}}</div>`;
                                }} else if (part.function_call) {{
                                    const fnName = part.function_call.name;
                                    const fnArgs = JSON.stringify(part.function_call.args, null, 2);
                                    html += `<div class="function-call-title">&gt;_ Function Call: ${{DOMPurify.sanitize(fnName)}}</div>
                                             <pre class="dark-code-block">${{DOMPurify.sanitize(fnArgs)}}</pre>`;
                                }} else if (part.function_response) {{
                                    const fnName = part.function_response.name;
                                    let fnRes = part.function_response.response;
                                    if(typeof fnRes === 'object' && fnRes !== null && fnRes.result !== undefined) {{
                                        fnRes = fnRes.result;
                                    }}
                                    const fnResStr = JSON.stringify(fnRes, null, 2);
                                    html += `<div class="function-response-title">
                                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                                                Tool Output: ${{DOMPurify.sanitize(fnName)}}
                                             </div>
                                             <pre class="dark-code-block">${{DOMPurify.sanitize(fnResStr)}}</pre>`;
                                }}
                            }});
                        }} else {{
                             html += `<div><pre class="raw-json-container">${{DOMPurify.sanitize(JSON.stringify(event.content, null, 2))}}</pre></div>`;
                        }}

                        html += `</div></div></div>`;
                    }});
                }}
                html += `</details>`;
            }});
            html += '</div>';
            return html;
        }}

        function renderSummary(summaryMetrics, metadata) {{
            const container = document.getElementById('summary-section');
            if (!summaryMetrics || summaryMetrics.length === 0) {{ container.innerHTML = '<h2>Summary Metrics</h2><p>No summary metrics.</p>'; return; }}
            const candidateNames = (metadata.candidate_names && metadata.candidate_names.length) ? metadata.candidate_names : null;
            let table = '<h2>Summary Metrics</h2><table><thead><tr><th>Metric</th><th>Mean Score</th><th>Std Dev</th><th>Win/Tie Rates</th></tr></thead><tbody>';
            summaryMetrics.forEach(m => {{
                let winRateText = 'N/A';
                if (m.win_rates) {{
                    winRateText = m.win_rates.map((rate, i) => `<b>${{candidateNames ? candidateNames[i] : `Candidate #${{i+1}}`}}</b> wins: <b>${{(rate * 100).toFixed(1)}}%</b>`).join('<br>');
                    if (m.tie_rate !== undefined) {{ winRateText += `<br>Ties: <b>${{(m.tie_rate * 100).toFixed(1)}}%</b>`; }}
                }}
                table += `<tr><td>${{m.metric_name}}</td><td>${{m.mean_score.toFixed(4)}}</td><td>${{m.stdev_score.toFixed(4)}}</td><td>${{winRateText}}</td></tr>`;
            }});
            container.innerHTML = table + '</tbody></table>';
        }}

        function renderDetails(caseResults, metadata) {{
            const container = document.getElementById('details-section');
            container.innerHTML = '<h2>Detailed Comparison</h2>';
            if (!caseResults || caseResults.length === 0) {{ container.innerHTML += '<p>No detailed results.</p>'; return; }}

            const datasetRows = metadata.dataset || [];
            const candidateNames = (metadata.candidate_names && metadata.candidate_names.length) ? metadata.candidate_names : null;

            caseResults.forEach((caseResult, i) => {{
                const original_case = datasetRows[caseResult.eval_case_index] || {{}};
                const isValEmpty = (val) => !val || val === 'None' || val === 'nan' || String(val).trim() === '';

                const promptText = isValEmpty(original_case.prompt_display_text) ? '' : original_case.prompt_display_text;
                const promptJson = original_case.prompt_raw_json;
                const agentData = original_case.agent_data;

                let card = `<details open><summary>Case #${{caseResult.eval_case_index}}</summary>`;

                if (promptText) {{
                    card += `<div class="prompt-container"><strong>Prompt:</strong><br>${{DOMPurify.sanitize(marked.parse(String(promptText)))}}</div>`;
                }}

                if (promptJson && promptJson !== '""' && promptJson !== 'null' && promptJson !== '{{}}') {{
                    card += `<details class="raw-json-details"><summary>View Raw Prompt JSON</summary><pre class="raw-json-container">${{DOMPurify.sanitize(promptJson)}}</pre></details>`;
                }}

                if (agentData) {{
                    if (typeof agentData === 'string') {{
                        try {{ agentData = JSON.parse(agentData); }} catch(e) {{}}
                    }}

                    if (agentData.agents && Object.keys(agentData.agents).length > 0) {{
                        card += `<details open class="system-topology-details">
                                    <summary>System Topology</summary>
                                    ${{formatSystemTopology(agentData.agents)}}
                                 </details>`;
                    }}

                    if (agentData.turns) {{
                        card += `<details open class="conversation-trace-details" style="margin-bottom: 16px;">
                                    <summary>Conversation Trace</summary>
                                    <div style="font-size:13px; color:#5f6368; margin-bottom:12px;">Sequence of multi-agent events across turns</div>
                                    <div class="agent-trace-container">${{formatAgentData(agentData)}}</div>
                                 </details>`;
                    }}
                }}

                card += `<div class="responses-grid">`;

                (caseResult.response_candidate_results || []).forEach((candidate, j) => {{
                    const candidateName = candidateNames ? candidateNames[j] : `Candidate #${{j + 1}}`;
                    const displayText = isValEmpty(candidate.display_text) ? '' : candidate.display_text;
                    const rawJsonResponse = candidate.raw_json;

                    card += `<div class="response-column"><h4>${{candidateName}}</h4>`;

                    if (displayText) {{
                        card += `<div class="response-text-container">${{DOMPurify.sanitize(marked.parse(String(displayText)))}}</div>`;
                    }}

                    if (rawJsonResponse && rawJsonResponse !== '""' && rawJsonResponse !== 'null' && rawJsonResponse !== '{{}}') {{
                        card += `<details class="raw-json-details"><summary>View Raw Response JSON</summary><pre class="raw-json-container">${{DOMPurify.sanitize(rawJsonResponse)}}</pre></details>`;
                    }}

                    card += `<h5 style="margin-top: 16px; margin-bottom: 8px; font-size: 1.1em; color: #3c4043;">Metrics</h5><div class="metrics-list">`;
                    Object.entries(candidate.metric_results || {{}}).forEach(([name, val]) => {{
                        let explanationHandled = false;
                        let bubbles = '';

                        if (val.rubric_verdicts && val.rubric_verdicts.length > 0) {{
                            bubbles += '<div class="rubric-bubble-container" style="margin-top: 8px;">';
                            val.rubric_verdicts.forEach(verdict => {{
                                const rubricDescription = verdict.evaluated_rubric && verdict.evaluated_rubric.content && verdict.evaluated_rubric.content.property ? verdict.evaluated_rubric.content.property.description : 'N/A';
                                const verdictText = verdict.verdict ? '<span class="pass">Pass</span>' : '<span class="fail">Fail</span>';
                                const verdictJson = JSON.stringify(verdict, null, 2);
                                bubbles += `
                                    <details class="rubric-details">
                                        <summary class="rubric-bubble">${{verdictText}}: ${{DOMPurify.sanitize(rubricDescription)}}</summary>
                                        <pre class="raw-json-container">${{DOMPurify.sanitize(verdictJson)}}</pre>
                                    </details>`;
                            }});
                            bubbles += '</div>';
                        }}

                        let scoreDisplay = val.score != null ? val.score.toFixed(2) : 'N/A';
                        let metricContent = '';

                        if (val.explanation && !explanationHandled) {{
                            metricContent += `<div class="explanation" style="margin-top:0; margin-bottom: 12px;">${{DOMPurify.sanitize(marked.parse(String(val.explanation)))}}</div>`;
                        }}
                        if (bubbles) {{
                            metricContent += bubbles;
                        }}
                        if (!metricContent) {{
                            metricContent = `<div style="color: #80868b; font-style: italic; font-size: 13px;">No additional details.</div>`;
                        }}

                        card += `
                            <details class="metric-details" open>
                                <summary class="metric-summary">
                                    <div class="metric-name-wrapper">${{DOMPurify.sanitize(name)}}</div>
                                    <div class="metric-score">${{DOMPurify.sanitize(scoreDisplay)}}</div>
                                </summary>
                                <div class="metric-body">
                                    ${{metricContent}}
                                </div>
                            </details>
                        `;
                    }});
                    card += '</div></div>';
                }});
                container.innerHTML += card + '</div></details>';
            }});
        }}
        renderSummary(vizData_vertex_eval_sdk.summary_metrics, vizData_vertex_eval_sdk.metadata);
        renderDetails(vizData_vertex_eval_sdk.eval_case_results, vizData_vertex_eval_sdk.metadata);
    </script>
</body>
</html>
"""
    )


def _get_inference_html(dataframe_json: str) -> str:
    """Returns a self-contained HTML for displaying inference results."""
    payload_b64 = _encode_to_base64(dataframe_json)
    return textwrap.dedent(
        f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Evaluation Dataset</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>
    <style>
        body {{ font-family: 'Roboto', sans-serif; margin: 2em; background-color: #f8f9fa; color: #202124;}}
        .container {{ max-width: 95%; margin: 20px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
        h1 {{ color: #3c4043; border-bottom: 2px solid #4285F4; padding-bottom: 8px; }}
        table {{ border-collapse: collapse; width: 100%; table-layout: fixed; }}
        th, td {{ border: 1px solid #dadce0; padding: 12px; text-align: left; vertical-align: top; }}
        th {{ background-color: #f2f2f2; font-weight: 500;}}
        td > div {{ white-space: pre-wrap; word-wrap: break-word; max-height: 400px; overflow-y: auto; overflow-wrap: break-word; }}
        .raw-json-details summary {{ font-size: 0.9em; cursor: pointer; color: #5f6368; }}
        .raw-json-container {{ white-space: pre-wrap; word-wrap: break-word; max-height: 300px; overflow-y: auto; background-color: #f1f1f1; padding: 10px; border-radius: 4px; margin-top: 8px; }}
        .rubric-group-title {{ font-weight: bold; margin-bottom: 10px; display: block; }}
        .rubric-bubble-container {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .rubric-details {{ border: none; padding: 0; margin: 0; }}
        .rubric-bubble {{
            display: inline-flex;
            align-items: center;
            background-color: #e8f0fe;
            color: #1967d2;
            border-radius: 16px;
            padding: 8px 12px;
            font-size: 0.9em;
            cursor: pointer;
            list-style: none; /* Hide default marker in Safari */
        }}
        .rubric-bubble::-webkit-details-marker {{ display: none; }} /* Hide default marker in Chrome */
        .rubric-bubble::before {{
            content: '►';
            margin-right: 8px;
            font-size: 0.8em;
            transition: transform 0.2s;
        }}
        .rubric-details[open] > .rubric-bubble::before {{
            transform: rotate(90deg);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Evaluation Dataset</h1>
        <div id="results-table"></div>
    </div>
    <script>
        var vizData_vertex_eval_sdk = JSON.parse(new TextDecoder().decode(Uint8Array.from(atob("{payload_b64}"), c => c.charCodeAt(0))));
        var container_vertex_eval_sdk = document.getElementById('results-table');

        function renderRubrics(cellValue) {{
            let content = '';
            let rubricData = cellValue;
            if (typeof rubricData === 'string') {{
                try {{
                    rubricData = JSON.parse(rubricData);
                }} catch (e) {{
                    console.error("Error parsing rubric_groups JSON:", e, rubricData);
                    return `<div>Error parsing rubrics.</div>`;
                }}
            }}

            if (typeof rubricData !== 'object' || rubricData === null) {{
                 return `<div>Invalid rubric data.</div>`;
            }}

            for (const groupName in rubricData) {{
                const rubrics = rubricData[groupName];
                content += `<div class="rubric-group-title">${{groupName}}</div>`;
                if (Array.isArray(rubrics) && rubrics.length > 0) {{
                    content += '<div class="rubric-bubble-container">';
                    rubrics.forEach((rubric, index) => {{
                        const rubricJson = JSON.stringify(rubric, null, 2);
                        const description = rubric.content && rubric.content.property ? rubric.content.property.description : 'N/A';
                        content += `
                            <details class="rubric-details">
                                <summary class="rubric-bubble">${{DOMPurify.sanitize(description)}}</summary>
                                <pre class="raw-json-container">${{DOMPurify.sanitize(rubricJson)}}</pre>
                            </details>`;
                    }});
                    content += '</div>';
                }}
            }}
            return `<div>${{content}}</div>`;
        }}

        function renderCell(cellValue, header) {{
            let cellContent = '';
            if (header === 'rubric_groups') {{
                return `<td>${{renderRubrics(cellValue)}}</td>`;
            }}

            if (cellValue && typeof cellValue === 'object' && cellValue.display_text !== undefined) {{
                cellContent += `<div>${{DOMPurify.sanitize(marked.parse(String(cellValue.display_text)))}}</div>`;
                if (cellValue.raw_json) {{
                    cellContent += `<details class="raw-json-details"><summary>View Raw JSON</summary><pre class="raw-json-container">${{DOMPurify.sanitize(cellValue.raw_json)}}</pre></details>`;
                }}
            }} else {{
                const cellDisplay = cellValue === null || cellValue === undefined ? '' : String(cellValue);
                cellContent = `<div>${{DOMPurify.sanitize(marked.parse(cellDisplay))}}</div>`;
            }}
            return `<td>${{cellContent}}</td>`;
        }}

        if (!vizData_vertex_eval_sdk || vizData_vertex_eval_sdk.length === 0) {{ container_vertex_eval_sdk.innerHTML = "<p>No data.</p>"; }}
        else {{
            let table = '<table><thead><tr>';
            const headers = Object.keys(vizData_vertex_eval_sdk[0] || {{}});
            headers.forEach(h => table += `<th>${{h}}</th>`);
            table += '</tr></thead><tbody>';
            vizData_vertex_eval_sdk.forEach(row => {{
                table += '<tr>';
                headers.forEach(header => {{
                    table += renderCell(row[header], header);
                }});
                table += '</tr>';
            }});
            container_vertex_eval_sdk.innerHTML = table + '</tbody></table>';
        }}
    </script>
</body>
</html>
"""
    )


def display_evaluation_result(
    eval_result_obj: types.EvaluationResult,
    candidate_names: Optional[list[str]] = None,
) -> None:
    """Displays evaluation result in an IPython environment."""
    if not _is_ipython_env():
        logger.warning("Skipping display: not in an IPython environment.")
        return
    else:
        from IPython import display

    try:
        result_dump = eval_result_obj.model_dump(
            mode="json", exclude_none=True, exclude={"evaluation_dataset"}
        )
    except errors.PydanticSerializationError as e:
        logger.error(
            "Serialization Error: %s\nCould not display the evaluation "
            "result due to a data serialization issue. Please check the "
            "content of the EvaluationResult object.",
            e,
        )
        return
    except Exception as e:
        logger.error("Failed to serialize EvaluationResult: %s", e, exc_info=True)
        raise

    input_dataset_list = eval_result_obj.evaluation_dataset
    is_comparison = input_dataset_list and len(input_dataset_list) > 1

    metadata_payload = result_dump.get("metadata", {})
    metadata_payload["candidate_names"] = candidate_names or metadata_payload.get(
        "candidate_names"
    )

    if is_comparison and input_dataset_list:
        if input_dataset_list[0]:
            metadata_payload["dataset"] = _extract_dataset_rows(input_dataset_list[0])

        if "eval_case_results" in result_dump:
            for case_res in result_dump["eval_case_results"]:
                for resp_idx, cand_res in enumerate(
                    case_res.get("response_candidate_results", [])
                ):
                    if (
                        input_dataset_list is not None
                        and resp_idx < len(input_dataset_list)
                        and input_dataset_list[resp_idx]
                    ):
                        rows = _extract_dataset_rows(input_dataset_list[resp_idx])
                        case_idx = case_res.get("eval_case_index")
                        if case_idx is not None and case_idx < len(rows):
                            original_case = rows[case_idx]
                            cand_res["display_text"] = original_case[
                                "response_display_text"
                            ]
                            cand_res["raw_json"] = original_case["response_raw_json"]

        win_rates = eval_result_obj.win_rates if eval_result_obj.win_rates else {}
        if "summary_metrics" in result_dump:
            for summary in result_dump["summary_metrics"]:
                if summary.get("metric_name") in win_rates:
                    summary.update(win_rates[summary["metric_name"]])

        result_dump["metadata"] = metadata_payload
        html_content = _get_comparison_html(json.dumps(result_dump))
    else:
        single_dataset = input_dataset_list[0] if input_dataset_list else None
        processed_rows = []
        if single_dataset is not None:
            processed_rows = _extract_dataset_rows(single_dataset)
            metadata_payload["dataset"] = processed_rows

            if "eval_case_results" in result_dump and processed_rows:
                for case_res in result_dump["eval_case_results"]:
                    case_idx = case_res.get("eval_case_index")
                    if (
                        case_idx is not None
                        and case_idx < len(processed_rows)
                        and case_res.get("response_candidate_results")
                    ):
                        original_case = processed_rows[case_idx]
                        cand_res = case_res["response_candidate_results"][0]
                        cand_res["display_text"] = original_case[
                            "response_display_text"
                        ]
                        cand_res["raw_json"] = original_case["response_raw_json"]

        result_dump["metadata"] = metadata_payload
        html_content = _get_evaluation_html(json.dumps(result_dump))

    display.display(display.HTML(html_content))


def display_evaluation_dataset(eval_dataset_obj: types.EvaluationDataset) -> None:
    """Displays an evaluation dataset in an IPython environment."""
    if not _is_ipython_env():
        logger.warning("Skipping display: not in an IPython environment.")
        return
    else:
        from IPython import display

    if (
        eval_dataset_obj.eval_dataset_df is None
        or eval_dataset_obj.eval_dataset_df.empty
    ):
        logger.warning("No inference data to display.")
        return

    processed_rows = []
    df = eval_dataset_obj.eval_dataset_df

    for _, row in df.iterrows():
        processed_row = {}
        for col_name, cell_value in row.items():
            if col_name in ["prompt", "request", "response"]:
                processed_row[col_name] = _extract_text_and_raw_json(cell_value)
            elif col_name == "rubric_groups":
                # Special handling for rubric_groups to keep it as a dict
                if isinstance(cell_value, dict):
                    processed_row[col_name] = {
                        k: [  # type: ignore[misc]
                            (
                                v_item.model_dump(mode="json")
                                if hasattr(v_item, "model_dump")
                                else v_item
                            )
                            for v_item in v
                        ]
                        for k, v in cell_value.items()
                    }
                else:
                    processed_row[col_name] = cell_value
            else:
                if isinstance(cell_value, (dict, list)):
                    processed_row[col_name] = json.dumps(  # type: ignore[assignment]
                        cell_value, ensure_ascii=False, default=_pydantic_serializer
                    )
                else:
                    processed_row[col_name] = cell_value
        processed_rows.append(processed_row)

    dataframe_json_string = json.dumps(processed_rows, ensure_ascii=False, default=str)
    html_content = _get_inference_html(dataframe_json_string)
    display.display(display.HTML(html_content))


def _get_status_html(status: str, error_message: Optional[str] = None) -> str:
    """Returns a simple HTML string for displaying a status and optional error."""
    error_html = ""
    if error_message:
        error_html = f"""
        <p>
            <b>Error:</b>
            <pre style="white-space: pre-wrap; word-wrap: break-word;">{html.escape(error_message)}</pre>
        </p>
        """

    return textwrap.dedent(
        f"""
    <div>
        <p><b>Status:</b> {html.escape(status)}</p>
        {error_html}
    </div>
    """
    )


def display_evaluation_run_status(eval_run_obj: "types.EvaluationRun") -> None:
    """Displays the status of an evaluation run in an IPython environment."""
    if not _is_ipython_env():
        logger.warning("Skipping display: not in an IPython environment.")
        return
    else:
        from IPython import display

    status = eval_run_obj.state.name if eval_run_obj.state else "UNKNOWN"
    error_message = str(eval_run_obj.error) if eval_run_obj.error else None
    html_content = _get_status_html(status, error_message)
    display.display(display.HTML(html_content))
