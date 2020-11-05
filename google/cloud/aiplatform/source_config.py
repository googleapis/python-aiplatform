from typing import Optional, Dict
from abc import ABC, abstractmethod
from google.cloud.aiplatform import schema
from google.cloud.aiplatform_v1beta1 import ImportDataConfig
from google.cloud.aiplatform_v1beta1 import GcsSource

class DataImportable(ABC):
    """
        An abstract class that provides import_data_config for importing data to an existing database
    """

    @property 
    def import_data_config(self) -> ImportDataConfig:
        raise NotImplementedError
        
class SourceConfig(ABC):
    @property
    def metadata_schema_uri(self) -> str:
        raise NotImplementedError

    @property
    def metadata(self) -> Dict:
        raise NotImplementedError

## TODO: Move to a EmptySourceConfig file
class EmptyNonTabularSourceConfig(SourceConfig):
    def __init__(self, metadata_schema_uri: str):
        """TODO

        Args:
            metadata_schema_uri (str):
                Required. Points to a YAML file stored on Google Cloud Storage
                describing additional information about the Dataset. The schema
                is defined as an OpenAPI 3.0.2 Schema Object. The schema files
                that can be used here are found in gs://google-cloud-
                aiplatform/schema/dataset/metadata/.
        """

        self._metadata_schema_uri = metadata_schema_uri
        
    @property
    def metadata_schema_uri(self) -> str:
        return self._metadata_schema_uri

    @property
    def metadata(self) -> Dict:
        return {}

## TODO: Move to a BQSourceConfig file
class BQTabularSourceConfig(SourceConfig):
    def __init__(self, source_uri: str):
        # TODO: Add doc strings

        # Perform validation of URI
        if not (source_uri.startswith('bq://') or source_uri.startswith('bigquery://')):
            raise ValueError(
                "Expected source_uri to start with 'bq://' or 'bigquery://'"
            )

        self._source_uri = source_uri        

    @property
    def metadata_schema_uri(self) -> str:
        # Always return tabular as BQ only supports tabular
        return schema.dataset.metadata.tabular

    @property
    def metadata(self) -> Dict:
        return {"input_config": {"bigquery_source": {"uri": self._source_uri}}}

## TODO: Move to a GCSSourceConfig file
# Do not instantiate this abstract class
class GCSSourceConfig(SourceConfig):
    def __init__(self, source_uris: [str]):
        # TODO: Add doc strings

        # Perform validation of URI's
        if not all([uri.startswith('gs://') for uri in source_uris]):
            raise ValueError(
                "Expected alls URI's in source_uris to start with 'gs://'"
            )

        self._source_uris = source_uris
        
    @property
    def metadata(self) -> Dict:
        return {"input_config": {"gcs_source": {"uri": self._source_uris}}}

class GCSTabularSourceConfig(GCSSourceConfig):
    @property
    def metadata_schema_uri(self) -> str:
        # Always return tabular as this config only supports tabular
        return schema.dataset.metadata.tabular

class GCSNonTabularSourceConfig(GCSSourceConfig, DataImportable):
    def __init__(self, source_uris: [str], metadata_schema_uri: str, import_schema_uri: str, data_items_labels: Optional[Dict] = None):
        """TODO

        Args:
            source_uris (Sequence[str]):
                Required. Google Cloud Storage URI(-s) to the
                input file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
            metadata_schema_uri (str):
                Required. Points to a YAML file stored on Google Cloud Storage
                describing additional information about the Dataset. The schema
                is defined as an OpenAPI 3.0.2 Schema Object. The schema files
                that can be used here are found in gs://google-cloud-
                aiplatform/schema/dataset/metadata/.
            import_schema_uri (str):
                Required. Points to a YAML file stored on Google Cloud
                Storage describing the import format. Validation will be
                done against the schema. The schema is defined as an
                `OpenAPI 3.0.2 Schema
                Object <https://tinyurl.com/y538mdwt>`__.
            data_item_labels: (Optional[Dict]) = None
                Labels that will be applied to newly imported DataItems. If
                an identical DataItem as one being imported already exists
                in the Dataset, then these labels will be appended to these
                of the already existing one, and if labels with identical
                key is imported before, the old label value will be
                overwritten. If two DataItems are identical in the same
                import data operation, the labels will be combined and if
                key collision happens in this case, one of the values will
                be picked randomly. Two DataItems are considered identical
                if their content bytes are identical (e.g. image bytes or
                pdf bytes). These labels will be overridden by Annotation
                labels specified inside index file refenced by
                [import_schema_uri][google.cloud.aiplatform.v1beta1.ImportDataConfig.import_schema_uri],
                e.g. jsonl file.
        """

        if metadata_schema_uri == schema.dataset.metadata.tabular:
            raise ValueError(
                "Expected non-tabular metadata schema uri. For tabular metadata schema, use GCSTabularSourceConfig"
            )
        
        GCSSourceConfig.__init__(self, source_uris)
        self._metadata_schema_uri = metadata_schema_uri
        self._import_schema_uri = import_schema_uri
        self._data_items_labels = data_items_labels

    @property
    def metadata_schema_uri(self) -> str:
        # Always return tabular as this config only supports tabular
        return self._metadata_schema_uri

    @property
    def metadata(self) -> Dict:
        # Non-tabular datasets shouldn't have any metadata set
        return {}

    @property 
    def import_data_config(self) -> ImportDataConfig:
        return ImportDataConfig(
                gcs_source=GcsSource(uris=self._source_uris),
                import_schema_uri=self._import_schema_uri,
                data_item_labels=self._data_items_labels,
            )