
transport inheritance structure
_______________________________

`FeatureOnlineStoreServiceTransport` is the ABC for all transports.
- public child `FeatureOnlineStoreServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `FeatureOnlineStoreServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseFeatureOnlineStoreServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `FeatureOnlineStoreServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
