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

import setuptools  # type: ignore

version = "0.3.0"

setuptools.setup(
    name="google-cloud-aiplatform",
    version=version,
    packages=setuptools.PEP420PackageFinder.find(),
    namespace_packages=("google", "google.cloud"),
    author="Google LLC",
    author_email="googleapis-packages@google.com",
    license="Apache 2.0",
    url="https://github.com/googleapis/python-aiplatform",
    platforms="Posix; MacOS X; Windows",
    include_package_data=True,
    install_requires=(
        "google-api-core[grpc] >= 1.22.2, < 2.0.0dev",
        "libcst >= 0.2.5",
        "proto-plus >= 1.10.1",
        "mock >= 4.0.2",
        "google-cloud-storage >= 1.26.0, < 2.0.0dev",
    ),
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
