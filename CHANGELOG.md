# Changelog

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
