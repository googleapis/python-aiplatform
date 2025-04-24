# Vertex Model Garden SDK for Python

The Vertex Model Garden SDK helps developers use [Model Garden](https://cloud.google.com/vertex-ai/generative-ai/docs/model-garden/explore-models) open models to build AI-powered features and applications.
The SDKs support use cases like the following:

- Deploy an open model
- Export open model weights

## Installation

To install the
[google-cloud-aiplatform](https://pypi.org/project/google-cloud-aiplatform/)
Python package, run the following command:

```shell
pip3 install --upgrade --user "google-cloud-aiplatform>=1.84"
```

## Usage

For detailed instructions, see [deploy an open model](https://cloud.google.com/vertex-ai/generative-ai/docs/model-garden/use-models#deploy_an_open_model) and [deploy notebook tutorial](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_deployment_tutorial.ipynb).

## Quick Start: Default Deployment

This is the simplest way to deploy a model. If you provide just a model name, the SDK will use the default deployment configuration.

```python
from vertexai.preview import model_garden

model = model_garden.OpenModel("google/paligemma@paligemma-224-float32")
endpoint = model.deploy()
```

**Use case:** Fast prototyping, first-time users evaluating model outputs.

## List Deployable Models

You can list all models that are currently deployable via Model Garden:

```python
from vertexai.preview import model_garden

models = model_garden.list_deployable_models()
```

To filter only Hugging Face models or by keyword:

```python
models = model_garden.list_deployable_models(list_hf_models=True, model_filter="stable-diffusion")
```

**Use case:** Discover available models before deciding which one to deploy.

## Hugging Face Model Deployment

Deploy a model directly from Hugging Face using the model ID.

```python
model = model_garden.OpenModel("Qwen/Qwen2-1.5B-Instruct")
endpoint = model.deploy()
```

**Use case:** Leverage community or third-party models without custom container setup. If the model is gated, you may need to provide a Hugging Face access token:

```python
endpoint = model.deploy(hugging_face_access_token="your_hf_token")
```

**Use case:** Deploy gated Hugging Face models requiring authentication.

## List Deployment Configurations

You can inspect available deployment configurations for a model:

```python
model = model_garden.OpenModel("google/paligemma@paligemma-224-float32")
deploy_options = model.list_deploy_options()
```

**Use case:** Evaluate compatible machine specs and containers before deployment.

## Customize Deployment: Machine and Resource Configuration

Specify exact hardware resources and endpoint/model names.

```python
endpoint = model.deploy(
    machine_type="g2-standard-4",
    accelerator_type="NVIDIA_L4",
    accelerator_count=1,
    min_replica_count=1,
    max_replica_count=1,
    endpoint_display_name="paligemma-endpoint",
    model_display_name="paligemma-model"
)
```

**Use case:** Production configuration, performance tuning, scaling.

## EULA Acceptance

Some models require acceptance of a license agreement. Pass `eula=True` if prompted.

```python
model = model_garden.OpenModel("google/gemma2@gemma-2-27b-it")
endpoint = model.deploy(eula=True)
```

**Use case:** First-time deployment of EULA-protected models.

## Spot VM Deployment

Schedule workloads on Spot VMs for lower cost.

```python
endpoint = model.deploy(spot=True)
```

**Use case:** Cost-sensitive development and batch workloads.

## Fast Tryout Deployment

Enable experimental fast-deploy path for popular models.

```python
endpoint = model.deploy(fast_tryout_enabled=True)
```

**Use case:** Interactive experimentation without full production setup.

## Dedicated Endpoints

Create a dedicated DNS-isolated endpoint.

```python
endpoint = model.deploy(use_dedicated_endpoint=True)
```

**Use case:** Traffic isolation for enterprise or regulated workloads.

## Reservation Affinity

Use shared or specific Compute Engine reservations.

```python
endpoint = model.deploy(
    reservation_affinity_type="SPECIFIC_RESERVATION",
    reservation_affinity_key="compute.googleapis.com/reservation-name",
    reservation_affinity_values="projects/YOUR_PROJECT/zones/YOUR_ZONE/reservations/YOUR_RESERVATION"
)
```

**Use case:** Optimized resource usage with pre-reserved capacity.

## Custom Container Image

Override the default container with a custom image.

```python
endpoint = model.deploy(
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/custom-container:latest"
)
```

**Use case:** Use of custom inference servers or fine-tuned environments.

## Advanced Full Container Configuration

Further customize startup probes, health checks, shared memory, and gRPC ports.

```python
endpoint = model.deploy(
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/custom-container:latest",
    container_command=["python3"],
    container_args=["serve.py"],
    container_ports=[8888],
    container_env_vars={"ENV": "prod"},
    container_predict_route="/predict",
    container_health_route="/health",
    serving_container_shared_memory_size_mb=512,
    serving_container_grpc_ports=[9000],
    serving_container_startup_probe_exec=["/bin/check-start.sh"],
    serving_container_health_probe_exec=["/bin/health-check.sh"]
)
```

**Use case:** Production-grade deployments requiring deep customization of runtime behavior and monitoring.

## Documentation

You can find complete documentation for the Vertex AI SDKs and Model Garden in the Google Cloud [documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/overview)

## Contributing

See [Contributing](https://github.com/googleapis/python-aiplatform/blob/main/CONTRIBUTING.rst) for more information on contributing to the Vertex AI Python SDK.

## License

The contents of this repository are licensed under the [Apache License, version 2.0](http://www.apache.org/licenses/LICENSE-2.0).