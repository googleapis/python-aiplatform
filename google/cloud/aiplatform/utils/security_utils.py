# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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

import hashlib
import hmac
import os
import re
from typing import Optional

_DEFAULT_SIGNING_KEY = "vertex-ai-fallback-signing-key-v1"


def validate_uri(uri: str):
    """Validates that a URI does not contain insecure protocols like SMB/UNC.

    Args:
        uri (str): Required. The URI string to validate.

    Raises:
        ValueError: If an insecure URI pattern is detected.
    """
    if uri.startswith("\\\\"):
        raise ValueError(
            f"Insecure UNC path detected: {uri}. Local network paths are forbidden."
        )

    # Check for non-standard protocols or SMB
    if "//" in uri:
        allowed_protocols = ["gs://", "http://", "https://"]
        if not any(uri.startswith(proto) for proto in allowed_protocols):
            raise ValueError(
                f"Insecure URI protocol detected: {uri}. "
                "Only gs://, http://, and https:// are allowed."
            )


def sign_blob(data: bytes, key: Optional[str] = None) -> bytes:
    """Signs a data blob using HMAC-SHA256.

    The signature is prepended to the data (32 bytes).

    Args:
        data (bytes): Required. The raw data to sign.
        key (str): Optional. The signing key. Falls back to $AIP_SIGNING_KEY.

    Returns:
        bytes: The signed blob (signature + data).
    """
    signing_key = key or os.environ.get("AIP_SIGNING_KEY", _DEFAULT_SIGNING_KEY)
    signature = hmac.new(signing_key.encode(), data, hashlib.sha256).digest()
    return signature + data


def verify_blob(signed_data: bytes, key: Optional[str] = None) -> bytes:
    """Verifies the HMAC signature of a blob and returns the original data.

    Args:
        signed_data (bytes): Required. The data blob containing the signature.
        key (str): Optional. The signing key for verification.

    Returns:
        bytes: The verified raw data.

    Raises:
        ValueError: If the signature is invalid or data is malformed.
    """
    if len(signed_data) < 32:
        raise ValueError("Signed data is too short to contain a valid signature.")

    signing_key = key or os.environ.get("AIP_SIGNING_KEY", _DEFAULT_SIGNING_KEY)
    signature = signed_data[:32]
    raw_data = signed_data[32:]

    expected_signature = hmac.new(
        signing_key.encode(), raw_data, hashlib.sha256
    ).digest()

    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError(
            "Security Error: Invalid signature detected. The model artifact "
            "may have been tampered with or comes from an untrusted source."
        )

    return raw_data
