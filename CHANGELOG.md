# Changelog

## [1.67.0](https://github.com/googleapis/python-aiplatform/compare/v1.66.0...v1.67.0) (2024-09-17)


### Features

* Add support for partial failures sink in import rag files. ([07e471e](https://github.com/googleapis/python-aiplatform/commit/07e471e0a069551f2c855e167e549fa92ac6af95))
* Adding Feature Store Vector DB option for RAG corpuses to SDK ([cfc3421](https://github.com/googleapis/python-aiplatform/commit/cfc3421fe8a883d459b66ed8c9f39697ded23f20))
* Adding Pinecone Vector DB option for RAG corpuses to SDK ([f78b953](https://github.com/googleapis/python-aiplatform/commit/f78b953f561b8697d07a530e89c7e727db1161ed))
* Adding Vertex Vector Search Vector DB option for RAG corpuses to SDK ([f882657](https://github.com/googleapis/python-aiplatform/commit/f882657183e34c8e07baa4b8dc9f45ed8bca9db7))
* Allow customizing pipeline caching options for model evaluation jobs. ([73490b2](https://github.com/googleapis/python-aiplatform/commit/73490b22a239cb1a3c31349f8db6cfbc5232e231))
* GenAI - Switched the GA version of the `generative_models` classes to use the v1  service APIs instead of v1beta1 ([66d84af](https://github.com/googleapis/python-aiplatform/commit/66d84afdd5b20f70b3ff62f25cc32ac0b324d5d5))


### Bug Fixes

* GenAI - Fixed `GenerativeModel.compute_tokens` for v1 API ([0de2987](https://github.com/googleapis/python-aiplatform/commit/0de298786c43427cb1a20b91cbabd1ce921c16da))
* Tensorboard - Fix error in tensorboard batch upload of nested dirs ([ab157c8](https://github.com/googleapis/python-aiplatform/commit/ab157c8ead718b2a1a1d13306c1256c1cb2561f1))


### Documentation

* Manually add summary overview page. ([0bc608a](https://github.com/googleapis/python-aiplatform/commit/0bc608a9c045007f12325231ed7f0069a40f469b))

## [1.66.0](https://github.com/googleapis/python-aiplatform/compare/v1.65.0...v1.66.0) (2024-09-11)


### Features

* Add max_wait_duration option to custom jobs. ([ee65917](https://github.com/googleapis/python-aiplatform/commit/ee65917fbc1edc58a7e57c3601f9329ffa1304b0))
* Add Ray 2.33 support to SDK Client Builder, remove deprecated protocol_version from ray client context. ([708a67b](https://github.com/googleapis/python-aiplatform/commit/708a67b9b781d41564058904d60af7db9beafbe0))
* Add support for version 2.33 for RoV Bigquery read/write, remove dead code from version 2.4 ([a4b6c60](https://github.com/googleapis/python-aiplatform/commit/a4b6c60051efe61ad590ede8682bd36b79cafc94))
* Update Ray system tests to be compatible with new RoV 2.33 changes ([8c7bf27](https://github.com/googleapis/python-aiplatform/commit/8c7bf2724037f1ad1081d29e9534f8d26b18d95f))
* Update setup.py for including Ray v2.33, restrict RoV prediction to 2.9.3 for now ([71c6f3c](https://github.com/googleapis/python-aiplatform/commit/71c6f3c6b48a001bfdbe5f5b47d787d4797ae9bf))


### Bug Fixes

* Identify nested Vertex Tensorboard profile runs for uploading when standard event data is not present ([0a08027](https://github.com/googleapis/python-aiplatform/commit/0a08027df7a7442af63522039445500ce1fdb7f1))
* Move region tag to include imports ([6d1f7fd](https://github.com/googleapis/python-aiplatform/commit/6d1f7fdaadade0f9f6a77c136490fac58d054ca8))
* Move region tag to include imports ([#4357](https://github.com/googleapis/python-aiplatform/issues/4357)) ([6d1f7fd](https://github.com/googleapis/python-aiplatform/commit/6d1f7fdaadade0f9f6a77c136490fac58d054ca8))
* Rollback change to tensorboard uploader causing increased latency ([879dbcd](https://github.com/googleapis/python-aiplatform/commit/879dbcd1ed49bee573df65e764914b708382404c))


### Documentation

* Update SDK Job Submission with Ray v2.33 updated comments ([7fda11f](https://github.com/googleapis/python-aiplatform/commit/7fda11fd25b5a78fcca69e48f9c734f2a8f86eb0))

## [1.65.0](https://github.com/googleapis/python-aiplatform/compare/v1.64.0...v1.65.0) (2024-09-04)


### ⚠ BREAKING CHANGES

* Tokenization - Deprecated `ComputeTokenResult.token_info_list` in favor of `ComputeTokenResult.tokens_info`

### Features

* Add support for system instruction and tools in tokenization. ([72fcc06](https://github.com/googleapis/python-aiplatform/commit/72fcc063ed4a086da0ad37ec2ac58860d4e79051))
* Add vector search alpha to rag retrieval for hybrid search ranking ([6624ebe](https://github.com/googleapis/python-aiplatform/commit/6624ebe22726942dd70781122352f47268ee2dee))
* Adding Weaviate Vector DB option for RAG corpuses to SDK ([9b28202](https://github.com/googleapis/python-aiplatform/commit/9b28202a1bb17f54e042301d6cdac3b6aa826797))
* GenAI - Added `system_instruction` and `tools` support to `GenerativeModel.count_tokens` ([50fca69](https://github.com/googleapis/python-aiplatform/commit/50fca693b2f3b1a0b61867dc136be5a468fb2b2f))
* GenAI - Added Llama3 support in GenAI batch prediction ([6166152](https://github.com/googleapis/python-aiplatform/commit/6166152844dc0078f7a5a02355ef3555cc428cfa))
* PrivateEndpoint.stream_raw_predict ([197f333](https://github.com/googleapis/python-aiplatform/commit/197f333be5a075d41f98b762cd933cd2e89cecae))
* Support reserved_ip_ranges for VPC network in Ray on Vertex cluster ([36a56b9](https://github.com/googleapis/python-aiplatform/commit/36a56b99f9e53d19d80c2bff3bf55c208988c518))
* Tokenization - Deprecated `ComputeTokenResult.token_info_list` in favor of `ComputeTokenResult.tokens_info` ([efbcb54](https://github.com/googleapis/python-aiplatform/commit/efbcb54e0d5df4d65a79e60afdbc5c328538aef6))


### Bug Fixes

* Tensorboard - Fixed bug in tensorboard uploader where profile logs are not uploaded from nested run directories. ([37627de](https://github.com/googleapis/python-aiplatform/commit/37627de4ec12b8c51abf41524b9e7e3adf2dab54))
* Tokenizers - Fixed `Tokenizer.compute_tokens` ([c29fa5d](https://github.com/googleapis/python-aiplatform/commit/c29fa5d98fc1c1550c039e84ff2f5725818c2231))

## [1.64.0](https://github.com/googleapis/python-aiplatform/compare/v1.63.0...v1.64.0) (2024-08-27)


### Features

* Endpoint - Add support for Prediction dedicated endpoint. predict/rawPredict/streamRawPredict can use dedicated DNS to access the dedicated endpoint. ([3d68777](https://github.com/googleapis/python-aiplatform/commit/3d687777d39b00280c22d2a14ddde3ba644febf7))
* GenAI - Added the model Distillation feature (private preview) ([a0d4ff2](https://github.com/googleapis/python-aiplatform/commit/a0d4ff20ceb1c48806d1711fdb2691dc34f9f1db))
* Grounding - Allow initialization of `grounding.VertexAISearch` with full resource name or data store ID, project ID, and location. ([f334321](https://github.com/googleapis/python-aiplatform/commit/f334321694bb3be1a421ee19a33fc973e5455da9))
* Evaluation - Make Rouge class available in base level init ([aed82a1](https://github.com/googleapis/python-aiplatform/commit/aed82a1bd5d8942ded4dd325a4eb1a5f73bc50c7))
* Feature Store - Read for online store w/private service connect ([7af80c6](https://github.com/googleapis/python-aiplatform/commit/7af80c624e026cfe8dda2d1644467a517f49b78f))
* Ray - Support autoscaling in Ray on Vertex ([961da42](https://github.com/googleapis/python-aiplatform/commit/961da429683db113a822300342484aaf1128cfc0))


### Bug Fixes

* Fix error in tensorboard uploader thrown when time_series_id is None ([d59a052](https://github.com/googleapis/python-aiplatform/commit/d59a0522ddc2131ab39b052e742a6472f84e0a5a))
* Evaluation - Fix typo in prompt templates: ([c8fa7a8](https://github.com/googleapis/python-aiplatform/commit/c8fa7a8cf53165354fa89e38fffc0ef4a821e211))


### Documentation

* **samples:** Adding code sample for vector search create streaming index ([71464e7](https://github.com/googleapis/python-aiplatform/commit/71464e7d2a57fa6770d2fcb7c5c0e669055c4cdb))

## [1.63.0](https://github.com/googleapis/python-aiplatform/compare/v1.62.0...v1.63.0) (2024-08-20)


### Features

* A new field `satisfies_pzs` is added to message `.google.cloud.aiplatform.v1.BatchPredictionJob` ([#4192](https://github.com/googleapis/python-aiplatform/issues/4192)) ([6919037](https://github.com/googleapis/python-aiplatform/commit/6919037e9513e922e9ffe197e68a99fb343c4fff))
* Add advanced PDF parsing option for RAG file import ([6e1dc06](https://github.com/googleapis/python-aiplatform/commit/6e1dc0658ffd875f4a3bbcab62976e15e997102e))
* Add multithreading for custom metric computation. ([2c93fc1](https://github.com/googleapis/python-aiplatform/commit/2c93fc17b4a76623209b7699a73d4e6c9c27cc81))
* Add progress bar for generating inference. ([b78714f](https://github.com/googleapis/python-aiplatform/commit/b78714f3cf8fc22f7caa193a7398efe3626c2c5f))
* Add progress bar to custom metrics. ([3974aec](https://github.com/googleapis/python-aiplatform/commit/3974aec92595870b6f33ecd016763f59d6630898))
* Add Prompt class support for configs and Prompt.generate_content wrapper ([7f1e031](https://github.com/googleapis/python-aiplatform/commit/7f1e0313842546b7e911ee3ef06d7193deb64a91))
* GenAI - Added seed parameter to the GenerationConfig class ([9f1e073](https://github.com/googleapis/python-aiplatform/commit/9f1e0739d837b3110b40b8806514ca3e49e2b1da))
* GenAI - Added the `Candidate.avg_logprobs` property ([de80695](https://github.com/googleapis/python-aiplatform/commit/de80695ad2359361a698cffbde2336417297ef35))
* GenAI - Released the `Prompt` feature to Public Preview ([64eeab8](https://github.com/googleapis/python-aiplatform/commit/64eeab8b3404e87c0cc19fb6862ff51ec8b95954))
* GenAI Evaluation: Add generic model-based `PointwiseMetric` and `PairwiseMetric` classes that allow customizing metric prompt templates. Add `PointwiseMetricPromptTemplate`, `PairwiseMetricPromptTemplate` classes to help formulate and customize metric prompt templates. Add `metric_column_mapping` parameter to `EvalTask` for metric prompt template input variable name mapping. ([fd38b49](https://github.com/googleapis/python-aiplatform/commit/fd38b49231bd1b35af57056b9e69a5427ddb114c))
* GenAI Evaluation: Open source model-based metric prompt template examples for Gemini 1.5 Pro autorater. Add `MetricPromptTemplateExamples` class to help retrieve model-based metric prompt templates. ([fd38b49](https://github.com/googleapis/python-aiplatform/commit/fd38b49231bd1b35af57056b9e69a5427ddb114c))
* GenAI Evaluation: Release GenAI Evaluation SDK GA features to `vertexai.preview` module. ([fd38b49](https://github.com/googleapis/python-aiplatform/commit/fd38b49231bd1b35af57056b9e69a5427ddb114c))
* Publish GenAI Evaluation SDK GA features to `vertexai.evaluation` module. Switch GenAI Evaluation Service client to v1 version. ([45e4251](https://github.com/googleapis/python-aiplatform/commit/45e42516fbc47db1c44a7669f2730a1590a992c2))


### Bug Fixes

* Add support of display_name to create_cached_content in python SDK ([ecc2d54](https://github.com/googleapis/python-aiplatform/commit/ecc2d54a84c03f7d06e987fba5f5c67fba109ce0))
* Always upload the pickled object and dependencies tarball when creating ReasoningEngine ([34ef5a3](https://github.com/googleapis/python-aiplatform/commit/34ef5a35bd91aea53c89650c20962dae29b3a535))
* Remove grouding attribution ([f6ece65](https://github.com/googleapis/python-aiplatform/commit/f6ece65d8f2933ddcb4ec1a08784f8d2c365f2de))


### Documentation

* Update Prompt docstring for batch prompting ([e96b6e6](https://github.com/googleapis/python-aiplatform/commit/e96b6e6f0574b96fc4b61f99c671ef6646fc4956))

## [1.62.0](https://github.com/googleapis/python-aiplatform/compare/v1.61.0...v1.62.0) (2024-08-13)


### Features

* Add metadata to evaluation result. ([375095e](https://github.com/googleapis/python-aiplatform/commit/375095e72cc4f43611710372a1e36753a891a710))
* Add Prompt class for multimodal prompt templating ([1bdc235](https://github.com/googleapis/python-aiplatform/commit/1bdc235ea64f8d63ce9d60d88cb873ee341d3ff9))
* Add support for query method in Vertex AI Extension SDK ([0008735](https://github.com/googleapis/python-aiplatform/commit/0008735968606a716add88072cff76f2fc552d7b))
* Add support for reservation affinity in custom training jobs. ([802609b](https://github.com/googleapis/python-aiplatform/commit/802609b1f5e5d8d41a77dafb5b1a2dbf01f2bd30))
* Add support for strategy in custom training jobs. ([a076191](https://github.com/googleapis/python-aiplatform/commit/a076191b8726363e1f7c47ef8343eb86cebf9918))
* Adding spot, reservation_affinity to Vertex SDK ([3e785bd](https://github.com/googleapis/python-aiplatform/commit/3e785bd9c9d3d11197ef930f563ee96231a67d84))
* Support api keys in initializer and create_client ([7404f67](https://github.com/googleapis/python-aiplatform/commit/7404f679246e41e0009ec2d49f05d669eb357f71))
* Support creating optimized online store with private service connect ([659ba3f](https://github.com/googleapis/python-aiplatform/commit/659ba3f287f9aa78840d4b9b9ca216002d5f1e6a))
* Support disable Cloud logging in Ray on Vertex ([accaa97](https://github.com/googleapis/python-aiplatform/commit/accaa9750d98b7a37b08da3bd2058d9cdd03bd5c))
* Support PSC-Interface in Ray on Vertex ([accaa97](https://github.com/googleapis/python-aiplatform/commit/accaa9750d98b7a37b08da3bd2058d9cdd03bd5c))


### Bug Fixes

* Added credentials, project, and location on PipelineJobSchedule init ([281c171](https://github.com/googleapis/python-aiplatform/commit/281c1710afc6cac49c02d926bee7a6c43b6ef851))
* Avoid breakage of langchain from orjson 3.10.7 ([c990f73](https://github.com/googleapis/python-aiplatform/commit/c990f73845f38e58ba2dddb372ad2f84d4a05479))
* Deprecate disable_attribution in GoogleSearchRetrieval. ([c68d559](https://github.com/googleapis/python-aiplatform/commit/c68d559b9d0fd7288b6775f57d05f474f5f7920a))


### Documentation

* Update the docstring for compute_tokens method. ([849e8d4](https://github.com/googleapis/python-aiplatform/commit/849e8d409e4838cad0a020231b806b0c9ef587ce))

## [1.61.0](https://github.com/googleapis/python-aiplatform/compare/v1.60.0...v1.61.0) (2024-08-05)


### Features

* Add a warning message for scheduled deprecation of Coherence metric class ([7f238fb](https://github.com/googleapis/python-aiplatform/commit/7f238fb3cebc44893b4e6959a77743cc4d96138e))
* Add deprecation messages for all model-based metric classes ([71c0fd3](https://github.com/googleapis/python-aiplatform/commit/71c0fd397139a95b6045f898e906ce11b2e7e8ce))
* Add support for task type (CODE_RETRIEVAL_QUERY) through get_embeddings. ([f2ce1e4](https://github.com/googleapis/python-aiplatform/commit/f2ce1e4caea9f344e39fc3232f697b1a6ea4f99a))
* Add system_instruction to LangchainAgent template. ([c71c3dd](https://github.com/googleapis/python-aiplatform/commit/c71c3ddbfeaa577dfce683b3299d94e77d1c4895))
* Adding Slack and Jira data connector for RAG to SDK ([d92e7c9](https://github.com/googleapis/python-aiplatform/commit/d92e7c91d280dd417d2c2a2cf5abc36592888593))
* Allow protobuf 5.x ([ce9cd5d](https://github.com/googleapis/python-aiplatform/commit/ce9cd5def14597822c1d071e438cf63b6d4ba3ca))
* LVM - Release `ImageGenerationModel` to GA ([718c199](https://github.com/googleapis/python-aiplatform/commit/718c1997778310b6898344b2e5a34513e7a82e5f))
* Support "update" for reasoning engine. ([b73ef3e](https://github.com/googleapis/python-aiplatform/commit/b73ef3eaa2d88dbc8071e3a4f0c7da934683fc2a))
* Update Rapid Evaluation Service QPS. Add a customizable evaluation service QPS parameter. ([9ee9289](https://github.com/googleapis/python-aiplatform/commit/9ee9289fbe5face719515e453d4f81648b44e7b1))


### Documentation

* Change init sample to use vertexai ([829e0f6](https://github.com/googleapis/python-aiplatform/commit/829e0f6fd286cf2de2ac307a836305766473faef))
* Make small fixes to file import documentation ([f7d65c3](https://github.com/googleapis/python-aiplatform/commit/f7d65c32948c54bcf3a6927639f2173b556bb310))

## [1.60.0](https://github.com/googleapis/python-aiplatform/compare/v1.59.0...v1.60.0) (2024-07-24)


### Features

* Add preflight validations to PipelineJob submit and run methods. ([c5a3535](https://github.com/googleapis/python-aiplatform/commit/c5a35354485a577dd5477449bc4bdcd7866a8df4))
* Add support for langchain v0.2+ package versions in default installation ([259b638](https://github.com/googleapis/python-aiplatform/commit/259b638300054e13b2dfe1d3f32d7126bbb18b15))
* GenAI - Added tokenization support via `GenerativeModel.compute_tokens` ([cfe0cc6](https://github.com/googleapis/python-aiplatform/commit/cfe0cc62cbf8dc12b4b021377ddd613d1072fe95))
* GenAI - ContextCaching - allow from_cached_content to take the cached_content resource name ([8f53902](https://github.com/googleapis/python-aiplatform/commit/8f53902b933f3abf0c9a222f45c2fa7ada727505))
* Make count_tokens generally-available at TextEmbeddingModel. ([efb8413](https://github.com/googleapis/python-aiplatform/commit/efb84134094ab87d6a2fac48a1f2f1b2199c1818))


### Bug Fixes

* Avoid throw error when Part.text is empty in modality content checks ([bbd4a49](https://github.com/googleapis/python-aiplatform/commit/bbd4a49d398052ba2c20e09f8f052e6f766d8fca))
* Correct logit_bias type annotation to accept keys as strings ([2676d25](https://github.com/googleapis/python-aiplatform/commit/2676d25e62d1bda68b0fbef274d0e669a6670415))
* Create FV embedding dimensions sample - dimensions should be an int ([2aa221e](https://github.com/googleapis/python-aiplatform/commit/2aa221ec994fea63bd73e2cfe760a314b990e4b0))
* Fix the sync option for Model Monitor job creation ([22151e2](https://github.com/googleapis/python-aiplatform/commit/22151e29e752dd8f27188046f8c8866c004ca196))
* Include DeploymentResourcePool class in aiplatform top-level sdk module ([ecc4f09](https://github.com/googleapis/python-aiplatform/commit/ecc4f09054b3e314b51ebf622b7241a5ab4ff072))
* Overriding the current TracerProvider when enabling tracing ([1476c10](https://github.com/googleapis/python-aiplatform/commit/1476c10f2fd91c02cd98799564a33ede742bc6e0))
* Pass the project ID from vertexai.init to CloudTraceSpanExporter when enable_tracing=True for LangchainAgent ([3ec043e](https://github.com/googleapis/python-aiplatform/commit/3ec043eefb053739f767d5199b1941bbc3c49120))


### Documentation

* GenAI - Update README.md for Vertex Generative AI SDK for Python to add subsections to the right nav. ([42af742](https://github.com/googleapis/python-aiplatform/commit/42af742d808abdca56b84b3381388a36c8454f1b))

## [1.59.0](https://github.com/googleapis/python-aiplatform/compare/v1.58.0...v1.59.0) (2024-07-09)


### Features

* Add model and contents fields to ComputeTokensRequest v1 ([f6e7b9c](https://github.com/googleapis/python-aiplatform/commit/f6e7b9c0f1656edba0c69d02475c2a7337fefb99))
* Add model and contents fields to ComputeTokensRequest v1beta1 ([f6e7b9c](https://github.com/googleapis/python-aiplatform/commit/f6e7b9c0f1656edba0c69d02475c2a7337fefb99))
* Add role field to TokensInfo v1 ([f6e7b9c](https://github.com/googleapis/python-aiplatform/commit/f6e7b9c0f1656edba0c69d02475c2a7337fefb99))
* Add role field to TokensInfo v1beta1 ([f6e7b9c](https://github.com/googleapis/python-aiplatform/commit/f6e7b9c0f1656edba0c69d02475c2a7337fefb99))
* GenAI - Tuning - Released the Supervised Fine Tuning feature o GA ([ae47639](https://github.com/googleapis/python-aiplatform/commit/ae47639c1dc03a89d83c8de1609aaa25af9a1368))


### Bug Fixes

* **deps:** Require proto-plus 1.22.3 ([4131e65](https://github.com/googleapis/python-aiplatform/commit/4131e6583799d16b5032fecd73d4539fb05f0cd1))
* Offline store - set application name + remove session param ([7395665](https://github.com/googleapis/python-aiplatform/commit/7395665bcd847a62b25392d98848a6fb130f5286))

## [1.58.0](https://github.com/googleapis/python-aiplatform/compare/v1.57.0...v1.58.0) (2024-07-03)


### Features

* Add deploy_metadata to PublisherModel.Deploy v1 ([71e41c8](https://github.com/googleapis/python-aiplatform/commit/71e41c8eeb0e081d67660161a31f6a228d7b0502))
* Add deploy_metadata to PublisherModel.Deploy v1beta1 ([b5c3cdd](https://github.com/googleapis/python-aiplatform/commit/b5c3cdd737acd695301c9a564d8f91371288f9f1))
* Add display tuning job button for Ipython environments when getting an existing job ([872b455](https://github.com/googleapis/python-aiplatform/commit/872b455bcdda59d73d7060aaaa20a0b0e86e8cbb))
* Add private_service_connect_config and service_attachment fields to DedicatedServingEndpoint v1 ([71e41c8](https://github.com/googleapis/python-aiplatform/commit/71e41c8eeb0e081d67660161a31f6a228d7b0502))
* Add satisfies_pzs and satisfies_pzi fields to Model v1 ([71e41c8](https://github.com/googleapis/python-aiplatform/commit/71e41c8eeb0e081d67660161a31f6a228d7b0502))
* Add satisfies_pzs and satisfies_pzi fields to Model v1beta1 ([b5c3cdd](https://github.com/googleapis/python-aiplatform/commit/b5c3cdd737acd695301c9a564d8f91371288f9f1))
* Add satisfies_pzs and satisfies_pzi fields to Tensorboard v1 ([71e41c8](https://github.com/googleapis/python-aiplatform/commit/71e41c8eeb0e081d67660161a31f6a228d7b0502))
* Add satisfies_pzs and satisfies_pzi fields to Tensorboard v1beta1 ([b5c3cdd](https://github.com/googleapis/python-aiplatform/commit/b5c3cdd737acd695301c9a564d8f91371288f9f1))
* Add UpdateDeploymentResourcePool method to DeploymentResourcePoolService v1 ([71e41c8](https://github.com/googleapis/python-aiplatform/commit/71e41c8eeb0e081d67660161a31f6a228d7b0502))
* Add UpdateDeploymentResourcePool method to DeploymentResourcePoolService v1beta1 ([b5c3cdd](https://github.com/googleapis/python-aiplatform/commit/b5c3cdd737acd695301c9a564d8f91371288f9f1))
* Add use_effective_order field to BleuSpec v1beta1 ([b5c3cdd](https://github.com/googleapis/python-aiplatform/commit/b5c3cdd737acd695301c9a564d8f91371288f9f1))
* GenAI - Evaluation - Add a progress bar for evaluation service requests ([bbffb0d](https://github.com/googleapis/python-aiplatform/commit/bbffb0d5bfe0509399c801d849311a6201caa633))
* GenAI - Evaluation - Implement rate limiter and refactor parallelization for online evaluation service requests ([bbffb0d](https://github.com/googleapis/python-aiplatform/commit/bbffb0d5bfe0509399c801d849311a6201caa633))
* GenAI - Evaluation - Return partial evaluation results with error logging ([bbffb0d](https://github.com/googleapis/python-aiplatform/commit/bbffb0d5bfe0509399c801d849311a6201caa633))
* Migrate DeploymentResourcePool and associated functionality to V1 namespace for GA launch of model co-hosting. ([1474d98](https://github.com/googleapis/python-aiplatform/commit/1474d988fa63cbbb3b200634719bc245cab6a448))


### Bug Fixes

* `IndexConfig` - use TreeAhConfig as default `algorithm_config`. ([341d287](https://github.com/googleapis/python-aiplatform/commit/341d287719cabdaa1041cdefe9b65b77f1e4bc3b))
* LVM - Update `Video.load_from_file()` to support storage.googleapis.com links ([b63f960](https://github.com/googleapis/python-aiplatform/commit/b63f9600f743067ae97103dfd43f4392b9f6de56))


### Documentation

* Update comments of AutoscalingSpec v1 ([71e41c8](https://github.com/googleapis/python-aiplatform/commit/71e41c8eeb0e081d67660161a31f6a228d7b0502))
* Update comments of AutoscalingSpec v1beta1 ([b5c3cdd](https://github.com/googleapis/python-aiplatform/commit/b5c3cdd737acd695301c9a564d8f91371288f9f1))
* Update import paths for Gemini README ([46b3042](https://github.com/googleapis/python-aiplatform/commit/46b30425e8c86588256bf75f857078caeb9d7dee))

## [1.57.0](https://github.com/googleapis/python-aiplatform/compare/v1.56.0...v1.57.0) (2024-06-26)


### Features

* Add _ModelBasedMetric base class to `vertexai.preview.evaluation.metrics` and allow metric spec customization ([536f1d5](https://github.com/googleapis/python-aiplatform/commit/536f1d5bfc0e03acaf48097446e6b3c9577961c7))
* Add `_AutomaticMetric` type and support customizing metric spec for automatic pointwise metrics. Add `Rouge` metric to `vertexai.preview.evaluation.metrics` ([f6b6dee](https://github.com/googleapis/python-aiplatform/commit/f6b6deed2a3973ed684898d30e209af4291b8f3a))
* Add 12 model-based pointwise metric classes to `vertexai.preview.evaluation.metrics` ([4742a87](https://github.com/googleapis/python-aiplatform/commit/4742a879c8f61c4798194a32243cf9a666477a02))
* Add display tuning job button for Ipython environments when starting a new job ([b1e9a6c](https://github.com/googleapis/python-aiplatform/commit/b1e9a6c3bdce42278f3c868667a652e8867d393e))
* Add encryption_spec to TuningJob ([5a6ce78](https://github.com/googleapis/python-aiplatform/commit/5a6ce7817e11c32fb138e1ba51825a18a12f8851))
* Add enum value MALFORMED_FUNCTION_CALL to `.google.cloud.aiplatform.v1beta1.content.Candidate.FinishReason` ([5a6ce78](https://github.com/googleapis/python-aiplatform/commit/5a6ce7817e11c32fb138e1ba51825a18a12f8851))
* Add fields grounding_chunks and grounding_supports to GroundingMetadata ([5a6ce78](https://github.com/googleapis/python-aiplatform/commit/5a6ce7817e11c32fb138e1ba51825a18a12f8851))
* Add MALFORMED_FUNCTION_CALL to FinishReason ([5a6ce78](https://github.com/googleapis/python-aiplatform/commit/5a6ce7817e11c32fb138e1ba51825a18a12f8851))
* Add preflight_validations to PipelineJob ([5a6ce78](https://github.com/googleapis/python-aiplatform/commit/5a6ce7817e11c32fb138e1ba51825a18a12f8851))
* Add streamRawPredict rpc to prediction service ([5a6ce78](https://github.com/googleapis/python-aiplatform/commit/5a6ce7817e11c32fb138e1ba51825a18a12f8851))
* Add support for hybrid queries for private endpoint in Matching Engine Index Endpoint. ([ce65eab](https://github.com/googleapis/python-aiplatform/commit/ce65eab2fd41aee06b378daa4ebd4dd7b53e1fca))
* Add text field in Segment ([5a6ce78](https://github.com/googleapis/python-aiplatform/commit/5a6ce7817e11c32fb138e1ba51825a18a12f8851))
* Change the icon for the model evaluation link to a lightbulb for ipython environments ([7dad7f0](https://github.com/googleapis/python-aiplatform/commit/7dad7f036b6c686379771c76314cae2585e384d8))
* Endpoint.direct_predict ([9351e1a](https://github.com/googleapis/python-aiplatform/commit/9351e1ac51a0dd5dc0739676b9790e3e202529ad))
* Endpoint.direct_predict_async ([9351e1a](https://github.com/googleapis/python-aiplatform/commit/9351e1ac51a0dd5dc0739676b9790e3e202529ad))
* Endpoint.direct_raw_predict ([9351e1a](https://github.com/googleapis/python-aiplatform/commit/9351e1ac51a0dd5dc0739676b9790e3e202529ad))
* Endpoint.direct_raw_predict_async ([9351e1a](https://github.com/googleapis/python-aiplatform/commit/9351e1ac51a0dd5dc0739676b9790e3e202529ad))
* Endpoint.stream_direct_predict ([9351e1a](https://github.com/googleapis/python-aiplatform/commit/9351e1ac51a0dd5dc0739676b9790e3e202529ad))
* Endpoint.stream_direct_raw_predict ([9351e1a](https://github.com/googleapis/python-aiplatform/commit/9351e1ac51a0dd5dc0739676b9790e3e202529ad))
* Endpoint.stream_raw_predict ([9351e1a](https://github.com/googleapis/python-aiplatform/commit/9351e1ac51a0dd5dc0739676b9790e3e202529ad))
* Expose new text embedding tuning parameters in GA namespace. ([249a5fa](https://github.com/googleapis/python-aiplatform/commit/249a5fa901a2f7572698892eac7fdc7dc6ca0ad7))
* GenAI - Batch Prediction - Added support for tuned GenAI models ([a90ee8d](https://github.com/googleapis/python-aiplatform/commit/a90ee8da161f95aa489aa4f09309a3fa34320a4c))
* Mark default profile run as complete when calling end_upload_tb_log ([6397f30](https://github.com/googleapis/python-aiplatform/commit/6397f3069cd164f5fb1423f9c73c5e1f6ae30714))
* Sample code for Vertex AI Feature Store ([2c28b4e](https://github.com/googleapis/python-aiplatform/commit/2c28b4eb8184d251bf612bd77f614e9b58e3ba6a))
* Sample code for Vertex AI Feature Store ([2fbf5a5](https://github.com/googleapis/python-aiplatform/commit/2fbf5a5704612d3f87e157e9ebeb8f6583386a06))
* Tokenization - Added count_tokens support for local tokenization ([a8a4c30](https://github.com/googleapis/python-aiplatform/commit/a8a4c30e492513708d1dd1e3e0dbd67a3918e172))
* Update rich html Ray on Vertex Client Context widget ([380c9d9](https://github.com/googleapis/python-aiplatform/commit/380c9d973480961c82ad22b4b298ce31c965272b))


### Bug Fixes

* `FeatureGroup.create()` - remove unused entity id column param ([c46f3e9](https://github.com/googleapis/python-aiplatform/commit/c46f3e9240eb34cf3f38fe73356d893c96edabde))
* Fix bug where retry_timeout does not work with evaluation with experiments ([a31ac4d](https://github.com/googleapis/python-aiplatform/commit/a31ac4da5de5bace03aeb531bea372953c66ac0c))
* Use default run_name in Tensorboard uploader for direct directory upload. ([78a92a1](https://github.com/googleapis/python-aiplatform/commit/78a92a1bad2bd4d75b85debfd401e122afa0dc11))


### Documentation

* A comment for field `distibution` in message `.google.cloud.aiplatform.v1beta1.model_monitoring_stats.ModelMonitoringStatsDataPoint` is changed. ([5a6ce78](https://github.com/googleapis/python-aiplatform/commit/5a6ce7817e11c32fb138e1ba51825a18a12f8851))
* A comment for field `name` in message `.google.cloud.aiplatform.v1beta1.cached_content.CachedContent` is changed ([5a6ce78](https://github.com/googleapis/python-aiplatform/commit/5a6ce7817e11c32fb138e1ba51825a18a12f8851))
* A comment for field `source` in message `.google.cloud.aiplatform.v1beta1.tool.Retrieval` is added. ([5a6ce78](https://github.com/googleapis/python-aiplatform/commit/5a6ce7817e11c32fb138e1ba51825a18a12f8851))
* Update the documentation for the `time_series_dataset` and `video_dataset` classes ([2cf4cb9](https://github.com/googleapis/python-aiplatform/commit/2cf4cb905236cd42d9c351aff26564504ed4b72e))

## [1.56.0](https://github.com/googleapis/python-aiplatform/compare/v1.55.0...v1.56.0) (2024-06-18)


### Features

* Add `retry_timeout` to EvalTask in `vertexai.preview.evaluation` ([4d9ee9d](https://github.com/googleapis/python-aiplatform/commit/4d9ee9dc6c046fd71e2f3176981a2a108fbbaeeb))
* Add hybrid query example to vector search sample. ([510da5e](https://github.com/googleapis/python-aiplatform/commit/510da5ef3bcaa507288571fc7e066f578fde329f))
* Add metric classes for 2 pairwise metrics for rapid evaluation SDK. ([831c8e4](https://github.com/googleapis/python-aiplatform/commit/831c8e45ee88f70efcdaba7dfed1856837074357))
* Add pipeline_job_name to allow PipelineJob.get(pipeline_job_name) ([32e3b22](https://github.com/googleapis/python-aiplatform/commit/32e3b22993a83414ee60e52b0c95bd8b63543787))
* Add sample code show how to create an optimized private online store in Vertex AI Feature Store. ([e352175](https://github.com/googleapis/python-aiplatform/commit/e3521751ecb79d5f711658c39d2dd5b204c191c5))
* GenAI - Context Caching - add get() classmethod and refresh() instance method ([6be874a](https://github.com/googleapis/python-aiplatform/commit/6be874a7c6c43b7acbf5926e38e56d2ab367f5a1))
* GenAI - Context Caching - also print model_name and expire_time. ([d548c11](https://github.com/googleapis/python-aiplatform/commit/d548c1128d8b6abc7ed8007436bc868a688fcace))
* GenAI - Tuning - Added support for CMEK ([eb651bc](https://github.com/googleapis/python-aiplatform/commit/eb651bc2ed60ba12d88998115470c12d858892ef))


### Bug Fixes

* Do not reset aiplatform.Experiment or aiplatform.ExperimentRun unnecessarily when running tensorboard uploader. ([28a091a](https://github.com/googleapis/python-aiplatform/commit/28a091ab609ae3c086bb35ee4901c61108a4e75e))


### Documentation

* Update the documentation for the `time_series_dataset` and `video_dataset` classes ([d5dc7b5](https://github.com/googleapis/python-aiplatform/commit/d5dc7b5697eb4c7e86ec9e108454a30c8c7028d7))

## [1.55.0](https://github.com/googleapis/python-aiplatform/compare/v1.54.1...v1.55.0) (2024-06-12)


### Features

* view model evaluations when AustoSxS pipeline completes ([17c59c4c2](https://github.com/googleapis/python-aiplatform/commit/17c59c4c2))
* Add support for user-configurable 1P embedding models and quota for RAG ([8b3beb666](https://github.com/googleapis/python-aiplatform/commit/8b3beb666))
* Add Webpage Browser Extension to Vertex AI Extension SDK ([c222f4bdb](https://github.com/googleapis/python-aiplatform/commit/c222f4bdb))
* Add enable_tracing to LangchainAgent. ([cad035cb3](https://github.com/googleapis/python-aiplatform/commit/cad035cb3))
* Implement multithreaded batch inference in Rapid Evaluation SDK for performance improvement ([3c6d1732b](https://github.com/googleapis/python-aiplatform/commit/3c6d1732b))

### Bug Fixes

* support VPC and BYOSA case in Ray on Vertex JobSubmissionClient using cluster resource name ([662d039c9](https://github.com/googleapis/python-aiplatform/commit/662d039c9))
* Include tensorboard profiler requirements when installing google-cloud-aiplatform[tensorboard] ([4f1b5593b](https://github.com/googleapis/python-aiplatform/commit/4f1b5593b))
* fix numerical NaN experiment run logging error in EvalTask. ([641faec0b](https://github.com/googleapis/python-aiplatform/commit/641faec0b))
* Generate uuid run_name when run_name_prefix is not specified. ([4e2d87f9a](https://github.com/googleapis/python-aiplatform/commit/4e2d87f9a))

### Documentation

* Update the documentation for the `image_dataset` class ([583cb9313](https://github.com/googleapis/python-aiplatform/commit/583cb9313))
* Include imports in experiment_tracking samples directly in cloud.google.com snippets. ([3ffb6cba7](https://github.com/googleapis/python-aiplatform/commit/3ffb6cba7))


## [1.54.1](https://github.com/googleapis/python-aiplatform/compare/v1.54.0...v1.54.1) (2024-06-07)


### Bug Fixes

* _append_tool_name list index out of range ([#3914](https://github.com/googleapis/python-aiplatform/issues/3914)) ([323c2f5](https://github.com/googleapis/python-aiplatform/commit/323c2f5b4a63451c8bb3ef1eb5457cc674c4f56f))

## [1.54.0](https://github.com/googleapis/python-aiplatform/compare/v1.53.0...v1.54.0) (2024-06-06)

### BREAKING CHANGES
* Remove Vertex SDK data science package ([ec4ec8f](https://github.com/googleapis/python-aiplatform/commit/ec4ec8f1214b3da12728c30a002b7f4632f4a90e))

### Features

* Add display experiment run button for Ipython environments ([ba65828](https://github.com/googleapis/python-aiplatform/commit/ba6582856b1d7f9a6ac8f90a3fa5ea6723ac64ab))
* Add hybrid search for public find_neighbors() call. ([9d35617](https://github.com/googleapis/python-aiplatform/commit/9d3561738d577129cb222417bf208166825d8043))
* Enable Ray Job submission without VPC peering ([37875b5](https://github.com/googleapis/python-aiplatform/commit/37875b507f25c31ac4a84e4fefe3cbba565682e3))
* GenAI - Allowed callable functions to return values directly in Automatic Function Calling ([768af67](https://github.com/googleapis/python-aiplatform/commit/768af6772ade2b67b90a05ae3db95039a3f2786d))
* GenAI - Release ToolConfig to GA ([bc8b14a](https://github.com/googleapis/python-aiplatform/commit/bc8b14a7c9c632721db9166dc9b63eec17d31afd))
* Sample code for Vertex AI Feature Store ([6c14e8b](https://github.com/googleapis/python-aiplatform/commit/6c14e8b31bd950ac4f4a862b4e62ead42fe30463))
* Support VertexTool in langchain template. ([28a3c56](https://github.com/googleapis/python-aiplatform/commit/28a3c56fdcfa4fab819e8f79d235f6576febdfce))


### Bug Fixes

* Allow non-lro delete method ([c23c0ad](https://github.com/googleapis/python-aiplatform/commit/c23c0ada07146f0e5ce6a787c8255313f7c4a06c))
* Deep copy dataset before passing it to evaluation ([019b610](https://github.com/googleapis/python-aiplatform/commit/019b6102c2dc98550592cde0adfbb4958faddbef))
* Ensure model starts with publishers/ when users provide resource path from models/ ([d689331](https://github.com/googleapis/python-aiplatform/commit/d689331af5172cdfe7428333536954e8339f8ab4))
* Fix failed unit tests due to google-cloud-storage upgrade. ([945b9e4](https://github.com/googleapis/python-aiplatform/commit/945b9e4835149111cd33beaee4301f3d8f05f59d))
* Generalize RAG files import from Google Drive ([88c6a6a](https://github.com/googleapis/python-aiplatform/commit/88c6a6a4f11285d429c3777f59101e53e4672185))
* Set upper bound of setuptools to unbreak public Colab for using vertex_ray namespace ([6cc45bb](https://github.com/googleapis/python-aiplatform/commit/6cc45bbbea154d087c1dfe4756d4e15f21b1d844))

## [1.53.0](https://github.com/googleapis/python-aiplatform/compare/v1.52.0...v1.53.0) (2024-05-30)


### Features

* Add a `cloneable` protocol for Reasoning Engine. ([8960a80](https://github.com/googleapis/python-aiplatform/commit/8960a8022dc7556413a83786fc14e25e91df8362))
* Add labels parameter to the supervised tuning train method ([f7c5567](https://github.com/googleapis/python-aiplatform/commit/f7c5567b6e44895033cf52e6f80a1bb55fb5f647))
* Added reboot command for PersistentResource ([7785f8c](https://github.com/googleapis/python-aiplatform/commit/7785f8c327ee17da4827840396c49063b8e6d18f))
* Added the new `GenerationConfig.response_schema` field ([#3772](https://github.com/googleapis/python-aiplatform/issues/3772)) ([5436d88](https://github.com/googleapis/python-aiplatform/commit/5436d88bf8d6c9b6a9df5a496afdc25106463d30))
* Enable Tensorboard profile plugin in all regions by default. ([8a4a41a](https://github.com/googleapis/python-aiplatform/commit/8a4a41afe47aaff2f69a73e5011b34bcba5cd2e9))
* GenAI - Added the `response_schema` parameter to the `GenerationConfig` class ([b5e2c02](https://github.com/googleapis/python-aiplatform/commit/b5e2c0204070e5f7fb695d39c7e5d23f937dbffd))
* LLM - Added the `seed` parameter to the `TextGenerationModel`'s `predict` methods ([cb2f4aa](https://github.com/googleapis/python-aiplatform/commit/cb2f4aa021af05c90e54c5e41c1c91f9d8bf13b8))


### Bug Fixes

* Create run_name when run_name_prefix is not specified for Tensorboard uploader. ([ac17d87](https://github.com/googleapis/python-aiplatform/commit/ac17d876074f3fb51ab6c04beff0d3985df54633))
* GenAI - Tuning - Supervised - Fix `adapter_size` parameter handling to match enum values. ([1cc22c3](https://github.com/googleapis/python-aiplatform/commit/1cc22c3c3561f7c6374d32fafd45839256064958))
* Model Monitor console uri. ([71fbc81](https://github.com/googleapis/python-aiplatform/commit/71fbc81df8fa0d7c863233abc3ed6d40666c1623))

## [1.52.0](https://github.com/googleapis/python-aiplatform/compare/v1.51.0...v1.52.0) (2024-05-21)


### Features

* Add FeatureGroup delete ([f9011e0](https://github.com/googleapis/python-aiplatform/commit/f9011e0b1b4ea8470849ecdd5ba9e086c73b778b))
* Add support for ToolConfig in the LangChain template ([9bda328](https://github.com/googleapis/python-aiplatform/commit/9bda3288b59eb52c18a13c292561cb2c720ff331))
* Create Vertex Experiment when uploading Tensorboard logs ([339f8b6](https://github.com/googleapis/python-aiplatform/commit/339f8b667952c7302c36605842ba92fa1c7135b8))
* GenAI - Add BatchPredictionJob for GenAI models ([df4a4f2](https://github.com/googleapis/python-aiplatform/commit/df4a4f2745178a6458bb6dc1f124c8ee60e986c1))
* GenAI - Add cancel, delete, list methods in BatchPredictionJob ([7ff8071](https://github.com/googleapis/python-aiplatform/commit/7ff80714c2ec55330d5d6a0075366f8f700128af))
* GenAI - Added the `BatchPredictionJob.submit` method ([4d091c6](https://github.com/googleapis/python-aiplatform/commit/4d091c68b17b3c1b4a912aa38d3a098fdc21238d))
* Private Endpoints - Added private service connect support to prediction endpoint. ([6bdcfb3](https://github.com/googleapis/python-aiplatform/commit/6bdcfb3c0c6b121d5fbfcdad9dd218a1ddfc3e0d))


### Bug Fixes

* Add validation for evaluation dataset fields, update logging info for eval api request count ([d6ef500](https://github.com/googleapis/python-aiplatform/commit/d6ef50080f3b2b923ba0fb89eb0a8daebf8f68d4))
* Fix feature attribution drift visualization for model monitoring SDK ([710f33d](https://github.com/googleapis/python-aiplatform/commit/710f33d87e242a283e8fbe5327ba9fa781d0d8fc))
* Fix the default value of response_column_name in EvalTask.evaluate() ([98f9b35](https://github.com/googleapis/python-aiplatform/commit/98f9b35ccde7dad7f3e6b9e259a201ee2784d15e))
* Update get_experiment_df to pass Experiment and allow empty metrics. ([de5d0f3](https://github.com/googleapis/python-aiplatform/commit/de5d0f3a17a77cbc70ada480768d9209c7b02828))


### Documentation

* Add Vertex Model Monitoring V2 SDK documentation ([b47e6ff](https://github.com/googleapis/python-aiplatform/commit/b47e6ff1f17278a6f1e4c31def05f3a09d981b28))
* Update docstrings for rapid evaluation library. ([d6d371d](https://github.com/googleapis/python-aiplatform/commit/d6d371d61abd2daa2f222ca82540c5e0c4b3a602))

## [1.51.0](https://github.com/googleapis/python-aiplatform/compare/v1.50.0...v1.51.0) (2024-05-10)


### Features

* Add FeatureGroup create function ([3938107](https://github.com/googleapis/python-aiplatform/commit/393810728b6b940e4cc8e1ac7f55875e3b750beb))
* Add FeatureGroup init/get ([e47d436](https://github.com/googleapis/python-aiplatform/commit/e47d436f24cc718e378a28c4a80293778e8c183a))
* Add support for BaseModels in LangChain templates ([5eb885e](https://github.com/googleapis/python-aiplatform/commit/5eb885ee7e01eece15679ce400f222930da1ac16))
* Added the `vision_models.Image._mime_type` property to make `vision_models.Image` compatible with `generative_models.Image` ([6557d88](https://github.com/googleapis/python-aiplatform/commit/6557d88eb73624c8dbc7da33db129f7cbdae8a06))
* AutoSxS Pairwise Metric in Rapid Evaluation SDK ([b0c5eda](https://github.com/googleapis/python-aiplatform/commit/b0c5eda79489d4b32972b2acea647e3c8cdc3ce9))
* GenAI - Grounding - Released Google Web Search retriever to GA ([32b030a](https://github.com/googleapis/python-aiplatform/commit/32b030a629a20d0557dba011df2658f46c199820))
* GenAI - Tuning - Supervised - Added support for the `adapter_size` parameter ([88188d2](https://github.com/googleapis/python-aiplatform/commit/88188d294fc2ec55ec0b05640dc791a1a3a88255))
* LLM - Made the tuning location parameters truly optional ([bae8429](https://github.com/googleapis/python-aiplatform/commit/bae8429ae078c69574d86280ae6c784aaa9b13b5))
* LLM - Support tuning of new text embedding models by migrating to the new v1.1.3 pipeline. ([7fea754](https://github.com/googleapis/python-aiplatform/commit/7fea7547084277dc974cbacc517ca1e95629a034))
* LLM - Text embedding - Added the `output_dimensionality` and `learning_rate_multiplier` parameters to text embedding tuning (Preview only) ([cc8bc96](https://github.com/googleapis/python-aiplatform/commit/cc8bc965932efb68a30db9decb5a24cf597b0d8b))
* LLM - Text Embedding - Added validation for text embedding tuning parameters. ([5a300c1](https://github.com/googleapis/python-aiplatform/commit/5a300c1071fa1492502cfde95700e1b171cdfbfc))
* Release Ray on Vertex SDK to GA ([f7c5132](https://github.com/googleapis/python-aiplatform/commit/f7c51327c49d000cc79d56bb5333ed7fea28fa01))
* Support custom service account for Ray cluster creation and Ray Client connection ([e0c6227](https://github.com/googleapis/python-aiplatform/commit/e0c6227d0dd92d83c98cc3c7e7607fd252e74a32))
* Support vector_distance_threshold filtering and file-based retrieval for RAG ([cd85d8f](https://github.com/googleapis/python-aiplatform/commit/cd85d8f74d3922de3f871415bacf77c594f0c547))


### Bug Fixes

* A bug in the evaluation library where the job crashes if only custom metrics are specified. ([c528b6f](https://github.com/googleapis/python-aiplatform/commit/c528b6ff44e2347797336db800ca01240e670d32))
* Add DeprecationWarning to vertexai.preview predictive models SDK ([3c3727b](https://github.com/googleapis/python-aiplatform/commit/3c3727b48ce4ba12bdaf36806cda4907a788d38e))
* Add MAX_TOKENS to the list of successful finish reasons for Rapid Evaluation SDK ([195c77e](https://github.com/googleapis/python-aiplatform/commit/195c77ed7320aea3ab5899427a922d606ed78997))
* AttributeError for TorchModelSerializer.deserialize in torch &gt;=2.3.0 ([20b1866](https://github.com/googleapis/python-aiplatform/commit/20b18668f15c448813aad4f58f2a4d470d6da2ec))
* GenAI - Fixed handling of multiple tools in `AutomaticFunctionCallingResponder` ([58e6ac9](https://github.com/googleapis/python-aiplatform/commit/58e6ac9b14daa42dc64d787156070c22bd7a1655))
* Remove InternalServerError and Unknown evaluation service error from retriable exceptions ([12c147b](https://github.com/googleapis/python-aiplatform/commit/12c147b1f3e127c925b6c42b7dbbd4e949ff8e98))
* Upload the reference model in model registry ([510c833](https://github.com/googleapis/python-aiplatform/commit/510c8334961cdb6f801863ecbd8fe49bf69b6c68))

## [1.50.0](https://github.com/googleapis/python-aiplatform/compare/v1.49.0...v1.50.0) (2024-05-02)


### Features

* Add `Candidate.grounding_metadata` property ([b22a8b8](https://github.com/googleapis/python-aiplatform/commit/b22a8b847e3b299b828e37405e3678093486de28))
* Add option to not include time_series_metrics in get_experiment_df call. This will improve execution time for Experiments with large number of runs. ([78a95c5](https://github.com/googleapis/python-aiplatform/commit/78a95c52d0e7bd9ec5b656ce67044b2f01677156))
* Add tune_model and deploy_tuned_model for TextEmbeddingModel. ([42f5d6f](https://github.com/googleapis/python-aiplatform/commit/42f5d6f7cd13d51c4a73113c59e8b3c728cfc08b))
* Automatically populate parents for full resource name in Vertex RAG SDK ([26657ff](https://github.com/googleapis/python-aiplatform/commit/26657ffd25ecb91882ca764e513c2e952833257f))
* Deploy a tuned text embedding model -- it doesn't matter, if it's tuned using Node.js, or curl. ([8ca9cdf](https://github.com/googleapis/python-aiplatform/commit/8ca9cdf3576e3ce3b373ace4cd6ab0e9c54aa9f2))
* Make get_embeddings work both for foundational & tuned models. ([b8b589c](https://github.com/googleapis/python-aiplatform/commit/b8b589ce9fff29d1721450d32b4a84a7f69413c3))
* Python SDK for Vertex Model Monitoring V2. ([021d59f](https://github.com/googleapis/python-aiplatform/commit/021d59f1487e4e16c847d4135899d6845c0210aa))
* Support public endpoint for Ray Client ([57a5f78](https://github.com/googleapis/python-aiplatform/commit/57a5f7815ffb8523e91d900da4ff7cfd0c344fe4))


### Bug Fixes

* Add deprecation warnings when using Ray v2.4 ([3a36784](https://github.com/googleapis/python-aiplatform/commit/3a367843840513e3257610c8ab38e9f79d3bcea0))
* Append allowed_plugins in tb-gcp-uploader to default allowed plugins ([aab9c3e](https://github.com/googleapis/python-aiplatform/commit/aab9c3e41b92a1d60090e3d1d594390a5e9f3ff6))
* LLM - Added missing parameters to the no-op `_TunableTextEmbeddingModelMixin.get_tuned_model` method ([eb05ac4](https://github.com/googleapis/python-aiplatform/commit/eb05ac421f186441a92c6e3b6a010d74caf14782))
* LVM - Fixed the typo in the VisionModel aspect ratio type annotation ([2d19137](https://github.com/googleapis/python-aiplatform/commit/2d1913773cf9f4a4f8a2c8c8f45680c3ea97f68e))
* Move torch import ([e6d34df](https://github.com/googleapis/python-aiplatform/commit/e6d34df7da7508c655eb17ee694e1ab2160fc8aa))
* Ray - Fixed exception when using Ray 2.4 ([2661f52](https://github.com/googleapis/python-aiplatform/commit/2661f52fd08169e5d29b58f2afce9702b30101ae))

## [1.49.0](https://github.com/googleapis/python-aiplatform/compare/v1.48.0...v1.49.0) (2024-04-27)


### Features

* Add additional parameters for `GenerationConfig` ([0599ca1](https://github.com/googleapis/python-aiplatform/commit/0599ca18342aece9d8b9b35534294de541593ef9))
* Add FeatureNormType to `MatchingEngineIndexConfig`. ([c0e7acc](https://github.com/googleapis/python-aiplatform/commit/c0e7acc27e67ef1a951bb4bd97f489164dda14f9))
* Add mappings to pipeline templates for text-embedding models. ([6279924](https://github.com/googleapis/python-aiplatform/commit/627992484ec16fbf7fdfc9c963046e10e3d7c6bf))
* Add support for TPU v5 lite pod(v5e) for custom training jobs. Custom training jobs now accept the v5e machine types as listed in https://cloud.google.com/tpu/docs/tpus-in-gke#v5e. ([415912e](https://github.com/googleapis/python-aiplatform/commit/415912e9258d2b960c7da730902d7f15116cc474))
* Fix typo in Vertex Feature Store SDK. ([b5404e7](https://github.com/googleapis/python-aiplatform/commit/b5404e7106059358dd7fcd21d487e5e31ed4d128))
* GenAI - Improved the exception messages when candidates, parts or text are not available ([e82264d](https://github.com/googleapis/python-aiplatform/commit/e82264d273e35d3b305d434181badfb63a37c79c))
* Support PreflightValidation in Preview PipelineJob submit function. ([e88dc0d](https://github.com/googleapis/python-aiplatform/commit/e88dc0d65ffaed3de9850e8eaadbfa41eb769e06))
* Tune_model method for class TextEmbeddingModel. ([3eda55d](https://github.com/googleapis/python-aiplatform/commit/3eda55d25a8e3816eec0fb3c43f7c16c8a2d9b32))
* Vertex RAG for enhanced generative AI ([39b5149](https://github.com/googleapis/python-aiplatform/commit/39b5149c18355a233dae7ada2f18c8072a6b59f1))


### Bug Fixes

* GCS Bucket subdirectory not being creating while using ReasoningEngine create method ([3d22a18](https://github.com/googleapis/python-aiplatform/commit/3d22a18abdacc7cb53d4b5fef941fa1a34caec08))
* GenAI - Fixed the `Part.mime_type` property ([819a44e](https://github.com/googleapis/python-aiplatform/commit/819a44ea9b624912c31843881fd6130febb8ec57))
* Handle missing import for RunnableConfig when generating schema for LangChain templates ([76c5d6d](https://github.com/googleapis/python-aiplatform/commit/76c5d6d6e99be5e7a8ec81e85aa383b1a39fef66))
* Parse intermediate steps from LangChain into JSON. ([754c89d](https://github.com/googleapis/python-aiplatform/commit/754c89d8514dde707255bf0e3602dfddff49f268))
* Register TensorFlow models from Ray checkpoints for more recent TensorFlow version, addressing the deprecation of SavedModel format in keras 3 ([1341e2c](https://github.com/googleapis/python-aiplatform/commit/1341e2c57907f7867d4237e84c5bb9b77e5dd5f5))
* Tensorboard uploader - move remaining tensorboard uploader code to aiplatform ([f34094b](https://github.com/googleapis/python-aiplatform/commit/f34094b50ea161c2b9f0653be8b5931e922bb8f6))

## [1.48.0](https://github.com/googleapis/python-aiplatform/compare/v1.47.0...v1.48.0) (2024-04-17)


### Features

* Add support for reading requirements from a file. ([80db7a0](https://github.com/googleapis/python-aiplatform/commit/80db7a0960b80ae0d78182687c1e99db696943f7))
* Adding tpu_topology to Vertex SDK ([423c764](https://github.com/googleapis/python-aiplatform/commit/423c7646185b4df19985fb41f5776557d572dd9f))
* Enable continuous upload for profile logs. ([f05924d](https://github.com/googleapis/python-aiplatform/commit/f05924d6bbd9e609f4ca98cdef7ab5a504672e58))
* GenAI - Added the `GenerationResponse.prompt_feedback` property ([efd5a72](https://github.com/googleapis/python-aiplatform/commit/efd5a72c1856a6767bdbbba9ea83f366518bdac2))
* GenAI - Added the `GenerationResponse.usage_metadata` property ([0654c35](https://github.com/googleapis/python-aiplatform/commit/0654c3504425d9f9bba6e3be919026229b616ec0))
* Support `NOT_EQUAL` for `MatchingEngineIndexEndpoint` `numeric_restricts`. ([aa918e3](https://github.com/googleapis/python-aiplatform/commit/aa918e31fcc40878e9f29affa02a4527d90188aa))
* Support referenced models in SDK. ([c9b6b8b](https://github.com/googleapis/python-aiplatform/commit/c9b6b8b3433854afd95a27065a052393768ceca8))


### Bug Fixes

* Add validation check for extra_packages when creating a reasoning engine. ([255dabc](https://github.com/googleapis/python-aiplatform/commit/255dabc77c647ef3ac33a10b06b3a36db122118a))
* Add validation for langchain tools. ([a821d50](https://github.com/googleapis/python-aiplatform/commit/a821d50724da7136c90abd157a7086d6571f2c30))
* Fixed the vertexai.init partial initialization issues ([636a654](https://github.com/googleapis/python-aiplatform/commit/636a654590919048f84baf343d291711f28eb03e))
* GenAI - Workaround for streaming when content role is missing in service responses ([fa35b91](https://github.com/googleapis/python-aiplatform/commit/fa35b9169677c62a5f0fa746dc9db9a5296f44a3))


### Documentation

* Add Reasoning Engine reference documentation ([496fc4b](https://github.com/googleapis/python-aiplatform/commit/496fc4b96768c872c9e7312bacf9989ea6e979f5))
* GenAI - Add Rapid Evaluation SDK reference documentation ([40b728b](https://github.com/googleapis/python-aiplatform/commit/40b728b28210f2bc57374c6c6d507cf3fa0be038))

## [1.47.0](https://github.com/googleapis/python-aiplatform/compare/v1.46.0...v1.47.0) (2024-04-06)


### Features

* Add display experiment button for tuning in Ipython environments ([9bb687c](https://github.com/googleapis/python-aiplatform/commit/9bb687c20b03ea7227908e09831fb1a13ac3a970))
* Add Persistent Resource ID parameter to Custom Job form_local_script, run, and submit methods. ([f5be0b5](https://github.com/googleapis/python-aiplatform/commit/f5be0b5652b0366eb6e823409ba1cb134e4b7b7c))
* Add Persistent Resource Id parameter to Custom Training Job run and submit methods. ([f428006](https://github.com/googleapis/python-aiplatform/commit/f428006507e9b053a2121089e89fc54aedd3550a))
* Added GA support for PersistentResource management ([98a07dd](https://github.com/googleapis/python-aiplatform/commit/98a07dd614063cb6a4c55c9024893874d3c95a1f))
* Added GA support for running Custom and Hp tuning jobs on Persistent Resources ([35ecbac](https://github.com/googleapis/python-aiplatform/commit/35ecbac53df299b681e835648a9884a091f5d4d8))
* Added the `Experiment.dashboard_url` property ([c8eec21](https://github.com/googleapis/python-aiplatform/commit/c8eec21d6f6e6f016669a18e19cebd9de1f0a7f9))
* GenAI - Added support for `SafetySetting.method` (probability or severity) ([317ab8f](https://github.com/googleapis/python-aiplatform/commit/317ab8f7499b345c5a73365b95e9ba91c1adfecf))
* GenAI - Added support for supervised fine-tuning ([036d2d0](https://github.com/googleapis/python-aiplatform/commit/036d2d0306e5190c972d2c4e5dd34257ea8fad6d))
* GenAI - Added support for system instructions ([4990eb6](https://github.com/googleapis/python-aiplatform/commit/4990eb6ade736c85c08455ca0ef9f7c9515662fd))
* GenAI - Forced function calling feature ([806ef9f](https://github.com/googleapis/python-aiplatform/commit/806ef9fe860c51ee99481cb7f209723a22a1d369))
* Initial template for Langchain on Vertex. ([0752a29](https://github.com/googleapis/python-aiplatform/commit/0752a29ec69280373519406be8528682f1c547ec))
* LLM - Add RLHF-tuning support for `text-bison@002` ([1f27c3e](https://github.com/googleapis/python-aiplatform/commit/1f27c3eb5bb95b04f5e1708d631309c928df932b))
* Vertex AI Extension SDK Public Preview ([137b5e1](https://github.com/googleapis/python-aiplatform/commit/137b5e11ab40abfd4f53c61544989d99770dabeb))
* Vertex AI Reasoning Engine SDK Public Preview ([6aaa5d0](https://github.com/googleapis/python-aiplatform/commit/6aaa5d01c7e675bb1a553fd6780b035e3513d58e))
* Vertex Rapid Evaluation SDK and Prompt Template for Vertex Prompt Management Public Preview ([8c6ddf5](https://github.com/googleapis/python-aiplatform/commit/8c6ddf54adf91e2fbf00034fef413ccfde3769d6))


### Bug Fixes

* GenAI - Fixed response validation error during streaming ([c881998](https://github.com/googleapis/python-aiplatform/commit/c881998c7fb54289efc5ae6f5431b631b3d6c11c))
* GenAI - Fixed the `GenerativeModel`'s handling of tuned models from different region ([bf33fb3](https://github.com/googleapis/python-aiplatform/commit/bf33fb3e0053898cf8ba919180ee246ea5ad1cdb))
* GenAI - Fixed the TuningJob dashboard URL ([5367fbb](https://github.com/googleapis/python-aiplatform/commit/5367fbb1125debd16357e4815c704105209fca2a))
* Reinstate persistent resource preview class and tests ([765d60d](https://github.com/googleapis/python-aiplatform/commit/765d60da57b3e3c947b121667f0a2a2cb93b88f3))


### Documentation

* Add run custom job on persistent resource sample. ([53fc845](https://github.com/googleapis/python-aiplatform/commit/53fc8455145c9fb7953a6e7dd6e85aab01055ad2))
* Add run custom job on persistent resource sample. ([31100c6](https://github.com/googleapis/python-aiplatform/commit/31100c6dd6d7d4b0b588ed7f008e7661835b19d2))

## [1.46.0](https://github.com/googleapis/python-aiplatform/compare/v1.45.0...v1.46.0) (2024-03-30)


### Features

* GenAI - Automatic Function Calling feature ([eef84c6](https://github.com/googleapis/python-aiplatform/commit/eef84c6a694ee848d19d8eab8f1a4940e50d4b0d))
* Python SDK for Vertex Feature Store. ([5015d25](https://github.com/googleapis/python-aiplatform/commit/5015d25c5efdb9ba0a01bc60441f7eb8d5fddc52))

## [1.45.0](https://github.com/googleapis/python-aiplatform/compare/v1.44.0...v1.45.0) (2024-03-28)


### Features

* Add an arg to turn off Ray metrics collection during cluster creation ([e33d11f](https://github.com/googleapis/python-aiplatform/commit/e33d11fa02eb721a6fe09bbd7c2e6a9954dbfe98))
* Add Batch Delete and Batch Cancel Pipeline Jobs and unit tests. ([cb495e7](https://github.com/googleapis/python-aiplatform/commit/cb495e740ace7b2ab9935188ca9f7d6d3bf86d2a))
* Add display model evaluation button for Ipython environments ([181dc7a](https://github.com/googleapis/python-aiplatform/commit/181dc7a575b0cefc1be0ea9b06cb4f30a7a0da0f))
* Add safety filter levels, watermark support and person generation support for Imagen 2 ([0c498c5](https://github.com/googleapis/python-aiplatform/commit/0c498c5e4226b2a16adb0ff3cf7e6698a05aa5c7))
* Add safety filter levels, watermark support and person generation support for Imagen 2 ([e2efdbe](https://github.com/googleapis/python-aiplatform/commit/e2efdbed324bd201f9793c43ca2167e8ccbbe426))
* Add support for output_dimensionality parameter through get_embeddings. ([b1cab3f](https://github.com/googleapis/python-aiplatform/commit/b1cab3fca34e7a1969c1828348bcbd0eefe42cb8))
* Add support for task types (TASK_QUESTION_ANSWERING, TASK_FACT_VERIFICATION) through get_embeddings. ([9ec4590](https://github.com/googleapis/python-aiplatform/commit/9ec459014612116e202c2dddda5f30716ff1a7f8))
* Add v1beta1 service clients for reasoning engine ([13ec7e0](https://github.com/googleapis/python-aiplatform/commit/13ec7e0c63649b7c9a7a0eb4a5d36afeae1ffadb))
* GenAI - Support generating JSON Schema from Python function ([be4922a](https://github.com/googleapis/python-aiplatform/commit/be4922adbfa42a91d67e46f0b705e62d794cb8c3))
* Improve get_experiment_df execution speed ([2e56acc](https://github.com/googleapis/python-aiplatform/commit/2e56acc7e5627c4ca46e84febaecf5b791f67462))
* Ray on Vertex enables XGBoost register model with custom version using pre-built container ([e45ef96](https://github.com/googleapis/python-aiplatform/commit/e45ef96de9f008a5c5556bf119a75403085d8dcb))
* Support `accelerator_type` in RLHF tuning ([e51c977](https://github.com/googleapis/python-aiplatform/commit/e51c97738e905dda1d726cd778d62647b096a3c8))


### Bug Fixes

* Fix failing get_experiments_df test. ([767712e](https://github.com/googleapis/python-aiplatform/commit/767712e9caf4bec8260c57668654bcd257f1c831))
* GenAI - Capture content blocked case when validating responses ([f0086df](https://github.com/googleapis/python-aiplatform/commit/f0086dfd76c138443e50bc18ae49b232905468f3))
* LLM - Fixed the `InlineContext` grounding source ([6f59100](https://github.com/googleapis/python-aiplatform/commit/6f591001e834dfc3e49efd988b4faf2b12b1f2d8))
* Made `Endpoint.raw_predict` thread-safe by setting `authorized_session` last ([c72c1ef](https://github.com/googleapis/python-aiplatform/commit/c72c1ef4c58c79fd7a0ee4064de7f2f4a4257f36))

## [1.44.0](https://github.com/googleapis/python-aiplatform/compare/v1.43.0...v1.44.0) (2024-03-14)


### Features

* Add custom tool context manager for telemetry ([b30f5a6](https://github.com/googleapis/python-aiplatform/commit/b30f5a69226310b11a7979d19e63e3b0aa873737))
* Add display experiment button for Ipython environments ([0b33bdd](https://github.com/googleapis/python-aiplatform/commit/0b33bdd873ab0f3195e4dc6389554a3cac2c3433))
* Allow module_name to be specified with the base logger. ([c01df66](https://github.com/googleapis/python-aiplatform/commit/c01df6681e5f94d74dcc5fd85a9ea4af4b9dcea6))
* Enable Ray cluster creation with custom_image for each Resource ([f90c9cc](https://github.com/googleapis/python-aiplatform/commit/f90c9cc0f96eb8108d0d55ffb7ddb51fdc60407d))
* GenAI - Added `function_calls` shortcut property to `Candidate` class. ([d6490ff](https://github.com/googleapis/python-aiplatform/commit/d6490ffdf28d2f1916d517c223e35537611b1073))
* LLM - Added support for the `max_context_length` tuning parameter ([e5daae9](https://github.com/googleapis/python-aiplatform/commit/e5daae92125eaada897a8de4f8de8f5da59af6db))
* Support `shard_size` for `MatchingEngineIndex` create index. ([6dbf7d3](https://github.com/googleapis/python-aiplatform/commit/6dbf7d3f9f74d08b80a3bfb85525ec6922b370fc))
* Use colab enterprise enviroment variables to infer project_id and region ([5baf5f8](https://github.com/googleapis/python-aiplatform/commit/5baf5f83494373049904bedc898e5b72303bccbd))


### Bug Fixes

* Batch read tensorboard time series data to allow reading more than 20 time series metrics. ([6e3eac2](https://github.com/googleapis/python-aiplatform/commit/6e3eac26ed40b1927541b71b99758834a89fa64b))
* GenAI - Fixed `get_tuned_model` deploying the model every time ([e1c7870](https://github.com/googleapis/python-aiplatform/commit/e1c7870aabe4fac5537589f49484509b3faf3f5b))
* GenAI - Improved `from_dict` methods for content types (`GenerationResponse`, `Candidate`, `Content`, `Part`) ([613ce69](https://github.com/googleapis/python-aiplatform/commit/613ce690d8224b85da5406507c4df75a35493b0d))
* Improve import time by moving TensorFlow to lazy import ([f294ba8](https://github.com/googleapis/python-aiplatform/commit/f294ba8b762a88b77a623b86145302c976fdabc4))
* LVM - Added support for GCS `storage.googleapis.com` URL import in `vision_models.Image` ([2690e72](https://github.com/googleapis/python-aiplatform/commit/2690e7223535d5758ed0e13075aebdde41a678f3))
* Raise AttributeError for accessing non-existent fields of a proto. ([b91edf5](https://github.com/googleapis/python-aiplatform/commit/b91edf52e2b993c3301a419ad89b473c31c60cc3))


### Documentation

* Fixed the documentation generation ([63ad1bf](https://github.com/googleapis/python-aiplatform/commit/63ad1bf9e365d2f10b91e2fd036e3b7d937336c0))
* GenAI - Added the GA classes to the documentation ([9eb5a52](https://github.com/googleapis/python-aiplatform/commit/9eb5a52c2f7f0c19a2035831181ad69f98bc3df5))

## [1.43.0](https://github.com/googleapis/python-aiplatform/compare/v1.42.1...v1.43.0) (2024-02-29)


### Features

* Add `update_mask` to `MatchingEngineIndex` `upsert_datapoints()` to support dynamic metadata update. ([81f6a25](https://github.com/googleapis/python-aiplatform/commit/81f6a25ab6600b325ff4e7b0f19332f13080bee9))
* Add Ray on Vertex BigQuery read/write support for Ray 2.9 ([e048e3a](https://github.com/googleapis/python-aiplatform/commit/e048e3a77834ce21a221dab75c890b651b9f3ce0))
* Add read_bigquery and write_bigquery wrappers for Ray on Vertex ([4739118](https://github.com/googleapis/python-aiplatform/commit/47391182a2b7edf0c8cb2cb470e649bf5486faf4))
* Add transport override to enable the use of REST instead of GRPC ([6ab4084](https://github.com/googleapis/python-aiplatform/commit/6ab4084aa549b1a28a4990f8b59dead510d7b296))
* Enable Ray cluster creation and registering TensorFlow checkpoint to Vertex with Ray version 2.9 ([ff148cd](https://github.com/googleapis/python-aiplatform/commit/ff148cd1f836e599c99f2c177abb085d08827375))
* LLM - Add support for batch prediction to `CodeGenerationModel` (`code-bison`) ([fbf2f7c](https://github.com/googleapis/python-aiplatform/commit/fbf2f7c3bf5b462e498a165017217d057a5f5bae))
* Support custom `timeout` for `MatchingEngineIndex` and `MatchingEngineIndexEndpoint` APIs. ([09d1946](https://github.com/googleapis/python-aiplatform/commit/09d1946711fb022bf584137299ed187bf885cb23))
* Update ray extras installation in setup.py for Ray 2.9.3 ([d947304](https://github.com/googleapis/python-aiplatform/commit/d947304314db5f683b154656551a8fd5b6e4c033))


### Bug Fixes

* Allow destination directory to exist before we copy. ([0b55762](https://github.com/googleapis/python-aiplatform/commit/0b55762a8f762b1b46a8d0dcd93381d7870e5200))
* LVM - Fixed `VideoSegmentConfig` in Multimodal Embeddings API call ([665e78c](https://github.com/googleapis/python-aiplatform/commit/665e78c1d037fcae4c17205ffc280c4b88aea627))


### Documentation

* Update transport docstrings to include that REST is in preview ([a442866](https://github.com/googleapis/python-aiplatform/commit/a442866d2df30ea534d06da10afd496b48114f4c))

## [1.42.1](https://github.com/googleapis/python-aiplatform/compare/v1.42.0...v1.42.1) (2024-02-15)


### Bug Fixes

* Handle case when no metadata is returned from model.predict ([59e2bca](https://github.com/googleapis/python-aiplatform/commit/59e2bca8fc9773f0610662d8bf426578b3015c41))
* Remove runtime dependency of setuptools ([07c2a25](https://github.com/googleapis/python-aiplatform/commit/07c2a25225cf163584fc38616ddb6c1e560ac288))


### Documentation

* GenAI - Docs - Added quickstart link and minimum SDK version ([cf6ab21](https://github.com/googleapis/python-aiplatform/commit/cf6ab218035e4712c0202330014cb3b6c241db5b))
* GenAI - Updated the README for GA ([cfd96d8](https://github.com/googleapis/python-aiplatform/commit/cfd96d804e66befe84c2eb6d259aa50faca2b5db))

## [1.42.0](https://github.com/googleapis/python-aiplatform/compare/v1.41.0...v1.42.0) (2024-02-15)


### Features

* Add Candidate.grounding_metadata ([310ee49](https://github.com/googleapis/python-aiplatform/commit/310ee49a11767c20bed9cc4a929cbb0b8b3e6940))
* Add GoogleSearchRetrieval ([310ee49](https://github.com/googleapis/python-aiplatform/commit/310ee49a11767c20bed9cc4a929cbb0b8b3e6940))
* Add metadata in model.predict output for LLMs ([4661e58](https://github.com/googleapis/python-aiplatform/commit/4661e581ea957e71c643afc6bbf3b2e729b38bc8))
* Add Retrieval ([310ee49](https://github.com/googleapis/python-aiplatform/commit/310ee49a11767c20bed9cc4a929cbb0b8b3e6940))
* Add Tool.google_search_retrieval ([310ee49](https://github.com/googleapis/python-aiplatform/commit/310ee49a11767c20bed9cc4a929cbb0b8b3e6940))
* Add Tool.retrieval ([310ee49](https://github.com/googleapis/python-aiplatform/commit/310ee49a11767c20bed9cc4a929cbb0b8b3e6940))
* Add VertexAiSearch ([310ee49](https://github.com/googleapis/python-aiplatform/commit/310ee49a11767c20bed9cc4a929cbb0b8b3e6940))
* GenAI - Added `to_dict()` methods to response and content classes ([a78748e](https://github.com/googleapis/python-aiplatform/commit/a78748e5cbe7b86ddfb1a36a4c0e5be8f66b27c3))
* GenAI - Added support for Grounding ([0c3e294](https://github.com/googleapis/python-aiplatform/commit/0c3e29421434fe36d0f583f9860ac2e3f60e0329))
* GenAI - Added the `GenerativeModel.start_chat(response_validation: bool = True)` parameter ([94f7cd9](https://github.com/googleapis/python-aiplatform/commit/94f7cd9e454d593e2544f8d93771d3093ffc18ae))
* GenAI - GAPIC - Added support for Grounding ([310ee49](https://github.com/googleapis/python-aiplatform/commit/310ee49a11767c20bed9cc4a929cbb0b8b3e6940))
* GenAI - Release the GenerativeModel to GA ([c7e3f07](https://github.com/googleapis/python-aiplatform/commit/c7e3f076f91f002ac5a889d8942a153e57e0147c))
* LLM - Add newly supported model `text-bison@002`, update pipeline template version and prediction row limit for pipeline-based LLM Evaluation SDK ([35e57b3](https://github.com/googleapis/python-aiplatform/commit/35e57b32e70902fc90ee5a39e9001d3fa4150c50))
* LVM - Add GCS URI support for Imagen Models (`imagetext`, `imagegeneration`) ([4109ea8](https://github.com/googleapis/python-aiplatform/commit/4109ea8d8ad456d90c0ca476e2147e9543e15b43))
* LVM - Added support for Images from GCS uri for multimodal embeddings ([90d95d7](https://github.com/googleapis/python-aiplatform/commit/90d95d778f94e598a78a6f1c8a38e1911bffd8e2))
* LVM - Added support for Videos from GCS uri for multimodal embeddings ([f3bd3bf](https://github.com/googleapis/python-aiplatform/commit/f3bd3bf1f74d283d7a95cd9cddf39947fcabc514))
* Support custom image for Ray cluster creation ([d727189](https://github.com/googleapis/python-aiplatform/commit/d7271899a5383ffef69af1c46ad28d92eb4d5751))


### Bug Fixes

* Add google-auth as a direct dependency ([ecc6454](https://github.com/googleapis/python-aiplatform/commit/ecc64544d3cc718957fbe472fef1eaf22818e093))
* Add restricts and crowding tag to `MatchingEngineIndexEndpoint` query response. ([83cb52d](https://github.com/googleapis/python-aiplatform/commit/83cb52d1ed3ec7587ea9bb877dba113abad569be))
* Remove usage of distutils ([e35ab64](https://github.com/googleapis/python-aiplatform/commit/e35ab64d7e47f696ef9dd9c071c2d322e705b5ff))


### Documentation

* Fix incorrect field in log_time_series_metrics_sample ([f249353](https://github.com/googleapis/python-aiplatform/commit/f249353b918823b35495b295a75a90528ad652c0))
* Update README ([14b41b5](https://github.com/googleapis/python-aiplatform/commit/14b41b50aff89e15f5f86f814df122c96231841d))

## [1.41.0](https://github.com/googleapis/python-aiplatform/compare/v1.40.0...v1.41.0) (2024-02-05)


### Features

* Add `numeric_filter` to `MatchingEngineIndexEndpoint` `match()` and `find_neighbor()` private endpoint queries. ([679646a](https://github.com/googleapis/python-aiplatform/commit/679646a352ea3623d752e4685c7224db8934bd9d))
* Added the `BatchPredictionJob.submit` method - a non-blocking version of  `BatchPredictionJob.create` ([b62ddcd](https://github.com/googleapis/python-aiplatform/commit/b62ddcd751323ae96e248ab8bb90561b44f6f5e0))
* LLM - Add support for RLHF tuning ([b2458ec](https://github.com/googleapis/python-aiplatform/commit/b2458ec51d7c3bbba787bbefac31c9aad6ffdb10))
* Remove deletion of model upload staging bucket in system tests ([b9b373b](https://github.com/googleapis/python-aiplatform/commit/b9b373b69eab7dd303816bad94da54cad60a331e))
* Switch Python generateContent to call Unary API endpoint ([9a19545](https://github.com/googleapis/python-aiplatform/commit/9a19545e864c6d4743156c737dd5bb8c4b86ab6f))


### Bug Fixes

* Fix crash when no target_col is specified for Bigframes tensorflow ([512b82d](https://github.com/googleapis/python-aiplatform/commit/512b82debdaf44d1b9c755c2bd06d1d24c080338))


### Documentation

* Add missing code block in docs/README.rst ([16d6b58](https://github.com/googleapis/python-aiplatform/commit/16d6b58ab27549a995919d70f78dd793feee7bd3))

## [1.40.0](https://github.com/googleapis/python-aiplatform/compare/v1.39.0...v1.40.0) (2024-01-24)


### Features

* Add `return_full_datapoint` for `MatchEngineIndexEndpoint` `match()`. ([ad8d9c1](https://github.com/googleapis/python-aiplatform/commit/ad8d9c1df17578de3b893ebe46d00d457960da00))
* Add batch delete method in preview pipeline job class and unit test. ([b0b604e](https://github.com/googleapis/python-aiplatform/commit/b0b604ec871eb99897e9b7c049c7f83abe64199e))
* Add option to not overwrite table in Ray on Vertex BQ Write ([a99e992](https://github.com/googleapis/python-aiplatform/commit/a99e9925038f6a3e4a1538e2da315e8a01071b8b))
* Add query by id for `MatchingEngineIndexEndpoint` `find_neighbors()` public endpoint query. ([42c7e08](https://github.com/googleapis/python-aiplatform/commit/42c7e08249f2ae758ad920e908c3f44fc72ac134))
* Add support for `low_level_batch_size` in `match()` for `MatchingEngineIndexEndpoint` private query. ([67e593b](https://github.com/googleapis/python-aiplatform/commit/67e593b34928682491c0d00555459108261feb8e))
* Added Public Preview support for PersistentResource management ([262a36b](https://github.com/googleapis/python-aiplatform/commit/262a36bdd942e73015a8160ddc3a01adbb99dee5))
* Enable inline context in grounding to TextGenerationModel predict. ([a75e81c](https://github.com/googleapis/python-aiplatform/commit/a75e81c9e8bfe577468205fc0fc97366ff06f19d))
* Fix dataset export system test ([1fbf049](https://github.com/googleapis/python-aiplatform/commit/1fbf0493dc5fa2bb05f33a4319d79a81625e07cc))
* LVM - Added the `MultiModalEmbeddingModel.get_embeddings(dimension=...)` parameter ([1d9bd23](https://github.com/googleapis/python-aiplatform/commit/1d9bd233e636c024def55d4c867f662a4a351f9e))
* Support empty index for `MatchingEngineIndex` create index. ([a00db07](https://github.com/googleapis/python-aiplatform/commit/a00db077a3ca77ee86117beb0b15d70d02e85e87))
* Support private service connect for `MatchingEngineIndexEndpoint` `match()` and `read_index_datapoints()`. ([61cff4b](https://github.com/googleapis/python-aiplatform/commit/61cff4bda371e3baa61d98528d18093e5fa890b4))


### Bug Fixes

* Fix example usage of batch delete pipelinejobs. ([3b28d64](https://github.com/googleapis/python-aiplatform/commit/3b28d64c0f263fc5baa457ebeec70adc20f71df9))
* Fix experiments failure when backing tensorboard has been deleted. ([e7a197e](https://github.com/googleapis/python-aiplatform/commit/e7a197ef5d349968994c029db4c5ce9d52e45bd7))
* Fix message to Json parse issue in Dataset class ([066f32d](https://github.com/googleapis/python-aiplatform/commit/066f32df4e1cd09f1c3d457d6727bc731253aeac))
* Fix typo in raise exception when tool is unsupported ([2301d79](https://github.com/googleapis/python-aiplatform/commit/2301d79ed2b08b4b76066ff0598236468ad656e7))
* Fixed the PipelineJob bucket creation after a breaking change in Google Cloud Storage client library ([a8b01e0](https://github.com/googleapis/python-aiplatform/commit/a8b01e03cdc12de3af87ed7e67b947230a164c42)), closes [#2936](https://github.com/googleapis/python-aiplatform/issues/2936)
* Increase memory for Ray on Vertex default machine type ([e6bcb17](https://github.com/googleapis/python-aiplatform/commit/e6bcb1757645c21cf8ccace79f9fd06531a5a1aa))
* Use https to connect through Ray dashboard ([7af3e67](https://github.com/googleapis/python-aiplatform/commit/7af3e67654e05c20f3cd6f1226ebac3521a95200))

## [1.39.0](https://github.com/googleapis/python-aiplatform/compare/v1.38.1...v1.39.0) (2024-01-05)


### Features

* Add `fraction_leaf_nodes_to_search_override`. Add support for private endpoint in `find_neighbors`. ([cd31c13](https://github.com/googleapis/python-aiplatform/commit/cd31c1306a9a00a01fbc1dda56fe99ed567a4cfb))
* Add notification_channels field to model monitoring alert config. ([bb228ce](https://github.com/googleapis/python-aiplatform/commit/bb228ced16862a1f452352f8941d3a24d1a77090))
* Add support of newly added fields of ExportData API to SDK ([ec3ea30](https://github.com/googleapis/python-aiplatform/commit/ec3ea305cd8a858fb770794c35481cdbc1520990))
* Allow reuse of deleted experiment run id. ([5f6ad8d](https://github.com/googleapis/python-aiplatform/commit/5f6ad8df5a08e78a121a72a21e21d95abb072e58))
* GenAI - Added support for "models/&lt;model ID&gt;" model name format ([ab21feb](https://github.com/googleapis/python-aiplatform/commit/ab21feb3528babbc619c0ea5bf4aa89e651340b3))
* Support "reservedIpRanges" parameter in PipelineJob run() and submit() methods. ([ab99e00](https://github.com/googleapis/python-aiplatform/commit/ab99e00a42868ec09796709a5d5fb6e4f276bfb7))
* Support custom target y column name for Bigframes Tensorflow ([1634940](https://github.com/googleapis/python-aiplatform/commit/1634940c91182fbd080556949d6c2557288216fb))
* Verify client and cluster Ray versions match in create_ray_cluster ([17dc9b7](https://github.com/googleapis/python-aiplatform/commit/17dc9b7663c484fe6250cafd4209ef8279acdb5b))


### Bug Fixes

* Missing request parameter for v1beta explain. ([443fa9d](https://github.com/googleapis/python-aiplatform/commit/443fa9d456294c4a6aa49368cc4b5e6f01ec3d0d))
* Pin google-cloud-aiplatform[tensorboard] dependency on tensorflow &lt; 2.15.0 due to breaking change introduced in tensorboard 2.15.1 ([4e891f7](https://github.com/googleapis/python-aiplatform/commit/4e891f7f0c83dabde429ffaa38166af5a44eab5a))


### Documentation

* GenAI - Added GenAI to docs ([92fd7f0](https://github.com/googleapis/python-aiplatform/commit/92fd7f0a10ae35b448ac4981c072fdc5d8b05c3b))
* Update docstring for start_upload_tb_log() ([c033c59](https://github.com/googleapis/python-aiplatform/commit/c033c5971c7692f84d0a5b58946c49348a4c4448))
* Update tensorboard continuous uploader sample ([1220746](https://github.com/googleapis/python-aiplatform/commit/122074659871daa72aec4a6d3330a82eec77a1c5))

## [1.38.1](https://github.com/googleapis/python-aiplatform/compare/v1.38.0...v1.38.1) (2023-12-13)


### Features

* Adding `serving_container_grpc_ports` parameter to Model.upload() method ([6a00ed7](https://github.com/googleapis/python-aiplatform/commit/6a00ed79252c97f3e5f5eef5492d5d7ef12c969c))
* LLM - Added support for model distillation ([28925e9](https://github.com/googleapis/python-aiplatform/commit/28925e9464254e9768ceab845001aa0e3d46bbbf))
* Support CMEK for scheduled pipeline jobs. ([406595d](https://github.com/googleapis/python-aiplatform/commit/406595dd78896d3c3fcec8975baccdabef468849))


### Miscellaneous Chores

* Release 1.38.1 ([537d00e](https://github.com/googleapis/python-aiplatform/commit/537d00e185df593f6c718859cbc92f8dfef67512))

## [1.38.0](https://github.com/googleapis/python-aiplatform/compare/v1.37.0...v1.38.0) (2023-12-11)


### Features

* Release GenerativeModel support for Gemini ([cd233ef](https://github.com/googleapis/python-aiplatform/commit/cd233ef81d1359f3ac89fca809e337ac866d2108))
* Add explicit constraints for update_ray_cluster ([979a4f3](https://github.com/googleapis/python-aiplatform/commit/979a4f3280cf79c672bd90b57049b1d9f20635fc))
* Check if dataset exists before creation for Ray on Vertex BigQuery Write ([544d6fe](https://github.com/googleapis/python-aiplatform/commit/544d6fe7925d673bc0fa5236a3ae2608fce10d8e))
* LLM - Added support for the `logprobs`, `presence_penalty`, `frequency_penalty`, and `logit_bias` generation parameters ([1449344](https://github.com/googleapis/python-aiplatform/commit/1449344490bbfd2ea9eddf0a7dfa651d89db7bc9))
* Support `read_index_datapoints` for private network. ([c9f7119](https://github.com/googleapis/python-aiplatform/commit/c9f7119f7c13a4f2a0ef3613ef03c0247ec263da))
* Support custom batch size for Bigframes Tensorflow ([7dc8771](https://github.com/googleapis/python-aiplatform/commit/7dc8771715387e4fb4536aa7080b795bfba8039c))
* Update the v1 service definition to add numeric_restricts. ([d0c2ffa](https://github.com/googleapis/python-aiplatform/commit/d0c2ffa8d8d070f9ef247c3c742a67b12d1bc16d))
* Verify client and cluster Ray versions match ([10c6ad2](https://github.com/googleapis/python-aiplatform/commit/10c6ad292f0eb79f4010ea22115b2f70abdea661))


### Bug Fixes

* `read_index_endpoint` private endpoint support. ([3d8835e](https://github.com/googleapis/python-aiplatform/commit/3d8835e1dbc48502246fc5ae141f465e0ac7ae90))
* Fix exception message to use vertexai when project is not provided. ([0cb1a7b](https://github.com/googleapis/python-aiplatform/commit/0cb1a7b16ef49813d5c59e2b9646dc7861291b42))
* Update test assumption for streaming endpoint of chat-bison@001 ([f9a5b69](https://github.com/googleapis/python-aiplatform/commit/f9a5b692a7b4ed7046ba5035cb1b592aa0cd9f0b))
* When user is not logged in, throw more intuitive message ([a8b24ad](https://github.com/googleapis/python-aiplatform/commit/a8b24adaf0485f41ea6fc0d65d17d3d9500821aa))


### Documentation

* Add default value to optional field parameter_values ([0a4d772](https://github.com/googleapis/python-aiplatform/commit/0a4d772aacc8b100aac6b0c7810296dd0a3e6692))

## [1.37.0](https://github.com/googleapis/python-aiplatform/compare/v1.36.4...v1.37.0) (2023-12-05)


### Features

* Add additional parameters to Model.upload(). ([7b7d7d2](https://github.com/googleapis/python-aiplatform/commit/7b7d7d2f2c7f074e62ee009a308341228fcd6582))
* Adding support for concurrent explanations ([8e2ad75](https://github.com/googleapis/python-aiplatform/commit/8e2ad75e255210f99ab091802899a75df92b6a20))
* Allow configuring container logging settings on models when deploying. ([beae48f](https://github.com/googleapis/python-aiplatform/commit/beae48f63e40ea171c3f1625164569e7311b8e5a))
* Support user provided api endpoint. ([92f2b4e](https://github.com/googleapis/python-aiplatform/commit/92f2b4e32035a35f5f2a4956fee443fe3061bc32))
* Add grpc_ports to UploadModel ModelContainerSpec, add DirectPredict, DirectRawPredict, StreamingPredict, StreamingRawPredict to PredictionService. ([6dfbad7](https://github.com/googleapis/python-aiplatform/commit/6dfbad7dcb29ef3b481bb90d989a1f6f68976996))

### Bug Fixes

* Clarify wording when Ray on Vertex cluster is missing head node ip ([4a71c8c](https://github.com/googleapis/python-aiplatform/commit/4a71c8c1df499aec763e7d16c2f022eb3593d3de))
* Fix error when allowed_plugins is set to None. ([6f2860a](https://github.com/googleapis/python-aiplatform/commit/6f2860aafce9b77819a3891fb6c29bfb65ea8a2a))
* Fixed INTEGER and BOOL parameters casting issue. Fix conversion bug where `INTEGER` and `BOOL` parameters are not cast to the correct type. ([9a204c4](https://github.com/googleapis/python-aiplatform/commit/9a204c4ffb16ba34c36f3869fbc36c52bc9986bb))
* Make PipelineJobSchedule propagate labels to created PipelineJobs ([a34533f](https://github.com/googleapis/python-aiplatform/commit/a34533f536d1d5caa46a68a640bd507e979c161e))


### Documentation

* Add upload Tensorboard profile log to Experiment sample. ([5780513](https://github.com/googleapis/python-aiplatform/commit/57805132f82e1e21d3999e130b5c5fdbc105143a))
* Update the documentation for the `image_dataset` class ([8562368](https://github.com/googleapis/python-aiplatform/commit/856236887a9159991b400829f5c05a307aaedd58))

## [1.36.4](https://github.com/googleapis/python-aiplatform/compare/v1.36.3...v1.36.4) (2023-11-16)


### Features

* Add `numeric_restricts` to MatchingEngineIndex `find_neighbors()` for querying ([6c1f2cc](https://github.com/googleapis/python-aiplatform/commit/6c1f2cc650cfe0c6cc9896de13746d1a25d7315a))
* Add `remove_datapoints()` to `MatchingEngineIndex`. ([b86a404](https://github.com/googleapis/python-aiplatform/commit/b86a4046c2cd0c189efc609bd6319f8da76cd6e7))
* Add `upsert_datapoints()` to `MatchingEngineIndex` to support streaming update index. ([7ca484d](https://github.com/googleapis/python-aiplatform/commit/7ca484da0431699c460358584b9e8be102d9cc46))
* LLM - include error code into blocked response from TextGenerationModel, ChatModel, CodeChatMode, and CodeGenerationModel. ([1f81cf2](https://github.com/googleapis/python-aiplatform/commit/1f81cf200c9394b50a43c3830ab8343ead1dc0d3))
* Populate Ray Cluster dashboard_address from proto field ([dd4b852](https://github.com/googleapis/python-aiplatform/commit/dd4b8529a72f6d08e56e8437cdd3cd0874df8a47))
* add CountTokens API, ComputeTokens API, and ModelContainerSpec features ([ba2fb39](https://github.com/googleapis/python-aiplatform/commit/ba2fb398b46b04fc2c9d0ea902746737ace64767))


### Bug Fixes

* Add check for empty `encryption_spec_key_name` for MatchingEngineIndexEndpoint `create`. ([7740132](https://github.com/googleapis/python-aiplatform/commit/7740132c315b2f1e55504e5c5b462eb27bf89937))
* Fix server error due to no `encryption_spec_key_name` in MatchingEngineIndex `create_tree_ah_index` and `create_brute_force_index` ([595b580](https://github.com/googleapis/python-aiplatform/commit/595b580bfaa238b63f61cb69a7829094c747aaea))


### Miscellaneous Chores

* Release 1.36.4 ([1fd7b4e](https://github.com/googleapis/python-aiplatform/commit/1fd7b4eb4773c9c58cb4e957e176c0053169afc0))

## [1.36.3](https://github.com/googleapis/python-aiplatform/compare/v1.36.2...v1.36.3) (2023-11-14)


### Features

* Add option to not use default tensorboard ([a25c669](https://github.com/googleapis/python-aiplatform/commit/a25c6697d75444e4134ac0b9ca8964458f70e275))
* Add preview HyperparameterTuningJob which can be run on persistent resource ([0da8c53](https://github.com/googleapis/python-aiplatform/commit/0da8c5373b35d9bc7520e93934b109c3ff583dac))
* Add Featurestore Bigtable Serving, Feature Registry v1, November bulk GAPIC release ([9f46f7c](https://www.google.com/url?sa=D&q=https%3A%2F%2Fgithub.com%2Fgoogleapis%2Fpython-aiplatform%2Fcommit%2F9f46f7c4289e78fb825837f602aecd4105f21e19))


### Documentation

* Fix documentation for obsolete link to GCS formatting ([95184de](https://github.com/googleapis/python-aiplatform/commit/95184de2570636e4ee0968dbcfb48c37f811e12f))


### Miscellaneous Chores

* Release 1.36.3 ([fdee5cb](https://github.com/googleapis/python-aiplatform/commit/fdee5cb1779344731b4cab0482079691601154d7))

## [1.36.2](https://github.com/googleapis/python-aiplatform/compare/v1.36.1...v1.36.2) (2023-11-10)


### Features

* Add `encryption_spec_key_name` to `MatchingEngineIndex` `create_tree_ah_index` and ([1a9e36f](https://github.com/googleapis/python-aiplatform/commit/1a9e36f4ea1672d0fc6ce1587c86c4f132c15190))
* Add `encryption_spec_key_name`, `enable_private_service_connect`,`project_allowlist` to MatchingEngineIndexEndpoint `create`. ([750e17b](https://github.com/googleapis/python-aiplatform/commit/750e17b4c25c9030018521545b3c21e1fb1404c2))
* Add `index_update_method` to MatchingEngineIndex `create()` ([dcb6205](https://github.com/googleapis/python-aiplatform/commit/dcb62051a7f3aeaa009b64165569c788d8c5ec44))
* Expose max_retry_cnt parameter for Ray on Vertex BigQuery write ([568907c](https://github.com/googleapis/python-aiplatform/commit/568907c3876b10dc104de5d19a973135b2638d62))
* LLM - Grounding - Added support for the `disable_attribution` grounding parameter ([91e985a](https://github.com/googleapis/python-aiplatform/commit/91e985a258180226053a23a9280249079574ad16))
* LLM - Support model evaluation when tuning chat models (`ChatModel`, `CodeChatModel`) ([755c3f9](https://github.com/googleapis/python-aiplatform/commit/755c3f99478e537ef5675ed7120a17eaf94ee5cd))
* LVM - Added multi-language support for `ImageGenerationModel` ([791eff5](https://github.com/googleapis/python-aiplatform/commit/791eff5fac48a4395017d7f9296cfb2209a073ba))


### Bug Fixes

* Async call bug in CodeChatModel.send_message_async method ([fcf05cb](https://github.com/googleapis/python-aiplatform/commit/fcf05cb6da15c83e91e6ce5f20ab3e6649983685))


### Documentation

* Add Bigframes remote training example to vertexai README ([8b993b3](https://github.com/googleapis/python-aiplatform/commit/8b993b367758dc4f195a7a80d13923687da53e04))
* Update the documentation for the `tabular_dataset` class ([6f40f1b](https://github.com/googleapis/python-aiplatform/commit/6f40f1baf02b279299c7ea825754fe1868d56276))


### Miscellaneous Chores

* Release 1.36.2 ([01be0c9](https://github.com/googleapis/python-aiplatform/commit/01be0c99ff86726962146bcf9601a04f7298cda1))

## [1.36.1](https://github.com/googleapis/python-aiplatform/compare/v1.36.0...v1.36.1) (2023-11-07)


### Features

* Add `per_crowding_attribute_neighbor_count`, `approx_num_neighbors`, `fraction_leaf_nodes_to_search_override`, and `return_full_datapoint` to MatchingEngineIndexEndpoint `find_neighbors` ([33c551e](https://github.com/googleapis/python-aiplatform/commit/33c551efca38688c8c62ef5847dfcef0221e848c))
* Add profiler support to tensorboard uploader sdk ([be1df7f](https://github.com/googleapis/python-aiplatform/commit/be1df7f4823f7b40022d31f529204dfe27fdb4d7))
* Add support for `per_crowding_attribute_num_neighbors` `approx_num_neighbors`to MatchingEngineIndexEndpoint `match()` ([e5c20c3](https://github.com/googleapis/python-aiplatform/commit/e5c20c3b5c0078c9dfc70e2d1d13513a4dcefa63))
* Add support for `per_crowding_attribute_num_neighbors` `approx_num_neighbors`to MatchingEngineIndexEndpoint `match()` ([53d31b5](https://github.com/googleapis/python-aiplatform/commit/53d31b5b6ec477e6f2b4391aaeadc8ae349800b8))
* Add support for `per_crowding_attribute_num_neighbors` `approx_num_neighbors`to MatchingEngineIndexEndpoint `match()` ([4e357d5](https://github.com/googleapis/python-aiplatform/commit/4e357d5121d053dc313f3a3f180131e1850bebe2))
* Enable grounding to ChatModel send_message and send_message_async methods ([d4667f2](https://github.com/googleapis/python-aiplatform/commit/d4667f25a7c95bd16511beaed85edf45307176b5))
* Enable grounding to TextGenerationModel predict and predict_async methods ([b0b4e6b](https://github.com/googleapis/python-aiplatform/commit/b0b4e6b8243cbdb829288e3fc204d94005f1e8b4))
* LLM - Added support for the `enable_checkpoint_selection` tuning evaluation parameter ([eaf4420](https://github.com/googleapis/python-aiplatform/commit/eaf4420479b64740cdd464afb64b8780f57c8199))
* LLM - Added tuning support for the `*-bison-32k` models ([9eba18f](https://github.com/googleapis/python-aiplatform/commit/9eba18f70d36ac3901ba8b580cde6dde04413bc3))
* LLM - Released `CodeChatModel` tuning to GA ([621af52](https://github.com/googleapis/python-aiplatform/commit/621af5244797a0e218195c72d9781cbd86b24fa0))


### Bug Fixes

* Correct class name in system test ([b822b57](https://github.com/googleapis/python-aiplatform/commit/b822b57fa490c8d89802ee5fbf0f3736e0811208))


### Documentation

* Clean up RoV create_ray_cluster docstring ([1473e19](https://github.com/googleapis/python-aiplatform/commit/1473e19c9b05c89ba2229f42a8d72588fa267d17))


### Miscellaneous Chores

* Release 1.36.1 ([1cde170](https://github.com/googleapis/python-aiplatform/commit/1cde1708fd26357995f3ee86194aa92aa7de5519))

## [1.36.0](https://github.com/googleapis/python-aiplatform/compare/v1.35.0...v1.36.0) (2023-10-31)


### Features

* Add preview count_tokens method to CodeGenerationModel ([96e7f7d](https://github.com/googleapis/python-aiplatform/commit/96e7f7d9243c36fa991dd147fe66b3a7e545b3bb))
* Allow the users to use extra serialization arguments for objects. ([ffbd872](https://github.com/googleapis/python-aiplatform/commit/ffbd87228ecc8d1f534e66d31301597822625b6a))
* Also support unhashable objects to be serialized with extra args ([77a741e](https://github.com/googleapis/python-aiplatform/commit/77a741e5bec00c89a7746794d77f7ab5e93e5b2f))
* LLM - Added `count_tokens` support to ChatModel (preview) ([01989b1](https://github.com/googleapis/python-aiplatform/commit/01989b185b7847549ccecfd4f83c9eaf3caa056d))
* LLM - Added new regions for tuning and tuned model inference ([3d43497](https://github.com/googleapis/python-aiplatform/commit/3d434979659f8801921745600b1ee82f725937cc))
* LLM - Added support for async streaming ([760a025](https://github.com/googleapis/python-aiplatform/commit/760a0256ef8da36ec2832b476e62626714488f3e))
* LLM - Added support for multiple response candidates in code chat models ([598d57d](https://github.com/googleapis/python-aiplatform/commit/598d57d24ea613130a74bf7db86c757a668626b8))
* LLM - Added support for multiple response candidates in code generation models ([0c371a4](https://github.com/googleapis/python-aiplatform/commit/0c371a4bd0adca8bec41dca6ef95e8a1011404f4))
* LLM - Enable tuning eval TensorBoard without evaluation data ([eaf5d81](https://github.com/googleapis/python-aiplatform/commit/eaf5d816a7a752373243033ea98146d70987ce18))
* LLM - Released `CodeGenerationModel` tuning to GA ([87dfe40](https://github.com/googleapis/python-aiplatform/commit/87dfe40d68255c62c30564a46a63a13417aa7fc4))
* LLM - Support `accelerator_type` in tuning ([98ab2f9](https://github.com/googleapis/python-aiplatform/commit/98ab2f99d63f2ea40dead12dbffc078d9dae8336))
* Support experiment autologging when using persistent cluster as executor ([c19b6c3](https://github.com/googleapis/python-aiplatform/commit/c19b6c3e88293f231aae0c9939e41c9e0f064ee7))
* Upgrade BigQuery Datasource to use write() interface ([7944348](https://github.com/googleapis/python-aiplatform/commit/794434856713b4aab6aa32e8dd37b3d767136c78))


### Bug Fixes

* Adding setuptools to dependencies for Python 3.12 and above. ([afd540d](https://github.com/googleapis/python-aiplatform/commit/afd540d5210e56d5ace19f94526916a2b0c4f1fc))
* Fix Bigframes tensorflow serializer dependencies ([b4cdb05](https://github.com/googleapis/python-aiplatform/commit/b4cdb05b12b82d3b9f605382828e3f854d985951))
* LLM - Fixed the async streaming ([41bfcb6](https://github.com/googleapis/python-aiplatform/commit/41bfcb6677fe40afc19548b9bfb1b360b1125adc))
* LLM - Make tuning use the global staging bucket if specified ([d9ced10](https://github.com/googleapis/python-aiplatform/commit/d9ced106b57cb21f5dcde433f1779b6500aaf7b0))
* LVM - Fixed negative prompt in `ImageGenerationModel` ([cbe3a0d](https://github.com/googleapis/python-aiplatform/commit/cbe3a0de14a2ee189df07f445545f68fa4bdd4ae))
* Made the Endpoint prediction client initialization lazy ([eb6071f](https://github.com/googleapis/python-aiplatform/commit/eb6071fe567ef80ba5490b9eaae0cedd6958aac5))
* Make sure PipelineRuntimeConfigBuilder is created with the right arguments ([ad19838](https://github.com/googleapis/python-aiplatform/commit/ad19838ebc51215dc6c2fe0f373a4773877a0fb6))
* Make sure the models list is populated before indexing ([f1659e8](https://github.com/googleapis/python-aiplatform/commit/f1659e80a7cc4f1e25d5f251c2483fa365bcdba2))
* Raise exception for RoV BQ Write for too many rate limit exceeded ([7e09529](https://github.com/googleapis/python-aiplatform/commit/7e095298d145fe24202bacdb6be88d44789a2aa9))
* Rollback BigQuery Datasource to use do_write() interface ([dc1b82a](https://github.com/googleapis/python-aiplatform/commit/dc1b82a9856beb3ab537b38b1ad1d2c244511c81))

## [1.35.0](https://github.com/googleapis/python-aiplatform/compare/v1.34.0...v1.35.0) (2023-10-10)


### Features

* Add serializer.register_custom_command() ([639cf10](https://github.com/googleapis/python-aiplatform/commit/639cf10e444f5aee200cdf0ffaa63e768dc4119b))
* Install Bigframes sklearn dependencies automatically ([7aaffe5](https://github.com/googleapis/python-aiplatform/commit/7aaffe505aa8e7bff86af5a3674085b8ff822107))
* Install Bigframes tensorflow dependencies automatically ([e58689b](https://github.com/googleapis/python-aiplatform/commit/e58689b65dd7e2da3e0ece33c2e0b08f7b441089))
* Install Bigframes torch dependencies automatically ([1d65347](https://github.com/googleapis/python-aiplatform/commit/1d65347468565e86d57e2dd003bdf87dbf37e613))
* LLM - Added support for multiple chat response candidates ([587df74](https://github.com/googleapis/python-aiplatform/commit/587df744e2b6c4b3e1a96ff69937697fe80a97be))
* LLM - Added support for multiple text generation response candidates ([c3ae475](https://github.com/googleapis/python-aiplatform/commit/c3ae475efaa9cbe85315b0792c0948a8f5c13bed))


### Bug Fixes

* Duplicate logs in Colab ([9b75259](https://github.com/googleapis/python-aiplatform/commit/9b7525987e05f6b63300440267fcdefea4caf35c))
* LLM - Fixed tuning and evaluation when explicit credentials are specified ([188dffe](https://github.com/googleapis/python-aiplatform/commit/188dffeb2fc83b4c7c123624eb544b403f042c87))


### Documentation

* Add probabilistic inference to TiDE and L2L  model code samples. ([efe88f9](https://github.com/googleapis/python-aiplatform/commit/efe88f98abb57ec11cdd326b87cb935a6b370257))

## [1.34.0](https://github.com/googleapis/python-aiplatform/compare/v1.33.1...v1.34.0) (2023-10-02)


### Features

* Add Model Garden support to vertexai.preview.from_pretrained ([f978200](https://github.com/googleapis/python-aiplatform/commit/f9782007c58ee11fe276c373d8d7ac6c2b0cb249))
* Enable vertexai preview persistent cluster executor ([0ae969d](https://github.com/googleapis/python-aiplatform/commit/0ae969d9e968c6b497d4f41e28f0ea1274d5253c))
* LLM - Added the `count_tokens` method to the preview `TextGenerationModel` and `TextEmbeddingModel` classes ([6a2f2aa](https://github.com/googleapis/python-aiplatform/commit/6a2f2aa8e348c6fc1e24012291f538d2b86eae7b))
* LLM - Improved representation for blocked responses ([222f222](https://github.com/googleapis/python-aiplatform/commit/222f222ed5f8e0c2266484b9992e45cf9827a119))
* LLM - Released `ChatModel` tuning to GA ([7d667f9](https://github.com/googleapis/python-aiplatform/commit/7d667f9f8be264bb36e3d720caa0d8210aec5d6b))


### Bug Fixes

* Create PipelineJobSchedule in same project and location as associated PipelineJob by default ([c22220e](https://github.com/googleapis/python-aiplatform/commit/c22220ef5db440020331634f5e25199c575cc886))


### Documentation

* Add documentation for the preview namespace ([69a67f2](https://github.com/googleapis/python-aiplatform/commit/69a67f203627e4ee7d5980ce874d4db1e6af5dd8))

## [1.33.1](https://github.com/googleapis/python-aiplatform/compare/v1.33.0...v1.33.1) (2023-09-20)


### Bug Fixes

* Lightning trainer fails to be unwrapped in remote training ([8271301](https://github.com/googleapis/python-aiplatform/commit/8271301454814b233a630d1c18ebe5e4833fcec2))

## [1.33.0](https://github.com/googleapis/python-aiplatform/compare/v1.32.0...v1.33.0) (2023-09-18)


### Features

* Add Custom Job support to from_pretrained ([8b0add1](https://github.com/googleapis/python-aiplatform/commit/8b0add169ebd0683b56dbe3b643d533ebbd5e1ca))
* Added async prediction and explanation support to the `Endpoint` class ([e9eb159](https://github.com/googleapis/python-aiplatform/commit/e9eb159756dfe90c9f72818204fa74d05096aec6))
* LLM - Added support for async prediction methods ([c9c9f10](https://github.com/googleapis/python-aiplatform/commit/c9c9f10058afead91f7298ec4f09f901898718b3))
* LLM - CodeChat - Added support for `context` ([f7feeca](https://github.com/googleapis/python-aiplatform/commit/f7feeca2161df7c12c993116364a663c4249f852))
* Release Ray on Vertex SDK Preview ([3be36e6](https://github.com/googleapis/python-aiplatform/commit/3be36e6c17ef5e335d4f12af7a7c64702b76570e))


### Bug Fixes

* Handle Ray image parsing error ([41a3a83](https://github.com/googleapis/python-aiplatform/commit/41a3a83b2e9411a642668d9713282e87e38c64b4))
* Vizier - Fixed field existence checks for child params in to_proto(). ([d516931](https://github.com/googleapis/python-aiplatform/commit/d51693115a32c054bf5f10ebe7fd2c52ea1ac2d7))

## [1.32.0](https://github.com/googleapis/python-aiplatform/compare/v1.31.1...v1.32.0) (2023-09-05)


### Features
* LLM - Added `stop_sequences` parameter to streaming methods and `CodeChatModel` ([d62bb1b](https://github.com/googleapis/python-aiplatform/commit/d62bb1b2d9a41e700e3564012e70735e5148bb80))
* LLM - Improved the handling of temperature and top_p in streaming ([6566529](https://github.com/googleapis/python-aiplatform/commit/656652964a9ab48ccd2b3c8249ecffc598da0a3a))
* Support bigframes sharded parquet ingestion at remote deserialization (Tensorflow) ([a8f85ec](https://github.com/googleapis/python-aiplatform/commit/a8f85ec68749390058f19a40906f326f91ea3eb6))
* Release Vertex SDK Preview ([c60b9ca](https://github.com/googleapis/python-aiplatform/commit/c60b9ca2dd8c9bbdee6d8b745ff5fa849fa38fe9))
* Allow setting default service account ([d11b8e6](https://github.com/googleapis/python-aiplatform/commit/d11b8e67607fb9c526d04869cab47f23789bc8d7))


### Bug Fixes

* Fix feature update since no LRO is created ([468e6e7](https://github.com/googleapis/python-aiplatform/commit/468e6e7b5021ea73a5847b57564e3c090b3f8fca))
* LLM - `CodeGenerationModel` now supports safety attributes ([c2c8a5e](https://github.com/googleapis/python-aiplatform/commit/c2c8a5e60ba11ab344cc41ce651740dc0556f6a2))
* LLM - Fixed batch prediction on tuned models ([2a08535](https://github.com/googleapis/python-aiplatform/commit/2a085354ed921485493b482c0f4e96f3f49d06f0))
* LLM - Fixed the handling of the `TextEmbeddingInput.task_type` parameter. ([2e3090b](https://github.com/googleapis/python-aiplatform/commit/2e3090b9f1f81b543650ae6bad31ee91395c03a4))
* Make statistics Optional for TextEmbedding. ([7eaa1d4](https://github.com/googleapis/python-aiplatform/commit/7eaa1d4216f0494897606b1225c3b3599a235544))


## [1.31.1](https://github.com/googleapis/python-aiplatform/compare/v1.31.0...v1.31.1) (2023-08-24)

* fix: LLM - De-hardcoded the `max_output_tokens` default value for the `CodeGenerationModel` ([f5a20eb](https://github.com/googleapis/python-aiplatform/commit/f5a20eb381af0685d8b6fffad085ded87f4cf5e3))


## [1.31.0](https://github.com/googleapis/python-aiplatform/compare/v1.30.1...v1.31.0) (2023-08-21)


### Features

* Add disable_retries option to custom jobs. ([db518b0](https://github.com/googleapis/python-aiplatform/commit/db518b0552a8900ca6a84a73ca711b775c786e92))
* LLM - Added support for `stop_sequences` in inference ([6f7ea84](https://github.com/googleapis/python-aiplatform/commit/6f7ea84415e5d0efcc49487c93b0f1d94fd68974))
* LLM - Exposed the `TextGenerationResponse.raw_prediction_response` ([f8f2b9c](https://github.com/googleapis/python-aiplatform/commit/f8f2b9cdf88f40fe0b7e86948515ab1cf72d92be))
* LLM - Made tuning asynchronous when tuning becomes GA ([226ab8b](https://github.com/googleapis/python-aiplatform/commit/226ab8b64efc01d7ce20cdf924e103d7673376cf))
* LLM - release model evaluation for TextGenerationModel to public preview ([8df5185](https://github.com/googleapis/python-aiplatform/commit/8df5185d668292d5adc11ebf9477e2fdd44599d4))
* LLM - Released `TextGenerationModel` tuning to GA ([62ff30d](https://github.com/googleapis/python-aiplatform/commit/62ff30daa718ac7869714c68e55d6955d6355945))
* LLM - Support streaming prediction for chat models ([ce60cf7](https://github.com/googleapis/python-aiplatform/commit/ce60cf75ec5c83db8033b553e1ad7164159fb3be))
* LLM - Support streaming prediction for code chat models ([0359f1d](https://github.com/googleapis/python-aiplatform/commit/0359f1dd83bf86df58d1145ddf5e4634d3c8e1ff))
* LLM - Support streaming prediction for code generation models ([3a8348b](https://github.com/googleapis/python-aiplatform/commit/3a8348bca2d9c74e5e52fb9fc131fdb766f49a5c))
* LLM - Support streaming prediction for text generation models ([fb527f3](https://github.com/googleapis/python-aiplatform/commit/fb527f3aa59ee90fa6306196b328f513ee4b4d9c))
* LLM - TextEmbeddingModel - Added support for structural inputs (`TextEmbeddingInput`), `auto_truncate` parameter and result `statistics` ([cbf9b6e](https://github.com/googleapis/python-aiplatform/commit/cbf9b6ee806d7eb89725f53c4509858a272b3141))
* LVM - Added support for Image Generation models ([b3729c1](https://github.com/googleapis/python-aiplatform/commit/b3729c11a70abaf061daa56ed4c483c4118d5acf))
* LVM - Released `ImageCaptioningModel` to GA ([7575046](https://github.com/googleapis/python-aiplatform/commit/7575046d953e83bbb8aa13769f28e1eb50e04a7d))
* LVM - Released `ImageQnAModel` to GA ([fd5cb02](https://github.com/googleapis/python-aiplatform/commit/fd5cb0226f4cff7ee160d2005c5907b81f847a1e))
* LVM - Released `MultiModalEmbeddingModel` to GA ([e99f366](https://github.com/googleapis/python-aiplatform/commit/e99f366fde802b8677b785613e02fc4d9f94d729))
* LVM - Removed the `width` and `height` parameters from `ImageGenerationModel.generate_images` since the service has dropped support for image sizes and aspect ratios ([52897e6](https://github.com/googleapis/python-aiplatform/commit/52897e669ff91d3bb991fcf05ae9a18df93df05f))
* Scheduled pipelines client GA. ([62b8b23](https://github.com/googleapis/python-aiplatform/commit/62b8b23e1144ec547b8d181240090b744dd5201a))


### Documentation

* Generate documentation for tune_model and related class ([705e1ea](https://github.com/googleapis/python-aiplatform/commit/705e1ea402684f3ff4a4cf1f80c04b88bf6cf7db))
* LVM - Added autogenerated documentation for visual models ([18e8bb2](https://github.com/googleapis/python-aiplatform/commit/18e8bb283e80fa9efb26f5fe3f8997b0b038bb12))

## [1.30.1](https://github.com/googleapis/python-aiplatform/compare/v1.30.0...v1.30.1) (2023-08-11)


### Features

* LLM - Added tuning support for `chat-bison` models ([3a97c52](https://github.com/googleapis/python-aiplatform/commit/3a97c523c8223f7f007008769ecb2efd0d44d182))
* LLM - Added tuning support for `codechat-bison` models ([af6e455](https://github.com/googleapis/python-aiplatform/commit/af6e45556d6b093189f363a95f2be45e0008aebd))


### Bug Fixes

* LLM - Fixed the `TextGenerationModel.predict` parameters ([f3b25ab](https://github.com/googleapis/python-aiplatform/commit/f3b25ab694eaee18f5cc34f800f1b6021d291bca))


### Miscellaneous Chores

* Release 1.30.1 ([d1c79c4](https://github.com/googleapis/python-aiplatform/commit/d1c79c4ef87a8d4601ab04de050af2be4c6d6ecf))

## [1.30.0](https://github.com/googleapis/python-aiplatform/compare/v1.29.0...v1.30.0) (2023-08-10)


### Features

* Add model.evaluate() method to Model class ([51df86e](https://github.com/googleapis/python-aiplatform/commit/51df86ee1390a51b82ffc015514ad1e145821a34))
* Add support for providing only text to MultiModalEmbeddingModel.get_embeddings() ([38ec40a](https://github.com/googleapis/python-aiplatform/commit/38ec40a12cf863c9da3de8336dceba10d92f6f56))


### Bug Fixes

* LLM - Fixed filter in `list_tuned_model_names` ([57806fb](https://github.com/googleapis/python-aiplatform/commit/57806fb947e5b692cd8d4701e572eaf54585d383))

## [1.29.0](https://github.com/googleapis/python-aiplatform/compare/v1.28.1...v1.29.0) (2023-08-02)


### Features

* Add preview CustomJob which can be run on persistent resource ([56906b0](https://github.com/googleapis/python-aiplatform/commit/56906b08d80bee64334f6ba0c713e30dae39cef4))
* LLM - Support for Batch Prediction for the `textembedding` models (preview) ([a368538](https://github.com/googleapis/python-aiplatform/commit/a36853869e627aabf3dc563400d184f44c8ae876))
* LLM - Support tuning for the code-bison model (preview) ([e4b23a2](https://github.com/googleapis/python-aiplatform/commit/e4b23a254aadfae821e326b238555cee2ecb463a))
* LVM - Large Vision Models SDK (preview release). Support for image captioning and image QnA (`imagetext` model) and multi modal embedding (`multimodelembedding` model) (preview) ([9bbf1ea](https://github.com/googleapis/python-aiplatform/commit/9bbf1eaa02dda0723303cd39e9f6bdffab32ec21))


### Bug Fixes

* LLM - Fixed `get_tuned_model` for the future models that are not `text-bison` ([1adf72b](https://github.com/googleapis/python-aiplatform/commit/1adf72b866021b9e857166778dbddf83fd808fb7))


### Documentation

* Fix auto-generated pydoc for language_models ([7d72bd1](https://github.com/googleapis/python-aiplatform/commit/7d72bd1c3740039d7c63d1042aa6bcadbd3e4946))
* LLM - Made it possible to provide message history to `CodeChatModel` when starting chat. ([cf46145](https://github.com/googleapis/python-aiplatform/commit/cf46145b3de8de794d4295f59d8af3ea9dd57826))

## [1.28.1](https://github.com/googleapis/python-aiplatform/compare/v1.28.0...v1.28.1) (2023-07-18)


### Features

* LLM - Released the BatchPrediction to GA for TextGenerationModel ([701c3a2](https://github.com/googleapis/python-aiplatform/commit/701c3a29bb09b45b513bcf1bf332388a9b60ae2d))
* LLM - Support tuning in the "us-central1" location ([4aa7745](https://github.com/googleapis/python-aiplatform/commit/4aa77451f5de33b90d82dba69b4c55cea5640b87))


### Bug Fixes

* Fix artifact registry link not showing in ui when creating schedules with SDK. ([203cb47](https://github.com/googleapis/python-aiplatform/commit/203cb477b6ef09a2f6d5f166b5b66a8c626848ef))
* Fixed the installation error caused by a PyYAML issue ([4b86ce1](https://github.com/googleapis/python-aiplatform/commit/4b86ce1afacc6937fda81f6e664e22155e968c7d))
* Require model name in ModelEvaluation.list() ([aed8c76](https://github.com/googleapis/python-aiplatform/commit/aed8c7604f5d89f52c53a599330fd502d02f7877))


### Documentation

* Fixed a docstring for train_steps ([1f55b05](https://github.com/googleapis/python-aiplatform/commit/1f55b05d4631f2b63ede8a3d5ec604d4550e22dd))


### Miscellaneous Chores

* Release 1.28.1 ([8ebf22e](https://github.com/googleapis/python-aiplatform/commit/8ebf22e3efbf47484117cbdf057cd286c8672b81))

## [1.28.0](https://github.com/googleapis/python-aiplatform/compare/v1.27.1...v1.28.0) (2023-07-08)


### Features

* LLM - Released the Chat models to GA ([22aa26d](https://github.com/googleapis/python-aiplatform/commit/22aa26daabbaaa84f84d3cad524f2b6e8c53e77d))

## [1.27.1](https://github.com/googleapis/python-aiplatform/compare/v1.27.0...v1.27.1) (2023-07-06)


### Features

* Add sdk support for xai example-based explanations ([f9ca1d5](https://github.com/googleapis/python-aiplatform/commit/f9ca1d52a6789f93b4eca9596c04f52a2ca75513))


### Miscellaneous Chores

* Release 1.27.1 ([2159f29](https://github.com/googleapis/python-aiplatform/commit/2159f29e8322aef33cfa27df52a57f7cc7722868))

## [1.27.0](https://github.com/googleapis/python-aiplatform/compare/v1.26.1...v1.27.0) (2023-06-30)


### Features

* Add submit for CustomTrainingJob and CustomContainerTrainingJob which won't block until complete. ([d6476d0](https://github.com/googleapis/python-aiplatform/commit/d6476d0ed1440f58301d8be0b9043b13aa8d910d))
* LLM - Added support for `learning_rate` in tuning ([c6cdd10](https://github.com/googleapis/python-aiplatform/commit/c6cdd108b5f3469340ca16bc6ef56efc55723ce3))
* LLM - Released the Codey models to GA ([89609c9](https://github.com/googleapis/python-aiplatform/commit/89609c9007684e5cbc4b3e5c30d26c0d5539aa39))


### Bug Fixes

* Fix aiplatform.init bug by replacing experiment_name with experiment ([c60773a](https://github.com/googleapis/python-aiplatform/commit/c60773a7db8ce7a59d2cb5787dc90937776c0b8f))
* Fix error when calling update_state() after ExperimentRun.list() ([cb255ec](https://github.com/googleapis/python-aiplatform/commit/cb255ec514995e193df7122dbf67bbd4011e6630))
* LLM - Exported the `ChatMessage` class ([7bf7634](https://github.com/googleapis/python-aiplatform/commit/7bf7634e97dfe56c3130264eeb62a9b5d6b55cac))
* LLM - Fixed the chat models failing due to safetyAttributes format ([459ba86](https://github.com/googleapis/python-aiplatform/commit/459ba86396ab9260fd7b28a1524c051b7ad300a5))
* Vizier - Fixed pyvizier client study creation errors ([16299d1](https://github.com/googleapis/python-aiplatform/commit/16299d14b8f209218d6576614f773c1bcbd21d64))


### Documentation

* Fixed a docstring for _Dataset ([b68a941](https://github.com/googleapis/python-aiplatform/commit/b68a941853f9c38b0ff30f5d07cea1d7fb0700a6))
* Fixed a docstring for TimeSeriesDataset ([a7dfce2](https://github.com/googleapis/python-aiplatform/commit/a7dfce217eebbef0877053b9c0f6f6127b556e82))
* Populate GA LLM SDK Pydocs ([e248285](https://github.com/googleapis/python-aiplatform/commit/e248285b5da4c33a68ccd6198ce7b1d8ab20febf))
* Update scheduled pipelines client max_run_count docstring with allowed values. ([750e161](https://github.com/googleapis/python-aiplatform/commit/750e16179e1a53bc916ae6db93cd28cfd3f911fe))

## [1.26.1](https://github.com/googleapis/python-aiplatform/compare/v1.26.0...v1.26.1) (2023-06-21)


### Features

* Add additional scheduled pipelines client getters and unit tests. ([9371b4f](https://github.com/googleapis/python-aiplatform/commit/9371b4fd3f7529636fc323a7914960d0c6a70db4))
* Add PipelineJobSchedule update method and unit tests. ([69c5f60](https://github.com/googleapis/python-aiplatform/commit/69c5f60bfea5308589a58c2b9ad9f392b3a1283e))
* Add tunable parameters for Model Garden model training to the "AutoMLImageTrainingJob" in SDK. ([50646be](https://github.com/googleapis/python-aiplatform/commit/50646be154b2be6c4738858af2440ad207c4020a))
* LLM - Added batch prediction ([2235305](https://github.com/googleapis/python-aiplatform/commit/2235305c7714835ff331e5294f90a6a23e31391d))
* LLM - Exposed the chat history ([bf0e20b](https://github.com/googleapis/python-aiplatform/commit/bf0e20b497675125e0bc5abc10455b06f7a0c019))
* LLM - Exposed the safety attributes ([01ba3ca](https://github.com/googleapis/python-aiplatform/commit/01ba3cabf522a500a29c4120a264e204a660482a))


### Bug Fixes

* Change scheduled pipelines client dashboard uri to view created schedules. Note: uri will not work until scheduler UI is GA. ([d4d8613](https://github.com/googleapis/python-aiplatform/commit/d4d86135ae1593eaffe782d1e197c2a844e6f28a))
* Fix bug where scheduled pipeline jobs were not running. ([4e7d11a](https://github.com/googleapis/python-aiplatform/commit/4e7d11a072c2b3bdb8e6233ff879ec2c31a626ea))
* Remove Schedule read mask because ListSchedules does not support it. ([1fda417](https://github.com/googleapis/python-aiplatform/commit/1fda4172baaf200414d95e7217bfef0e500cc16a))


### Miscellaneous Chores

* Release 1.26.1 ([42567d2](https://github.com/googleapis/python-aiplatform/commit/42567d2ba7dc14d7fbfea2a4afb71cb701582012))


### Documentation

* Update scheduled pipelines client wait() docstring. ([a7d92e5](https://github.com/googleapis/python-aiplatform/commit/a7d92e51ceab2e7c0f72aec1a19404c7c17c65a5))

## [1.26.0](https://github.com/googleapis/python-aiplatform/compare/v1.25.0...v1.26.0) (2023-06-07)


### Features

* Add additional scheduled pipelines client create method unit tests. ([0463678](https://github.com/googleapis/python-aiplatform/commit/0463678723acc485da34e89e342c20a2b6809435))
* Add pipelineJob create_schedule() method and unit test. ([635ae9c](https://github.com/googleapis/python-aiplatform/commit/635ae9c1170f536550e69fa2049e891f696c8d6f))
* Add scheduled pipelines client create/get methods and unit tests. ([4755fc7](https://github.com/googleapis/python-aiplatform/commit/4755fc79d27da0975991d828e407df7fafe8c4d3))
* Add scheduled pipelines client list/pause/resume methods and unit tests. ([ce5dee4](https://github.com/googleapis/python-aiplatform/commit/ce5dee454ff16e92141b8c8e46a7f855c5635843))
* Adding `enable_access_logging` parameter to Endpoint.deploy() method, minor edit to batch_predict() docstring ([794cedd](https://github.com/googleapis/python-aiplatform/commit/794cedd0e9e34544d6c8d5bf6892ef2c28eaaf5d))
* LLM - Added support for CMEK in tuning ([aebf74a](https://github.com/googleapis/python-aiplatform/commit/aebf74a666327210495dad12a28a0f8080d91f9b))
* LLM - Released the LLM SDK to GA ([76465e2](https://github.com/googleapis/python-aiplatform/commit/76465e27ba233f04632688c8ce06b9d2818ff1b8))
* Support publisher models in `BatchPredictionJob.create` ([13b11c6](https://github.com/googleapis/python-aiplatform/commit/13b11c667ac38bd3898ebca88428bea5bd923661))


### Bug Fixes

* CustomJob.from_local_script does not pass args to script for custom container images ([6ead69d](https://github.com/googleapis/python-aiplatform/commit/6ead69d069667ddc6590f2f32fac73ab0bd12b85))
* Fix bug when checking PipelineJob failure status ([a154859](https://github.com/googleapis/python-aiplatform/commit/a154859141da22df6a9fcfdcc3898d9a94175a68))
* Fix the bug that start_upload_tb_log() doesn't continuously upload ([66e6eae](https://github.com/googleapis/python-aiplatform/commit/66e6eaebbe2ac4e9cd370afa32242ae9117beece))
* LLM - Fixed parameters set in `ChatModel.start_chat` being ignored ([a0d815d](https://github.com/googleapis/python-aiplatform/commit/a0d815d646d5b0885366677a533e44337530d71a))
* LLM - Fixed the DataFrame staging on Windows ([056b0bd](https://github.com/googleapis/python-aiplatform/commit/056b0bde6f05b2a36934cc18c7f1bc34dce75dba))
* Resource created by `_construct_sdk_resource_from_gapic` should use the project from the resource name instead of the default project. ([162b2f2](https://github.com/googleapis/python-aiplatform/commit/162b2f265ac6cd91a78f29e2110eaf87a4a6c2e3))
* Retry for etag errors on context update. ([d3d5f9a](https://github.com/googleapis/python-aiplatform/commit/d3d5f9a2a33b4f22e53599b515f0e4d1415c5786))
* Unbreak additional timeout for MatchingEngineIndexEndpoint deploy_index ([af199c0](https://github.com/googleapis/python-aiplatform/commit/af199c035c037478abccfa629801b843909baf99))


### Documentation

* Correct text embedding model ID docstring ([8824629](https://github.com/googleapis/python-aiplatform/commit/88246293a8a4ba94a13106bc99044129674fd15e))
* LLM - Fixed the rendering of the example usage code blocks. ([eaaee28](https://github.com/googleapis/python-aiplatform/commit/eaaee28d1cf96eb1077f7092fb526d1162080a96))

## [1.25.0](https://github.com/googleapis/python-aiplatform/compare/v1.24.1...v1.25.0) (2023-05-09)


### Features

* Add support for Large Language Models ([866c6aa](https://github.com/googleapis/python-aiplatform/commit/866c6aaf72b9a7a5f6155665f574cc11cf8075f4))
* Add default TensorBoard support. ([fa7d3a0](https://github.com/googleapis/python-aiplatform/commit/fa7d3a0e3cd5040eb4ab1c3b0df4e494dc84bac3))
* Add support for find_neighbors/read_index_datapoints in matching engine public endpoint ([e3a87f0](https://github.com/googleapis/python-aiplatform/commit/e3a87f04abf013341fe4f655b96405e27228ffdb))
* Added the new root `vertexai` package ([fbd03b1](https://github.com/googleapis/python-aiplatform/commit/fbd03b15e9b71cbeeaebc868745a36c892b55c8f))


### Bug Fixes

* EntityType RPC update returns the updated EntityType - not an LRO. ([8f9c714](https://github.com/googleapis/python-aiplatform/commit/8f9c7144c152e105924d87abb30aa734af376486))
* Fix default AutoML Forecasting transformations list. ([77b89c0](https://github.com/googleapis/python-aiplatform/commit/77b89c0151ce3647b8fac8f4e8b6a7f7c07a1192))
* Fix type hints for `Prediction.predictions`. ([56518f1](https://github.com/googleapis/python-aiplatform/commit/56518f166215761354aba43d78301a11d198daf5))
* Removed parameter Resume, due to causing confusion and errors. ([c82e0b5](https://github.com/googleapis/python-aiplatform/commit/c82e0b5fb74fe9ba15f9d0f14a441349499ee257))

## [1.24.1](https://github.com/googleapis/python-aiplatform/compare/v1.24.0...v1.24.1) (2023-04-21)


### Features

* Add preview capability to deploy models with shared resources. ([29d4e45](https://github.com/googleapis/python-aiplatform/commit/29d4e45839180f50163de04cd0802ee88d8dd926))
* Add support for create public index endpoint in matching engine ([7e6022b](https://github.com/googleapis/python-aiplatform/commit/7e6022bc05a8ed0e38329c92466e4ff2e924be87))
* Add support for return public endpoint dns name in matching engine ([1b5ae44](https://github.com/googleapis/python-aiplatform/commit/1b5ae4402b74d234d0fd8c886e935b3e8919bb50))
* Add the new model types to "AutoMLImageTrainingJob" in SDK. ([4d032d5](https://github.com/googleapis/python-aiplatform/commit/4d032d59840fdc812dbbedb45acdf45c259e50bd))
* Adds the Time series Dense Encoder (TiDE) forecasting job. ([d8e6744](https://github.com/googleapis/python-aiplatform/commit/d8e67446dedd2c9fde58c6da1e468346391b8ab7))
* Remove google internal annotation when export to github. ([fd5ff99](https://github.com/googleapis/python-aiplatform/commit/fd5ff998282dc5d0511f03ea6eb6d27c05183d59))


### Bug Fixes

* Support timestamp in Vertex SDK write_feature_values() ([4b0722c](https://github.com/googleapis/python-aiplatform/commit/4b0722cfcdcc5246054e0a185be9db1e23f8043b))


### Documentation

* Add Time series Dense Encoder (TiDE) model code sample. ([8e91a58](https://github.com/googleapis/python-aiplatform/commit/8e91a58b5fea6c8e4172e19f8d57f0db9a04bf92))
* Fix docstring formatting for exceptions ([d75322c](https://github.com/googleapis/python-aiplatform/commit/d75322c24d1b802c77493550fa08bfffdf3ec8fb))


### Miscellaneous Chores

* Release 1.24.1 ([cf633a2](https://github.com/googleapis/python-aiplatform/commit/cf633a2513e215e409b9426ff751330fbc481de6))

## [1.24.0](https://github.com/googleapis/python-aiplatform/compare/v1.23.0...v1.24.0) (2023-04-12)


### Features

* Add ExperimentRun.get_logged_custom_jobs method ([c116b07](https://github.com/googleapis/python-aiplatform/commit/c116b074c45387d9264fa8ee5d60723aa9bd63cd))
* Add get method for Experiment and ExperimentRun ([41cd943](https://github.com/googleapis/python-aiplatform/commit/41cd9438f709e2ad8ed530b62d1967a15b5565e2))
* Add incremental training to AutoMLImageTrainingJob. ([bb92380](https://github.com/googleapis/python-aiplatform/commit/bb92380f1281466db95d31218d1e898c77e596f5))
* Add preview capability to manage DeploymentResourcePools. ([5df5da0](https://github.com/googleapis/python-aiplatform/commit/5df5da0ffa1c3a17235a061a756f9afdc261f2ac))
* Add start_time support for BatchReadFeatureValues wrapper methods. ([91d8459](https://github.com/googleapis/python-aiplatform/commit/91d84591913044c547b09f70bf55ef8b4e35cd71))
* Add TensorBoard log uploader ([3fad7bb](https://github.com/googleapis/python-aiplatform/commit/3fad7bba8c90f4a34259d9712728d16c59aba888))
* Enable deployment of models that do not support deployment ([25f3f21](https://github.com/googleapis/python-aiplatform/commit/25f3f219210938c6eb0ea88d0fc3a0897d09ee4b))
* Enable experiment tracking in CustomJob ([94a63b8](https://github.com/googleapis/python-aiplatform/commit/94a63b81a5a6cc51124d19484cefef58c6fc2cca))
* Update the v1 service definition to add the embedding_id field in MatchRequest. ([5a1146e](https://github.com/googleapis/python-aiplatform/commit/5a1146e02ec9c021d3a2b064d30078f4e985591a))


### Bug Fixes

* Adding previously created PrivateEndpoint network parameter in Model deploy helper method ([3e1b206](https://github.com/googleapis/python-aiplatform/commit/3e1b206b1670e4e4c9cca5ffe02f770c9ffae700))


### Documentation

* Adds note to delete endpoint sample ([#2060](https://github.com/googleapis/python-aiplatform/issues/2060)) ([9922eb2](https://github.com/googleapis/python-aiplatform/commit/9922eb26ac1bdf7d99950cb5c85c02998197dc59))
* Fix create tensorboard sample ([2c45123](https://github.com/googleapis/python-aiplatform/commit/2c45123d671ed91e1a56f1200e86485dc4f93f4f))
* **samples:** Add sample for experiment run state update. ([111a747](https://github.com/googleapis/python-aiplatform/commit/111a747fdce1ab92e4d4673b1011c8b6a01d984e))
* Update docstring for 3 model uploading methods ([a71e4a3](https://github.com/googleapis/python-aiplatform/commit/a71e4a389b9597ec09833cbe023ad497f9f4870d))
* Update Vertex Forecasting weight column description. ([e0ee183](https://github.com/googleapis/python-aiplatform/commit/e0ee183d93984bd83b7d2745fec4db75b28976ae))

## [1.23.0](https://github.com/googleapis/python-aiplatform/compare/v1.22.1...v1.23.0) (2023-03-15)


### Features

* Implement Model.copy functionality. ([94dd82f](https://github.com/googleapis/python-aiplatform/commit/94dd82fd2df04e50ede441145684e78b16c4e3e1))
* Update the v1 service definition to add the fraction_leaf_nodes_to_search_override field which replaces leaf_nodes_to_search_percent_override. ([badd386](https://github.com/googleapis/python-aiplatform/commit/badd3863605f5b63ea107d6af09c71999852f846))


### Documentation

* Added missing comma in README ([8cb4377](https://github.com/googleapis/python-aiplatform/commit/8cb43770b33cd9b2070565bf409364d372f139b8))

## [1.22.1](https://github.com/googleapis/python-aiplatform/compare/v1.22.0...v1.22.1) (2023-02-28)


### Features

* Add support for enable_dashboard_access field for Training jobs in SDK ([3500eab](https://github.com/googleapis/python-aiplatform/commit/3500eab379593023147c35654758daf2c0eaf02d))
* Add the recently added new model type "cloud_1" to the "AutoMLImageTrainingJob" in SDK. ([581939b](https://github.com/googleapis/python-aiplatform/commit/581939b1879ca6b47af482883fe0dfbec089f804))


### Documentation

* Add temporal fusion transformer (TFT) model code sample. ([8ddc062](https://github.com/googleapis/python-aiplatform/commit/8ddc062669044ac0889d9f27c93a8b36c1140433))
* **samples:** Add samples for autologging ([f8052b8](https://github.com/googleapis/python-aiplatform/commit/f8052b8f103b1bf8d7f891cf9ae537d7fa48c718))


### Miscellaneous Chores

* Release 1.22.1 ([ed4c0b1](https://github.com/googleapis/python-aiplatform/commit/ed4c0b1513c142aae06b5f8200bd922722a69a27))

## [1.22.0](https://github.com/googleapis/python-aiplatform/compare/v1.21.0...v1.22.0) (2023-02-16)


### Features

* Add a return value (ClassificationMetrics) for the log_classification_metrics() ([8ebcdbd](https://github.com/googleapis/python-aiplatform/commit/8ebcdbdd47f69d537417106e44dfcb4226ee6041))
* Add metric and parameter autologging to experiments ([96e9e12](https://github.com/googleapis/python-aiplatform/commit/96e9e1239ae13e70b9b8ae929f7343155efe3e22))
* Add update_version to Model Registry ([8621e24](https://github.com/googleapis/python-aiplatform/commit/8621e24cd02cb545e353f54562bf111616d7a9f2))
* Support a list of GCS URIs in CustomPythonPackageTrainingJob ([05bb71f](https://github.com/googleapis/python-aiplatform/commit/05bb71ffe437af6da4a8efc331673ff6fc5b38b3))
* Support Model Serialization in Vertex Experiments(tensorflow) ([f38ddc2](https://github.com/googleapis/python-aiplatform/commit/f38ddc29b1f3c47cb7dd8952f8baed9103793ddf))


### Bug Fixes

* Added missing instances_format parameter to batch_prediction_job_samples ([82a2afc](https://github.com/googleapis/python-aiplatform/commit/82a2afc09d6bbfd216daed7ca0cd507c497543a0))
* Address broken unit tests in certain environments ([d06b22d](https://github.com/googleapis/python-aiplatform/commit/d06b22d1ac6197c460092739e8572b9beb08bd63))
* List method for MLMD schema classes ([2401a1d](https://github.com/googleapis/python-aiplatform/commit/2401a1dd642c89fd60c93266d72a6272a69ed357))
* Unbreak additional timeout for _deploy_call() ([076308f](https://github.com/googleapis/python-aiplatform/commit/076308fa3f3bf440177ec895f42d7449cfa0d65b))
* Unbreak additional timeout for MatchingEngine update_embeddings ([5d0bc1e](https://github.com/googleapis/python-aiplatform/commit/5d0bc1ea24cd1465f29df26f293fb9a5afb30da7))
* Unbreak timeouts for Dataset create. ([328ebac](https://github.com/googleapis/python-aiplatform/commit/328ebac961f5771c8f544672faafbb6425375911))
* Use Client.list_blobs instead of Bucket.list_blobs in CPR artifact downloader, to make sure that CPR works with custom service accounts on Vertex Prediction. ([bb27619](https://github.com/googleapis/python-aiplatform/commit/bb27619d71fe237690f9c14a37461f1ca839822b))


### Documentation

* Add a hint to auth Docker to the LocalModel push_image docstring. ([e97a6fb](https://github.com/googleapis/python-aiplatform/commit/e97a6fb684144962e96af84ad105df1adbe26010))
* Fix Create and Import Tabular BQ dataset sample ([4415c10](https://github.com/googleapis/python-aiplatform/commit/4415c107609c04125a601a10f3ff579d5ca5371b))
* Fix LocalModel push_image docstring. ([5fdb7fc](https://github.com/googleapis/python-aiplatform/commit/5fdb7fc2768240a7c8585491e5ea7afdeb725fa8))
* Fixed a typo in docstring. ([4ee6232](https://github.com/googleapis/python-aiplatform/commit/4ee6232f771dce9d545ec62c6687c1b3e289f450))
* New samples for model serialization ([83457ca](https://github.com/googleapis/python-aiplatform/commit/83457ca7c04fda3286bbe3f419c11ec31a043942))
* Samples for model serialization ([7997094](https://github.com/googleapis/python-aiplatform/commit/79970947b12a097a14a82736ef3a9c5c465029b1))

## [1.21.0](https://github.com/googleapis/python-aiplatform/compare/v1.20.0...v1.21.0) (2023-01-13)


### Features

* Add default skew threshold to be an optional input at _SkewDetectionConfig and also mark the target_field and data_source of skew config to optional. ([7da4164](https://github.com/googleapis/python-aiplatform/commit/7da4164697ac01ac94a45b34086facfd0d360f1b))
* Add filter to Model Registry list_versions API. ([c1cb33f](https://github.com/googleapis/python-aiplatform/commit/c1cb33fb1488c2e935f857b9e0993b51fec67fef))
* Add MLMD schema class ExperimentModel ([94b2f29](https://github.com/googleapis/python-aiplatform/commit/94b2f29f040829bbc97d29385f7652c377d9b36b))
* Add Service Account support to BatchPredictionJob ([deba06b](https://github.com/googleapis/python-aiplatform/commit/deba06b938afa695b5fb2d8184647109913abd7c))
* Add support for Predict Request Response Logging in Endpoint SDK ([372ab8d](https://github.com/googleapis/python-aiplatform/commit/372ab8dd59b3a2c5e5eae9af46141ff8e215a610))
* Adding Feature Store: Streaming ingestion to GA ([6bc4c84](https://github.com/googleapis/python-aiplatform/commit/6bc4c848bd9104e5e76fda6e733c051e3ffd4f91))
* Enable passing experiment_tensorboard to init without experiment ([369a0cc](https://github.com/googleapis/python-aiplatform/commit/369a0ccdea4fb869fb13c59603dfbe995c7a74b7))
* Support Model Serialization in Vertex Experiments(sklearn) ([d4deed3](https://github.com/googleapis/python-aiplatform/commit/d4deed3d59dec90c02ea681b4b8dc33399815069))
* Support Model Serialization in Vertex Experiments(xgboost) ([fe75eba](https://github.com/googleapis/python-aiplatform/commit/fe75ebaeeb9bbd19307100bed06cba5ca282aeed))


### Bug Fixes

* `Endpoint.undeploy_all()` doesn't undeploy all models ([9fb24d7](https://github.com/googleapis/python-aiplatform/commit/9fb24d7d647eeb8b93adf432bd20ca368c3d46f7))
* Fix bug in associating tensorboard to an experiment ([6def0b8](https://github.com/googleapis/python-aiplatform/commit/6def0b80f587a5523754ab027e98ea8e4c7feaa9))
* Pin shapely version to &lt;2.0.0 ([1efd816](https://github.com/googleapis/python-aiplatform/commit/1efd81666ac63e1704322ad5771b3208a35bc479))
* Unbreak timeouts for Dataset create, FeatureStore ingest, and MatchingEngine Index create. ([3096d1c](https://github.com/googleapis/python-aiplatform/commit/3096d1c72de7c280e56d8d58192230ba36ccfce3))
* Updated proto message formatting logic for batch predict model monitoring ([f87fef0](https://github.com/googleapis/python-aiplatform/commit/f87fef040cbdc15b5ab547426b7d4ce44b53f2c2))

## [1.20.0](https://github.com/googleapis/python-aiplatform/compare/v1.19.1...v1.20.0) (2022-12-15)


### Features

* Adds the temporal fusion transformer (TFT) forecasting job ([99313e0](https://github.com/googleapis/python-aiplatform/commit/99313e0baacd61d7d00d6576a22b151c1d8e1a49))
* Reraise exceptions from API calls ([d72bc83](https://github.com/googleapis/python-aiplatform/commit/d72bc835184c73e61bb2879e53c71d6772d1b802))


### Documentation

* **samples:** Feature Store: Streaming ingestion code sample and test ([bc9e2cf](https://github.com/googleapis/python-aiplatform/commit/bc9e2cf55f6b4f651c79f68f426a75ed42a7d4c7))

## [1.19.1](https://github.com/googleapis/python-aiplatform/compare/v1.19.0...v1.19.1) (2022-12-08)


### Features

* Add explanationSpec to TrainingPipeline-based custom jobs ([957703f](https://github.com/googleapis/python-aiplatform/commit/957703f9b9c953ee1f67740a652f68279907b104))


### Bug Fixes

* Add pre-built container(tf2-gpu-2-1) to the container URI list ([cdd557e](https://github.com/googleapis/python-aiplatform/commit/cdd557e5e86b0b4d4cf401509aba5914e0bab8b7))
* Fix bug that broke profiler with '0-rc2' tensorflow versions. ([8779df5](https://github.com/googleapis/python-aiplatform/commit/8779df5362a6851372cf3cea005a1c6c3096b19e))
* Fixed argument name in UnmanagedContainerModel ([d876b3a](https://github.com/googleapis/python-aiplatform/commit/d876b3ad8d0129dc98de9f86567d5bf17791058b))


### Documentation

* Add a sample for create_tensorboard. ([52656ca](https://github.com/googleapis/python-aiplatform/commit/52656cac24eedd500a3d97b3d4678857b1d51ed8))
* Fix Experiment resource name format docstring. ([f8e5842](https://github.com/googleapis/python-aiplatform/commit/f8e5842a086bcd90c3b153ffa9dc7e788650e670))
* Fix get Experiment data frame sample ([24e1465](https://github.com/googleapis/python-aiplatform/commit/24e146551237c494349b324ee8830154d129860c))
* Update docstrings for "data_item_labels" in dataset ([b2f8c42](https://github.com/googleapis/python-aiplatform/commit/b2f8c42d88c29010cf78a9f44fb3cdb711a1e94c))
* Update README fix product doc link ([43a2679](https://github.com/googleapis/python-aiplatform/commit/43a2679c0d6f5cba7dff4535a03aedd84e09a2f1))


### Miscellaneous Chores

* Release 1.19.1 ([f01867f](https://github.com/googleapis/python-aiplatform/commit/f01867f697a5d5134c993283f7cf9b22717da029))

## [1.19.0](https://github.com/googleapis/python-aiplatform/compare/v1.18.3...v1.19.0) (2022-11-17)


### Features

* Add Feature Store: Streaming Ingestion (write_feature_values()) and introduce Preview namespace to Vertex SDK ([bae0315](https://github.com/googleapis/python-aiplatform/commit/bae03158c06865d1b61c06a1c8af64e876ce76dd))
* Add bq_dataset_id parameter to batch_serve_to_df ([bb72562](https://github.com/googleapis/python-aiplatform/commit/bb72562f4515b6ace73a735477584ca0b5a30f58))
* Add annotation_labels to ImportDataConfig in aiplatform v1 dataset.proto ([43e2805](https://github.com/googleapis/python-aiplatform/commit/43e28052d798c380de6e102edbe257a0100738cd))
* Add support for ordery_by in Metadata SDK list methods for Artifact, Execution and Context. ([2377606](https://github.com/googleapis/python-aiplatform/commit/23776066909b5b7f77f704722d2719e1a1733ad4))
* Support global network parameter. ([c7f57ad](https://github.com/googleapis/python-aiplatform/commit/c7f57ad505b7251b9c663538e2312998445db691))


### Bug Fixes

* Correct data file gcs path for import_data_text_sentiment_analysis_sample test ([86df4b5](https://github.com/googleapis/python-aiplatform/commit/86df4b5d79118caf8f45c3845c92afe6585c24e9))
* Print error for schema classes ([13e2165](https://github.com/googleapis/python-aiplatform/commit/13e216518f20a32c7e18e6ea5b497a5fcb1d77a0))


### Documentation

* Update README with new link for AI Platform API ([35b83d9](https://github.com/googleapis/python-aiplatform/commit/35b83d90649ec396b736469278def4aaaf80621e))

## [1.18.3](https://github.com/googleapis/python-aiplatform/compare/v1.18.2...v1.18.3) (2022-11-01)


### Documentation

* Add a sample for get_experiment_run_artifacts ([7266352](https://github.com/googleapis/python-aiplatform/commit/7266352ddddf035f68aed96d05d27bdf46559418))

## [1.18.3](https://github.com/googleapis/python-aiplatform/compare/v1.18.2...v1.18.3) (2022-10-31)


### Documentation

* Add a sample for get_experiment_run_artifacts ([7266352](https://github.com/googleapis/python-aiplatform/commit/7266352ddddf035f68aed96d05d27bdf46559418))

## [1.18.2](https://github.com/googleapis/python-aiplatform/compare/v1.18.0...v1.18.2) (2022-10-20)


### Bug Fixes

* Added proto message conversion to MDMJob.update fields ([#1718](https://github.com/googleapis/python-aiplatform/issues/1718)) ([9e77c61](https://github.com/googleapis/python-aiplatform/commit/9e77c61ab7349d4278274b317d316dbf2b8453c7))
* Log_classification_metrics ([#1742](https://github.com/googleapis/python-aiplatform/issues/1742)) ([3588526](https://github.com/googleapis/python-aiplatform/commit/3588526deb5e5c5cf7467d8ef104cff3dafaa09f))
* PipelineJob should only pass bearer tokens for AR URIs ([b43851c](https://github.com/googleapis/python-aiplatform/commit/b43851c791441e5a789ed43ffb9fe855555bb017))


### Documentation

* Fix create experiment sample ([#1716](https://github.com/googleapis/python-aiplatform/issues/1716)) ([cba7fbf](https://github.com/googleapis/python-aiplatform/commit/cba7fbfba6f06273aa3f95911c92d25720009c28))
* Resurface googleapis.dev and prediction docs ([#1724](https://github.com/googleapis/python-aiplatform/issues/1724)) ([24f0c6f](https://github.com/googleapis/python-aiplatform/commit/24f0c6ff0ab25b2d03c1e0521f680fea8ed35d00))
* **samples:** Improve docstring of Vertex AI Python SDK Model Registry samples ([#1705](https://github.com/googleapis/python-aiplatform/issues/1705)) ([f97e90f](https://github.com/googleapis/python-aiplatform/commit/f97e90f3d40e34c4af92dccbfe8246943e8c79d5))

## [1.18.1](https://github.com/googleapis/python-aiplatform/compare/v1.18.0...v1.18.1) (2022-10-10)


### Bug Fixes

* **deps:** Allow protobuf 3.19.5 ([#1720](https://github.com/googleapis/python-aiplatform/issues/1720)) ([83e3b7c](https://github.com/googleapis/python-aiplatform/commit/83e3b7c284d3fe0b5e40b3dc25c6246e792c24c0))

## [1.18.0](https://github.com/googleapis/python-aiplatform/compare/v1.17.1...v1.18.0) (2022-10-03)


### Features

* Add deleteFeatureValues in aiplatform v1beta1 featurestore_service.proto ([#1670](https://github.com/googleapis/python-aiplatform/issues/1670)) ([9a506ee](https://github.com/googleapis/python-aiplatform/commit/9a506eeae6be3fa33b262dc7782d0bb4f10bf765))
* Add model_source_info to Model in aiplatform v1beta1 model.proto ([#1691](https://github.com/googleapis/python-aiplatform/issues/1691)) ([876fb2a](https://github.com/googleapis/python-aiplatform/commit/876fb2a832a458a4b457b0cd2481e0e783493215))
* Add support for HTTPS URI pipeline templates ([#1683](https://github.com/googleapis/python-aiplatform/issues/1683)) ([926d0b6](https://github.com/googleapis/python-aiplatform/commit/926d0b6f0eb27a3d24dd3a6fb0a16d7c4e5b9662))
* Add support for V1 and V2 classification models for the V1Beta2 API ([#1680](https://github.com/googleapis/python-aiplatform/issues/1680)) ([1cda4b4](https://github.com/googleapis/python-aiplatform/commit/1cda4b4833d31c1be44322850c4e0574e3e46e2b))
* Support complex metrics in Vertex Experiments ([#1698](https://github.com/googleapis/python-aiplatform/issues/1698)) ([ed0492e](https://github.com/googleapis/python-aiplatform/commit/ed0492eb866490e85cd9a5c43fc519510e1f5917))


### Bug Fixes

* **deps:** Require protobuf &gt;= 3.20.2 ([#1699](https://github.com/googleapis/python-aiplatform/issues/1699)) ([c5c77ad](https://github.com/googleapis/python-aiplatform/commit/c5c77ada26d1a51a55f18d4beee47ceab8987103))
* Fix endpoint parsing in ModelDeploymentMonitoringJob.update ([#1671](https://github.com/googleapis/python-aiplatform/issues/1671)) ([186872d](https://github.com/googleapis/python-aiplatform/commit/186872d97d55f1ff8a52f5517fb3dd9b620f678d))
* Project/location parsing for nested resources ([#1700](https://github.com/googleapis/python-aiplatform/issues/1700)) ([9e1d796](https://github.com/googleapis/python-aiplatform/commit/9e1d79671e3be73283842649705be83c3eb3de6a))
* Show inherited SDK methods in pydoc ([#1707](https://github.com/googleapis/python-aiplatform/issues/1707)) ([2b7583b](https://github.com/googleapis/python-aiplatform/commit/2b7583b47194b049b083f4cb490d8abcb32e5b10))


### Documentation

* Fix typos ([#1709](https://github.com/googleapis/python-aiplatform/issues/1709)) ([5fe515c](https://github.com/googleapis/python-aiplatform/commit/5fe515cd17c90103808ca1f11a3899d1250562bf))

## [1.17.1](https://github.com/googleapis/python-aiplatform/compare/v1.17.0...v1.17.1) (2022-09-15)


### Features

* Add enable_simple_view to PipelineJob.list() ([#1614](https://github.com/googleapis/python-aiplatform/issues/1614)) ([627fdf9](https://github.com/googleapis/python-aiplatform/commit/627fdf9542e177d9ee07849c7c7ca6857381a83d))
* Add eval metrics types to get_experiment_df ([#1648](https://github.com/googleapis/python-aiplatform/issues/1648)) ([944b03f](https://github.com/googleapis/python-aiplatform/commit/944b03fc9bd7f1d69f6852c65286b72f49f425df))
* Adding Python 3.10 support + updating google-vizier version ([#1644](https://github.com/googleapis/python-aiplatform/issues/1644)) ([f4766dc](https://github.com/googleapis/python-aiplatform/commit/f4766dc288904ae504e9559c535907c7497e04a9))


### Miscellaneous Chores

* Release 1.17.1 ([#1668](https://github.com/googleapis/python-aiplatform/issues/1668)) ([b54d659](https://github.com/googleapis/python-aiplatform/commit/b54d65930bc48d675679fe3fc99943c418b4a5f5))

## [1.17.0](https://github.com/googleapis/python-aiplatform/compare/v1.16.1...v1.17.0) (2022-09-07)


### Features

* Add input artifact when creating a pipeline ([#1593](https://github.com/googleapis/python-aiplatform/issues/1593)) ([2cf9fe6](https://github.com/googleapis/python-aiplatform/commit/2cf9fe69e6946e21da585ad44d76c2c0c6209cca))
* Add model_monitoring_stats_anomalies,model_monitoring_status to BatchPredictionJob in aiplatform v1beta1 batch_prediction_job.proto ([#1621](https://github.com/googleapis/python-aiplatform/issues/1621)) ([0a1f4e9](https://github.com/googleapis/python-aiplatform/commit/0a1f4e9c2568af585623543c0d9cc291bf2e1c9f))
* Add read_mask to ListPipelineJobsRequest in aiplatform v1 pipeline_service ([#1589](https://github.com/googleapis/python-aiplatform/issues/1589)) ([9e19a40](https://github.com/googleapis/python-aiplatform/commit/9e19a40a4a81cf17759637f0310f0885166b626e))
* Add samples for get execution input and output artifacts ([#1585](https://github.com/googleapis/python-aiplatform/issues/1585)) ([eb5a4b6](https://github.com/googleapis/python-aiplatform/commit/eb5a4b65a16ed13dd45f2c3098b23aeabd5fd565))
* Add support for SDK Method metrics tracking via _USER_AGENT_SDK… ([#1591](https://github.com/googleapis/python-aiplatform/issues/1591)) ([28e56ef](https://github.com/googleapis/python-aiplatform/commit/28e56ef1c8c51e57a5d818b1cd45dd3ec4c5e4bf))
* Support filters in matching engine vector matching ([#1608](https://github.com/googleapis/python-aiplatform/issues/1608)) ([d591d3e](https://github.com/googleapis/python-aiplatform/commit/d591d3e36b76e5bf2f4828041cbdeb783bdcfea5))
* Support model monitoring for batch prediction in Vertex SDK ([#1570](https://github.com/googleapis/python-aiplatform/issues/1570)) ([bbec998](https://github.com/googleapis/python-aiplatform/commit/bbec998ea71aa342fee08d0d5fa115ab36a6f60f))
* Support raw_predict for Endpoint ([#1620](https://github.com/googleapis/python-aiplatform/issues/1620)) ([cc7c968](https://github.com/googleapis/python-aiplatform/commit/cc7c968512db84385c053a8353a8dad8a57aef22))
* Support ResourceName with Version. ([#1609](https://github.com/googleapis/python-aiplatform/issues/1609)) ([737dc2b](https://github.com/googleapis/python-aiplatform/commit/737dc2bacd89e3c9af06bb408abe5ed9304a1397))
* Update the samples of hyperparameter tuning in the public doc ([#1600](https://github.com/googleapis/python-aiplatform/issues/1600)) ([653b759](https://github.com/googleapis/python-aiplatform/commit/653b759a6d5a7740511d4ff6d27762ff4056008e))


### Bug Fixes

* **deps:** Allow protobuf < 5.0.0 ([#1587](https://github.com/googleapis/python-aiplatform/issues/1587)) ([3d3e0aa](https://github.com/googleapis/python-aiplatform/commit/3d3e0aa9f0283dafe3056ed7d3067310535db48c))
* **deps:** require proto-plus >= 1.22.0 ([3d3e0aa](https://github.com/googleapis/python-aiplatform/commit/3d3e0aa9f0283dafe3056ed7d3067310535db48c))
* Log_metrics docstring error ([#1588](https://github.com/googleapis/python-aiplatform/issues/1588)) ([0385c4c](https://github.com/googleapis/python-aiplatform/commit/0385c4c1515b6ddb75732ab5dfdbcf0bd3fb3a00))
* Study.list() method ([#1594](https://github.com/googleapis/python-aiplatform/issues/1594)) ([47eb0ae](https://github.com/googleapis/python-aiplatform/commit/47eb0aef224f14e3ce8f0144b0e266d7bdf5ec83))
* Update Model.list_model_evaluations and get_model_evaluation to use the provided version ([#1616](https://github.com/googleapis/python-aiplatform/issues/1616)) ([8fb836b](https://github.com/googleapis/python-aiplatform/commit/8fb836bcf361230e47d3af9e7ca5882a17da136a))


### Documentation

* ExperimentRun docstring and end_run kwarg ([#1649](https://github.com/googleapis/python-aiplatform/issues/1649)) ([075a6c2](https://github.com/googleapis/python-aiplatform/commit/075a6c2fca09e76db37224fac0d0a2d6096e44ea))
* Remove TODOs from docs ([#1513](https://github.com/googleapis/python-aiplatform/issues/1513)) ([406ed84](https://github.com/googleapis/python-aiplatform/commit/406ed84aca7eed06788289edb7423cfec602b012))
* **samples:** Add AutoML image classification sample ([#923](https://github.com/googleapis/python-aiplatform/issues/923)) ([677b311](https://github.com/googleapis/python-aiplatform/commit/677b311803ecae7069f94f3a8829b93dcd42305f))
* **samples:** Add Model Registry samples to Vertex AI Python SDK ([#1602](https://github.com/googleapis/python-aiplatform/issues/1602)) ([72fd36d](https://github.com/googleapis/python-aiplatform/commit/72fd36d703fb45ac411a0c44160b8b1d5ebb068b))
* **samples:** Added seq2seq sample ([#1595](https://github.com/googleapis/python-aiplatform/issues/1595)) ([4e7175f](https://github.com/googleapis/python-aiplatform/commit/4e7175f6c4a2a4c8fbceae4c351578829ef88519))

## [1.16.1](https://github.com/googleapis/python-aiplatform/compare/v1.16.0...v1.16.1) (2022-08-02)


### Features

* Add google.ClassificationMetrics, google.RegressionMetrics, and google.Forecasting Metrics ([#1549](https://github.com/googleapis/python-aiplatform/issues/1549)) ([3526b3e](https://github.com/googleapis/python-aiplatform/commit/3526b3e28b41488929de1a1c33dad787bee1a794))
* added support for conditional parameters in hyperparameter tuning ([#1544](https://github.com/googleapis/python-aiplatform/issues/1544)) ([744cc38](https://github.com/googleapis/python-aiplatform/commit/744cc380fb2e7ab15b8d55be4af6ccd8ce7b98a7))
* SDK support for model monitoring ([#1249](https://github.com/googleapis/python-aiplatform/issues/1249)) ([18c88d1](https://github.com/googleapis/python-aiplatform/commit/18c88d1d9e5e2e70fab7d435064ae4adc1077f1b))
* support case insensitive match on search facets ([#1523](https://github.com/googleapis/python-aiplatform/issues/1523)) ([cb4d405](https://github.com/googleapis/python-aiplatform/commit/cb4d405264d639bbe5302d30e2c8cba81a37db37))
* Vertex Vizier support in SDK. ([#1434](https://github.com/googleapis/python-aiplatform/issues/1434)) ([b63b3ba](https://github.com/googleapis/python-aiplatform/commit/b63b3ba8b9a18faeeb71eb2565a63b28d6b8d590))


### Bug Fixes

* Correct docstring in Dataset classes ([#1553](https://github.com/googleapis/python-aiplatform/issues/1553)) ([caebb47](https://github.com/googleapis/python-aiplatform/commit/caebb47da6647b7ea395668703468ef99fcef877))


### Miscellaneous Chores

* release 1.16.1 ([#1568](https://github.com/googleapis/python-aiplatform/issues/1568)) ([4437cdd](https://github.com/googleapis/python-aiplatform/commit/4437cddda827d82dadf47ade8b24f05b74d2ae0d))

## [1.16.0](https://github.com/googleapis/python-aiplatform/compare/v1.15.1...v1.16.0) (2022-07-27)


### Features

* Add metadata SDK sample for delete method. ([#1530](https://github.com/googleapis/python-aiplatform/issues/1530)) ([46aa9b5](https://github.com/googleapis/python-aiplatform/commit/46aa9b5e9cf1df72f41ad997d2bd1ca0a40ecfca))
* Add metadata SDK samples for list artifact and list execution ([#1514](https://github.com/googleapis/python-aiplatform/issues/1514)) ([c0d01f1](https://github.com/googleapis/python-aiplatform/commit/c0d01f1d7c9dbcc3df115a5a59eb23b5ce1440dc))
* Add Metadata SDK support and samples for get method ([#1516](https://github.com/googleapis/python-aiplatform/issues/1516)) ([d442248](https://github.com/googleapis/python-aiplatform/commit/d4422483cb8864d0e7b8b23ee4e334156d8a7de6))
* Add samples for Metadata context list, get, and create ([#1525](https://github.com/googleapis/python-aiplatform/issues/1525)) ([d913e1d](https://github.com/googleapis/python-aiplatform/commit/d913e1d777a4f0bb3315ad97283763bdf6d34589))
* Change the Metadata SDK _Context class to an external class ([#1519](https://github.com/googleapis/python-aiplatform/issues/1519)) ([95b107c](https://github.com/googleapis/python-aiplatform/commit/95b107c8727245e1836f9cbddd3f2e331532dd62))
* Refactor schema classes to subclass from _Resource ([#1536](https://github.com/googleapis/python-aiplatform/issues/1536)) ([93002e8](https://github.com/googleapis/python-aiplatform/commit/93002e82778b3ae8570809076f8bf55bf76dcf34))
* Support custom containers in CustomJob.from_local_script ([#1483](https://github.com/googleapis/python-aiplatform/issues/1483)) ([be0b7e1](https://github.com/googleapis/python-aiplatform/commit/be0b7e1ff0649fe78250395950d81af0a848a244))
* Vertex AI Prediction Custom Prediction Routine ([34bbd0a](https://github.com/googleapis/python-aiplatform/commit/34bbd0abbaf29e644ed7703b3251f1de65bf5a86))


### Bug Fixes

* Fixed getting the output GCS bucket in PipelineJob.submit ([#1542](https://github.com/googleapis/python-aiplatform/issues/1542)) ([69d6c7d](https://github.com/googleapis/python-aiplatform/commit/69d6c7dc4e87a9d1e908bd7ab3a5c6f552936c84))
* Pass the PipelineJob credentials to `create_gcs_bucket_for_pipeline_artifacts_if_it_does_not_exist` ([#1537](https://github.com/googleapis/python-aiplatform/issues/1537)) ([b53e2b5](https://github.com/googleapis/python-aiplatform/commit/b53e2b5942faad388a6c34bd4af700b666ed1f1c))

## [1.15.1](https://github.com/googleapis/python-aiplatform/compare/v1.15.0...v1.15.1) (2022-07-18)


### Features

* add get_associated_experiment method to pipeline_jobs ([#1476](https://github.com/googleapis/python-aiplatform/issues/1476)) ([e9f2c3c](https://github.com/googleapis/python-aiplatform/commit/e9f2c3c54740e4735f864c5eabd3b0ac9655b6de))
* Add sample for create artifact and execution using the Metadata SDK. ([#1462](https://github.com/googleapis/python-aiplatform/issues/1462)) ([1fc7dd9](https://github.com/googleapis/python-aiplatform/commit/1fc7dd99d618a462273d597518f007c6b0cb188e))
* Add support for start_execution in MLMD SDK.  ([#1465](https://github.com/googleapis/python-aiplatform/issues/1465)) ([298958f](https://github.com/googleapis/python-aiplatform/commit/298958f404f902b9e1d7e93bbceb97b43612f649))
* Add support for Vertex Tables Q2 regions ([#1498](https://github.com/googleapis/python-aiplatform/issues/1498)) ([1b16f90](https://github.com/googleapis/python-aiplatform/commit/1b16f90821d13fc3fb693d60b44c2e57444c4287))
* Added the PipelineJob.from_pipeline_func method ([#1415](https://github.com/googleapis/python-aiplatform/issues/1415)) ([6ef05de](https://github.com/googleapis/python-aiplatform/commit/6ef05de85b51a67f8df6ad8813518eb7c9158e71))


### Bug Fixes

* **deps:** require google-api-core>=1.32.0,>=2.8.0 ([#1512](https://github.com/googleapis/python-aiplatform/issues/1512)) ([6d09dee](https://github.com/googleapis/python-aiplatform/commit/6d09deec18d1152705dc55e912d4d0248ea64672))
* Unbreak aiplatform.Experiment.create ([#1509](https://github.com/googleapis/python-aiplatform/issues/1509)) ([558c141](https://github.com/googleapis/python-aiplatform/commit/558c1410b43356da0832b3ded78977ee80be93cd))


### Miscellaneous Chores

* release 1.15.1 ([#1510](https://github.com/googleapis/python-aiplatform/issues/1510)) ([e500ff3](https://github.com/googleapis/python-aiplatform/commit/e500ff3b96384e25c08a50bd16e6e0fd6266d98b))

## [1.15.0](https://github.com/googleapis/python-aiplatform/compare/v1.14.0...v1.15.0) (2022-06-29)


### Features

* add default_skew_threshold to TrainingPredictionSkewDetectionConfig in aiplatform v1beta1, v1 model_monitoring.proto ([#1411](https://github.com/googleapis/python-aiplatform/issues/1411)) ([7a8e3be](https://github.com/googleapis/python-aiplatform/commit/7a8e3bed0f1084ab6f33c032b9c436f9b57da6cd))
* add model_monitoring_config to BatchPredictionJob in aiplatform v1beta1 batch_prediction_job.proto ([#1450](https://github.com/googleapis/python-aiplatform/issues/1450)) ([d35df58](https://github.com/googleapis/python-aiplatform/commit/d35df58f703e04c59bcdaa7b763920fca3750220))
* add model_version_id to BatchPredictionJob in aiplatform v1 batch_prediction_job.proto ([#1453](https://github.com/googleapis/python-aiplatform/issues/1453)) ([9ef057a](https://github.com/googleapis/python-aiplatform/commit/9ef057abe35895b57dcbe3cbab619a1b785c0b95))
* add model_version_id to UploadModelResponse in aiplatform v1 model_service.proto ([#1442](https://github.com/googleapis/python-aiplatform/issues/1442)) ([1c198f1](https://github.com/googleapis/python-aiplatform/commit/1c198f1d457d41a1bbb0ea501e8cff45bb119f8e))
* Add PrivateEndpoint class and HTTP methods ([#1033](https://github.com/googleapis/python-aiplatform/issues/1033)) ([425a32f](https://github.com/googleapis/python-aiplatform/commit/425a32fccab2147101bec0031ca139bb311b7cff))
* add support for accepting an Artifact Registry URL in pipeline_job ([#1405](https://github.com/googleapis/python-aiplatform/issues/1405)) ([e138cfd](https://github.com/googleapis/python-aiplatform/commit/e138cfd8b8f8033a562c1b7f2d340042f57db27e))
* add support for failure_policy in PipelineJob ([#1452](https://github.com/googleapis/python-aiplatform/issues/1452)) ([d0968ea](https://github.com/googleapis/python-aiplatform/commit/d0968ead02d14edf209f36a18b61a9400233a4b8))
* Improved metadata artifact and execution creation using python / SDK  ([#1430](https://github.com/googleapis/python-aiplatform/issues/1430)) ([6c4374f](https://github.com/googleapis/python-aiplatform/commit/6c4374f893d34f8c2310223afb39f48f8961a0bb))
* support dataset update ([#1416](https://github.com/googleapis/python-aiplatform/issues/1416)) ([e3eb82f](https://github.com/googleapis/python-aiplatform/commit/e3eb82f59d3f28dfedd71b9e69a0e967a01eada5))
* Support for Model Versioning ([#1438](https://github.com/googleapis/python-aiplatform/issues/1438)) ([d890685](https://github.com/googleapis/python-aiplatform/commit/d890685c981d47992e4cdb2c9196f64dc520a5ff))
* Vertex AI Experiments GA ([#1410](https://github.com/googleapis/python-aiplatform/issues/1410)) ([24d1bb6](https://github.com/googleapis/python-aiplatform/commit/24d1bb6d85dda76b9895dc924c7e0437864ea7a2))


### Bug Fixes

* Fixed docstrings for wildcards and matching engine type ([#1220](https://github.com/googleapis/python-aiplatform/issues/1220)) ([d778dee](https://github.com/googleapis/python-aiplatform/commit/d778dee69402bc280bf6cf0d7cf08cf165be5299))
* Removed dirs_exist_ok parameter as it's not backwards compatible ([#1170](https://github.com/googleapis/python-aiplatform/issues/1170)) ([50d4129](https://github.com/googleapis/python-aiplatform/commit/50d41293d699643d3753693af79af95f68a2b07a))

## [1.14.0](https://github.com/googleapis/python-aiplatform/compare/v1.13.1...v1.14.0) (2022-06-08)


### Features

* add a way to easily clone a PipelineJob ([#1239](https://github.com/googleapis/python-aiplatform/issues/1239)) ([efaf6ed](https://github.com/googleapis/python-aiplatform/commit/efaf6edc36262b095aa13d0b40348c20e39b3fc6))
* add display_name and metadata to ModelEvaluation in aiplatform model_evaluation.proto ([b6bf6dc](https://github.com/googleapis/python-aiplatform/commit/b6bf6dc643274220e6eeca6479b5f9df61b11d16))
* add Examples to Explanation related messages in aiplatform v1beta1 explanation.proto ([b6bf6dc](https://github.com/googleapis/python-aiplatform/commit/b6bf6dc643274220e6eeca6479b5f9df61b11d16))
* Add hierarchy and window configs to Vertex Forecasting training job ([#1255](https://github.com/googleapis/python-aiplatform/issues/1255)) ([8560fa8](https://github.com/googleapis/python-aiplatform/commit/8560fa88c8e0fe51f2ae56f68be575e85db3696a))
* add holiday regions for vertex forecasting ([#1253](https://github.com/googleapis/python-aiplatform/issues/1253)) ([0036ab0](https://github.com/googleapis/python-aiplatform/commit/0036ab07004e0c9ae7806c4c2c25f22d5af4a978))
* add IAM policy to aiplatform_v1beta1.yaml ([b6bf6dc](https://github.com/googleapis/python-aiplatform/commit/b6bf6dc643274220e6eeca6479b5f9df61b11d16))
* add latent_space_source to ExplanationMetadata in aiplatform v1 explanation_metadata.proto ([b6bf6dc](https://github.com/googleapis/python-aiplatform/commit/b6bf6dc643274220e6eeca6479b5f9df61b11d16))
* add latent_space_source to ExplanationMetadata in aiplatform v1beta1 explanation_metadata.proto ([b6bf6dc](https://github.com/googleapis/python-aiplatform/commit/b6bf6dc643274220e6eeca6479b5f9df61b11d16))
* add preset configuration for example-based explanations in aiplatform v1beta1 explanation.proto ([b6bf6dc](https://github.com/googleapis/python-aiplatform/commit/b6bf6dc643274220e6eeca6479b5f9df61b11d16))
* add scaling to OnlineServingConfig in aiplatform v1 featurestore.proto ([b6bf6dc](https://github.com/googleapis/python-aiplatform/commit/b6bf6dc643274220e6eeca6479b5f9df61b11d16))
* add seq2seq forecasting training job ([#1196](https://github.com/googleapis/python-aiplatform/issues/1196)) ([643d335](https://github.com/googleapis/python-aiplatform/commit/643d335693ec57848949ee173401867a1188678b))
* add successful_forecast_point_count to CompletionStats in completion_stats.proto ([b6bf6dc](https://github.com/googleapis/python-aiplatform/commit/b6bf6dc643274220e6eeca6479b5f9df61b11d16))
* add template_metadata to PipelineJob in aiplatform v1 pipeline_job.proto ([b6bf6dc](https://github.com/googleapis/python-aiplatform/commit/b6bf6dc643274220e6eeca6479b5f9df61b11d16))
* Add Vertex Forecasting E2E test. ([#1248](https://github.com/googleapis/python-aiplatform/issues/1248)) ([e82c179](https://github.com/googleapis/python-aiplatform/commit/e82c1792293396045a1032df015a3700fc38609b))
* Added forecasting snippets and fixed bugs with existing snippets ([#1210](https://github.com/googleapis/python-aiplatform/issues/1210)) ([4e4bff5](https://github.com/googleapis/python-aiplatform/commit/4e4bff5cac3a99e7f55145ab2aee83b20af67060))


### Bug Fixes

* change endpoint update method to return resource ([#1409](https://github.com/googleapis/python-aiplatform/issues/1409)) ([44e279b](https://github.com/googleapis/python-aiplatform/commit/44e279b15a1b03bf234111333517153ffdbaf696))
* Changed system test to use list_models() correctly ([#1397](https://github.com/googleapis/python-aiplatform/issues/1397)) ([a3da19a](https://github.com/googleapis/python-aiplatform/commit/a3da19aac6bdd3fa8d218408582205f7241a4b04))
* Pinned protobuf to prevent issues with pb files. ([#1398](https://github.com/googleapis/python-aiplatform/issues/1398)) ([7a54637](https://github.com/googleapis/python-aiplatform/commit/7a54637d9b0e7a52ec4648505a6902610c4cc5b7))


### Documentation

* fix changelog header to consistent size ([#1404](https://github.com/googleapis/python-aiplatform/issues/1404)) ([f6a7e6f](https://github.com/googleapis/python-aiplatform/commit/f6a7e6f35188d6032fc8b34a3c205b0632029e02))

## [1.13.1](https://github.com/googleapis/python-aiplatform/compare/v1.13.0...v1.13.1) (2022-05-26)


### Features

* add batch_size kwarg for batch prediction jobs ([#1194](https://github.com/googleapis/python-aiplatform/issues/1194)) ([50bdb01](https://github.com/googleapis/python-aiplatform/commit/50bdb01504740ed31de788d8a160f3e2be7f55df))
* add update endpoint ([#1162](https://github.com/googleapis/python-aiplatform/issues/1162)) ([0ecfe1e](https://github.com/googleapis/python-aiplatform/commit/0ecfe1e7ab8687c13cb4267985e8b6ebc7bd2534))
* support autoscaling metrics when deploying models ([#1197](https://github.com/googleapis/python-aiplatform/issues/1197)) ([095717c](https://github.com/googleapis/python-aiplatform/commit/095717c8b77dc5d66e677413a437ea6ed92e0b1a))


### Bug Fixes

* check in service proto file ([#1174](https://github.com/googleapis/python-aiplatform/issues/1174)) ([5fdf151](https://github.com/googleapis/python-aiplatform/commit/5fdf151ee0d0a630c07a75dc8f19906e7ad1aa8a))
* regenerate pb2 files using grpcio-tools ([#1394](https://github.com/googleapis/python-aiplatform/issues/1394)) ([406c868](https://github.com/googleapis/python-aiplatform/commit/406c868344280d424f4191c98bcbbdeaf947b2d1))


### Documentation

* update aiplatform SDK arrangement for Sphinx ([#1163](https://github.com/googleapis/python-aiplatform/issues/1163)) ([e9510ea](https://github.com/googleapis/python-aiplatform/commit/e9510ea6344a296e0c93ddf32280cf4c010ee4f1))


### Miscellaneous Chores

* release 1.13.1 ([#1395](https://github.com/googleapis/python-aiplatform/issues/1395)) ([df78407](https://github.com/googleapis/python-aiplatform/commit/df78407b2f14c95c9e84b4b1375a8de5bc9c7bb5))

## [1.13.0](https://github.com/googleapis/python-aiplatform/compare/v1.12.1...v1.13.0) (2022-05-09)


### Features

* add ConvexAutomatedStoppingSpec to StudySpec in aiplatform v1 study.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add ConvexAutomatedStoppingSpec to StudySpec in aiplatform v1beta1 study.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add JOB_STATE_UPDATING to JobState in aiplatform v1 job_state.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add JOB_STATE_UPDATING to JobState in aiplatform v1beta1 job_state.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add LatestMonitoringPipelineMetadata to ModelDeploymentMonitoringJob in aiplatform v1beta1 model_deployment_monitoring_job.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add ListModelVersion, DeleteModelVersion, and MergeVersionAliases rpcs to aiplatform v1beta1 model_service.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add MfsMount in aiplatform v1 machine_resources.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add MfsMount in aiplatform v1beta1 machine_resources.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add model_id and parent_model to TrainingPipeline in aiplatform v1beta1 training_pipeline.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add model_version_id to DeployedModel in aiplatform v1beta1 endpoint.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add model_version_id to PredictResponse in aiplatform v1beta1 prediction_service.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add model_version_id to UploadModelRequest and UploadModelResponse in aiplatform v1beta1 model_service.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add nfs_mounts to WorkPoolSpec in aiplatform v1 custom_job.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add nfs_mounts to WorkPoolSpec in aiplatform v1beta1 custom_job.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add Pandas DataFrame support to TabularDataset ([#1185](https://github.com/googleapis/python-aiplatform/issues/1185)) ([4fe4558](https://github.com/googleapis/python-aiplatform/commit/4fe4558ea0aaf73e3c0e9715ae90cb729a4c5678))
* add PredictRequestResponseLoggingConfig to aiplatform v1beta1 endpoint.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add reserved_ip_ranges to CustomJobSpec in aiplatform v1 custom_job.proto ([#1165](https://github.com/googleapis/python-aiplatform/issues/1165)) ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add reserved_ip_ranges to CustomJobSpec in aiplatform v1beta1 custom_job.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* add template_metadata to PipelineJob in aiplatform v1beta1 pipeline_job.proto ([#1186](https://github.com/googleapis/python-aiplatform/issues/1186)) ([99aca4a](https://github.com/googleapis/python-aiplatform/commit/99aca4a9b0deeefd294cfd64fa3e247cc41e006c))
* add version_id to Model in aiplatform v1beta1 model.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))
* allow creating featurestore without online node ([#1180](https://github.com/googleapis/python-aiplatform/issues/1180)) ([3224ae3](https://github.com/googleapis/python-aiplatform/commit/3224ae3402e9493866dd4958d011a431968b9c2c))
* Allow users to specify timestamp split for vertex forecasting ([#1187](https://github.com/googleapis/python-aiplatform/issues/1187)) ([ee49e00](https://github.com/googleapis/python-aiplatform/commit/ee49e004c8fbd0c8c27760b525c6e7431057a45e))
* Make matching engine API public ([#1192](https://github.com/googleapis/python-aiplatform/issues/1192)) ([469db6b](https://github.com/googleapis/python-aiplatform/commit/469db6b08a9aa7fc64d8ea27f7e2e2fb2e9f643b))
* rename Similarity to Examples, and similarity to examples in ExplanationParameters in aiplatform v1beta1 explanation.proto ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))


### Documentation

* fix type in docstring for map fields ([847ad78](https://github.com/googleapis/python-aiplatform/commit/847ad789e09aec14238a7476a3fa88729ce24d6f))

## [1.12.1](https://github.com/googleapis/python-aiplatform/compare/v1.12.0...v1.12.1) (2022-04-20)


### Features

* Add endpoind_id arg to Endpoint#create ([#1168](https://github.com/googleapis/python-aiplatform/issues/1168)) ([4c21993](https://github.com/googleapis/python-aiplatform/commit/4c21993642b84d7595ead7a63424260deafaf43c))
* add ModelEvaluation support ([#1167](https://github.com/googleapis/python-aiplatform/issues/1167)) ([10f95cd](https://github.com/googleapis/python-aiplatform/commit/10f95cde5e0282a99041ff2108111970f52379f3))


### Bug Fixes

* change default for create_request_timeout arg to None ([#1175](https://github.com/googleapis/python-aiplatform/issues/1175)) ([47791f7](https://github.com/googleapis/python-aiplatform/commit/47791f79c56a67be7503b5d5d4eb72dc409b18a0))


### Documentation

* endpoint.create => aiplatform.Endpoint.create ([#1153](https://github.com/googleapis/python-aiplatform/issues/1153)) ([1122a26](https://github.com/googleapis/python-aiplatform/commit/1122a26fd01d4c964055ca85a683de0c91867b6f))
* update changelog headers ([#1164](https://github.com/googleapis/python-aiplatform/issues/1164)) ([c1e899d](https://github.com/googleapis/python-aiplatform/commit/c1e899dba3f57e515b1f1958e962f355276460c4))
* update model code snippet order in README ([#1154](https://github.com/googleapis/python-aiplatform/issues/1154)) ([404d7f1](https://github.com/googleapis/python-aiplatform/commit/404d7f13d8666ea673743ab54928046eb64ee542))


### Miscellaneous Chores

* release 1.12.1 ([#1176](https://github.com/googleapis/python-aiplatform/issues/1176)) ([f98d92e](https://github.com/googleapis/python-aiplatform/commit/f98d92ecf7ad42fdbb095e65f98800bc6b2d3d12))

## [1.12.0](https://github.com/googleapis/python-aiplatform/compare/v1.11.0...v1.12.0) (2022-04-07)


### Features

* add categorical_threshold_config to FeaturestoreMonitoringConfig in aiplatform v1 featurestore_monitoring.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add categorical_threshold_config to FeaturestoreMonitoringConfig in aiplatform v1beta1 featurestore_monitoring.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add disable_monitoring to Feature in aiplatform v1 feature.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add disable_monitoring to Feature in aiplatform v1beta1 feature.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* Add done method for pipeline, training, and batch prediction jobs ([#1062](https://github.com/googleapis/python-aiplatform/issues/1062)) ([f3338fc](https://github.com/googleapis/python-aiplatform/commit/f3338fcd4f51072ee86b765ee580cfe3c4b222ce))
* add import_features_analysis to FeaturestoreMonitoringConfig in aiplatform v1 featurestore_monitoring.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add import_features_analysis to FeaturestoreMonitoringConfig in aiplatform v1beta1 featurestore_monitoring.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add ImportModelEvaluation in aiplatform v1 model_service.proto ([#1105](https://github.com/googleapis/python-aiplatform/issues/1105)) ([ef5930c](https://github.com/googleapis/python-aiplatform/commit/ef5930c58838ce51f92ef1acb941f5141c83faad))
* add monitoring_config to EntityType in aiplatform v1 entity_type.proto ([#1077](https://github.com/googleapis/python-aiplatform/issues/1077)) ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add monitoring_stats_anomalies to Feature in aiplatform v1 feature.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add monitoring_stats_anomalies to Feature in aiplatform v1beta1 feature.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add numerical_threshold_config to FeaturestoreMonitoringConfig in aiplatform v1 featurestore_monitoring.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add numerical_threshold_config to FeaturestoreMonitoringConfig in aiplatform v1beta1 featurestore_monitoring.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add objective to MonitoringStatsSpec in aiplatform v1 featurestore_service.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add objective to MonitoringStatsSpec in aiplatform v1beta1 featurestore_service.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add PredictRequestResponseLoggingConfig to Endpoint in aiplatform v1 endpoint.proto ([#1072](https://github.com/googleapis/python-aiplatform/issues/1072)) ([be0ccc4](https://github.com/googleapis/python-aiplatform/commit/be0ccc488dac22128be317ca40337d6b93af0906))
* add staleness_days to SnapshotAnalysis in aiplatform v1 featurestore_monitoring.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* add staleness_days to SnapshotAnalysis in aiplatform v1beta1 featurestore_monitoring.proto ([38f3711](https://github.com/googleapis/python-aiplatform/commit/38f3711bd76bbcfe4ce48739bb11049e2711d47f))
* Add support for Vertex Tables Q1 regions ([#1065](https://github.com/googleapis/python-aiplatform/issues/1065)) ([6383d4f](https://github.com/googleapis/python-aiplatform/commit/6383d4f20f1ab0a7634c1028cb9f270e91c31d2a))
* add timeout arg across SDK ([#1099](https://github.com/googleapis/python-aiplatform/issues/1099)) ([184f7f3](https://github.com/googleapis/python-aiplatform/commit/184f7f327aa00b4c8d1acc24dcb1c4c4be6c5bcc))
* Add timeout arguments to Endpoint.predict and Endpoint.explain ([#1094](https://github.com/googleapis/python-aiplatform/issues/1094)) ([cc59e60](https://github.com/googleapis/python-aiplatform/commit/cc59e60193a72bb57d699cabea03ab7bdd386b0e))
* Made display_name parameter optional for most calls ([#882](https://github.com/googleapis/python-aiplatform/issues/882)) ([400b760](https://github.com/googleapis/python-aiplatform/commit/400b7608afeaca9a36936cabd402c5322eb9345b))
* **sdk:** enable loading both JSON and YAML pipelines IR ([#1089](https://github.com/googleapis/python-aiplatform/issues/1089)) ([f2e70b1](https://github.com/googleapis/python-aiplatform/commit/f2e70b1563171b5a92a2c40edf29ae373bbeb175))
* **v1beta1:** add `service_account` to `BatchPredictionJob` in `batch_prediction_job.proto` ([#1084](https://github.com/googleapis/python-aiplatform/issues/1084)) ([b7a5177](https://github.com/googleapis/python-aiplatform/commit/b7a517731bc8127d4186838bfb88fa883b2be853))


### Bug Fixes

* add resource manager utils to get project ID from project number ([#1068](https://github.com/googleapis/python-aiplatform/issues/1068)) ([f10a1d4](https://github.com/googleapis/python-aiplatform/commit/f10a1d4280c3e653c9f4795f0423bf07a23acdf9))
* add self.wait() in operations after optional_sync supported resource creation ([#1083](https://github.com/googleapis/python-aiplatform/issues/1083)) ([79aeec1](https://github.com/googleapis/python-aiplatform/commit/79aeec1380068318398851b2a7b2fd6ddee7fa8b))
* Don't throw exception when getting representation of unrun GCA objects ([#1071](https://github.com/googleapis/python-aiplatform/issues/1071)) ([c9ba060](https://github.com/googleapis/python-aiplatform/commit/c9ba0603e6a8e3d772af67367242aad7a18e03c8))
* Fix import error string showing wrong pip install path ([#1076](https://github.com/googleapis/python-aiplatform/issues/1076)) ([74ffa19](https://github.com/googleapis/python-aiplatform/commit/74ffa19e7d540f6bb5f21d2335c2a5d23cc49ee2))
* Fixed getting project ID when running on Vertex AI; Fixes [#852](https://github.com/googleapis/python-aiplatform/issues/852) ([#943](https://github.com/googleapis/python-aiplatform/issues/943)) ([876cb33](https://github.com/googleapis/python-aiplatform/commit/876cb33a407cfea5c965e4f348056b147b1d16c3))
* Give aiplatform logging its own log namespace, let the user configure their own root logger ([#1081](https://github.com/googleapis/python-aiplatform/issues/1081)) ([fb78243](https://github.com/googleapis/python-aiplatform/commit/fb782434d456f41c6c6bd6664b203cebb53131b8))
* Honoring the model's supported_deployment_resources_types ([#865](https://github.com/googleapis/python-aiplatform/issues/865)) ([db34b85](https://github.com/googleapis/python-aiplatform/commit/db34b85aaf211ca491313d2b8ae2a45253109614))
* missing reference to logged_web_access_uris ([#1056](https://github.com/googleapis/python-aiplatform/issues/1056)) ([198a1b5](https://github.com/googleapis/python-aiplatform/commit/198a1b5753f509c9137a8d9e9b56d68e6e386563))
* system tests failure from test_upload_and_deploy_xgboost_model ([#1149](https://github.com/googleapis/python-aiplatform/issues/1149)) ([c8422a9](https://github.com/googleapis/python-aiplatform/commit/c8422a9b807e092f2d48e7f3fa8b40c8724cc028))


### Documentation

* fix CustomContainerTrainingJob example in docstring ([#1101](https://github.com/googleapis/python-aiplatform/issues/1101)) ([d2fb9db](https://github.com/googleapis/python-aiplatform/commit/d2fb9db095d1acb15894df3d0a5e66128ce8f14e))
* improve bigquery_destination_prefix docstring ([#1098](https://github.com/googleapis/python-aiplatform/issues/1098)) ([a46df64](https://github.com/googleapis/python-aiplatform/commit/a46df64ab99aee8d7e47b44394a234243dc2a0f8))
* Include time dependency in documentation for weight, time, and target columns. ([#1102](https://github.com/googleapis/python-aiplatform/issues/1102)) ([52273c2](https://github.com/googleapis/python-aiplatform/commit/52273c2108c9bb24eadab214036f2ef93b847321))
* **samples:** read, import, batch_serve, batch_create features ([#1046](https://github.com/googleapis/python-aiplatform/issues/1046)) ([80dd40d](https://github.com/googleapis/python-aiplatform/commit/80dd40dcb830ece3b5442d60834357ada6583204))
* Update AutoML Video docstring ([#987](https://github.com/googleapis/python-aiplatform/issues/987)) ([6002d5d](https://github.com/googleapis/python-aiplatform/commit/6002d5d9bf24542f9f3f844e469bc3f8ad9636ec))

## [1.11.0](https://github.com/googleapis/python-aiplatform/compare/v1.10.0...v1.11.0) (2022-03-03)


### Features

* add additional_experiement flag in the tables and forecasting training job ([#979](https://github.com/googleapis/python-aiplatform/issues/979)) ([5fe59a4](https://github.com/googleapis/python-aiplatform/commit/5fe59a4015882d56c22f9973aff888966dd53a2e))
* add TPU_V2 & TPU_V3 values to AcceleratorType in aiplatform v1/v1beta1 accelerator_type.proto ([#1010](https://github.com/googleapis/python-aiplatform/issues/1010)) ([09c2e8a](https://github.com/googleapis/python-aiplatform/commit/09c2e8a368c6d265d99acfb12addd5ba6f1a50e6))
* Added scheduling to CustomTrainingJob, CustomPythonPackageTrainingJob, CustomContainerTrainingJob ([#970](https://github.com/googleapis/python-aiplatform/issues/970)) ([89078e0](https://github.com/googleapis/python-aiplatform/commit/89078e0d2a719e2b0d25ae36ecd06c356a5a33c9))


### Bug Fixes

* **deps:** allow google-cloud-storage < 3.0.0dev ([#1008](https://github.com/googleapis/python-aiplatform/issues/1008)) ([1c34154](https://github.com/googleapis/python-aiplatform/commit/1c341544e9bd94c6ff0ee41177565c8c078673a3))
* **deps:** require google-api-core>=1.31.5, >=2.3.2 ([#1050](https://github.com/googleapis/python-aiplatform/issues/1050)) ([dfbd68a](https://github.com/googleapis/python-aiplatform/commit/dfbd68a79f1c892c4380405dd900deb6ac6574a6))
* **deps:** require proto-plus>=1.15.0 ([dfbd68a](https://github.com/googleapis/python-aiplatform/commit/dfbd68a79f1c892c4380405dd900deb6ac6574a6))
* enforce bq SchemaField field_type and mode using feature value_type ([#1019](https://github.com/googleapis/python-aiplatform/issues/1019)) ([095bea2](https://github.com/googleapis/python-aiplatform/commit/095bea23bc15a490ddbb1a8edac7f5db626bc659))
* Fix create_lit_model_from_endpoint not accepting models that don't return a dictionary. ([#1020](https://github.com/googleapis/python-aiplatform/issues/1020)) ([b9a057d](https://github.com/googleapis/python-aiplatform/commit/b9a057d001deb8727cb725d44bb5528dce330653))
* loosen assertions for system test featurestore ([#1040](https://github.com/googleapis/python-aiplatform/issues/1040)) ([2ba404f](https://github.com/googleapis/python-aiplatform/commit/2ba404f8bfbccd7a18ef613417912ed94882c4bd))
* remove empty scripts kwarg in setup.py ([#1014](https://github.com/googleapis/python-aiplatform/issues/1014)) ([ef3fcc8](https://github.com/googleapis/python-aiplatform/commit/ef3fcc86fb3808b37706470c8c49903ec3a302fb))
* show logs when TFX pipelines are submitted ([#976](https://github.com/googleapis/python-aiplatform/issues/976)) ([c10923b](https://github.com/googleapis/python-aiplatform/commit/c10923b47b9b9941d14ae2c5398348d971a23f9d))
* update system test_model_upload to use BUILD_SPECIFIC_GCP_PROJECT ([#1043](https://github.com/googleapis/python-aiplatform/issues/1043)) ([e7d2719](https://github.com/googleapis/python-aiplatform/commit/e7d27193f323f88f4238206ecb380d746d98df31))


### Documentation

* **samples:** add samples to create/delete featurestore ([#980](https://github.com/googleapis/python-aiplatform/issues/980)) ([5ee6354](https://github.com/googleapis/python-aiplatform/commit/5ee6354a12c6422015acb81caef32d6d2f52c838))
* **samples:** added create feature and create entity type samples and tests ([#984](https://github.com/googleapis/python-aiplatform/issues/984)) ([d221e6b](https://github.com/googleapis/python-aiplatform/commit/d221e6bebd7fb98a8c6e3f3b8ae507f2f214128f))

## [1.10.0](https://github.com/googleapis/python-aiplatform/compare/v1.9.0...v1.10.0) (2022-02-07)


### Features

* _TrainingScriptPythonPackager to support folders ([#812](https://github.com/googleapis/python-aiplatform/issues/812)) ([3aec6a7](https://github.com/googleapis/python-aiplatform/commit/3aec6a7b8f26ef2a5b378a6224d6402e3b42c917))
* add dedicated_resources to DeployedIndex in aiplatform v1beta1 index_endpoint.proto feat: add Scaling to OnlineServingConfig in aiplatform v1beta1 featurestore.proto chore: sort imports ([#991](https://github.com/googleapis/python-aiplatform/issues/991)) ([7a7f0d4](https://github.com/googleapis/python-aiplatform/commit/7a7f0d45f3d08c93b11fcd2c5a265a8db4b0c890))
* add dedicated_resources to DeployedIndex message in aiplatform v1 index_endpoint.proto chore: sort imports ([#990](https://github.com/googleapis/python-aiplatform/issues/990)) ([a814923](https://github.com/googleapis/python-aiplatform/commit/a8149233bcd857e75700c6ec7d29c0aabf1687c1))
* Add XAI SDK integration to TensorFlow models with LIT integration ([#917](https://github.com/googleapis/python-aiplatform/issues/917)) ([ea2b5cf](https://github.com/googleapis/python-aiplatform/commit/ea2b5cfbcafead1c63009fda10bd44a00d560efb))
* Added `aiplatform.Model.update`  method ([#952](https://github.com/googleapis/python-aiplatform/issues/952)) ([44e208a](https://github.com/googleapis/python-aiplatform/commit/44e208a8dbf082e770373d58c31b3ad3e8b39f4f))
* Enable europe-west6 and northamerica-northeast2 regions ([0f6b670](https://github.com/googleapis/python-aiplatform/commit/0f6b6701e96fb0ec345e81560d03059a7900160f))
* enable feature store batch serve to BigQuery and GCS for csv and tfrecord ([#919](https://github.com/googleapis/python-aiplatform/issues/919)) ([c840728](https://github.com/googleapis/python-aiplatform/commit/c840728e503eea3300e9629405978e28c6aafec7))
* enable feature store batch serve to Pandas DataFrame; fix: read instances uri for batch serve ([#983](https://github.com/googleapis/python-aiplatform/issues/983)) ([e0fec36](https://github.com/googleapis/python-aiplatform/commit/e0fec36686e373c13acca3203372572c760c7af4))
* enable feature store online serving ([#918](https://github.com/googleapis/python-aiplatform/issues/918)) ([b8f5f82](https://github.com/googleapis/python-aiplatform/commit/b8f5f82ae43edfb933305a074c315e2f3239b4b1))
* enable ingest from pd.DataFrame ([#977](https://github.com/googleapis/python-aiplatform/issues/977)) ([9289f2d](https://github.com/googleapis/python-aiplatform/commit/9289f2d3ce424f3f9754a3dd23883e25dec1300f))
* Open LIT with a deployed model ([#963](https://github.com/googleapis/python-aiplatform/issues/963)) ([ea16849](https://github.com/googleapis/python-aiplatform/commit/ea16849f936d7a2e8402fd235decefe5972685ed))


### Bug Fixes

* Fixed BigQuery datasets that have colon in URI ([#855](https://github.com/googleapis/python-aiplatform/issues/855)) ([153578f](https://github.com/googleapis/python-aiplatform/commit/153578f19d57db96e3674b2d797c5352c107f936))
* Fixed integration test for model.upload ([#975](https://github.com/googleapis/python-aiplatform/issues/975)) ([0ca3747](https://github.com/googleapis/python-aiplatform/commit/0ca374769f922fd427c5b6f58c9ce1ab40f18d18))
* rename teardown fixture ([#1004](https://github.com/googleapis/python-aiplatform/issues/1004)) ([fcd0096](https://github.com/googleapis/python-aiplatform/commit/fcd00969dbbbf06887dfdbaa6bc65b135c24f95f))


### Documentation

* **samples:** replace deprecated fields in create_training_pipeline_tabular_forecasting_sample.py ([#981](https://github.com/googleapis/python-aiplatform/issues/981)) ([9ebc972](https://github.com/googleapis/python-aiplatform/commit/9ebc972bba972b1e1920db422ed28a721e90329d))

## [1.9.0](https://www.github.com/googleapis/python-aiplatform/compare/v1.8.1...v1.9.0) (2021-12-29)


### Features

* add create in Featurestore, EntityType, Feature; add create_entity_type in Featurestore; add create_feature, batch_create_features in EntityType; add ingest_from_* for bq and gcs in EntityType; add and update delete with force delete nested resources ([#872](https://www.github.com/googleapis/python-aiplatform/issues/872)) ([ba11c3d](https://www.github.com/googleapis/python-aiplatform/commit/ba11c3d3cd8d3869e2deb3207a8698fa7ce284ec))
* Add LIT methods for Pandas DataFrame and TensorFlow saved model. ([#874](https://www.github.com/googleapis/python-aiplatform/issues/874)) ([03cf301](https://www.github.com/googleapis/python-aiplatform/commit/03cf301989a5802b122803eac7a2d03f2d1769fb))
* Add support to create TensorboardExperiment ([#909](https://www.github.com/googleapis/python-aiplatform/issues/909)) ([96ce738](https://www.github.com/googleapis/python-aiplatform/commit/96ce7387ac58e0ec7cb6a7f6d6a6e422eae5da96))
* Add support to create TensorboardRun ([#912](https://www.github.com/googleapis/python-aiplatform/issues/912)) ([8df74a2](https://www.github.com/googleapis/python-aiplatform/commit/8df74a29df0adb95fff5500fcc9d7a025012ab5e))


### Bug Fixes

* Fix timestamp proto util to default to timestamp at call time. ([#933](https://www.github.com/googleapis/python-aiplatform/issues/933)) ([d72a254](https://www.github.com/googleapis/python-aiplatform/commit/d72a254e97cf74f3fdd55a32a4af86737243593a))
* Improve handling of undeploying model without redistributing remaining traffic ([#898](https://www.github.com/googleapis/python-aiplatform/issues/898)) ([8a8a4fa](https://www.github.com/googleapis/python-aiplatform/commit/8a8a4faa667bde2a4df04afa23a6dd5b1856f958))
* issues/192254729 ([#914](https://www.github.com/googleapis/python-aiplatform/issues/914)) ([3ec620c](https://www.github.com/googleapis/python-aiplatform/commit/3ec620c64bd60ceb5b89918200e11e3fbff67370))
* issues/192254729 ([#915](https://www.github.com/googleapis/python-aiplatform/issues/915)) ([0f22ff6](https://www.github.com/googleapis/python-aiplatform/commit/0f22ff61460a3f2bd55d2c10c4ee06e582f03944))
* use open_in_new_tab in the render method. ([#926](https://www.github.com/googleapis/python-aiplatform/issues/926)) ([04618e0](https://www.github.com/googleapis/python-aiplatform/commit/04618e0563b8588eec2ccd8342c6085ca08b5adb))

## [1.8.1](https://www.github.com/googleapis/python-aiplatform/compare/v1.8.0...v1.8.1) (2021-12-14)


### Bug Fixes

* add clarity to param model_name ([#888](https://www.github.com/googleapis/python-aiplatform/issues/888)) ([1d81783](https://www.github.com/googleapis/python-aiplatform/commit/1d81783b2f914dd7606ee884ca31c1a594e5135f))
* add clarity to parameters per user feedback ([#886](https://www.github.com/googleapis/python-aiplatform/issues/886)) ([37ee0a1](https://www.github.com/googleapis/python-aiplatform/commit/37ee0a1dc6e0105e19aca18f44995a352bfc40cb))
* add param for multi-label per user's feedback ([#887](https://www.github.com/googleapis/python-aiplatform/issues/887)) ([fda942f](https://www.github.com/googleapis/python-aiplatform/commit/fda942ffbe009077b47f36aad1c29603a451e38b))
* add support for API base path overriding ([#908](https://www.github.com/googleapis/python-aiplatform/issues/908)) ([45c4086](https://www.github.com/googleapis/python-aiplatform/commit/45c4086dd07dd7d3d3b7417196ff61a7107d8a1a))
* Important the correct constants and use v1 for tensorboard experiments ([#905](https://www.github.com/googleapis/python-aiplatform/issues/905)) ([48c2bf1](https://www.github.com/googleapis/python-aiplatform/commit/48c2bf1ea2fa42afea1b5d419527bfb8e49e0ac0))
* incorrect uri for IOD yaml ([#889](https://www.github.com/googleapis/python-aiplatform/issues/889)) ([e108ef8](https://www.github.com/googleapis/python-aiplatform/commit/e108ef8250c77c8a8edeccb6b601cbe0b0380c89))
* Minor docstring and snippet fixes ([#873](https://www.github.com/googleapis/python-aiplatform/issues/873)) ([578e06d](https://www.github.com/googleapis/python-aiplatform/commit/578e06df481c3d60074a7b8e9365f8361b04e32b))


### Documentation

* Update references to containers and notebook samples. ([#890](https://www.github.com/googleapis/python-aiplatform/issues/890)) ([67fa1f1](https://www.github.com/googleapis/python-aiplatform/commit/67fa1f179af66686339d797e5b368e96816ed1c5))
* Updated docstrings with exception error classes ([#894](https://www.github.com/googleapis/python-aiplatform/issues/894)) ([f9aecd2](https://www.github.com/googleapis/python-aiplatform/commit/f9aecd22fe08a97e45187b4d11c755ac3b9dfadd))

## [1.8.0](https://www.github.com/googleapis/python-aiplatform/compare/v1.7.1...v1.8.0) (2021-12-03)


### Features

* Add cloud profiler to training_utils ([6d5c7c4](https://www.github.com/googleapis/python-aiplatform/commit/6d5c7c42d1c352f161e4738c6dbbf540a032017b))
* add enable_private_service_connect field to Endpoint feat: add id field to DeployedModel feat: add service_attachment field to PrivateEndpoints feat: add endpoint_id to CreateEndpointRequest and method signature to CreateEndpoint feat: add method... ([#878](https://www.github.com/googleapis/python-aiplatform/issues/878)) ([ca813be](https://www.github.com/googleapis/python-aiplatform/commit/ca813be08ec2620380b5a12b0d6cdc079e27ba79))
* add enable_private_service_connect field to Endpoint feat: add id field to DeployedModel feat: add service_attachment field to PrivateEndpoints feat: add endpoint_id to CreateEndpointRequest and method signature to CreateEndpoint feat: add method... ([#879](https://www.github.com/googleapis/python-aiplatform/issues/879)) ([47e93b2](https://www.github.com/googleapis/python-aiplatform/commit/47e93b20843f30805b73cd6db214c8743f8bfc97))
* add featurestore module including Featurestore, EntityType, and Feature classes; add get, update, delete, list methods in all featurestore classes; add search method in Feature class ([#850](https://www.github.com/googleapis/python-aiplatform/issues/850)) ([66745a6](https://www.github.com/googleapis/python-aiplatform/commit/66745a6ce13fb8b32dd7fbf3eb86e71bd291869b))
* Add prediction container URI builder method ([#805](https://www.github.com/googleapis/python-aiplatform/issues/805)) ([91dd3c0](https://www.github.com/googleapis/python-aiplatform/commit/91dd3c0d5de72fac5b1dc8a9bc23d6cb431061a4))
* default to custom job display name if experiment name looks like a custom job ID ([#833](https://www.github.com/googleapis/python-aiplatform/issues/833)) ([8b9376e](https://www.github.com/googleapis/python-aiplatform/commit/8b9376e9c961a751799f5b80d1b19917c8c353f8))
* Support uploading local models ([#779](https://www.github.com/googleapis/python-aiplatform/issues/779)) ([bffbd9d](https://www.github.com/googleapis/python-aiplatform/commit/bffbd9d359edb099e661736a0c77269bb3a0c746))
* Tensorboard v1 protos release ([#847](https://www.github.com/googleapis/python-aiplatform/issues/847)) ([e0fc3d9](https://www.github.com/googleapis/python-aiplatform/commit/e0fc3d9e4e8a7911f21671ea49818c5f84798d12))
* updating Tensorboard related code to use v1 ([#851](https://www.github.com/googleapis/python-aiplatform/issues/851)) ([b613b26](https://www.github.com/googleapis/python-aiplatform/commit/b613b264524aaab2cb65e63a5487770736faa7c8))
* Upgrade Tensorboard from v1beta1 to v1 ([#849](https://www.github.com/googleapis/python-aiplatform/issues/849)) ([c40ec85](https://www.github.com/googleapis/python-aiplatform/commit/c40ec85e1fca2bee6813f52712d063f96264ec2c))


### Bug Fixes

* Import error for cloud_profiler ([#869](https://www.github.com/googleapis/python-aiplatform/issues/869)) ([0f124e9](https://www.github.com/googleapis/python-aiplatform/commit/0f124e93a1ddead16c0018970f34e45c73d5ed81))
* Support multiple instances in custom predict sample ([#857](https://www.github.com/googleapis/python-aiplatform/issues/857)) ([8cb4839](https://www.github.com/googleapis/python-aiplatform/commit/8cb483918bdbaeae34935eef2b3cd997c1ae89a3))


### Documentation

* Added comment for evaluation_id to python examples ([#860](https://www.github.com/googleapis/python-aiplatform/issues/860)) ([004bf5f](https://www.github.com/googleapis/python-aiplatform/commit/004bf5fa4cb2d66e36de7ec52dee8e2c8dd438ee))
* Reverted IDs in model_service snippets test ([#871](https://www.github.com/googleapis/python-aiplatform/issues/871)) ([da747b5](https://www.github.com/googleapis/python-aiplatform/commit/da747b5ffca3c12b8d64bc80bfe93da5afde0d43))
* Update name of BQ source parameter in samples ([#859](https://www.github.com/googleapis/python-aiplatform/issues/859)) ([f11b598](https://www.github.com/googleapis/python-aiplatform/commit/f11b598f9069f77e86631ada53941876aea010bc))

## [1.7.1](https://www.github.com/googleapis/python-aiplatform/compare/v1.7.0...v1.7.1) (2021-11-16)


### Features

* Add support for new Vertex regions ([#811](https://www.github.com/googleapis/python-aiplatform/issues/811)) ([8d04138](https://www.github.com/googleapis/python-aiplatform/commit/8d0413880486d03314ecab80347a713318c6944a))


### Bug Fixes

* add parameters_value in PipelineJob for schema > 2.0.0 ([#817](https://www.github.com/googleapis/python-aiplatform/issues/817)) ([900a449](https://www.github.com/googleapis/python-aiplatform/commit/900a44962ac85608dbcb3d23049db160d49d842a))
* exclude support for python 3.10 ([#831](https://www.github.com/googleapis/python-aiplatform/issues/831)) ([0301a1d](https://www.github.com/googleapis/python-aiplatform/commit/0301a1de5719031c6c826fe4887ff5fb6bcfa956))


### Miscellaneous Chores

* release 1.7.1 ([#845](https://www.github.com/googleapis/python-aiplatform/issues/845)) ([ca04de6](https://www.github.com/googleapis/python-aiplatform/commit/ca04de6a95f8b22d0161e250d8d4314a35becfab))

## [1.7.0](https://www.github.com/googleapis/python-aiplatform/compare/v1.6.2...v1.7.0) (2021-11-06)


### Features

* Adds support for `google.protobuf.Value` pipeline parameters in the `parameter_values` field ([#807](https://www.github.com/googleapis/python-aiplatform/issues/807)) ([c97199d](https://www.github.com/googleapis/python-aiplatform/commit/c97199dd2cb712ef436ee9cbf6b8add27b42b174))
* Adds support for `google.protobuf.Value` pipeline parameters in the `parameter_values` field ([#808](https://www.github.com/googleapis/python-aiplatform/issues/808)) ([726b620](https://www.github.com/googleapis/python-aiplatform/commit/726b620bea1223c80225c9a3c2b54342e9c14052))
* PipelineJob switch to v1 API from v1beta1 API ([#750](https://www.github.com/googleapis/python-aiplatform/issues/750)) ([8db7e0c](https://www.github.com/googleapis/python-aiplatform/commit/8db7e0ca4e796fea47c1bdf4c0fccd514f2dd8c2))


### Bug Fixes

* Correct PipelineJob credentials description ([#816](https://www.github.com/googleapis/python-aiplatform/issues/816)) ([49aaa87](https://www.github.com/googleapis/python-aiplatform/commit/49aaa8719a3daabf7e0d23fa1cd1d64c19159a83))
* Fixed docstrings for Dataset in AutoMLForecastingTrainingJob ([760887b](https://www.github.com/googleapis/python-aiplatform/commit/760887b196884707473896def9e8b69c9fc77423))


### Documentation

* Fix pydocs README to be consistent with repo README ([#821](https://www.github.com/googleapis/python-aiplatform/issues/821)) ([95dbd60](https://www.github.com/googleapis/python-aiplatform/commit/95dbd6020ee8f3037b0834eb39312b5d7e5fd8e1))
* Update sample with feedback from b/191251050 ([#818](https://www.github.com/googleapis/python-aiplatform/issues/818)) ([6b2d938](https://www.github.com/googleapis/python-aiplatform/commit/6b2d93834734b6789c13ef3782b1b3632f5c6133))

## [1.6.2](https://www.github.com/googleapis/python-aiplatform/compare/v1.6.1...v1.6.2) (2021-11-01)


### Features

* Add PipelineJob.submit to create PipelineJob without monitoring it's completion. ([#798](https://www.github.com/googleapis/python-aiplatform/issues/798)) ([7ab05d5](https://www.github.com/googleapis/python-aiplatform/commit/7ab05d5e127636d96365b7ea408974ccd6c2f0fe))
* support new protobuf value param types for Pipeline Job client ([#797](https://www.github.com/googleapis/python-aiplatform/issues/797)) ([2fc05ca](https://www.github.com/googleapis/python-aiplatform/commit/2fc05cab03a2c7f8462b234b02d43bc7581ba845))


### Bug Fixes

* Add retries when polling during monitoring runs ([#786](https://www.github.com/googleapis/python-aiplatform/issues/786)) ([45401c0](https://www.github.com/googleapis/python-aiplatform/commit/45401c09f23ed616a7ca84b3d7f53b8a1db21c7c))
* use version.py for versioning ([#804](https://www.github.com/googleapis/python-aiplatform/issues/804)) ([514031f](https://www.github.com/googleapis/python-aiplatform/commit/514031fce90b6e4606279d4903dc93b0f18b9f2a))
* Widen system test timeout, handle tearing down failed training pipelines ([#791](https://www.github.com/googleapis/python-aiplatform/issues/791)) ([78879e2](https://www.github.com/googleapis/python-aiplatform/commit/78879e2482cac7ef5520f1d7fe900768147b948e))


### Miscellaneous Chores

* release 1.6.2 ([#809](https://www.github.com/googleapis/python-aiplatform/issues/809)) ([e50b049](https://www.github.com/googleapis/python-aiplatform/commit/e50b0497574411a9c7462d76dca489281ee48d83))

## [1.6.1](https://www.github.com/googleapis/python-aiplatform/compare/v1.6.0...v1.6.1) (2021-10-25)


### Features

* Add debugging terminal support for CustomJob, HyperparameterTun… ([#699](https://www.github.com/googleapis/python-aiplatform/issues/699)) ([2deb505](https://www.github.com/googleapis/python-aiplatform/commit/2deb50502ae2bb8ba3f97d69b06b72b7625639a4))
* add support for python 3.10 ([#769](https://www.github.com/googleapis/python-aiplatform/issues/769)) ([8344804](https://www.github.com/googleapis/python-aiplatform/commit/83448044508f5feb052ae7fc5a5a7ca917cee0d1))
* Add training_utils folder and environment_variables for training ([141c008](https://www.github.com/googleapis/python-aiplatform/commit/141c008759aefe56a41e1eac654739c509d9754d))
* enable reduction server ([#741](https://www.github.com/googleapis/python-aiplatform/issues/741)) ([8ef0ded](https://www.github.com/googleapis/python-aiplatform/commit/8ef0ded034db797adb4d458eba43537992d822bd))
* enabling AutoML Forecasting training response to include BigQuery location of exported evaluated examples  ([#657](https://www.github.com/googleapis/python-aiplatform/issues/657)) ([c1c2326](https://www.github.com/googleapis/python-aiplatform/commit/c1c2326b2342ab1b6f4c4ce3852e63376eae740d))
* **PipelineJob:** allow PipelineSpec as param ([#774](https://www.github.com/googleapis/python-aiplatform/issues/774)) ([f90a1bd](https://www.github.com/googleapis/python-aiplatform/commit/f90a1bd775daa0892e16fd82fc1738fa9a912ec7))
* pre batch creating TensorboardRuns and TensorboardTimeSeries in one_shot mode to speed up uploading ([#772](https://www.github.com/googleapis/python-aiplatform/issues/772)) ([c9f68c6](https://www.github.com/googleapis/python-aiplatform/commit/c9f68c6e840ba3cda04080623dfbcba6945d53e8))


### Bug Fixes

* cast resource labels to dict type ([#783](https://www.github.com/googleapis/python-aiplatform/issues/783)) ([255edc9](https://www.github.com/googleapis/python-aiplatform/commit/255edc92dc897619ddd705463aefb8a1723ae8cd))
* Remove sync parameter from create_endpoint_sample ([#695](https://www.github.com/googleapis/python-aiplatform/issues/695)) ([0477f5a](https://www.github.com/googleapis/python-aiplatform/commit/0477f5a10ba1048e64c11fc3d7e1e375b19a10fe))


### Miscellaneous Chores

* release 1.6.1 ([#789](https://www.github.com/googleapis/python-aiplatform/issues/789)) ([4520d35](https://www.github.com/googleapis/python-aiplatform/commit/4520d350beb756549304de60d62ff637bb1807c5))

## [1.6.0](https://www.github.com/googleapis/python-aiplatform/compare/v1.5.0...v1.6.0) (2021-10-12)


### Features

* add featurestore service to aiplatform v1  ([#765](https://www.github.com/googleapis/python-aiplatform/issues/765)) ([68c88e4](https://www.github.com/googleapis/python-aiplatform/commit/68c88e48f62d5c2ff561862ba810a48389f7e41a))
* Add one shot profile uploads to tensorboard uploader. ([#704](https://www.github.com/googleapis/python-aiplatform/issues/704)) ([a83f253](https://www.github.com/googleapis/python-aiplatform/commit/a83f2535b31e2aaff0306c7290265b864b9ddb40))
* Added column_specs, training_encryption_spec_key_name, model_encryption_spec_key_name to AutoMLForecastingTrainingJob.init and various split methods to AutoMLForecastingTrainingJob.run ([#647](https://www.github.com/googleapis/python-aiplatform/issues/647)) ([7cb6976](https://www.github.com/googleapis/python-aiplatform/commit/7cb69764e0f9be9ca0fcb1641f4dc90e3b306bed))
* Lazy load Endpoint class ([#655](https://www.github.com/googleapis/python-aiplatform/issues/655)) ([c795c6f](https://www.github.com/googleapis/python-aiplatform/commit/c795c6fbb87c4f71845cfbd2647c1adbc029bcef))

## [1.5.0](https://www.github.com/googleapis/python-aiplatform/compare/v1.4.3...v1.5.0) (2021-09-30)


### Features

* Add data plane code snippets for feature store service ([#713](https://www.github.com/googleapis/python-aiplatform/issues/713)) ([e3ea683](https://www.github.com/googleapis/python-aiplatform/commit/e3ea683bf754832340853a15bdb0a0662500a70f))
* add flaky test diagnostic script ([#734](https://www.github.com/googleapis/python-aiplatform/issues/734)) ([09e48de](https://www.github.com/googleapis/python-aiplatform/commit/09e48de8b79fb5d601169663c9a8e1c33883f1cf))
* add vizier service to aiplatform v1 BUILD.bazel ([#731](https://www.github.com/googleapis/python-aiplatform/issues/731)) ([1a580ae](https://www.github.com/googleapis/python-aiplatform/commit/1a580aec158b5e25b94f27a6a9daa3943124c485))
* code snippets for feature store control plane ([#709](https://www.github.com/googleapis/python-aiplatform/issues/709)) ([8e06ced](https://www.github.com/googleapis/python-aiplatform/commit/8e06ced83ed2cc480d869318c4debef9c28ad214))
* Updating the Tensorboard uploader to use the new batch write API so it runs more efficiently ([#710](https://www.github.com/googleapis/python-aiplatform/issues/710)) ([9d1b01a](https://www.github.com/googleapis/python-aiplatform/commit/9d1b01a91dc077bfe8edf023216b65b826d67d5f))


### Bug Fixes

* [#677](https://www.github.com/googleapis/python-aiplatform/issues/677) ([#728](https://www.github.com/googleapis/python-aiplatform/issues/728)) ([7f548e4](https://www.github.com/googleapis/python-aiplatform/commit/7f548e4b5322055a3c2befcdc9d4eef1bc2278ca))
* **PipelineJob:** use name as output only field ([#719](https://www.github.com/googleapis/python-aiplatform/issues/719)) ([1c84464](https://www.github.com/googleapis/python-aiplatform/commit/1c84464e3130f9db81cd341306b334f9a490587f))
* use the project id from BQ dataset instead of the default project id ([#717](https://www.github.com/googleapis/python-aiplatform/issues/717)) ([e87a255](https://www.github.com/googleapis/python-aiplatform/commit/e87a255705a5d04ade79f12c706dc842c0228118))

## [1.4.3](https://www.github.com/googleapis/python-aiplatform/compare/v1.4.2...v1.4.3) (2021-09-17)


### Features

* **PipelineJob:** support dict, list, bool typed input parameters fr… ([#693](https://www.github.com/googleapis/python-aiplatform/issues/693)) ([243b75c](https://www.github.com/googleapis/python-aiplatform/commit/243b75c2655beeef47848410a40d86a072428ac3))


### Bug Fixes

* Update milli node_hours for image training ([#663](https://www.github.com/googleapis/python-aiplatform/issues/663)) ([64768c3](https://www.github.com/googleapis/python-aiplatform/commit/64768c3591f648932e023713d2a728ce5318bb8b))
* XAI Metadata compatibility with Model.upload ([#705](https://www.github.com/googleapis/python-aiplatform/issues/705)) ([f0570cb](https://www.github.com/googleapis/python-aiplatform/commit/f0570cb999f024ca96e7daaa102c81b681c2a575))


### Miscellaneous Chores

* release 1.4.3 ([#715](https://www.github.com/googleapis/python-aiplatform/issues/715)) ([b610486](https://www.github.com/googleapis/python-aiplatform/commit/b6104868161a236fc5585855b5948a5e3294aea2))

## [1.4.2](https://www.github.com/googleapis/python-aiplatform/compare/v1.4.1...v1.4.2) (2021-09-10)


### Features

* add explanation metadata `get_metadata_protobuf` for reuse ([#672](https://www.github.com/googleapis/python-aiplatform/issues/672)) ([efb6d18](https://www.github.com/googleapis/python-aiplatform/commit/efb6d18f868086bc53aceab60942eb837ced65b7))


## [1.4.1](https://www.github.com/googleapis/python-aiplatform/compare/v1.4.0...v1.4.1) (2021-09-07)


### Features

* add prediction service RPC RawPredict to aiplatform_v1beta1 feat: add tensorboard service RPCs to aiplatform_v1beta1: BatchCreateTensorboardRuns, BatchCreateTensorboardTimeSeries, WriteTensorboardExperimentData feat: add model_deployment_monitori... ([#670](https://www.github.com/googleapis/python-aiplatform/issues/670)) ([b73cd94](https://www.github.com/googleapis/python-aiplatform/commit/b73cd9485f8713ac42e7efa9bfd952f67368b778))
* add Vizier service to aiplatform v1 ([#671](https://www.github.com/googleapis/python-aiplatform/issues/671)) ([179150a](https://www.github.com/googleapis/python-aiplatform/commit/179150aed80d1386993a07870fe34f2b637ded18))
* add XAI, model monitoring, and index services to aiplatform v1 ([#668](https://www.github.com/googleapis/python-aiplatform/issues/668)) ([1fbce55](https://www.github.com/googleapis/python-aiplatform/commit/1fbce55fd846f473f41c16c1185be893e2376bdd))
* Update tensorboard uploader to use Dispatcher for handling different event types ([#651](https://www.github.com/googleapis/python-aiplatform/issues/651)) ([d20b520](https://www.github.com/googleapis/python-aiplatform/commit/d20b520ea936a6554a24099beb0e044f237ff741)), closes [#519](https://www.github.com/googleapis/python-aiplatform/issues/519)


### Documentation

* Add code sample for Pipelines ([#684](https://www.github.com/googleapis/python-aiplatform/issues/684)) ([4f0c18e](https://www.github.com/googleapis/python-aiplatform/commit/4f0c18e8989cf353019876a73aa57457332e88fb))

## [1.4.0](https://www.github.com/googleapis/python-aiplatform/compare/v1.3.0...v1.4.0) (2021-08-30)


### Features

* add filter and timestamp splits  ([#627](https://www.github.com/googleapis/python-aiplatform/issues/627)) ([1a13577](https://www.github.com/googleapis/python-aiplatform/commit/1a135775966c8a2303ded529eba514dcf9db7205))
* add labels to all resource creation apis ([#601](https://www.github.com/googleapis/python-aiplatform/issues/601)) ([4e7666a](https://www.github.com/googleapis/python-aiplatform/commit/4e7666a30b4472698ed980d9d746ba85ad4142d8))
* add PipelineJob.list ([a58ea82](https://www.github.com/googleapis/python-aiplatform/commit/a58ea826c575b9b0c8cb69e47fc2f07a98bb285b))
* add support for export_evaluated_data_items_config in AutoMLTab… ([#583](https://www.github.com/googleapis/python-aiplatform/issues/583)) ([2a6b0a3](https://www.github.com/googleapis/python-aiplatform/commit/2a6b0a369296698f79d75e93007e4c7319f3523c))
* add util functions to get URLs for Tensorboard web app. ([#635](https://www.github.com/googleapis/python-aiplatform/issues/635)) ([8d88c00](https://www.github.com/googleapis/python-aiplatform/commit/8d88c006c5586b28d340448382a9292543448fd6))
* Add wait_for_resource_creation to BatchPredictionJob and unblock async creation when model is pending creation. ([#660](https://www.github.com/googleapis/python-aiplatform/issues/660)) ([db580ad](https://www.github.com/googleapis/python-aiplatform/commit/db580ad43e97e0d877c29c0e8c077c37dee33ff3))
* Added the VertexAiResourceNoun.to_dict() method ([#588](https://www.github.com/googleapis/python-aiplatform/issues/588)) ([b478075](https://www.github.com/googleapis/python-aiplatform/commit/b478075efb05553760514256fee9a63126a9916f))
* expose base_output_dir for custom job ([#586](https://www.github.com/googleapis/python-aiplatform/issues/586)) ([2f138d1](https://www.github.com/googleapis/python-aiplatform/commit/2f138d1dfe4959d1b5f53a9dfef90a18de9908ec))
* expose boot disk type and size for CustomTrainingJob, CustomPythonPackageTrainingJob, and CustomContainerTrainingJob ([#602](https://www.github.com/googleapis/python-aiplatform/issues/602)) ([355ea24](https://www.github.com/googleapis/python-aiplatform/commit/355ea24c6dd9b061ae0933df4dd07dd5b8c2232b))
* split GAPIC samples by service ([#599](https://www.github.com/googleapis/python-aiplatform/issues/599)) ([5f15b4f](https://www.github.com/googleapis/python-aiplatform/commit/5f15b4f9a4bad2c9447747a8bdebaa99eab00b75))


### Bug Fixes

* Fixed bug in TabularDataset.column_names ([#590](https://www.github.com/googleapis/python-aiplatform/issues/590)) ([0fbcd59](https://www.github.com/googleapis/python-aiplatform/commit/0fbcd592cd7e9c4b0a131d777fa84e592a43a21c))
* pipeline none values ([#649](https://www.github.com/googleapis/python-aiplatform/issues/649)) ([2f89343](https://www.github.com/googleapis/python-aiplatform/commit/2f89343adbd69610fc5cacc7121119fc7279186e))
* Populate service_account and network in PipelineJob instead of pipeline_spec ([#658](https://www.github.com/googleapis/python-aiplatform/issues/658)) ([8fde2ce](https://www.github.com/googleapis/python-aiplatform/commit/8fde2ce4441139784bc0fdd62c88d4b833018765))
* re-remove extra TB dependencies introduced due to merge conflict ([#593](https://www.github.com/googleapis/python-aiplatform/issues/593)) ([433b94a](https://www.github.com/googleapis/python-aiplatform/commit/433b94a78004de6d3a4726317d8bac32c358ace8))
* Update BatchPredictionJob.iter_outputs() and BQ docstrings ([#631](https://www.github.com/googleapis/python-aiplatform/issues/631)) ([28f32fd](https://www.github.com/googleapis/python-aiplatform/commit/28f32fd11470ad86d2f103346b3e6be8f1adc2d8))

## [1.3.0](https://www.github.com/googleapis/python-aiplatform/compare/v1.2.0...v1.3.0) (2021-07-30)


### Features

* add get method for PipelineJob ([#561](https://www.github.com/googleapis/python-aiplatform/issues/561)) ([fe5e6e4](https://www.github.com/googleapis/python-aiplatform/commit/fe5e6e4576a6c8c73549effae99bced709e29402))
* add Samples section to CONTRIBUTING.rst ([#558](https://www.github.com/googleapis/python-aiplatform/issues/558)) ([d35c466](https://www.github.com/googleapis/python-aiplatform/commit/d35c466e19ac9fa43b5668ce18520090b5e4edd9))
* add tensorboard resource management ([#539](https://www.github.com/googleapis/python-aiplatform/issues/539)) ([6f8d3d1](https://www.github.com/googleapis/python-aiplatform/commit/6f8d3d1ed89f0aa6f2f0418ae752185104196c63))
* add tf1 metadata builder ([#526](https://www.github.com/googleapis/python-aiplatform/issues/526)) ([918998c](https://www.github.com/googleapis/python-aiplatform/commit/918998c0bdc25b6a39d359a34f892dac1ca4efac))
* add wait for creation and more informative exception when properties are not available ([#566](https://www.github.com/googleapis/python-aiplatform/issues/566)) ([e346117](https://www.github.com/googleapis/python-aiplatform/commit/e346117d5453358a32a1d6e584613ace5c2251d9))
* Adds a new API method FindMostStableBuild ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds attribution_score_drift_threshold field ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds attribution_score_skew_thresholds field ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds BigQuery output table field to batch prediction job output config ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds CustomJob.enable_web_access field ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds CustomJob.web_access_uris field ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds Endpoint.network, Endpoint.private_endpoints fields and PrivateEndpoints message ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds Execution.State constants: CACHED and CANCELLED ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds Feature Store features ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds fields to Study message ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds IndexEndpoint.private_ip_ranges field ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds IndexEndpointService.deployed_index_id field ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds MetadataService.DeleteArtifact and DeleteExecution methods ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds ModelMonitoringObjectConfig.explanation_config field ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* Adds ModelMonitoringObjectConfig.ExplanationConfig message field ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))
* column specs for tabular transformation ([#466](https://www.github.com/googleapis/python-aiplatform/issues/466)) ([71d0bd4](https://www.github.com/googleapis/python-aiplatform/commit/71d0bd4615b436eaa3ec3eade4445934552f1cb3))
* enable_caching in PipelineJob to compile time settings ([#557](https://www.github.com/googleapis/python-aiplatform/issues/557)) ([c9da662](https://www.github.com/googleapis/python-aiplatform/commit/c9da662ec24709622bcc4a9e85d1938bead91923))
* Removes breaking change from v1 version of AI Platform protos ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))


### Bug Fixes

* change default replica count to 1 for custom training job classes ([#579](https://www.github.com/googleapis/python-aiplatform/issues/579)) ([c24251f](https://www.github.com/googleapis/python-aiplatform/commit/c24251fdd230e73c2aadb4369266b78979a31015))
* create pipeline job with user-specified job id ([#567](https://www.github.com/googleapis/python-aiplatform/issues/567)) ([df68ec3](https://www.github.com/googleapis/python-aiplatform/commit/df68ec3441eeb7670531f50aaed00df6f7e2a1a3))
* **deps:** pin 'google-{api,cloud}-core', 'google-auth' to allow 2.x versions ([#556](https://www.github.com/googleapis/python-aiplatform/issues/556)) ([5d79795](https://www.github.com/googleapis/python-aiplatform/commit/5d797956737f2d0d4afa4d28fe1fa2f835992991))
* enable self signed jwt for grpc ([#570](https://www.github.com/googleapis/python-aiplatform/issues/570)) ([6a99b12](https://www.github.com/googleapis/python-aiplatform/commit/6a99b125922b8fca7c997150b81b6925376e9d1d))


### Documentation

* fix spelling ([#565](https://www.github.com/googleapis/python-aiplatform/issues/565)) ([fe5c702](https://www.github.com/googleapis/python-aiplatform/commit/fe5c7020040fb0b3b558643b8bc3e12e76f4055f))

## [1.2.0](https://www.github.com/googleapis/python-aiplatform/compare/v1.1.1...v1.2.0) (2021-07-14)


### Features

* Add additional_experiments field to AutoMlTablesInputs ([#540](https://www.github.com/googleapis/python-aiplatform/issues/540)) ([96ee726](https://www.github.com/googleapis/python-aiplatform/commit/96ee7261d5c3ffac5598c618b7c7499fad34ab12))
* add always_use_jwt_access ([#498](https://www.github.com/googleapis/python-aiplatform/issues/498)) ([6df4866](https://www.github.com/googleapis/python-aiplatform/commit/6df48663286db10b1b88f947fc5873a18084cf37))
* add explain get_metadata function for tf2.  ([#507](https://www.github.com/googleapis/python-aiplatform/issues/507)) ([f6f9a97](https://www.github.com/googleapis/python-aiplatform/commit/f6f9a97bb178d9859b8d43166a43792d88e57710))
* Add structure for XAI explain (from XAI SDK) ([#502](https://www.github.com/googleapis/python-aiplatform/issues/502)) ([cb9ef11](https://www.github.com/googleapis/python-aiplatform/commit/cb9ef1115e58c230f3d009397a6e6a27fd376bed))
* Add two new ModelType constants for Video Action Recognition training jobs ([96ee726](https://www.github.com/googleapis/python-aiplatform/commit/96ee7261d5c3ffac5598c618b7c7499fad34ab12))
* Adds AcceleratorType.NVIDIA_TESLA_A100 constant ([f3a3d03](https://www.github.com/googleapis/python-aiplatform/commit/f3a3d03c8509dc49c24139155a572dacbe954f66))
* Adds additional_experiments field to AutoMlForecastingInputs ([8077b3d](https://www.github.com/googleapis/python-aiplatform/commit/8077b3d728b6e168c8aad41291dd90144ab75633))
* Adds additional_experiments field to AutoMlTablesInputs ([#544](https://www.github.com/googleapis/python-aiplatform/issues/544)) ([8077b3d](https://www.github.com/googleapis/python-aiplatform/commit/8077b3d728b6e168c8aad41291dd90144ab75633))
* Adds AutoscalingMetricSpec message ([f3a3d03](https://www.github.com/googleapis/python-aiplatform/commit/f3a3d03c8509dc49c24139155a572dacbe954f66))
* Adds BigQuery output table field to batch prediction job output config ([f3a3d03](https://www.github.com/googleapis/python-aiplatform/commit/f3a3d03c8509dc49c24139155a572dacbe954f66))
* Adds fields to Study message ([f3a3d03](https://www.github.com/googleapis/python-aiplatform/commit/f3a3d03c8509dc49c24139155a572dacbe954f66))
* Adds JobState.JOB_STATE_EXPIRED constant ([f3a3d03](https://www.github.com/googleapis/python-aiplatform/commit/f3a3d03c8509dc49c24139155a572dacbe954f66))
* Adds PipelineService methods for Create, Get, List, Delete, Cancel ([f3a3d03](https://www.github.com/googleapis/python-aiplatform/commit/f3a3d03c8509dc49c24139155a572dacbe954f66))
* Adds two new ModelType constants for Video Action Recognition training jobs ([8077b3d](https://www.github.com/googleapis/python-aiplatform/commit/8077b3d728b6e168c8aad41291dd90144ab75633))
* Removes AcceleratorType.TPU_V2 and TPU_V3 constants ([#543](https://www.github.com/googleapis/python-aiplatform/issues/543)) ([f3a3d03](https://www.github.com/googleapis/python-aiplatform/commit/f3a3d03c8509dc49c24139155a572dacbe954f66))


### Bug Fixes

* Handle nested fields from BigQuery source when getting default column_names ([#522](https://www.github.com/googleapis/python-aiplatform/issues/522)) ([3fc1d44](https://www.github.com/googleapis/python-aiplatform/commit/3fc1d44ac0acbb4f58088e7eeb16d85818af1125))
* log pipeline completion and raise pipeline failures ([#523](https://www.github.com/googleapis/python-aiplatform/issues/523)) ([2508fe9](https://www.github.com/googleapis/python-aiplatform/commit/2508fe9d8a75ac8b05f06a78589c657313bd1d3d))
* making the uploader depend on tensorflow-proper ([#499](https://www.github.com/googleapis/python-aiplatform/issues/499)) ([b95e040](https://www.github.com/googleapis/python-aiplatform/commit/b95e0406566879e8f71cefda72b41dc6fe4e578f))
* Set prediction client when listing Endpoints ([#512](https://www.github.com/googleapis/python-aiplatform/issues/512)) ([95639ee](https://www.github.com/googleapis/python-aiplatform/commit/95639ee1c2c9cb66624265383d4d27bed3ff7dbd))

## [1.1.1](https://www.github.com/googleapis/python-aiplatform/compare/v1.1.0...v1.1.1) (2021-06-22)


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

## [1.0.1](https://www.github.com/googleapis/python-aiplatform/compare/v1.0.0...v1.0.1) (2021-05-21)


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

## [0.7.1](https://www.github.com/googleapis/python-aiplatform/compare/v0.7.0...v0.7.1) (2021-04-14)


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

## [0.5.1](https://www.github.com/googleapis/python-aiplatform/compare/v0.5.0...v0.5.1) (2021-03-01)


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

## [0.3.1](https://www.github.com/googleapis/python-aiplatform/compare/v0.3.0...v0.3.1) (2020-11-13)


### Features

* add samples ([#56](https://www.github.com/googleapis/python-aiplatform/issues/56)) ([53cc5f5](https://www.github.com/googleapis/python-aiplatform/commit/53cc5f51bf3845fe688ee7b7a0494ff42c549f69))

## 0.3.0 (2020-11-05)


### Features

* generate v1beta1 ([e80a4fc](https://www.github.com/googleapis/python-aiplatform/commit/e80a4fcbdc84bdd76b159520c93943ada88c7210))
* python-aiplatform beta library ([#39](https://www.github.com/googleapis/python-aiplatform/issues/39)) ([81366dc](https://www.github.com/googleapis/python-aiplatform/commit/81366dcec173ed1e63b17e242c1ef74f623dd31b))
* regenerate v1beta1 ([#4](https://www.github.com/googleapis/python-aiplatform/issues/4)) ([4ddc426](https://www.github.com/googleapis/python-aiplatform/commit/4ddc426a6b4b8cd319fa885e363c94b35ef777d9))


### Bug Fixes

* re-add py sessions to noxfile ([#22](https://www.github.com/googleapis/python-aiplatform/issues/22)) ([3c713d5](https://www.github.com/googleapis/python-aiplatform/commit/3c713d5cf47bf343bf53583296daed6161d4f4ed))
