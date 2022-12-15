"""
.. module:: timr
   :platform: Unix, Windows
   :synopsis: The module provide the timr custom exceptions
.. moduleauthor:: Thibaut Stalin <thibaut.st@gmail.com>
"""


class AlreadySetTimerIdError(Exception):
    """
    Raised when a timer id already exist
    """


class NotSetTimerIdError(Exception):
    """
    Raised when a timer id do not exist
    """
