"""
.. module:: timr
   :platform: Unix, Windows
   :synopsis: The module provide the timr tests
.. moduleauthor:: Thibaut Stalin <thibaut.st@gmail.com>
"""
import asyncio
from time import sleep
from unittest import TestCase

from timr.timr import Timr, monitor_function


class TestTimr(TestCase):
    """
    Test the Timr class
    """

    def test_timr_init(self) -> None:
        """
        Test Timr init
        """
        timr_print = Timr()

        self.assertIsInstance(timr_print, Timr)

    def test_start(self) -> None:
        """
        Test Timr start
        """
        timr = Timr().start()
        timr.stop()

        timr_with_id = Timr().start("test-id")
        timr_with_id.stop("test-id")

        timr_with_precision = Timr(0.3).start()
        timr_with_precision.stop()

    def test_decorator(self) -> None:
        """
        Test monitor_function
        """

        @monitor_function(0.3)
        def test_method(rec: int) -> None:
            sleep(1)
            if rec > 0:
                rec = rec - 1
                test_method(rec)

        test_method(5)

    def test_decorator_async(self) -> None:
        """
        Test monitor_function
        """

        @monitor_function(0.3)
        async def test_method(rec: int) -> None:
            sleep(1)
            if rec > 0:
                rec = rec - 1
                await test_method(rec)

        asyncio.run(test_method(5))
