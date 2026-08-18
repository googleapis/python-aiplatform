#!/bin/bash
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

set -exu

# Optional destination folder in GCS
folder="${1:-}"

TEMP_DIR=$(mktemp -d)
echo "Temporary directory: $TEMP_DIR"

cleanup() {
  echo "Cleaning up..."
  rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Get directory of this script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
RUN_DIR="$PWD"

# Resolve google3 directory and workspace root
GOOGLE3_DIR=$(cd "$SCRIPT_DIR/../../../../../../../" && pwd)
COPYBARA_SKY="$SCRIPT_DIR/../../copy.bara.sky"

# Run Copybara to temporary directory
/google/bin/releases/copybara/public/copybara/copybara \
  "$COPYBARA_SKY" \
  folder_to_folder \
  "$GOOGLE3_DIR/.." \
  --folder-dir="$TEMP_DIR" \
  --ignore-noop

# Go to the package directory in the temp dir
cd "$TEMP_DIR/pypi/google_cloud_agentplatform"

# setuptools will not carry sources from outside the project root into an
# sdist. Leaving the package at the repo root produces an sdist with no code,
# and `build` makes the wheel from that sdist, so it ships empty. Stage the
# package inside the project instead.
cp -r "$TEMP_DIR/agentplatform" ./agentplatform

# Build the sdist and wheel (requires setuptools to be installed in the environment)
python3 -m build --no-isolation --outdir ./whl-output

# Get version from the transformed source
version_file="./agentplatform/version.py"
pkg_version=$(grep '__version__' "$version_file" | sed -E "s/__version__\s*=\s*['\"]([^'\"]+)['\"].*/\1/")
whl_file="./whl-output/google_cloud_agentplatform-$pkg_version-py3-none-any.whl"
sdist_file="./whl-output/google_cloud_agentplatform-$pkg_version.tar.gz"

# Copy or upload
if [[ -n "$folder" ]]; then
  echo "Uploading to gs://unified-genai-dev/$folder/"
  gcloud storage cp "$whl_file" "$sdist_file" "gs://unified-genai-dev/$folder/"
else
  echo "Copying distributions to original directory..."
  cp "$whl_file" "$sdist_file" "$RUN_DIR/"
  echo "Distributions copied to $RUN_DIR/"
fi
