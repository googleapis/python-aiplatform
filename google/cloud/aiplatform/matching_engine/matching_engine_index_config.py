import abc
from dataclasses import dataclass
import enum

from typing import Optional, Dict

# This file mirrors the configuration options as defined in gs://google-cloud-aiplatform/schema/matchingengine/metadata/nearest_neighbor_search_1.0.0.yaml
class DistanceMeasureType(enum.Enum):
    # Dot Product Distance. Defined as a negative of the dot product
    DOT_PRODUCT_DISTANCE = "DOT_PRODUCT_DISTANCE"
    # Euclidean (L_2) Distance
    SQUARED_L2_DISTANCE = "SQUARED_L2_DISTANCE"
    # Manhattan (L_1) Distance
    L1_DISTANCE = "L1_DISTANCE"
    # Cosine Distance. Defined as 1 - cosine similarity.
    COSINE_DISTANCE = "COSINE_DISTANCE"


class FeatureNormType(enum.Enum):
    # Unit L2 normalization type.
    UNIT_L2_NORM = "UNIT_L2_NORM"
    # No normalization type is specified.
    NONE = "NONE"


class AlgorithmConfig(abc.ABC):
    def as_dict(self) -> Dict:
        pass


@dataclass
class TreeAhConfig(AlgorithmConfig):
    # Number of embeddings on each leaf node. The default value is 1000 if not set.
    leaf_node_embedding_count: Optional[int] = None
    # The default percentage of leaf nodes that any query may be searched. Must be in
    # range 1-100, inclusive. The default value is 10 (means 10%) if not set.
    leaf_nodes_to_search_percent: Optional[float] = None

    def as_dict(self) -> Dict:
        return {
            "treeAhConfig": {
                "leafNodeEmbeddingCount": self.leaf_node_embedding_count,
                "leafNodesToSearchPercent": self.leaf_nodes_to_search_percent,
            }
        }


@dataclass
class BruteForceConfig(AlgorithmConfig):
    def as_dict(self) -> Dict:
        return {"bruteForceConfig": {}}


@dataclass
class MatchingEngineIndexConfig:
    # The number of dimensions of the input vectors.
    dimensions: int

    # The configuration with regard to the algorithms used for efficient search.
    algorithm_config: AlgorithmConfig

    # The default number of neighbors to find via approximate search before exact reordering is
    # performed. Exact reordering is a procedure where results returned by an
    # approximate search algorithm are reordered via a more expensive distance computation.
    # Required if tree-AH algorithm is used.
    approximate_neighbors_count: Optional[int] = None

    # The distance measure used in nearest neighbor search.
    distance_measure_type: Optional[DistanceMeasureType] = None

    def as_dict(self) -> Dict:
        return {
            "dimensions": self.dimensions,
            "algorithmConfig": self.algorithm_config.as_dict(),
            "approximateNeighborsCount": self.approximate_neighbors_count,
            "distanceMeasureType": self.distance_measure_type,
        }

