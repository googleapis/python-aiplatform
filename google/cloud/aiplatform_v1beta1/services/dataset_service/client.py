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

from collections import OrderedDict
from typing import Dict, Sequence, Tuple, Type, Union
import pkg_resources

import google.api_core.client_options as ClientOptions  # type: ignore
from google.api_core import exceptions  # type: ignore
from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.auth import credentials  # type: ignore
from google.oauth2 import service_account  # type: ignore

from google.api_core import operation as ga_operation
from google.cloud.aiplatform_v1beta1.services.dataset_service import pagers
from google.cloud.aiplatform_v1beta1.types import annotation
from google.cloud.aiplatform_v1beta1.types import annotation_spec
from google.cloud.aiplatform_v1beta1.types import data_item
from google.cloud.aiplatform_v1beta1.types import dataset
from google.cloud.aiplatform_v1beta1.types import dataset as gca_dataset
from google.cloud.aiplatform_v1beta1.types import dataset_service
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.protobuf import empty_pb2 as empty  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore

from .transports.base import DatasetServiceTransport
from .transports.grpc import DatasetServiceGrpcTransport


class DatasetServiceClientMeta(type):
    """Metaclass for the DatasetService client.

    This provides class-level methods for building and retrieving
    support objects (e.g. transport) without polluting the client instance
    objects.
    """

    _transport_registry = (
        OrderedDict()
    )  # type: Dict[str, Type[DatasetServiceTransport]]
    _transport_registry["grpc"] = DatasetServiceGrpcTransport

    def get_transport_class(cls, label: str = None,) -> Type[DatasetServiceTransport]:
        """Return an appropriate transport class.

        Args:
            label: The name of the desired transport. If none is
                provided, then the first transport in the registry is used.

        Returns:
            The transport class to use.
        """
        # If a specific transport is requested, return that one.
        if label:
            return cls._transport_registry[label]

        # No transport is requested; return the default (that is, the first one
        # in the dictionary).
        return next(iter(cls._transport_registry.values()))


class DatasetServiceClient(metaclass=DatasetServiceClientMeta):
    """"""

    DEFAULT_OPTIONS = ClientOptions.ClientOptions(
        api_endpoint="aiplatform.googleapis.com"
    )

    @classmethod
    def from_service_account_file(cls, filename: str, *args, **kwargs):
        """Creates an instance of this client using the provided credentials
        file.

        Args:
            filename (str): The path to the service account private key json
                file.
            args: Additional arguments to pass to the constructor.
            kwargs: Additional arguments to pass to the constructor.

        Returns:
            {@api.name}: The constructed client.
        """
        credentials = service_account.Credentials.from_service_account_file(filename)
        kwargs["credentials"] = credentials
        return cls(*args, **kwargs)

    from_service_account_json = from_service_account_file

    @staticmethod
    def dataset_path(project: str, location: str, dataset: str,) -> str:
        """Return a fully-qualified dataset string."""
        return "projects/{project}/locations/{location}/datasets/{dataset}".format(
            project=project, location=location, dataset=dataset,
        )

    def __init__(
        self,
        *,
        credentials: credentials.Credentials = None,
        transport: Union[str, DatasetServiceTransport] = None,
        client_options: ClientOptions.ClientOptions = DEFAULT_OPTIONS,
    ) -> None:
        """Instantiate the dataset service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.DatasetServiceTransport]): The
                transport to use. If set to None, a transport is chosen
                automatically.
            client_options (ClientOptions): Custom options for the client.
        """
        if isinstance(client_options, dict):
            client_options = ClientOptions.from_dict(client_options)

        # Save or instantiate the transport.
        # Ordinarily, we provide the transport, but allowing a custom transport
        # instance provides an extensibility point for unusual situations.
        if isinstance(transport, DatasetServiceTransport):
            if credentials:
                raise ValueError(
                    "When providing a transport instance, "
                    "provide its credentials directly."
                )
            self._transport = transport
        else:
            Transport = type(self).get_transport_class(transport)
            self._transport = Transport(
                credentials=credentials,
                host=client_options.api_endpoint or "aiplatform.googleapis.com",
            )

    def create_dataset(
        self,
        request: dataset_service.CreateDatasetRequest = None,
        *,
        parent: str = None,
        dataset: gca_dataset.Dataset = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> ga_operation.Operation:
        r"""Creates a Dataset.

        Args:
            request (:class:`~.dataset_service.CreateDatasetRequest`):
                The request object. Request message for
                [DatasetService.CreateDataset][google.cloud.aiplatform.v1beta1.DatasetService.CreateDataset].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                the Dataset in. Format:
                ``projects/{project}/locations/{location}``
                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            dataset (:class:`~.gca_dataset.Dataset`):
                Required. The Dataset to create.
                This corresponds to the ``dataset`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.ga_operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:``~.gca_dataset.Dataset``: A collection of
                DataItems and Annotations on them.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([parent, dataset]):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = dataset_service.CreateDatasetRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if parent is not None:
            request.parent = parent
        if dataset is not None:
            request.dataset = dataset

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.create_dataset,
            default_timeout=None,
            client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = ga_operation.from_gapic(
            response,
            self._transport.operations_client,
            gca_dataset.Dataset,
            metadata_type=dataset_service.CreateDatasetOperationMetadata,
        )

        # Done; return the response.
        return response

    def get_dataset(
        self,
        request: dataset_service.GetDatasetRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> dataset.Dataset:
        r"""Gets a Dataset.

        Args:
            request (:class:`~.dataset_service.GetDatasetRequest`):
                The request object. Request message for
                [DatasetService.GetDataset][google.cloud.aiplatform.v1beta1.DatasetService.GetDataset].
            name (:class:`str`):
                Required. The name of the Dataset
                resource.
                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.dataset.Dataset:
                A collection of DataItems and
                Annotations on them.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([name]):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = dataset_service.GetDatasetRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.get_dataset, default_timeout=None, client_info=_client_info,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    def update_dataset(
        self,
        request: dataset_service.UpdateDatasetRequest = None,
        *,
        dataset: gca_dataset.Dataset = None,
        update_mask: field_mask.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_dataset.Dataset:
        r"""Updates a Dataset.

        Args:
            request (:class:`~.dataset_service.UpdateDatasetRequest`):
                The request object. Request message for
                [DatasetService.UpdateDataset][google.cloud.aiplatform.v1beta1.DatasetService.UpdateDataset].
            dataset (:class:`~.gca_dataset.Dataset`):
                Required. The Dataset which replaces
                the resource on the server.
                This corresponds to the ``dataset`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`~.field_mask.FieldMask`):
                Required. The update mask applies to the resource. For
                the ``FieldMask`` definition, see

                [FieldMask](https:
                //tinyurl.com/dev-google-protobuf#google.protobuf.FieldMask).
                Updatable fields:

                -  ``display_name``
                -  ``description``
                -  ``labels``
                This corresponds to the ``update_mask`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.gca_dataset.Dataset:
                A collection of DataItems and
                Annotations on them.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([dataset, update_mask]):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = dataset_service.UpdateDatasetRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if dataset is not None:
            request.dataset = dataset
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.update_dataset,
            default_timeout=None,
            client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    def list_datasets(
        self,
        request: dataset_service.ListDatasetsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListDatasetsPager:
        r"""Lists Datasets in a Location.

        Args:
            request (:class:`~.dataset_service.ListDatasetsRequest`):
                The request object. Request message for
                [DatasetService.ListDatasets][google.cloud.aiplatform.v1beta1.DatasetService.ListDatasets].
            parent (:class:`str`):
                Required. The name of the Dataset's parent resource.
                Format: ``projects/{project}/locations/{location}``
                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.pagers.ListDatasetsPager:
                Response message for
                [DatasetService.ListDatasets][google.cloud.aiplatform.v1beta1.DatasetService.ListDatasets].

                Iterating over this object will yield results and
                resolve additional pages automatically.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([parent]):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = dataset_service.ListDatasetsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.list_datasets,
            default_timeout=None,
            client_info=_client_info,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # This method is paged; wrap the response in a pager, which provides
        # an `__iter__` convenience method.
        response = pagers.ListDatasetsPager(
            method=rpc, request=request, response=response,
        )

        # Done; return the response.
        return response

    def delete_dataset(
        self,
        request: dataset_service.DeleteDatasetRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> ga_operation.Operation:
        r"""Deletes a Dataset.

        Args:
            request (:class:`~.dataset_service.DeleteDatasetRequest`):
                The request object. Request message for
                [DatasetService.DeleteDataset][google.cloud.aiplatform.v1beta1.DatasetService.DeleteDataset].
            name (:class:`str`):
                Required. The resource name of the Dataset to delete.
                Format:
                ``projects/{project}/locations/{location}/datasets/{dataset}``
                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.ga_operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:``~.empty.Empty``: A generic empty message that
                you can re-use to avoid defining duplicated empty
                messages in your APIs. A typical example is to use it as
                the request or the response type of an API method. For
                instance:

                ::

                    service Foo {
                      rpc Bar(google.protobuf.Empty) returns (google.protobuf.Empty);
                    }

                The JSON representation for ``Empty`` is empty JSON
                object ``{}``.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([name]):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = dataset_service.DeleteDatasetRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.delete_dataset,
            default_timeout=None,
            client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = ga_operation.from_gapic(
            response,
            self._transport.operations_client,
            empty.Empty,
            metadata_type=gca_operation.DeleteOperationMetadata,
        )

        # Done; return the response.
        return response

    def import_data(
        self,
        request: dataset_service.ImportDataRequest = None,
        *,
        name: str = None,
        import_configs: Sequence[dataset.ImportDataConfig] = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> ga_operation.Operation:
        r"""Imports data into a Dataset.

        Args:
            request (:class:`~.dataset_service.ImportDataRequest`):
                The request object. Request message for
                [DatasetService.ImportData][google.cloud.aiplatform.v1beta1.DatasetService.ImportData].
            name (:class:`str`):
                Required. The name of the Dataset resource. Format:
                ``projects/{project}/locations/{location}/datasets/{dataset}``
                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            import_configs (:class:`Sequence[~.dataset.ImportDataConfig]`):
                Required. The desired input
                locations. The contents of all input
                locations will be imported in one batch.
                This corresponds to the ``import_configs`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.ga_operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:``~.dataset_service.ImportDataResponse``:
                Response message for
                [DatasetService.ImportData][google.cloud.aiplatform.v1beta1.DatasetService.ImportData].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([name, import_configs]):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = dataset_service.ImportDataRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if name is not None:
            request.name = name
        if import_configs is not None:
            request.import_configs = import_configs

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.import_data, default_timeout=None, client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = ga_operation.from_gapic(
            response,
            self._transport.operations_client,
            dataset_service.ImportDataResponse,
            metadata_type=dataset_service.ImportDataOperationMetadata,
        )

        # Done; return the response.
        return response

    def export_data(
        self,
        request: dataset_service.ExportDataRequest = None,
        *,
        name: str = None,
        export_config: dataset.ExportDataConfig = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> ga_operation.Operation:
        r"""Exports data from a Dataset.

        Args:
            request (:class:`~.dataset_service.ExportDataRequest`):
                The request object. Request message for
                [DatasetService.ExportData][google.cloud.aiplatform.v1beta1.DatasetService.ExportData].
            name (:class:`str`):
                Required. The name of the Dataset resource. Format:
                ``projects/{project}/locations/{location}/datasets/{dataset}``
                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            export_config (:class:`~.dataset.ExportDataConfig`):
                Required. The desired output
                location.
                This corresponds to the ``export_config`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.ga_operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:``~.dataset_service.ExportDataResponse``:
                Response message for
                [DatasetService.ExportData][google.cloud.aiplatform.v1beta1.DatasetService.ExportData].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([name, export_config]):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = dataset_service.ExportDataRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if name is not None:
            request.name = name
        if export_config is not None:
            request.export_config = export_config

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.export_data, default_timeout=None, client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = ga_operation.from_gapic(
            response,
            self._transport.operations_client,
            dataset_service.ExportDataResponse,
            metadata_type=dataset_service.ExportDataOperationMetadata,
        )

        # Done; return the response.
        return response

    def list_data_items(
        self,
        request: dataset_service.ListDataItemsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListDataItemsPager:
        r"""Lists DataItems in a Dataset.

        Args:
            request (:class:`~.dataset_service.ListDataItemsRequest`):
                The request object. Request message for
                [DatasetService.ListDataItems][google.cloud.aiplatform.v1beta1.DatasetService.ListDataItems].
            parent (:class:`str`):
                Required. The resource name of the Dataset to list
                DataItems from. Format:
                ``projects/{project}/locations/{location}/datasets/{dataset}``
                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.pagers.ListDataItemsPager:
                Response message for
                [DatasetService.ListDataItems][google.cloud.aiplatform.v1beta1.DatasetService.ListDataItems].

                Iterating over this object will yield results and
                resolve additional pages automatically.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([parent]):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = dataset_service.ListDataItemsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.list_data_items,
            default_timeout=None,
            client_info=_client_info,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # This method is paged; wrap the response in a pager, which provides
        # an `__iter__` convenience method.
        response = pagers.ListDataItemsPager(
            method=rpc, request=request, response=response,
        )

        # Done; return the response.
        return response

    def get_annotation_spec(
        self,
        request: dataset_service.GetAnnotationSpecRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> annotation_spec.AnnotationSpec:
        r"""Gets an AnnotationSpec.

        Args:
            request (:class:`~.dataset_service.GetAnnotationSpecRequest`):
                The request object. Request message for
                [DatasetService.GetAnnotationSpec][google.cloud.aiplatform.v1beta1.DatasetService.GetAnnotationSpec].
            name (:class:`str`):
                Required. The name of the AnnotationSpec resource.
                Format:

                ``projects/{project}/locations/{location}/datasets/{dataset}/annotationSpecs/{annotation_spec}``
                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.annotation_spec.AnnotationSpec:
                Identifies a concept with which
                DataItems may be annotated with.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([name]):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = dataset_service.GetAnnotationSpecRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.get_annotation_spec,
            default_timeout=None,
            client_info=_client_info,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    def list_annotations(
        self,
        request: dataset_service.ListAnnotationsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListAnnotationsPager:
        r"""Lists Annotations belongs to a dataitem

        Args:
            request (:class:`~.dataset_service.ListAnnotationsRequest`):
                The request object. Request message for
                [DatasetService.ListAnnotations][google.cloud.aiplatform.v1beta1.DatasetService.ListAnnotations].
            parent (:class:`str`):
                Required. The resource name of the DataItem to list
                Annotations from. Format:

                ``projects/{project}/locations/{location}/datasets/{dataset}/dataItems/{data_item}``
                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.pagers.ListAnnotationsPager:
                Response message for
                [DatasetService.ListAnnotations][google.cloud.aiplatform.v1beta1.DatasetService.ListAnnotations].

                Iterating over this object will yield results and
                resolve additional pages automatically.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([parent]):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = dataset_service.ListAnnotationsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.list_annotations,
            default_timeout=None,
            client_info=_client_info,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # This method is paged; wrap the response in a pager, which provides
        # an `__iter__` convenience method.
        response = pagers.ListAnnotationsPager(
            method=rpc, request=request, response=response,
        )

        # Done; return the response.
        return response


try:
    _client_info = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            "google-cloud-aiplatform",
        ).version,
    )
except pkg_resources.DistributionNotFound:
    _client_info = gapic_v1.client_info.ClientInfo()


__all__ = ("DatasetServiceClient",)
