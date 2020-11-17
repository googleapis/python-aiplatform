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


import pytest
from uuid import uuid4
from random import choice
from random import randint
from string import ascii_letters

from google.cloud import aiplatform
from google.cloud.aiplatform.utils import Fields
from google.cloud.aiplatform.utils import extract_fields_from_resource_name


@pytest.mark.parametrize(
    "resource_name, expected",
    [
        ("projects/123456/locations/us-central1/datasets/987654", True),
        ("projects/857392/locations/us-central1/trainingPipelines/347292", True),
        ("projects/acme-co-proj-1/locations/us-central1/datasets/123456", True),
        ("projects/acme-co-proj-1/locations/us-central1/datasets/abcdef", False),
        ("project/123456/locations/us-central1/datasets/987654", False),
        ("project//locations//datasets/987654", False),
        ("locations/europe-west4/datasets/987654", False),
        ("987654", False),
    ],
)
def test_extract_fields_from_resource_name(resource_name: str, expected: bool):
    # Given a resource name and expected validity, test extract_fields_from_resource_name()
    assert expected == bool(extract_fields_from_resource_name(resource_name))


@pytest.fixture
def generated_resource_fields():
    generated_fields = Fields(
        project=str(uuid4()),
        location=str(uuid4()),
        resource="".join(choice(ascii_letters) for i in range(10)),  # 10 random letters
        id=str(randint(0, 100000)),
    )

    yield generated_fields


@pytest.fixture
def generated_resource_name(generated_resource_fields: Fields):
    name = (
        f"projects/{generated_resource_fields.project}/"
        f"locations/{generated_resource_fields.location}"
        f"/{generated_resource_fields.resource}/{generated_resource_fields.id}"
    )

    yield name


def test_extract_fields_from_resource_name_with_extracted_fields(
    generated_resource_name: str, generated_resource_fields: Fields
):
    """Verify fields extracted from resource name match the original fields"""

    assert (
        extract_fields_from_resource_name(resource_name=generated_resource_name)
        == generated_resource_fields
    )


@pytest.mark.parametrize(
    "resource_name, resource_noun, expected",
    [
        # Expects pattern "projects/.../locations/.../datasets/..."
        ("projects/123456/locations/us-central1/datasets/987654", "datasets", True),
        # Expects pattern "projects/.../locations/.../batchPredictionJobs/..."
        (
            "projects/857392/locations/us-central1/trainingPipelines/347292",
            "batchPredictionJobs",
            False,
        ),
    ],
)
def test_extract_fields_from_resource_name_with_resource_noun(
    resource_name: str, resource_noun: str, expected: bool
):
    assert (
        bool(
            extract_fields_from_resource_name(
                resource_name=resource_name, resource_noun=resource_noun
            )
        )
        == expected
    )


def test_invalid_region_raises_with_invalid_region():
    with pytest.raises(ValueError):
        aiplatform.utils.validate_region(region="us-west4")


def test_invalid_region_does_not_raise_with_valid_region():
    aiplatform.utils.validate_region(region="us-central1")


@pytest.mark.parametrize(
    "resource_noun, project, location, full_name",
    [
        (
            "datasets",
            "123456",
            "us-central1",
            "projects/123456/locations/us-central1/datasets/987654",
        ),
        (
            "trainingPipelines",
            "857392",
            "us-west20",
            "projects/857392/locations/us-central1/trainingPipelines/347292",
        ),
    ],
)
def test_full_resource_name_with_full_name(
    resource_noun: str, project: str, location: str, full_name: str,
):
    # should ignore issues with other arguments as resource_name is full_name
    assert (
        aiplatform.utils.full_resource_name(
            resource_name=full_name,
            resource_noun=resource_noun,
            project=project,
            location=location,
        )
        == full_name
    )


@pytest.mark.parametrize(
    "partial_name, resource_noun, project, location, full_name",
    [
        (
            "987654",
            "datasets",
            "123456",
            "us-central1",
            "projects/123456/locations/us-central1/datasets/987654",
        ),
        (
            "347292",
            "trainingPipelines",
            "857392",
            "us-central1",
            "projects/857392/locations/us-central1/trainingPipelines/347292",
        ),
    ],
)
def test_full_resource_name_with_partial_name(
    partial_name: str, resource_noun: str, project: str, location: str, full_name: str,
):
    assert (
        aiplatform.utils.full_resource_name(
            resource_name=partial_name,
            resource_noun=resource_noun,
            project=project,
            location=location,
        )
        == full_name
    )


@pytest.mark.parametrize(
    "partial_name, resource_noun, project, location",
    [("347292", "trainingPipelines", "857392", "us-west2020")],
)
def test_full_resource_name_raises_value_error(
    partial_name: str, resource_noun: str, project: str, location: str,
):
    with pytest.raises(ValueError):
        aiplatform.utils.full_resource_name(
            resource_name=partial_name,
            resource_noun=resource_noun,
            project=project,
            location=location,
        )


def test_validate_display_name_raises_length():
    with pytest.raises(ValueError):
        aiplatform.utils.validate_display_name(
            "slanflksdnlikh;likhq290u90rflkasndfkljashndfkl;jhowq2342;iehoiwerhowqihjer34564356o;iqwjr;oijsdalfjasl;kfjas;ldifhja;slkdfsdlkfhj"
        )


def test_validate_display_name():
    aiplatform.utils.validate_display_name("my_model_abc")
