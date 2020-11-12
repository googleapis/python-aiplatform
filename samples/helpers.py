import re


def get_name(out, key="name"):
    pattern = re.compile(f'{key}:\s*"([\-a-zA-Z0-9/]+)"')
    name = re.search(pattern, out).group(1)

    return name


def get_state(out):
    pattern = re.compile("state:\s*([._a-zA-Z0-9/]+)")
    state = re.search(pattern, out).group(1)

    return state
