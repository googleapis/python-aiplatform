# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

tensorboard_extra_require = ["tensorflow >=2.3.0, <3.0.0dev"]
metadata_extra_require = ["pandas >= 1.0.0"]
xai_extra_require = ["tensorflow >=2.3.0, <3.0.0dev"]
lit_extra_require = [
    "tensorflow >= 2.3.0, <3.0.0dev",
    "pandas >= 1.0.0",
    "lit-nlp >= 0.4.0",
    "explainable-ai-sdk >= 1.0.0",
]
profiler_extra_require = [
    "tensorboard-plugin-profile >= 2.4.0, <3.0.0dev",
    "werkzeug >= 2.0.0, <2.1.0dev",
    "tensorflow >=2.4.0, <3.0.0dev",
]
featurestore_extra_require = [
    "google-cloud-bigquery-storage",
    "pandas >= 1.0.0",
    "pyarrow >= 6.0.1",
]
pipelines_extra_require = [
    "pyyaml>=5.3,<6",
]
datasets_extra_require = [
    "pyarrow >= 3.0.0, < 8.0dev",
]
private_endpoints_extra_require = [
    "urllib3 >=1.21.1, <1.27",
]
full_extra_require = list(
    set(
        tensorboard_extra_require
        + metadata_extra_require
        + xai_extra_require
        + lit_extra_require
        + featurestore_extra_require
        + pipelines_extra_require
        + datasets_extra_require
        + private_endpoints_extra_require
    )
)
testing_extra_require = (
    full_extra_require
    + profiler_extra_require
    + ["grpcio-testing", "pytest-xdist", "ipython", "kfp"]
)


setuptools.setup(
    name=name,
    version=version,
    description=description,
    long_description=readme,
    packages=[
        package
        for package in setuptools.PEP420PackageFinder.find()
        if package.startswith("google")
    ],
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
        "google-api-core[grpc] >= 1.32.0, <3.0.0dev,!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*",
        "proto-plus >= 1.15.0, <2.0.0dev",
        "protobuf >= 3.19.0, <4.0.0dev",
        "packaging >= 14.3, <22.0.0dev",
        "google-cloud-storage >= 1.32.0, < 3.0.0dev",
        "google-cloud-bigquery >= 1.15.0, < 3.0.0dev",
        "google-cloud-resource-manager >= 1.3.3, < 3.0.0dev",
    ),
    extras_require={
        "full": full_extra_require,
        "metadata": metadata_extra_require,
        "tensorboard": tensorboard_extra_require,
        "testing": testing_extra_require,
        "xai": xai_extra_require,
        "lit": lit_extra_require,
        "cloud_profiler": profiler_extra_require,
        "pipelines": pipelines_extra_require,
        "datasets": datasets_extra_require,
        "private_endpoints": private_endpoints_extra_require,
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)
