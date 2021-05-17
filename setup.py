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
version = "0.9.0"
description = "Cloud AI Platform API client library"

package_root = os.path.abspath(os.path.dirname(__file__))
readme_filename = os.path.join(package_root, "README.rst")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

tensorboard_extra_require = [
    "tensorflow-cpu>=2.3.0, <=2.5.0",
    "grpcio~=1.34.0",
    "six~=1.15.0",
]
metadata_extra_require = ["pandas >= 1.0.0"]
full_extra_require = tensorboard_extra_require + metadata_extra_require
testing_extra_require = full_extra_require + ["grpcio-testing ~= 1.34.0"]


setuptools.setup(
    name=name,
    version=version,
    description=description,
    long_description=readme,
    packages=setuptools.PEP420PackageFinder.find(),
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
        "google-api-core[grpc] >= 1.22.2, < 2.0.0dev",
        "proto-plus >= 1.10.1",
        "packaging >= 14.3",
        "google-cloud-storage >= 1.32.0, < 2.0.0dev",
        "google-cloud-bigquery >= 1.15.0, < 3.0.0dev",
    ),
    extras_require={
        "full": full_extra_require,
        "metadata": metadata_extra_require,
        "tensorboard": tensorboard_extra_require,
        "testing": testing_extra_require,
    },
    python_requires=">=3.6",
    scripts=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)
