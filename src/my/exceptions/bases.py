# -*- coding: utf-8 -*-
"""my.exceptions.bases

Created on Oct 16, 2021
@author: Tom Blackshaw

This module contains the base exceptions that I use. The more specific
subclasses are in my.exceptions, not here. Please do not raise any of
the exceptions listed in this source file.

Todo:
    * Use more of the preexisting exceptions, instead of custom ones,
      wherever possible
    * Make the comments sound less informal

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""


class MyException(Exception):
    """All my custom exceptions are subclasses of MyException.

    Note:
        Wherever possible, I use preexisting exceptions (e.g.
        ValueError). I try to avoid reinventing the wheel.

        Do not raise me. I'm not specifice nough.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.

    """

    def __init__(self, msg, code=None):  # pylint: disable=super-init-not-called
        self.msg = msg
        self.code = code


class MyDisktoolsException(MyException):
    """The custom exceptions related to my.disktools are subclasses of me.

    Note:
        Do not raise me. I'm not specific enough.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.

    """

    def __init__(self, msg, code=None):  # pylint: disable=super-init-not-called
        self.msg = msg
        self.code = code


class MyDisktoolsDiskException(MyDisktoolsException):
    """Custom exceptions related to *disks* are subclasses of me.

    Note:
        Do not raise me. I'm not specific enough.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.

    """

    def __init__(self, msg, code=None):  # pylint: disable=super-init-not-called
        self.msg = msg
        self.code = code


class MyDisktoolsPartitionException(MyDisktoolsException):
    """Custom exceptions related to *partitions* are subclasses of me.

    Note:
        Do not raise me. I'm not specific enough.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.

    """

    def __init__(self, msg, code=None):  # pylint: disable=super-init-not-called
        self.msg = msg
        self.code = code


class PartitionCreationException(MyDisktoolsPartitionException):
    """Custom exceptions for errors relating to the creating of a partition.

    Note:
        Do not raise me. I'm not specific enough.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.

    """

    def __init__(self, msg, code=None):  # pylint: disable=super-init-not-called
        self.msg = msg
        self.code = code


class PartitionModificationException(MyDisktoolsPartitionException):
    """Custom exceptions for errors relating to the modifying of a partition.

    Note:
        Do not raise me. I'm not specific enough.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.

    """

    def __init__(self, msg, code=None):  # pylint: disable=super-init-not-called
        self.msg = msg
        self.code = code


class PartitionDeletionException(MyDisktoolsException):
    """Custom exceptions for errors relating to the deleting of a partition.

    The function delete_partition() raises this exception if the function
    fails to delete the specified partition.

    Note:
        This does not apply to bad parameters. ValueError() is raised
        if the parameters are invalid or unworkable.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.

    """

    def __init__(self, msg, code=None):  # pylint: disable=super-init-not-called
        self.msg = msg
        self.code = code


class MyDisktoolsOtherException(MyDisktoolsException):
    """Miscellaneous my.disktools exceptions are subclasses of me.

    There is a class for partitions and a class for disks. I am
    for my.disktools-related exceptions that are neither disk-related
    nor partition-related... or are perhaps related to both at the
    same time. Either way, those exceptions don't fit neatly into a
    category. That is why they are subclassed from me.

    Note:
        Do not raise me. I'm not specific enough.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.

    """

    def __init__(self, msg, code=None):  # pylint: disable=super-init-not-called
        self.msg = msg
        self.code = code


class MyFructifyException(MyException):
    """Exceptions related directly to the main() fructification loop.

    The __init__ method may be documented in either the class level
    docstring, or as a docstring on the __init__ method itself.

    Either form is acceptable, but the two should not be mixed. Choose one
    convention to document the __init__ method and be consistent with it.

    Note:
        Do not include the `self` parameter in the ``Args`` section.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.

    """

    def __init__(self, msg, code=None):  # pylint: disable=super-init-not-called
        self.msg = msg
        self.code = code
