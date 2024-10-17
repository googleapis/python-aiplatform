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
#
"""Classes for working with Vertex AI Search."""

from collections.abc import Iterator
import enum
import re
from typing import Optional, Union

from google.api_core import exceptions
from google.cloud import discoveryengine_v1alpha as discoveryengine
from google.cloud.aiplatform import initializer as aiplatform_initializer
from vertexai.generative_models import _generative_models

TargetSite = discoveryengine.TargetSite
InlineSource = discoveryengine.ImportDocumentsRequest.InlineSource
GcsSource = discoveryengine.GcsSource
BigQuerySource = discoveryengine.BigQuerySource
SpannerSource = discoveryengine.SpannerSource
FirestoreSource = discoveryengine.FirestoreSource
BigtableOptions = discoveryengine.BigtableOptions
BigtableSource = discoveryengine.BigtableSource
AlloyDbSource = discoveryengine.AlloyDbSource
FhirStoreSource = discoveryengine.FhirStoreSource

DataSource = Union[
    TargetSite,
    InlineSource,
    GcsSource,
    BigQuerySource,
    SpannerSource,
    FirestoreSource,
    BigtableSource,
    AlloyDbSource,
    FhirStoreSource,
]

_import_document_map = {
    InlineSource: "inline_source",
    GcsSource: "gcs_source",
    BigQuerySource: "bigquery_source",
    SpannerSource: "spanner_source",
    FirestoreSource: "firestore_source",
    BigtableSource: "bigtable_source",
    AlloyDbSource: "alloydb_source",
}

IndustryVertical = discoveryengine.IndustryVertical
ReconciliationMode = discoveryengine.ImportDocumentsRequest.ReconciliationMode
SearchTier = discoveryengine.SearchTier
SearchAddOn = discoveryengine.SearchAddOn


class DataType(enum.Enum):
    WEBSITE = discoveryengine.DataStore.ContentConfig.PUBLIC_WEBSITE
    STRUCTURED = discoveryengine.DataStore.ContentConfig.NO_CONTENT
    UNSTRUCTURED = discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED
    GOOGLE_WORKSPACE = discoveryengine.DataStore.ContentConfig.GOOGLE_WORKSPACE
    WEBSITE_ADVANCED = enum.auto()


def _collection_name(project: str, location: str) -> str:
    """Returns the full resource name starting with projects/ given a project and location."""
    return f"projects/{project}/locations/{location}/collections/default_collection"


def _fihr_store_name(project: str, location: str, dataset: str, fihr_store: str) -> str:
    """Returns the full resource name starting with projects/ given a project and location."""
    return f"projects/{project}/locations/{location}/datasets/{dataset}/fhirStores/{fihr_store}"


FhirStoreSource.fhir_store_name = _fihr_store_name


class DataStore:
    r"""Data Store for Vertex AI Search."""

    _data_store_client_instance: discoveryengine.DataStoreServiceClient = None
    _site_search_engine_client_instance: (
        discoveryengine.SiteSearchEngineServiceClient
    ) = None
    _document_client_instance: discoveryengine.DocumentServiceClient = None

    def __init__(
        self,
        data_store_id: str,
    ) -> None:
        r"""Initializes a Data Store.

        Args:
            data_store_id (str): ID or full resource name of the data store.
        """
        pattern = (
            r"^projects\/(?P<project>[a-z0-9-]+)\/"
            r"locations\/(?P<location>[a-z0-9][a-z0-9-]*)\/"
            r"(?:collections\/[a-z0-9][a-z0-9-_]*)?\/"
            r"dataStores\/(?P<data_store>[a-z0-9][a-z0-9-_]*)$"
        )
        match = re.match(pattern, data_store_id)

        if match:
            self._project = match.group("project")
            self._location = match.group("location")
            self._data_store_id = match.group("data_store")
        else:
            self._project = aiplatform_initializer.search_config.project
            self._location = aiplatform_initializer.search_config.location
            self._data_store_id = data_store_id

    @classmethod
    def _data_store_client(cls) -> discoveryengine.DataStoreServiceClient:
        """Class-level method to create the Data Store client if it doesn't exist."""
        if cls._data_store_client_instance is None:
            cls._data_store_client_instance = (
                aiplatform_initializer.search_config.create_client(
                    client_class=discoveryengine.DataStoreServiceClient
                )
            )
        return cls._data_store_client_instance

    @classmethod
    def _site_search_engine_client(
        cls,
    ) -> discoveryengine.SiteSearchEngineServiceClient:
        """Class-level method to create the Site Search Engine client if it doesn't exist."""
        if cls._site_search_engine_client_instance is None:
            cls._site_search_engine_client_instance = (
                aiplatform_initializer.search_config.create_client(
                    client_class=discoveryengine.SiteSearchEngineServiceClient
                )
            )
        return cls._site_search_engine_client_instance

    @classmethod
    def _document_client(cls) -> discoveryengine.DocumentServiceClient:
        """Class-level method to create the Document Service client if it doesn't exist."""
        if cls._document_client_instance is None:
            cls._document_client_instance = (
                aiplatform_initializer.search_config.create_client(
                    client_class=discoveryengine.DocumentServiceClient
                )
            )
        return cls._document_client_instance

    @property
    def _gapic_data_store(self) -> discoveryengine.types.DataStore:
        return DataStore._data_store_client().get_data_store(name=self._data_store_name)

    @property
    def _collection_name(self) -> str:
        """Returns the full resource name starting with projects/ given a project and location."""
        return _collection_name(self._project, self._location)

    @property
    def _data_store_name(self) -> str:
        """Returns the full resource name starting with projects/ given a data store name."""
        return f"{self._collection_name}/dataStores/{self._data_store_id}"

    @property
    def _branch_name(self) -> str:
        """Returns the full resource name starting with projects/."""
        return f"{self._data_store_name}/branches/default_branch"

    @classmethod
    def create(
        cls,
        data_store_id: str,
        display_name: str,
        data_type: DataType,
        industry_vertical: IndustryVertical = IndustryVertical.GENERIC,
        workspace_config: Optional[discoveryengine.WorkspaceConfig] = None,
    ) -> "DataStore":
        """Creates a Data Store.

        Args:
            data_store_id (str): ID or full resource name of the data store.
            display_name (str): Display name of the data store.
            data_type (DataType): Data type of the data store. Options: WEBSITE, STRUCTURED, UNSTRUCTURED, GOOGLE_WORKSPACE, WEBSITE_ADVANCED.
            industry_vertical (IndustryVertical): Industry vertical of the data store. Options: GENERIC, MEDIA, HEALTHCARE_FHIR.
            workspace_config (WorkspaceConfig): Optional. Workspace config of the data store. Only supported for GOOGLE_WORKSPACE data type.

        Returns:
            DataStore
        """
        data_store = cls(data_store_id)

        gapic_data_store = discoveryengine.DataStore(
            name=data_store._data_store_name,
            display_name=display_name,
            industry_vertical=industry_vertical,
            solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
            content_config=data_type.value,
            workspace_config=workspace_config,
        )

        operation = cls._data_store_client().create_data_store(
            request=discoveryengine.CreateDataStoreRequest(
                parent=data_store._collection_name,
                data_store=gapic_data_store,
                data_store_id=data_store._data_store_id,
                create_advanced_site_search=(data_type == DataType.WEBSITE_ADVANCED),
            )
        )
        operation.result()
        return data_store

    @classmethod
    def list_data_stores(cls) -> Iterator["DataStore"]:
        """Returns an iterator of Data Stores."""
        request = discoveryengine.ListDataStoresRequest(
            parent=_collection_name(
                aiplatform_initializer.search_config.project,
                aiplatform_initializer.search_config.location,
            )
        )
        while True:
            pager = cls._data_store_client().list_data_stores(request=request)
            for response in pager:
                yield DataStore(data_store_id=response.name)

            if not pager.next_page_token:
                break
            request.page_token = pager.next_page_token

    def import_data(
        self,
        data_source: DataSource,
        reconciliation_mode: Optional[ReconciliationMode] = None,
    ) -> None:
        """Imports data from a Data Source into the Data Store.

        Args:
            data_source (DataSource): Data source to import data from.
            reconciliation_mode (ReconciliationMode): Optional. How to reconcile
                the data. Options: INCREMENTAL, FULL.
        """

        if isinstance(data_source, TargetSite):
            operation = DataStore._site_search_engine_client().create_target_site(
                parent=f"{self._data_store_name}/siteSearchEngine",
                target_site=data_source,
            )
        else:
            operation = DataStore._document_client().import_documents(
                request=discoveryengine.ImportDocumentsRequest(
                    name=self._branch_name,
                    **{_import_document_map[type(data_source)]: data_source},
                    reconciliation_mode=reconciliation_mode,
                )
            )
        # TODO: Handle Operation Result and Metadata - Return to user
        operation.result()

    def delete(self) -> None:
        operation = DataStore._data_store_client().delete_data_store(
            name=self._data_store_name
        )
        try:
            operation.result()
        except exceptions.GoogleAPICallError:
            pass

    def purge(self, filter_: str = "*", force: bool = False) -> None:
        """Remove all data from the Data Store."""
        operation = DataStore._document_client().purge_documents(
            request=discoveryengine.PurgeDocumentsRequest(
                parent=self._branch_name,
                filter=filter_,
                force=force,
            )
        )
        operation.result()

    def __repr__(self) -> str:
        return repr(self._gapic_data_store)


class App:
    r"""App for Vertex AI Search."""

    _engine_client_instance: discoveryengine.EngineServiceClient = None
    _search_client_instance: (discoveryengine.SearchServiceClient) = None
    _conversational_search_client_instance: discoveryengine.ConversationalSearchServiceClient = (
        None
    )

    def __init__(
        self,
        app_id: str,
    ) -> None:
        r"""Initializes an App.

        Args:
            app_id (str): ID or Full resource name of the app.
        """
        pattern = (
            r"^projects\/(?P<project>[a-z0-9-]+)\/"
            r"locations\/(?P<location>[a-z0-9][a-z0-9-]*)\/"
            r"(?:collections\/[a-z0-9][a-z0-9-_]*)?\/"
            r"engines\/(?P<app>[a-z0-9][a-z0-9-_]*)$"
        )
        match = re.match(pattern, app_id)

        if match:
            self._project = match.group("project")
            self._location = match.group("location")
            self._app_id = match.group("app")
        else:
            self._project = aiplatform_initializer.search_config.project
            self._location = aiplatform_initializer.search_config.location
            self._app_id = app_id

    @property
    def _collection_name(self) -> str:
        """Returns the full resource name starting with projects/ given a project and location."""
        return _collection_name(self._project, self._location)

    @classmethod
    def _engine_client(cls) -> discoveryengine.EngineServiceClient:
        """Class-level method to create the Engine client if it doesn't exist."""
        if cls._engine_client_instance is None:
            cls._data_store_client_instance = (
                aiplatform_initializer.search_config.create_client(
                    client_class=discoveryengine.EngineServiceClient
                )
            )
        return cls._engine_client_instance

    @classmethod
    def _search_client(cls) -> discoveryengine.SearchServiceClient:
        """Class-level method to create the Search Service client if it doesn't exist."""
        if cls._search_client_instance is None:
            cls._search_client_instance = (
                aiplatform_initializer.search_config.create_client(
                    client_class=discoveryengine.SearchServiceClient
                )
            )
        return cls._search_client_instance

    @classmethod
    def _conversational_search_client(
        cls,
    ) -> discoveryengine.ConversationalSearchServiceClient:
        """Class-level method to create the Conversational Search Service client if it doesn't exist."""
        if cls._conversational_search_client_instance is None:
            cls._conversational_search_client_instance = (
                aiplatform_initializer.search_config.create_client(
                    client_class=discoveryengine.ConversationalSearchServiceClient
                )
            )
        return cls._conversational_search_client_instance

    @property
    def _gapic_engine(self) -> discoveryengine.Engine:
        return App._engine_client().get_engine(name=self._engine_name)

    @property
    def _engine_name(self) -> str:
        """Returns the full resource name starting with projects/ given an engine name."""
        return f"{self._collection_name}/engines/{self._app_id}"

    @property
    def _serving_config_name(self) -> str:
        """Returns the full resource name starting with projects/ given an engine name."""
        return f"{self._engine_name}/servingConfigs/default_search"

    @classmethod
    def create(
        cls,
        app_id: str,
        display_name: str,
        data_stores: list[DataStore],
        search_tier: SearchTier = SearchTier.SEARCH_TIER_STANDARD,
        search_add_ons: Optional[list[SearchAddOn]] = None,
    ) -> "App":
        r"""Creates a new Vertex AI Search App.

        Args:
            app_id (str): ID or Full resource name of the app.
            display_name (str): Display name of the app.
            data_stores (list[DataStore]): Data stores to be connected to the app.
            search_tier (SearchTier): Search tier of the app. Options: SEARCH_TIER_STANDARD, SEARCH_TIER_ENTERPRISE.
            search_add_ons (list[SearchAddOn]): Search add-ons of the app. Options: SEARCH_ADD_ON_LLM.

        Returns:
            App
        """
        app = cls(app_id=app_id)

        gapic_engine = discoveryengine.Engine(
            display_name=display_name,
            data_store_ids=[data_store._data_store_id for data_store in data_stores],
            search_engine_config=discoveryengine.Engine.SearchEngineConfig(
                search_tier=search_tier,
                search_add_ons=search_add_ons,
            ),
            solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
            industry_vertical=data_stores[0]._gapic_data_store.industry_vertical,
        )

        operation = cls._engine_client().create_engine(
            parent=app._collection_name,
            engine=gapic_engine,
            engine_id=app._app_id,
        )

        operation.result()
        return app

    @classmethod
    def list_apps(cls) -> Iterator["App"]:
        """Returns an iterator of Apps."""
        request = discoveryengine.ListEnginesRequest(
            parent=_collection_name(
                aiplatform_initializer.search_config.project,
                aiplatform_initializer.search_config.location,
            )
        )
        while True:
            pager = cls._engine_client().list_engines(request=request)
            for response in pager:
                yield App(app_id=response.name)

            if not pager.next_page_token:
                break
            request.page_token = pager.next_page_token

    def search(
        self, query: Union[str, _generative_models.Image], **kwargs
    ) -> Iterator[discoveryengine.SearchResponse]:
        r"""Performs a search query.

        Args:
            query (str or Image): Text query or image query.
            **kwargs (dict): Additional arguments to pass to the search request.

        Yields:
            discoveryengine.SearchResponse
        """

        text_query = None
        image_query = None
        if isinstance(query, _generative_models.Image):
            image_query = discoveryengine.SearchRequest.ImageQuery(
                image_bytes=query.data
            )
        else:
            text_query = query

        request = discoveryengine.SearchRequest(
            serving_config=self._serving_config_name,
            query=text_query,
            image_query=image_query,
            **kwargs,
        )

        while True:
            pager = App._search_client().search(request=request)
            for response in pager:
                yield response

            if not pager.next_page_token:
                break
            request.page_token = pager.next_page_token

    def answer(self, query: str, **kwargs) -> discoveryengine.AnswerQueryResponse:
        r"""Performs a question answering query.

        Args:
            query (str): Text query.
            **kwargs (dict): Additional arguments to pass to the Answer Query request.

        Returns:
            discoveryengine.AnswerQueryResponse
        """
        return App._conversational_search_client().answer_query(
            request=discoveryengine.AnswerQueryRequest(
                serving_config=self._serving_config_name,
                query=discoveryengine.Query(text=query),
                **kwargs,
            )
        )

    def delete(self) -> None:
        r"""Deletes the App."""
        operation = App._engine_client().delete_engine(name=self._engine_name)
        try:
            operation.result()
        except exceptions.GoogleAPICallError:
            pass

    def __repr__(self) -> str:
        return repr(self._gapic_engine)
