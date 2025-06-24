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

import json
import logging
from typing import Optional

from pydantic import errors
import pandas as pd

from . import types

logger = logging.getLogger(__name__)


def _is_ipython_env() -> bool:
    """Checks if the code is running in an IPython environment."""
    try:
        from IPython import get_ipython

        return get_ipython() is not None
    except ImportError:
        return False


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

            def stringify_cell(cell):
                if pd.isna(cell):
                    return None
                if isinstance(cell, (dict, list)):
                    try:
                        return json.dumps(cell, ensure_ascii=False)
                    except TypeError:
                        return str(cell)
                elif not isinstance(cell, (str, int, float, bool)):
                    return str(cell)
                return cell

            df_copy[col] = df_copy[col].apply(stringify_cell)
    return df_copy


def _get_evaluation_html(eval_result_json: str) -> str:
    """Returns a self-contained HTML for single evaluation visualization."""
    return f"""
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
        .prompt-container {{ background-color: #e8f0fe; padding: 16px; margin: 12px 0; border-radius: 8px; white-space: pre-wrap; word-wrap: break-word; }}
        .reference-container {{ background-color: #e6f4ea; padding: 16px; margin: 12px 0; border-radius: 8px; white-space: pre-wrap; word-wrap: break-word; }}
        .response-container {{ background-color: #f9f9f9; padding: 12px; margin-top: 8px; border-radius: 8px; border: 1px solid #eee; }}
        .explanation {{ color: #5f6368; font-style: italic; font-size: 0.9em; padding-top: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Evaluation Report</h1>
        <div id="summary-section"></div>
        <div id="details-section"></div>
    </div>
    <script>
        const data = {eval_result_json};
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
                const prompt = original_case.prompt || '(prompt not found)';
                const reference = original_case.reference || '';
                let card = `<details><summary>Case #${{caseResult.eval_case_index != null ? caseResult.eval_case_index : i}}</summary>`;
                card += `<div class="prompt-container"><strong>Prompt:</strong><br>${{DOMPurify.sanitize(marked.parse(String(prompt)))}}</div>`;
                if (reference) {{ card += `<div class="reference-container"><strong>Reference:</strong><br>${{DOMPurify.sanitize(marked.parse(String(reference)))}}</div>`; }}
                (caseResult.response_candidate_results || []).forEach(candidate => {{
                    const candidateResponse = candidate.response_text || '(response not found)';
                    card += `<div class="response-container"><h4>Candidate Response</h4>${{DOMPurify.sanitize(marked.parse(String(candidateResponse)))}}</div>`;
                    let metricTable = '<h4>Metrics</h4><table><tbody>';
                    Object.entries(candidate.metric_results || {{}}).forEach(([name, val]) => {{
                        metricTable += `<tr><td>${{name}}</td><td><b>${{val.score != null ? val.score.toFixed(2) : 'N/A'}}</b></td></tr>`;
                        if (val.explanation) {{ metricTable += `<tr><td colspan="2"><div class="explanation">${{DOMPurify.sanitize(marked.parse(String(val.explanation)))}}</div></td></tr>`; }}
                    }});
                    card += metricTable + '</tbody></table>';
                }});
                container.innerHTML += card + '</details>';
            }});
        }}
        renderSummary(data.summary_metrics);
        renderDetails(data.eval_case_results, data.metadata);
    </script>
</body>
</html>
"""


def _get_comparison_html(eval_result_json: str) -> str:
    """Returns a self-contained HTML for a side-by-side eval comparison."""
    return f"""
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
        .prompt-container {{ background-color: #e8f0fe; padding: 16px; margin-bottom: 16px; border-radius: 8px; white-space: pre-wrap; word-wrap: break-word; }}
        .responses-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-top: 16px;}}
        .response-column {{ border: 1px solid #e0e0e0; padding: 16px; border-radius: 8px; background: #f9f9f9; }}
        .response-text-container {{ background-color: #fff; padding: 12px; margin-top: 8px; border-radius: 4px; border: 1px solid #eee; white-space: pre-wrap; word-wrap: break-word; max-height: 400px; overflow-y: auto; }}
        .explanation {{ color: #5f6368; font-style: italic; font-size: 0.9em; padding-top: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Eval Comparison Report</h1>
        <div id="summary-section"></div>
        <div id="details-section"></div>
    </div>
    <script>
        const data = {eval_result_json};
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
                let card = `<details open><summary>Case #${{caseResult.eval_case_index}}</summary><div class="prompt-container">${{DOMPurify.sanitize(marked.parse(String(original_case.prompt || '')))}}</div><div class="responses-grid">`;
                (caseResult.response_candidate_results || []).forEach((candidate, j) => {{
                    const candidateName = candidateNames ? candidateNames[j] : `Candidate #${{j + 1}}`;
                    card += `<div class="response-column"><h4>${{candidateName}}</h4><div class="response-text-container">${{DOMPurify.sanitize(marked.parse(String(candidate.response_text || '')))}}</div><h5>Metrics</h5><table><tbody>`;
                    Object.entries(candidate.metric_results || {{}}).forEach(([name, val]) => {{
                        card += `<tr><td>${{name}}</td><td><b>${{val.score.toFixed(2)}}</b></td></tr>`;
                        if(val.explanation) card += `<tr><td colspan="2" class="explanation">${{DOMPurify.sanitize(marked.parse(String(val.explanation)))}}</td></tr>`;
                    }});
                    card += '</tbody></table></div>';
                }});
                container.innerHTML += card + '</div></details>';
            }});
        }}
        renderSummary(data.summary_metrics, data.metadata);
        renderDetails(data.eval_case_results, data.metadata);
    </script>
</body>
</html>
"""


def _get_inference_html(dataframe_json: str) -> str:
    """Returns a self-contained HTML for displaying inference results."""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Inference Results</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>
    <style>
        body {{ font-family: 'Roboto', sans-serif; margin: 2em; background-color: #f8f9fa; color: #202124;}}
        .container {{ max-width: 95%; margin: 20px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
        h1 {{ border-bottom: 1px solid #dadce0; padding-bottom: 8px; color: #3c4043; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #dadce0; padding: 12px; text-align: left; vertical-align: top; }}
        th {{ background-color: #f2f2f2; font-weight: 500;}}
        td > div {{ white-space: pre-wrap; word-wrap: break-word; max-height: 400px; overflow-y: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Inference Results</h1>
        <div id="results-table"></div>
    </div>
    <script>
        const data = JSON.parse({dataframe_json});
        const container = document.getElementById('results-table');
        if (!data || data.length === 0) {{ container.innerHTML = "<p>No data.</p>"; }}
        else {{
            let table = '<table><thead><tr>';
            const headers = Object.keys(data[0] || {{}});
            headers.forEach(h => table += `<th>${{h}}</th>`);
            table += '</tr></thead><tbody>';
            data.forEach(row => {{
                table += '<tr>';
                headers.forEach(header => {{
                    const cellValue = row[header];
                    const cellDisplay = cellValue === null || cellValue === undefined ? '' : String(cellValue);
                    table += `<td><div>${{DOMPurify.sanitize(marked.parse(cellDisplay))}}</div></td>`;
                }});
                table += '</tr>';
            }});
            container.innerHTML = table + '</tbody></table>';
        }}
    </script>
</body>
</html>
"""


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

    if is_comparison:
        if (
            input_dataset_list
            and input_dataset_list[0]
            and input_dataset_list[0].eval_dataset_df is not None
        ):
            metadata_payload["dataset"] = _preprocess_df_for_json(
                input_dataset_list[0].eval_dataset_df
            ).to_dict(orient="records")

        if "eval_case_results" in result_dump:
            for case_res in result_dump["eval_case_results"]:
                for resp_idx, cand_res in enumerate(
                    case_res.get("response_candidate_results", [])
                ):
                    if (
                        resp_idx < len(input_dataset_list)
                        and input_dataset_list[resp_idx].eval_dataset_df is not None
                    ):
                        df = _preprocess_df_for_json(
                            input_dataset_list[resp_idx].eval_dataset_df
                        )
                        case_idx = case_res.get("eval_case_index")
                        if (
                            df is not None
                            and case_idx is not None
                            and case_idx < len(df)
                        ):
                            cand_res["response_text"] = df.iloc[case_idx].get(
                                "response"
                            )

        win_rates = eval_result_obj.win_rates if eval_result_obj.win_rates else {}
        if "summary_metrics" in result_dump:
            for summary in result_dump["summary_metrics"]:
                if summary.get("metric_name") in win_rates:
                    summary.update(win_rates[summary["metric_name"]])

        result_dump["metadata"] = metadata_payload
        html_content = _get_comparison_html(json.dumps(result_dump))
    else:
        single_dataset = input_dataset_list[0] if input_dataset_list else None

        if (
            single_dataset is not None
            and isinstance(single_dataset, types.EvaluationDataset)
            and single_dataset.eval_dataset_df is not None
        ):
            processed_df = _preprocess_df_for_json(single_dataset.eval_dataset_df)
            metadata_payload["dataset"] = processed_df.to_dict(orient="records")
            if "eval_case_results" in result_dump and processed_df is not None:
                for case_res in result_dump["eval_case_results"]:
                    case_idx = case_res.get("eval_case_index")
                    if (
                        case_idx is not None
                        and case_idx < len(processed_df)
                        and case_res.get("response_candidate_results")
                    ):
                        case_res["response_candidate_results"][0][
                            "response_text"
                        ] = processed_df.iloc[case_idx].get("response")

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

    processed_df = _preprocess_df_for_json(eval_dataset_obj.eval_dataset_df)
    dataframe_json_string = json.dumps(processed_df.to_json(orient="records"))
    html_content = _get_inference_html(dataframe_json_string)
    display.display(display.HTML(html_content))
