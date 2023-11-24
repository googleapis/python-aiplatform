# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script is used to synthesize generated parts of this library."""

import re

import synthtool as s
import synthtool.gcp as gcp
from synthtool.languages import python

common = gcp.CommonTemplates()

default_version = "v1"

has_generator_updates = False
for library in s.get_staging_dirs(default_version):
    # ---------------------------------------------------------------------
    # Patch each version of the library
    # ---------------------------------------------------------------------

    # https://github.com/googleapis/gapic-generator-python/issues/413
    s.replace(
        library
        / f"google/cloud/aiplatform_{library.name}/services/prediction_service/client.py",
        "request.instances = instances",
        "request.instances.extend(instances)",
    )

    # Remove test_predict_flattened/test_predict_flattened_async due to gapic generator bug
    # https://github.com/googleapis/gapic-generator-python/issues/414
    s.replace(
        library
        / f"tests/unit/gapic/aiplatform_{library.name}/test_prediction_service.py",
        """def test_predict_flattened.*?def test_predict_flattened_error""",
        "def test_predict_flattened_error",
        flags=re.MULTILINE | re.DOTALL,
    )

    # Remove test_explain_flattened/test_explain_flattened_async due to gapic generator bug
    # https://github.com/googleapis/gapic-generator-python/issues/414
    s.replace(
        library
        / f"tests/unit/gapic/aiplatform_{library.name}/test_prediction_service.py",
        """def test_explain_flattened.*?def test_explain_flattened_error""",
        "def test_explain_flattened_error",
        flags=re.MULTILINE | re.DOTALL,
    )

    s.move(
        library,
        excludes=[
            ".coveragerc",
            ".pre-commit-config.yaml",
            "setup.py",
            "README.rst",
            "docs/index.rst",
            f"docs/definition_{library.name}/services.rst",
            f"docs/instance_{library.name}/services.rst",
            f"docs/params_{library.name}/services.rst",
            f"docs/prediction_{library.name}/services.rst",
            f"scripts/fixup_aiplatform_{library.name}_keywords.py",
            f"scripts/fixup_definition_{library.name}_keywords.py",
            f"scripts/fixup_instance_{library.name}_keywords.py",
            f"scripts/fixup_params_{library.name}_keywords.py",
            f"scripts/fixup_prediction_{library.name}_keywords.py",
            "google/cloud/aiplatform/__init__.py",
            f"google/cloud/aiplatform/{library.name}/schema/**/services/",
            "testing/constraints-3.7.txt",
            "**/gapic_version.py", # exclude gapic_version.py to avoid reverting the version to 0.1.0
            ".kokoro/samples",
            "noxfile.py",
            "testing",
            "docs/conf.py",
        ],
    )
    has_generator_updates = True

s.remove_staging_dirs()

# only run post processor when there are changes to the generated code
if has_generator_updates:

    # ----------------------------------------------------------------------------
    # Add templated files
    # ----------------------------------------------------------------------------

    templated_files = common.py_library(
        cov_level=98,
        system_test_python_versions=["3.8"],
        unit_test_python_versions=["3.8", "3.9", "3.10", "3.11"],
        unit_test_extras=["testing"],
        system_test_extras=["testing"],
        microgenerator=True,
    )
    s.move(
        templated_files,
        excludes=[
            ".coveragerc",
            ".pre-commit-config.yaml",
            ".kokoro/continuous/common.cfg",
            ".kokoro/presubmit/presubmit.cfg",
            ".kokoro/continuous/prerelease-deps.cfg",
            ".kokoro/presubmit/prerelease-deps.cfg",
            ".kokoro/docs/docs-presubmit.cfg",
            # exclude sample configs so periodic samples are tested against main
            # instead of pypi
            ".kokoro/samples/python3.7/common.cfg",
            ".kokoro/samples/python3.8/common.cfg",
            ".kokoro/samples/python3.9/common.cfg",
            ".kokoro/samples/python3.10/common.cfg",
            ".kokoro/samples/python3.11/common.cfg",
            ".kokoro/samples/python3.7/periodic.cfg",
            ".kokoro/samples/python3.8/periodic.cfg",
            ".kokoro/samples/python3.9/periodic.cfg",
            ".kokoro/samples/python3.10/periodic.cfg",
            ".kokoro/samples/python3.11/periodic.cfg",
            ".github/CODEOWNERS",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/workflows",  # exclude gh actions as credentials are needed for tests
            "README.rst",
            ".github/release-please.yml", # use release please manifest
            "noxfile.py",
            "testing",
            "docs/conf.py",
        ],
    )  # the microgenerator has a good coveragerc file

    python.py_samples(skip_readmes=True)

    python.configure_previous_major_version_branches()

    # Update samples config to use `ucaip-sample-tests` project
    s.replace(
        ".kokoro/samples/python3.*/common.cfg",
        """env_vars: \{
        key: "BUILD_SPECIFIC_GCLOUD_PROJECT"
        value: "python-docs-samples-tests-.*?"
    \}""",
        """env_vars: {  
        key: "BUILD_SPECIFIC_GCLOUD_PROJECT"
        value: "ucaip-sample-tests"
    }""",
    )

    s.replace(
        ".kokoro/test-samples-impl.sh",
        "python3.9",
        "python3",
    )

    s.shell.run(["nox", "-s", "blacken"], hide_output=False)
