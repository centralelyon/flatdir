import packaging.version

import flatdir


def test_version_is_valid() -> None:
    _ = packaging.version.parse(flatdir.__version__)
