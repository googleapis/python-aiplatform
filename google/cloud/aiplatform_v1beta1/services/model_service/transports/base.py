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

import abc
import typing

from google import auth
from google.api_core import operations_v1  # type: ignore
from google.auth import credentials  # type: ignore

from google.cloud.aiplatform_v1beta1.types import model
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types import model_evaluation
from google.cloud.aiplatform_v1beta1.types import model_evaluation_slice
from google.cloud.aiplatform_v1beta1.types import model_service
from google.longrunning import operations_pb2 as operations  # type: ignore


class ModelServiceTransport(metaclass=abc.ABCMeta):
    """Abstract transport class for ModelService."""

    AUTH_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: credentials.Credentials = None,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]): The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
        """
        # Save the hostname. Default to port 443 (HTTPS) if none is specified.
        if ":" not in host:
            host += ":443"
        self._host = host

        # If no credentials are provided, then determine the appropriate
        # defaults.
        if credentials is None:
            credentials, _ = auth.default(scopes=self.AUTH_SCOPES)

        # Save the credentials.
        self._credentials = credentials

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Return the client designed to process long-running operations."""
        raise NotImplementedError

    @property
    def upload_model(
        self,
    ) -> typing.Callable[[model_service.UploadModelRequest], operations.Operation]:
        raise NotImplementedError

    @property
    def get_model(
        self,
    ) -> typing.Callable[[model_service.GetModelRequest], model.Model]:
        raise NotImplementedError

    @property
    def list_models(
        self,
    ) -> typing.Callable[
        [model_service.ListModelsRequest], model_service.ListModelsResponse
    ]:
        raise NotImplementedError

    @property
    def update_model(
        self,
    ) -> typing.Callable[[model_service.UpdateModelRequest], gca_model.Model]:
        raise NotImplementedError

    @property
    def delete_model(
        self,
    ) -> typing.Callable[[model_service.DeleteModelRequest], operations.Operation]:
        raise NotImplementedError

    @property
    def export_model(
        self,
    ) -> typing.Callable[[model_service.ExportModelRequest], operations.Operation]:
        raise NotImplementedError

    @property
    def get_model_evaluation(
        self,
    ) -> typing.Callable[
        [model_service.GetModelEvaluationRequest], model_evaluation.ModelEvaluation
    ]:
        raise NotImplementedError

    @property
    def list_model_evaluations(
        self,
    ) -> typing.Callable[
        [model_service.ListModelEvaluationsRequest],
        model_service.ListModelEvaluationsResponse,
    ]:
        raise NotImplementedError

    @property
    def get_model_evaluation_slice(
        self,
    ) -> typing.Callable[
        [model_service.GetModelEvaluationSliceRequest],
        model_evaluation_slice.ModelEvaluationSlice,
    ]:
        raise NotImplementedError

    @property
    def list_model_evaluation_slices(
        self,
    ) -> typing.Callable[
        [model_service.ListModelEvaluationSlicesRequest],
        model_service.ListModelEvaluationSlicesResponse,
    ]:
        raise NotImplementedError


__all__ = ("ModelServiceTransport",)
