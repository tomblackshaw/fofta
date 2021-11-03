"""FOFTA - from one filesystem to another

Created on Oct 16, 2021
@author: Tom Blackshaw

To run a unit test:-
# python3 -m unittest test.test_disktools.test_globals

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import subprocess
import random
import string
import time


def generate_random_string(length):
    """Generate a N-chars-long random alphanumeric string"""
    x = "".join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _ in range(length)
    )
    return x


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
        input_str = ""
    if type(param_lst) not in (list, tuple):
        raise ValueError(
            "call_binary()'s first parameter should be a list or tuple, \
e.g. ['fdisk', '/dev/sda']."
        )
    proc = subprocess.Popen(
        param_lst, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    res_pair = proc.communicate(bytes(input_str, "ascii"))
    to_be_returned = (
        proc.returncode,
        (None if res_pair[0] is None else res_pair[0].decode("UTF-8")),
        (None if res_pair[1] is None else res_pair[1].decode("UTF-8")),
    )
    return to_be_returned



def pause_until_true(timeout, test_func, nudge_func=None):
    """Pause until test_func() returns True. Run tryme_func() every 1s, if specified.

    This subroutine runs test_func() once per second, starting immediately, to see
    if it returns True yet. If it doesn't: (i) wait for one second, (ii) run the
    nudge_func() if it was specified, and (iii) check again. If, after {timeout}
    loops, the condition still isn't True, raise TimeoutError. Otherwise, return.

    Args:
        timeout (int): How many loops (one second each) should we do before raising
            a TimeoutError exception?
        test_func (func): Run this function -- probably a lambda -- to get a result.
            If it returns True, return. Else, loop again.
        nudge_func (func, optional): Run this function after a one-second delay, if
            test_func() returns False.

    Returns:
        None.
    
    Example:
        pause_until_true(timeout=5, test_func = lambda x: os.path.exists(x),
                                nudge_func = lambda: call_binary(['partprobe']))
        
    Raises:
        TimeoutError: After {timeout} seconds, test_func() still is returning False.

    Todo:
        * Add more TODOs

    """
    while timeout > 0 and not test_func():
        timeout = timeout - 1
        time.sleep(1)
        if nudge_func:
            nudge_func()
    if timeout <= 0:
        raise TimeoutError("pause_until_true() timed out")


