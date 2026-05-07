
transport inheritance structure
_______________________________

`VertexRagDataServiceTransport` is the ABC for all transports.
- public child `VertexRagDataServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `VertexRagDataServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseVertexRagDataServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `VertexRagDataServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
