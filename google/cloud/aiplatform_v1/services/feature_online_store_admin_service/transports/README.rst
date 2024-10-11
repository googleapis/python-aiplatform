
transport inheritance structure
_______________________________

`FeatureOnlineStoreAdminServiceTransport` is the ABC for all transports.
- public child `FeatureOnlineStoreAdminServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseFeatureOnlineStoreAdminServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `FeatureOnlineStoreAdminServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
