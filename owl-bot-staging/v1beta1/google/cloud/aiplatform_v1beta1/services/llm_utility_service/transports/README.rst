
transport inheritance structure
_______________________________

`LlmUtilityServiceTransport` is the ABC for all transports.
- public child `LlmUtilityServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `LlmUtilityServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseLlmUtilityServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `LlmUtilityServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
