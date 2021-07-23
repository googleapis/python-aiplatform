import re
import time

from typing import Callable


def get_name(out, key="name"):
    pattern = re.compile(fr'{key}:\s*"([\-a-zA-Z0-9/]+)"')
    name = re.search(pattern, out).group(1)

    return name


def get_state(out):
    pattern = re.compile(r"state:\s*([._a-zA-Z0-9/]+)")
    state = re.search(pattern, out).group(1)

    return state


def wait_for_job_state(
    get_job_method: Callable[[str], "proto.Message"],  # noqa: F821
    name: str,
    expected_state: str = "CANCELLED",
    timeout: int = 90,
    freq: float = 1.5,
) -> None:
    """ Waits until the Job state of provided resource name is a particular state.

    Args:
        get_job_method: Callable[[str], "proto.Message"]
            Required. The GAPIC getter method to poll. Takes 'name' parameter
            and has a 'state' attribute in its response.
        name (str):
            Required. Complete uCAIP resource name to pass to get_job_method
        expected_state (str):
            The state at which this method will stop waiting.
            Default is "CANCELLED".
        timeout (int):
            Maximum number of seconds to wait for expected_state. If the job
            state is not expected_state within timeout, a TimeoutError will be raised.
            Default is 90 seconds.
        freq (float):
            Number of seconds between calls to get_job_method.
            Default is 1.5 seconds.
    """

    for _ in range(int(timeout / freq)):
        response = get_job_method(name=name)
        if expected_state in str(response.state):
            return None
        time.sleep(freq)

    raise TimeoutError(
        f"Job state did not become {expected_state} within {timeout} seconds"
        "\nTry increasing the timeout in sample test"
        f"\nLast recorded state: {response.state}"
    )
