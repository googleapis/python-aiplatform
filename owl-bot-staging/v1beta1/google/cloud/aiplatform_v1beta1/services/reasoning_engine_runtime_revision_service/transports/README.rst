
transport inheritance structure
_______________________________

``ReasoningEngineRuntimeRevisionServiceTransport`` is the ABC for all transports.

- public child ``ReasoningEngineRuntimeRevisionServiceGrpcTransport`` for sync gRPC transport (defined in ``grpc.py``).
- public child ``ReasoningEngineRuntimeRevisionServiceGrpcAsyncIOTransport`` for async gRPC transport (defined in ``grpc_asyncio.py``).
- private child ``_BaseReasoningEngineRuntimeRevisionServiceRestTransport`` for base REST transport with inner classes ``_BaseMETHOD`` (defined in ``rest_base.py``).
- public child ``ReasoningEngineRuntimeRevisionServiceRestTransport`` for sync REST transport with inner classes ``METHOD`` derived from the parent's corresponding ``_BaseMETHOD`` classes (defined in ``rest.py``).
