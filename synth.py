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

gapic = gcp.GAPICBazel()

common = gcp.CommonTemplates()

# ----------------------------------------------------------------------------
# Generate AI Platform GAPIC layer
# ----------------------------------------------------------------------------


versions = ["v1beta1", "v1"]

for version in versions:
    library = gapic.py_library(
        service="aiplatform",
        version=version,
        bazel_target=f"//google/cloud/aiplatform/{version}:aiplatform-{version}-py",
    )

    s.move(
        library,
        excludes=[
            ".pre-commit-config.yaml",
            "setup.py",
            "README.rst",
            "docs/index.rst",
            f"docs/definition_{version}/services.rst",
            f"docs/instance_{version}/services.rst",
            f"docs/params_{version}/services.rst",
            f"docs/prediction_{version}/services.rst",
            f"scripts/fixup_aiplatform_{version}_keywords.py",
            f"scripts/fixup_definition_{version}_keywords.py",
            f"scripts/fixup_instance_{version}_keywords.py",
            f"scripts/fixup_params_{version}_keywords.py",
            f"scripts/fixup_prediction_{version}_keywords.py",
            "google/cloud/aiplatform/__init__.py",
            f"google/cloud/aiplatform/{version}/schema/**/services/",
            f"tests/unit/gapic/aiplatform_{version}/test_prediction_service.py",
            f"tests/unit/gapic/definition_{version}/",
            f"tests/unit/gapic/instance_{version}/",
            f"tests/unit/gapic/params_{version}/",
            f"tests/unit/gapic/prediction_{version}/",
        ],
    )

    # ---------------------------------------------------------------------
    # Patch each version of the library
    # ---------------------------------------------------------------------

    # https://github.com/googleapis/gapic-generator-python/issues/413
#    s.replace(
#        f"google/cloud/aiplatform_{version}/services/prediction_service/client.py",
#        "request.instances = instances",
#        "request.instances.extend(instances)",
#    )

    # https://github.com/googleapis/gapic-generator-python/issues/672
#    s.replace(
#        "google/cloud/aiplatform_{version}/services/endpoint_service/client.py",
#        "request.traffic_split.extend\(traffic_split\)",
#        "request.traffic_split = traffic_split",
#    )

# ----------------------------------------------------------------------------
# Patch the library
# ----------------------------------------------------------------------------


# Generator adds a bad import statement to enhanced type;
# need to fix in post-processing steps.
#s.replace(
#    "google/cloud/aiplatform/v1beta1/schema/predict/prediction_v1beta1/types/text_sentiment.py",
#    "text_sentiment_pb2 as gcaspi_text_sentiment  # type: ignore",
#    "TextSentimentPredictionInstance")

#s.replace(
#    "google/cloud/aiplatform/v1beta1/schema/predict/prediction_v1beta1/types/text_sentiment.py",
#    "message=gcaspi_text_sentiment.TextSentimentPredictionInstance,",
#    "message=TextSentimentPredictionInstance,")



# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------

templated_files = common.py_library(cov_level=99, microgenerator=True)
s.move(
    templated_files,
    excludes=[
        ".coveragerc",
        ".kokoro/samples/**"
    ]
)  # the microgenerator has a good coveragerc file

# Don't treat docs warnings as errors
s.replace("noxfile.py", """["']-W["'],  # warnings as errors""", "")

s.shell.run(["nox", "-s", "blacken"], hide_output=False)
