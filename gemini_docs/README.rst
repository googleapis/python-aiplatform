Vertex AI SDK for Python
=================================================

|GA| |pypi| |versions|

`Vertex AI`_: Google Vertex AI is an integrated suite of machine learning tools and services for building and using ML models with AutoML or custom code. It offers both novices and experts the best workbench for the entire machine learning development lifecycle.

- `Client Library Documentation`_
- `Product Documentation`_

.. |GA| image:: https://img.shields.io/badge/support-ga-gold.svg
   :target: https://github.com/googleapis/google-cloud-python/blob/main/README.rst#general-availability
.. |pypi| image:: https://img.shields.io/pypi/v/google-cloud-aiplatform.svg
   :target: https://pypi.org/project/google-cloud-aiplatform/
.. |versions| image:: https://img.shields.io/pypi/pyversions/google-cloud-aiplatform.svg
   :target: https://pypi.org/project/google-cloud-aiplatform/
.. _Vertex AI: https://cloud.google.com/vertex-ai/docs
.. _Client Library Documentation: https://cloud.google.com/python/docs/reference/aiplatform/latest
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
.. _Enable the Vertex AI API.:  https://cloud.google.com/vertex-ai/docs/start/use-vertex-ai-python-sdk
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

Supported Python Versions
^^^^^^^^^^^^^^^^^^^^^^^^^
Python >= 3.8

Importing
^^^^^^^^^

Vertex AI SDK general availability (GA) functionality can be used by importing the following namespace:

.. code-block:: Python

    import vertexai


Vertex AI SDK preview functionality can be used by importing the following namespace:

.. code-block:: Python

    from vertexai import preview

Usage
^^^^^

For detailed instructions, see `quickstart <http://cloud.google.com/vertex-ai/docs/generative-ai/start/quickstarts/quickstart-multimodal>`_ and `Introduction to multimodal classes in the Vertex AI SDK <http://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/sdk-for-gemini/gemini-sdk-overview-reference>`_.

Imports
^^^^^^^

.. code-block:: Python

  from vertexai.generative_models import GenerativeModel, Image, Content, Part, Tool, FunctionDeclaration, GenerationConfig


Basic generation:
^^^^^^^^^^^^^^^^^

.. code-block:: Python

  from vertexai.generative_models import GenerativeModel
  model = GenerativeModel("gemini-pro")
  print(model.generate_content("Why is sky blue?"))


Using images and videos
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: Python

  from vertexai.generative_models import GenerativeModel, Image
  vision_model = GenerativeModel("gemini-pro-vision")

  # Local image
  image = Image.load_from_file("image.jpg")
  print(vision_model.generate_content(["What is shown in this image?", image]))

  # Image from Cloud Storage
  image_part = generative_models.Part.from_uri("gs://download.tensorflow.org/example_images/320px-Felis_catus-cat_on_snow.jpg", mime_type="image/jpeg")
  print(vision_model.generate_content([image_part, "Describe this image?"]))

  # Text and video
  video_part = Part.from_uri("gs://cloud-samples-data/video/animals.mp4", mime_type="video/mp4")
  print(vision_model.generate_content(["What is in the video? ", video_part]))

Chat
^^^^

.. code-block:: Python

  from vertexai.generative_models import GenerativeModel, Image
  vision_model = GenerativeModel("gemini-ultra-vision")
  vision_chat = vision_model.start_chat()
  image = Image.load_from_file("image.jpg")
  print(vision_chat.send_message(["I like this image.", image]))
  print(vision_chat.send_message("What things do I like?."))


System instructions
^^^^^^^^^^^^^^^^^^^

.. code-block:: Python

  from vertexai.generative_models import GenerativeModel
  model = GenerativeModel(
      "gemini-1.0-pro",
      system_instruction=[
          "Talk like a pirate.",
          "Don't use rude words.",
      ],
  )
  print(model.generate_content("Why is sky blue?"))


Function calling
^^^^^^^^^^^^^^^^

.. code-block:: Python

  # First, create tools that the model is can use to answer your questions.
  # Describe a function by specifying it's schema (JsonSchema format)
  get_current_weather_func = generative_models.FunctionDeclaration(
      name="get_current_weather",
      description="Get the current weather in a given location",
      parameters={
          "type": "object",
          "properties": {
              "location": {
                  "type": "string",
                  "description": "The city and state, e.g. San Francisco, CA"
              },
              "unit": {
                  "type": "string",
                  "enum": [
                      "celsius",
                      "fahrenheit",
                  ]
              }
          },
          "required": [
              "location"
          ]
      },
  )
  # Tool is a collection of related functions
  weather_tool = generative_models.Tool(
      function_declarations=[get_current_weather_func],
  )

  # Use tools in chat:
  model = GenerativeModel(
      "gemini-pro",
      # You can specify tools when creating a model to avoid having to send them with every request.
      tools=[weather_tool],
  )
  chat = model.start_chat()
  # Send a message to the model. The model will respond with a function call.
  print(chat.send_message("What is the weather like in Boston?"))
  # Then send a function response to the model. The model will use it to answer.
  print(chat.send_message(
      Part.from_function_response(
          name="get_current_weather",
          response={
              "content": {"weather": "super nice"},
          }
      ),
  ))



Automatic Function calling
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: Python

  from vertexai..preview generative_models import GenerativeModel, Tool, FunctionDeclaration, AutomaticFunctionCallingResponder

  # First, create functions that the model is can use to answer your questions.
  def get_current_weather(location: str, unit: str = "centigrade"):
      """Gets weather in the specified location.

      Args:
          location: The location for which to get the weather.
          unit: Optional. Temperature unit. Can be Centigrade or Fahrenheit. Defaults to Centigrade.
      """
      return dict(
          location=location,
          unit=unit,
          weather="Super nice, but maybe a bit hot.",
      )

  # Infer function schema
  get_current_weather_func = FunctionDeclaration.from_func(get_current_weather)
  # Tool is a collection of related functions
  weather_tool = Tool(
      function_declarations=[get_current_weather_func],
  )

  # Use tools in chat:
  model = GenerativeModel(
      "gemini-pro",
      # You can specify tools when creating a model to avoid having to send them with every request.
      tools=[weather_tool],
  )

  # Activate automatic function calling:
  afc_responder = AutomaticFunctionCallingResponder(
      # Optional:
      max_automatic_function_calls=5,
  )
  chat = model.start_chat(responder=afc_responder)
  # Send a message to the model. The model will respond with a function call.
  # The SDK will automatically call the requested function and respond to the model.
  # The model will use the function call response to answer the original question.
  print(chat.send_message("What is the weather like in Boston?"))


Documentation
^^^^^^^^^^^^^

You can find complete documentation for the Vertex AI SDKs and the Gemini model in the Google Cloud [documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/overview)

Contributing
^^^^^^^^^^^^

See [Contributing](https://github.com/googleapis/python-aiplatform/blob/main/CONTRIBUTING.rst) for more information on contributing to the Vertex AI Python SDK.

License
^^^^^^^

The contents of this repository are licensed under the [Apache License, version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
