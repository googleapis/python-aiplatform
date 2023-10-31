# Vertex AI SDK User guide


## Introduction
Vertex AI SDK adds a new usability layer to the [Vertex SDK](https://cloud.google.com/python/docs/reference/aiplatform/latest) with the goal of substantially improving the traditional data-to-model workflows. It allows users to shift from thinking about the mechanics of calling Vertex services, to thinking in terms of building models and seamlessly interleaving the [Vertex SDK](https://cloud.google.com/python/docs/reference/aiplatform/latest) throughout their workflow.


## Setup
Vertex AI SDK is currently available in preview under `vertexai` package. Please install `google-cloud-aiplatform[preview]` using pip to enable full functionalities.

We also recommend installing the package in a [virtualenv](https://virtualenv.pypa.io/en/latest/) using pip. [virtualenv](https://virtualenv.pypa.io/en/latest/) is a tool to create isolated Python environments and helps manage dependencies and versions, and indirectly permissions.

### Mac/Linux

```shell
pip install virtualenv
virtualenv <your-env>
source <your-env>/bin/activate
<your-env>/bin/pip install google-cloud-aiplatform[preview]
```

### Windows

```shell
pip install virtualenv
virtualenv <your-env>
<your-env>\Scripts\activate
<your-env>\Scripts\pip.exe install google-cloud-aiplatform[preview]
```


## Remote training
With the remote training feature in Vertex AI SDK, you can write your machine learning code as usual and then the code will be automatically executed on [Vertex AI CustomJob](https://cloud.google.com/vertex-ai/docs/training/create-custom-job) with few small changes. This feature allows you to seamlessly access Vertex resources while reducing the time needed to learn how to interact with Vertex services.

### Supported frameworks
1. scikit-learn
2. tensorflow
3. pytorch
4. lightning

### User journey
```py
import vertexai
from sklearn.linear_model import LogisticRegression

# Wrap classes to enable Vertex remote execution
LogisticRegression = vertexai.preview.remote(LogisticRegression)

# Init vertexai and switch to remote mode for training
vertexai.init(project="my-project", location="my-location")
vertexai.preview.init(remote=True)

model = LogisticRegression()

# Model will be trained on Vertex
model.fit(X, y)
```

### (Optional) Remote job configuration
Vertex will help you set the remote job based on the model you use. But you can also customize those configurations, e.g., display name, staging bucket, machine type.

```py
# Set the config before training the model
model.fit.vertex.remote_config.display_name = "my-sklearn-training"
model.fit.vertex.remote_config.staging_bucket = "gs://my-bucket"
model.fit.vertex.remote_config.machine_type = "n1-highmem-64"

# Model will be trained on Vertex
model.fit(X, y)
```

[Here](https://github.com/googleapis/python-aiplatform/blob/main/vertexai/preview/_workflow/shared/configs.py#L22-L104) is the full list of supported configurations.


## Remote GPU training
This is an extra feature on top of remote training. It allows you to remotely train supported models on GPU, even though you don't have any GPU resources in your local device. Please check [here](https://github.com/googleapis/python-aiplatform/blob/main/vertexai/preview/_workflow/shared/configs.py#L63-L73) for more information.

### Supported frameworks
1. tensorflow
2. pytorch

### User journey
```py
import vertexai
from tensorflow import keras

# Wrap classes to enable Vertex remote execution
keras.Sequential = vertexai.preview.remote(keras.Sequential)

# Init vertexai and switch to remote mode for training
vertexai.init(project="my-project", location="my-location")
vertexai.preview.init(remote=True)

# Instantiate model
model = keras.Sequential(
    [keras.layers.Dense(5, input_shape=(4,)), keras.layers.Softmax()]
)
model.compile(optimizer="adam", loss="mean_squared_error")

# Set `enable_cuda` to True in remote config
model.fit.vertex.remote_config.enable_cuda = True

# Model will be trained on Vertex with GPU
model.fit(dataset, epochs=10)
```


## Remote distributed training
This feature extends remote training by enabling you to remotely train supported models on multi-worker CPU or GPU machines, regardless of the resources available in your local device. Please check [here](https://github.com/googleapis/python-aiplatform/blob/main/vertexai/preview/_workflow/shared/configs.py#L74-L86) for more information.

### Supported frameworks
1. tensorflow
2. pytorch

### User journey
```py
import torch
import vertexai
from vertexai.preview import VertexModel
from vertexai.preview.developer import remote_specs

# Define the custom model with `VertexModel` to enable remote execution
class TorchLogisticRegression(VertexModel, torch.nn.Module):

  def __init__(self, input_size:int, output_size:int):
    torch.nn.Module.__init__(self)
    VertexModel.__init__(self)
    self.linear = torch.nn.Linear(input_size, output_size)
    self.softmax = torch.nn.Softmax(dim=1)

  def forward(self, x):
    return self.softmax(self.linear(x))

  # Add this train decorator to allow remote training
  @vertexai.preview.developer.mark.train()
  def train(self, dataloader, num_epochs, lr):
    # Add this line to enable distributed training for pytorch
    self = remote_specs.setup_pytorch_distributed_training(self)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(self.parameters(), lr=lr)

    for t in range(num_epochs):
      for idx, batch in enumerate(dataloader):
        device = next(self.parameters()).device
        x, y = batch[0].to(device), batch[1].to(device)
        optimizer.zero_grad()
        pred = self(x)
        loss = criterion(pred, y)
        loss.backward()
        optimizer.step()


# Init vertexai and switch to remote mode for training
vertexai.init(project="my-project", location="my-location")
vertexai.preview.init(remote=True)

# Instantiate model
model = TorchLogisticRegression(4, 3)

# Set `enable_distributed` to True in remote config
model.fit.vertex.remote_config.enable_distributed = True

# Model will be distributed trained on Vertex
model.train(dataloader, num_epochs=100, lr=0.05)
```

## Remote training with Autologging
The [autologging feature](https://cloud.google.com/vertex-ai/docs/experiments/autolog-data) is available in remote training. Metrics (summary metrics, time series metrics, etc) and parameters for your remote training can be automatically logged into [Vertex Experiments](https://cloud.google.com/vertex-ai/docs/experiments/intro-vertex-ai-experiments). This feature allows you to easily track, compare, and analyze your training runs with different setups.

### User journey
```py
# Init with experiment and autolog
vertexai.init(
  project="my-project",
  location="my-location",
  experiment="my-exp",
)
vertexai.preview.init(remote=True)
...
# Set a service account in remote config, this is required for autologging
model.fit.vertex.remote_config.service_account = "GCE"

# Model will be trained on Vertex with data automatically logged
model.fit(X, y)
```


## Uptraining
Once you finish training a model, you may register your trained model to the [Vertex Model Registry](https://cloud.google.com/vertex-ai/docs/model-registry/introduction). And then pulled the pretrained model from the model registry for up training with new input training data.

### Supported frameworks
1. scikit-learn
2. tensorflow
3. pytorch

### User journey

#### Register to Model Registry
After a model is trained, you can register the model with `register()` method. It returns an [aiplatform.Model](https://github.com/googleapis/python-aiplatform/blob/main/google/cloud/aiplatform/models.py#L2610) object.

```py
# Model could be trained locally or remotely in previous steps
registered_model = vertexai.preview.register(model)
```

#### Pulled pre-trained model from Model Registry
You can then use the `from_pretrained()` method with the resource name of an [aiplatform.Model](https://github.com/googleapis/python-aiplatform/blob/main/google/cloud/aiplatform/models.py#L2610) or an [aiplatdform.CustomJob](https://github.com/googleapis/python-aiplatform/blob/main/google/cloud/aiplatform/jobs.py#L1171) to retrieve the model object.

```py
# You can get the model resource name through SDK or Google Cloud console.
pulled_model = vertexai.preview.from_pretrained(
  model_name=registered_model.resource_name
)
```

```py
# You can get the custom job resource name through Google Cloud console.
pulled_model = vertexai.preview.from_pretrained(
  custom_job_name="1234567890123456789"
)
```


#### Uptraining
You can proceed with uptraining (remotely or locally) using new input training data.

```py
pulled_model.fit(X_retrain, y_retrain)
```


## Remote training with Built-in Models
In addition to custom machine learning code, we also support remote training with built-in algorithms through pre-built containers. You will be able to run training jobs on your data without having to write any code for a training application.

### Supported frameworks
1. [TabNetTrainer](https://github.com/googleapis/python-aiplatform/blob/main/vertexai/preview/tabular_models/tabnet_trainer.py#L52)

### User Journey
```py
import vertexai
from vertexai.preview.tabular_models import TabNetTrainer

# Init vertexai and switch to remote mode for training
vertexai.init(project="my-project", location="my-location")
vertexai.preview.init(remote=True)

trainer = TabNetTrainer(
  model_type = "classification",
  target_column = "target",
  learning_rate = 0.01,
  max_train_secs = 1800,
)

trainer.fit(training_data, validation_data)
```


## Vizier Hyperparameter Tuning
Vertex AI SDK supports local and remote hyperparameter tuning using [Vertex AI Vizier](https://cloud.google.com/vertex-ai/docs/vizier/overview). Local tuning creates trials locally and runs training locally, meanwhile remote tuning creates trials locally and runs training remotely on [Vertex AI CustomJob](https://cloud.google.com/vertex-ai/docs/training/create-custom-job), with each CustomJob corresponding to one trial.

### Supported frameworks
1. scikit-learn
2. tensorflow
3. pytorch
4. lightning

### User journey
```py
import vertexai

# Init vertexai and switch to remote mode for tuning
vertexai.init(project="my-project", location="my-location")
vertexai.preview.init(remote=True)


def get_model_func(C: float):
    from sklearn.linear_model import LogisticRegression

    # Wrap the class to train models on Vertex
    LogisticRegression = vertexai.preview.remote(LogisticRegression)
    # Instantiate model. C will be tuned.
    model = LogisticRegression(C=C)

    return model


tuner = VizierHyperparameterTuner(
    get_model_func=get_model_func,
    max_trial_count=4,
    parallel_trial_count=2,
    hparam_space=[
      {
        "parameter_id": "C",
        "discrete_value_spec": {"values": [0.1, 0.5, 1.0]},
      }
    ],
    metric_id="custom",
    metric_goal="MAXIMIZE",
)

# Tune model using Vizier. Tuning runs locally while trials run on Vertex.
tuner.fit(X_train, y_train)

# Get the best model after tuning is done.
best_model = tuner.get_best_models()[0]
```


## Sample Notebooks
The notebooks below showcase the different usage of Vertex AI SDK.

- [remote_training_sklearn.ipynb](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/official/vertex_ai_sdk/remote_training_sklearn.ipynb)
    - Remote training
    - Uptraining

- [remote_training_pytorch.ipynb](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/official/vertex_ai_sdk/remote_training_pytorch.ipynb)
    - Remote training
    - Remote GPU training
    - Uptraining

- [remote_training_tensorflow_with_autologging.ipynb](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/official/vertex_ai_sdk/remote_training_tensorflow_with_autologging.ipynb)
    - Remote training
    - Remote GPU training
    - Remote training with Autologging
    - Uptraining

- [remote_training_lightning.ipynb](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/official/vertex_ai_sdk/remote_training_lightning.ipynb)
    - Remote training

- [remote_hyperparameter_tuning.ipynb](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/official/vertex_ai_sdk/remote_hyperparameter_tuning.ipynb)
    - Vizier Hyperparameter Tuning