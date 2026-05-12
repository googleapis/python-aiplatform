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

import os
from typing import Any, Optional

from google.genai._api_client import HttpOptions
import pytest


is_api_mode = "config.getoption('--mode') == 'api'"


# Sets up the test framework.
# file: Always use __file__
# globals_for_file: Always use globals()
def setup(
    *,
    file: str,
    globals_for_file: Optional[dict[str, Any]] = None,
    test_method: Optional[str] = None,
    http_options: Optional[HttpOptions] = None,
):
    """Generates parameterization for tests"""
    replays_directory = (
        file.replace(os.path.dirname(__file__), "tests/vertex_sdk_genai_replays")
        .replace(".py", "")
        .replace("/test_", "/")
    )

    # Add fixture for requested client option.
    return pytest.mark.parametrize(
        "use_vertex, replays_prefix, http_options",
        [
            (True, replays_directory, http_options),
        ],
    )
