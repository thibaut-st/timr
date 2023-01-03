"""
.. module:: timer
   :platform: Unix, Windows
   :synopsis: The module provide the Timer class
.. moduleauthor:: Thibaut Stalin <thibaut.st@gmail.com>
"""
import inspect
import time
from logging import Logger
from typing import Awaitable, Callable, ParamSpec, Self, TypeAlias, TypeVar

from shortuuid import uuid

from performance_timer.exceptions import AlreadySetTimerIdError, NotSetTimerIdError

# remove mypy lines when version 1.0 will be available
# mypy: disable-error-code="valid-type, attr-defined, type-var"

FunctionParameters = ParamSpec("FunctionParameters")
FunctionReturn = TypeVar("FunctionReturn")

DecoratedFunction: TypeAlias = Callable[FunctionParameters, FunctionReturn | Awaitable[FunctionReturn]]  # type: ignore
Wrapper: TypeAlias = DecoratedFunction
Decorator: TypeAlias = Callable[[DecoratedFunction], Wrapper]


class Timer:
    """
    Monitor time performance
    """

    _timer_default_id = "default"

    def __init__(self, precision: float = 0.1, with_print: bool = True, logger: Logger | None = None):
        """
        Initialize a Timer object

        :param precision: The float precision for the timer display (e.g. 0.1 --> x.y seconds, 0.3 --> x.yyy seconds)
        :param with_print: Should the messages and times be printed in the terminal
        :param logger: Provide a logger to log the times
        """
        if not isinstance(precision, float):
            raise ValueError("The argument `precision` must be a float")
        if not isinstance(with_print, bool):
            raise ValueError("The argument `with_print` must be a boolean")
        if not isinstance(logger, Logger) and logger is not None:
            raise ValueError("The argument `logger` must be a Logger")

        self._precision = precision
        self._with_print = with_print
        self._logger = logger

        # dict[str<timer id>, float<timer perf_counter start>]
        self._timers: dict[str, float] = {}

    def start(self, timer_id: str = _timer_default_id) -> Self:
        """
        Start a new timer

        :param timer_id: A string used as timer id (default id is "default")
        :return: The Timer instance (allow to write timer = Timer().start())
        """
        if timer_id in self._timers:
            raise AlreadySetTimerIdError(f'Timer id "{timer_id}" already exist')

        self._timers[timer_id] = time.perf_counter()
        message = f'Timer "{timer_id}" - start monitoring'

        if self._with_print:
            print(message)
        if self._logger:
            self._logger.debug(message)

        return self

    def stop(self, timer_id: str = _timer_default_id) -> Self:
        """
        Stop the timer, and report the elapsed time (default id is "default")

        :param timer_id: The id provided at start(<timer_id>) call
        :return: The Timer instance
        """
        if timer_id not in self._timers:
            raise NotSetTimerIdError(f"{timer_id} do not exist")

        elapsed_time = time.perf_counter() - self._timers[timer_id]
        message = f'Timer "{timer_id}" - monitored time: {elapsed_time:{self._precision}f} seconds'

        if self._with_print:
            print(message)
        if self._logger:
            self._logger.debug(message)

        del self._timers[timer_id]

        return self


def monitor_function(precision: float = 0.1, with_print: bool = True, logger: Logger | None = None) -> Decorator:
    """
    Decorator factory with parameters matching the Timer class init

     Monitor a function or method time execution (handle both sync and async)

    :param precision: The float precision for the timer display (e.g. 0.1 --> x.y seconds, 0.3 --> x.yyy seconds)
    :param with_print: Should the messages and times be printed in the terminal
    :param logger: Provide a logger to log the times
    :return: The decorator
    """

    def decorator(function: DecoratedFunction) -> Wrapper:
        """
        Decorator

        Generate the right wrapper depending on the sync/async nature of the function or method

        :param function: The function to monitor
        :return: The decorator wrapper
        """

        async def async_wrapper(*args: FunctionParameters.args, **kwargs: FunctionParameters.kwargs) -> FunctionReturn:
            """
            Wrap the async function execution with timers

            :param args: Function args
            :param kwargs: Function kwargs
            :return: Function result
            """
            timer_id = f"{function.__name__} - {uuid()}"

            timer = Timer(precision, with_print, logger).start(timer_id)
            result: FunctionReturn = await function(*args, **kwargs)
            timer.stop(timer_id)

            return result

        def wrapper(*args: FunctionParameters.args, **kwargs: FunctionParameters.kwargs) -> FunctionReturn:
            """
            Wrap the function execution with timers

            :param args: Function args
            :param kwargs: Function kwargs
            :return: Function result
            """
            timer_id = f"{function.__name__} - {uuid()}"

            timer = Timer(precision, with_print, logger).start(timer_id)
            result: FunctionReturn = function(*args, **kwargs)
            timer.stop(timer_id)

            return result

        return async_wrapper if inspect.iscoroutinefunction(function) else wrapper

    return decorator
