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
"""Unit tests for generative model tuning."""
# pylint: disable=protected-access,bad-continuation,g-import-not-at-top,reimported

import datetime
import sys


# b/328302251
def test_vertexai_import():
    """Tests the effects of importing the vertexai module."""

    # We only have one chance to test the imports since cleaning up loaded modules
    # is not fully possible.
    # This is especially made hard by protobuf C code and its global proto registry.
    # So we test everything in a single run.

    # First let's check that the aiplatform and vertexai models are not loaded yet.
    # This is not trivial since in google3 all modules including this test are
    # under google.cloud.aiplatform. Moudle names are different in google3.
    # My solution is to ignore modules that are parents of the current test module.
    modules_before_aip = set(sys.modules)
    for module_name in modules_before_aip:
        assert ".aiplatform" not in module_name or __name__.startswith(module_name)
        assert "vertexai" not in module_name or __name__.startswith(module_name)

    # Test aiplatform import
    start_time = datetime.datetime.now(datetime.timezone.utc)

    from google.cloud.aiplatform import initializer as _  # noqa: F401

    end_time = datetime.datetime.now(datetime.timezone.utc)
    aip_import_timedelta = end_time - start_time
    # modules_after_aip = set(sys.modules)
    # Assertion broken by `google.cloud.aiplatform.preview.featurestore`
    # assert not [
    #     module_name
    #     for module_name in modules_after_aip
    #     if ".preview" in module_name
    # ]

    # Test vertexai import
    modules_before_vertexai = set(sys.modules)
    start_time = datetime.datetime.now(datetime.timezone.utc)

    import vertexai

    end_time = datetime.datetime.now(datetime.timezone.utc)
    vertexai_import_timedelta = start_time - end_time
    modules_after_vertexai = set(sys.modules)
    new_modules_after_vertexai = modules_after_vertexai - modules_before_vertexai

    vertexai_module_name = vertexai.__name__  # == "vertexai"
    assert sorted(new_modules_after_vertexai) == [vertexai_module_name]

    assert vertexai_import_timedelta.total_seconds() < 0.005
    assert aip_import_timedelta.total_seconds() < 20
