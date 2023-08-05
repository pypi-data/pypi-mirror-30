"""Run the tests from the directory of the file."""
import functools
import os


def pytest_runtest_setup(item):
    """Execute each test in the directory where the test file lives."""
    starting_directory = os.getcwd()
    test_directory = os.path.dirname(str(item.fspath))
    os.chdir(test_directory)

    teardown = functools.partial(os.chdir, starting_directory)
    item.session._setupstate.addfinalizer(teardown, item)
