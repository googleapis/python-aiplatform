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

import os

import synthtool as s
import synthtool.gcp as gcp
from synthtool.languages import python

# Use the microgenerator for now since we want to pin the generator version.
# gapic = gcp.GAPICBazel()
gapic = gcp.GAPICMicrogenerator()

common = gcp.CommonTemplates()

# ----------------------------------------------------------------------------
# Generate AI Platform GAPIC layer
# ----------------------------------------------------------------------------

# library = gapic.py_library(
#     service="aiplatform",
#     version="v1beta1",
#     bazel_target="//google/cloud/aiplatform/v1beta1:aiplatform-v1beta1-py",
# )
library = gapic.py_library("aiplatform", "v1beta1", generator_version="0.20")

s.move(
    library,
    excludes=[
        ".kokoro",
        "setup.py",
        "README.rst",
        "docs/index.rst",
        "google/cloud/aiplatform/__init__.py",
        "tests/unit/aiplatform_v1beta1/test_prediction_service.py",
    ],
)

# ----------------------------------------------------------------------------
# Patch the library
# ----------------------------------------------------------------------------

# https://github.com/googleapis/gapic-generator-python/issues/336
s.replace("**/client.py", " operation.from_gapic", " ga_operation.from_gapic")

s.replace(
    "**/client.py",
    "client_options: ClientOptions = ",
    "client_options: ClientOptions.ClientOptions = ",
)

# https://github.com/googleapis/gapic-generator-python/issues/413
s.replace(
    "google/cloud/aiplatform_v1beta1/services/prediction_service/client.py",
    "request.instances = instances",
    "request.instances.extend(instances)",
)

# post processing to fix the generated reference doc
from synthtool import transforms as st
import re

# https://github.com/googleapis/gapic-generator-python/issues/479
paths = st._filter_files(st._expand_paths("google/cloud/**/*.py", "."))

pattern = r"(:\w+:``[^`]+``)"
expr = re.compile(pattern, flags=re.MULTILINE)
replaces = []
for path in paths:
    with path.open("r+") as fh:
        content = fh.read()
    matches = re.findall(expr, content)
    if matches:
        for match in matches:
            before = match
            after = match.replace("``", "`")
            replaces.append((path, before, after))

for path, before, after in replaces:
    s.replace([path], before, after)


# https://github.com/googleapis/gapic-generator-python/issues/483
paths = st._filter_files(st._expand_paths("google/cloud/**/*.py", "."))
pattern = r"(?P<full>\[(?P<first>[\w.]+)\]\[(?P<second>[\w.]+)\])"
expr = re.compile(pattern, flags=re.MULTILINE)
replaces = []
for path in paths:
    with path.open("r+") as fh:
        content = fh.read()
        for match in expr.finditer(content):
            before = match.groupdict()["full"].replace("[", "\[").replace("]", "\]")
            after = match.groupdict()["first"]
            after = f"``{after}``"
            replaces.append((path, before, after))

for path, before, after in replaces:
    s.replace([path], before, after)


s.replace("google/cloud/**/*.py", "\]\(\n\n\s*", "](")

s.replace("google/cloud/**/*.py", "\s*//\n\s*", "")

s.replace("google/cloud/**/*.py", "https:[\n]*\s*//", "https://")

s.replace("google/cloud/**/*.py", "[\n]*\s*//\s*/", "/")

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------

templated_files = common.py_library(cov_level=99, microgenerator=True)
s.move(
    templated_files, excludes=[".coveragerc"]
)  # the microgenerator has a good coveragerc file

# Don't treat docs warnings as errors
s.replace("noxfile.py", """["']-W["'],  # warnings as errors""", "")

s.shell.run(["nox", "-s", "blacken"], hide_output=False)
