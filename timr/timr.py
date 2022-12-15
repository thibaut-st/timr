"""
.. module:: timr
   :platform: Unix, Windows
   :synopsis: The module provide the Timr class
.. moduleauthor:: Thibaut Stalin <thibaut.st@gmail.com>
"""
import inspect
import time
from logging import Logger
from typing import Callable, Self, Awaitable, TypeAlias, ParamSpec, TypeVar

from shortuuid import uuid

from timr.exceptions import AlreadySetTimerIdError, NotSetTimerIdError

FunctionParameters = ParamSpec("FunctionParameters")
FunctionReturn = TypeVar("FunctionReturn")

DecoratedFunction: TypeAlias = Callable[FunctionParameters, FunctionReturn | Awaitable[FunctionReturn]]
Wrapper: TypeAlias = DecoratedFunction
Decorator: TypeAlias = Callable[[DecoratedFunction], Wrapper]


class Timr:
    """
    Monitor time performance
    """

    _timer_default_id = "default"

    def __init__(self, precision: float = 0.1, with_print: bool = True, logger: Logger | None = None):
        """
        Initialize a Timr object

        :param precision: The float precision for the timer display (e.g. 0.1 --> x.y seconds, 0.3 --> x.yyy seconds)
        :param with_print: Should the messages and times be printed in the terminal
        :param logger: Provide a logger to log the times
        """
        self._precision = precision
        self._with_print = with_print
        self._logger = logger

        self._timers: dict[str, float] = {}

    def start(self, timer_id: str = _timer_default_id) -> Self:
        """
        Start a new timer

        :param timer_id: A string used as timer id
        """
        if timer_id in self._timers:
            raise AlreadySetTimerIdError(f'Timer id "{timer_id}" already exist')

        self._timers[timer_id] = time.perf_counter()
        message = f'Timer "{timer_id}" - start monitoring'

        if self._logger:
            self._logger.debug(message)
        if self._with_print:
            print(message)

        return self

    def stop(self, timer_id: str = _timer_default_id) -> Self:
        """
        Stop the timer, and report the elapsed time

        :param timer_id: The string provided at instantiation or start() call
        """
        if timer_id not in self._timers:
            raise NotSetTimerIdError(f"{timer_id} do not exist")

        elapsed_time = time.perf_counter() - self._timers[timer_id]
        message = f'Timer "{timer_id}" - monitored time: {elapsed_time:{self._precision}f} seconds'

        if self._logger:
            self._logger.debug(message)
        if self._with_print:
            print(message)

        del self._timers[timer_id]

        return self


def monitor_function(precision: float = 0.1, with_print: bool = True, logger: Logger | None = None) -> Decorator:
    """
    Decorator with parameters matching the Timr class init - Monitor a function or method time execution

    :param precision: The float precision for the timer display (e.g. 0.1 --> x.y seconds, 0.3 --> x.yyy seconds)
    :param with_print: Should the messages and times be printed in the terminal
    :param logger: Provide a logger to log the times
    :return: The decorator
    """

    def decorator(function: DecoratedFunction) -> Wrapper:
        """
        Decorator - Monitor a function or method time execution

        :param function: The function to monitor
        :return: The decorator wrapper
        """

        async def async_wrapper(*args: FunctionParameters.args, **kwargs: FunctionParameters.kwargs) -> FunctionReturn:
            """
            Wrap the async function execution with timers

            :param args: function args
            :param kwargs: function kwargs
            :return: function result
            """
            timer_id = f"{function.__name__} - {uuid()}"

            timr = Timr(precision, with_print, logger).start(timer_id)
            result: FunctionReturn = await function(*args, **kwargs)
            timr.stop(timer_id)

            return result

        def wrapper(*args: FunctionParameters.args, **kwargs: FunctionParameters.kwargs) -> FunctionReturn:
            """
            Wrap the function execution with timers

            :param args: function args
            :param kwargs: function kwargs
            :return: function result
            """
            timer_id = f"{function.__name__} - {uuid()}"

            timr = Timr(precision, with_print, logger).start(timer_id)
            result: FunctionReturn = function(*args, **kwargs)
            timr.stop(timer_id)

            return result

        if inspect.iscoroutinefunction(function):
            return async_wrapper
        return wrapper

    return decorator