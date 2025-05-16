
transport inheritance structure
_______________________________

`FeatureRegistryServiceTransport` is the ABC for all transports.
- public child `FeatureRegistryServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `FeatureRegistryServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseFeatureRegistryServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `FeatureRegistryServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
