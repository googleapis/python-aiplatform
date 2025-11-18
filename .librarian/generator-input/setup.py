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

import io
import os

import setuptools  # type: ignore

name = "google-cloud-aiplatform"
description = "Vertex AI API client library"

package_root = os.path.abspath(os.path.dirname(__file__))
readme_filename = os.path.join(package_root, "README.rst")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

version = {}
with open(os.path.join(package_root, "google/cloud/aiplatform/version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

packages = [
    package
    for package in setuptools.PEP420PackageFinder.find()
    if package.startswith("google") or package.startswith("vertexai")
]

# Add vertex_ray relative packages
packages += [
    package.replace("google.cloud.aiplatform.vertex_ray", "vertex_ray")
    for package in setuptools.PEP420PackageFinder.find()
    if package.startswith("google.cloud.aiplatform.vertex_ray")
]

profiler_extra_require = [
    "tensorboard-plugin-profile >= 2.4.0, <2.18.0",  # <3.0.0",
    "werkzeug >= 2.0.0, <4.0.0",
]
tensorboard_extra_require = profiler_extra_require

metadata_extra_require = ["pandas >= 1.0.0", "numpy>=1.15.0"]
xai_extra_require = ["tensorflow >=2.3.0, <3.0.0; python_version<'3.13'"]
lit_extra_require = [
    "tensorflow >= 2.3.0, <3.0.0; python_version<'3.13'",
    "pandas >= 1.0.0",
    "lit-nlp == 0.4.0; python_version<'3.14'",
    "explainable-ai-sdk >= 1.0.0; python_version<'3.13'",
]
featurestore_extra_require = [
    "google-cloud-bigquery-storage",
    "pandas >= 1.0.0",
    "pyarrow >= 6.0.1",
]
pipelines_extra_require = [
    "pyyaml>=5.3.1,<7",
]
datasets_extra_require = [
    "pyarrow >= 3.0.0, < 8.0.0; python_version<'3.11'",
    "pyarrow >= 10.0.1; python_version=='3.11'",
    "pyarrow >= 14.0.0; python_version>='3.12'",
]

vizier_extra_require = [
    "google-vizier>=0.1.6",
]

prediction_extra_require = [
    "docker >= 5.0.3",
    "fastapi >= 0.71.0, <=0.114.0",
    "httpx >=0.23.0, <=0.28.1",  # Optional dependency of fastapi
    "starlette >= 0.17.1",
    "uvicorn[standard] >= 0.16.0",
]

endpoint_extra_require = ["requests >= 2.28.1", "requests-toolbelt <= 1.0.0"]

private_endpoints_extra_require = [
    "urllib3 >=1.21.1, <1.27",
    "requests >= 2.28.1",
]

autologging_extra_require = [
    "mlflow>=1.27.0,<=2.16.0; python_version<'3.13'",
    "mlflow>=1.27.0; python_version>='3.13'",
]

preview_extra_require = []

ray_extra_require = [
    # Cluster only supports 2.9.3, 2.33.0, 2.42.0 and 2.47.1. Keep 2.4.0 for our
    # testing environment.
    # Note that testing is submitting a job in a cluster with Ray 2.9.3 remotely.
    (
        "ray[default] >= 2.4, <= 2.42.0,!= 2.5.*,!= 2.6.*,!= 2.7.*,!="
        " 2.8.*,!=2.9.0,!=2.9.1,!=2.9.2, !=2.10.*, !=2.11.*, !=2.12.*, !=2.13.*, !="
        " 2.14.*, !=2.15.*, !=2.16.*, !=2.17.*, !=2.18.*, !=2.19.*, !=2.20.*, !="
        " 2.21.*, !=2.22.*, !=2.23.*, !=2.24.*, !=2.25.*, !=2.26.*, !=2.27.*, !="
        " 2.28.*, !=2.29.*, !=2.30.*, !=2.31.*, !=2.32.*, !=2.34.*, !=2.35.*, !="
        " 2.36.*, !=2.37.*, !=2.38.*, !=2.39.*, !=2.40.*, !=2.41.*;"
        " python_version<'3.11'"
    ),
    # Ray Data v2.4 in Python 3.11 is broken, but got fixed in Ray v2.5.
    "ray[default] >= 2.5, <= 2.47.1; python_version=='3.11'",
    "google-cloud-bigquery-storage",
    "google-cloud-bigquery",
    "pandas >= 1.0.0",
    "pyarrow >= 6.0.1",
    "immutabledict",
]

genai_requires = (
    "pydantic < 3",
    "typing_extensions",
    "docstring_parser < 1",
)

ray_testing_extra_require = ray_extra_require + [
    "pytest-xdist",
    # ray train extras required for prediction tests
    "ray[train]",
    # Framework version constraints copied from testing_extra_require
    "scikit-learn<1.6.0",
    "tensorflow; python_version<'3.13'",
    "torch >= 2.0.0, < 2.1.0",
    "xgboost",
    "xgboost_ray",
]

adk_extra_require = [
    # 1.0.0 contains breaking changes, so we need to pin to 1.0.0.
    "google-adk >= 1.0.0, < 2.0.0",
    "opentelemetry-instrumentation-google-genai>=0.3b0, <1.0.0",
]

reasoning_engine_extra_require = [
    "cloudpickle >= 3.0, < 4.0",
    "google-cloud-trace < 2",
    "opentelemetry-sdk < 2",
    "opentelemetry-exporter-gcp-logging >= 1.11.0a0, < 2.0.0",
    "opentelemetry-exporter-gcp-trace < 2",
    "opentelemetry-exporter-otlp-proto-http < 2",
    "pydantic >= 2.11.1, < 3",
    "typing_extensions",
]

agent_engines_extra_require = [
    "packaging >= 24.0",
    "cloudpickle >= 3.0, < 4.0",
    "google-cloud-trace < 2",
    "google-cloud-logging < 4",
    "opentelemetry-sdk < 2",
    "opentelemetry-exporter-gcp-logging >= 1.11.0a0, < 2.0.0",
    "opentelemetry-exporter-gcp-trace < 2",
    "opentelemetry-exporter-otlp-proto-http < 2",
    "pydantic >= 2.11.1, < 3",
    "typing_extensions",
]

evaluation_extra_require = [
    "pandas >= 1.0.0",
    "tqdm>=4.23.0",
    "scikit-learn<1.6.0; python_version<='3.10'",
    "scikit-learn; python_version>'3.10'",
    "jsonschema",
    "ruamel.yaml",
    "pyyaml",
    "litellm >= 1.72.4, != 1.77.2, != 1.77.3, != 1.77.4",
]

langchain_extra_require = [
    "langchain >= 0.3, < 0.4",
    "langchain-core >= 0.3, < 0.4",
    "langchain-google-vertexai >= 2.0.22, < 3",
    "langgraph >= 0.2.45, < 0.4",
    "openinference-instrumentation-langchain >= 0.1.19, < 0.2",
]

langchain_testing_extra_require = list(
    set(
        langchain_extra_require
        + reasoning_engine_extra_require
        + ["absl-py", "pytest-xdist"]
    )
)

ag2_extra_require = [
    "ag2[gemini]",
    "openinference-instrumentation-autogen >= 0.1.6, < 0.2",
]

ag2_testing_extra_require = list(
    set(
        ag2_extra_require + reasoning_engine_extra_require + ["absl-py", "pytest-xdist"]
    )
)

llama_index_extra_require = [
    "llama-index",
    "llama-index-llms-google-genai",
    "openinference-instrumentation-llama-index >= 3.0, < 4.0",
]

llama_index_testing_extra_require = list(
    set(
        llama_index_extra_require
        + reasoning_engine_extra_require
        + ["absl-py", "pytest-xdist"]
    )
)

tokenization_extra_require = ["sentencepiece >= 0.2.0"]
tokenization_testing_extra_require = tokenization_extra_require + ["nltk"]

full_extra_require = list(
    set(
        tensorboard_extra_require
        + metadata_extra_require
        + xai_extra_require
        + lit_extra_require
        + featurestore_extra_require
        + pipelines_extra_require
        + datasets_extra_require
        + endpoint_extra_require
        + vizier_extra_require
        + prediction_extra_require
        + private_endpoints_extra_require
        + autologging_extra_require
        + preview_extra_require
        + ray_extra_require
        + evaluation_extra_require
    )
)
testing_extra_require = (
    full_extra_require
    + profiler_extra_require
    + tokenization_testing_extra_require
    + vizier_extra_require
    + [
        # aiohttp is required for async rest tests (need google-auth[aiohttp],
        # but can't specify extras in constraints files)
        "aiohttp",
        "bigframes; python_version>='3.10' and python_version<'3.14'",
        # google-api-core 2.x is required since kfp requires protobuf > 4
        "google-api-core >= 2.11, < 3.0.0",
        "grpcio-testing",
        "grpcio-tools >= 1.63.0; python_version>='3.13'",
        "ipython",
        "kfp >= 2.6.0, < 3.0.0; python_version<'3.13'",
        "pytest-asyncio",
        "pytest-cov",
        "mock",
        "pytest-xdist",
        "Pillow",
        "scikit-learn<1.6.0; python_version<='3.10'",
        "scikit-learn; python_version>'3.10'",
        # Lazy import requires > 2.12.0
        "tensorflow == 2.14.1; python_version<='3.11'",
        "tensorflow == 2.19.0; python_version>'3.11' and python_version<'3.13'",
        "protobuf <= 5.29.4",
        # TODO(jayceeli) torch 2.1.0 has conflict with pyfakefs, will check if
        # future versions fix this issue
        "torch >= 2.0.0, < 2.1.0; python_version<='3.11'",
        "torch >= 2.2.0; python_version>'3.11' and python_version<'3.13'",
        "requests-toolbelt <= 1.0.0",
        "immutabledict",
        "xgboost",
    ]
)


setuptools.setup(
    name=name,
    version=version,
    description=description,
    long_description=readme,
    packages=packages,
    package_dir={"vertex_ray": "google/cloud/aiplatform/vertex_ray"},
    package_data={"": ["*.html.j2"]},
    entry_points={
        "console_scripts": [
            "tb-gcp-uploader=google.cloud.aiplatform.tensorboard.uploader_main:run_main"
        ],
    },
    namespace_packages=("google", "google.cloud"),
    author="Google LLC",
    author_email="googleapis-packages@google.com",
    license="Apache 2.0",
    url="https://github.com/googleapis/python-aiplatform",
    platforms="Posix; MacOS X; Windows",
    include_package_data=True,
    install_requires=(
        (
            "google-api-core[grpc] >= 1.34.1,"
            " <3.0.0,!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*"
        ),
        "google-auth >= 2.14.1, <3.0.0",
        "proto-plus >= 1.22.3, <2.0.0",
        "protobuf>=3.20.2,<7.0.0,!=4.21.0,!=4.21.1,!=4.21.2,!=4.21.3,!=4.21.4,!=4.21.5",
        "packaging >= 14.3",
        "google-cloud-storage >= 1.32.0, < 4.0.0; python_version<'3.13'",
        "google-cloud-storage >= 2.10.0, < 4.0.0; python_version>='3.13'",
        "google-cloud-bigquery >= 1.15.0, < 4.0.0, !=3.20.0",
        "google-cloud-resource-manager >= 1.3.3, < 3.0.0",
        "shapely < 3.0.0",
        "google-genai >= 1.37.0, <2.0.0",
    )
    + genai_requires,
    extras_require={
        "endpoint": endpoint_extra_require,
        "full": full_extra_require,
        "metadata": metadata_extra_require,
        "tensorboard": tensorboard_extra_require,
        "testing": testing_extra_require,
        "xai": xai_extra_require,
        "lit": lit_extra_require,
        "cloud_profiler": profiler_extra_require,
        "pipelines": pipelines_extra_require,
        "vizier": vizier_extra_require,
        "prediction": prediction_extra_require,
        "datasets": datasets_extra_require,
        "private_endpoints": private_endpoints_extra_require,
        "autologging": autologging_extra_require,
        "preview": preview_extra_require,
        "ray": ray_extra_require,
        "ray_testing": ray_testing_extra_require,
        "adk": adk_extra_require,
        "reasoningengine": reasoning_engine_extra_require,
        "agent_engines": agent_engines_extra_require,
        "evaluation": evaluation_extra_require,
        "langchain": langchain_extra_require,
        "langchain_testing": langchain_testing_extra_require,
        "tokenization": tokenization_extra_require,
        "ag2": ag2_extra_require,
        "ag2_testing": ag2_testing_extra_require,
        "llama_index": llama_index_extra_require,
        "llama_index_testing": llama_index_testing_extra_require,
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)
