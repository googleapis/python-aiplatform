
transport inheritance structure
_______________________________

`MemoryBankServiceTransport` is the ABC for all transports.
- public child `MemoryBankServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `MemoryBankServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseMemoryBankServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `MemoryBankServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
