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

    # Importing some required modules to reduce noise
    import grpc as _  # noqa: F811
    import google.api_core.iam as _  # noqa: F811
    import google.api_core.future as _  # noqa: F811
    import google.api_core.gapic_v1 as _  # noqa: F811
    import google.api_core.operation as _  # noqa: F811
    import google.api_core.operation_async as _  # noqa: F811
    import google.api_core.operations_v1 as _  # noqa: F811
    import google.api_core.rest_streaming as _  # noqa: F811
    import google.cloud.storage as _  # noqa: F811

    try:
        # Needed for Python 3.8
        import aiohttp as _  # noqa: F811
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    # We only have one chance to test the imports since cleaning up loaded modules
    # is not fully possible.
    # This is especially made hard by protobuf C code and its global proto registry.
    # So we test everything in a single run.

    # First let's check that the aiplatform and vertexai models are not loaded yet.
    # This is not trivial since in google3 all modules including this test are
    # under google.cloud.aiplatform. Module names are different in google3.
    # My solution is to ignore modules that are parents of the current test module.
    modules_before_aip = set(sys.modules)
    for module_name in modules_before_aip:
        assert ".aiplatform" not in module_name or __name__.startswith(module_name)
        assert "vertexai" not in module_name or __name__.startswith(module_name)

    # Test aiplatform import
    start_time = datetime.datetime.now(datetime.timezone.utc)

    from google.cloud.aiplatform import initializer as _  # noqa: F401,F811

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
    assert aip_import_timedelta.total_seconds() < 40

    # Testing that external modules are not loaded.
    new_modules = modules_after_vertexai - modules_before_aip
    _test_external_imports(new_modules)

    # Tests the GenAI client module is lazy loaded.
    from vertexai._genai import client as _  # noqa: F401,F811

    modules_after_genai_client_import = set(sys.modules)

    # The evals module has additional required deps that should not be required
    # to instantiate a client.
    assert "pandas" not in modules_after_genai_client_import
    assert "pydantic" in modules_after_genai_client_import

    # The types module should not import _evals_metric_loaders until
    # PrebuiltMetric or RubricMetric are accessed.
    from vertexai._genai import types  # noqa: F401

    assert (
        "google.cloud.aiplatform.vertexai._genai._evals_metric_loaders"
        not in sys.modules
    )

    # Tests the evals module is lazy loaded.
    from vertexai._genai import evals as _  # noqa: F401,F811

    modules_after_eval_import = set(sys.modules)

    assert "pandas" in modules_after_eval_import


def _test_external_imports(new_modules: list):
    builtin_modules = {
        "concurrent",
        # "email",  # Imported by google.cloud.storage
        "importlib_metadata",
        "pickle",
        # Needed for external tests
        "packaging",
    }
    allowed_external_modules = {
        "google.cloud.resourcemanager_v3",
        "google3",
        # Needed for external tests
        "google.api",
        "google.api_core",
        "google.cloud.location",
        "google.cloud.resourcemanager",
        "google.iam",
        "google.type",
    }
    allowed_modules = allowed_external_modules | builtin_modules
    # a.b.c -> a.b._*
    allowed_private_prefixes = {
        (("." + module_name).rpartition(".")[0] + "._").lstrip(".")
        for module_name in allowed_modules
    }

    import re

    allowed_module_name_pattern = re.compile(
        rf"""^({"|".join(map(re.escape, allowed_modules))})(\..*)?$"""
        "|"
        rf"""^({"|".join(map(re.escape, allowed_private_prefixes))}).*$""",
        re.DOTALL,
    )

    new_external_modules = {
        module_name
        for module_name in new_modules
        if not (
            module_name.startswith("google.cloud.aiplatform")
            or module_name.startswith("vertexai")
        )
    }
    new_unexpected_modules = {
        module_name
        for module_name in new_external_modules
        if not allowed_module_name_pattern.match(module_name)
    }
    if new_unexpected_modules:
        raise AssertionError(
            f"Unexpected modules were loaded: {sorted(new_unexpected_modules)}"
        )
