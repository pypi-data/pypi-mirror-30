#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from cl import Loop

from eeee import Event, Publisher, subscribe

__author__ = 'Paweł Zadrożny'
__copyright__ = 'Copyright (c) 2018, Pawelzny'


class TestSubscribe(unittest.TestCase):
    def test_standalone_decorator(self):
        event = Event('sub standalone')
        self.assertEqual(len(event.pub_sub), 0)

        @subscribe(event)
        async def simple_handler():
            return 'simple_handler'

        self.assertEqual(len(event.pub_sub), 1)
        self.assertIsNone(event.pub_sub[0].publisher)
        self.assertIs(event.pub_sub[0].subscriber, simple_handler)

    def test_standalone_decorator_with_set_publisher(self):
        event = Event('sub to specific publisher')
        self.assertEqual(len(event.pub_sub), 0)

        @event.subscribe(publisher='specific')
        async def nice_handler():
            return 'nice_handler'

        self.assertEqual(len(event.pub_sub), 1)
        self.assertEqual(event.pub_sub[0].publisher, 'specific')
        self.assertEqual(event.pub_sub[0].publisher, Publisher('specific'))
        self.assertIs(event.pub_sub[0].subscriber, nice_handler)

    def test_decorator_attached_to_event(self):
        event = Event('builtin decorator')
        self.assertEqual(len(event.pub_sub), 0)

        @event.subscribe()
        async def better_handler():
            return 'better_handler'

        self.assertEqual(len(event.pub_sub), 1)
        self.assertIsNone(event.pub_sub[0].publisher)
        self.assertIs(event.pub_sub[0].subscriber, better_handler)

    def test_unsubscribe(self):
        event = Event('unsubscribe me')

        # noinspection PyShadowingNames,PyUnusedLocal
        @event.subscribe()
        async def i_will_do_it(message, publisher, event):
            return ['received', publisher, event]

        self.assertEqual(len(event.pub_sub), 1)

        event.unsubscribe(i_will_do_it)
        self.assertEqual(len(event.pub_sub), 0)

    def test_unsubscribe_with_publisher(self):
        event = Event('unsubscribe nuke')

        # noinspection PyShadowingNames,PyUnusedLocal
        @event.subscribe(Publisher('nuke'))
        async def i_feel_no_regret(message, publisher, event):
            return ['received', publisher, event]

        self.assertEqual(len(event.pub_sub), 1)

        event.unsubscribe(i_feel_no_regret, Publisher('nuke'))
        self.assertEqual(len(event.pub_sub), 0)


class TestPublishMessage(unittest.TestCase):
    def test_publish_to_all(self):
        event = Event('publish to all')

        # noinspection PyShadowingNames,PyUnusedLocal
        @event.subscribe()
        async def first_all(message, publisher, event):
            return [message, publisher, event]

        # noinspection PyShadowingNames,PyUnusedLocal
        @event.subscribe()
        async def second_all(message, publisher, event):
            return [message, publisher, event]

        with Loop(event.publish('test message')) as loop:
            result = loop.run_until_complete()

        self.assertEqual(len(result), 2)
        for r in result:
            self.assertEqual(r[0], 'test message')
            self.assertIsNone(r[1])
            self.assertEqual(r[2], 'publish to all')

    def test_publish_to_specific(self):
        event = Event('publish to secret')

        # noinspection PyShadowingNames,PyUnusedLocal
        @event.subscribe(publisher='omit')
        async def first_sp(message, publisher, event):
            return ['omitted', publisher, event]

        # noinspection PyShadowingNames,PyUnusedLocal
        @event.subscribe(publisher='secret')
        async def second_sp(message, publisher, event):
            return ['received', publisher, event]

        with Loop(event.publish('secret message', Publisher('secret'))) as loop:
            result = loop.run_until_complete()

        self.assertEqual(len(result), 1)
        result = result.pop()
        self.assertEqual(result[0], 'received')
        self.assertEqual(result[1], Publisher('secret'))
        self.assertEqual(result[2], 'publish to secret')

    def test_publish_to_all_but_specific(self):
        event = Event('publish to all but omit')

        # noinspection PyShadowingNames,PyUnusedLocal
        @event.subscribe(publisher=Publisher('omit'))
        async def first_sp(message, publisher, event):
            return ['omitted', publisher, event]

        # noinspection PyShadowingNames,PyUnusedLocal
        @event.subscribe()
        async def second_sp(message, publisher, event):
            return ['received', publisher, event]

        with Loop(event.publish('secret message', Publisher('broadcast'))) as loop:
            result = loop.run_until_complete()

        self.assertEqual(len(result), 1)
        result = result.pop()
        self.assertEqual(result[0], 'received')
        self.assertEqual(result[1], Publisher('broadcast'))
        self.assertEqual(result[2], 'publish to all but omit')

    def test_publish_to_empty_event(self):
        event = Event('I am empty inside :(')

        self.assertEqual(len(event.pub_sub), 0)

        with Loop(event.publish('enter the void')) as loop:
            result = loop.run_until_complete()

        self.assertListEqual(result, [])

    def test_publish_on_disabled_event(self):
        event = Event('disabled')
        event.disable()

        # noinspection PyShadowingNames
        @event.subscribe()
        async def funny_handler(message, publisher, event):
            return [message, publisher, event]

        with Loop(event.publish('sad message')) as loop:
            result = loop.run_until_complete()

        self.assertIsNone(result)
