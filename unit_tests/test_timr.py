"""
.. module:: timr
   :platform: Unix, Windows
   :synopsis: The module provide the timr tests
.. moduleauthor:: Thibaut Stalin <thibaut.st@gmail.com>
"""
import asyncio
from logging import Logger, getLogger
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

import callee  # type: ignore

from timr.exceptions import AlreadySetTimerIdError, NotSetTimerIdError
from timr.timer import Timer, monitor_function

# pylint: disable=protected-access
# remove mypy line when version 1.0 will be available
# mypy:  disable-error-code=attr-defined

LOGGER = getLogger(__name__)


class TestTimr(TestCase):
    """
    Test the Timr class
    """

    def test_timr_init_no_args(self) -> None:
        """
        Test Timr init without args
        """
        timr = Timer()

        self.assertIsInstance(timr, Timer)

        self.assertEqual(0.1, timr._precision)
        self.assertEqual(True, timr._with_print)
        self.assertEqual(None, timr._logger)
        self.assertEqual({}, timr._timers)

    def test_timr_init_with_args(self) -> None:
        """
        Test Timr init with args
        """
        timr = Timer(0.2, False, LOGGER)

        self.assertEqual(0.2, timr._precision)
        self.assertEqual(False, timr._with_print)
        self.assertEqual(LOGGER, timr._logger)

    def test_timr_init_wrong_args(self) -> None:
        """
        Test Timr init with wrong args
        """
        self.assertRaises(ValueError, Timer, "test")
        self.assertRaises(ValueError, Timer, 0.1, "test")
        self.assertRaises(ValueError, Timer, 0.1, True, "test")

    def test_start_without_args(self) -> None:
        """
        Test Timr start without args
        """
        timr = Timer()

        self.assertTrue(timr._timer_default_id not in timr._timers)

        timr.start()

        self.assertTrue(timr._timer_default_id in timr._timers)

        timr.stop()

        self.assertTrue(timr._timer_default_id not in timr._timers)

    def test_start_with_args(self) -> None:
        """
        Test Timr start with args
        """
        timr = Timer()

        self.assertTrue(len(timr._timers) == 0)

        timr.start("custom_id")

        self.assertTrue("custom_id" in timr._timers)

        timr.stop("custom_id")

        self.assertTrue("custom_id" not in timr._timers)

    def test_start_same_id(self) -> None:
        """
        Test Timr start raise an exception for the same id
        """
        timr = Timer().start("custom_id")

        self.assertRaises(AlreadySetTimerIdError, timr.start, "custom_id")

    @patch("builtins.print")
    def test_start_print_and_log_called(self, mock_print: Mock) -> None:
        """
        Test Timr start call print and log

        :param mock_print: print() mock
        """
        mock_logger = MagicMock(spec=Logger)
        mock_logger.debug = MagicMock()

        Timer(logger=mock_logger).start()

        mock_print.assert_called_with('Timer "default" - start monitoring')
        mock_logger.debug.assert_called_with('Timer "default" - start monitoring')

    @patch("builtins.print")
    def test_start_print_and_log_not_called(self, mock_print: Mock) -> None:
        """
        Test Timr start don't call print and log

        :param mock_print: print() mock
        """
        mock_logger = MagicMock(spec=Logger)
        mock_logger.debug = MagicMock()

        Timer(with_print=False).start()

        mock_print.assert_not_called()
        mock_logger.debug.assert_not_called()

    @patch("builtins.print")
    def test_stop_print_and_log(self, mock_print: Mock) -> None:
        """
        Test Timr stop without args
        """
        mock_logger = MagicMock(spec=Logger)
        mock_logger.debug = MagicMock()

        timr = Timer(logger=mock_logger).start()
        timr.stop()

        mock_print.assert_called_with(callee.String() & callee.Regex('Timer "default" - monitored time: .* seconds'))
        mock_logger.debug.assert_called_with(
            callee.String() & callee.Regex('Timer "default" - monitored time: .* seconds')
        )

    @patch("builtins.print")
    def test_stop_print_and_log_not_called(self, mock_print: Mock) -> None:
        """
        Test Timr stop without args
        """
        mock_logger = MagicMock(spec=Logger)
        mock_logger.debug = MagicMock()

        timr = Timer(with_print=False).start()
        timr.stop()

        mock_print.assert_not_called()
        mock_logger.debug.assert_not_called()

    def test_stop_wrong_id(self) -> None:
        """
        Test Timr stop with the wrong id
        """
        timr = Timer().start("custom_id")

        self.assertRaises(NotSetTimerIdError, timr.stop, "wrong_id")

    @patch("builtins.print")
    def test_decorator(self, mock_print: Mock) -> None:
        """
        Test monitor_function with sync function
        """

        @monitor_function(0.3)
        def test_method(recursive_depth: int) -> None:
            if recursive_depth > 1:
                recursive_depth = recursive_depth - 1
                test_method(recursive_depth)

        test_method(5)

        self.assertEqual(10, mock_print.call_count)

    @patch("builtins.print")
    def test_decorator_async(self, mock_print: Mock) -> None:
        """
        Test monitor_function with async function
        """

        @monitor_function(0.3)
        async def test_method(recursive_depth: int) -> None:
            if recursive_depth > 1:
                recursive_depth = recursive_depth - 1
                await test_method(recursive_depth)

        asyncio.run(test_method(5))

        self.assertEqual(10, mock_print.call_count)
