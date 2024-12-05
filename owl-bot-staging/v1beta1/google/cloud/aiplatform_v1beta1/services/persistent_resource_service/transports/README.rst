
transport inheritance structure
_______________________________

`PersistentResourceServiceTransport` is the ABC for all transports.
- public child `PersistentResourceServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `PersistentResourceServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BasePersistentResourceServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `PersistentResourceServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
