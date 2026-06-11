# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
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
from __future__ import annotations

from typing import MutableMapping, MutableSequence

import proto  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "Rubric",
        "RubricGroup",
        "RubricVerdict",
    },
)


class Rubric(proto.Message):
    r"""Message representing a single testable criterion for
    evaluation. One input prompt could have multiple rubrics.


    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        rubric_id (str):
            Unique identifier for the rubric.
            This ID is used to refer to this rubric, e.g.,
            in RubricVerdict.
        content (google.cloud.aiplatform_v1beta1.types.Rubric.Content):
            Required. The actual testable criteria for
            the rubric.
        type_ (str):
            Optional. A type designator for the rubric, which can inform
            how it's evaluated or interpreted by systems or users. It's
            recommended to use consistent, well-defined, upper
            snake_case strings. Examples: "SUMMARIZATION_QUALITY",
            "SAFETY_HARMFUL_CONTENT", "INSTRUCTION_ADHERENCE".

            This field is a member of `oneof`_ ``_type``.
        importance (google.cloud.aiplatform_v1beta1.types.Rubric.Importance):
            Optional. The relative importance of this
            rubric.

            This field is a member of `oneof`_ ``_importance``.
    """

    class Importance(proto.Enum):
        r"""Importance level of the rubric.

        Values:
            IMPORTANCE_UNSPECIFIED (0):
                Importance is not specified.
            HIGH (1):
                High importance.
            MEDIUM (2):
                Medium importance.
            LOW (3):
                Low importance.
        """

        IMPORTANCE_UNSPECIFIED = 0
        HIGH = 1
        MEDIUM = 2
        LOW = 3

    class Content(proto.Message):
        r"""Content of the rubric, defining the testable criteria.

        .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

        Attributes:
            property (google.cloud.aiplatform_v1beta1.types.Rubric.Content.Property):
                Evaluation criteria based on a specific
                property.

                This field is a member of `oneof`_ ``content_type``.
        """

        class Property(proto.Message):
            r"""Defines criteria based on a specific property.

            Attributes:
                description (str):
                    Description of the property being evaluated.
                    Example: "The model's response is grammatically
                    correct.".
            """

            description: str = proto.Field(
                proto.STRING,
                number=1,
            )

        property: "Rubric.Content.Property" = proto.Field(
            proto.MESSAGE,
            number=1,
            oneof="content_type",
            message="Rubric.Content.Property",
        )

    rubric_id: str = proto.Field(
        proto.STRING,
        number=1,
    )
    content: Content = proto.Field(
        proto.MESSAGE,
        number=2,
        message=Content,
    )
    type_: str = proto.Field(
        proto.STRING,
        number=3,
        optional=True,
    )
    importance: Importance = proto.Field(
        proto.ENUM,
        number=4,
        optional=True,
        enum=Importance,
    )


class RubricGroup(proto.Message):
    r"""A group of rubrics, used for grouping rubrics based on a
    metric or a version.

    Attributes:
        group_id (str):
            Unique identifier for the group.
        display_name (str):
            Human-readable name for the group. This
            should be unique  within a given context if used
            for display or selection.  Example: "Instruction
            Following V1", "Content Quality - Summarization
            Task".
        rubrics (MutableSequence[google.cloud.aiplatform_v1beta1.types.Rubric]):
            Rubrics that are part of this group.
    """

    group_id: str = proto.Field(
        proto.STRING,
        number=1,
    )
    display_name: str = proto.Field(
        proto.STRING,
        number=2,
    )
    rubrics: MutableSequence["Rubric"] = proto.RepeatedField(
        proto.MESSAGE,
        number=3,
        message="Rubric",
    )


class RubricVerdict(proto.Message):
    r"""Represents the verdict of an evaluation against a single
    rubric.


    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        evaluated_rubric (google.cloud.aiplatform_v1beta1.types.Rubric):
            Required. The full rubric definition that was
            evaluated. Storing this ensures the verdict is
            self-contained and understandable, especially if
            the original rubric definition changes or was
            dynamically generated.
        verdict (bool):
            Required. Outcome of the evaluation against the rubric,
            represented as a boolean. ``true`` indicates a "Pass",
            ``false`` indicates a "Fail".
        reasoning (str):
            Optional. Human-readable reasoning or
            explanation for the verdict. This can include
            specific examples or details from the evaluated
            content that justify the given verdict.

            This field is a member of `oneof`_ ``_reasoning``.
    """

    evaluated_rubric: "Rubric" = proto.Field(
        proto.MESSAGE,
        number=1,
        message="Rubric",
    )
    verdict: bool = proto.Field(
        proto.BOOL,
        number=2,
    )
    reasoning: str = proto.Field(
        proto.STRING,
        number=3,
        optional=True,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
