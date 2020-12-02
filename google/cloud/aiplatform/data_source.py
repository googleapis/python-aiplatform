from typing import Optional, Dict
from abc import ABC, abstractmethod
from google.cloud.aiplatform import schema
from google.cloud.aiplatform_v1beta1 import ImportDataConfig
from google.cloud.aiplatform_v1beta1 import GcsSource
        
class DataSource(ABC):
    @property
    def metadata_schema_uri(self) -> str:
        raise NotImplementedError

    @property
    def metadata(self) -> Dict:
        raise NotImplementedError

class EmptyNonTabularDataSource(DataSource):
    """Class for a empty, non-tabular dataset schema that provides Dataset metadata
    
    To be used with the Dataset.create function to create an empty, non-tabular dataset.
    """

    def __init__(self, metadata_schema_uri: str):
        """
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

class BQTabularDataSource(DataSource):
    """Class for a tabular dataset schema that provides Dataset metadata
    
    Used for data stored on BigQuery.
    To be used with the Dataset.create function to import the dataset at creation time.
    """

    def __init__(self, source_uri: str):
        """
        Args:
            source_uris (Sequence[str]):
                Required. Google Cloud Storage URI(-s) to the
                input file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
        """

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

# Do not instantiate this abstract class
class GCSSourceValidating(DataSource):
    """Abstract class that takes in GCS source_uri's and performs validation"""

    def __init__(self, source_uris: [str]):
        """
        Args:
            source_uris (Sequence[str]):
                Required. Google Cloud Storage URI(-s) to the
                input file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
        """

        # Perform validation of URI's
        if not all([uri.startswith('gs://') for uri in source_uris]):
            raise ValueError(
                "Expected alls URI's in source_uris to start with 'gs://'"
            )

        self._source_uris = source_uris
        
# Do not instantiate this abstract class
class GCSDataSource(GCSSourceValidating, DataSource):
    """Abstract class for GCS source_uri's that provides Dataset metadata"""

    @property
    def metadata(self) -> Dict:
        return {"input_config": {"gcs_source": {"uri": self._source_uris}}}

class GCSTabularDataSource(GCSDataSource):
    """Class for a tabular dataset schema that provides Dataset metadata. 
    
    Used for CSV files on Google Cloud Storage.
    To be used with the Dataset.create function to import the dataset at creation time.
    """

    @property
    def metadata_schema_uri(self) -> str:
        # Always return tabular as this config only supports tabular
        return schema.dataset.metadata.tabular

class DataImportable(ABC):
    """An abstract class that provides import_data_config for importing data to an existing database"""

    @property 
    def import_data_config(self) -> ImportDataConfig:
        raise NotImplementedError
    
class GCSNonTabularImportDataSource(GCSSourceValidating, DataImportable):
    """Class for a non-tabular dataset schema that provides import metadata.

    Used for files on Google Cloud Storage.
    To be used with the Dataset.import_data function to import files from Google Cloud Storage to an existing dataset.
    """

    def __init__(self, source_uris: [str], import_schema_uri: str, data_items_labels: Optional[Dict] = None):
        """
        Args:
            source_uris (Sequence[str]):
                Required. Google Cloud Storage URI(-s) to the
                input file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
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

        GCSSourceValidating.__init__(self, source_uris)
        self._import_schema_uri = import_schema_uri
        self._data_items_labels = data_items_labels
        
    @property 
    def import_data_config(self) -> ImportDataConfig:
        return ImportDataConfig(
                gcs_source=GcsSource(uris=self._source_uris),
                import_schema_uri=self._import_schema_uri,
                data_item_labels=self._data_items_labels,
            )

class GCSNonTabularDataSource(GCSDataSource, GCSNonTabularImportDataSource):
    """Class for a non-tabular dataset schema that provides Dataset metadata. 
    
    Used for files on Google Cloud Storage.
    To be used with the Dataset.create function to import data at creation time.
    """

    def __init__(self, source_uris: [str], metadata_schema_uri: str, import_schema_uri: str, data_items_labels: Optional[Dict] = None):
        """
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
                "Expected non-tabular metadata schema uri. For tabular metadata schema, use GCSTabularDataSource"
            )
        
        GCSDataSource.__init__(self, source_uris)
        GCSNonTabularImportDataSource.__init__(self, source_uris, import_schema_uri, data_items_labels)
        self._metadata_schema_uri = metadata_schema_uri

    @property
    def metadata_schema_uri(self) -> str:
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