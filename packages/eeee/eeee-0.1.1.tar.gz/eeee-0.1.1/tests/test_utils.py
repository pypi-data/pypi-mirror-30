#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from eeee import exceptions
from eeee.event import _is_coro, _is_callable, Subscriber, _parse_handler

__author__ = 'Paweł Zadrożny'
__copyright__ = 'Copyright (c) 2018, Pawelzny'


class TestUtils(unittest.TestCase):
    def test_is_coro(self):
        async def i_am_coro():
            pass

        self.assertIsNone(_is_coro(i_am_coro))

    def test_raises_is_not_coro(self):
        def i_am_not_coro():
            pass

        with self.assertRaises(exceptions.NotCoroutineError):
            _is_coro(i_am_not_coro)

    def test_raises_on_not_callable_obj(self):
        class NotCallable:
            pass

        with self.assertRaises(exceptions.NotCoroutineError):
            _is_coro(NotCallable())

    def test_is_callable(self):
        async def i_am_callable():
            pass

        def i_am_callable_too():
            pass

        class IamCallable:
            def __call__(self):
                pass

        self.assertIsNone(_is_callable(i_am_callable))
        self.assertIsNone(_is_callable(i_am_callable_too))
        self.assertIsNone(_is_callable(IamCallable()))

    def test_parse_handler_sub(self):
        async def some_coro():
            pass

        sub = Subscriber(some_coro)

        name, handler = _parse_handler(sub)
        self.assertEqual(name, 'some_coro')
        self.assertIs(handler, some_coro)

    def test_parse_handler_coro(self):
        async def other_coro():
            pass

        name, handler = _parse_handler(other_coro)
        self.assertEqual(name, 'other_coro')
        self.assertIs(handler, other_coro)

    def test_parse_handler_callable_obj(self):
        class Coro:
            def __call__(self):
                pass

        coro = Coro()

        name, handler = _parse_handler(coro)
        self.assertEqual(name, 'Coro')
        self.assertIs(handler, coro)
