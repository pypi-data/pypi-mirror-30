import re

_canonicalize_regex = re.compile('[-_.]+')


def canonicalize_name(name):  # type: (str) -> str
    return _canonicalize_regex.sub('-', name).lower()


def module_name(name):  # type: (str) -> str
    return canonicalize_name(name).replace('-', '_')
