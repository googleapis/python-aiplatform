# Explainable AI SDK for TensorFlow 1.x

This page provides additional examples for each of the three TensorFlow 1.x
metadata builders. These metadata builders help you to create and upload an
explanation metadata file that is required for model deployment on AI Platform.

For more information, refer to the [main README file](../../../../README.md).

## Explanation metadata file

Each metadata builder helps to identify your model's inputs and outputs for
your explanation request. When you call the `save_model_with_metadata()`
function, it creates an explanation metadata file that looks like this:

```json
{
  "outputs": {
    "Relu": {
      "output_tensor_name": "Relu:0"
    }
  },
  "inputs": {
    "inp": {
      "input_tensor_name": "inp:0",
      "encoding": "identity",
      "modality": "numeric"
    }
  },
  "framework": "Tensorflow",
  "tags": [
    "explainable_ai_sdk"
  ]
}
```

The Explainable AI SDK saves this file in Cloud Storage along with your
SavedModel, which prepares you to deploy your model on AI Platform and request
explanations.

### Keras metadata builder

The Keras metadata builder supports models built with TensorFlow Keras. Here is
an example:

```python
import tensorflow.compat.v1 as tf
from explainable_ai_sdk.metadata.tf.v1 import KerasGraphMetadataBuilder

my_model = keras.models.Sequential()
my_model.add(keras.layers.Dense(32, activation='relu', input_dim=10))
my_model.add(keras.layers.Dense(32, activation='relu'))
my_model.add(keras.layers.Dense(1, activation='sigmoid'))
builder = KerasGraphMetadataBuilder(my_model)
builder.save_model_with_metadata('gs://my_bucket/model')  # Save the model and the metadata.
```

### Estimator metadata builder

The Estimator metadata builder supports models built with TensorFlow Estimator.
Here is an example:

```python
import tensorflow.compat.v1 as tf
from explainable_ai_sdk.metadata.tf.v1 import EstimatorMetadataBuilder

# Build a model.
language = tf.feature_column.categorical_column_with_vocabulary_list(
    key='language',
    vocabulary_list=('english', 'korean'),
    num_oov_buckets=1)
language_indicator = tf.feature_column.indicator_column(language)
class_identity = tf.feature_column.categorical_column_with_identity(
    key='class_identity', num_buckets=4)
class_id_indicator = tf.feature_column.indicator_column(class_identity)
age = tf.feature_column.numeric_column(key='age', default_value=0.0)
classifier_dnn = tf.estimator.DNNClassifier(
    hidden_units=[4],
    feature_columns=[age, language_indicator, language_embedding, class_id_indicator])
classifier_dnn.train(input_fn=_train_input_fn, steps=5)

# Build the metadata.
md_builder = EstimatorMetadataBuilder(
    classifier_dnn, [age, language, class_identity],  _get_json_serving_input_fn, 'logits')
model_path = md_builder.save_model_with_metadata("gs://my_model")
```

### Graph metadata builder

The Graph metadata builder supports models built with the low-level TensorFlow
API. The SDK provides a function to help you add metadata for each type of
input: numeric, categorical, image, and text.

Here is an example:

```python
import tensorflow.compat.v1 as tf
from explainable_ai_sdk.metadata.tf.v1 import GraphMetadataBuilder

# Build a model.
sess = tf.Session(graph=tf.Graph())
with sess.graph.as_default():
  x = tf.placeholder(shape=[None, 10], dtype=tf.float32, name='inp')
  weights = tf.constant(1., shape=(10, 2), name='weights')
  bias_weight = tf.constant(1., shape=(2,), name='bias')
  linear_layer = tf.add(tf.matmul(x, weights), bias_weight)
  prediction = tf.nn.relu(linear_layer)

# Build the metadata.
builder = GraphMetadataBuilder(
    session=sess, tags=['serve'])
builder.add_numeric_metadata(x)
builder.add_output_metadata(prediction)
model_path = os.path.join('gs://my_model', 'xai')
builder.save_model_with_metadata(model_path)
```
