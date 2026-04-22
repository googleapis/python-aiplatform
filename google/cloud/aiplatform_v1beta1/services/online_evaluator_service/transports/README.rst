
transport inheritance structure
_______________________________

`OnlineEvaluatorServiceTransport` is the ABC for all transports.
- public child `OnlineEvaluatorServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `OnlineEvaluatorServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseOnlineEvaluatorServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `OnlineEvaluatorServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
