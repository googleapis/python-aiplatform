
transport inheritance structure
_______________________________

`ModelGardenServiceTransport` is the ABC for all transports.
- public child `ModelGardenServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `ModelGardenServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseModelGardenServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `ModelGardenServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
