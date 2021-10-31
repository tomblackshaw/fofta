"""FOFTA - from one filesystem to another

Created on Oct 16, 2021
@author: Tom Blackshaw

To run a unit test:-
# python3 -m unittest test/test_disktools

https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import subprocess
import random
import string

def call_binary(param_lst, input_str=None):
    """Retrieve the disk ID, disk size (bytes and sectors), and sector size.

    This subroutine interrogates the disk device path via fdisk and obtains
    the disk ID (its eight-digit hexadecimal string), its size in bytes,
    its size in disk sectors, and the sector size.

    Args:
        disk_path (:obj:`str`): The /dev entry (e.g. /dev/sda) of the disk_path.

    Returns:
        tuple (
            :obj:`str` - A ten-character string, composed of the
                prefix '0x' and then eight hexadecimal characters, e.g.
                "0x1234ABCD".
            int - The maximum capacity of the disk, in bytes.
            int - The maximum capacity of the disk, in sectors.
            int - The size of each sector, in bytes.
            )

    Example:
        retcode_int, stdout_txt, stderr_txt, stdout_txt = call_binary(['fdisk', '/dev/sda'], '''l
q
''')
    Raises:
        FileNotFoundError: Binary not found.


    Todo:
        * Add more TODOs

    """
    if input_str is None:
        input_str = ''
    if type(param_lst) not in (list, tuple):
        raise ValueError("call_binary()'s first parameter should be a list or tuple, \
e.g. ['fdisk', '/dev/sda'].")
    proc = subprocess.Popen(param_lst, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    res_pair = proc.communicate(bytes(input_str, "ascii"))
    to_be_returned = (proc.returncode, \
                        (None if res_pair[0] is None else res_pair[0].decode('UTF-8')), \
                        (None if res_pair[1] is None else res_pair[1].decode('UTF-8')))
    return to_be_returned







def generate_random_string(length):
    x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))
    return x

