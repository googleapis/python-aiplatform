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

# Builds google-cloud-agentplatform and uploads it to the release staging
# repository.
#
# Publishing to PyPI is a separate, manually approved step; the command to do it
# is printed at the end. google-cloud-aiplatform is released independently from
# the same tag and shares no staging state with this package.

set -eo pipefail

readonly EG_PROJECT="google-cloud-agentplatform"
readonly EG_REPO="${EG_PROJECT}--pypi"
readonly EG_REPO_LOCATION="us"
readonly EG_REPO_PROJECT="oss-exit-gate-prod"
readonly EG_BUCKET="oss-exit-gate-prod-projects-bucket"
readonly EG_BUCKET_PATH="${EG_PROJECT}/pypi/manifests"

readonly REPO_DIR="${KOKORO_ARTIFACTS_DIR}/github/python-aiplatform"

# The distributable lives in a subdirectory but packages a source tree that sits
# at the repository root.
readonly PACKAGE_DIR="pypi/google_cloud_agentplatform"
readonly SOURCE_TREE="agentplatform"

function checkout_release_tag() {
  cd "${REPO_DIR}"
  # The checkout is owned by a different uid than the build process, which git
  # refuses to operate on until the path is marked safe.
  git config --global --add safe.directory "${REPO_DIR}"
  if [[ -n "${_LOUHI_TAG_NAME:-}" ]]; then
    echo "Tag trigger detected; checking out ${_LOUHI_TAG_NAME}"
    git fetch --tags origin || true
    git checkout "${_LOUHI_TAG_NAME}"
  else
    echo "No tag supplied; building the checked-out revision:"
    git log -1 --oneline
  fi
}

function stage_sources() {
  # setuptools will not carry sources from outside the project root: built in
  # place, the sdist contains no code and the wheel is derived from that sdist.
  # Copy the contents rather than the directory, so that a rerun on a warm
  # workspace cannot nest agentplatform/agentplatform/.
  echo "Staging ${SOURCE_TREE} into ${PACKAGE_DIR}"
  rm -rf "${REPO_DIR:?}/${PACKAGE_DIR}/${SOURCE_TREE}"
  mkdir -p "${REPO_DIR}/${PACKAGE_DIR}/${SOURCE_TREE}"
  cp -r "${REPO_DIR}/${SOURCE_TREE}/." "${REPO_DIR}/${PACKAGE_DIR}/${SOURCE_TREE}/"
}

function build_package() {
  cd "${REPO_DIR}/${PACKAGE_DIR}"
  # Pinned: these run with credentials that can write to the staging repository,
  # so the release must not pick up whatever happens to be latest on PyPI that
  # day. Bump deliberately.
  python3 -m pip install \
    "build==1.6.0" \
    "twine==7.0.0" \
    "keyring==25.7.0" \
    "keyrings.google-artifactregistry-auth==1.1.2"
  rm -rf dist
  python3 -m build --outdir dist
  ls -al dist/
}

function read_version() {
  sed -nE "s/^__version__[[:space:]]*=[[:space:]]*['\"]([^'\"]+)['\"].*/\1/p" \
    "${REPO_DIR}/${PACKAGE_DIR}/${SOURCE_TREE}/version.py"
}

# Drop any existing copy of this version, so that retrying after a failed or
# partial upload cannot leave a stale artifact in place. This is hygiene, not
# correctness: if it cannot run, the upload below still refuses to overwrite an
# existing version, so a retry fails loudly rather than shipping something
# unexpected.
function clear_staged_version() {
  local version=$1
  if ! command -v gcloud &>/dev/null; then
    echo "gcloud unavailable; skipping cleanup of any previously staged ${version}"
    return
  fi
  gcloud --project="${EG_REPO_PROJECT}" -q \
    artifacts versions delete \
    --repository="${EG_REPO}" \
    --location="${EG_REPO_LOCATION}" \
    --package="${EG_PROJECT}" \
    "${version}" || echo "nothing staged for ${version} yet"
}

function upload_package() {
  cd "${REPO_DIR}/${PACKAGE_DIR}"
  twine upload \
    --repository-url "https://${EG_REPO_LOCATION}-python.pkg.dev/${EG_REPO_PROJECT}/${EG_REPO}/" \
    --verbose \
    dist/*
}

function write_manifest() {
  local version=$1
  # Name the exact version rather than publishing everything staged, so that
  # anything left behind by an abandoned build cannot be swept into a release.
  cat >"${REPO_DIR}/${PACKAGE_DIR}/publish-${version}.json" <<EOF
{
  "publish_all": false,
  "publishing_groups": [
    {
      "packages": [
        {
          "name": "${EG_PROJECT}",
          "version": "${version}"
        }
      ]
    }
  ]
}
EOF
}


checkout_release_tag
stage_sources
build_package

version="$(read_version)"
if [[ -z "${version}" ]]; then
  echo "Failed to read __version__ from ${PACKAGE_DIR}/${SOURCE_TREE}/version.py" >&2
  exit 1
fi
echo "Staging ${EG_PROJECT} ${version}"

clear_staged_version "${version}"
upload_package
write_manifest "${version}"

cat <<EOF

${EG_PROJECT} ${version} is staged for release.

Publishing to PyPI requires approval. An authorized release owner runs:

  gcloud storage cp \\
    ${REPO_DIR}/${PACKAGE_DIR}/publish-${version}.json \\
    gs://${EG_BUCKET}/${EG_BUCKET_PATH}/publish-${version}.json

The manifest is also saved as a build artifact.
EOF
