# test for Issue #1 (https://github.com/joommf/discretisedfield/issues/1)

# This test may catch any warnings/print statements that are
# unintentionally issued during import.

import sys

import subprocess
import pytest


def test_matplotlib_warning():
    executable = sys.executable
    command = executable + """ -c "import discretisedfield" """
    status, output = subprocess.getstatusoutput(command)

    # show output in case of failure, so we know what it is
    print(output)

    assert status == 0
    assert len(output) == 0
