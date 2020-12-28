from typing import Optional, Dict
import abc
from google.cloud.aiplatform import schema
from google.cloud.aiplatform_v1beta1 import ImportDataConfig
from google.cloud.aiplatform_v1beta1 import GcsSource


class Datasource(abc.ABC):
    @property
    def dataset_metadata(self) -> Optional[Dict]:
        raise NotImplementedError


class DatasourceImportable(abc.ABC):
    """An abstract class that provides import_data_config for importing data to an existing dataset"""

    @property
    def import_data_config(self) -> ImportDataConfig:
        raise NotImplementedError


class TabularDatasource(Datasource):
    def __init__(self, gcs_source_uri: Optional[str], bq_source_uri: Optional[str]):
        if gcs_source_uri and bq_source_uri:
            raise ValueError("Only one of gcs_source_uri or bq_source_uri can be set.")

        if not any([gcs_source_uri, bq_source_uri]):
            raise ValueError("One of gcs_source_uri or bq_source_uri must be set.")

        dataset_metadata = None
        if gcs_source_uri:
            dataset_metadata = {"input_config": {"gcs_source": {"uri": gcs_source_uri}}}
        elif bq_source_uri:
            dataset_metadata = {
                "input_config": {"bigquery_source": {"uri": bq_source_uri}}
            }

        self._dataset_metadata = dataset_metadata

    @property
    def dataset_metadata(self) -> Optional[Dict]:
        return self._dataset_metadata


class EmptyNonTabularDatasource(Datasource):
    def __init__(self):
        pass

    @property
    def dataset_metadata(self) -> Optional[Dict]:
        return None


class NonTabularDatasource(Datasource, DatasourceImportable):
    def __init__(
        self,
        gcs_source_uris: Sequence[str],
        import_schema_uri: str,
        data_items_labels: Optional[Dict] = None,
    ):
        self._gcs_source_uris = gcs_source_uris
        self._import_schema_uri = import_schema_uri
        self._data_items_labels = data_items_labels

    @property
    def dataset_metadata(self) -> Optional[Dict]:
        return None

    @property
    def import_data_config(self) -> ImportDataConfig:
        return ImportDataConfig(
            gcs_source=GcsSource(uris=self._gcs_source_uris),
            import_schema_uri=self._import_schema_uri,
            data_item_labels=self._data_items_labels,
        )

