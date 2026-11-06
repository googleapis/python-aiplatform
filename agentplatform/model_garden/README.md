# Gemini Enterprise Agent Platform Model Garden SDK for Python

The Gemini Enterprise Agent Platform Model Garden SDK helps developers use [Model Garden](https://cloud.google.com/model-garden) open models to build AI-powered features and applications.
The SDK supports use cases like the following:

- Discover deployable models and their verified deployment configurations
- Deploy an open, partner, or Hugging Face model
- Deploy a model from custom weights in Cloud Storage
- Export open model weights
- Run batch prediction on an open model

All methods live on `client.model_garden`, and follow the Google Gen AI SDK
convention: required arguments are passed directly, and optional settings go in
a typed config from `agentplatform.types` (or an equivalent dict).

## Installation

To install the
[google-cloud-aiplatform](https://pypi.org/project/google-cloud-aiplatform/)
Python package, run the following command:

```shell
pip3 install --upgrade --user google-cloud-aiplatform
```

## Usage

Create a client for your project and region:

```python
import agentplatform
from agentplatform import types

client = agentplatform.Client(project="YOUR_PROJECT", location="us-central1")
```

For detailed instructions, see [deploy an open model](https://cloud.google.com/gemini-enterprise-agent-platform/models/open-models/deploy-model-garden).

## Quick Start: Default Deployment

This is the simplest way to deploy a model. If you provide just a model name,
the SDK uses the model's default deployment configuration.

```python
response = client.model_garden.deploy_publisher_model(
    model="google/gemma3@gemma-3-1b-it",
)
print(response.endpoint)  # projects/.../locations/.../endpoints/...
```

`deploy_publisher_model` waits until the model is serving and returns a
`DeployResponse` with the `endpoint` and `model` resource names.

**Use case:** Fast prototyping, first-time users evaluating model outputs.

## Send a Prediction Request

```python
prediction = client.endpoints.predict(
    name=response.endpoint,
    instances=[{"prompt": "What is a tree?", "max_tokens": 64}],
)
print(prediction.predictions)
```

Requests to a dedicated endpoint are sent to its dedicated DNS automatically.
The instance format depends on the model's serving container; for example,
PaliGemma expects an `image` (base64) alongside the `prompt`.

## List Deployable Models

You can list all models that are currently deployable via Model Garden:

```python
models = client.model_garden.list_deployable_models()
```

To include Hugging Face models or filter by keyword:

```python
models = client.model_garden.list_deployable_models(
    config=types.ListDeployableModelsConfig(
        include_hugging_face_models=True,
        model_filter="stable-diffusion",
    ),
)
```

Use `list_models` with `types.ListModelGardenModelsConfig` to list every model,
including ones without a verified deployment.

**Use case:** Discover available models before deciding which one to deploy.

## List Deployment Configurations

You can inspect the verified deployment configurations for a model:

```python
deploy_options = client.model_garden.list_publisher_model_deploy_options(
    model="google/paligemma@paligemma-224-float32",
)
for option in deploy_options:
    print(option.machine_type, option.accelerator_type, option.serving_container_image_uri)
```

To narrow the results, or get a human-readable summary instead of a list:

```python
summary = client.model_garden.list_publisher_model_deploy_options(
    model="google/paligemma@paligemma-224-float32",
    config=types.ListPublisherModelDeployOptionsConfig(
        machine_type_filter="g2",
        accelerator_type_filter=["L4", "H100"],
        concise=True,
    ),
)
print(summary)
```

**Use case:** Evaluate compatible machine specs and containers before deployment.

## Hugging Face Model Deployment

Deploy a model directly from Hugging Face using the model ID.

```python
response = client.model_garden.deploy_publisher_model(
    model="Qwen/Qwen2-1.5B-Instruct",
)
```

**Use case:** Leverage community or third-party models without custom container
setup. If the model is gated, provide a Hugging Face access token:

```python
response = client.model_garden.deploy_publisher_model(
    model="meta-llama/Llama-3.3-70B-Instruct",
    config=types.DeployPublisherModelConfig(
        hugging_face_access_token="your_hf_token",
    ),
)
```

## Select a Verified Deployment: By Container Image

Specify a container image from the list of verified deployment configurations
(`list_publisher_model_deploy_options`).

```python
response = client.model_garden.deploy_publisher_model(
    model="google/paligemma@paligemma-224-float32",
    config=types.DeployPublisherModelConfig(
        serving_container_image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/jax-paligemma-serve-gpu:20240513_0916_RC00",
    ),
)
```

## Select a Verified Deployment: By Hardware

Specify a hardware configuration from the list of verified deployment configurations.

```python
response = client.model_garden.deploy_publisher_model(
    model="google/paligemma@paligemma-224-float32",
    config=types.DeployPublisherModelConfig(
        machine_type="g2-standard-16",
        accelerator_type="NVIDIA_L4",
        accelerator_count=1,
    ),
)
```

## Select a Verified Deployment: By Container and Hardware

Specify both a container image and a hardware configuration from the list of
verified deployment configurations. They must belong to the same verified
option: a pair that matches no option is rejected unless you also pass the full
container settings (command, arguments or environment variables).

```python
response = client.model_garden.deploy_publisher_model(
    model="google/paligemma@paligemma-224-float32",
    config=types.DeployPublisherModelConfig(
        serving_container_image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/jax-paligemma-serve-gpu:20240513_0916_RC00",
        machine_type="g2-standard-16",
        accelerator_type="NVIDIA_L4",
        accelerator_count=1,
    ),
)
```

**Use case:** Production configuration, performance tuning, scaling.

## EULA Acceptance

Some models require acceptance of a license agreement. Set `accept_eula=True` to
accept it.

```python
response = client.model_garden.deploy_publisher_model(
    model="google/gemma2@gemma-2-27b-it",
    config=types.DeployPublisherModelConfig(accept_eula=True),
)
```

**Use case:** First-time deployment of EULA-protected models.

## Deployment Options

All of the following are fields on `types.DeployPublisherModelConfig` and can be
combined.

| Field | Effect |
| --- | --- |
| `spot=True` | Schedule the deployment on Spot VMs for lower cost. |
| `fast_tryout_enabled=True` | Use the experimental fast-deploy path for popular models. |
| `dedicated_endpoint_disabled=True` | Serve through the shared regional DNS instead of a dedicated, traffic-isolated DNS. |
| `min_replica_count`, `max_replica_count` | Autoscaling bounds. |
| `endpoint_display_name`, `model_display_name` | Display names for the created resources. |
| `enable_private_service_connect=True`, `psc_project_allow_list=[...]` | Expose the endpoint through Private Service Connect. |

```python
response = client.model_garden.deploy_publisher_model(
    model="google/gemma2@gemma-2-27b-it",
    config=types.DeployPublisherModelConfig(
        accept_eula=True,
        spot=True,
        endpoint_display_name="gemma-2-27b-it-spot",
    ),
)
```

## Custom Container Image

Override the default container with a custom image. The command, arguments and
environment variables are only applied together with
`serving_container_image_uri`.

```python
response = client.model_garden.deploy_publisher_model(
    model="google/paligemma@paligemma-224-float32",
    config=types.DeployPublisherModelConfig(
        # Replace with your own serving container image.
        serving_container_image_uri="us-docker.pkg.dev/YOUR_PROJECT/YOUR_REPOSITORY/YOUR_IMAGE:TAG",
        container_command=["python3"],
        container_args=["serve.py"],
        container_variables={"ENV": "prod"},
    ),
)
```

**Use case:** Use of custom inference servers or fine-tuned environments.

## Deploy Without Waiting

Set `wait_for_completion=False` to get the long-running operation back
immediately and poll it yourself.

```python
operation = client.model_garden.deploy_publisher_model(
    model="google/gemma2@gemma-2-27b-it",
    config=types.DeployPublisherModelConfig(accept_eula=True, wait_for_completion=False),
)
operation = client.model_garden.get_deploy_publisher_model_operation(
    operation_name=operation.name,
)
if operation.done:
    print(operation.response.endpoint)
```

When waiting, `poll_interval_seconds` and `timeout_seconds` (default 2 hours)
control the polling.

## Deploy a Model with Custom Weights

Deploy weights you produced yourself, such as a tuning job checkpoint, from a
Cloud Storage folder that holds the weights and config files.

```python
options = client.model_garden.list_custom_model_deploy_options(
    src="gs://your-bucket/weights/",
)
print(options)

response = client.model_garden.deploy_custom_model(
    src="gs://your-bucket/weights/",
    config=types.DeployCustomModelConfig(
        machine_type="g2-standard-12",
        accelerator_type="NVIDIA_L4",
        accelerator_count=1,
    ),
)
```

Set all three machine fields, or none of them for an automatic configuration.
`types.DeployCustomModelConfig` also supports reservation affinity
(`reservation_affinity_type`, `reservation_affinity_key`,
`reservation_affinity_values`) and `system_labels`.

## Export Open Model Weights

Export the weights of a Google open model to Cloud Storage:

```python
destination = client.model_garden.export_open_model(
    model="google/gemma2@gemma-2-2b-it",
    output_gcs_uri="gs://your-bucket/gemma-weights/",
)
```

Exports of large models can take hours; pass
`config=types.ExportOpenModelConfig(wait_for_completion=False)` to get the
operation back and poll it with `get_export_publisher_model_operation`.

## Batch Prediction

Run an open model over a JSONL file in Cloud Storage (or a BigQuery table):

```python
job = client.model_garden.batch_predict(
    model="google/gemma3@gemma-3-1b-it",
    src="gs://your-bucket/input/requests.jsonl",
    config=types.BatchPredictConfig(
        dest="gs://your-bucket/output/",
        machine_type="g2-standard-12",
        accelerator_type="NVIDIA_L4",
        accelerator_count=1,
    ),
)
job = client.model_garden.get_batch_prediction_job(name=job.name)
print(job.state)
```

Each input line is one request, for example
`{"custom_id": "1", "method": "POST", "url": "/v1/chat/completions", "body": {"messages": [{"role": "user", "content": "What is a tree?"}]}}`.
`batch_predict` returns as soon as the job is created.

## Async

Every method has an async counterpart on `client.aio.model_garden`:

```python
models = await client.aio.model_garden.list_deployable_models()
```

## Migrating from `model_garden.OpenModel`

| Legacy | New |
| --- | --- |
| `model_garden.list_deployable_models(list_hf_models=True)` | `client.model_garden.list_deployable_models(config=types.ListDeployableModelsConfig(include_hugging_face_models=True))` |
| `OpenModel(m).list_deploy_options()` | `client.model_garden.list_publisher_model_deploy_options(model=m)` |
| `OpenModel(m).deploy(...)`, `PartnerModel(m).deploy(...)` | `client.model_garden.deploy_publisher_model(model=m, config=types.DeployPublisherModelConfig(...))` |
| `CustomModel(gcs_uri=src).list_deploy_options()` | `client.model_garden.list_custom_model_deploy_options(src=src)` |
| `CustomModel(gcs_uri=src).deploy(...)` | `client.model_garden.deploy_custom_model(src=src, config=types.DeployCustomModelConfig(...))` |
| `OpenModel(m).export(target_gcs_path=uri)` | `client.model_garden.export_open_model(model=m, output_gcs_uri=uri)` |
| `OpenModel(m).batch_predict(input_dataset=src, output_uri_prefix=dest)` | `client.model_garden.batch_predict(model=m, src=src, config=types.BatchPredictConfig(dest=dest))` |
| `endpoint.predict(...)` on the returned `aiplatform.Endpoint` | `client.endpoints.predict(name=response.endpoint, instances=[...])` |

Deploy methods now return a `DeployResponse` (resource names) instead of an
`aiplatform.Endpoint`, and errors are raised from `google.genai.errors`.

## Contributing

See [Contributing](https://github.com/googleapis/python-aiplatform/blob/main/CONTRIBUTING.rst) for more information on contributing to the Gemini Enterprise Agent Platform Python SDK.

## License

The contents of this repository are licensed under the [Apache License, version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
