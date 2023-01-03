"""
.. module:: exceptions
   :platform: Unix, Windows
   :synopsis: The module provide the performance_timer custom exceptions
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
