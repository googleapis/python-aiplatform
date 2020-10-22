from distutils.core import run_setup
import os
import pytest
import subprocess
import shutil
import tarfile
import tempfile

from unittest import mock
from importlib import reload
from unittest.mock import patch

from google.cloud import aiplatform
from google.cloud.aiplatform.training_jobs import _timestamped_copy_to_gcs
from google.cloud.aiplatform.training_jobs import _get_python3_alias
from google.cloud.aiplatform.training_jobs import _TrainingScriptPythonPackager
from google.cloud.aiplatform import initializer
from google.cloud import storage

_TEST_BUCKET_NAME = "test-bucket"
_TEST_LOCAL_SCRIPT_FILE_NAME = "____test____script.py"
_TEST_LOCAL_SCRIPT_FILE_PATH = f"path/to/{_TEST_LOCAL_SCRIPT_FILE_NAME}.py"

_TEST_PROJECT = "test-project"
_TEST_PYTHON_SOURCE = """
print('hello world')
"""

_TEST_REQUIREMENTS = ["pandas", "numpy", "tensorflow"]


def local_copy_method(path):
    shutil.copy(path, ".")
    return os.path.basename(path)


class TestTrainingScriptPythonPackagerHelpers:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    @pytest.fixture
    def mock_client_bucket(self):
        with patch.object(storage.Client, "bucket") as mock_client_bucket:
            MockBucket = mock.Mock(autospec=storage.Bucket)
            MockBucket.name = _TEST_BUCKET_NAME
            MockBlob = mock.Mock(autospec=storage.Blob)
            MockBlob.name = _TEST_LOCAL_SCRIPT_FILE_PATH
            MockBlob.bucket = MockBucket
            MockBucket.blob.return_value = MockBlob
            mock_client_bucket.return_value = MockBucket

            yield mock_client_bucket

    def test_timestamp_copy_to_gcs_calls_gcs_client(self, mock_client_bucket):

        gcs_path = _timestamped_copy_to_gcs(
            local_file_path=_TEST_LOCAL_SCRIPT_FILE_PATH,
            staging_bucket=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
        )

        mock_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_client_bucket.return_value.blob.assert_called_once()
        mock_client_bucket.return_value.blob.return_value.upload_from_filename.assert_called_once_with(
            _TEST_LOCAL_SCRIPT_FILE_PATH
        )
        assert gcs_path.endswith(os.path.basename(_TEST_LOCAL_SCRIPT_FILE_PATH))
        assert gcs_path.startswith(f"gs://{_TEST_BUCKET_NAME}")

    def test_get_python3_alias_fails_with_just_python2(self):
        with patch.object(subprocess, "check_output") as mock_check_output:
            mock_check_output.return_value = b"Python 2.7.3"
            with pytest.raises(EnvironmentError):
                python_cmd = _get_python3_alias()

    def test_get_python3_alias_fails_with_no_python(self):
        with patch.object(subprocess, "check_output") as mock_check_output:
            mock_check_output.side_effect = FileNotFoundError()
            with pytest.raises(EnvironmentError):
                python_cmd = _get_python3_alias()

    def test_get_python3_alias_succeeds_with_python3(self):
        with patch.object(subprocess, "check_output") as mock_check_output:
            mock_check_output.side_effect = [b"Python 2.7.3", b"Python 3.6.3"]
            assert _get_python3_alias() == "python3"

    def test_get_python3_alias_succeeds_with_python(self):
        with patch.object(subprocess, "check_output") as mock_check_output:
            mock_check_output.side_effect = [b"Python 3.6.3", b"Python 3.6.3"]
            assert _get_python3_alias() == "python"


class TestTrainingScriptPythonPackager:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        with open(_TEST_LOCAL_SCRIPT_FILE_NAME, "w") as fp:
            fp.write(_TEST_PYTHON_SOURCE)

    def teardown_method(self):
        os.remove(_TEST_LOCAL_SCRIPT_FILE_NAME)
        python_package_file = f"{_TrainingScriptPythonPackager._ROOT_MODULE}-{_TrainingScriptPythonPackager._SETUP_PY_VERSION}.tar.gz"
        if os.path.isfile(python_package_file):
            os.remove(python_package_file)
        subprocess.check_output(
            ["pip3", "uninstall", "-y", _TrainingScriptPythonPackager._ROOT_MODULE]
        )

    def test_packager_creates_and_copies_python_package(self):
        tsp = _TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)
        tsp.package_and_copy(copy_method=local_copy_method)
        assert os.path.isfile(f"{tsp._ROOT_MODULE}-{tsp._SETUP_PY_VERSION}.tar.gz")

    def test_created_package_module_is_installable_and_can_be_run(self):
        tsp = _TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)
        source_dist_path = tsp.package_and_copy(copy_method=local_copy_method)
        subprocess.check_output(["pip3", "install", source_dist_path])
        module_output = subprocess.check_output(
            [_get_python3_alias(), "-m", tsp.module_name]
        )
        assert "hello world" in module_output.decode()

    def test_requirements_are_in_package(self):
        tsp = _TrainingScriptPythonPackager(
            _TEST_LOCAL_SCRIPT_FILE_NAME, requirements=_TEST_REQUIREMENTS
        )
        source_dist_path = tsp.package_and_copy(copy_method=local_copy_method)
        with tarfile.open(source_dist_path) as tf:
            with tempfile.TemporaryDirectory() as tmpdirname:
                setup_py_path = f"{_TrainingScriptPythonPackager._ROOT_MODULE}-{_TrainingScriptPythonPackager._SETUP_PY_VERSION}/setup.py"
                tf.extract(setup_py_path, path=tmpdirname)
                setup_py = run_setup(
                    os.path.join(tmpdirname, setup_py_path), stop_after="init"
                )
                assert _TEST_REQUIREMENTS == setup_py.install_requires
