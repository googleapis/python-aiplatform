#!/bin/bash
# Copyright 2023 Google LLC
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

set -eo pipefail

# Start the releasetool reporter
python3 -m pip install --require-hashes  --no-deps -r github/python-aiplatform/.kokoro/requirements.txt
python3 -m releasetool publish-reporter-script > /tmp/publisher-script; source /tmp/publisher-script

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

# Move into the `google-cloud-aiplatform` package, build the distribution and upload.
GCA_TWINE_PASSWORD=$(cat "${KOKORO_KEYSTORE_DIR}/73713_google-cloud-pypi-token-keystore-3")
cd github/python-aiplatform
python3 setup.py sdist bdist_wheel
twine upload --username __token__ --password "${GCA_TWINE_PASSWORD}" dist/*

# Move into the `vertexai` package, build the distribution and upload.
VERTEXAI_TWINE_PASSWORD=$(cat "${KOKORO_KEYSTORE_DIR}/73713_vertexai-pypi-token-2")
cd pypi/_vertex_ai_placeholder
python3 -m build
twine upload --username __token__ --password "${VERTEXAI_TWINE_PASSWORD}" dist/*


