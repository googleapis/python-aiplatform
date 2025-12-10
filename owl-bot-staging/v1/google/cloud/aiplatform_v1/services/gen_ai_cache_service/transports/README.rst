
transport inheritance structure
_______________________________

`GenAiCacheServiceTransport` is the ABC for all transports.
- public child `GenAiCacheServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `GenAiCacheServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseGenAiCacheServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `GenAiCacheServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
