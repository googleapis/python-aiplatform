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
    "tensorboard-plugin-profile >= 2.4.0, <3.0.0dev",
    "werkzeug >= 2.0.0, <2.1.0dev",
    "tensorflow >=2.4.0, <3.0.0dev",
]
tensorboard_extra_require = [
    "tensorflow >=2.3.0, <3.0.0dev; python_version<='3.11'"
] + profiler_extra_require

metadata_extra_require = ["pandas >= 1.0.0", "numpy>=1.15.0"]
xai_extra_require = ["tensorflow >=2.3.0, <3.0.0dev"]
lit_extra_require = [
    "tensorflow >= 2.3.0, <3.0.0dev",
    "pandas >= 1.0.0",
    "lit-nlp == 0.4.0",
    "explainable-ai-sdk >= 1.0.0",
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
    "pyarrow >= 3.0.0, < 8.0dev; python_version<'3.11'",
    "pyarrow >= 10.0.1; python_version=='3.11'",
    "pyarrow >= 14.0.0; python_version>='3.12'",
]

vizier_extra_require = [
    "google-vizier>=0.1.6",
]

prediction_extra_require = [
    "docker >= 5.0.3",
    "fastapi >= 0.71.0, <=0.109.1",
    "httpx >=0.23.0, <0.25.0",  # Optional dependency of fastapi
    "starlette >= 0.17.1",
    "uvicorn[standard] >= 0.16.0",
]

endpoint_extra_require = ["requests >= 2.28.1"]

private_endpoints_extra_require = [
    "urllib3 >=1.21.1, <1.27",
    "requests >= 2.28.1",
]

autologging_extra_require = ["mlflow>=1.27.0,<=2.1.1"]

preview_extra_require = [
    "cloudpickle < 3.0",
    "google-cloud-logging < 4.0",
]

ray_extra_require = [
    # Cluster only supports 2.9.3. Keep 2.4.0 for our testing environment.
    # Note that testing is submiting a job in a cluster with Ray 2.9.3 remotely.
    (
        "ray[default] >= 2.4, <= 2.9.3,!= 2.5.*,!= 2.6.*,!= 2.7.*,!="
        " 2.8.*,!=2.9.0,!=2.9.1,!=2.9.2; python_version<'3.11'"
    ),
    # To avoid  ImportError: cannot import name 'packaging' from 'pkg)resources'
    "setuptools < 70.0.0",
    # Ray Data v2.4 in Python 3.11 is broken, but got fixed in Ray v2.5.
    "ray[default] >= 2.5, <= 2.9.3; python_version=='3.11'",
    "google-cloud-bigquery-storage",
    "google-cloud-bigquery",
    "pandas >= 1.0.0, < 2.2.0",
    "pyarrow >= 6.0.1",
    # Workaround for https://github.com/ray-project/ray/issues/36990.
    # TODO(b/295406381): Remove this pin when we drop support of ray<=2.5.
    "pydantic < 2",
    "immutabledict",
]

genai_requires = (
    "pydantic < 3",
    "docstring_parser < 1",
)

ray_testing_extra_require = ray_extra_require + [
    "pytest-xdist",
    # ray train extras required for prediction tests
    "ray[train] == 2.9.3",
    # Framework version constraints copied from testing_extra_require
    "scikit-learn",
    "tensorflow",
    "torch >= 2.0.0, < 2.1.0",
    "xgboost",
    "xgboost_ray",
]

reasoning_engine_extra_require = [
    "cloudpickle >= 3.0, < 4.0",
    "opentelemetry-sdk < 2",
    "opentelemetry-exporter-gcp-trace < 2",
    "pydantic >= 2.6.3, < 3",
]

rapid_evaluation_extra_require = [
    "pandas >= 1.0.0, < 2.2.0",
    "tqdm>=4.23.0",
]

langchain_extra_require = [
    "langchain >= 0.1.16, < 0.3",
    "langchain-core < 0.2",
    "langchain-google-vertexai < 2",
    "openinference-instrumentation-langchain >= 0.1.19, < 0.2",
    "tenacity <= 8.3",
]

langchain_testing_extra_require = list(
    set(
        langchain_extra_require
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
        + rapid_evaluation_extra_require
    )
)
testing_extra_require = (
    full_extra_require
    + profiler_extra_require
    + tokenization_testing_extra_require
    + [
        "bigframes; python_version>='3.10'",
        # google-api-core 2.x is required since kfp requires protobuf > 4
        "google-api-core >= 2.11, < 3.0.0",
        "grpcio-testing",
        "ipython",
        "kfp >= 2.6.0, < 3.0.0",
        "pyfakefs",
        "pytest-asyncio",
        "pytest-xdist",
        "scikit-learn",
        # Lazy import requires > 2.12.0
        "tensorflow == 2.13.0; python_version<='3.11'",
        "tensorflow == 2.16.1; python_version>'3.11'",
        # TODO(jayceeli) torch 2.1.0 has conflict with pyfakefs, will check if
        # future versions fix this issue
        "torch >= 2.0.0, < 2.1.0; python_version<='3.11'",
        "torch >= 2.2.0; python_version>'3.11'",
        "requests-toolbelt < 1.0.0",
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
            " <3.0.0dev,!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*"
        ),
        "google-auth >= 2.14.1, <3.0.0dev",
        "proto-plus >= 1.22.0, <2.0.0dev",
        "protobuf>=3.19.5,<5.0.0dev,!=3.20.0,!=3.20.1,!=4.21.0,!=4.21.1,!=4.21.2,!=4.21.3,!=4.21.4,!=4.21.5",
        "packaging >= 14.3",
        "google-cloud-storage >= 1.32.0, < 3.0.0dev",
        "google-cloud-bigquery >= 1.15.0, < 4.0.0dev, !=3.20.0",
        "google-cloud-resource-manager >= 1.3.3, < 3.0.0dev",
        "shapely < 3.0.0dev",
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
        "reasoningengine": reasoning_engine_extra_require,
        "rapid_evaluation": rapid_evaluation_extra_require,
        "langchain": langchain_extra_require,
        "langchain_testing": langchain_testing_extra_require,
        "tokenization": tokenization_extra_require,
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)
