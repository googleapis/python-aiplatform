
FeatureValueType = Union[
    ValueType.VALUE_TYPE_UNSPECIFIED,
    ValueType.BOOL,
    ValueType.BOOL_ARRAY,
    ValueType.DOUBLE,
    ValueType.DOUBLE_ARRAY,
    ValueType.INT64,
    ValueType.INT64_ARRAY,
    ValueType.STRING,
    ValueType.STRING_ARRAY,
    ValueType.BYTES
]

class Featurestore(base.VertexAiResourceNounWithFutureManager):
  """Managed featurestore resource for Vertex AI."""

  client_class = utils.FeaturestoreClientWithOverride

  _is_client_prediction_client = False
  _resource_noun = "featurestores"
  _getter_method = "get_featurestore"
  _list_method = "list_featurestores"
  _delete_method = "delete_featurestore"

  def __init__(self,
      featurestore_name: str,
      project: Optional[str] = None,
      location: Optional[str] = None,
      credentials: Optional[auth_credentials.Credentials] = None,
  ):
    """"""

  @classmethod
  def create(cls,
      id: str,
      online_serving_fixed_node_count: Optional[int], # is there a default value?
      labels: Optional[Dict[str, str]] = None,
      project: Optional[str] = None,
      location: Optional[str] = None,
      credentials: Optional[auth_credentials.Credentials] = None,
      encryption_spec_key_name: Optional[str] = None,
  ) -> "Featurestore":
    """"""

  def update(self,
      online_serving_fixed_node_count: Optional[int] = None,
      labels: Optional[Dict[str, str]] = None,
  ) -> "Featurestore":
    """"""

  def get_entity_type(self, id: str) -> "EntityType":
    """"""

  def create_entity_type(self,
      id: str,
      description: Optional[str] = None,
      labels: Optional[Dict[str, str]] = None,
      snapshot_analysis_disabled: Optional[bool] = True,
      monitoring_interval: Optional[int] = None,
      monitoring_interval_days: Optional[int] = None,
  ) -> "EntityType":
    """"""

  def list_entity_types(self, ids: List(str)) -> List["EntityType"]:
    """"""

  def delete_entity_types(self, ids: List(str)):
    """"""

  def batch_serve(self,
      entity_type_ids: List[str],
      destination_feature_mappings: Optional[List["FeatureMapping"]],
      df_read_instance: Optional[DataFrame] = None,
      df_read_instance_time: Optional[Timestamp] = None,
      bq_read_instance: Optional[str] = None,
      gcs_read_instances: Optional[List[str]] = None,
      pass_through_field: Optional[List[str]] = None,
      bq_destination_output_uri: Optional[str] = None,
      gcs_destination_output_uri_prefix: Optional[str] = None,
      gcs_destination_type: Optional[str] = None,
      df_destination_output: Optional[bool] = False,
  ) -> Optional[DataFrame]:
    """"""

  def search_features(self,
      query: Optional[str] = None,
      location: Optional[str] = None,
  ) -> List["Feature"]:
    """"""

class EntityType(base.VertexAiResourceNounWithFutureManager):
  """Managed entityType resource for Vertex AI."""

  client_class = utils.FeaturestoreClientWithOverride
  online_client_class = utils.FeaturestoreOnlineClientWithOverride

  _is_client_prediction_client = False
  _resource_noun = "entityTypes"
  # `_resource_noun` will update to `featurestores/{featurestore_id}/entityTypes` during class construction"
  _getter_method = "get_entity_type"
  _list_method = "list_entity_types"
  _delete_method = "delete_entity_type"

  def __init__(self,
      featurestore: Union["Featurestore", str],
      entity_type_name: str,
      project: Optional[str] = None,
      location: Optional[str] = None,
      credentials: Optional[auth_credentials.Credentials] = None,
  ):
    """"""

  @classmethod
  def create(cls,
      featurestore: Union["Featurestore", str],
      id: str,
      description: Optional[str] = None,
      labels: Optional[Dict[str, str]] = None,
      snapshot_analysis_disabled: Optional[bool] = True,
      monitoring_interval: Optional[int] = None,
      monitoring_interval_days: Optional[int] = None,
  ) -> "EntityType":
    """"""

  def update(self,
      description: Optional[str] = None,
      labels: Optional[Dict[str, str]] = None,
      snapshot_analysis_disabled: Optional[bool] = None,
      monitoring_interval: Optional[int] = None,
  ) -> "EntityType":
    """"""

  def get_feature(self, id: str) -> "Feature":
    """"""

  def list_features(self, ids: List(str)) -> List["Feature"]:
    """"""

  def delete_features(self, ids: List(str)):
    """"""

  def create_feature(self,
      id: str,
      description: Optional[str] = None,
      labels: Optional[Dict[str, str]] = None,
      snapshot_analysis_disabled: Optional[bool] = True,
      monitoring_interval: Optional[int] = None,
      monitoring_interval_days: Optional[int] = None,
  ) -> "Feature":
    """"""

  def create_features(self,
      feature_configs: Optional[List["FeatureConfig"]] = None,
      source_feature_mapping: Optional["FeatureMapping"] = None,
      df_source: Optional[DataFrame] = None,
      bq_source_uri: Optional[str] = None,
      gcs_source_uris: Optional[List[str]] = None,
      feature_time_field: Optional[str] = None,
      feature_time: Optional[Timestamp] = None,
      entity_id_field: Optional[str] = "entity_id",
      disable_online_serving: Optional[bool] = False,
      worker_count: Optional[int] = 1,
  ):
    """"""

  def ingest(self,
      source_feature_mapping: Optional["FeatureMapping"] = None,
      df_source: Optional[DataFrame] = None,
      bq_source_uri: Optional[str] = None,
      gcs_source_uris: Optional[List[str]] = None,
      feature_time_field: Optional[str] = None,
      feature_time: Optional[google.protobuf.timestamp_pb2.Timestamp] = None,
      entity_id_field: Optional[str] = "entity_id",
      disable_online_serving: Optional[bool] = False,
      worker_count: Optional[int] = 1,
  ):
    """"""

  def read(self,
      entity_ids: List[str],
      feature_ids: Optional[List[str]] = None,
  ) -> List["EntityView"]:
    """"""

  def export(self,
      destination_feature_mapping: Optional["FeatureMapping"] = None,
      snapshot_export_time: Optional[google.protobuf.timestamp_pb2.Timestamp] = None,
      bq_destination_output_uri: Optional[str] = None,
      gcs_destination_output_uri_prefix: Optional[str] = None,
      gcs_destination_type: Optional[str] = None,
      df_destination_output: Optional[bool] = False,
  ) -> Optional[DataFrame]:
    """"""

class Feature(base.VertexAiResourceNounWithFutureManager):
  """Managed feature resource for Vertex AI."""

  client_class = utils.FeaturestoreClientWithOverride
  online_client_class = utils.FeaturestoreOnlineClientWithOverride

  _is_client_prediction_client = False
  _resource_noun = "features"
  _getter_method = "get_feature"
  _list_method = "list_features"
  _delete_method = "delete_feature"

  def __init__(self,
      entity_type: Union["EntityType", str],
      feature_name: str,
      project: Optional[str] = None,
      location: Optional[str] = None,
      credentials: Optional[auth_credentials.Credentials] = None,
  ):
    """"""

  @classmethod
  def create(cls,
      entity_type: Union["EntityType", str],
      id: str,
      value_type: FeatureValueType,
      description: Optional[str] = None,
      labels: Optional[Dict[str, str]] = None,
      snapshot_analysis_disabled: Optional[bool] = True,
      monitoring_interval: Optional[int] = None,
      monitoring_interval_days: Optional[int] = None,
  ) -> "Feature":
    """"""

  def update(self,
      description: Optional[str] = None,
      labels: Optional[Dict[str, str]] = None,
      snapshot_analysis_disabled: Optional[bool] = None,
      monitoring_interval: Optional[int] = None,
  ) -> "Feature":
    """"""

class FeatureConfig(NamedTuple):
  """Managed feature resource for Vertex AI."""

  feature_id: str
  value_type: FeatureValueType
  description: str = None
  labels: Dict[str, str] = None
  snapshot_analysis_disabled: bool = True
  monitoring_interval: int = None
  monitoring_interval_days: int = None

class FeatureMapping(NamedTuple):
  entity_type_id: str
  feature_ids: List[str]
  feature_fields: List[str] = None

FeatureMapping(entity_type_id, feature_ids)
FeatureMapping(entity_type_id, feature_ids, feature_fields)
