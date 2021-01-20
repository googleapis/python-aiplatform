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


"""Utilities for explanations for all frameworks.
"""

from __future__ import absolute_import
from __future__ import division

from __future__ import print_function

import base64
import collections
import json
from multiprocessing import pool

import numpy as np
import six
from google.cloud.aiplatform.explainable_ai.common import types

EXPLAIN_OUTPUT_INDEX_TEMPLATE = "explain__index/{}"


class FieldKeys(object):
    @classmethod
    def values(cls):
        return {
            v
            for k, v in cls.__dict__.items()
            if not (k.startswith("__") and k.endswith("__"))
        }


class EvaluatedSparseTensor(object):
    """A data-holder class to contain feed for a single sparse tensor."""

    def __init__(self, values, indices, dense_shape):
        """Initializes EvaluatedSparseTensor with all inputs cast to numpy arrays.

    Args:
      values: Dictionary from values tensor name to sparse values.
      indices: Dictionary from indices tensor name to indices for the values.
      dense_shape: Dictionary from dense_shape tensor name to shape.
    """
        self._values = values
        self._indices = indices
        self._dense_shape = dense_shape

    @property
    def values(self):
        return self._values

    @property
    def indices(self):
        return self._indices

    @property
    def dense_shape(self):
        return self._dense_shape

    def to_dict(self):
        """Returns unified dictionary representation of the feed."""
        sparse_feed = {}
        sparse_feed.update(self.values)
        sparse_feed.update(self.indices)
        sparse_feed.update(self.dense_shape)
        return sparse_feed


def merge_dict(dict1, dict2):
    """Merge two dictionaries into a third dictionary.

  Args:
    dict1: First dictionary to be merged.
    dict2: Second dictionary to be merged.

  Returns:
    A dictionary by merging the two dictionaries. Note that if the two
    dictionary has the same keys the value of the latter dictionary will be
    used.
  """
    res = dict1.copy()
    res.update(dict2)
    return res


def recursive_merge_dict(dict1, dict2):
    """Merge two dictionaries into a third dictionary recursively.

  Args:
    dict1: First dictionary to be merged.
    dict2: Second dictionary to be merged.

  Returns:
    A dictionary by merging the two dictionaries. If any of the values are
    dicts, they will be merged recursively.
  """
    res = dict1.copy()
    for k, v in dict2.items():
        if k in res and isinstance(res[k], dict):
            res[k].update(recursive_merge_dict(res[k], dict2[k]))
        else:
            res[k] = v
    return res


def get_sample_from_batched_tensors(tensors, idx):
    """Collect sample at index idx of a given dictionary or list.

  Args:
    tensors: Rowified or columnarized format of a batch of inputs.
    idx: Index to fetch the batch from
  Returns:
    Same dictionary where idx is chosen from values.
  """
    if isinstance(tensors, list):
        return tensors[idx] if idx < len(tensors) else {}
    return {key: val[idx] for key, val in tensors.items()}


def _check_size_type(a, b):
    """Check if two instances have the same type. Check shape for list, ndarray.

  Args:
    a: Instance to compare with.
    b: Instance to compare with.
  Returns:
    True, if same type and same shape for list, ndarray. False, otherwise.
  """
    a = np.array(a)
    b = np.array(b)
    if not isinstance(a, type(b)):
        return False
    if isinstance(a, np.ndarray):
        return a.shape == b.shape
    return True


def columnarize(instances, keys=None):
    """Columnarize inputs.

  Each line in the input is a dictionary of input names to the value
  for that input (a single instance). For each input "column", this method
  appends each of the input values to a list. The result is a dict mapping
  input names to a batch of input data. This can be directly used as the
  feed dict during prediction.

  For example,

    instances = [{"a": [1.0, 2.0], "b": "a"},
                 {"a": [3.0, 4.0], "b": "c"},
                 {"a": [5.0, 6.0], "b": "e"},]
    batch = utils.columnarize(instances)
    assert batch == {"a": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
                     "b": ["a", "c", "e"]}

  Arguments:
    instances: List of dictionaries where the dictionaries map input names
      to the values for those inputs.
    keys: List of keys that we columnarize. If None, all items will be
      columnarized. If non-empty, keys not in the set will be ignored.

  Returns:
    A dictionary mapping input names to values, as described above.
  """
    columns = {}
    for instance in instances:
        for k, v in six.iteritems(instance):
            if keys is not None and k not in keys:
                continue
            if k not in columns:
                columns[k] = []
            if columns[k] and not _check_size_type(columns[k][-1], v):
                raise ValueError(
                    "All the elements in the dictionary should have"
                    " identical length/shape."
                )
            columns[k].append(v)
    return columns


def concat(instances, keys=None):
    """Concat inputs.

  Each line in the input is a dictionary of input names to the value
  for that input (a single instance). For each input "column", this method
  appends each of the input values to a list and then concatenate.
  The result is a dict mapping input names to a batch of input data.
  This can be directly used as the feed dict during prediction. The values of
  the instances can only be a list or 1d array.

  For example,

    instances = [{"a": [1.0, 2.0], "b": ["a"]},
                 {"a": [3.0, 4.0], "b": ["c"]},
                 {"a": [5.0, 6.0], "b": ["e"]},]
    batch = utils.concat(instances)
    assert batch == {"a": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
                     "b": ["a", "c", "e"]}

  Arguments:
    instances: List of dictionaries where the dictionaries map input names
      to the values for those inputs.
    keys: List of keys that we concat. If None, all items will be concatenated.
      If non-empty, keys not in the set will be ignored.

  Returns:
    A dictionary mapping input names to values, as described above.
  """
    columns = {}
    for instance in instances:
        for k, v in instance.items():
            if keys is not None and k not in keys:
                continue
            if k not in columns:
                columns[k] = []
            if not isinstance(v, (np.ndarray, list)):
                raise ValueError(
                    "Values to be concatenated should be an array. " "Got: %s." % v
                )
            columns[k].extend(v)
    return columns


def rowify(columns):
    """Converts columnar input to row data.

  We treat the first dimension of each input tensor as `batch` dimension and
  and break into single instance based on the `batch` dimension.

  Consider the following code:

    columns = {"prediction": np.array([1,             # 1st instance
                                       0,             # 2nd
                                       1]),           # 3rd
               "scores": np.array([[0.1, 0.9],        # 1st instance
                                   [0.7, 0.3],        # 2nd
                                   [0.4, 0.6]])}      # 3rd

  Then rowify will return the equivalent of:

    [{"prediction": 1, "scores": [0.1, 0.9]},
     {"prediction": 0, "scores": [0.7, 0.3]},
     {"prediction": 1, "scores": [0.4, 0.6]}]

  Arguments:
    columns: (dict) mapping names to numpy arrays, where the arrays
      contain a batch of data.

  Raises:
    PredictionError: if the outer dimension of each input isn't identical
    for each of element.

  Returns:
    A list of a single instance dictionary mapping input names to values.
  """
    result = []
    if not columns:
        return result  # Empty row.

    # Make sure columns are ndarrays.
    columns = {key: np.array(value) for (key, value) in columns.items()}
    sizes_set = {e.shape[0] for e in six.itervalues(columns)}

    # All the elements in the length array should be identical. Otherwise,
    # raise an exception.
    if len(sizes_set) > 1:
        sizes_dict = {name: e.shape[0] for name, e in six.iteritems(columns)}
        raise ValueError(
            "All the elements in the length array should be identical."
            " See the inputs and their size: %s." % sizes_dict
        )

    # Pick an arbitrary value in the map to get its size.
    num_instances = len(next(six.itervalues(columns)))
    for row in six.moves.xrange(num_instances):
        result.append(
            {
                name: output[row, Ellipsis].tolist()
                for name, output in six.iteritems(columns)
            }
        )
    return result


def split_feeds(dense_feed, sparse_feed, side_feed, max_batch_size):
    """Splits given feeds into smaller batches and returns unified subbatches.

  Args:
    dense_feed: A dictionary from tensor names to values representing dense
      tensors.
    sparse_feed: A list of EvaluatedSparseTensor instances containing values,
      indices, and dense_shape of sparse tensors.
    side_feed: A dictionary from tensor names to values for side inputs to the
      model. Currently, they are assumed to be dense and handled the same way.
    max_batch_size: Maximum batch size to split to. If it is zero, no split is
      performed.

  Returns:
    A list of dictionaries from tensor names to values. Each dictionary is
      directly feedable to the model.
  """
    if max_batch_size < 0:
        raise ValueError("Batch size cannot be negative.")
    if dense_feed:
        actual_size = len(next(six.itervalues(dense_feed)))
    elif side_feed:
        actual_size = len(next(six.itervalues(side_feed)))
    elif sparse_feed:
        # Infers the size from the dense shape of the first EvaluatedSparseTensor
        actual_size = next(six.itervalues(sparse_feed[0].dense_shape))[0]
    else:
        return [{}]

    if not max_batch_size:
        max_batch_size = actual_size

    dense_feeds = _split_dense_feed(dense_feed, actual_size, max_batch_size)
    side_feeds = _split_dense_feed(side_feed, actual_size, max_batch_size)
    sparse_sub_feeds = split_sparse_feed(sparse_feed, actual_size, max_batch_size)
    subbatch_count = actual_size // max_batch_size
    if actual_size % max_batch_size != 0:
        subbatch_count += 1
    return unify_subbatches(dense_feeds, sparse_sub_feeds, side_feeds, subbatch_count)


def unify_subbatches(dense_feeds, sparse_feeds, side_feeds, size):
    """Unifies given subbatch feeds to a single list of subbatch feeds.

  This function unifies subbatches of dense, side and sparse feeds, which were
  split separately, into a single list of subbatches. An example input would be
  as follows:

  (dense_feeds=[{'a': 1, 'x': 3}, {'a': 2, 'x': 5}],
   sparse_feeds=[[EvaluatedSparseTensor({'v': 0}, {'i': 0}, {'d': 0}),
                  EvaluatedSparseTensor({'v': 1}, {'i': 1}, {'d': 1})],
                 [EvaluatedSparseTensor({'v2': 2}, {'i2': 2}, {'d2': 2}),
                  EvaluatedSparseTensor({'v2': 3}, {'i2': 3}, {'d2': 3})]],
   side_feeds=[{'c': 6}, {'c': 2}])

  corresponding output:
  [{'a': 1, 'x': 3, 'v': 0, 'i': 0, 'd': 0, 'v2': 2, 'i2': 2, 'd2': 2, 'c': 6},
   {'a': 2, 'x': 5, 'v': 1, 'i': 1, 'd': 1, 'v2': 3, 'i2': 3, 'd2': 3, 'c': 2}]

  Args:
    dense_feeds: A list of dictionaries containing batched dense feeds.
    sparse_feeds: A list of batched EvaluatedSparseTensors.
    side_feeds: A list of dictionaries containing batched side feeds.
    size: Number of subbatches to merge.

  Returns:
    A list of dictionaries formed by merging all dictionaries in each position
      in the given list.
  """
    merged_feeds = [{} for _ in range(size)]
    for i, merged_feed in enumerate(merged_feeds):
        if dense_feeds:
            merged_feed.update(dense_feeds[i])
        if side_feeds:
            merged_feed.update(side_feeds[i])
        if sparse_feeds:
            for sparse_subfeed in sparse_feeds:
                merged_feed.update(sparse_subfeed[i].to_dict())
    return merged_feeds


def _split_dense_feed(feed, actual_size, max_batch_size):
    """Splits a dictionary of arrays into sub-batches in the first dimension."""
    return [
        {k: v[i : i + max_batch_size] for k, v in feed.items()}
        for i in range(0, actual_size, max_batch_size)
    ]


def split_sparse_feed(sparse_feed, actual_size, max_batch_size):
    """Splits sparse feed to a list of smaller feeds.

  Args:
    sparse_feed: A list of EvaluatedSparseTensors.
    actual_size: Given number of elements for the feed.
    max_batch_size: Batch size to split the batch.

  Returns:
    A list of EvaluatedSparseTensors for each sparse_feed item.
  """
    if not sparse_feed:
        return []

    sizes = [max_batch_size for _ in range(actual_size // max_batch_size)]
    if actual_size % max_batch_size > 0:
        sizes.append(actual_size % max_batch_size)

    return [_split_sparse_eval(sparse_eval, sizes) for sparse_eval in sparse_feed]


def _split_sparse_eval(sparse_eval, sizes):
    """Splits a given sparse tensor to given batch sizes.

  A sparse tensor is a compact representation of a dense tensor via 3 tensors.
  Values tensor specify what values exist in this conceptual dense tensor.
  Indices specify where those values are. Dense shape specifies the shape of
  this conceptual dense tensor. This function splits this hypothetical dense
  tensor into smaller pieces along its first dimension given by sizes list. It
  finds the split points in the hypothetical dense tensor first. Then, it splits
  the indices by finding the sorted insert index of these split locations. Using
  the same sorted index locations, it splits values tensor. Finally, a set of
  dense shape arrays are created based on the hypothetical sizes of smaller
  arrays.

  Once indices, values and dense shape tensor values are split to lists of
  arrays, new EvaluatedSparseTensor is created for each subbatch.

  Args:
    sparse_eval: A EvaluatedSparseTensor containing three dictionaries.
      Dictionaries contain a single key-value pair and map from tensor names to
      evaluated sparse values, indices, and dense shape.
    sizes: A list of integers representing resulting batch size for each
      sub-batch.

  Returns:
    A list of EvaluatedSparseTensor representing subbatches for the given
      EvaluatedSparseTensor.
  """
    split_points_in_dense = np.cumsum(sizes[:-1]).tolist()

    ((indices_name, indices_array),) = sparse_eval.indices.items()
    indices_array = np.array(indices_array)
    split_at = _find_sparse_split_points(indices_array, split_points_in_dense)
    indices_splits = _split_indices(indices_array, split_points_in_dense, split_at)

    ((values_name, values_array),) = sparse_eval.values.items()
    values_splits = _split_values(values_array, split_at)

    ((dense_shape_name, dense_shape_array),) = sparse_eval.dense_shape.items()
    dense_splits = _split_dense_shape(dense_shape_array, sizes)

    feed_splits = []
    for i, values_subbatch in enumerate(values_splits):
        feed_splits.append(
            EvaluatedSparseTensor(
                {values_name: values_subbatch},
                {indices_name: indices_splits[i]},
                {dense_shape_name: dense_splits[i]},
            )
        )
    return feed_splits


def _find_sparse_split_points(indices_array, split_points_in_dense):
    """Finds split locations in the indices array.

  Args:
    indices_array: A numpy array representing indices of a sparse tensor.
    split_points_in_dense: A list specifying where the split should happen in
      densified version of the tensor.

  Returns:
    A list containing positions where the original array was split.
  """
    if len(indices_array.shape) > 1:
        return indices_array[:, 0].searchsorted(split_points_in_dense)
    return indices_array.searchsorted(split_points_in_dense)


def _split_indices(indices_array, split_points_in_dense, split_at):
    """Splits indices array for the given sizes.

  Indices arrays specify the value locations for the values in a corresponding
  dense array. For 2D example, they can be similar to [[0, 0], [2, 0], [2, 1]].
  This could represent an array with at least 3 rows and 2 columns -- with only
  specified locations are filled. We split the array on the given locations.
  Then, first dimensions for each cut is adjusted as if they were indexing a new
  dense representation. For the example above, if we were to split into two
  batches of size 2, we would return the following indices splits:
  [[[0, 0]], [[0, 0], [0, 1]]].

  Args:
    indices_array: A numpy array representing indices of a sparse tensor.
    split_points_in_dense: Locations to split the conceptual dense tensor.
    split_at: Locations to split indices array.

  Returns:
    A list of indices tensors for each subbatch.
  """
    index_reduction = [0] + split_points_in_dense
    indices_splits = np.split(indices_array, split_at)
    for i, indices_split in enumerate(indices_splits):
        if len(indices_array.shape) > 1:
            indices_split[:, 0] -= index_reduction[i]
        else:
            indices_split -= index_reduction[i]
    return indices_splits


def _split_values(values_array, split_at):
    """Splits values tensor based on given split points."""
    return np.split(values_array, split_at)


def _split_dense_shape(dense_shape_array, sizes):
    """Splits dense shape array based on batch sizes."""
    return [np.concatenate(([size], dense_shape_array[1:])) for size in sizes]


def merge_evaluated_subbatches(dense_fetches, sparse_fetches, side_fetches):
    """Merges evaluated subbatches.

  Args:
    dense_fetches: A list of dictionaries, each of which representing evaluated
      dense tensor fetch for a subbatch.
    sparse_fetches: A 2D list of EvaluatedSparseTensors. First dimension
      represents different sparse tensors, second dimension represents each
      subbatch.
    side_fetches: A list of dictionaries, each of which representing evaluated
      side tensor fetch for a subbatch. They are treated same as dense fetch for
      now.

  Returns:
    A dictionary representing a combined fetch of all subbatches.
  """
    dense_fetch = concat(dense_fetches)
    side_fetch = concat(side_fetches)
    sparse_fetch = merge_sparse_fetches(sparse_fetches)
    return merge_dict(side_fetch, merge_dict(dense_fetch, sparse_fetch))


def merge_sparse_fetches(sparse_fetches):
    """Merges subbatches of evaluated sparse tensors into a single dictionary.

  Args:
    sparse_fetches: A list of list of evaluated sparse tensors. Each list in the
      outer list represents a different sparse tensor. Inner list represents
      each subbatch.

  Returns:
    A dictionary representing combined fetch for all given sparse tensors.
  """
    sparse_fetch = {}
    for subbatched_sparse_fetch in sparse_fetches:
        sparse_fetch.update(
            _merge_subbatched_sparse_fetch(subbatched_sparse_fetch).to_dict()
        )
    return sparse_fetch


def _merge_subbatched_sparse_fetch(sparse_fetch_subbatches):
    """Merges an evaluated sparse tensor subbatches into a single tensor.

  Args:
    sparse_fetch_subbatches: A list of EvaluatedSparseTensors representing
      evaluation of a single sparse tensor for a list of subbatches.

  Returns:
    An EvaluatedSparseTensor instance representing the eval of a single sparse
      tensor composed by combining all subbatches.
  """
    if not sparse_fetch_subbatches:
        return EvaluatedSparseTensor({}, {}, {})
    values_fetch = concat([tensor.values for tensor in sparse_fetch_subbatches])
    dense_shapes = [
        next(six.itervalues(sparse_eval.dense_shape))
        for sparse_eval in sparse_fetch_subbatches
    ]
    dense_tensor_name = next(six.iterkeys(sparse_fetch_subbatches[0].dense_shape))
    dense_fetch = _merge_dense_shapes(dense_tensor_name, dense_shapes)
    indices_fetch = _merge_indices(
        [tensor.indices for tensor in sparse_fetch_subbatches], dense_shapes
    )
    return EvaluatedSparseTensor(values_fetch, indices_fetch, dense_fetch)


def _merge_dense_shapes(tensor_name, shapes):
    """Merges subbatches of dense shape arrays.

  It takes an arbitrary shape array to infer dimensions. Then, sums the 0th
  dimension to figure out the batch size.

  Args:
    tensor_name: Name of the dense shape tensor.
    shapes: A list of dense shapes for each subbatch.

  Returns:
    A dictionary mapping from dense tensor name to combined dense shape.
  """
    dense_shape_fetch = np.copy(shapes[0])
    dense_shape_fetch[0] = np.sum(shapes, axis=0)[0]
    return {tensor_name: dense_shape_fetch}


def _merge_indices(indices_subbatches, dense_shape_subbatches):
    """Merges subbatches of indices tensors.

  This function merges subbatches for each indices tensor. It essentially
  concats the given list of indices after adjusting first dimension of each
  index based on batch size. For an example list of indices tensors
  [{'a': [0, 0], 'a': [0, 0]}] and subbatch shapes of [[2, 2], [2, 2]], the
  final result looks like {'a': [[0, 0], [2, 0]]}.

  Sparse tensors are assumed to be 1D or 2D only. Hence, the indices for an
  empty sparse tensor is reshaped to (0,) or (0, 2).

  Args:
    indices_subbatches: A list of dictinoaries where each dictionary contains a
      single key-value pair from indices tensor name to evaluation of that
      tensor for a single subbatch. List dimension represents different
      subbatches.
    dense_shape_subbatches: Shapes of the conceptual dense tensor implied by
      the sparse  for each subbatch

  Returns:
    A single dictionary mapping from indices tensor name to combined indices
      tensor values for all subbatches.
  """
    subbatch_sizes = np.array(dense_shape_subbatches)
    if len(subbatch_sizes.shape) > 1:
        subbatch_sizes = subbatch_sizes[:, 0]

    sizes_sum = np.cumsum(subbatch_sizes)
    merged_indices = concat(indices_subbatches)
    name, array = next(six.iteritems(merged_indices))
    array = np.array(array)
    if not array.size:
        indices_shape = [0]
        if np.array(dense_shape_subbatches[0]).shape:
            indices_shape.append(2)
        return {name: array.reshape(indices_shape)}
    adjustment = sizes_sum - subbatch_sizes
    num_elements = [len(list(batch.values())[0]) for batch in indices_subbatches]
    adjustment = np.repeat(adjustment, num_elements).astype(int)
    if len(array.shape) > 1:
        array[:, 0] += adjustment
    else:
        array += adjustment
    return {name: array}


def multithreaded_call(fn, args, worker_count=0, thread_pool=None):
    """Runs the given function in a thread pool and returns the results.

  Args:
    fn: Function to call in parallel.
    args: An iterable of argument list to call fn with.
    worker_count: Number of thread workers to launch.
    thread_pool: Optional thread pool to use instead of creating a new one.

  Returns:
    Function results in a list.
  """
    if not thread_pool:
        if worker_count:
            threads = pool.ThreadPool(worker_count)
        else:
            threads = pool.ThreadPool()
    else:
        threads = thread_pool
    results = threads.starmap(fn, args)
    if not thread_pool:
        threads.close()
        threads.join()
    return list(results)


class NumpyEncoder(json.JSONEncoder):
    """JSON Encoder to use when encoding dicts with numpy arrays."""

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif np.issubdtype(obj, np.number):
            return obj.item()  # convert most primitive np types to py-native types.
        return json.JSONEncoder.default(self, obj)


def decode_list(sequence):
    """Converts list elements to unicode if they are of bytes type."""
    return [token.decode() if isinstance(token, bytes) else token for token in sequence]


def convert_dict_key(key_map, dict_to_convert, keep_unmapped_keys=False):
    """Convert all keys in dictionary to the new key provided in mapping.

  Args:
    key_map: A mapping from old key to new key.
    dict_to_convert: The dictionary to be converted.
    keep_unmapped_keys: Keep the key, value pair as is if not in key_map.

  Returns:
    A dictionary with the same values as dict_to_convert with the new keys
      provided in key_map.
  """
    d = collections.OrderedDict()
    for k, v in dict_to_convert.items():
        if k in key_map:
            d[key_map[k]] = v
        elif keep_unmapped_keys:
            d[k] = v
        else:
            # This will only happen when we have an invalid explain metadata.
            raise ValueError(
                "Conversion failed. Key %s not in key map %s." % (k, repr(key_map))
            )
    return d


def replace_b64_dict(dict_to_replace):
    """Convert all {'b64': '...'} in dict to a b64 decoded string of the value.

  Args:
    dict_to_replace: The dictionary to be replaced.

  Returns:
    A new dictionary with the values (even nested) replaced to b64 decoded for
      the values in the form of {'b64': '...'}.
  """
    try:
        return _decode_b64(dict_to_replace)
    except Exception as e:
        raise ValueError("Base64 decode failed: %s" % e)


def _decode_b64(data):
    """Helper function that decodes {'b64': ...} to a string recursively.

  Args:
    data: Container that may contains {'b64': ...}.

  Returns:
    A new container with the values (even nested) replaced to b64 decoded for
      the values in the form of {'b64': '...'}.
  """
    if isinstance(data, list):
        return [_decode_b64(val) for val in data]
    elif isinstance(data, dict):
        if six.viewkeys(data) == {"b64"}:
            return base64.b64decode(data["b64"])
        else:
            return {k: _decode_b64(v) for k, v in six.iteritems(data)}
    elif isinstance(data, np.ndarray):
        data = data.tolist()
        return np.array(_decode_b64(data))
    else:
        return data


def top_k_indices_for_batch(batched_array, k=1):
    """Returns top k indices for given batched array.

  Args:
    batched_array: An array (first dimension is the batch) to determine top k
      indices.
    k: To calculate top k.

  Returns:
    A 2D or 3D numpy array where the first dimension is the batch and other
      dimensions indexing the position in the original array (after batch).
  """
    if batched_array[0].size < k:
        k = batched_array[0].size
    if k == 1:
        if len(batched_array.shape) == 2:
            return np.array(
                [
                    np.unravel_index(np.argmax(array), array.shape)
                    for array in batched_array
                ],
                dtype=np.int32,
            )
        else:
            return np.array(
                [
                    [np.unravel_index(np.argmax(array), array.shape)]
                    for array in batched_array
                ],
                dtype=np.int32,
            )

    top_k_batch = []
    for single_output in batched_array:
        top_k_batch.append(
            np.stack(
                np.unravel_index(
                    single_output.argsort(axis=None)[-k:][::-1], single_output.shape
                ),
                axis=1,
            ).squeeze()
        )

    return np.array(top_k_batch, dtype=np.int32)


def merge_feed_dict_with_explain_index(feed, label_indices, output_tensor_name):
    """Adds the explain index input to the feed_dict.

  Args:
    feed: The input values to evaluate the model.
    label_indices: The label index for each instance, to be explained.
    output_tensor_name: Name of the output tensor whose label_index is being
      explained.

  Returns:
    feed augmented with explain index name (key) and tensor name (value).
  """
    feed[EXPLAIN_OUTPUT_INDEX_TEMPLATE.format(output_tensor_name)] = label_indices
    return feed


def is_explain_index_needed(output_tensor_value):
    """Checks if we need a label index to explain from a multi-class output."""
    return is_multi_class(output_tensor_value.shape)


def is_multi_class(output_shape):
    """Checks if output is multi-class."""
    # If single value output
    if len(output_shape) == 1:
        return False

    return True


def suffix_dict_keys(in_dict, suffix):
    """Adds the given suffix to all dictionary keys."""
    return {key + suffix: value for key, value in in_dict.items()}


def add_gaussian_noise(data, noise_sigma):
    """Returns given batch data with gaussian noise added to it.

  Args:
    data: The batch data for which noisy data is to be produced.
    noise_sigma: This represents the standard deviation of the gaussian kernel
      that will be used to add noise to the interpolated inputs prior to
      computing gradients. The standard deviation must be provided for each
      feature for which we produce attributions.

  Returns:
    A copy of data with noise added to it.
    Adds noise only to those features for which noise_sigma is provided.
  """
    result = {}
    for feature in data:
        if feature not in noise_sigma:
            # No noise to be added since there's no noise_sigma for this feature.
            result[feature] = data[feature]
        else:
            result[feature] = data[feature] + np.random.normal(
                0.0,  # Mean.
                noise_sigma[feature],  # Standard deviation.
                data[feature].shape,
            )  # Shape.
    return result
