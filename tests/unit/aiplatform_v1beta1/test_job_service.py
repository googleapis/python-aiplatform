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

from unittest import mock

import grpc
import math
import pytest

from google import auth
from google.api_core import client_options
from google.api_core import future
from google.api_core import operations_v1
from google.auth import credentials
from google.cloud.aiplatform_v1beta1.services.job_service import JobServiceClient
from google.cloud.aiplatform_v1beta1.services.job_service import pagers
from google.cloud.aiplatform_v1beta1.services.job_service import transports
from google.cloud.aiplatform_v1beta1.types import accelerator_type
from google.cloud.aiplatform_v1beta1.types import (
    accelerator_type as gca_accelerator_type,
)
from google.cloud.aiplatform_v1beta1.types import batch_prediction_job
from google.cloud.aiplatform_v1beta1.types import (
    batch_prediction_job as gca_batch_prediction_job,
)
from google.cloud.aiplatform_v1beta1.types import completion_stats
from google.cloud.aiplatform_v1beta1.types import (
    completion_stats as gca_completion_stats,
)
from google.cloud.aiplatform_v1beta1.types import custom_job
from google.cloud.aiplatform_v1beta1.types import custom_job as gca_custom_job
from google.cloud.aiplatform_v1beta1.types import data_labeling_job
from google.cloud.aiplatform_v1beta1.types import (
    data_labeling_job as gca_data_labeling_job,
)
from google.cloud.aiplatform_v1beta1.types import hyperparameter_tuning_job
from google.cloud.aiplatform_v1beta1.types import (
    hyperparameter_tuning_job as gca_hyperparameter_tuning_job,
)
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import job_service
from google.cloud.aiplatform_v1beta1.types import job_state
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import manual_batch_tuning_parameters
from google.cloud.aiplatform_v1beta1.types import (
    manual_batch_tuning_parameters as gca_manual_batch_tuning_parameters,
)
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.cloud.aiplatform_v1beta1.types import study
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import any_pb2 as any  # type: ignore
from google.protobuf import duration_pb2 as duration  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.rpc import status_pb2 as status  # type: ignore
from google.type import money_pb2 as money  # type: ignore


def test_job_service_client_from_service_account_file():
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = JobServiceClient.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = JobServiceClient.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "aiplatform.googleapis.com:443"


def test_job_service_client_client_options():
    # Check the default options have their expected values.
    assert JobServiceClient.DEFAULT_OPTIONS.api_endpoint == "aiplatform.googleapis.com"

    # Check that options can be customized.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.job_service.JobServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = JobServiceClient(client_options=options)
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_job_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.job_service.JobServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = JobServiceClient(client_options={"api_endpoint": "squid.clam.whelk"})
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_create_custom_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.CreateCustomJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_custom_job.CustomJob(
            name="name_value",
            display_name="display_name_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
        )

        response = client.create_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_custom_job.CustomJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_create_custom_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_custom_job.CustomJob()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.create_custom_job(
            parent="parent_value",
            custom_job=gca_custom_job.CustomJob(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].custom_job == gca_custom_job.CustomJob(name="name_value")


def test_create_custom_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_custom_job(
            job_service.CreateCustomJobRequest(),
            parent="parent_value",
            custom_job=gca_custom_job.CustomJob(name="name_value"),
        )


def test_get_custom_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.GetCustomJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_custom_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = custom_job.CustomJob(
            name="name_value",
            display_name="display_name_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
        )

        response = client.get_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, custom_job.CustomJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_get_custom_job_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetCustomJobRequest(name="name/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_custom_job), "__call__") as call:
        call.return_value = custom_job.CustomJob()
        client.get_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_custom_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_custom_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = custom_job.CustomJob()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_custom_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_custom_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_custom_job(
            job_service.GetCustomJobRequest(), name="name_value",
        )


def test_list_custom_jobs(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.ListCustomJobsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_custom_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListCustomJobsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_custom_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListCustomJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_custom_jobs_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListCustomJobsRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_custom_jobs), "__call__"
    ) as call:
        call.return_value = job_service.ListCustomJobsResponse()
        client.list_custom_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_custom_jobs_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_custom_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListCustomJobsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_custom_jobs(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_custom_jobs_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_custom_jobs(
            job_service.ListCustomJobsRequest(), parent="parent_value",
        )


def test_list_custom_jobs_pager():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_custom_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListCustomJobsResponse(custom_jobs=[], next_page_token="def",),
            job_service.ListCustomJobsResponse(
                custom_jobs=[custom_job.CustomJob(),], next_page_token="ghi",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[custom_job.CustomJob(), custom_job.CustomJob(),],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_custom_jobs(request={},)]
        assert len(results) == 6
        assert all(isinstance(i, custom_job.CustomJob) for i in results)


def test_list_custom_jobs_pages():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_custom_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListCustomJobsResponse(custom_jobs=[], next_page_token="def",),
            job_service.ListCustomJobsResponse(
                custom_jobs=[custom_job.CustomJob(),], next_page_token="ghi",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[custom_job.CustomJob(), custom_job.CustomJob(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_custom_jobs(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_delete_custom_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.DeleteCustomJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.delete_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_custom_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.delete_custom_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_custom_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_custom_job(
            job_service.DeleteCustomJobRequest(), name="name_value",
        )


def test_cancel_custom_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.CancelCustomJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.cancel_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.cancel_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_custom_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.cancel_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.cancel_custom_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_cancel_custom_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_custom_job(
            job_service.CancelCustomJobRequest(), name="name_value",
        )


def test_create_data_labeling_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.CreateDataLabelingJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_data_labeling_job.DataLabelingJob(
            name="name_value",
            display_name="display_name_value",
            datasets=["datasets_value"],
            labeler_count=1375,
            instruction_uri="instruction_uri_value",
            inputs_schema_uri="inputs_schema_uri_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            labeling_progress=1810,
            specialist_pools=["specialist_pools_value"],
        )

        response = client.create_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_data_labeling_job.DataLabelingJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.datasets == ["datasets_value"]
    assert response.labeler_count == 1375
    assert response.instruction_uri == "instruction_uri_value"
    assert response.inputs_schema_uri == "inputs_schema_uri_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.labeling_progress == 1810
    assert response.specialist_pools == ["specialist_pools_value"]


def test_create_data_labeling_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_data_labeling_job.DataLabelingJob()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.create_data_labeling_job(
            parent="parent_value",
            data_labeling_job=gca_data_labeling_job.DataLabelingJob(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].data_labeling_job == gca_data_labeling_job.DataLabelingJob(
            name="name_value"
        )


def test_create_data_labeling_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_data_labeling_job(
            job_service.CreateDataLabelingJobRequest(),
            parent="parent_value",
            data_labeling_job=gca_data_labeling_job.DataLabelingJob(name="name_value"),
        )


def test_get_data_labeling_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.GetDataLabelingJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = data_labeling_job.DataLabelingJob(
            name="name_value",
            display_name="display_name_value",
            datasets=["datasets_value"],
            labeler_count=1375,
            instruction_uri="instruction_uri_value",
            inputs_schema_uri="inputs_schema_uri_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            labeling_progress=1810,
            specialist_pools=["specialist_pools_value"],
        )

        response = client.get_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, data_labeling_job.DataLabelingJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.datasets == ["datasets_value"]
    assert response.labeler_count == 1375
    assert response.instruction_uri == "instruction_uri_value"
    assert response.inputs_schema_uri == "inputs_schema_uri_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.labeling_progress == 1810
    assert response.specialist_pools == ["specialist_pools_value"]


def test_get_data_labeling_job_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetDataLabelingJobRequest(name="name/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_data_labeling_job), "__call__"
    ) as call:
        call.return_value = data_labeling_job.DataLabelingJob()
        client.get_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_data_labeling_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = data_labeling_job.DataLabelingJob()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_data_labeling_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_data_labeling_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_data_labeling_job(
            job_service.GetDataLabelingJobRequest(), name="name_value",
        )


def test_list_data_labeling_jobs(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.ListDataLabelingJobsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_data_labeling_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListDataLabelingJobsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_data_labeling_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDataLabelingJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_data_labeling_jobs_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListDataLabelingJobsRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_data_labeling_jobs), "__call__"
    ) as call:
        call.return_value = job_service.ListDataLabelingJobsResponse()
        client.list_data_labeling_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_data_labeling_jobs_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_data_labeling_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListDataLabelingJobsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_data_labeling_jobs(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_data_labeling_jobs_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_data_labeling_jobs(
            job_service.ListDataLabelingJobsRequest(), parent="parent_value",
        )


def test_list_data_labeling_jobs_pager():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_data_labeling_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[], next_page_token="def",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[data_labeling_job.DataLabelingJob(),],
                next_page_token="ghi",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_data_labeling_jobs(request={},)]
        assert len(results) == 6
        assert all(isinstance(i, data_labeling_job.DataLabelingJob) for i in results)


def test_list_data_labeling_jobs_pages():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_data_labeling_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[], next_page_token="def",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[data_labeling_job.DataLabelingJob(),],
                next_page_token="ghi",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_data_labeling_jobs(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_delete_data_labeling_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.DeleteDataLabelingJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.delete_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_data_labeling_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.delete_data_labeling_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_data_labeling_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_data_labeling_job(
            job_service.DeleteDataLabelingJobRequest(), name="name_value",
        )


def test_cancel_data_labeling_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.CancelDataLabelingJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.cancel_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.cancel_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_data_labeling_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.cancel_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.cancel_data_labeling_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_cancel_data_labeling_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_data_labeling_job(
            job_service.CancelDataLabelingJobRequest(), name="name_value",
        )


def test_create_hyperparameter_tuning_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.CreateHyperparameterTuningJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob(
            name="name_value",
            display_name="display_name_value",
            max_trial_count=1609,
            parallel_trial_count=2128,
            max_failed_trial_count=2317,
            state=job_state.JobState.JOB_STATE_QUEUED,
        )

        response = client.create_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_hyperparameter_tuning_job.HyperparameterTuningJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_trial_count == 1609
    assert response.parallel_trial_count == 2128
    assert response.max_failed_trial_count == 2317
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_create_hyperparameter_tuning_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.create_hyperparameter_tuning_job(
            parent="parent_value",
            hyperparameter_tuning_job=gca_hyperparameter_tuning_job.HyperparameterTuningJob(
                name="name_value"
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[
            0
        ].hyperparameter_tuning_job == gca_hyperparameter_tuning_job.HyperparameterTuningJob(
            name="name_value"
        )


def test_create_hyperparameter_tuning_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_hyperparameter_tuning_job(
            job_service.CreateHyperparameterTuningJobRequest(),
            parent="parent_value",
            hyperparameter_tuning_job=gca_hyperparameter_tuning_job.HyperparameterTuningJob(
                name="name_value"
            ),
        )


def test_get_hyperparameter_tuning_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.GetHyperparameterTuningJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = hyperparameter_tuning_job.HyperparameterTuningJob(
            name="name_value",
            display_name="display_name_value",
            max_trial_count=1609,
            parallel_trial_count=2128,
            max_failed_trial_count=2317,
            state=job_state.JobState.JOB_STATE_QUEUED,
        )

        response = client.get_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, hyperparameter_tuning_job.HyperparameterTuningJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_trial_count == 1609
    assert response.parallel_trial_count == 2128
    assert response.max_failed_trial_count == 2317
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_get_hyperparameter_tuning_job_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetHyperparameterTuningJobRequest(name="name/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_hyperparameter_tuning_job), "__call__"
    ) as call:
        call.return_value = hyperparameter_tuning_job.HyperparameterTuningJob()
        client.get_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_hyperparameter_tuning_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = hyperparameter_tuning_job.HyperparameterTuningJob()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_hyperparameter_tuning_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_hyperparameter_tuning_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_hyperparameter_tuning_job(
            job_service.GetHyperparameterTuningJobRequest(), name="name_value",
        )


def test_list_hyperparameter_tuning_jobs(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.ListHyperparameterTuningJobsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListHyperparameterTuningJobsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_hyperparameter_tuning_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListHyperparameterTuningJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_hyperparameter_tuning_jobs_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListHyperparameterTuningJobsRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        call.return_value = job_service.ListHyperparameterTuningJobsResponse()
        client.list_hyperparameter_tuning_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_hyperparameter_tuning_jobs_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListHyperparameterTuningJobsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_hyperparameter_tuning_jobs(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_hyperparameter_tuning_jobs_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_hyperparameter_tuning_jobs(
            job_service.ListHyperparameterTuningJobsRequest(), parent="parent_value",
        )


def test_list_hyperparameter_tuning_jobs_pager():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[], next_page_token="def",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_hyperparameter_tuning_jobs(request={},)]
        assert len(results) == 6
        assert all(
            isinstance(i, hyperparameter_tuning_job.HyperparameterTuningJob)
            for i in results
        )


def test_list_hyperparameter_tuning_jobs_pages():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[], next_page_token="def",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_hyperparameter_tuning_jobs(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_delete_hyperparameter_tuning_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.DeleteHyperparameterTuningJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.delete_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_hyperparameter_tuning_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.delete_hyperparameter_tuning_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_hyperparameter_tuning_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_hyperparameter_tuning_job(
            job_service.DeleteHyperparameterTuningJobRequest(), name="name_value",
        )


def test_cancel_hyperparameter_tuning_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.CancelHyperparameterTuningJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.cancel_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.cancel_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_hyperparameter_tuning_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.cancel_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.cancel_hyperparameter_tuning_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_cancel_hyperparameter_tuning_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_hyperparameter_tuning_job(
            job_service.CancelHyperparameterTuningJobRequest(), name="name_value",
        )


def test_create_batch_prediction_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.CreateBatchPredictionJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_batch_prediction_job.BatchPredictionJob(
            name="name_value",
            display_name="display_name_value",
            model="model_value",
            generate_explanation=True,
            state=job_state.JobState.JOB_STATE_QUEUED,
        )

        response = client.create_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_batch_prediction_job.BatchPredictionJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.model == "model_value"

    assert response.generate_explanation is True
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_create_batch_prediction_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_batch_prediction_job.BatchPredictionJob()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.create_batch_prediction_job(
            parent="parent_value",
            batch_prediction_job=gca_batch_prediction_job.BatchPredictionJob(
                name="name_value"
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[
            0
        ].batch_prediction_job == gca_batch_prediction_job.BatchPredictionJob(
            name="name_value"
        )


def test_create_batch_prediction_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_batch_prediction_job(
            job_service.CreateBatchPredictionJobRequest(),
            parent="parent_value",
            batch_prediction_job=gca_batch_prediction_job.BatchPredictionJob(
                name="name_value"
            ),
        )


def test_get_batch_prediction_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.GetBatchPredictionJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = batch_prediction_job.BatchPredictionJob(
            name="name_value",
            display_name="display_name_value",
            model="model_value",
            generate_explanation=True,
            state=job_state.JobState.JOB_STATE_QUEUED,
        )

        response = client.get_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, batch_prediction_job.BatchPredictionJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.model == "model_value"

    assert response.generate_explanation is True
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_get_batch_prediction_job_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetBatchPredictionJobRequest(name="name/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_batch_prediction_job), "__call__"
    ) as call:
        call.return_value = batch_prediction_job.BatchPredictionJob()
        client.get_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_batch_prediction_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = batch_prediction_job.BatchPredictionJob()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_batch_prediction_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_batch_prediction_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_batch_prediction_job(
            job_service.GetBatchPredictionJobRequest(), name="name_value",
        )


def test_list_batch_prediction_jobs(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.ListBatchPredictionJobsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListBatchPredictionJobsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_batch_prediction_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListBatchPredictionJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_batch_prediction_jobs_field_headers():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListBatchPredictionJobsRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        call.return_value = job_service.ListBatchPredictionJobsResponse()
        client.list_batch_prediction_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_batch_prediction_jobs_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListBatchPredictionJobsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_batch_prediction_jobs(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_batch_prediction_jobs_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_batch_prediction_jobs(
            job_service.ListBatchPredictionJobsRequest(), parent="parent_value",
        )


def test_list_batch_prediction_jobs_pager():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[], next_page_token="def",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[batch_prediction_job.BatchPredictionJob(),],
                next_page_token="ghi",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_batch_prediction_jobs(request={},)]
        assert len(results) == 6
        assert all(
            isinstance(i, batch_prediction_job.BatchPredictionJob) for i in results
        )


def test_list_batch_prediction_jobs_pages():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[], next_page_token="def",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[batch_prediction_job.BatchPredictionJob(),],
                next_page_token="ghi",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_batch_prediction_jobs(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_delete_batch_prediction_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.DeleteBatchPredictionJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.delete_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_batch_prediction_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.delete_batch_prediction_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_batch_prediction_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_batch_prediction_job(
            job_service.DeleteBatchPredictionJobRequest(), name="name_value",
        )


def test_cancel_batch_prediction_job(transport: str = "grpc"):
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = job_service.CancelBatchPredictionJobRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.cancel_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.cancel_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_batch_prediction_job_flattened():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.cancel_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.cancel_batch_prediction_job(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_cancel_batch_prediction_job_flattened_error():
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_batch_prediction_job(
            job_service.CancelBatchPredictionJobRequest(), name="name_value",
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = JobServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = JobServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = JobServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.JobServiceGrpcTransport,)


def test_job_service_base_transport():
    # Instantiate the base transport.
    transport = transports.JobServiceTransport(
        credentials=credentials.AnonymousCredentials(),
    )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_custom_job",
        "get_custom_job",
        "list_custom_jobs",
        "delete_custom_job",
        "cancel_custom_job",
        "create_data_labeling_job",
        "get_data_labeling_job",
        "list_data_labeling_jobs",
        "delete_data_labeling_job",
        "cancel_data_labeling_job",
        "create_hyperparameter_tuning_job",
        "get_hyperparameter_tuning_job",
        "list_hyperparameter_tuning_jobs",
        "delete_hyperparameter_tuning_job",
        "cancel_hyperparameter_tuning_job",
        "create_batch_prediction_job",
        "get_batch_prediction_job",
        "list_batch_prediction_jobs",
        "delete_batch_prediction_job",
        "cancel_batch_prediction_job",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_job_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        JobServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",)
        )


def test_job_service_host_no_port():
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:443"


def test_job_service_host_with_port():
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com:8000"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:8000"


def test_job_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")
    transport = transports.JobServiceGrpcTransport(channel=channel,)
    assert transport.grpc_channel is channel


def test_job_service_grpc_lro_client():
    client = JobServiceClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_batch_prediction_job_path():
    project = "squid"
    location = "clam"
    batch_prediction_job = "whelk"

    expected = "projects/{project}/locations/{location}/batchPredictionJobs/{batch_prediction_job}".format(
        project=project, location=location, batch_prediction_job=batch_prediction_job,
    )
    actual = JobServiceClient.batch_prediction_job_path(
        project, location, batch_prediction_job
    )
    assert expected == actual


def test_data_labeling_job_path():
    project = "squid"
    location = "clam"
    data_labeling_job = "whelk"

    expected = "projects/{project}/locations/{location}/dataLabelingJobs/{data_labeling_job}".format(
        project=project, location=location, data_labeling_job=data_labeling_job,
    )
    actual = JobServiceClient.data_labeling_job_path(
        project, location, data_labeling_job
    )
    assert expected == actual


def test_custom_job_path():
    project = "squid"
    location = "clam"
    custom_job = "whelk"

    expected = "projects/{project}/locations/{location}/customJobs/{custom_job}".format(
        project=project, location=location, custom_job=custom_job,
    )
    actual = JobServiceClient.custom_job_path(project, location, custom_job)
    assert expected == actual


def test_hyperparameter_tuning_job_path():
    project = "squid"
    location = "clam"
    hyperparameter_tuning_job = "whelk"

    expected = "projects/{project}/locations/{location}/hyperparameterTuningJobs/{hyperparameter_tuning_job}".format(
        project=project,
        location=location,
        hyperparameter_tuning_job=hyperparameter_tuning_job,
    )
    actual = JobServiceClient.hyperparameter_tuning_job_path(
        project, location, hyperparameter_tuning_job
    )
    assert expected == actual
