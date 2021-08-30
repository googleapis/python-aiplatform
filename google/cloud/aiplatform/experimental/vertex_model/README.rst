VertexModel SDK for Python
=================================================

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
All implementations of the VertexModel SDK must extend the abstract VertexModel class. Below is an example of a child class that also uses the PyTorch library to complete training and prediction on data stored in Pandas DataLoader objects.

To use the VertexModel class, your implementation must adhere to the following contract:

1. The constructor of VertexModel must be called with the constructor arguments of your child class.
2. You must implement your own versions of fit() and predict().

.. code-block:: Python

   import torch
   from google.cloud.aiplatform.experimental.vertex_model import base
   import numpy as np
   import pandas as pd

   class LinearRegression(base.VertexModel, torch.nn.Module): 

     def __init__(self, input_size: int, output_size: int):
       base.VertexModel.__init__(self, input_size=input_size, output_size=output_size)
       torch.nn.Module.__init__(self)
       self.linear = torch.nn.Linear(input_size, output_size)

     def forward(self, x):
       return self.linear(x)

     def train_loop(self, dataloader, loss_fn, optimizer):
       size = len(dataloader.dataset)

       for batch, (X, y) in enumerate(dataloader):
           pred = self.linear(X.float())
           loss = loss_fn(pred.float(), y.float())

           optimizer.zero_grad()
           loss.backward()
           optimizer.step()

     # Implementation of fit(), an abstract method in VertexModel
     def fit(self, data: pd.DataFrame, target_column: str, epochs: int, learning_rate: float):
       feature_columns = list(data.columns)
       feature_columns.remove(target_column)

       features = torch.tensor(data[feature_columns].values)
       target = torch.tensor(data[target_column].values)

       dataloader = torch.utils.data.DataLoader(
             torch.utils.data.TensorDataset(features, target),
             batch_size=10, shuffle=True)

       loss_fn = torch.nn.MSELoss()
       optimizer = torch.optim.SGD(self.parameters(), lr=learning_rate)

       for t in range(epochs):
           self.train_loop(dataloader, loss_fn, optimizer)

     # Implementation of predict(), an abstract method in VertexModel
     def predict(self, data):
       return self.forward(data)


Dependencies
^^^^^^^^
When using libraries other than PyTorch and Pandas (the default libraries for this SDK), update the dependencies of your
child class so that internal calls to the Vertex AI API have the correct information. Your dependencies must
take the form of a list of strings. You can do so as follows:

.. code-block:: Python

   my_model = MyModelClass()
   my_model.dependencies = ["library_name>=1.3", "library_name>=1.7",]


Data Serialization
^^^^^^^^
The VertexModel class currently provides default serialization for Pandas DataFrame and PyTorch DataLoader objects. If you wish to perform remote training 
and/or prediction with other dataset objects, you must implement your own serialization and deserialization functions that obey the following rules:

1. Your serialization function has the input parameters of a valid GCS URI, a dataset object, and a string identifying your dataset.
2. Your serialization function returns the remote location of your serialized object.
3. Your deserialization function has one input parameter: the GCS URI of your serialized object.
4. Your deserialization function returns a deserialized dataset object.

More specifically, the function signatures should follow this format:

.. code-block:: Python

   def my_serialization_method(artifact_uri: str, obj: Any, dataset_type:str) -> str:
      pass

   def my_deserialization_method(artifact_uri: str) -> Any:
      pass

To add your functions to the VertexModel implementation:

.. code-block:: Python

    my_model = MyModelClass()
    my_model._data_serialization_mapping[DatasetType] = (my_deserialization_function, my_serialization_function)
    
    
Training
^^^^^^^^
The Vertex SDK for Python allows you to train your custom child class.

**Running Training**

.. code-block:: Python

    import google.cloud.aiplatform as aiplatform
    
    aiplatform.init(project=MY_PROJECT_ID, staging_bucket=MY_STAGING_BUCKET)

    my_model = MyModelClass()

    my_model.remote = False # Local training using machine resources
    my_model.remote = True # Remote training using GCS and Vertex AI API Custom Job

    my_model.fit(my_train_data, epochs=num_epochs, learning_rate=lr)

Prediction
^^^^^^^^

To get predictions from your model:

.. code-block:: Python

  my_model.remote = False # Local prediction using machine resources
  my_model.remote = True # Remote prediction using GCS and Vertex AI API Endpoint
  
  results = my_model.predict(my_test_data)
  

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
