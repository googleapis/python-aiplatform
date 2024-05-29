Cloud Profiler
=================================

Cloud Profiler allows you to profile your remote Vertex AI Training jobs on demand and visualize the results in Vertex Tensorboard.

Quick Start
------------

To start using the profiler with TensorFlow, update your training script to include the following:

.. code-block:: Python

    from google.cloud.aiplatform.training_utils import cloud_profiler
    ...
    cloud_profiler.init()


Next, run the job with with a Vertex TensorBoard instance. For full details on how to do this, visit https://cloud.google.com/vertex-ai/docs/experiments/tensorboard-overview

Finally, visit your TensorBoard in your Google Cloud Console, navigate to the "Profile" tab, and click the `Capture Profile` button. This will allow users to capture profiling statistics for the running jobs.
