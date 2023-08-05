#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Paweł Zadrożny'
__copyright__ = 'Copyright (c) 2018, Pawelzny'


class EeeeException(Exception):
    """Root package exception.

    All other exceptions are derived from this one.
    """

    message = 'Unexpected usage of "eeee" module.'
    """General "eeee" exception message."""


class EeeeTypeError(EeeeException):
    """General type related exception.

    All other exceptions related to Type are derived from this one.
    """

    message = 'Argument type error.'
    """Type mismatch "eeee" exception message."""


class NamingError(EeeeTypeError):
    """Name type error exceptions.

    Raised when name argument type is not allowed.
    """

    message = 'Argument "name" type mismatch.'
    """Naming error message."""

    def __init__(self, message: str = None, types: list = None, wrong: str = None):
        if message is not None:
            self.message = message
        elif types and wrong:
            self.message = ('{message} Must be one of type: {types}, '
                            'got {wrong} instead.'.format(message=self.message,
                                                          types=types,
                                                          wrong=wrong))
        super().__init__(self.message)


class HandlerError(EeeeTypeError):
    """Root Exception for handler type errors."""

    message = 'Argument "handler" type mismatch.'
    """Handler error message."""

    def __init__(self, message: str = None):
        if message is not None:
            self.message = message
        super().__init__(self.message)


class NotCallableError(HandlerError):
    """Leaf of HandlerError, raised when wrong type of handler has been provided."""

    message = 'Argument "handler" must be function or class with __call__ method.'
    """Handler type mismatch message."""


class NotCoroutineError(HandlerError):
    """Leaf of HandlerError, raised when handler is not coroutine."""

    message = 'Argument "handler" must be coroutine.'
    """Handler type mismatch message."""
