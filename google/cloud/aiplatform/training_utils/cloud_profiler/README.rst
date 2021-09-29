Cloud Profiler
=================================

Cloud Profiler allows you to profile your remote Vertex AI Training jobs on demand. To understand the performance of your training code, a user can update their scripts by initializing the profiler and capturing the profile session through Vertex TensorBoard.

Quick Start
------------

To start using the profiler, update the training script to include the following:

.. code-block:: Python

    from google.cloud.aiplatform.training_utils import cloud_profiler
    ...
    cloud_profiler.init()


Next, run the job with with a Vertex TensorBoard instance. For full details on how to do this, visit https://cloud.google.com/vertex-ai/docs/experiments/tensorboard-overview

Finally, visit your TensorBoard instance and click the `Capture Profile` button. This will allow users to capture profiling statistics for the running jobs.
