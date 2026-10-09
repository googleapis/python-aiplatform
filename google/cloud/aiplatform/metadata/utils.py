# -*- coding: utf-8 -*-
# Copyright 2022 Google LLC
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

from typing import List, Optional, Union
import datetime


def _convert_to_rfc3339(date_time) -> str:
    """Convert date or datetime objects to RFC-3339 formatted string.

    Args:
        date_time: A datetime.datetime, datetime.date object, or string.

    Returns:
        RFC-3339 formatted string.

    Raises:
        ValueError: If the input cannot be converted to RFC-3339 format.
    """
    if isinstance(date_time, str):
        # 既に文字列の場合は、書式を確認して必要なら変換
        try:
            # 'YYYY-MM-DD'形式の場合
            if len(date_time) == 10 and date_time[4] == '-' and date_time[7] == '-':
                date_obj = datetime.datetime.strptime(date_time, "%Y-%m-%d")
                return date_obj.strftime("%Y-%m-%dT00:00:00Z")
            # すでにRFC-3339形式と見なす
            return date_time
        except ValueError:
            raise ValueError(f"String '{date_time}' is not in a recognized date format.")
    elif isinstance(date_time, datetime.datetime):
        # タイムゾーン情報がない場合はUTCと見なす
        if date_time.tzinfo is None:
            date_time = date_time.replace(tzinfo=datetime.timezone.utc)
        return date_time.isoformat().replace('+00:00', 'Z')
    elif isinstance(date_time, datetime.date):
        # 日付のみの場合は時刻を00:00:00Zとする
        return f"{date_time.isoformat()}T00:00:00Z"
    else:
        raise ValueError(
            f"Expected string, datetime.datetime, or datetime.date. Got {type(date_time)}"
        )


def _make_filter_string(
    schema_title: Optional[Union[str, List[str]]] = None,
    in_context: Optional[List[str]] = None,
    parent_contexts: Optional[List[str]] = None,
    uri: Optional[str] = None,
    create_time_start_date: Optional[Union[str, datetime.datetime, datetime.date]] = None,
    create_time_end_date: Optional[Union[str, datetime.datetime, datetime.date]] = None,
) -> str:
    """Helper method to format filter strings for Metadata querying.

    No enforcement of correctness.

    Args:
        schema_title (Union[str, List[str]]): Optional. schema_titles to filter for.
        in_context (List[str]):
            Optional. Context resource names that the node should be in. Only for Artifacts/Executions.
        parent_contexts (List[str]): Optional. Parent contexts the context should be in. Only for Contexts.
        uri (str): Optional. uri to match for. Only for Artifacts.
        create_time_start_date (Union[str, datetime.datetime, datetime.date]): 
            Optional. Start date for filtering by creation time. 
            If string, should be in 'YYYY-MM-DD' or RFC-3339 format.
            If datetime or date object, will be converted to RFC-3339 format.
        create_time_end_date (Union[str, datetime.datetime, datetime.date]): 
            Optional. End date for filtering by creation time. 
            If string, should be in 'YYYY-MM-DD' or RFC-3339 format.
            If datetime or date object, will be converted to RFC-3339 format.
    Returns:
        String that can be used for Metadata service filtering.
    """
    parts = []
    if schema_title:
        if isinstance(schema_title, str):
            parts.append(f'schema_title="{schema_title}"')
        else:
            substring = " OR ".join(f'schema_title="{s}"' for s in schema_title)
            parts.append(f"({substring})")
    if in_context:
        for context in in_context:
            parts.append(f'in_context("{context}")')
    if parent_contexts:
        parent_context_str = ",".join([f'"{c}"' for c in parent_contexts])
        parts.append(f"parent_contexts:{parent_context_str}")
    if uri:
        parts.append(f'uri="{uri}"')
    if create_time_start_date:
        rfc3339_start = _convert_to_rfc3339(create_time_start_date)
        parts.append(f'create_time>="{rfc3339_start}"')
    if create_time_end_date:
        rfc3339_end = _convert_to_rfc3339(create_time_end_date)
        parts.append(f'create_time<="{rfc3339_end}"')
    return " AND ".join(parts)
