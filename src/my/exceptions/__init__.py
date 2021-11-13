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

from my.exceptions.bases import (
    PartitionCreationException,
    PartitionModificationException,
    PartitionDeletionException,
    MyDisktoolsOtherException, MyFructifyException,
)


class PartitionsOverlapError(PartitionCreationException):
    """Raised if a partition failed to be created because of overlap.

    If *creating* a partition would cause an overlapping of the two
    partitions (the new one and an older one), *or* if two or more
    partitions *already* overlap, raise this exception.

    Note:
        None.

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


class ExistentPriorPartitionError(PartitionCreationException):
    """Raised if a partition already exists and therefore cannot be created..

    Note:
        None.

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


class MissingPriorPartitionError(PartitionCreationException):
    """Raised if a missing partition means I can't create this one.

    For example, I cannot create partition #3 unless partition #2
    already exists. I mean, perhaps I could try, but I refuse to.

    Note:
        None.

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


class StartEndAssBackwardsError(PartitionCreationException):
    """Raised if the start and end values appear to be backwards.

    The first sector must be before the last, obviously. So, if
    the programmer supplies values that appear to have been
    transposed, I'll complain.

    Note:
        None.

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


class WeNeedAnExtendedPartitionError(PartitionCreationException):
    """Raised if you try to create a logical partition w/o an extended one.

    It isn't possible to create a logical partition unless there's an extended
    partition for it to love in. So, if you try, you'll fail. I'll see to it.

    Note:
        None.

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


class PartitionWasNotCreatedError(PartitionCreationException):
    """Raised if the partition was missing after we 'created' it.

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


# class NonspecificPartitionCreationError(PartitionCreationException):
#     """Raised if the partition can't be created.
#
#     ...and if we don't know why.
#
#     Note:
#         This does not apply to bad parameters. ValueError() is raised
#         if the parameters are invalid or unworkable.
#
#     Args:
#         msg (str): Human readable string describing the exception.
#         code (:obj:`int`, optional): Error code.
#
#     Attributes:
#         msg (str): Human readable string describing the exception.
#         code (int): Exception error code.
#
#     """
#
#     def __init__(self, msg, code=None):
#         self.msg = msg
#         self.code = code


class PartitionDeletionError(PartitionDeletionException):
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

    def __init__(self, msg, code=None):  # pylint: disable=super-init-not-called
        self.msg = msg
        self.code = code


class PartitionModificationError(PartitionModificationException):
    """Raised if an attempt fails to modify a partition.

    This exception is raised if a function fails to delete the
    specified partition.

    Note:
        This does not apply to bad parameters. ValueError() is
        raised if the parameters are invalid or unworkable.

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


class PartitionAttributeReadFailureError(PartitionModificationError):
    """Raised if a subroutine failed to read an attribute of a specific partition.

    This isn't used widely. It is a low-level error.

    Note:
        None.

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


class PartitionAttributeWriteFailureError(PartitionModificationError):
    """Raised if a subroutine failed to write an attribute of a specific partition.

    This isn't used widely. It is a low-level error.

    Note:
        None.

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


class PartitionTableReorderingError(PartitionModificationError):
    """Raised if fdisk failed to sort the partition table.

    This isn't used widely. It is a low-level error.

    Note:
        None.

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


class PartitionTableCannotReadError(PartitionModificationError):
    """Raised if we cannot read/interrogate partition table.

    This isn't used widely. It is a low-level error.

    Note:
        None.

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


class SernoSettingFailureError(MyDisktoolsOtherException):
    """Raised if set_serno() failed to set the serial number of the disk.

    Note:
        None.

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





class FructifyPreparationException(MyFructifyException):
    """Do not raise me.

    Note:
        None.

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


class UnpopulatedWorkingCopyCreationException(FructifyPreparationException):
    """Do not raise me.

    Note:
        None.

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




class BlankFileCreationError(UnpopulatedWorkingCopyCreationException):
    """Failed to write big file of N MB of blank data to a temp file.

    Note:
        None.

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



class DestinationDeviceTooSmallError(UnpopulatedWorkingCopyCreationException):
    """Failed to copy the temp image file to the real destination image.

    Note:
        None.

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



class DestinationImageWriteError(UnpopulatedWorkingCopyCreationException):
    """Failed to move/rename the temp image file to/as the real destination file.

    Note:
        None.

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


class FilesystemCopyError(UnpopulatedWorkingCopyCreationException):
    """Failed to copy files from source to destination.

    Note:
        None.

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



class MBRCopyError(UnpopulatedWorkingCopyCreationException):
    """Failed to copy the master boot record (including boot sector) across.

    Note:
        None.

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



class DestinationPaddingWriteError(UnpopulatedWorkingCopyCreationException):
    """Failed to pad out the destination image and make it the right size.

    Note:
        None.

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




class FilesystemFormattingError(UnpopulatedWorkingCopyCreationException):
    """Failed to pad out the destination image and make it the right size.

    Note:
        None.

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



