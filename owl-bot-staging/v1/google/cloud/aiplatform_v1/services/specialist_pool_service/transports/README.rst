
transport inheritance structure
_______________________________

`SpecialistPoolServiceTransport` is the ABC for all transports.
- public child `SpecialistPoolServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `SpecialistPoolServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseSpecialistPoolServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `SpecialistPoolServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
