# -*- coding: utf-8 -*-
# Copyright 2026 Google LLC
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
"""Verification script for google-cloud-agentplatform imports."""

import importlib
import logging
import sys

# This runs against an installed wheel outside google3, so it configures the
# stdlib root logger rather than using absl. The exit code is the signal for
# callers; the messages are for whoever is watching the build.
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

# Loaded by name: copy.bara.sky rewrites spelled-out agentplatform imports in
# both directions, and a literal one here fails its reversibility check.
_PACKAGE = "agentplatform"

# Subpackages that setuptools only ships if they are listed in the
# `[tool.setuptools.packages.find] include` glob. Importing the top-level
# package does not reach them, so a missing entry there stays invisible until a
# user hits ModuleNotFoundError against the published wheel.
_SUBMODULES = (
    "frameworks",
    "frameworks.a2a",
)


def main():
    logging.info("Importing %s...", _PACKAGE)
    try:
        package = importlib.import_module(_PACKAGE)
    except ImportError as e:
        logging.error("Failed to import %s: %s", _PACKAGE, e)
        sys.exit(1)
    logging.info("Successfully imported %s.", _PACKAGE)

    logging.info("Instantiating %s.Client...", _PACKAGE)
    try:
        # Use dummy project and location for import verification.
        package.Client(project="dummy-project", location="us-central1")
    except Exception as e:
        logging.error("Failed to instantiate %s.Client: %s", _PACKAGE, e)
        sys.exit(1)
    logging.info("Successfully instantiated %s.Client.", _PACKAGE)

    for submodule in _SUBMODULES:
        name = f"{_PACKAGE}.{submodule}"
        logging.info("Importing %s...", name)
        try:
            importlib.import_module(name)
        except ImportError as e:
            logging.error("Failed to import %s: %s", name, e)
            sys.exit(1)
        logging.info("Successfully imported %s.", name)

    logging.info("Verification passed.")


if __name__ == "__main__":
    main()
