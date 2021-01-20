# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Utilities for semantic versioning of model_preparers.

Format: major.minor.patch[-label]

major, minor, patch, must all be present and integers with no leading zeros.
They are compared numerically by segment. Label is an optional alphanumeric that
can be appended with a dash symbol.

Major version represents backwards compatibility; having same major version with
the library guarantees that the model is explainable. Minor version should
represent additional (non-breaking) features made to the library. Patch will
represents bug fixes and other small changes. For our library, cl number will be
used for patch field.

For more information about semantic versioning: https://semver.org/
"""

from __future__ import absolute_import
from __future__ import division

from __future__ import print_function

import re


# Only digits, with no leading zeros.
_DIGITS = r"(?:0|[1-9][0-9]*)"
# Digits, letters, underscores and dashes
_ALPHA_NUM = r"[-0-9A-Za-z_]+"

_SEMVER = (
    r"^(?P<major>{digits})\.(?P<minor>{digits})\.(?P<patch>{digits})"
    r"(?:\-(?P<label>{label}))?$"
).format(digits=_DIGITS, label=_ALPHA_NUM)


class ParseError(Exception):
    """An exception for when a string failed to parse as a valid semver."""

    pass


class SemanticVersion(object):
    """Object to hold a parsed semantic version string."""

    def __init__(self, version):
        """Creates a SemanticVersion object from the given version string.

    Args:
      version: str, The version string to parse.

    Raises:
      ParseError: If the version could not be correctly parsed.

    Returns:
      SemanticVersion, The parsed version.
    """
        (self.major, self.minor, self.patch, self.label) = SemanticVersion._from_string(
            version
        )

    @classmethod
    def _from_string(cls, version):
        """Parse the given version string into its parts."""
        if version is None:
            raise ParseError("The value is not a valid SemanticVersion string: [None]")

        try:
            match = re.match(_SEMVER, version)
        except (TypeError, re.error) as e:
            raise ParseError(
                "Error parsing version string: [{0}].  {1}".format(version, e)
            )

        if not match:
            raise ParseError(
                "The value is not a valid SemanticVersion string: [{0}]".format(version)
            )

        parts = match.groupdict()
        return (
            int(parts["major"]),
            int(parts["minor"]),
            int(parts["patch"]),
            parts["label"],
        )

    def to_string(self):
        """Returns the string representation of this version."""
        if not self.label:
            return "{}.{}.{}".format(self.major, self.minor, self.patch)
        return "{}.{}.{}-{}".format(self.major, self.minor, self.patch, self.label)

    @classmethod
    def _cmp_tuples(cls, x, y):
        """Just a helper equivalent to the cmp() function in Python 2."""
        return (x > y) - (x < y)

    def _compare(self, other):
        """Compare this SemanticVersion to other.

    Args:
      other: SemanticVersion, the other version to compare this one to.

    Returns:
      1 if self > other, -1 if other > self, 0 if equal.
    """
        # Compare the required parts.
        return SemanticVersion._cmp_tuples(
            (self.major, self.minor, self.patch),
            (other.major, other.minor, other.patch),
        )

    def __eq__(self, other):
        return other and (
            (self.major, self.minor, self.patch, self.label)
            == (other.major, other.minor, other.patch, other.label)
        )

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return self._compare(other) > 0

    def __lt__(self, other):
        return self._compare(other) < 0

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not self > other
