#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import asyncio
from cl import Loop

__author__ = 'Paweł Zadrożny'
__copyright__ = 'Copyright (c) 2018, Pawelzny'


async def wait_for_it(wait):
    await asyncio.sleep(wait)
    return 'success with wait {}'.format(wait)


class TestLoop(unittest.TestCase):
    def tearDown(self):
        asyncio.get_event_loop().close()

    def test_get_existing_event_loop(self):
        existing_loop = asyncio.new_event_loop()
        loop = Loop._get_event_loop(existing_loop)
        self.assertIs(loop, existing_loop)

    def test_gather_futures(self):
        loop = Loop()
        self.assertIsNone(loop.futures)

        loop.gather(wait_for_it(0.001), wait_for_it(0.001))
        self.assertIsInstance(loop.futures, asyncio.Future)
        loop.run_until_complete()

    def test_gather_single_future(self):
        loop = Loop()
        self.assertIsNone(loop.futures)

        loop.gather(wait_for_it(0.001))
        self.assertIsInstance(loop.futures, asyncio.Future)
        loop.run_until_complete()

    def test_auto_gather_through_constructor(self):
        loop = Loop(wait_for_it(0.001), wait_for_it(0.001))
        self.assertIsInstance(loop.futures, asyncio.Future)
        loop.run_until_complete()

    def test_auto_gather_single_through_constructor(self):
        loop = Loop(wait_for_it(0.001), wait_for_it(0.001))
        self.assertIsInstance(loop.futures, asyncio.Future)
        loop.run_until_complete()

    def test_run_loop_with_futures(self):
        with Loop(wait_for_it(0.005), wait_for_it(0.002)) as loop:
            result = loop.run_until_complete()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 'success with wait 0.005')
        self.assertEqual(result[1], 'success with wait 0.002')

    def test_run_loop_with_single_future(self):
        with Loop(wait_for_it(0.003)) as loop:
            result = loop.run_until_complete()

        self.assertEqual(result, 'success with wait 0.003')

    def test_cancel_within_coro(self):
        async def nuke_loop():
            return loop.cancel()

        loop = Loop()
        loop.gather(nuke_loop())

        with loop as lo:
            result = lo.run_until_complete()

        self.assertIsNone(result)

    def test_return_exception_as_result(self):
        exc = Exception('fail')

        async def raise_exc():
            raise exc

        with Loop(raise_exc(), return_exceptions=True) as loop:
            result = loop.run_until_complete()

        self.assertEqual(result, exc)

    def test_raise_exception_instead_of_result(self):
        async def raise_exc():
            raise Exception

        with self.assertRaises(Exception):
            with Loop(raise_exc()) as loop:
                loop.run_until_complete()
