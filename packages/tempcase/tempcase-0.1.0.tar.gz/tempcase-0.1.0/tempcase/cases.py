
import os
import unittest
from datetime import datetime
import shutil
from functools import wraps
from warnings import warn
from tempfile import mkdtemp
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory


__all__ = ['TempCase', 'in_tempdir']


TIMESTAMP = datetime.now().isoformat()
DEFAULT_PROJECT_NAME = 'python'


class TempCase(unittest.TestCase):
    """
    Usage:
    If your test case dumps out any files, use ``self.path_to("path", "to", "my.file")`` to get the path to a directory
    in your temporary directory. This will be namespaced by the test class, timestamp and test method, e.g.

    >>> self.path_to("path", "to", "my.file")
    /tmp/mymodule_MyTestCase_2018-03-08T18:32:18.967927_r4nd0m/my_test_method/path/to/my.file

    Each test method's data will be deleted after the test case is run (regardless of pass, fail or error).

    To disable test method data deletion, set ``self._cleanup = False`` anywhere in the test.

    The test case directory will be deleted after every test method is run, unless there is data left in it.

    Any files written directly to the class output directory (rather than the test output subdirectory) should therefore
    be explicitly removed before tearDownClass is called.

    To disable data deletion for the whole class (the test case directory and all tests), set ``_cleanup = False`` in the
    class definition. N.B. doing this in a method (``type(self)._cleanup = False``) will have unexpected results
    depending on the order of test execution.

    Subclasses implementing their own tearDown and tearDownClass should explicitly call the
    ``super`` method in the method definition.

    Subclasses can override the ``_project_name`` class member with the name of the project for more informative paths.
    """
    _output_root = None
    _cleanup = True
    _project_name = DEFAULT_PROJECT_NAME

    def path_to(self, *args):
        """
        Create a path by joining the root tempdir, the TestCase dir, and the test method dir with the given elements.

        The TestCase dir and test method dirs will be created if they do not already exist.
        """
        test_root = type(self).path_to_cls(self._testMethodName)
        if not os.path.isdir(test_root):
            os.mkdir(test_root)
        return os.path.join(test_root, *args)

    @classmethod
    def path_to_cls(cls, *args):
        """
        Create a path by joining the root tempdir and the TestCase dir with the given elements.

        The TestCase dir will be created if it does not already exist.
        """
        if not cls._output_root:
            cls._output_root = mkdtemp(prefix='{}_{}_{}_'.format(cls._project_name, cls.__name__, TIMESTAMP))
        return os.path.join(cls._output_root, *args)

    def tearDown(self):
        if not self._output_root:
            return
        path = os.path.join(self._output_root, self._testMethodName)
        if not os.path.isdir(path):
            return

        try:
            if self._cleanup:
                shutil.rmtree(path)
            else:
                warn('Directory {} was not deleted'.format(path))
        except OSError as e:
            if '[Errno 2]' in str(e):
                pass
            else:
                raise

    @classmethod
    def tearDownClass(cls):
        try:
            if not cls._output_root:
                return
            if cls._cleanup:
                os.rmdir(cls._output_root)
            else:
                warn('Directory {} was not deleted'.format(cls._output_root))
        except OSError as e:
            if '[Errno 39]' in str(e):
                warn('Directory {} could not be deleted as it still had data in it'.format(cls._output_root))
            elif '[Errno 2]' in str(e):
                pass
            else:
                raise


class ContainingTemporaryDirectory(TemporaryDirectory):
    def __enter__(self):
        tmpdirname = super(ContainingTemporaryDirectory, self).__enter__()
        self._initial_dir = os.getcwd()
        os.chdir(tmpdirname)
        return tmpdirname

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self._initial_dir)
        return super(ContainingTemporaryDirectory, self).__exit__(exc_type, exc_val, exc_tb)


def in_tempdir(project_name=DEFAULT_PROJECT_NAME):
    """
    Return a decorator which wraps a test function or method, and ensures that that method creates and changes
    the working directory to an informatively-named temporary directory, and then cleans up after itself.

    Parameters
    ----------
    project_name : str
        If the wrapped function is not a method of a ``TestCase``, or is but the test case does not have a
        ``_project_name`` defined, use this name when generating a temporary directory

    Returns
    -------
    decorator
    """
    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if len(args) > 0 and isinstance(args[0], unittest.TestCase):
                prefix_elements = [getattr(args[0], '_project_name', project_name), type(args[0]).__name__]
                suffix = '_' + args[0]._testMethodName
            else:
                prefix_elements = [project_name]
                suffix = None
            prefix_elements.append(TIMESTAMP)
            prefix = '_'.join(prefix_elements) + '_'
            with ContainingTemporaryDirectory(prefix=prefix, suffix=suffix):
                return fn(*args, **kwargs)
        return wrapped
    return wrapper
