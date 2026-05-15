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
import json
import os
import tempfile
from unittest import mock
import google.auth.credentials
from agentplatform import _genai as genai
from agentplatform._genai import client as agentplatform_client
from google.genai import types as genai_types
import pytest
import asyncio
import time


@pytest.fixture
def skills_client():
    creds = mock.create_autospec(google.auth.credentials.Credentials, instance=True)
    creds.token = "test_token"
    client = agentplatform_client.Client(
        project="test-project", location="test-location", credentials=creds
    )
    return client.skills


@pytest.fixture
def async_skills_client():
    creds = mock.create_autospec(google.auth.credentials.Credentials, instance=True)
    creds.token = "test_token"
    client = agentplatform_client.Client(
        project="test-project", location="test-location", credentials=creds
    )
    return client.aio.skills


class TestGenaiSkills:

    mock_get_skill_response = {
        "name": "projects/test-project/locations/test-location/skills/test-skill",
        "displayName": "My Test Skill",
    }

    def test_get_skill(self, skills_client):
        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(self.mock_get_skill_response)
            )
            skill_name = (
                "projects/test-project/locations/test-location/skills/test-skill"
            )
            skill = skills_client.get(name=skill_name)
            request_mock.assert_called_once_with(
                "get",
                skill_name,
                {"_url": {"name": skill_name}},
                None,
            )
            assert isinstance(skill, genai.types.Skill)
            assert skill.name == skill_name
            assert skill.display_name == "My Test Skill"

    def test_retrieve_skills_response(self, skills_client):
        mock_retrieve_response = {
            "retrievedSkills": [
                {
                    "skillName": (
                        "projects/test-project/locations/test-location/skills/skill-1"
                    ),
                    "description": "Skill 1 Description",
                },
                {
                    "skillName": (
                        "projects/test-project/locations/test-location/skills/skill-2"
                    ),
                    "description": "Skill 2 Description",
                },
            ]
        }

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(mock_retrieve_response)
            )

            response = skills_client.retrieve(query="test query", config={"top_k": 5})

            assert isinstance(response, genai.types.RetrieveSkillsResponse)
            assert len(response.retrieved_skills) == 2
            assert response.retrieved_skills[0].skill_name == (
                "projects/test-project/locations/test-location/skills/skill-1"
            )
            assert response.retrieved_skills[0].description == "Skill 1 Description"

    def test_retrieve_skills_request_params(self, skills_client):
        mock_retrieve_response = {"retrievedSkills": []}

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(mock_retrieve_response)
            )

            skills_client.retrieve(query="test query", config={"top_k": 5})

            request_mock.assert_called_once_with(
                "get",
                "skills:retrieve?query=test+query&topK=5",
                {"_query": {"query": "test query", "topK": 5}},
                None,
            )

    @pytest.mark.asyncio
    async def test_retrieve_skills_async(self, async_skills_client):
        mock_retrieve_response = {
            "retrievedSkills": [
                {
                    "skillName": (
                        "projects/test-project/locations/test-location/skills/skill-1"
                    ),
                    "description": "Skill 1 Description",
                }
            ]
        }

        with mock.patch.object(
            async_skills_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(mock_retrieve_response)
            )

            response = await async_skills_client.retrieve(
                query="test query", config={"top_k": 1}
            )

            assert isinstance(response, genai.types.RetrieveSkillsResponse)
            assert len(response.retrieved_skills) == 1
            assert response.retrieved_skills[0].skill_name == (
                "projects/test-project/locations/test-location/skills/skill-1"
            )

            request_mock.assert_called_once_with(
                "get",
                "skills:retrieve?query=test+query&topK=1",
                {"_query": {"query": "test query", "topK": 1}},
                None,
            )

    def test_create_skill(self, skills_client):
        """Tests the create_skill method with wait_for_completion=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy file in tmpdir
            with open(os.path.join(tmpdir, "SKILL.md"), "w") as f:
                f.write("# Test Skill")

            # Prepare mock responses
            pending_op = {
                "name": (
                    "projects/test-project/locations/test-location/skills/test-skill/operations/op-123"
                ),
                "done": False,
            }
            finished_op = {
                "name": (
                    "projects/test-project/locations/test-location/skills/test-skill/operations/op-123"
                ),
                "done": True,
                "response": {
                    "name": (
                        "projects/test-project/locations/test-location/skills/test-skill"
                    ),
                    "displayName": "My Test Skill",
                    "description": "My Test Skill Description",
                },
            }

            # Final Skill response returned by get call
            skill_response = {
                "name": (
                    "projects/test-project/locations/test-location/skills/test-skill"
                ),
                "displayName": "My Test Skill",
                "description": "My Test Skill Description",
            }

            with mock.patch.object(
                skills_client._api_client, "request", autospec=True
            ) as request_mock:
                request_mock.side_effect = [
                    genai_types.HttpResponse(body=json.dumps(pending_op)),
                    genai_types.HttpResponse(body=json.dumps(finished_op)),
                    genai_types.HttpResponse(body=json.dumps(skill_response)),
                ]

                # We mock time.sleep to speed up the test
                with mock.patch.object(time, "sleep", return_value=None):
                    skill = skills_client.create(
                        display_name="My Test Skill",
                        description="My Test Skill Description",
                        config={"local_path": tmpdir, "wait_for_completion": True},
                    )

                # Verify requests using robust assert_has_calls matching
                # mock.ANY for base64 zipped Filesystem
                request_mock.assert_has_calls(
                    [
                        mock.call(
                            "post",
                            "skills",
                            {
                                "displayName": "My Test Skill",
                                "description": "My Test Skill Description",
                                "zippedFilesystem": mock.ANY,
                            },
                            None,
                        ),
                        mock.call(
                            "get",
                            "projects/test-project/locations/test-location/skills/test-skill/operations/op-123",
                            {
                                "_url": {
                                    "operationName": "projects/test-project/locations/test-location/skills/test-skill/operations/op-123"
                                }
                            },
                            None,
                        ),
                        mock.call(
                            "get",
                            "projects/test-project/locations/test-location/skills/test-skill",
                            {
                                "_url": {
                                    "name": "projects/test-project/locations/test-location/skills/test-skill"
                                }
                            },
                            None,
                        ),
                    ]
                )

                # Verify returned skill
                assert isinstance(skill, genai.types.Skill)
                assert (
                    skill.name
                    == "projects/test-project/locations/test-location/skills/test-skill"
                )
                assert skill.display_name == "My Test Skill"
                assert skill.description == "My Test Skill Description"

    def test_create_skill_no_wait(self, skills_client):
        """Tests the create_skill method with wait_for_completion=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "SKILL.md"), "w") as f:
                f.write("# Test Skill")

            pending_op = {
                "name": (
                    "projects/test-project/locations/test-location/skills/test-skill/operations/op-123"
                ),
                "done": False,
            }

            with mock.patch.object(
                skills_client._api_client, "request", autospec=True
            ) as request_mock:
                request_mock.return_value = genai_types.HttpResponse(
                    body=json.dumps(pending_op)
                )

                operation = skills_client.create(
                    display_name="My Test Skill",
                    description="My Test Skill Description",
                    config={"local_path": tmpdir, "wait_for_completion": False},
                )

                # Assertions
                assert request_mock.call_count == 1
                assert isinstance(operation, genai.types.SkillOperation)
                assert (
                    operation.name
                    == "projects/test-project/locations/test-location/skills/test-skill/operations/op-123"
                )
                assert not operation.done

    @pytest.mark.asyncio
    async def test_create_skill_async(self, async_skills_client):
        """Tests the create_skill method asynchronously with wait_for_completion=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "SKILL.md"), "w") as f:
                f.write("# Test Skill")

            pending_op = {
                "name": (
                    "projects/test-project/locations/test-location/skills/test-skill/operations/op-123"
                ),
                "done": False,
            }
            finished_op = {
                "name": (
                    "projects/test-project/locations/test-location/skills/test-skill/operations/op-123"
                ),
                "done": True,
                "response": {
                    "name": (
                        "projects/test-project/locations/test-location/skills/test-skill"
                    ),
                    "displayName": "My Test Skill",
                    "description": "My Test Skill Description",
                },
            }

            # Final Skill response returned by async get call
            skill_response = {
                "name": (
                    "projects/test-project/locations/test-location/skills/test-skill"
                ),
                "displayName": "My Test Skill",
                "description": "My Test Skill Description",
            }

            with mock.patch.object(
                async_skills_client._api_client, "async_request", autospec=True
            ) as request_mock:
                request_mock.side_effect = [
                    genai_types.HttpResponse(body=json.dumps(pending_op)),
                    genai_types.HttpResponse(body=json.dumps(finished_op)),
                    genai_types.HttpResponse(body=json.dumps(skill_response)),
                ]

                with mock.patch.object(asyncio, "sleep", new_callable=mock.AsyncMock):
                    skill = await async_skills_client.create(
                        display_name="My Test Skill",
                        description="My Test Skill Description",
                        config={"local_path": tmpdir, "wait_for_completion": True},
                    )

                # Verify requests using robust assert_has_calls
                request_mock.assert_has_calls(
                    [
                        mock.call(
                            "post",
                            "skills",
                            {
                                "displayName": "My Test Skill",
                                "description": "My Test Skill Description",
                                "zippedFilesystem": mock.ANY,
                            },
                            None,
                        ),
                        mock.call(
                            "get",
                            "projects/test-project/locations/test-location/skills/test-skill/operations/op-123",
                            {
                                "_url": {
                                    "operationName": "projects/test-project/locations/test-location/skills/test-skill/operations/op-123"
                                }
                            },
                            None,
                        ),
                        mock.call(
                            "get",
                            "projects/test-project/locations/test-location/skills/test-skill",
                            {
                                "_url": {
                                    "name": "projects/test-project/locations/test-location/skills/test-skill"
                                }
                            },
                            None,
                        ),
                    ]
                )

                # Verify returned skill
                assert isinstance(skill, genai.types.Skill)
                assert (
                    skill.name
                    == "projects/test-project/locations/test-location/skills/test-skill"
                )
                assert skill.display_name == "My Test Skill"
                assert skill.description == "My Test Skill Description"

    def test_update_skill(self, skills_client):
        """Tests the update method with wait_for_completion=True (default)."""
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        # Prepare mock responses
        pending_op = {
            "name": (
                "projects/test-project/locations/test-location/skills/test-skill/operations/op-456"
            ),
            "done": False,
        }
        finished_op = {
            "name": (
                "projects/test-project/locations/test-location/skills/test-skill/operations/op-456"
            ),
            "done": True,
            "response": {
                "name": skill_name,
                "displayName": "Updated Skill",
                "description": "Updated Description",
            },
        }
        skill_response = {
            "name": skill_name,
            "displayName": "Updated Skill",
            "description": "Updated Description",
        }

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(pending_op)),
                genai_types.HttpResponse(body=json.dumps(finished_op)),
                genai_types.HttpResponse(body=json.dumps(skill_response)),
            ]

            with mock.patch.object(time, "sleep", return_value=None):
                skill = skills_client.update(
                    name=skill_name,
                    config={
                        "display_name": "Updated Skill",
                        "description": "Updated Description",
                    },
                )

            # Verify requests using robust assert_has_calls
            request_mock.assert_has_calls(
                [
                    mock.call(
                        "patch",
                        f"{skill_name}?updateMask=displayName%2Cdescription",
                        {
                            "_url": {
                                "name": "projects/test-project/locations/test-location/skills/test-skill"
                            },
                            "displayName": "Updated Skill",
                            "description": "Updated Description",
                            "_query": {
                                "updateMask": "displayName,description",
                            },
                        },
                        None,
                    ),
                    mock.call(
                        "get",
                        "projects/test-project/locations/test-location/skills/test-skill/operations/op-456",
                        {
                            "_url": {
                                "operationName": "projects/test-project/locations/test-location/skills/test-skill/operations/op-456"
                            }
                        },
                        None,
                    ),
                    mock.call(
                        "get",
                        skill_name,
                        {
                            "_url": {
                                "name": "projects/test-project/locations/test-location/skills/test-skill"
                            }
                        },
                        None,
                    ),
                ]
            )

            # Verify returned skill
            assert isinstance(skill, genai.types.Skill)
            assert skill.name == skill_name
            assert skill.display_name == "Updated Skill"
            assert skill.description == "Updated Description"

    def test_update_skill_no_wait(self, skills_client):
        """Tests the update method with wait_for_completion=False."""
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        pending_op = {
            "name": (
                "projects/test-project/locations/test-location/skills/test-skill/operations/op-456"
            ),
            "done": False,
        }

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(pending_op)
            )

            operation = skills_client.update(
                name=skill_name,
                config={
                    "display_name": "Updated Skill",
                    "wait_for_completion": False,
                },
            )

            # Assertions
            assert isinstance(operation, genai.types.SkillOperation)
            assert (
                operation.name
                == "projects/test-project/locations/test-location/skills/test-skill/operations/op-456"
            )
            assert not operation.done

            request_mock.assert_called_once_with(
                "patch",
                f"{skill_name}?updateMask=displayName",
                {
                    "_url": {
                        "name": (
                            "projects/test-project/locations/test-location/skills/test-skill"
                        )
                    },
                    "displayName": "Updated Skill",
                    "_query": {
                        "updateMask": "displayName",
                    },
                },
                None,
            )

    @pytest.mark.asyncio
    async def test_update_skill_async(self, async_skills_client):
        """Tests the async update method with wait_for_completion=True."""
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        pending_op = {
            "name": (
                "projects/test-project/locations/test-location/skills/test-skill/operations/op-456"
            ),
            "done": False,
        }
        finished_op = {
            "name": (
                "projects/test-project/locations/test-location/skills/test-skill/operations/op-456"
            ),
            "done": True,
            "response": {
                "name": skill_name,
                "displayName": "Updated Skill",
            },
        }
        skill_response = {
            "name": skill_name,
            "displayName": "Updated Skill",
        }

        with mock.patch.object(
            async_skills_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(pending_op)),
                genai_types.HttpResponse(body=json.dumps(finished_op)),
                genai_types.HttpResponse(body=json.dumps(skill_response)),
            ]

            with mock.patch.object(asyncio, "sleep", new_callable=mock.AsyncMock):
                skill = await async_skills_client.update(
                    name=skill_name,
                    config={
                        "display_name": "Updated Skill",
                        "wait_for_completion": True,
                    },
                )

            # Verify requests using robust assert_has_calls
            request_mock.assert_has_calls(
                [
                    mock.call(
                        "patch",
                        f"{skill_name}?updateMask=displayName",
                        {
                            "_url": {
                                "name": "projects/test-project/locations/test-location/skills/test-skill"
                            },
                            "displayName": "Updated Skill",
                            "_query": {
                                "updateMask": "displayName",
                            },
                        },
                        None,
                    ),
                    mock.call(
                        "get",
                        "projects/test-project/locations/test-location/skills/test-skill/operations/op-456",
                        {
                            "_url": {
                                "operationName": "projects/test-project/locations/test-location/skills/test-skill/operations/op-456"
                            }
                        },
                        None,
                    ),
                    mock.call(
                        "get",
                        skill_name,
                        {
                            "_url": {
                                "name": "projects/test-project/locations/test-location/skills/test-skill"
                            }
                        },
                        None,
                    ),
                ]
            )

            # Verify returned skill
            assert isinstance(skill, genai.types.Skill)
            assert skill.name == skill_name
            assert skill.display_name == "Updated Skill"

    def test_update_skill_invalid_args(self, skills_client):
        """Verifies ValueError is raised when no update fields are provided."""
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        with pytest.raises(
            ValueError,
            match=(
                "At least one of `display_name`, `description`, `local_path`, or"
                " `zipped_filesystem` must be provided for update in config."
            ),
        ):
            skills_client.update(name=skill_name)

    def test_update_skill_mutually_exclusive_args(self, skills_client):
        """Verifies ValueError is raised when both local_path and zipped_filesystem are provided."""
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        with pytest.raises(
            ValueError,
            match="Only one of `local_path` or `zipped_filesystem` can be provided",
        ):
            skills_client.update(
                name=skill_name,
                config={
                    "local_path": "/some/path",
                    "zipped_filesystem": b"zipped_bytes",
                },
            )

    def test_list_skills(self, skills_client):
        """Tests the list method using the standard Pager."""
        mock_list_response = {
            "skills": [
                {
                    "name": (
                        "projects/test-project/locations/test-location/skills/skill-1"
                    ),
                    "displayName": "Skill 1",
                },
                {
                    "name": (
                        "projects/test-project/locations/test-location/skills/skill-2"
                    ),
                    "displayName": "Skill 2",
                },
            ],
            "nextPageToken": "token-123",
        }
        mock_list_response_page_2 = {
            "skills": [
                {
                    "name": (
                        "projects/test-project/locations/test-location/skills/skill-3"
                    ),
                    "displayName": "Skill 3",
                },
            ],
        }

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(mock_list_response)),
                genai_types.HttpResponse(body=json.dumps(mock_list_response_page_2)),
            ]

            skills = list(skills_client.list())

            # Verify Pager correct retrieval across pages
            assert len(skills) == 3
            assert skills[0].display_name == "Skill 1"
            assert skills[1].display_name == "Skill 2"
            assert skills[2].display_name == "Skill 3"

            # Verify requests using robust assert_has_calls
            request_mock.assert_has_calls(
                [
                    mock.call(
                        "get",
                        "skills",
                        {},
                        None,
                    ),
                    mock.call(
                        "get",
                        "skills?pageToken=token-123",
                        {"_query": {"pageToken": "token-123"}},
                        None,
                    ),
                ]
            )

    @pytest.mark.asyncio
    async def test_list_skills_async(self, async_skills_client):
        """Tests the async list method returning AsyncPager."""
        mock_list_response = {
            "skills": [
                {
                    "name": (
                        "projects/test-project/locations/test-location/skills/skill-1"
                    ),
                    "displayName": "Skill 1",
                },
            ],
        }

        with mock.patch.object(
            async_skills_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(mock_list_response)
            )

            skills = []
            pager = await async_skills_client.list()
            async for skill in pager:
                skills.append(skill)

            assert len(skills) == 1
            assert skills[0].display_name == "Skill 1"
            request_mock.assert_called_once_with(
                "get",
                "skills",
                {},
                None,
            )

    def test_delete_skill(self, skills_client):
        """Tests the delete method with wait_for_completion=True (default)."""
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        pending_op = {
            "name": (
                "projects/test-project/locations/test-location/skills/test-skill/operations/op-789"
            ),
            "done": False,
        }
        finished_op = {
            "name": (
                "projects/test-project/locations/test-location/skills/test-skill/operations/op-789"
            ),
            "done": True,
            "response": {},
        }

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(pending_op)),
                genai_types.HttpResponse(body=json.dumps(finished_op)),
            ]

            with mock.patch("time.sleep", return_value=None):
                result = skills_client.delete(name=skill_name)

            assert result is None

            # Verify both DELETE and LRO GET requests using robust assert_has_calls
            request_mock.assert_has_calls(
                [
                    mock.call(
                        "delete",
                        skill_name,
                        {"_url": {"name": skill_name}},
                        None,
                    ),
                    mock.call(
                        "get",
                        "projects/test-project/locations/test-location/skills/test-skill/operations/op-789",
                        {
                            "_url": {
                                "operationName": (
                                    "projects/test-project/locations/test-location/skills/test-skill/operations/op-789"
                                )
                            }
                        },
                        None,
                    ),
                ]
            )

    def test_delete_skill_no_wait(self, skills_client):
        """Tests the delete method with wait_for_completion=False."""
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        pending_op = {
            "name": (
                "projects/test-project/locations/test-location/skills/test-skill/operations/op-789"
            ),
            "done": False,
        }

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(pending_op)
            )

            operation = skills_client.delete(
                name=skill_name, config={"wait_for_completion": False}
            )

            assert isinstance(operation, genai.types.DeleteSkillOperation)
            assert (
                operation.name
                == "projects/test-project/locations/test-location/skills/test-skill/operations/op-789"
            )
            assert not operation.done
            request_mock.assert_called_once_with(
                "delete",
                skill_name,
                {"_url": {"name": skill_name}},
                None,
            )

    @pytest.mark.asyncio
    async def test_delete_skill_async(self, async_skills_client):
        """Tests the async delete method with wait_for_completion=True."""
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        pending_op = {
            "name": (
                "projects/test-project/locations/test-location/skills/test-skill/operations/op-789"
            ),
            "done": False,
        }
        finished_op = {
            "name": (
                "projects/test-project/locations/test-location/skills/test-skill/operations/op-789"
            ),
            "done": True,
            "response": {},
        }

        with mock.patch.object(
            async_skills_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(pending_op)),
                genai_types.HttpResponse(body=json.dumps(finished_op)),
            ]

            with mock.patch("asyncio.sleep", new_callable=mock.AsyncMock):
                result = await async_skills_client.delete(
                    name=skill_name, config={"wait_for_completion": True}
                )

            assert result is None

            # Verify both DELETE and LRO GET requests asynchronously using robust assert_has_calls
            request_mock.assert_has_calls(
                [
                    mock.call(
                        "delete",
                        skill_name,
                        {"_url": {"name": skill_name}},
                        None,
                    ),
                    mock.call(
                        "get",
                        "projects/test-project/locations/test-location/skills/test-skill/operations/op-789",
                        {
                            "_url": {
                                "operationName": (
                                    "projects/test-project/locations/test-location/skills/test-skill/operations/op-789"
                                )
                            }
                        },
                        None,
                    ),
                ]
            )

    def test_get_skill_revision(self, skills_client):
        revision_name = "projects/test-project/locations/test-location/skills/test-skill/revisions/rev-1"
        mock_response = {
            "name": revision_name,
            "state": "ACTIVE",
        }

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(mock_response)
            )

            revision = skills_client.revisions.get(name=revision_name)

            assert isinstance(revision, genai.types.SkillRevision)
            assert revision.name == revision_name
            assert revision.state == "ACTIVE"

            request_mock.assert_called_once_with(
                "get",
                revision_name,
                {"_url": {"name": revision_name}},
                None,
            )

    @pytest.mark.asyncio
    async def test_get_skill_revision_async(self, async_skills_client):
        revision_name = "projects/test-project/locations/test-location/skills/test-skill/revisions/rev-1"
        mock_response = {
            "name": revision_name,
            "state": "ACTIVE",
        }

        with mock.patch.object(
            async_skills_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(mock_response)
            )

            revision = await async_skills_client.revisions.get(name=revision_name)

            assert isinstance(revision, genai.types.SkillRevision)
            assert revision.name == revision_name
            assert revision.state == "ACTIVE"

            request_mock.assert_called_once_with(
                "get",
                revision_name,
                {"_url": {"name": revision_name}},
                None,
            )

    def test_list_skill_revisions(self, skills_client):
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        mock_response = {
            "skillRevisions": [
                {
                    "name": f"{skill_name}/revisions/rev-1",
                    "state": "ACTIVE",
                }
            ]
        }

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(mock_response)
            )

            pager = skills_client.revisions.list(name=skill_name)

            from google.genai import pagers

            assert isinstance(pager, pagers.Pager)

            revisions = list(pager)
            assert len(revisions) == 1
            assert revisions[0].name == f"{skill_name}/revisions/rev-1"

            request_mock.assert_called_once_with(
                "get",
                f"{skill_name}/revisions",
                {"_url": {"name": skill_name}},
                None,
            )

    @pytest.mark.asyncio
    async def test_list_skill_revisions_async(self, async_skills_client):
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        mock_response = {
            "skillRevisions": [
                {
                    "name": f"{skill_name}/revisions/rev-1",
                    "state": "ACTIVE",
                }
            ]
        }

        with mock.patch.object(
            async_skills_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(mock_response)
            )

            pager = await async_skills_client.revisions.list(name=skill_name)

            from google.genai import pagers

            assert isinstance(pager, pagers.AsyncPager)

            revisions = []
            async for revision in pager:
                revisions.append(revision)

            assert len(revisions) == 1
            assert revisions[0].name == f"{skill_name}/revisions/rev-1"

            request_mock.assert_called_once_with(
                "get",
                f"{skill_name}/revisions",
                {"_url": {"name": skill_name}},
                None,
            )

    def test_list_skills_with_max_results(self, skills_client):
        mock_list_response = {
            "skills": [
                {
                    "name": "projects/test-project/locations/test-location/skills/skill-1",
                    "displayName": "Skill 1",
                },
                {
                    "name": "projects/test-project/locations/test-location/skills/skill-2",
                    "displayName": "Skill 2",
                },
            ],
            "nextPageToken": "token-123",
        }
        mock_list_response_page_2 = {
            "skills": [
                {
                    "name": "projects/test-project/locations/test-location/skills/skill-3",
                    "displayName": "Skill 3",
                },
                {
                    "name": "projects/test-project/locations/test-location/skills/skill-4",
                    "displayName": "Skill 4",
                },
            ],
            "nextPageToken": "token-456",
        }

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(mock_list_response)),
                genai_types.HttpResponse(body=json.dumps(mock_list_response_page_2)),
            ]

            pager = skills_client.list(config={"max_results": 3})
            skills = list(pager)

            assert len(skills) == 3
            assert skills[0].display_name == "Skill 1"
            assert skills[1].display_name == "Skill 2"
            assert skills[2].display_name == "Skill 3"

            assert request_mock.call_count == 2
            request_mock.assert_has_calls(
                [
                    mock.call("get", "skills", {}, None),
                    mock.call(
                        "get",
                        "skills?pageToken=token-123",
                        {"_query": {"pageToken": "token-123"}},
                        None,
                    ),
                ]
            )

    @pytest.mark.asyncio
    async def test_list_skills_with_max_results_async(self, async_skills_client):
        mock_list_response = {
            "skills": [
                {
                    "name": "projects/test-project/locations/test-location/skills/skill-1",
                    "displayName": "Skill 1",
                },
                {
                    "name": "projects/test-project/locations/test-location/skills/skill-2",
                    "displayName": "Skill 2",
                },
            ],
            "nextPageToken": "token-123",
        }
        mock_list_response_page_2 = {
            "skills": [
                {
                    "name": "projects/test-project/locations/test-location/skills/skill-3",
                    "displayName": "Skill 3",
                },
                {
                    "name": "projects/test-project/locations/test-location/skills/skill-4",
                    "displayName": "Skill 4",
                },
            ],
            "nextPageToken": "token-456",
        }

        with mock.patch.object(
            async_skills_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(mock_list_response)),
                genai_types.HttpResponse(body=json.dumps(mock_list_response_page_2)),
            ]

            pager = await async_skills_client.list(config={"max_results": 3})
            skills = []
            async for skill in pager:
                skills.append(skill)

            assert len(skills) == 3
            assert skills[0].display_name == "Skill 1"
            assert skills[1].display_name == "Skill 2"
            assert skills[2].display_name == "Skill 3"

            assert request_mock.call_count == 2
            request_mock.assert_has_calls(
                [
                    mock.call("get", "skills", {}, None),
                    mock.call(
                        "get",
                        "skills?pageToken=token-123",
                        {"_query": {"pageToken": "token-123"}},
                        None,
                    ),
                ]
            )

    def test_list_skill_revisions_with_max_results(self, skills_client):
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        mock_response = {
            "skillRevisions": [
                {"name": f"{skill_name}/revisions/rev-1", "state": "ACTIVE"},
                {"name": f"{skill_name}/revisions/rev-2", "state": "ACTIVE"},
            ],
            "nextPageToken": "token-123",
        }
        mock_response_page_2 = {
            "skillRevisions": [
                {"name": f"{skill_name}/revisions/rev-3", "state": "ACTIVE"},
            ],
        }

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(mock_response)),
                genai_types.HttpResponse(body=json.dumps(mock_response_page_2)),
            ]

            pager = skills_client.revisions.list(
                name=skill_name, config={"max_results": 2}
            )
            revisions = list(pager)

            assert len(revisions) == 2
            assert revisions[0].name == f"{skill_name}/revisions/rev-1"
            assert revisions[1].name == f"{skill_name}/revisions/rev-2"

            assert request_mock.call_count == 1
            request_mock.assert_called_once_with(
                "get",
                f"{skill_name}/revisions",
                {"_url": {"name": skill_name}},
                None,
            )

    @pytest.mark.asyncio
    async def test_list_skill_revisions_with_max_results_async(
        self, async_skills_client
    ):
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        mock_response = {
            "skillRevisions": [
                {"name": f"{skill_name}/revisions/rev-1", "state": "ACTIVE"},
                {"name": f"{skill_name}/revisions/rev-2", "state": "ACTIVE"},
            ],
            "nextPageToken": "token-123",
        }
        mock_response_page_2 = {
            "skillRevisions": [
                {"name": f"{skill_name}/revisions/rev-3", "state": "ACTIVE"},
            ],
        }

        with mock.patch.object(
            async_skills_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(mock_response)),
                genai_types.HttpResponse(body=json.dumps(mock_response_page_2)),
            ]

            pager = await async_skills_client.revisions.list(
                name=skill_name, config={"max_results": 2}
            )
            revisions = []
            async for revision in pager:
                revisions.append(revision)

            assert len(revisions) == 2
            assert revisions[0].name == f"{skill_name}/revisions/rev-1"
            assert revisions[1].name == f"{skill_name}/revisions/rev-2"

            assert request_mock.call_count == 1
            request_mock.assert_called_once_with(
                "get",
                f"{skill_name}/revisions",
                {"_url": {"name": skill_name}},
                None,
            )

    def test_pager_invalid_max_results(self, skills_client):
        import pydantic

        mock_list_response = {"skills": []}
        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(mock_list_response)
            )

            with pytest.raises(ValueError, match="max_results must be greater than 0"):
                list(skills_client.list(config={"max_results": 0}))

            with pytest.raises(ValueError, match="max_results must be greater than 0"):
                list(skills_client.list(config={"max_results": -1}))

            with pytest.raises(pydantic.ValidationError):
                list(skills_client.list(config={"max_results": "invalid"}))

    def test_list_skills_default_limit(self, skills_client):
        # 50 pages of size 2 = 100 items (reaches default limit)
        responses = []
        for i in range(50):
            responses.append(genai_types.HttpResponse(body=json.dumps({
                "skills": [
                    {"name": f"projects/test-project/locations/test-location/skills/skill-{i*2+1}", "displayName": f"Skill {i*2+1}"},
                    {"name": f"projects/test-project/locations/test-location/skills/skill-{i*2+2}", "displayName": f"Skill {i*2+2}"},
                ],
                "nextPageToken": f"token-{i+1}"
            })))
        # 51st page (should NOT be fetched)
        responses.append(genai_types.HttpResponse(body=json.dumps({
            "skills": [
                {"name": "projects/test-project/locations/test-location/skills/skill-101", "displayName": "Skill 101"},
            ]
        })))

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = responses

            # No max_results specified, should default to 100
            pager = skills_client.list()
            skills = list(pager)

            assert len(skills) == 100
            assert skills[0].display_name == "Skill 1"
            assert skills[99].display_name == "Skill 100"

            # Should have called request 50 times (fetching 100 items)
            assert request_mock.call_count == 50
            # Ensure the last call was with the 49th token
            request_mock.assert_has_calls(
                [
                    mock.call("get", "skills", {}, None),
                ] + [
                    mock.call(
                        "get",
                        f"skills?pageToken=token-{i}",
                        {"_query": {"pageToken": f"token-{i}"}},
                        None,
                    ) for i in range(1, 50)
                ]
            )

    def test_list_skill_revisions_default_limit(self, skills_client):
        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        # 50 pages of size 2 = 100 items
        responses = []
        for i in range(50):
            responses.append(genai_types.HttpResponse(body=json.dumps({
                "skillRevisions": [
                    {"name": f"{skill_name}/revisions/rev-{i*2+1}", "state": "ACTIVE"},
                    {"name": f"{skill_name}/revisions/rev-{i*2+2}", "state": "ACTIVE"},
                ],
                "nextPageToken": f"token-{i+1}"
            })))
        # 51st page (should NOT be fetched)
        responses.append(genai_types.HttpResponse(body=json.dumps({
            "skillRevisions": [
                {"name": f"{skill_name}/revisions/rev-101", "state": "ACTIVE"},
            ]
        })))

        with mock.patch.object(
            skills_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = responses

            pager = skills_client.revisions.list(name=skill_name)
            revisions = list(pager)

            assert len(revisions) == 100
            assert revisions[0].name == f"{skill_name}/revisions/rev-1"
            assert revisions[99].name == f"{skill_name}/revisions/rev-100"

            assert request_mock.call_count == 50

    @pytest.mark.asyncio
    async def test_list_skills_default_limit_async(self, async_skills_client):
        # 50 pages of size 2 = 100 items
        responses = []
        for i in range(50):
            responses.append(genai_types.HttpResponse(body=json.dumps({
                "skills": [
                    {"name": f"projects/test-project/locations/test-location/skills/skill-{i*2+1}", "displayName": f"Skill {i*2+1}"},
                    {"name": f"projects/test-project/locations/test-location/skills/skill-{i*2+2}", "displayName": f"Skill {i*2+2}"},
                ],
                "nextPageToken": f"token-{i+1}"
            })))
        # 51st page (should NOT be fetched)
        responses.append(genai_types.HttpResponse(body=json.dumps({
            "skills": [
                {"name": "projects/test-project/locations/test-location/skills/skill-101", "displayName": "Skill 101"},
            ]
        })))

        with mock.patch.object(
            async_skills_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.side_effect = responses

            pager = await async_skills_client.list()
            skills = []
            async for skill in pager:
                skills.append(skill)

            assert len(skills) == 100
            assert skills[0].display_name == "Skill 1"
            assert skills[99].display_name == "Skill 100"

            assert request_mock.call_count == 50
