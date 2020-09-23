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

from google.cloud.aiplatform_v1beta1.types import annotation_spec
from google.cloud.aiplatform_v1beta1.types import dataset
from google.cloud.aiplatform_v1beta1.types import dataset as gca_dataset
from google.cloud.aiplatform_v1beta1.types import dataset_service
from google.longrunning import operations_pb2 as operations  # type: ignore


class DatasetServiceTransport(metaclass=abc.ABCMeta):
    """Abstract transport class for DatasetService."""

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
    def create_dataset(
        self,
    ) -> typing.Callable[[dataset_service.CreateDatasetRequest], operations.Operation]:
        raise NotImplementedError

    @property
    def get_dataset(
        self,
    ) -> typing.Callable[[dataset_service.GetDatasetRequest], dataset.Dataset]:
        raise NotImplementedError

    @property
    def update_dataset(
        self,
    ) -> typing.Callable[[dataset_service.UpdateDatasetRequest], gca_dataset.Dataset]:
        raise NotImplementedError

    @property
    def list_datasets(
        self,
    ) -> typing.Callable[
        [dataset_service.ListDatasetsRequest], dataset_service.ListDatasetsResponse
    ]:
        raise NotImplementedError

    @property
    def delete_dataset(
        self,
    ) -> typing.Callable[[dataset_service.DeleteDatasetRequest], operations.Operation]:
        raise NotImplementedError

    @property
    def import_data(
        self,
    ) -> typing.Callable[[dataset_service.ImportDataRequest], operations.Operation]:
        raise NotImplementedError

    @property
    def export_data(
        self,
    ) -> typing.Callable[[dataset_service.ExportDataRequest], operations.Operation]:
        raise NotImplementedError

    @property
    def list_data_items(
        self,
    ) -> typing.Callable[
        [dataset_service.ListDataItemsRequest], dataset_service.ListDataItemsResponse
    ]:
        raise NotImplementedError

    @property
    def get_annotation_spec(
        self,
    ) -> typing.Callable[
        [dataset_service.GetAnnotationSpecRequest], annotation_spec.AnnotationSpec
    ]:
        raise NotImplementedError

    @property
    def list_annotations(
        self,
    ) -> typing.Callable[
        [dataset_service.ListAnnotationsRequest],
        dataset_service.ListAnnotationsResponse,
    ]:
        raise NotImplementedError


__all__ = ("DatasetServiceTransport",)
