# Changelog

### [1.1.1](https://www.github.com/googleapis/python-aiplatform/compare/v1.1.0...v1.1.1) (2021-06-22)


### Features

* add cancel method to pipeline client ([#488](https://www.github.com/googleapis/python-aiplatform/issues/488)) ([3b19fff](https://www.github.com/googleapis/python-aiplatform/commit/3b19fff399b85c92e661eb83a48a4c6636423518))


### Bug Fixes

* check if training_task_metadata is populated before logging backingCustomJob ([#494](https://www.github.com/googleapis/python-aiplatform/issues/494)) ([2e627f8](https://www.github.com/googleapis/python-aiplatform/commit/2e627f876e1d7dd03e5d6bd2e81e6234e361a9df))


### Documentation

* omit mention of Python 2.7 in 'CONTRIBUTING.rst' ([#1127](https://www.github.com/googleapis/python-aiplatform/issues/1127)) ([#489](https://www.github.com/googleapis/python-aiplatform/issues/489)) ([cbc47f8](https://www.github.com/googleapis/python-aiplatform/commit/cbc47f862f291b00b85718498571e0c737cb26a6))


### Miscellaneous Chores

* release 1.1.1 ([1a38ce2](https://www.github.com/googleapis/python-aiplatform/commit/1a38ce2f9879e1c42c0c6b25b72bd4836e3a1f73))

## [1.1.0](https://www.github.com/googleapis/python-aiplatform/compare/v1.0.1...v1.1.0) (2021-06-17)


### Features

* add aiplatform API Vizier service ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* add featurestore, index, metadata, monitoring, pipeline, and tensorboard services to aiplatform v1beta1 ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* add invalid_row_count to ImportFeatureValuesResponse and ImportFeatureValuesOperationMetadata ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* add pipeline client init and run to vertex AI ([1f1226f](https://www.github.com/googleapis/python-aiplatform/commit/1f1226fd8c745a7cd86c299fa0cfc2291947f3e7))
* add tensorboard support for CustomTrainingJob, CustomContainerTrainingJob, CustomPythonPackageTrainingJob ([#462](https://www.github.com/googleapis/python-aiplatform/issues/462)) ([8cfd611](https://www.github.com/googleapis/python-aiplatform/commit/8cfd61179af06232173b91b4d9fd633028823624))
* adds enhanced protos for time series forecasting ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* adds enhanced protos for time series forecasting ([#374](https://www.github.com/googleapis/python-aiplatform/issues/374)) ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* allow the prediction endpoint to be overridden ([#461](https://www.github.com/googleapis/python-aiplatform/issues/461)) ([c2cf612](https://www.github.com/googleapis/python-aiplatform/commit/c2cf61288326cad28ab474064b887687bc649d76))
* AutoMlImageSegmentationInputs.ModelType adds MOBILE_TF_LOW_LATENCY constant ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* AutoMlVideoClassificationInputs.ModelType adds MOBILE_JETSON_VERSATILE_1 constant ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* Expose additional attributes into Vertex SDK to close gap with GAPIC ([#477](https://www.github.com/googleapis/python-aiplatform/issues/477)) ([572a27c](https://www.github.com/googleapis/python-aiplatform/commit/572a27c7929e5686b61950e09e17134564987d50))
* ImageSegmentationPredictionResult.category_mask field changed to string data type ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* remove unsupported accelerator types ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* removes forecasting (time_series_forecasting proto) from public v1beta1 protos ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* removes unused protos from schema/ folders: schema/io_format.proto, schema/saved_query_metadata.proto ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* support additional_experiments for AutoML Tables and AutoML Forecasting ([#428](https://www.github.com/googleapis/python-aiplatform/issues/428)) ([b4211f2](https://www.github.com/googleapis/python-aiplatform/commit/b4211f2f60aead88107c08a18d30b0800b019593))
* support self-signed JWT flow for service accounts ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))


### Bug Fixes

* add async client to %name_%version/init.py ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* add target_column docstring ([#473](https://www.github.com/googleapis/python-aiplatform/issues/473)) ([c0543cd](https://www.github.com/googleapis/python-aiplatform/commit/c0543cdd1e9ba0efd18d7d1a442906938fc6db9a))
* configuring timeouts for aiplatform v1 methods ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* Enable MetadataStore to use credentials when aiplatfrom.init passed experiment and credentials. ([#460](https://www.github.com/googleapis/python-aiplatform/issues/460)) ([e7bf0d8](https://www.github.com/googleapis/python-aiplatform/commit/e7bf0d83d8bb0849a9bce886c958d13f5cbe5fab))
* exclude docs and tests from package ([#481](https://www.github.com/googleapis/python-aiplatform/issues/481)) ([b209904](https://www.github.com/googleapis/python-aiplatform/commit/b2099049484f66f4348ddd4448c676feecb0b46e))
* pass credentials to BQ and GCS clients ([#469](https://www.github.com/googleapis/python-aiplatform/issues/469)) ([481d172](https://www.github.com/googleapis/python-aiplatform/commit/481d172542ffd80e18f4fab5b01945be17d5e18c))
* remove display_name from FeatureStore ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* Remove URI attribute from Endpoint sample ([#478](https://www.github.com/googleapis/python-aiplatform/issues/478)) ([e3cbdd8](https://www.github.com/googleapis/python-aiplatform/commit/e3cbdd8322c854f526c8564f8bb61fb6525598d7))


### Documentation

* changes product name to Vertex AI ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* correct link to fieldmask ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))
* removes tinyurl links ([fdc968f](https://www.github.com/googleapis/python-aiplatform/commit/fdc968f49e89a5c7ca14692080c0ae7e8b6e0865))

### [1.0.1](https://www.github.com/googleapis/python-aiplatform/compare/v1.0.0...v1.0.1) (2021-05-21)


### Bug Fixes

* use resource name location when passed full resource name ([#421](https://www.github.com/googleapis/python-aiplatform/issues/421)) ([f40f322](https://www.github.com/googleapis/python-aiplatform/commit/f40f32289e1fbeb93b35e4b66f65d15528a6481c))

## [1.0.0](https://www.github.com/googleapis/python-aiplatform/compare/v0.9.0...v1.0.0) (2021-05-19)


### Features

* add custom and hp tuning ([#388](https://www.github.com/googleapis/python-aiplatform/issues/388)) ([aab9e58](https://www.github.com/googleapis/python-aiplatform/commit/aab9e589426331bfe7ac3f6efa97109e0bd0db0d))
* add tensorboard support to custom job and hyperparameter tuning job ([#404](https://www.github.com/googleapis/python-aiplatform/issues/404)) ([fa9bc39](https://www.github.com/googleapis/python-aiplatform/commit/fa9bc3943df55bc0d077ba9b02101ae792a6fb57))


### Bug Fixes

* tb-gcp-uploader to show flags in "--help" correctly ([#409](https://www.github.com/googleapis/python-aiplatform/issues/409)) ([9f603dd](https://www.github.com/googleapis/python-aiplatform/commit/9f603dd57868d893cb3be6cf70686fdce2706a6c))


### Miscellaneous Chores

* release 1.0.0 ([#407](https://www.github.com/googleapis/python-aiplatform/issues/407)) ([a2d7b68](https://www.github.com/googleapis/python-aiplatform/commit/a2d7b68e4016965f6e3771053f77e1745b44c403))

## [0.9.0](https://www.github.com/googleapis/python-aiplatform/compare/v0.8.0...v0.9.0) (2021-05-17)


### Features

* Add AutoML vision, Custom training job, and generic prediction samples ([#300](https://www.github.com/googleapis/python-aiplatform/issues/300)) ([cc1a708](https://www.github.com/googleapis/python-aiplatform/commit/cc1a7084f7715c94657d5a3b3374c0fc9a86a299))
* Add VPC Peering support to CustomTrainingJob classes ([#378](https://www.github.com/googleapis/python-aiplatform/issues/378)) ([56273f7](https://www.github.com/googleapis/python-aiplatform/commit/56273f7d1329a3404e58af4666297e6d6325f6ed))
* AutoML Forecasting, Metadata Experiment Tracking, Tensorboard uploader ([e94c9db](https://www.github.com/googleapis/python-aiplatform/commit/e94c9dbeac701390b25e6d70b0b0acc270636029))


### Bug Fixes

* **deps:** add packaging requirement ([#392](https://www.github.com/googleapis/python-aiplatform/issues/392)) ([47c1530](https://www.github.com/googleapis/python-aiplatform/commit/47c15300d6c8e879e1d7a10ad0c79e2bb4f18aee))
* enable aiplatform unit tests ([dcc459d](https://www.github.com/googleapis/python-aiplatform/commit/dcc459d55890961a8aa3cadb696c023a991eea05))
* rollback six to 1.15 ([#391](https://www.github.com/googleapis/python-aiplatform/issues/391)) ([066624b](https://www.github.com/googleapis/python-aiplatform/commit/066624b7c2ab3af281b7f63e47c990efbcd52673))

## [0.8.0](https://www.github.com/googleapis/python-aiplatform/compare/v0.7.1...v0.8.0) (2021-05-11)


### Features

* Add export model ([#353](https://www.github.com/googleapis/python-aiplatform/issues/353)) ([12c5be4](https://www.github.com/googleapis/python-aiplatform/commit/12c5be4690b23375468af16b00790c106232f539))
* add mbsdk video dataset samples ([#307](https://www.github.com/googleapis/python-aiplatform/issues/307)) ([24d6920](https://www.github.com/googleapis/python-aiplatform/commit/24d6920a530995a3a5c6ad6b25d0b867f7aebe27))
* Add service account support to Custom Training and Model deployment ([#342](https://www.github.com/googleapis/python-aiplatform/issues/342)) ([b4b1b12](https://www.github.com/googleapis/python-aiplatform/commit/b4b1b12d735e7c40717bd9ff8f8fd330d5e83738))
* add services to aiplatform_v1beta1 ([#367](https://www.github.com/googleapis/python-aiplatform/issues/367)) ([beb4032](https://www.github.com/googleapis/python-aiplatform/commit/beb4032e2b8c62e65fabcd8ef7cc4cf3d90535a3))
* Added create_training_pipeline_custom_job_sample and create_training_pipeline_custom_training_managed_dataset_sample and fixed create_training_pipeline_image_classification_sample ([#343](https://www.github.com/googleapis/python-aiplatform/issues/343)) ([1c6b998](https://www.github.com/googleapis/python-aiplatform/commit/1c6b998d9145309d79712f494a2b00b50a9a9bf4))
* Added create_training_pipeline_custom_package_job_sample and create_training_pipeline_custom_container_job_sample and reworked create_training_pipeline_custom_job_sample ([#351](https://www.github.com/googleapis/python-aiplatform/issues/351)) ([7abf8ef](https://www.github.com/googleapis/python-aiplatform/commit/7abf8ef54c606aa1d1093490369bb797c22fc331))
* Added default AutoMLTabularTrainingJob column transformations ([#357](https://www.github.com/googleapis/python-aiplatform/issues/357)) ([4fce8c4](https://www.github.com/googleapis/python-aiplatform/commit/4fce8c42504c6c5b86025d728819f61284ac5eef))
* Added deploy_model_with_dedicated_resources_sample, deploy_model_with_automatic_resources_sample, upload_model and get_model samples ([#337](https://www.github.com/googleapis/python-aiplatform/issues/337)) ([ef4f6f8](https://www.github.com/googleapis/python-aiplatform/commit/ef4f6f8aa5f6a3eea5d9d88e4604410d97b1ef54))
* Added explain tabular samples ([#348](https://www.github.com/googleapis/python-aiplatform/issues/348)) ([c95d1ce](https://www.github.com/googleapis/python-aiplatform/commit/c95d1cebec0a3e2bf6a25a76700d46a42e65376c))
* **aiplatform:** Add support for setting User agent header ([#364](https://www.github.com/googleapis/python-aiplatform/issues/364)) ([d50d26d](https://www.github.com/googleapis/python-aiplatform/commit/d50d26d18b892767dcf2e37d30d85b2b405e2708))
* expose env var in cust training class run func args ([#366](https://www.github.com/googleapis/python-aiplatform/issues/366)) ([7ae28b8](https://www.github.com/googleapis/python-aiplatform/commit/7ae28b84b0b8dd7068f8c0d0303776098816fab0))
* MBSDK Tabular samples ([#338](https://www.github.com/googleapis/python-aiplatform/issues/338)) ([4241738](https://www.github.com/googleapis/python-aiplatform/commit/4241738bf93c34611b777e4926a939549eb4134e))
* update featurestore ([#377](https://www.github.com/googleapis/python-aiplatform/issues/377)) ([bc17163](https://www.github.com/googleapis/python-aiplatform/commit/bc17163449a428f2caf17b521add3dde0b5c4391))


### Bug Fixes

* Add all supported uCAIP GA regions ([#350](https://www.github.com/googleapis/python-aiplatform/issues/350)) ([5e14c59](https://www.github.com/googleapis/python-aiplatform/commit/5e14c5969c53e50712295aa0343e7622d5db629d))
* **aiplatform:** Fix doc formatting ([#359](https://www.github.com/googleapis/python-aiplatform/issues/359)) ([857f63d](https://www.github.com/googleapis/python-aiplatform/commit/857f63d475463189ebb89b25d0ca08d9544c3bf3))
* Bump google-cloud-storage min version to 1.32.0 ([#371](https://www.github.com/googleapis/python-aiplatform/issues/371)) ([6fda925](https://www.github.com/googleapis/python-aiplatform/commit/6fda9255493684bed3820f2c81dca5599872b8b6))
* default model_display_name to _CustomTrainingJob.display_name when model_serving_container_image_uri is provided ([#324](https://www.github.com/googleapis/python-aiplatform/issues/324)) ([a5fa7a2](https://www.github.com/googleapis/python-aiplatform/commit/a5fa7a224570901988e5e7579c46cc2b823caa9b))
* env formatiing ([#379](https://www.github.com/googleapis/python-aiplatform/issues/379)) ([6bc4c61](https://www.github.com/googleapis/python-aiplatform/commit/6bc4c612d5471911f82ee5ada9fb3a9307ee836f))
* remove Optional type hint on deploy ([#345](https://www.github.com/googleapis/python-aiplatform/issues/345)) ([79b0ab1](https://www.github.com/googleapis/python-aiplatform/commit/79b0ab13e6d08a12ac0a0971a8001e9ddb8baf56))

### [0.7.1](https://www.github.com/googleapis/python-aiplatform/compare/v0.7.0...v0.7.1) (2021-04-14)


### Bug Fixes

* fix list failing without order_by and local sorting ([#320](https://www.github.com/googleapis/python-aiplatform/issues/320)) ([06e99db](https://www.github.com/googleapis/python-aiplatform/commit/06e99db849d954344aeb8bdefde41d1884e36315))

## [0.7.0](https://www.github.com/googleapis/python-aiplatform/compare/v0.6.0...v0.7.0) (2021-04-14)


### Features

* Add Custom Container Prediction support, move to single API endpoint ([#277](https://www.github.com/googleapis/python-aiplatform/issues/277)) ([ca7f6d6](https://www.github.com/googleapis/python-aiplatform/commit/ca7f6d64ea75349a841b53fe6ef6547942439e35))
* Add initial Model Builder SDK samples ([#265](https://www.github.com/googleapis/python-aiplatform/issues/265)) ([1230dc6](https://www.github.com/googleapis/python-aiplatform/commit/1230dc68a34c5b747186d31a25d1b8f40bf7a97e))
* Add list() method to all resource nouns ([#294](https://www.github.com/googleapis/python-aiplatform/issues/294)) ([3ec9386](https://www.github.com/googleapis/python-aiplatform/commit/3ec9386f8f766662c91922af66b8098ddfa1eb8f))
* add support for multiple client versions, change aiplatform from compat.V1BETA1 to compat.V1 ([#290](https://www.github.com/googleapis/python-aiplatform/issues/290)) ([89e3212](https://www.github.com/googleapis/python-aiplatform/commit/89e321246b6223a2355947d8dbd0161b84523478))
* Make aiplatform.Dataset private ([#296](https://www.github.com/googleapis/python-aiplatform/issues/296)) ([1f0d5f3](https://www.github.com/googleapis/python-aiplatform/commit/1f0d5f3e3f95ee5056545e9d4742b96e9380a22e))
* parse project location when passed full resource name to get apis ([#297](https://www.github.com/googleapis/python-aiplatform/issues/297)) ([674227d](https://www.github.com/googleapis/python-aiplatform/commit/674227d2e7ed4a4a4e180213dc1178dde7d65a3a))


### Bug Fixes

* add quotes to logged snippet ([0ecd0a8](https://www.github.com/googleapis/python-aiplatform/commit/0ecd0a8bbc5a2fc645877d0eb3b930e1b03a270a))
* make logging more informative during training ([#310](https://www.github.com/googleapis/python-aiplatform/issues/310)) ([9a4d991](https://www.github.com/googleapis/python-aiplatform/commit/9a4d99150a035b8dde7b4f9e72f25745af17b609))
* remove TPU from accelerator test cases ([57f4fcf](https://www.github.com/googleapis/python-aiplatform/commit/57f4fcf7637467f6176436f6d2e1f6c8be909c4a))

## [0.6.0](https://www.github.com/googleapis/python-aiplatform/compare/v0.5.1...v0.6.0) (2021-03-22)


### Features

* add Vizier service ([#266](https://www.github.com/googleapis/python-aiplatform/issues/266)) ([e5c1b1a](https://www.github.com/googleapis/python-aiplatform/commit/e5c1b1a4909d701efeb27f29af43a95516c51475))


### Bug Fixes

* skip create data labeling job sample tests ([#254](https://www.github.com/googleapis/python-aiplatform/issues/254)) ([116a29b](https://www.github.com/googleapis/python-aiplatform/commit/116a29b1efcebb15bad14c3c36d3591c09ef10be))

### [0.5.1](https://www.github.com/googleapis/python-aiplatform/compare/v0.5.0...v0.5.1) (2021-03-01)


### Bug Fixes

* fix create data labeling job samples tests ([#244](https://www.github.com/googleapis/python-aiplatform/issues/244)) ([3c440de](https://www.github.com/googleapis/python-aiplatform/commit/3c440dea14ad4d04b05ebf17ba4bcb031fe95b3e))
* fix predict sample tests for proto-plus==1.14.2 ([#250](https://www.github.com/googleapis/python-aiplatform/issues/250)) ([b1c9d88](https://www.github.com/googleapis/python-aiplatform/commit/b1c9d88646f00b034e2576890406325db5384f10))
* fix update export model sample, and add sample test ([#239](https://www.github.com/googleapis/python-aiplatform/issues/239)) ([20b8859](https://www.github.com/googleapis/python-aiplatform/commit/20b88592da3dd7344c7053d7fe652115ed42e4aa))


### Documentation

* update index.rst to include v1 ([#246](https://www.github.com/googleapis/python-aiplatform/issues/246)) ([82193ef](https://www.github.com/googleapis/python-aiplatform/commit/82193ef401258b17fd20895e2b0f6c95a39a24a1))

## [0.5.0](https://www.github.com/googleapis/python-aiplatform/compare/v0.4.0...v0.5.0) (2021-02-17)


### Features

* exposes v1 enhanced types and adds tests ([#226](https://www.github.com/googleapis/python-aiplatform/issues/226)) ([42b587d](https://www.github.com/googleapis/python-aiplatform/commit/42b587de2805b9efacb6e1eb5bf05e50ffb37797))
* LRO metadata ([#204](https://www.github.com/googleapis/python-aiplatform/issues/204)) ([2863dc0](https://www.github.com/googleapis/python-aiplatform/commit/2863dc0ba2337a0e997b95e2cb8669abd62635e3))
* moves manual enhanced lib edits outside of generated files ([#198](https://www.github.com/googleapis/python-aiplatform/issues/198)) ([a04a561](https://www.github.com/googleapis/python-aiplatform/commit/a04a5613cec36811db8768da5ea7c3229da3074b))
* updates python-aiplatform to v1 ([#212](https://www.github.com/googleapis/python-aiplatform/issues/212)) ([efc00ed](https://www.github.com/googleapis/python-aiplatform/commit/efc00ed6bb838dceaee7ad9469cc51d1500a365d))


### Bug Fixes

* correct text sentiment analysis sample ([#222](https://www.github.com/googleapis/python-aiplatform/issues/222)) ([0befde3](https://www.github.com/googleapis/python-aiplatform/commit/0befde36bfd4ff1b5161b7ceb3bb55f6e7d8ea37))
* **deps:** remove optional dependencies ([#187](https://www.github.com/googleapis/python-aiplatform/issues/187)) ([6589383](https://www.github.com/googleapis/python-aiplatform/commit/6589383f149fcf463d153fe76973bd874ff3967a))
* Fix sample test ([#215](https://www.github.com/googleapis/python-aiplatform/issues/215)) ([cdeb0ec](https://www.github.com/googleapis/python-aiplatform/commit/cdeb0ec30c334ff2b5d5e06bc976e824d6e18c04))
* reduces image size for test image ([#213](https://www.github.com/googleapis/python-aiplatform/issues/213)) ([3ed0e09](https://www.github.com/googleapis/python-aiplatform/commit/3ed0e0961f104762194d9ac598a81017ac9d2392))

## [0.4.0](https://www.github.com/googleapis/python-aiplatform/compare/v0.3.1...v0.4.0) (2021-01-08)


### Features

* add create_batch_prediction_job samples ([#67](https://www.github.com/googleapis/python-aiplatform/issues/67)) ([96a850f](https://www.github.com/googleapis/python-aiplatform/commit/96a850f2d24d7ae95f2cdec83a56362abecb85a2))
* add create_hyperparameter_tuning_job_python_package sample ([#76](https://www.github.com/googleapis/python-aiplatform/issues/76)) ([5155dee](https://www.github.com/googleapis/python-aiplatform/commit/5155dee5edd86fb700a91dfca01bddd4d6393410))
* add create_training_pipeline_custom_training_managed_dataset sample ([#75](https://www.github.com/googleapis/python-aiplatform/issues/75)) ([b012283](https://www.github.com/googleapis/python-aiplatform/commit/b012283c08cf8abc2974dc73ff7c2d3b8112a16b))
* add custom_job samples ([#69](https://www.github.com/googleapis/python-aiplatform/issues/69)) ([fb165b3](https://www.github.com/googleapis/python-aiplatform/commit/fb165b3632119b361a1936f367128f7146b49685))
* add data_labeling samples ([#78](https://www.github.com/googleapis/python-aiplatform/issues/78)) ([7daacd5](https://www.github.com/googleapis/python-aiplatform/commit/7daacd576dc96149c05e2908f276831337076316))
* add get_custom_job and get_hyperparameter_tuning_job samples ([#68](https://www.github.com/googleapis/python-aiplatform/issues/68)) ([26da7a7](https://www.github.com/googleapis/python-aiplatform/commit/26da7a7d4c1f5db2d2c3b2faedccbd9899c14a47))
* add schema namespace ([#140](https://www.github.com/googleapis/python-aiplatform/issues/140)) ([1cbd4a5](https://www.github.com/googleapis/python-aiplatform/commit/1cbd4a553fb8d035f687247ce87843167bf106ad))
* add video action recognition samples ([#77](https://www.github.com/googleapis/python-aiplatform/issues/77)) ([4c60ad6](https://www.github.com/googleapis/python-aiplatform/commit/4c60ad67dcd9026cb989d6e81dec4813cbae962f))
* Added tabular forecasting sample ([#156](https://www.github.com/googleapis/python-aiplatform/issues/156)) ([a23857b](https://www.github.com/googleapis/python-aiplatform/commit/a23857bc9be94c4a23ae7cf6f2eac75d8ea5ae95))
* Added tabular forecasting samples ([#128](https://www.github.com/googleapis/python-aiplatform/issues/128)) ([69fc7fd](https://www.github.com/googleapis/python-aiplatform/commit/69fc7fd415e1b404530fd3e2881a94c0441791cf))
* adds function/method enhancements, demo samples ([#122](https://www.github.com/googleapis/python-aiplatform/issues/122)) ([1a302d2](https://www.github.com/googleapis/python-aiplatform/commit/1a302d232d868a96bf6a41cbf92a550edcdb0673))
* adds text batch prediction samples ([#82](https://www.github.com/googleapis/python-aiplatform/issues/82)) ([ad09c29](https://www.github.com/googleapis/python-aiplatform/commit/ad09c29c1685a904966e34894c1c4ea77baa2425))
* initial generation of enhanced types ([#102](https://www.github.com/googleapis/python-aiplatform/issues/102)) ([5ddbf16](https://www.github.com/googleapis/python-aiplatform/commit/5ddbf16f35234dc1781de9d17310a345ac1524de))
* update create_training_pipeline samples ([#142](https://www.github.com/googleapis/python-aiplatform/issues/142)) ([624a08d](https://www.github.com/googleapis/python-aiplatform/commit/624a08d65c2088c0d5272a7b1b88983a8c7e6284))
* xai samples ([#83](https://www.github.com/googleapis/python-aiplatform/issues/83)) ([5cf3859](https://www.github.com/googleapis/python-aiplatform/commit/5cf38596d115da63cdddc8958b6ae8f455bdb9a6))


### Bug Fixes

* blacken on library, test files ([#135](https://www.github.com/googleapis/python-aiplatform/issues/135)) ([53cdbab](https://www.github.com/googleapis/python-aiplatform/commit/53cdbabdef6bd10488f49d0c3ed6f05149af32a6))
* predict image samples params ([#150](https://www.github.com/googleapis/python-aiplatform/issues/150)) ([7983b44](https://www.github.com/googleapis/python-aiplatform/commit/7983b448158cf8166ada54c60fb896d5658a2162))


### Documentation

* update readme ([#81](https://www.github.com/googleapis/python-aiplatform/issues/81)) ([19dc31a](https://www.github.com/googleapis/python-aiplatform/commit/19dc31a7e63ec112e9d0dc72e22db04910137d07))

### [0.3.1](https://www.github.com/googleapis/python-aiplatform/compare/v0.3.0...v0.3.1) (2020-11-13)


### Features

* add samples ([#56](https://www.github.com/googleapis/python-aiplatform/issues/56)) ([53cc5f5](https://www.github.com/googleapis/python-aiplatform/commit/53cc5f51bf3845fe688ee7b7a0494ff42c549f69))

## 0.3.0 (2020-11-05)


### Features

* generate v1beta1 ([e80a4fc](https://www.github.com/googleapis/python-aiplatform/commit/e80a4fcbdc84bdd76b159520c93943ada88c7210))
* python-aiplatform beta library ([#39](https://www.github.com/googleapis/python-aiplatform/issues/39)) ([81366dc](https://www.github.com/googleapis/python-aiplatform/commit/81366dcec173ed1e63b17e242c1ef74f623dd31b))
* regenerate v1beta1 ([#4](https://www.github.com/googleapis/python-aiplatform/issues/4)) ([4ddc426](https://www.github.com/googleapis/python-aiplatform/commit/4ddc426a6b4b8cd319fa885e363c94b35ef777d9))


### Bug Fixes

* re-add py sessions to noxfile ([#22](https://www.github.com/googleapis/python-aiplatform/issues/22)) ([3c713d5](https://www.github.com/googleapis/python-aiplatform/commit/3c713d5cf47bf343bf53583296daed6161d4f4ed))
