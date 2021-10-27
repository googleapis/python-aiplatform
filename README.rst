Vertex SDK for Python
=================================================

|GA| |pypi| |versions| |unit-tests| |system-tests| |sample-tests|


`Vertex AI`_: Google Vertex AI is an integrated suite of machine learning tools and services for building and using ML models with AutoML or custom code. It offers both novices and experts the best workbench for the entire machine learning development lifecycle.

- `Client Library Documentation`_
- `Product Documentation`_

.. |GA| image:: https://img.shields.io/badge/support-ga-gold.svg
   :target: https://github.com/googleapis/google-cloud-python/blob/main/README.rst#general-availability
.. |pypi| image:: https://img.shields.io/pypi/v/google-cloud-aiplatform.svg
   :target: https://pypi.org/project/google-cloud-aiplatform/
.. |versions| image:: https://img.shields.io/pypi/pyversions/google-cloud-aiplatform.svg
   :target: https://pypi.org/project/google-cloud-aiplatform/
.. |unit-tests| image:: https://storage.googleapis.com/cloud-devrel-public/python-aiplatform/badges/sdk-unit-tests.svg
   :target: https://storage.googleapis.com/cloud-devrel-public/python-aiplatform/badges/sdk-unit-tests.html
.. |system-tests| image:: https://storage.googleapis.com/cloud-devrel-public/python-aiplatform/badges/sdk-system-tests.svg
   :target: https://storage.googleapis.com/cloud-devrel-public/python-aiplatform/badges/sdk-system-tests.html
.. |sample-tests| image:: https://storage.googleapis.com/cloud-devrel-public/python-aiplatform/badges/sdk-sample-tests.svg
   :target: https://storage.googleapis.com/cloud-devrel-public/python-aiplatform/badges/sdk-sample-tests.html
.. _Vertex AI: https://cloud.google.com/vertex-ai/docs
.. _Client Library Documentation: https://googleapis.dev/python/aiplatform/latest
.. _Product Documentation:  https://cloud.google.com/vertex-ai/docs

Quick Start
-----------

In order to use this library, you first need to go through the following steps:

1. `Select or create a Cloud Platform project.`_
2. `Enable billing for your project.`_
3. `Enable the Vertex AI API.`_
4. `Setup Authentication.`_

.. _Select or create a Cloud Platform project.: https://console.cloud.google.com/project
.. _Enable billing for your project.: https://cloud.google.com/billing/docs/how-to/modify-project#enable_billing_for_a_project
.. _Enable the Vertex AI API.:  https://cloud.google.com/ai-platform/docs
.. _Setup Authentication.: https://googleapis.dev/python/google-api-core/latest/auth.html

Installation
~~~~~~~~~~~~

Install this library in a `virtualenv`_ using pip. `virtualenv`_ is a tool to
create isolated Python environments. The basic problem it addresses is one of
dependencies and versions, and indirectly permissions.

With `virtualenv`_, it's possible to install this library without needing system
install permissions, and without clashing with the installed system
dependencies.

.. _virtualenv: https://virtualenv.pypa.io/en/latest/


Mac/Linux
^^^^^^^^^

.. code-block:: console

    pip install virtualenv
    virtualenv <your-env>
    source <your-env>/bin/activate
    <your-env>/bin/pip install google-cloud-aiplatform


Windows
^^^^^^^

.. code-block:: console

    pip install virtualenv
    virtualenv <your-env>
    <your-env>\Scripts\activate
    <your-env>\Scripts\pip.exe install google-cloud-aiplatform


Overview
~~~~~~~~
This section provides a brief overview of the Vertex SDK for Python. You can also reference the notebooks in `vertex-ai-samples`_ for examples.

.. _vertex-ai-samples: https://github.com/GoogleCloudPlatform/ai-platform-samples/tree/master/ai-platform-unified/notebooks/unofficial/sdk

Importing
^^^^^^^^^
SDK functionality can be used from the root of the package:

.. code-block:: Python

    from google.cloud import aiplatform


Initialization
^^^^^^^^^^^^^^
Initialize the SDK to store common configurations that you use with the SDK.

.. code-block:: Python

    aiplatform.init(
        # your Google Cloud Project ID or number
        # environment default used is not set
        project='my-project',

        # the Vertex AI region you will use
        # defaults to us-central1
        location='us-central1',

        # Googlge Cloud Stoage bucket in same region as location
        # used to stage artifacts
        staging_bucket='gs://my_staging_bucket',

        # custom google.auth.credentials.Credentials
        # environment default creds used if not set
        credentials=my_credentials,

        # customer managed encryption key resource name
        # will be applied to all Vertex AI resources if set
        encryption_spec_key_name=my_encryption_key_name,

        # the name of the experiment to use to track
        # logged metrics and parameters
        experiment='my-experiment',

        # description of the experiment above
        experiment_description='my experiment decsription'
    )

Datasets
^^^^^^^^
Vertex AI provides managed tabular, text, image, and video datasets. In the SDK, datasets can be used downstream to
train models.

To create a tabular dataset:

.. code-block:: Python

    my_dataset = aiplatform.TabularDataset.create(
        display_name="my-dataset", gcs_source=['gs://path/to/my/dataset.csv'])

You can also create and import a dataset in separate steps:

.. code-block:: Python

    from google.cloud import aiplatform

    my_dataset = aiplatform.TextDataset.create(
        display_name="my-dataset")

    my_dataset.import(
        gcs_source=['gs://path/to/my/dataset.csv']
        import_schema_uri=aiplatform.schema.dataset.ioformat.text.multi_label_classification
    )

To get a previously created Dataset:

.. code-block:: Python

  dataset = aiplatform.ImageDataset('projects/my-project/location/us-central1/datasets/{DATASET_ID}')

Vertex AI supports a variety of dataset schemas. References to these schemas are available under the
:code:`aiplatform.schema.dataset` namespace. For more information on the supported dataset schemas please refer to the
`Preparing data docs`_.

.. _Preparing data docs: https://cloud.google.com/ai-platform-unified/docs/datasets/prepare

Training
^^^^^^^^
The Vertex SDK for Python allows you train Custom and AutoML Models.

You can train custom models using a custom Python script, custom Python package, or container.

**Preparing Your Custom Code**

Vertex AI custom training enables you to train on Vertex AI datasets and produce Vertex AI models. To do so your
script must adhere to the following contract:

It must read datasets from the environment variables populated by the training service:

.. code-block:: Python

  os.environ['AIP_DATA_FORMAT']  # provides format of data
  os.environ['AIP_TRAINING_DATA_URI']  # uri to training split
  os.environ['AIP_VALIDATION_DATA_URI']  # uri to validation split
  os.environ['AIP_TEST_DATA_URI']  # uri to test split

Please visit `Using a managed dataset in a custom training application`_ for a detailed overview.

.. _Using a managed dataset in a custom training application: https://cloud.google.com/vertex-ai/docs/training/using-managed-datasets

It must write the model artifact to the environment variable populated by the traing service:

.. code-block:: Python

  os.environ['AIP_MODEL_DIR']

**Running Training**

.. code-block:: Python

  job = aiplatform.CustomTrainingJob(
      display_name="my-training-job",
      script_path="training_script.py",
      container_uri="gcr.io/cloud-aiplatform/training/tf-cpu.2-2:latest",
      requirements=["gcsfs==0.7.1"],
      model_serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-2:latest",
  )

  model = job.run(my_dataset,
                  replica_count=1,
                  machine_type="n1-standard-4",
                  accelerator_type='NVIDIA_TESLA_K80',
                  accelerator_count=1)

In the code block above `my_dataset` is managed dataset created in the `Dataset` section above. The `model` variable is a managed Vertex AI model that can be deployed or exported.


AutoMLs
-------
The Vertex SDK for Python supports AutoML tabular, image, text, video, and forecasting.

To train an AutoML tabular model:

.. code-block:: Python

  dataset = aiplatform.TabularDataset('projects/my-project/location/us-central1/datasets/{DATASET_ID}')

  job = aiplatform.AutoMLTabularTrainingJob(
    display_name="train-automl",
    optimization_prediction_type="regression",
    optimization_objective="minimize-rmse",
  )

  model = job.run(
      dataset=dataset,
      target_column="target_column_name",
      training_fraction_split=0.6,
      validation_fraction_split=0.2,
      test_fraction_split=0.2,
      budget_milli_node_hours=1000,
      model_display_name="my-automl-model",
      disable_early_stopping=False,
  )


Models
------

To deploy a model:


.. code-block:: Python

  endpoint = model.deploy(machine_type="n1-standard-4",
                          min_replica_count=1,
                          max_replica_count=5
                          machine_type='n1-standard-4',
                          accelerator_type='NVIDIA_TESLA_K80',
                          accelerator_count=1)


To upload a model:

.. code-block:: Python

  model = aiplatform.Model.upload(
      display_name='my-model',
      artifact_uri="gs://python/to/my/model/dir",
      serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-2:latest",
  )

To get a model:

.. code-block:: Python

  model = aiplatform.Model('/projects/my-project/locations/us-central1/models/{MODEL_ID}')

Please visit `Importing models to Vertex AI`_ for a detailed overview:

.. _Importing models to Vertex AI: https://cloud.google.com/vertex-ai/docs/general/import-model


Batch Prediction
----------------

To create a batch prediction job:

.. code-block:: Python

  model = aiplatform.Model('/projects/my-project/locations/us-central1/models/{MODEL_ID}')

  batch_prediction_job = model.batch_predict(
    job_display_name='my-batch-prediction-job',
    instances_format='csv'
    machine_type='n1-standard-4',
    gcs_source=['gs://path/to/my/file.csv']
    gcs_destination_prefix='gs://path/to/by/batch_prediction/results/'
  )

You can also create a batch prediction job asynchronously by including the `sync=False` argument:

.. code-block:: Python

  batch_prediction_job = model.batch_predict(..., sync=False)

  # wait for resource to be created
  batch_prediction_job.wait_for_resource_creation()

  # get the state
  batch_prediction_job.state

  # block until job is complete
  batch_prediction_job.wait()


Endpoints
---------

To get predictions from endpoints:

.. code-block:: Python

  endpoint.predict(instances=[[6.7, 3.1, 4.7, 1.5], [4.6, 3.1, 1.5, 0.2]])


To create an endpoint

.. code-block:: Python

  endpoint = endpoint.create(display_name='my-endpoint')

To deploy a model to a created endpoint:

.. code-block:: Python

  model = aiplatform.Model('/projects/my-project/locations/us-central1/models/{MODEL_ID}')

  endpoint.deploy(model,
                  min_replica_count=1,
                  max_replica_count=5
                  machine_type='n1-standard-4',
                  accelerator_type='NVIDIA_TESLA_K80',
                  accelerator_count=1)

To undeploy models from an endpoint:

.. code-block:: Python

  endpoint.undeploy_all()

To delete an endpoint:

.. code-block:: Python

  endpoint.delete()


Pipelines
---------

To create a Vertex Pipeline run and monitor until completion:

.. code-block:: Python

  # Instantiate PipelineJob object
  pl = PipelineJob(
      display_name="My first pipeline",

      # Whether or not to enable caching
      # True = always cache pipeline step result
      # False = never cache pipeline step result
      # None = defer to cache option for each pipeline component in the pipeline definition
      enable_caching=False,

      # Local or GCS path to a compiled pipeline definition
      template_path="pipeline.json",

      # Dictionary containing input parameters for your pipeline
      parameter_values=parameter_values,

      # GCS path to act as the pipeline root
      pipeline_root=pipeline_root,
  )

  # Execute pipeline in Vertex and monitor until completion
  pl.run(
    # Email address of service account to use for the pipeline run
    # You must have iam.serviceAccounts.actAs permission on the service account to use it
    service_account=service_account,

    # Whether this function call should be synchronous (wait for pipeline run to finish before terminating)
    # or asynchronous (return immediately)
    sync=True
  )

To create a Vertex Pipeline without monitoring until completion, use `submit` instead of `run`:

.. code-block:: Python

  # Instantiate PipelineJob object
  pl = PipelineJob(
      display_name="My first pipeline",

      # Whether or not to enable caching
      # True = always cache pipeline step result
      # False = never cache pipeline step result
      # None = defer to cache option for each pipeline component in the pipeline definition
      enable_caching=False,

      # Local or GCS path to a compiled pipeline definition
      template_path="pipeline.json",

      # Dictionary containing input parameters for your pipeline
      parameter_values=parameter_values,

      # GCS path to act as the pipeline root
      pipeline_root=pipeline_root,
  )

  # Submit the Pipeline to Vertex
  pl.submit(
    # Email address of service account to use for the pipeline run
    # You must have iam.serviceAccounts.actAs permission on the service account to use it
    service_account=service_account,
  )


Explainable AI: Get Metadata
----------------------------

To get metadata in dictionary format from TensorFlow 1 models:

.. code-block:: Python

  from google.cloud.aiplatform.explain.metadata.tf.v1 import saved_model_metadata_builder

  builder = saved_model_metadata_builder.SavedModelMetadataBuilder(
            'gs://python/to/my/model/dir', tags=[tf.saved_model.tag_constants.SERVING]
        )
  generated_md = builder.get_metadata()

To get metadata in dictionary format from TensorFlow 2 models:

.. code-block:: Python

  from google.cloud.aiplatform.explain.metadata.tf.v2 import saved_model_metadata_builder

  builder = saved_model_metadata_builder.SavedModelMetadataBuilder('gs://python/to/my/model/dir')
  generated_md = builder.get_metadata()

To use Explanation Metadata in endpoint deployment and model upload:

.. code-block:: Python

  explanation_metadata = builder.get_metadata_protobuf()

  # To deploy a model to an endpoint with explanation
  model.deploy(..., explanation_metadata=explanation_metadata)

  # To deploy a model to a created endpoint with explanation
  endpoint.deploy(..., explanation_metadata=explanation_metadata)

  # To upload a model with explanation
  aiplatform.Model.upload(..., explanation_metadata=explanation_metadata)


Next Steps
~~~~~~~~~~

-  Read the `Client Library Documentation`_ for Vertex AI
   API to see other available methods on the client.
-  Read the `Vertex AI API Product documentation`_ to learn
   more about the product and see How-to Guides.
-  View this `README`_ to see the full list of Cloud
   APIs that we cover.

.. _Vertex AI API Product documentation:  https://cloud.google.com/vertex-ai/docs
.. _README: https://github.com/googleapis/google-cloud-python/blob/main/README.rst
