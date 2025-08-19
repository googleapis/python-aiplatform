
transport inheritance structure
_______________________________

`DataFoundryServiceTransport` is the ABC for all transports.
- public child `DataFoundryServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `DataFoundryServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseDataFoundryServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `DataFoundryServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
