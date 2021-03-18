
# Specifies base image and tag
FROM gcr.io/google-appengine/python
WORKDIR /root

# Installs additional packages
RUN pip3 install git+https://github.com/googleapis/python-aiplatform@mb-release

# Copies the trainer code to the docker image.
COPY remote_runner.py /root/remote_runner.py

# Sets up the entry point to invoke the trainer.
ENTRYPOINT ["python3", "remote_runner.py"]
