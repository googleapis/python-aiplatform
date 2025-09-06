
transport inheritance structure
_______________________________

`ExtensionRegistryServiceTransport` is the ABC for all transports.
- public child `ExtensionRegistryServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `ExtensionRegistryServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseExtensionRegistryServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `ExtensionRegistryServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
