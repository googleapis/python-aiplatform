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
library = gapic.py_library(
    'aiplatform',
    'v1beta1',
    generator_version='0.20'
)

s.move(
	library,
	excludes=[
		"setup.py",
		"README.rst",
		"docs/index.rst",
	]
)

# ----------------------------------------------------------------------------
# Patch the library
# ----------------------------------------------------------------------------

# https://github.com/googleapis/gapic-generator-python/issues/336
s.replace(
    '**/client.py',
    ' operation.from_gapic',
    ' ga_operation.from_gapic'
)

s.replace(
    '**/client.py',
    'client_options: ClientOptions = ',
    'client_options: ClientOptions.ClientOptions = '
)

# https://github.com/googleapis/gapic-generator-python/issues/413
s.replace(
    'google/cloud/aiplatform_v1alpha1/services/prediction_service/client.py',
    'request.instances = instances',
    'request.instances.extend(instances)'
)

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------

templated_files = common.py_library(cov_level=99, microgenerator=True)
s.move(
    templated_files, excludes=[".coveragerc"] 
) # the microgenerator has a good coveragerc file

s.shell.run(["nox", "-s", "blacken"], hide_output=False)