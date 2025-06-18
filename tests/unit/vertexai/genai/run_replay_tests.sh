#!/bin/bash

# This script runs replay tests for the Vertex SDK GenAI client
# It is intended to be used from the google3 directory of a CitC client.
# You can provide a specific test file to run, or it will run all the replay tests
# in third_party/py/google/cloud/aiplatform/tests/unit/vertexai/genai/replays/
#
# Example:
#   ./third_party/py/google/cloud/aiplatform/tests/unit/vertexai/genai/run_replay_tests.sh test_evals.py

# It also supports a --mode flag, which can be one of:
#   * record: Call the API and record the result in a replay file.
#   * replay: Use the recorded replay file to simulate the API call, or record if the replay file does not exist.
#   * api: Call the API and do not record.

# Get the current working directory
START_DIR=$(pwd)

# Check if the current directory ends with /google3
# Otherwise the copybara command will fail
if [[ "$START_DIR" != */google3 ]]; then
    echo "Error: This script must be run from your client's '/google3' directory."
    echo "Your current directory is: $START_DIR"
    exit 1
fi

# Check required env vars have been set
REQUIRED_ENV_VARS=(
    "GOOGLE_CLOUD_PROJECT"
    "GOOGLE_CLOUD_LOCATION"
    "GOOGLE_GENAI_REPLAYS_DIRECTORY"
)

for var_name in "${REQUIRED_ENV_VARS[@]}"; do
    var_value="${!var_name}"
    if [ -z "$var_value" ]; then
        echo "Error: Environment variable $var_name is not set."
        echo "Please set it before running this script."
        exit 1
    fi
done

# Generate a unique temporary directory in /tmp/
TEMP_DIR=$(mktemp -d -t XXXXXX)

# Check if the temporary directory was created successfully
if [ -z "$TEMP_DIR" ]; then
    echo "Error: Could not create a temporary directory."
    exit 1
fi

echo "Created temporary directory: $TEMP_DIR"

# Run copybara and copy Vertex SDK to the temporary directory
# The --folder-dir argument is set to the newly created temporary directory.
echo "Running copybara..."
COPYBARA_EXEC="/google/bin/releases/copybara/public/copybara/copybara"
"$COPYBARA_EXEC" third_party/py/google/cloud/aiplatform/copy.bara.sky folder_to_folder .. --folder-dir="$TEMP_DIR" --ignore-noop

# Check copybara's exit status
if [ $? -ne 0 ]; then
    echo "Error: copybara command failed. Exiting."
    # Clean up the temporary directory on failure
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "Copybara completed successfully."

# Change into the temporary directory with copybara output
echo "Changing into temp directory: $TEMP_DIR"
cd "$TEMP_DIR"

if [ $? -ne 0 ]; then
    echo "Error: Could not change into directory $TEMP_DIR. Exiting."
    exit 1
fi

PARSED_ARGS=$(getopt -o "" -l "mode:" -- "$@")

if [ $? -ne 0 ]; then
    echo "Error: Failed to parse command line arguments." >&2
    exit 1
fi

# Get the test file path and --mode flag value if provided
eval set -- "$PARSED_ARGS"

TEST_FILE_ARG="" # Stores the provided test path, if any
MODE_VALUE=""    # Stores the value of the --mode flag (e.g., 'replay')

while true; do
    case "$1" in
        --mode)
            MODE_VALUE="$2"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Internal error: Unrecognized arg option: '$1'" >&2
            exit 1
            ;;
    esac
done

# We expect at most one positional argument (the test file path).
if [ -n "$1" ]; then
    TEST_FILE_ARG="$1"
    if [ "$#" -gt 1 ]; then
        echo "Warning: Ignoring extra positional arguments after '$TEST_FILE_ARG'. Only one test file/path can be specified." >&2
    fi
fi

# Construct the full --mode argument string to be passed to pytest.
MODE_ARG=""
if [ -n "$MODE_VALUE" ]; then
    MODE_ARG="--mode $MODE_VALUE"
fi


# Set pytest path for which tests to run
DEFAULT_TEST_PATH="tests/unit/vertexai/genai/replays/"

if [ -n "$TEST_FILE_ARG" ]; then
    PYTEST_PATH="${DEFAULT_TEST_PATH}${TEST_FILE_ARG}"
    echo "Provided test file path: '$TEST_FILE_ARG'. Running pytest on: ${PYTEST_PATH}"
else
    PYTEST_PATH="$DEFAULT_TEST_PATH"
    echo "No test file arg provided. Running pytest on default path: ${PYTEST_PATH}"
fi

# Run tests
# -s is equivalent to --capture=no, it ensures pytest doesn't capture the output from stdout and stderr
# so it can be logged when this script is run
pytest -v -s "$PYTEST_PATH" ${MODE_ARG} --replays-directory-prefix="$START_DIR"

PYTEST_EXIT_CODE=$?

echo "Cleaning up temporary directory: $TEMP_DIR"
# Go back to the original directory before removing the temporary directory
cd - > /dev/null
rm -rf "$TEMP_DIR"

echo "Pytest tests completed with exit code: $PYTEST_EXIT_CODE."

exit $PYTEST_EXIT_CODE