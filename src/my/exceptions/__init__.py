# -*- coding: utf-8 -*-
"""my.exceptions

Created on Oct 16, 2021
@author: Tom Blackshaw

This module contains the custom exceptions that I use. These subclasses
are derived from the less specific base classes in my.exceptions.bases;
please do not raise them. In general, please do not raise any custom
exceptions whose names end in 'Exception'. Ones ending in 'Error' are
fair game.

Todo:
    * Use more of the preexisting exceptions, instead of custom ones,
      wherever possible
    * Make the comments sound less informal

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

from my.exceptions.bases import MyDisktoolsOtherException, \
                                MyDisktoolsDiskException, \
                                MyDisktoolsPartitionException


class PartitionCreationError(MyDisktoolsPartitionException):
    """Raised if an attempt fails to create a partition.

    The function add_partition() raises this exception if the function
    fails to create the specified partition.

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

    def __init__(self, msg, code=None):
        self.msg = msg
        self.code = code


class PartitionDeletionError(MyDisktoolsPartitionException):
    """Raised if an attempt fails to delete a partition.

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

    def __init__(self, msg, code=None):
        self.msg = msg
        self.code = code


class DiskFooError(MyDisktoolsDiskException):
    """QQQExceptions are documented in the same way as classes.

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
        code (int): Exception error code. QQQ

    """

    def __init__(self, msg, code=None):
        self.msg = msg
        self.code = code
