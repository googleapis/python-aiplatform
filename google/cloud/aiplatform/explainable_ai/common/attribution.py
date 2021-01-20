# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Attribution classes that contain input attributions..

Explainer class returns the Attribution object below.
"""
import abc
import base64
import collections
import gzip
import json

import numpy as np

from google.cloud.aiplatform.explainable_ai.common import constants

# Keys expected to be populated in the returned attribution object.
OUTPUT_NAME = "output_name"
BASELINE_SCORE = "baseline_score"
EXAMPLE_SCORE = "example_score"
LABEL_INDEX = "label_index"
LABEL_NAME = "label_name"
ATTRIBUTIONS = "attributions"
APPROX_ERROR = "approx_error"

# Keys for debug information expected to be populated in the returned
# attribution object, if debug information is requested by the user.
DEBUG_RAW_ATTRIBUTION_DICT = "debug_raw_attribution_dict"
DEBUG_INPUT_VALUES = "debug_input_values"

# Keys for compressed attrs dict expected to be populated in the returned
# attribution object, if requested by the user.
COMPRESSED_ATTRS_DICT = "compressed_attrs_dict"

ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})


def _convert_dict_to_numpy_types(obj):
    """Converts data in a dict into corresponding numpy types.

  Args:
    obj: a dict that has been decoded from a json str.

  Returns:
    An updated dict with certain types of values being converted
    to numpy types (int, float, and list).
  """

    if isinstance(obj, dict):
        for key in obj:
            if isinstance(obj[key], int):
                obj[key] = np.int32(obj[key])
            elif isinstance(obj[key], float):
                obj[key] = np.float64(obj[key])
            elif isinstance(obj[key], list):
                obj[key] = np.asarray(obj[key], dtype=np.float64)
            elif isinstance(obj[key], dict):
                obj[key] = _convert_dict_to_numpy_types(obj[key])

    return obj


def _compress_attrs_dict(attrs_dict):
    """Compresses an attribution dict and return it in b64 str.

  Args:
    attrs_dict: an attribution dict.

  Returns:
    A str for compressed attributions.
  """
    attrs_json = json.dumps(attrs_dict, sort_keys=True, cls=_NumpyEncoder)
    byte_json = bytes(attrs_json, "utf-8")
    gzipped = gzip.compress(byte_json)
    return base64.b64encode(gzipped).decode("utf-8")


def _decompress_attrs_dict(compressed_attrs_dict):
    """Decompress compressed attributions back to attrs dicts.

  Args:
    compressed_attrs_dict: a str represents compressed attrs dicts.

  Returns:
    A decompressed attrs dict.
  """
    decoded_str = base64.b64decode(compressed_attrs_dict)
    unzipped_str = gzip.decompress(decoded_str)
    unzipped_dict = json.loads(unzipped_str.decode("utf-8"))
    attrs_dict = _convert_dict_to_numpy_types(unzipped_dict)

    return attrs_dict


class _NumpyEncoder(json.JSONEncoder):
    """Convert numpy to list if we see a numpy array during json encoding."""

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if np.issubdtype(type(obj), np.number):
            return obj.item()  # convert most primitive np types to py-native types.
        if isinstance(obj, bytes):
            return obj.decode("utf-8")
        return json.JSONEncoder.default(self, obj)


class _NumpyDecoder(json.JSONDecoder):
    """Convert list to numpy if we see a list during json decoding."""

    def __init__(self, *args, **kargs):
        super(_NumpyDecoder, self).__init__(
            object_hook=_convert_dict_to_numpy_types, *args, **kargs
        )


class Attribution(object):
    """Attribution data-holder class for a single example and a single class.

  Library receives input examples in the form of a list of dict objects.
  Internally, it converts the list of a single, batched dict to make attribution
  calculations. It, then, breaks the batch to return a list of Attributions.
  """

    def __init__(
        self,
        output_name,
        baseline_score,
        example_score,
        values_dict=None,
        attrs_dict=None,
        label_index=None,
        processed_attrs_dict=None,
        approx_error=None,
        label_name=None,
    ):
        """Returns an Attribution  object.

    Args:
      output_name: Name of the explained output.
      baseline_score: Model score for the baseline input.
      example_score: Model score for the given data point.
      values_dict: A dictionary for input values. From feature names to
        np.array.
        None if the Attribution object is constructed from service returned
        json or dict.
      attrs_dict: A dictionary for attributions. From feature
        names to np.array.
        None if the Attribution object is constructed from service returned
        json or dict.
      label_index: Index of the output we are generating. This can be a tuple if
        the output we're explaining is nD array where n > 1. label_index can be
        None if there's only a scalar output like regression.
      processed_attrs_dict: Additional dict comprising post processed data
        generated from attributions in attr_dict. (Optional)
      approx_error: A numeric value reflecting the approximation error of the
        attribution method. The value can be calculated differently for
        different methods but should provide insights for user to tweak the
        method's parameters.
      label_name: The friendly name of label, corresponding to label_index
        above.
    """
        self._output_name = output_name
        self._baseline_score = baseline_score
        self._example_score = example_score
        self._values_dict = values_dict
        self._attrs_dict = attrs_dict
        self._approx_error = approx_error
        if processed_attrs_dict is None:
            processed_attrs_dict = attrs_dict  # No PostProcessor, consider it a no-op
        self._processed_attrs_dict = processed_attrs_dict
        if label_index is not None and isinstance(label_index, tuple):
            if len(label_index) == 1:
                label_index = label_index[0] if label_index[0] >= 0 else None
        if label_index is None:
            label_index = constants.SCALAR_OUTPUT_INDEX  # non multi-class model.
        self._label_index = label_index
        self._label_name = label_name

    def __repr__(self):
        return str(self.__dict__)

    @property
    def baseline_score(self):
        return self._baseline_score

    @property
    def output_name(self):
        return self._output_name

    @property
    def example_score(self):
        return self._example_score

    @property
    def attrs_dict(self):
        return self._attrs_dict

    @property
    def values_dict(self):
        return self._values_dict

    @property
    def label_index(self):
        return self._label_index

    @property
    def label_name(self):
        return self._label_name

    @property
    def approx_error(self):
        return self._approx_error

    @property
    def post_processed_attributions(self):
        return self._processed_attrs_dict

    def _get_attributions_dict(self):
        """Returns sanitized, structured attributions dict keyed by feature name."""
        ret = {}
        for feature_name, attrs in self.post_processed_attributions.items():
            # Sanitize the pretty-formatted to_dict output for images.
            # We'll remove all other entries except for B64_JPEG which holds the
            # visualized image output.
            if isinstance(attrs, dict) and constants.B64_JPEG in attrs:
                ret[feature_name] = {constants.B64_JPEG: attrs[constants.B64_JPEG]}
            else:
                ret[feature_name] = attrs
        return ret

    def to_dict(self, debug=False, include_compressed_attrs_dict=False):
        """Returns a dict of this attribution.

    Args:
      debug: Whether to include debug information in the returned
        dictionary.
      include_compressed_attrs_dict: Whether to include compressed attrs dict.
    """
        ret = {
            OUTPUT_NAME: self.output_name,
            BASELINE_SCORE: self.baseline_score,
            EXAMPLE_SCORE: self.example_score,
            LABEL_INDEX: self.label_index,
            LABEL_NAME: self.label_name,
            ATTRIBUTIONS: self._get_attributions_dict(),
            APPROX_ERROR: self.approx_error,
        }
        # If debug information is requested, we'll add the original input values,
        # raw attributions (in addition to post_processed values) and full
        # post processor output.
        if debug:
            ret[DEBUG_INPUT_VALUES] = self.values_dict
            ret[DEBUG_RAW_ATTRIBUTION_DICT] = self.attrs_dict
            ret[ATTRIBUTIONS] = self.post_processed_attributions

        if include_compressed_attrs_dict:
            ret[COMPRESSED_ATTRS_DICT] = _compress_attrs_dict(self.attrs_dict)

        return {key: val for key, val in ret.items() if val is not None}

    @classmethod
    def from_dict(cls, attrs_obj_dict):
        """Construct the Attribution class from a dict returned by the service.

    Args:
      attrs_obj_dict: a dict returned by the service.

    Returns:
      An Attribution object.
    """

        # Make sure the dict has been converted into numpy types
        if not isinstance(attrs_obj_dict, np.float64):
            attrs_obj_dict = _convert_dict_to_numpy_types(attrs_obj_dict)

        # The following are required fields
        output_name = attrs_obj_dict[OUTPUT_NAME]
        baseline_score = attrs_obj_dict[BASELINE_SCORE]
        example_score = attrs_obj_dict[EXAMPLE_SCORE]
        processed_attrs_dict = attrs_obj_dict[ATTRIBUTIONS]

        # The following are optional fields
        label_index = attrs_obj_dict.get(LABEL_INDEX)
        label_name = attrs_obj_dict.get(LABEL_NAME)
        approx_error = attrs_obj_dict.get(APPROX_ERROR)

        # Dicts that come from the debug flag
        values_dict = attrs_obj_dict.get(DEBUG_INPUT_VALUES)
        attrs_dict = attrs_obj_dict.get(DEBUG_RAW_ATTRIBUTION_DICT)

        # Extract the attrs dict if we don't already have it and the
        # compressed one is available.
        if attrs_dict is None and COMPRESSED_ATTRS_DICT in attrs_obj_dict:
            attrs_dict = _decompress_attrs_dict(attrs_obj_dict[COMPRESSED_ATTRS_DICT])

        return cls(
            output_name,
            baseline_score,
            example_score,
            values_dict,
            attrs_dict,
            label_index,
            processed_attrs_dict,
            approx_error,
            label_name,
        )

    def to_json(self, debug=False, include_compressed_attrs_dict=False):
        """Returns a string JSON representation of this attribution.

    Args:
      debug(bool): Whether to include debug information in the returned JSON
        string.
      include_compressed_attrs_dict: Whether to include compressed attrs dict.
    """
        ret_sanitized = self.to_dict(debug, include_compressed_attrs_dict)
        return json.dumps(ret_sanitized, sort_keys=True, cls=_NumpyEncoder)

    @classmethod
    def from_json(cls, attrs_obj_json):
        """Construct the Attribution class from a json str returned by the service.

    Args:
      attrs_obj_json: a json str returned by the service.

    Returns:
      An Attribution object.
    """
        attrs_obj_dict = json.loads(attrs_obj_json, cls=_NumpyDecoder)
        return cls.from_dict(attrs_obj_dict)

    def feature_importance(self, input_names=None):
        """Derive feature importance value of each feature from attributions.

    If a feature attribution is not a scalar (e.g., RGB channels, embeddings),
    the value is the sum of attribution values in all dimensions.

    Args:
      input_names: List of input names for getting feature importance. If not
        given, will return feature attributions of all float arrays.

    Returns:
      A dictionary of features and corresponding feature importance value.
    """
        importance_dict = {}

        for key, value in self.as_tensors(input_names).items():
            importance_dict[key] = float(np.sum(value))

        return importance_dict

    def as_tensors(self, input_names=None):
        """Return a dict of each feature and the corresponding attribution tensors.

    Unlike the feature_importance method, this method does not aggregate the
    attributions, it keeps the attributions in the shape of their original
    dimensions.

    Args:
      input_names: List of input names for getting feature importance. If not
        given, will return feature attributions of all float arrays.

    Returns:
      A dictionary of features and corresponding feature attribution tensors
    """
        tensors_dict = {}

        if not input_names:
            input_names = self.post_processed_attributions.keys()

        for input_name in input_names:
            if input_name in self.post_processed_attributions:
                val = np.array(self.post_processed_attributions[input_name])

                # Filter attributions to exclude b64 strings.
                if val.dtype in [np.dtype("float32"), np.dtype("float64")]:
                    tensors_dict[input_name] = val.copy()

        return tensors_dict


class LabelIndexToAttribution(collections.abc.Mapping):
    """Immutable Dict that holds Attribution object with label index as key.
  """

    def __init__(self, attributions):
        self._data = dict()

        if attributions:
            for attr in attributions:
                self._data[attr.label_index] = attr

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def get_top_k_label_index_list(self, k=1):
        """Returns top k label index in a list (sorted by example scores).

    Args:
      k: Number of top classes to return. Default k=1.
        k=None returns all classes
    """
        sorted_attr_list = sorted(
            self._data.keys(),
            key=lambda idx: self._data[idx].example_score,
            reverse=True,
        )

        return sorted_attr_list[:k]

    def to_dict(self, debug=False, include_compressed_attrs_dict=False):
        """Returns a dictionary mapping label index to attribution dict.

    Args:
      debug(bool): Whether to include debug information in the returned JSON
        string.
      include_compressed_attrs_dict: Whether to include compressed attrs dict.
    """
        ret = {}
        for key, val in self._data.items():
            if val:
                val_dict = val.to_dict(debug, include_compressed_attrs_dict)
                if val_dict:
                    ret[str(key)] = val_dict
        return ret

    def to_list(self, debug=False, include_compressed_attrs_dict=False):
        """Returns list representation of the attributions sorted by example scores.

    Args:
      debug: Whether to include debug information in the returned JSON
        string.
      include_compressed_attrs_dict: Whether to include compressed attrs dict.
    """
        # k=None gets all items
        sorted_label_index_list = self.get_top_k_label_index_list(k=None)
        return [
            self._data[label_index].to_dict(debug, include_compressed_attrs_dict)
            for label_index in sorted_label_index_list
        ]

    def to_json(self, debug=False, include_compressed_attrs_dict=False):
        """Returns a string JSON representation of this LabelIndexToAttribution.

    Since dictionary representation cannot retain the order, we return a list
    of attribution dictionaries instead.

    Args:
      debug: Whether to include debug information in the returned JSON
        string.
      include_compressed_attrs_dict: Whether to include compressed attrs dict.
    """
        return json.dumps(
            self.to_list(debug, include_compressed_attrs_dict), cls=_NumpyEncoder
        )

    @classmethod
    def from_list(cls, attr_dict_list):
        """Creating a LabelIndexToAttribution instance from a list.

    Args:
      attr_dict_list: A list of attribution dict.

    Returns:
      A LabelIndexToAttribution instance
    """
        attr_obj_list = []
        for attr_dict in attr_dict_list:
            attr_obj = Attribution.from_dict(attr_dict)
            attr_obj_list.append(attr_obj)

        return cls(attr_obj_list)

    @classmethod
    def from_json(cls, json_str):
        """Creating a LabelIndexToAttribution instance from a json str.

    JsonDecoder cannot handle array conversion direction via object_hook.
    Therefore, we handle it separately in this function without using
    _NumpyDecoder.

    Args:
      json_str: A string of list of attribution json.

    Returns:
      A LabelIndexToAttribution instance
    """
        attr_dict_list = json.loads(json_str)

        return cls.from_list(attr_dict_list)
