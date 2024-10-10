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
from typing import Any, Optional, Union

from google.api_core import exceptions

try:
    from google.cloud import discoveryengine_v1alpha as discoveryengine
except ImportError:
    raise ImportError(
        "The Vertex AI Search Client Library is not installed and is required for this module."
        'Please install the SDK using "pip install google-cloud-aiplatform[search]"'
    )

from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform.constants import base as constants

TargetSite = discoveryengine.TargetSite
InlineSource = discoveryengine.ImportDocumentsRequest.InlineSource
GcsSource = discoveryengine.GcsSource
BigQuerySource = discoveryengine.BigQuerySource
SpannerSource = discoveryengine.SpannerSource
FirestoreSource = discoveryengine.FirestoreSource
BigtableOptions = discoveryengine.BigtableOptions
BigtableSource = discoveryengine.BigtableSource
AlloyDbSource = discoveryengine.AlloyDbSource

DataSource = Union[
    TargetSite,
    InlineSource,
    GcsSource,
    BigQuerySource,
    SpannerSource,
    FirestoreSource,
    BigtableSource,
    AlloyDbSource,
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

ReconciliationMode = discoveryengine.ImportDocumentsRequest.ReconciliationMode
SearchTier = discoveryengine.SearchTier
SearchAddOn = discoveryengine.SearchAddOn
RelevanceThreshold = discoveryengine.SearchRequest.RelevanceThreshold


class DataType(enum.Enum):
    """Data type of the data store."""

    WEBSITE = discoveryengine.DataStore.ContentConfig.PUBLIC_WEBSITE
    STRUCTURED = discoveryengine.DataStore.ContentConfig.NO_CONTENT
    UNSTRUCTURED = discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED
    WEBSITE_ADVANCED = enum.auto()


class SearchOptions:
    """Options for Vertex AI Search Requests.

    Attributes:
        page_size (int): Number of results to return per page.
        order_by (str): Field to order the search results by.
        filter_ (str): Filter to apply to the search results.
        safe_search (bool): Whether to enable safe search.
        relevance_threshold (RelevanceThreshold): Relevance threshold for
            the search results.
    """

    page_size: Optional[int] = None
    order_by: Optional[str] = None
    filter_: Optional[str] = None
    safe_search: Optional[bool] = None
    relevance_threshold: Optional[RelevanceThreshold] = None


class Excerpt:
    """Excerpt of Search Result for Vertex AI Search."""

    type_: str
    content: str
    html_content: Optional[str] = None
    page_number: Optional[str] = None

    def __init__(
        self,
        type_: str,
        content: str,
        html_content: Optional[str] = None,
        page_number: Optional[str] = None,
    ):
        self.type_ = type_
        self.content = content
        self.html_content = html_content
        self.page_number = page_number


class SearchResult:
    """Result of a Vertex AI Search Request."""

    id: str
    name: str
    title: str
    link: str
    excerpts: list[Excerpt]

    html_title: Optional[str] = None
    html_formatted_url: Optional[str] = None
    formatted_url: Optional[str] = None
    display_link: Optional[str] = None

    page_map: Optional[dict[str, Any]] = None

    def __init__(self, document: discoveryengine.Document):
        self.id = document.id
        self.name = document.name

        derived_struct_data = dict(document.derived_struct_data)
        self.title = derived_struct_data.get("title")
        self.uri = derived_struct_data.get("link")
        self.excerpts = []

        extractive_answers = derived_struct_data.get("extractive_answers")
        if extractive_answers:
            self.excerpts.extend(
                [
                    Excerpt(
                        page_number=a.get("pageNumber"),
                        content=a.get("content"),
                        type_="extractive_answer",
                    )
                    for a in extractive_answers
                ]
            )

        snippets = derived_struct_data.get("snippets")
        if snippets:
            self.excerpts.extend(
                [
                    Excerpt(
                        content=s.get("snippet"),
                        html_content=s.get("htmlSnippet"),
                        type_="snippet",
                    )
                    for s in snippets
                ]
            )

        self.html_title = derived_struct_data.get("htmlTitle")
        self.html_formatted_url = derived_struct_data.get("htmlFormattedUrl")
        self.formatted_url = derived_struct_data.get("formattedUrl")
        self.display_link = derived_struct_data.get("displayLink")
        self.page_map = dict(derived_struct_data.get("pagemap"))


def _collection_name(project: str, location: str) -> str:
    """Returns the full resource name starting with projects/ given a project and location."""
    return f"projects/{project}/locations/{location}/collections/default_collection"


def _get_data_store_client() -> discoveryengine.DataStoreServiceClient:
    """Create the Data Store client."""
    return aiplatform_initializer.global_config.create_client(
        client_class=discoveryengine.DataStoreServiceClient,
        location_override=aiplatform_initializer.global_config.search_location,
        api_base_path_override=constants.DISCOVERYENGINE_API_BASE_PATH,
    )


def _get_engine_client() -> discoveryengine.EngineServiceClient:
    """Create the Engine client."""
    return aiplatform_initializer.global_config.create_client(
        client_class=discoveryengine.EngineServiceClient,
        location_override=aiplatform_initializer.global_config.search_location,
        api_base_path_override=constants.DISCOVERYENGINE_API_BASE_PATH,
    )


class DataStore:
    r"""Data Store for Vertex AI Search."""

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
            r"dataStores\/(?P<data_store>[a-z0-9][a-z0-9-_]*)"
        )
        match = re.match(pattern, data_store_id)

        if match:
            self._project = match.group("project")
            self._location = match.group("location")
            self._data_store_id = match.group("data_store")
        else:
            self._project = aiplatform_initializer.global_config.project
            self._location = aiplatform_initializer.global_config.search_location
            self._data_store_id = data_store_id

    @property
    def _data_store_client(self) -> discoveryengine.DataStoreServiceClient:
        # Switch to @functools.cached_property once its available.
        if not getattr(self, "_data_store_client_value", None):
            self._data_store_client_value = _get_data_store_client()
        return self._data_store_client_value

    @property
    def _site_search_engine_client(
        self,
    ) -> discoveryengine.SiteSearchEngineServiceClient:
        # Switch to @functools.cached_property once its available.
        if not getattr(self, "_site_search_engine_client_value", None):
            self._site_search_engine_client_value = aiplatform_initializer.search_config.create_client(
                client_class=discoveryengine.SiteSearchEngineServiceClient,
                location_override=aiplatform_initializer.global_config.search_location,
                api_base_path_override=constants.DISCOVERYENGINE_API_BASE_PATH,
            )
        return self._site_search_engine_client_value

    @property
    def _document_client(self) -> discoveryengine.DocumentServiceClient:
        # Switch to @functools.cached_property once its available.
        if not getattr(self, "_document_client_value", None):
            self._document_client_value = aiplatform_initializer.search_config.create_client(
                client_class=discoveryengine.DocumentServiceClient,
                location_override=aiplatform_initializer.global_config.search_location,
                api_base_path_override=constants.DISCOVERYENGINE_API_BASE_PATH,
            )
        return self._document_client_value

    @property
    def _gapic_data_store(self) -> discoveryengine.DataStore:
        return self._data_store_client.get_data_store(name=self._data_store_name)

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
        *,
        data_store_id: str,
        display_name: str,
        data_type: DataType,
    ) -> "DataStore":
        """Creates a Data Store.

        Args:
            data_store_id (str): ID or full resource name of the data store.
            display_name (str): Display name of the data store.
            data_type (DataType): Data type of the data store. Options: WEBSITE, STRUCTURED, UNSTRUCTURED, WEBSITE_ADVANCED.

        Returns:
            DataStore
        """
        data_store = cls(data_store_id)

        gapic_data_store = discoveryengine.DataStore(
            name=data_store._data_store_name,
            display_name=display_name,
            industry_vertical=discoveryengine.IndustryVertical.GENERIC,
            solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
            content_config=data_type.value,
        )

        operation = data_store._data_store_client.create_data_store(
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
        client = _get_data_store_client()
        request = discoveryengine.ListDataStoresRequest(
            parent=_collection_name(
                aiplatform_initializer.global_config.project,
                aiplatform_initializer.global_config.search_location,
            )
        )
        while True:
            pager = client.list_data_stores(request=request)
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
            operation = self._site_search_engine_client.create_target_site(
                parent=f"{self._data_store_name}/siteSearchEngine",
                target_site=data_source,
            )
        else:
            operation = self._document_client.import_documents(
                request=discoveryengine.ImportDocumentsRequest(
                    name=self._branch_name,
                    **{_import_document_map[type(data_source)]: data_source},
                    reconciliation_mode=reconciliation_mode,
                )
            )
        # TODO: Handle Operation Result and Metadata - Return to user
        operation.result()

    def delete(self) -> None:
        operation = self._data_store_client.delete_data_store(
            name=self._data_store_name
        )
        try:
            operation.result()
        except exceptions.GoogleAPICallError:
            pass

    def purge(self, filter_: str = "*", force: bool = False) -> None:
        """Remove all data from the Data Store."""
        operation = self._document_client.purge_documents(
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
            self._project = aiplatform_initializer.global_config.project
            self._location = aiplatform_initializer.global_config.search_location
            self._app_id = app_id

    @property
    def _collection_name(self) -> str:
        """Returns the full resource name starting with projects/ given a project and location."""
        return _collection_name(self._project, self._location)

    @property
    def _engine_client(self) -> discoveryengine.EngineServiceClient:
        # Switch to @functools.cached_property once its available.
        if not getattr(self, "_engine_client_value", None):
            self._engine_client_value = _get_engine_client()
        return self._engine_client_value

    @property
    def _search_client(self) -> discoveryengine.SearchServiceClient:
        # Switch to @functools.cached_property once its available.
        if not getattr(self, "_search_client_value", None):
            self._search_client_value = aiplatform_initializer.search_config.create_client(
                client_class=discoveryengine.SearchServiceClient,
                location_override=aiplatform_initializer.global_config.search_location,
                api_base_path_override=constants.DISCOVERYENGINE_API_BASE_PATH,
            )
        return self._search_client_value

    @property
    def _conversational_search_client(
        self,
    ) -> discoveryengine.ConversationalSearchServiceClient:
        # Switch to @functools.cached_property once its available.
        if not getattr(self, "_conversational_search_client_value", None):
            self._conversational_search_client_value = aiplatform_initializer.search_config.create_client(
                client_class=discoveryengine.ConversationalSearchServiceClient,
                location_override=aiplatform_initializer.global_config.search_location,
                api_base_path_override=constants.DISCOVERYENGINE_API_BASE_PATH,
            )
        return self._conversational_search_client_value

    @property
    def _gapic_engine(self) -> discoveryengine.Engine:
        return self._engine_client.get_engine(name=self._engine_name)

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
        *,
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
            industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        )

        operation = app._engine_client.create_engine(
            parent=app._collection_name,
            engine=gapic_engine,
            engine_id=app._app_id,
        )

        operation.result()
        return app

    @classmethod
    def list_apps(cls) -> Iterator["App"]:
        """Returns an iterator of Apps."""
        client = _get_engine_client()
        request = discoveryengine.ListEnginesRequest(
            parent=_collection_name(
                aiplatform_initializer.global_config.project,
                aiplatform_initializer.global_config.search_location,
            )
        )
        while True:
            pager = client.list_engines(request=request)
            for response in pager:
                yield App(app_id=response.name)

            if not pager.next_page_token:
                break
            request.page_token = pager.next_page_token

    def search(
        self,
        query: str,
        search_options: Optional[SearchOptions] = None,
    ) -> Iterator[SearchResult]:
        r"""Performs a search query.

        Args:
            query (str): Text query.
            search_options (SearchOptions): Optional. Options for the search request.
        Yields:
            discoveryengine.SearchResponse
        """
        if search_options is None:
            search_options = SearchOptions()

        request = discoveryengine.SearchRequest(
            serving_config=self._serving_config_name,
            query=query,
            page_size=search_options.page_size,
            order_by=search_options.order_by,
            filter=search_options.filter_,
            safe_search=search_options.safe_search,
            relevance_threshold=search_options.relevance_threshold,
        )

        while True:
            pager = self._search_client.search(request=request)
            for response in pager:
                for result in response.results:
                    yield SearchResult(
                        document=result.document,
                    )

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
        return self._conversational_search_client.answer_query(
            request=discoveryengine.AnswerQueryRequest(
                serving_config=self._serving_config_name,
                query=discoveryengine.Query(text=query),
                **kwargs,
            )
        )

    def delete(self) -> None:
        r"""Deletes the App."""
        operation = self._engine_client.delete_engine(name=self._engine_name)
        try:
            operation.result()
        except exceptions.GoogleAPICallError:
            pass

    def __repr__(self) -> str:
        return repr(self._gapic_engine)
