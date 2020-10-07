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
from importlib import reload
from string import ascii_letters

from google.cloud import aiplatform as aip
from google.cloud.aiplatform.utils import Fields
from google.cloud.aiplatform.utils import validate_name
from google.cloud.aiplatform.utils import get_client_options


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
def test_validate_name(resource_name: str, expected: bool):
    # Given a resource name and expected validity, test validate_name()
    assert expected == bool(validate_name(resource_name))


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


def test_validate_name_with_extracted_fields(
    generated_resource_name: str, generated_resource_fields: Fields
):
    """Verify fields extracted from resource name match the original fields"""

    assert (
        validate_name(resource_name=generated_resource_name)
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
def test_validate_name_with_resource_noun(
    resource_name: str, resource_noun: str, expected: bool
):
    assert (
        bool(validate_name(resource_name=resource_name, resource_noun=resource_noun))
        == expected
    )


@pytest.mark.parametrize(
    "init_location, location_override, prediction, expected_endpoint",
    [
        ("us-central1", None, False, "us-central1-aiplatform.googleapis.com"),
        (
            "us-central1",
            "europe-west4",
            False,
            "europe-west4-aiplatform.googleapis.com",
        ),
        ("asia-east1", None, False, "asia-east1-aiplatform.googleapis.com"),
        ("asia-east1", None, True, "asia-east1-prediction-aiplatform.googleapis.com"),
    ],
)
def test_get_client_options(
    init_location: str, location_override: str, prediction: bool, expected_endpoint: str
):
    reload(aip)  # Reload aiplatform module to reset initializer settings
    aip.init(location=init_location)

    assert get_client_options(
        location_override=location_override, prediction_client=prediction
    ) == {"api_endpoint": expected_endpoint}


def test_get_client_options_with_invalid_region():
    with pytest.raises(ValueError):
        reload(aip)
        aip.init(location="us-west4")
        get_client_options()  # Throws ValueError due to unsupported region
