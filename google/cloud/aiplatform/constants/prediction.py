# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re


# [region]-docker.pkg.dev/vertex-ai/prediction/[framework]-[accelerator].[version]:latest
CONTAINER_URI_PATTERN = re.compile(
    r"(?P<region>[\w]+)\-docker\.pkg\.dev\/vertex\-ai\/prediction\/"
    r"(?P<framework>[\w]+)\-(?P<accelerator>[\w]+)\.(?P<version>[\d-]+):latest"
)

SKLEARN = "sklearn"
TF = "tf"
TF2 = "tf2"
XGBOOST = "xgboost"

XGBOOST_CONTAINER_URIS = [
    "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-4:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-4:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-4:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-3:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-3:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-3:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-2:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-2:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-2:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-1:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-1:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-1:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.0-90:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.0-90:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.0-90:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.0-82:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.0-82:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.0-82:latest",
]

SKLEARN_CONTAINER_URIS = [
    "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-24:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-24:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-24:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-23:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-23:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-23:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-22:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-22:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-22:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-20:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-20:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-20:latest",
]

TF_CONTAINER_URIS = [
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-6:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-6:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-6:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-6:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-6:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-6:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-5:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-5:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-5:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-5:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-5:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-5:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-4:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-4:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-4:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-4:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-4:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-4:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-3:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-3:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-3:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-3:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-3:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-3:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-2:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-2:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-2:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-2:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-2:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-2:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-1:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-1:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-1:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf-cpu.1-15:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf-cpu.1-15:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf-cpu.1-15:latest",
    "us-docker.pkg.dev/vertex-ai/prediction/tf-gpu.1-15:latest",
    "europe-docker.pkg.dev/vertex-ai/prediction/tf-gpu.1-15:latest",
    "asia-docker.pkg.dev/vertex-ai/prediction/tf-gpu.1-15:latest",
]

# Pattern:
# {user_provided_framework: framework_name_in_uri}
_FRAMEWORK_TO_URI_REF = {
    SKLEARN: SKLEARN,
    "scikitlearn": SKLEARN,
    "scikit-learn": SKLEARN,
    TF: TF,
    "tensorflow": TF,
    XGBOOST: XGBOOST,
    "xgb": XGBOOST,
}

# Pattern:
# {framework: (accelerator, no_accelerator)}
_ACCELERATOR_TO_URI_REF = {
    # If `None`, accelerator is not supported
    SKLEARN: (None, "cpu"),
    TF: ("gpu", "cpu"),
    TF2: ("gpu", "cpu"),
    XGBOOST: (None, "cpu"),
}

SERVING_CONTAINER_URIS = (
    SKLEARN_CONTAINER_URIS + TF_CONTAINER_URIS + XGBOOST_CONTAINER_URIS
)

# All Vertex AI Prediction first-party prediction containers as a string
_SERVING_CONTAINER_URIS_STR = " ".join(SERVING_CONTAINER_URIS)

_SERVING_CONTAINER_DOCUMENTATION_URL = (
    "https://cloud.google.com/vertex-ai/docs/predictions/pre-built-containers"
)
