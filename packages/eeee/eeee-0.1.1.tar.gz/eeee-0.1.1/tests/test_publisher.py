#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from eeee import Publisher, exceptions

__author__ = 'Paweł Zadrożny'
__copyright__ = 'Copyright (c) 2018, Pawelzny'


class TestPublisher(unittest.TestCase):
    def test_name_as_string(self):
        pub = Publisher('test name')
        self.assertEqual(pub.name, 'test name')

    def test_name_as_publisher_instance(self):
        pub = Publisher('clone me?')
        clone = Publisher(pub)

        self.assertEqual(pub.name, clone.name)
        self.assertEqual(pub.id, clone.id)
        self.assertIsNot(pub, clone)

    def test_raise_naming_error(self):
        with self.assertRaises(exceptions.NamingError):
            Publisher(['wrong name'])

    def test_raise_type_error(self):
        with self.assertRaises(exceptions.EeeeTypeError):
            Publisher({'wrong name'})

    def test_raise_eeee_exception(self):
        with self.assertRaises(exceptions.EeeeException):
            Publisher({'wrong name'})

    def test_identification(self):
        pub = Publisher('broadcaster')
        expected_id = "<class 'eeee.event.Publisher'>broadcaster</class>"
        self.assertEqual(pub.id, expected_id)

    def test_comparison_difference(self):
        self.assertNotEqual(Publisher('first'), Publisher('second'))
        self.assertNotEqual(Publisher('first'), 'second')
        self.assertIsNot(Publisher('first'), Publisher('first'))

    def test_comparison_the_same(self):
        self.assertEqual(Publisher('one another'), Publisher('one another'))
        self.assertEqual(Publisher('one another'), 'one another')

    def test_comparison_not_equal(self):
        self.assertNotEqual(Publisher('None'), None)
        self.assertNotEqual(Publisher('123'), 123)
        self.assertNotEqual(Publisher('\'{"dict": true\'}'), {'dict': True})
