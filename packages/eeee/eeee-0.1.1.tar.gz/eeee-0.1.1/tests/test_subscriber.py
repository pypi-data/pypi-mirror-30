#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from cl import Loop

from eeee import exceptions
from eeee.event import Subscriber

__author__ = 'Paweł Zadrożny'
__copyright__ = 'Copyright (c) 2018, Pawelzny'


class TestSubscriberHandler(unittest.TestCase):
    def test_function_handler(self):
        async def foo_handler():
            pass

        sub = Subscriber(foo_handler)
        self.assertIs(sub.handler, foo_handler)

    def test_class_handler(self):
        class FooHandler:
            async def __call__(self):
                pass

        sub = Subscriber(FooHandler())
        self.assertIsInstance(sub.handler, FooHandler)

    def test_subscriber_as_handler(self):
        async def just_handler():
            pass

        sub = Subscriber(just_handler)
        clone = Subscriber(sub)
        self.assertEqual(sub, clone)
        self.assertIsNot(sub, clone)

    def test_raise_not_callable_error(self):
        with self.assertRaises(exceptions.NotCallableError):
            Subscriber('foo')

    def test_not_coroutine_error(self):
        def handler():
            pass

        with self.assertRaises(exceptions.NotCoroutineError):
            Subscriber(handler)

    def test_handler_of_wrong_type(self):
        with self.assertRaises(exceptions.HandlerError):
            Subscriber(tuple)

    def test_not_callable_object_handler(self):
        class NotCallable:
            name = 'test'

        with self.assertRaises(exceptions.HandlerError):
            Subscriber(NotCallable())

    def test_raise_not_error(self):
        with self.assertRaises(exceptions.NotCallableError):
            Subscriber('foo')


class TestSubscriberComparison(unittest.TestCase):
    def test_identification(self):
        async def broadcaster():
            pass

        sub = Subscriber(broadcaster)
        expected_id = "<class 'eeee.event.Subscriber'>broadcaster</class>"
        self.assertEqual(sub.id, expected_id)

    def test_comparison_difference(self):
        async def first():
            pass

        async def second():
            pass

        self.assertNotEqual(Subscriber(first), Subscriber(second))
        self.assertNotEqual(Subscriber(first), second)
        self.assertIsNot(Subscriber(first), Subscriber(first))

    def test_comparison_the_same(self):
        async def simple_handler():
            pass

        self.assertEqual(Subscriber(simple_handler), Subscriber(simple_handler))
        self.assertEqual(Subscriber(simple_handler), 'simple_handler')


class TestSubscriberExecute(unittest.TestCase):
    def test_call_function_handler(self):
        async def test_func(message, publisher, event):
            return [message, publisher, event]

        sub = Subscriber(test_func)
        with Loop(sub('some message', None, 'test')) as loop:
            result = loop.run_until_complete()

        self.assertEqual(result[0], 'some message')
        self.assertIsNone(result[1])
        self.assertEqual(result[2], 'test')

    def test_call_class_handler(self):
        class TestCls:
            async def __call__(self, message, publisher, event):
                return [message, publisher, event]

        sub = Subscriber(TestCls())
        with Loop(sub('some message', None, 'test')) as loop:
            result = loop.run_until_complete()

        self.assertEqual(result[0], 'some message')
        self.assertIsNone(result[1])
        self.assertEqual(result[2], 'test')
