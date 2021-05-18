Vertex SDK for Python
=================================================

|beta| |pypi| |versions|


`Vertex AI`_: Google Vertex AI is an integrated suite of machine learning tools and services for building and using ML models with AutoML or custom code. It offers both novices and experts the best workbench for the entire machine learning development lifecycle.

- `Client Library Documentation`_
- `Product Documentation`_

.. |beta| image:: https://img.shields.io/badge/support-beta-orange.svg
   :target: https://github.com/googleapis/google-cloud-python/blob/master/README.rst#beta-support
.. |pypi| image:: https://img.shields.io/pypi/v/google-cloud-aiplatform.svg
   :target: https://pypi.org/project/google-cloud-aiplatform/
.. |versions| image:: https://img.shields.io/pypi/pyversions/google-cloud-aiplatform.svg
   :target: https://pypi.org/project/google-cloud-aiplatform/
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

.. _`virtualenv`: https://virtualenv.pypa.io/en/latest/


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
Importing
^^^^^^^^^^^^^^^^^^^^
SDK functionality can be used from the root of the package:

.. code-block:: Python

    from google.cloud import aiplatform


Initialization
^^^^^^^^^^^^^^^^^^^^
Initialize the SDK to store common configurations that will be used throughout the SDK.

.. code-block:: Python

    aiplatform.init(
        # your GCP project ID or number
        # environment default used is not set
        project='my-project',

        # the Vertex AI region you will use
        # defaults to us-central1
        location='us-central1',

        # bucket in same region as location
        # used to stage artifacts
        staging_bucket='gs://my_staging_bucket',

        # custom google.auth.credentials.Credentials
        # environment default creds used if not set
        credentials=my_credentials,

        # customer managed encryption key resource name
        # will be applied to all AI Platform resources if set
        encryption_spec_key_name=my_encryption_key_name,

        # the name of the experiment to use to track
        # logged metrics and parameters
        experiment='my-experiment',

        # description of the experiment above
        experiment_description='my experiment decsription' 
    )

Datasets
^^^^^^^^
AI Platform provides managed Tabular, Text, Image, and Video datasets. In the SDK, Datasets can be used downstream to
train models.

To create a Tabular dataset:

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

Vertex AI supports a variety of dataset schemas. References to these schemas are available under the
:code:`aiplatform.schema.dataset` namespace. For more information on the supported dataset schemas please refer to the
`Preparing data docs`_.

.. _Preparing data docs: https://cloud.google.com/ai-platform-unified/docs/datasets/prepare

Training
^^^^^^^^
The Vertex SDK allows you train Custom and AutoML Models.

Custom models can be trained using a custom Python script, custom Python package, or container.

Preparing Your Custom Code
--------------------------
Vertex AI custom training enables you to train on AI Platform Datasets and produce AI Platform Models. To do so your
script must adhere to the following contract:

1. It must read dataset from the environment variables populated by the training service:

.. code-block:: Python

  os.environ['AIP_DATA_FORMAT']  # provides format of data  
  os.environ['AIP_TRAINING_DATA_URI']  # uri to training split
  os.environ['AIP_VALIDATION_DATA_URI']  # uri to validation split
  os.environ['AIP_TEST_DATA_URI']  # uri to test split

Please visit `Using a managed dataset in a custom training application`_ for a detailed overview information.

.. _Using a managed dataset in a custom training application: https://cloud.google.com/vertex-ai/docs/training/using-managed-datasets

2. It must write the model artifact to the environment variable populated by the traing service:

.. code-block:: Python 

  os.environ['AIP_MODEL_DIR']

Running Training
----------------

.. code-block:: Python

  job = aiplatform.CustomTrainingJob(
      display_name="my-training-job",
      script_path="training_script.py",
      container_uri="gcr.io/cloud-aiplatform/training/tf-cpu.2-2:latest",
      requirements=["gcsfs==0.7.1"],
      model_serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-2:latest",
  )

  model = job.run(my_dataset, replica_count=1)

In the code block above my_dataset is managed dataset created in the `Datasets` section above. `model` is a Managed Vertex AI Model that the be deployed or exported.




Next Steps
~~~~~~~~~~

-  Read the `Client Library Documentation`_ for Vertex AI
   API to see other available methods on the client.
-  Read the `Vertex AI API Product documentation`_ to learn
   more about the product and see How-to Guides.
-  View this `README`_ to see the full list of Cloud
   APIs that we cover.

.. _Vertex AI API Product documentation:  https://cloud.google.com/vertex-ai/docs
.. _README: https://github.com/googleapis/google-cloud-python/blob/master/README.rst