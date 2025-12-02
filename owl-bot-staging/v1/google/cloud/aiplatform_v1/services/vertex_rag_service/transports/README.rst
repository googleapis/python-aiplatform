
transport inheritance structure
_______________________________

`VertexRagServiceTransport` is the ABC for all transports.
- public child `VertexRagServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `VertexRagServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseVertexRagServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `VertexRagServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
