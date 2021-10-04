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
version = "1.5.0"
description = "Cloud AI Platform API client library"

package_root = os.path.abspath(os.path.dirname(__file__))
readme_filename = os.path.join(package_root, "README.rst")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

tensorboard_extra_require = ["tensorflow >=2.3.0, <=2.5.0"]
metadata_extra_require = ["pandas >= 1.0.0"]
xai_extra_require = ["tensorflow >=2.3.0, <=2.5.0"]
full_extra_require = list(
    set(tensorboard_extra_require + metadata_extra_require + xai_extra_require)
)
testing_extra_require = full_extra_require + ["grpcio-testing", "pytest-xdist"]


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
        # NOTE: Maintainers, please do not require google-api-core>=2.x.x
        # Until this issue is closed
        # https://github.com/googleapis/google-cloud-python/issues/10566
        "google-api-core[grpc] >= 1.26.0, <3.0.0dev",
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
        "xai": xai_extra_require,
    },
    python_requires=">=3.6",
    scripts=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
