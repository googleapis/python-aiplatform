
transport inheritance structure
_______________________________

`GenAiTuningServiceTransport` is the ABC for all transports.
- public child `GenAiTuningServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `GenAiTuningServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseGenAiTuningServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `GenAiTuningServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
