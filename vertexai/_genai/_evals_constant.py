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
"""Constants for evals module."""

SUPPORTED_PREDEFINED_METRICS = frozenset(
    {
        # v1 metrics (kept for backward compatibility).
        "general_quality_v1",
        "text_quality_v1",
        "instruction_following_v1",
        "grounding_v1",
        "safety_v1",
        "multi_turn_general_quality_v1",
        "multi_turn_text_quality_v1",
        "multi_turn_tool_use_quality_v1",
        "multi_turn_trajectory_quality_v1",
        "multi_turn_task_success_v1",
        "final_response_match_v2",
        "final_response_reference_free_v1",
        "final_response_quality_v1",
        "hallucination_v1",
        "tool_use_quality_v1",
        "gecko_text2image_v1",
        "gecko_text2video_v1",
        # v2/v3 metrics backed by Gemini 3.5 Flash.
        "general_quality_v2",
        "instruction_following_v2",
        "text_quality_v2",
        "grounding_v2",
        "hallucination_v2",
        "safety_v3",
        "multi_turn_general_quality_v2",
        "multi_turn_text_quality_v2",
        "tool_use_quality_v2",
        "final_response_quality_v2",
        "final_response_match_v3",
        "final_response_reference_free_v2",
        "gecko_text2image_v2",
        "gecko_text2video_v2",
    }
)

# Maps the SDK-facing base metric name to the latest API spec name.
# When a user creates a metric without specifying a version, this resolves to
# the latest available version (backed by Gemini 3.5 Flash).
# Note: v2/v3 specs require Gemini 3.5 Flash, which is not available in all
# regions (e.g. us-central1). To use v1 explicitly for full regional
# availability:
#   types.RubricMetric.GENERAL_QUALITY(version="v1")
METRIC_LATEST_SPEC_NAME: dict[str, str] = {
    "general_quality": "general_quality_v2",
    "instruction_following": "instruction_following_v2",
    "text_quality": "text_quality_v2",
    "grounding": "grounding_v2",
    "hallucination": "hallucination_v2",
    "safety": "safety_v3",
    "multi_turn_general_quality": "multi_turn_general_quality_v2",
    "multi_turn_text_quality": "multi_turn_text_quality_v2",
    "tool_use_quality": "tool_use_quality_v2",
    "final_response_quality": "final_response_quality_v2",
    "final_response_match": "final_response_match_v3",
    "final_response_reference_free": "final_response_reference_free_v2",
    "gecko_text2image": "gecko_text2image_v2",
    "gecko_text2video": "gecko_text2video_v2",
}

SUPPORTED_VERTEX_MAAS_MODEL_PREFIXES = frozenset(
    {
        "meta/",  # Meta/Llama
        "deepseek-ai/",  # DeepSeek AI
        "qwen/",  # Qwen
        "openai/",  # OpenAI (GPT-OSS)
        "claude-",  # Anthropic (Claude)
        "mistral-",  # Mistral AI
        "jamba-",  # AI21 (Jamba)
    }
)
INTERMEDIATE_EVENTS = "intermediate_events"
RESPONSE = "response"
PROMPT = "prompt"
REFERENCE = "reference"
SESSION_INPUT = "session_inputs"
CONTEXT = "context"
CONTENT = "content"
PARTS = "parts"
USER_AUTHOR = "user"
AGENT_DATA = "agent_data"
STARTING_PROMPT = "starting_prompt"
CONVERSATION_PLAN = "conversation_plan"
HISTORY = "history"
CONVERSATION_HISTORY = "conversation_history"

COMMON_DATASET_COLUMNS = frozenset(
    {
        INTERMEDIATE_EVENTS,
        PROMPT,
        REFERENCE,
        SESSION_INPUT,
        CONTEXT,
        HISTORY,
        CONVERSATION_HISTORY,
        STARTING_PROMPT,
        CONVERSATION_PLAN,
        AGENT_DATA,
    }
)
