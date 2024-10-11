
transport inheritance structure
_______________________________

`IndexServiceTransport` is the ABC for all transports.
- public child `IndexServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `IndexServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseIndexServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `IndexServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
