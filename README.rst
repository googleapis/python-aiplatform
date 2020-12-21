Python Client for Cloud AI Platform
=================================================

**Experimental**

This is an Experimental release. Experiments are focused on validating a prototype. They are not guaranteed to be released and might be subject to backward-incompatible changes. They are not intended for production use or covered by any SLA,  support obligation, or deprecation policy. They are covered by the `Pre-GA Offerings Terms`_ of the Google Cloud Platform Terms of Services.

.. _Pre-GA Offerings Terms:  https://cloud.google.com/terms/service-terms#1

----

|beta| |pypi| |versions|


`Cloud AI Platform`_: Google Cloud AI Platform is an integrated suite of machine learning tools and services for building and using ML models with AutoML or custom code. It offers both novices and experts the best workbench for the entire machine learning development lifecycle.

- `Client Library Documentation`_
- `Product Documentation`_

.. |beta| image:: https://img.shields.io/badge/support-beta-orange.svg
   :target: https://github.com/googleapis/google-cloud-python/blob/master/README.rst#beta-support
.. |pypi| image:: https://img.shields.io/pypi/v/google-cloud-aiplatform.svg
   :target: https://pypi.org/project/google-cloud-aiplatform/
.. |versions| image:: https://img.shields.io/pypi/pyversions/google-cloud-aiplatform.svg
   :target: https://pypi.org/project/google-cloud-aiplatform/
.. _Cloud AI Platform: https://cloud.google.com/ai-platform-unified/docs
.. _Client Library Documentation: https://googleapis.dev/python/aiplatform/latest
.. _Product Documentation:  https://cloud.google.com/ai-platform-unified/docs

Quick Start
-----------

In order to use this library, you first need to go through the following steps:

1. `Select or create a Cloud Platform project.`_
2. `Enable billing for your project.`_
3. `Enable the Cloud AI Platform API.`_
4. `Setup Authentication.`_

.. _Select or create a Cloud Platform project.: https://console.cloud.google.com/project
.. _Enable billing for your project.: https://cloud.google.com/billing/docs/how-to/modify-project#enable_billing_for_a_project
.. _Enable the Cloud AI Platform API.:  https://cloud.google.com/ai-platform/docs
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

Next Steps
~~~~~~~~~~

-  Read the `Client Library Documentation`_ for Cloud AI Platform
   API to see other available methods on the client.
-  Read the `Cloud AI Platform API Product documentation`_ to learn
   more about the product and see How-to Guides.
-  View this `README`_ to see the full list of Cloud
   APIs that we cover.

.. _Cloud AI Platform API Product documentation:  https://cloud.google.com/ai-platform-unified/docs
.. _README: https://github.com/googleapis/google-cloud-python/blob/master/README.rst
