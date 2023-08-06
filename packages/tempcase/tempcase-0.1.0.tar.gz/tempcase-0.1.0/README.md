# tempcase

[![Build Status](https://travis-ci.org/clbarnes/tempcase.svg?branch=master)](https://travis-ci.org/clbarnes/tempcase)

Utilities for handling python test cases with temporary directories and files, for people using `pyunit`/`unittest`.

Supports python 2.7 and 3.4+.

N.B. the existence of this library is **not** an endorsement of `unittest`. 
Use [`pytest`](https://docs.pytest.org/en/latest/) if you want a powerful, modern, pythonic testing paradigm. 
Please.

## Motivation

Unit tests should be as isolated as possible, but when testing a file-generating method, it is often inconvenient to 
manually handle separate output directories with informative names and away from the code.

`pytest` solves this easily with the `tmpdir` fixture, but `unittest` has no such utility.

`tempcase` provides a base class for `unittest`-style test cases with ergonomic methods for creating temporary 
directories as required, with automatic cleanup which can be disabled for debugging purposes.

## Installation

```bash
pip install tempcase
```

## Usage

```python
import os

import tempcase


class MyTestCase(tempcase.TempCase):
    _project_name = 'mylibrary'

    def test_creates_file(self):
        """
        Test that ``my_file.txt`` is successfully created.
        The first call to ``path_to`` for a ``TestCase`` will create a directory in your default temp directory, 
        which has the name of the project as defined above, the name of the ``TestCase``, a timestamp, and a random
        alphanumeric string.
        The first call to ``path_to`` for a test method will create a subdirectory within that, named for the 
        test method.
        The test method directory and its contents will be deleted by ``tearDown``.
        The ``TestCase`` directory, if empty, will be cleaned up by ``tearDownClass``.
        """
        fpath = self.path_to('my_file.txt')  # os.path.join-like syntax
        open(fpath, 'w').close()
        self.assertTrue(os.path.isfile(fpath))
    
    def test_something_else(self):
        """No unnecessary directories are created"""
        self.assertTrue(True)

    def test_creates_file_no_cleanup(self):
        """
        Setting ``self._cleanup = False`` anywhere in a test method will disable cleanup just for that method, 
        allowing you to look at the output for debugging purposes.
        The containing ``TestCase`` directory will also not be deleted.
        """
        fpath = self.path_to('my_other_file.txt')
        open(fpath, 'w').close()
        self.assertTrue(os.path.isfile(fpath))
        self._cleanup = False

    def tearDown(self):
        """Be sure to call the super() tearDown if you override it! Same goes for tearDownClass."""
        super().tearDown()  # python 3+
        print("I did a tearDown")


class MyTestCaseWithNoCleanup(tempcase.TempCase):
    _project_name = 'mylibrary'
    _cleanup = False

    def test_creates_file(self):
        """This will not be cleaned up, by default"""
        fpath = self.path_to('my_file.txt')
        open(fpath, 'w').close()
    
    def test_creates_file_with_cleanup(self)
        """You can clean up individual methods if you like"""
        self._cleanup = True
        open(self.path_to('my_file.txt'), 'w').close()

```

For existing projects with an already-fragile inheritance chain above every test case, and local paths defined in
a method body (not in a `setUp`), the `in_tempdir` decorator may be useful. It creates a temporary directory, 
changes the working directory, and then changes back and cleans up the temp dir after execution.

```python
import unittest
import tempcase

class MyOldTestCase(unittest.TestCase):
    @tempcase.in_tempdir('my_project')
    def test_old_code(self):
        """
        This method has now be ``os.chdir()``'d into a temporary directory which will be cleaned up.
        The working directory will then automatically switch back to whatever it was before.
        The directory's cleanup cannot be prevented.
        """
        open('my_local_file.txt', 'w').close()
    
    _project_name = 'my_project'  # can be defined in the class or passed to the decorator

    @tempcase.in_tempdir
    def test_slightly_newer_code(self):
        pass

```
