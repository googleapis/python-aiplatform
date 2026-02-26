
transport inheritance structure
_______________________________

`FeaturestoreOnlineServingServiceTransport` is the ABC for all transports.
- public child `FeaturestoreOnlineServingServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `FeaturestoreOnlineServingServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseFeaturestoreOnlineServingServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `FeaturestoreOnlineServingServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).
