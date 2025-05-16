
transport inheritance structure
_______________________________

`VizierServiceTransport` is the ABC for all transports.
- public child `VizierServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `VizierServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseVizierServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `VizierServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
