
transport inheritance structure
_______________________________

`DeploymentResourcePoolServiceTransport` is the ABC for all transports.
- public child `DeploymentResourcePoolServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `DeploymentResourcePoolServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseDeploymentResourcePoolServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `DeploymentResourcePoolServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
