VertexModel SDK for Python
=================================================

|GA| |pypi| |versions|


`Vertex AI`_: Google Vertex AI is an integrated suite of machine learning tools and services for building and using ML models with AutoML or custom code. It offers both novices and experts the best workbench for the entire machine learning development lifecycle.

- `Client Library Documentation`_
- `Product Documentation`_

.. |GA| image:: https://img.shields.io/badge/support-ga-gold.svg
   :target: https://github.com/googleapis/google-cloud-python/blob/master/README.rst#general-availability
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

Install this library by either forking this GitHub repository, or running the following command in a CoLab notebook:

.. code-block:: console

    ! pip3 install --force-reinstall --upgrade git+https://github.com/googleapis/python-aiplatform.git@refs/pull/603/merge


Overview
~~~~~~~~
This section provides a brief overview of the VertexModel SDK for Python. You can also reference the following notebooks (Alphabet-internal only) for examples.

- `Local Training and Prediction`_
- `Cloud Training and Local Prediction`_
 
.. _Local Training and Prediction: https://colab.research.google.com/drive/12vD9fMPE3uYwdxWFUkPXT1bV-IrUcGIS?usp=sharing
.. _Cloud Training and Local Prediction: https://colab.research.google.com/drive/1J0CxGCJXiNWj-RlRk8Boq_Rk-PehVf2N?usp=sharing
 
 
Importing
^^^^^^^^^
SDK functionality can be used from the root of the package:

.. code-block:: Python

    from google.cloud.aiplatform.experimental.vertex_model import base


VertexModel Class
^^^^^^^^^^^^^^
All implementations of the VertexModel SDK must extend the abstract VertexModel class.

.. code-block:: Python

    class VertexModel(metaclass=abc.ABCMeta):
    """ Parent class that users can extend to use the Vertex AI SDK """

    _data_serialization_mapping = {
        pd.DataFrame: (pandas._deserialize_dataframe, pandas._serialize_dataframe),
        torch.utils.data.DataLoader: (
            pytorch._deserialize_dataloader,
            pytorch._serialize_dataloader,
        ),
    }

    def __init__(self, *args, **kwargs):
        """ All child class constructor arguments must be passed to the
            VertexModel constructor as well. """
        
        self._training_job = None
        self._model = None
        self._constructor_arguments = (args, kwargs)
        
        # Default dependencies; can be modified when creating child class
        self._dependencies = [
            "pandas>=1.3",
            "torch>=1.7",
            "google-cloud-aiplatform @ git+https://github.com/googleapis/python-aiplatform@refs/pull/603/head#egg=google-cloud-aiplatform",
        ]

        # Default to local training on creation; change this variable to "cloud"
        # to switch to remote training and prediction
        self.training_mode = "local"

        # Hidden functionality that allows you to switch workflows
        self.fit = vertex_fit_function_wrapper(self.fit)
        self.predict = vertex_predict_function_wrapper(self.predict)

    @abc.abstractmethod
    def fit(self):
        """Train model."""
        pass

    @abc.abstractmethod
    def predict(self):
        """Make predictions on training data."""
        pass


Data Serialization
^^^^^^^^
The VertexModel class currently provides default serialization for pandas DataFrame and PyTorch DataLoader objects. If you wish to perform remote training 
and/or prediction with any other form of dataset, you must implement your own serialization and deserialization functions that obey the following rules:

1. Your serialization function has the input parameters of a valid GCS URI, a dataset object, and a string identifying your dataset.
2. Your serialization function returns the remote location of your serialized object.
3. Your deserialization function has one input parameter: the GCS URI of your serialized object.
4. Your deserialization function returns a deserialized dataset object.

To add your functions to the VertexModel implementation:

.. code-block:: Python

    my_model = MyModelClass()
    my_model._data_serialization_mapping[DatasetType] = (my_deserialization_function, my_serialization_function)

Training
^^^^^^^^
The Vertex SDK for Python allows you to train your custom child class.

**Preparing Your Custom Code**

To do so your script must adhere to the following contract:

1. The constructor of VertexModel must be called with the constructor arguments of your child class
2. You must implement your own versions of fit() and predict()

**Running Training**

.. code-block:: Python

    import google.cloud.aiplatform as aiplatform
    
    aiplatform.init(project=MY_PROJECT_ID, staging_bucket=MY_STAGING_BUCKET)

    my_model = MyModelClass()

    my_model.training_mode = "local" # Local training using machine resources
    my_model.training_mode = "remote" # Remote training using GCS and Vertex AI API Custom Job

    my_model.fit("""Input parameters here, such as your dataset, number of epochs, etc.""")

Prediction
^^^^^^^^

To get predictions from your model:

.. code-block:: Python

  my_model.training_mode = "local" # Local prediction using machine resources
  my_model.training_mode = "remote" # Remote prediction using GCS and Vertex AI API Endpoint
  
  results = my_model.predict("""Input parameters here, such as the data you wish to perform predictions on""")
  

Background
~~~~~~~~~~

-  Read the `Client Library Documentation`_ for Vertex AI
   API to see other available methods on the client.
-  Read the `Vertex AI API Product documentation`_ to learn
   more about the product and see How-to Guides.
-  View this `README`_ to see the full list of Cloud
   APIs that we cover.

.. _Vertex AI API Product documentation:  https://cloud.google.com/vertex-ai/docs
.. _README: https://github.com/googleapis/google-cloud-python/blob/master/README.rst
