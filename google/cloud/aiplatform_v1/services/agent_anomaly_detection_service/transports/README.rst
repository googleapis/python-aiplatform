
transport inheritance structure
_______________________________

``AgentAnomalyDetectionServiceTransport`` is the ABC for all transports.

- public child ``AgentAnomalyDetectionServiceGrpcTransport`` for sync gRPC transport (defined in ``grpc.py``).
- public child ``AgentAnomalyDetectionServiceGrpcAsyncIOTransport`` for async gRPC transport (defined in ``grpc_asyncio.py``).
- private child ``_BaseAgentAnomalyDetectionServiceRestTransport`` for base REST transport with inner classes ``_BaseMETHOD`` (defined in ``rest_base.py``).
- public child ``AgentAnomalyDetectionServiceRestTransport`` for sync REST transport with inner classes ``METHOD`` derived from the parent's corresponding ``_BaseMETHOD`` classes (defined in ``rest.py``).
