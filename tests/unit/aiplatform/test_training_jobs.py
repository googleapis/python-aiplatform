from distutils.core import run_setup
import functools
import pathlib
import pytest
import subprocess
import shutil
import sys
import tarfile
import tempfile

from unittest import mock
from importlib import reload
from unittest.mock import patch

from google.cloud import aiplatform
from google.cloud.aiplatform.training_jobs import _timestamped_copy_to_gcs
from google.cloud.aiplatform.training_jobs import _get_python_executable
from google.cloud.aiplatform.training_jobs import _TrainingScriptPythonPackager
from google.cloud.aiplatform import initializer
from google.cloud import storage

_TEST_BUCKET_NAME = "test-bucket"
_TEST_GCS_PATH_WITHOUT_BUCKET = "path/to/folder"
_TEST_GCS_PATH = f"{_TEST_BUCKET_NAME}/{_TEST_GCS_PATH_WITHOUT_BUCKET}"
_TEST_GCS_PATH_WITH_TRAILING_SLASH = f"{_TEST_GCS_PATH}/"
_TEST_LOCAL_SCRIPT_FILE_NAME = "____test____script.py"
_TEST_LOCAL_SCRIPT_FILE_PATH = f"path/to/{_TEST_LOCAL_SCRIPT_FILE_NAME}"
_TEST_PROJECT = "test-project"
_TEST_PYTHON_SOURCE = """
print('hello world')
"""
_TEST_REQUIREMENTS = ["pandas", "numpy", "tensorflow"]


def local_copy_method(path):
    shutil.copy(path, ".")
    return pathlib.Path(path).name


@pytest.fixture
def mock_client_bucket():
    with patch.object(storage.Client, "bucket") as mock_client_bucket:

        def blob_side_effect(name, mock_blob, bucket):
            mock_blob.name = name
            mock_blob.bucket = bucket
            return mock_blob

        MockBucket = mock.Mock(autospec=storage.Bucket)
        MockBucket.name = _TEST_BUCKET_NAME
        MockBlob = mock.Mock(autospec=storage.Blob)
        MockBucket.blob.side_effect = functools.partial(
            blob_side_effect, mock_blob=MockBlob, bucket=MockBucket
        )
        mock_client_bucket.return_value = MockBucket

        yield mock_client_bucket, MockBlob


class TestTrainingScriptPythonPackagerHelpers:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def test_timestamp_copy_to_gcs_calls_gcs_client_with_bucket(
        self, mock_client_bucket
    ):

        mock_client_bucket, mock_blob = mock_client_bucket

        gcs_path = _timestamped_copy_to_gcs(
            local_file_path=_TEST_LOCAL_SCRIPT_FILE_PATH,
            gcs_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
        )

        local_script_file_name = pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_PATH).name

        mock_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_client_bucket.return_value.blob.assert_called_once()

        blob_arg = mock_client_bucket.return_value.blob.call_args[0][0]
        assert blob_arg.startswith("aiplatform-")
        assert blob_arg.endswith(_TEST_LOCAL_SCRIPT_FILE_NAME)

        mock_blob.upload_from_filename.assert_called_once_with(
            _TEST_LOCAL_SCRIPT_FILE_PATH
        )
        assert gcs_path.endswith(local_script_file_name)
        assert gcs_path.startswith(f"gs://{_TEST_BUCKET_NAME}/aiplatform-")

    def test_timestamp_copy_to_gcs_calls_gcs_client_with_gcs_path(
        self, mock_client_bucket
    ):

        mock_client_bucket, mock_blob = mock_client_bucket

        gcs_path = _timestamped_copy_to_gcs(
            local_file_path=_TEST_LOCAL_SCRIPT_FILE_PATH,
            gcs_dir=_TEST_GCS_PATH_WITH_TRAILING_SLASH,
            project=_TEST_PROJECT,
        )

        local_script_file_name = pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_PATH).name

        mock_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_client_bucket.return_value.blob.assert_called_once()

        blob_arg = mock_client_bucket.return_value.blob.call_args[0][0]
        assert blob_arg.startswith(f"{_TEST_GCS_PATH_WITHOUT_BUCKET}/aiplatform-")
        assert blob_arg.endswith(f"{_TEST_LOCAL_SCRIPT_FILE_NAME}")

        mock_blob.upload_from_filename.assert_called_once_with(
            _TEST_LOCAL_SCRIPT_FILE_PATH
        )

        assert gcs_path.startswith(f"gs://{_TEST_GCS_PATH}/aiplatform-")
        assert gcs_path.endswith(local_script_file_name)

    def test_timestamp_copy_to_gcs_calls_gcs_client_with_trailing_slash(
        self, mock_client_bucket
    ):

        mock_client_bucket, mock_blob = mock_client_bucket

        gcs_path = _timestamped_copy_to_gcs(
            local_file_path=_TEST_LOCAL_SCRIPT_FILE_PATH,
            gcs_dir=_TEST_GCS_PATH,
            project=_TEST_PROJECT,
        )

        local_script_file_name = pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_PATH).name

        mock_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_client_bucket.return_value.blob.assert_called_once()

        blob_arg = mock_client_bucket.return_value.blob.call_args[0][0]
        assert blob_arg.startswith(f"{_TEST_GCS_PATH_WITHOUT_BUCKET}/aiplatform-")
        assert blob_arg.endswith(_TEST_LOCAL_SCRIPT_FILE_NAME)

        mock_blob.upload_from_filename.assert_called_once_with(
            _TEST_LOCAL_SCRIPT_FILE_PATH
        )

        assert gcs_path.startswith(f"gs://{_TEST_GCS_PATH}/aiplatform-")
        assert gcs_path.endswith(local_script_file_name)

    def test_timestamp_copy_to_gcs_calls_gcs_client(self, mock_client_bucket):

        mock_client_bucket, mock_blob = mock_client_bucket

        gcs_path = _timestamped_copy_to_gcs(
            local_file_path=_TEST_LOCAL_SCRIPT_FILE_PATH,
            gcs_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
        )

        mock_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_client_bucket.return_value.blob.assert_called_once()
        mock_blob.upload_from_filename.assert_called_once_with(
            _TEST_LOCAL_SCRIPT_FILE_PATH
        )
        assert gcs_path.endswith(pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_PATH).name)
        assert gcs_path.startswith(f"gs://{_TEST_BUCKET_NAME}")

    def test_get_python_executable_raises_if_None(self):
        with patch.object(sys, "executable", new=None):
            with pytest.raises(EnvironmentError):
                _get_python_executable()

    def test_get_python_executable_returns_python_executable(self):
        assert "python" in _get_python_executable().lower()


class TestTrainingScriptPythonPackager:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        with open(_TEST_LOCAL_SCRIPT_FILE_NAME, "w") as fp:
            fp.write(_TEST_PYTHON_SOURCE)

    def teardown_method(self):
        pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_NAME).unlink()
        python_package_file = f"{_TrainingScriptPythonPackager._ROOT_MODULE}-{_TrainingScriptPythonPackager._SETUP_PY_VERSION}.tar.gz"
        if pathlib.Path(python_package_file).is_file():
            pathlib.Path(python_package_file).unlink()
        subprocess.check_output(
            ["pip3", "uninstall", "-y", _TrainingScriptPythonPackager._ROOT_MODULE]
        )

    def test_packager_creates_and_copies_python_package(self):
        tsp = _TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)
        tsp.package_and_copy(copy_method=local_copy_method)
        assert pathlib.Path(
            f"{tsp._ROOT_MODULE}-{tsp._SETUP_PY_VERSION}.tar.gz"
        ).is_file()

    def test_created_package_module_is_installable_and_can_be_run(self):
        tsp = _TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)
        source_dist_path = tsp.package_and_copy(copy_method=local_copy_method)
        subprocess.check_output(["pip3", "install", source_dist_path])
        module_output = subprocess.check_output(
            [_get_python_executable(), "-m", tsp.module_name]
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
                    pathlib.Path(tmpdirname, setup_py_path), stop_after="init"
                )
                assert _TEST_REQUIREMENTS == setup_py.install_requires

    def test_packaging_fails_whith_RuntimeError(self):
        with patch("subprocess.Popen") as mock_popen:
            mock_subprocess = mock.Mock()
            mock_subprocess.communicate.return_value = (b"", b"")
            mock_subprocess.returncode = 1
            mock_popen.return_value = mock_subprocess
            tsp = _TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)
            with pytest.raises(RuntimeError):
                tsp.package_and_copy(copy_method=local_copy_method)

    def test_package_and_copy_to_gcs_copies_to_gcs(self, mock_client_bucket):
        mock_client_bucket, mock_blob = mock_client_bucket

        tsp = _TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)

        gcs_path = tsp.package_and_copy_to_gcs(
            gcs_staging_dir=_TEST_BUCKET_NAME, project=_TEST_PROJECT
        )

        mock_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_client_bucket.return_value.blob.assert_called_once()

        mock_blob.upload_from_filename.call_args[0][0].endswith(
            "/trainer/dist/aiplatform_custom_trainer_script-0.1.tar.gz"
        )

        assert gcs_path.endswith("-aiplatform_custom_trainer_script-0.1.tar.gz")
        assert gcs_path.startswith(f"gs://{_TEST_BUCKET_NAME}")
