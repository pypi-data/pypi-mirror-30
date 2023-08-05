#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from collections import namedtuple
from inspect import iscoroutinefunction
from typing import Any, Union

from eeee import exceptions

__author__ = 'Paweł Zadrożny'
__copyright__ = 'Copyright (c) 2018, Pawelzny'


def subscribe(event: "Event", publisher: Union["Publisher", str] = None):
    """Decorator function which subscribe callable to event.

    :Example:

    .. code-block:: python

        >>> my_event = Event('MyEvent')
        >>> @subscribe(my_event, publisher='incoming webhook')
        ... async def incoming_webhook_handler(message, publisher, event):
        ...    pass # doo something
        ...

    :param event: Event Event object
    :type event: eeee.event.Event
    :param publisher: Optional name or instance of Publisher
    :type publisher: eeee.event.Publisher, str
    :return: decorator wrapper
    """
    if publisher is not None:
        publisher = Publisher(publisher)

    def wrapper(subscriber: callable):
        """Register subscriber to event.

        :param subscriber: Async function or class with async __call__ method
        :type subscriber: eeee.event.Subscriber, callable
        :return: subscriber
        """
        subscriber = Subscriber(subscriber)
        # noinspection PyProtectedMember
        event._reg_sub(subscriber, publisher)
        return subscriber

    return wrapper


class Event:
    """Async event emitter.

    Register subscribers to this event and publish message asynchronously.

    :Example:

    .. code-block:: python

        >>> my_event = Event('MyEvent')
        >>> result = await my_event.publish({'message': 'secret'})

    Result will contain list with values returned by handlers.

    :param name: Optional Event name. If empty will be assigned to name of Class.
    :type name: eeee.event.Event, str
    :raises eeee.exceptions.NamingError: Naming error
    """

    RETURN_EXCEPTIONS = False
    """If set to True will return handler's exception as result instead of raise it."""

    _PubSub = namedtuple('PubSub', ['subscriber', 'publisher'])

    def __init__(self, name: Union["Event", str] = None):
        if name is None:
            name = self.__class__.__name__
        elif isinstance(name, self.__class__):
            name = name.name
        elif type(name) is not str:
            raise exceptions.NamingError(types=[self.__class__, str], wrong=str(type(name)))

        self.name = name
        self.pub_sub = tuple()
        self.__is_enable = True

    @property
    def is_enable(self):
        """Check if Event emitter is enabled.

        :return: Boolean
        """
        return self.__is_enable

    async def publish(self, message: Any, publisher: Union["Publisher", str] = None):
        """Propagate message to all interested in subscribers.

        If publisher is not set, then broadcast is meant for all subscribers.
        Any subscriber can listen to all or only to one publisher within event.

        :Example:

        Secret message will be passed to handlers which listen to 'secret publisher'
        or to handlers which set publisher to None (default)

        .. code-block:: python

            >>> my_event = Event('MyEvent')
            >>> result = await my_event.publish({'message': 'secret'},
            ...                                 Publisher('secret publisher'))

        When publisher is set to None, message will be passed only to
        handlers which set publisher to None (default)

        .. code-block:: python

            >>> broadcast = Event('Broadcast')
            >>> result = await broadcast.publish({'message': 'non secret'})

        :param message: Literally anything.
        :type message: Any
        :param publisher: Optional name or instance of Publisher
        :type publisher: eeee.event.Publisher, str
        :return: List of results from subscribed handlers or None if event is disabled.
        """
        if not self.is_enable:
            return None

        publisher = Publisher(publisher) if publisher else publisher

        coros = []
        for ps in self.pub_sub:
            if ps.publisher is None or (publisher is not None and ps.publisher == publisher):
                coros.append(ps.subscriber(message, publisher, event=self.name))
        return await asyncio.gather(*coros, return_exceptions=self.RETURN_EXCEPTIONS)

    def subscribe(self, publisher: Union["Publisher", str] = None):
        """Subscribe decorator integrated within Event object.

        :Example:

        .. code-block:: python

            >>> my_event = Event('MyEvent')
            >>> @my_event.subscribe(publisher='incoming_webhook')
            ... async def incoming_webhook_handler(message, publisher, event):
            ...     pass # doo something

        Subscribe method must be called to decorate handler.

        :param publisher: Optional name or instance of Publisher
        :type publisher: eeee.event.Publisher, str
        :return: subscribe decorator
        """
        return subscribe(self, publisher)  # delegate to subscribe decorator

    def unsubscribe(self, subscriber: Union["Subscriber", callable],
                    publisher: Union["Publisher", str] = None):
        """Unsubscribe subscribed handler from event.

        If publisher had been set on subscribe, then must be provided as well.

        :Example:

        .. code-block:: python

            >>> my_event = Event('MyEvent')
            >>> my_event.unsubscribe(event_handler, 'secret publisher')

        :param subscriber: Async function or class with async __call__ method
        :type subscriber: eeee.event.Subscriber, callable
        :param publisher: Optional name or instance of Publisher
        :type publisher: eeee.event.Publisher, str
        """
        subscriber = Subscriber(subscriber)
        if publisher is not None:
            publisher = Publisher(publisher)
        pub_sub = self._PubSub(subscriber=subscriber, publisher=publisher)
        self.pub_sub = tuple(ps for ps in self.pub_sub if ps != pub_sub)

    def enable(self):
        """Enable event.

        Idempotent method which set Event as enabled.

        :return: self
        """
        self.__is_enable = True
        return self

    def disable(self):
        """Disable event.

        Idempotent method which set Event as disabled.

        :return: self
        """
        self.__is_enable = False
        return self

    def toggle(self):
        """Toggle event enable-disable.

        Change state of Event to opposite.

        :return: self
        """
        self.__is_enable = not self.__is_enable
        return self

    def _reg_sub(self, subscriber: Union["Subscriber", callable],
                 publisher: Union["Publisher", str] = None):
        """Append subscriber to list of subscribers.

        :param subscriber: Async function or class with async __call__ method
        :type subscriber: eeee.event.Subscriber, callable
        :param publisher: Optional name or instance of Publisher
        :type publisher: eeee.event.Publisher, str
        """
        self.pub_sub += (self._PubSub(subscriber=subscriber, publisher=publisher),)


class Publisher:
    """Event publisher.

    Publisher is a wrapper which provides unified interface.
    Instead of using plain strings which may be error prone,
    It is recommended to use Publisher instance.

    Two instances of the same name are considered equal but not the same.
    Publisher is not a singleton.

    :Example:

    Create publisher and use multiple times or in case of import clash
    create new instance of the same name

    .. code-block:: python

        >>> broadcaster = Publisher('Broadcaster')
        >>> broadcaster_clone = Publisher('Broadcaster')
        >>> broadcaster == broadcaster_clone
        True

        >>> broadcaster == 'Broadcaster'
        True

        >>> broadcaster is broadcaster_clone
        False

    One instance may be input for new one which creates a copy

    .. code-block:: python

        >>> fancy = Publisher('Fancy')
        >>> fancy_clone = Publisher(fancy)
        >>> fancy is fancy_clone
        False

        >>> fancy.name == fancy_clone.name
        True

    :param name: Name of Publisher
    :type name: eeee.event.Publisher, str
    """

    def __init__(self, name: Union["Publisher", str]):
        if isinstance(name, self.__class__):
            name = name.name
        elif type(name) is str:
            name = name
        else:
            raise exceptions.NamingError(types=[self.__class__, str], wrong=str(type(name)))
        self.name = name
        self.__template = str(self.__class__) + '{name}</class>'
        self.__id = self.__template.format(name=self.name)

    def __str__(self):
        return str(self.id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        if type(other) is str:
            return self.id == self.__template.format(name=other)
        return False

    @property
    def id(self) -> str:
        """Publisher identification.

        :return: string ID
        :rtype: str
        """
        return self.__id


class Subscriber:
    """Event subscriber.

    Subscriber is a wrapper which provides unified interface.
    Instead of using event handlers directly which may be error prone,
    It is recommended to use Subscriber instance.

    Subscriber is not meant to be used outside of Event context.

    Two instances of the same name are considered equal but not the same.
    Subscriber is not a singleton.

    :Example:

    .. code-block:: python

        >>> async def default_handler(message, publisher, event):
        ...     pass
        ...
        >>> sub = Subscriber(default_handler)
        >>> sub_clone = Subscriber(default_handler)
        >>> sub == 'default_handler'
        True

        >>> sub == sub_clone
        True

        >>> sub is sub_clone
        False

        >>> result = await sub('a message', Publisher('global'), 'mock event')


    :param handler: Async function or class with async __call__ method
    :type handler: eeee.event.Subscriber, callable
    """

    def __init__(self, handler: Union["Subscriber", callable]):
        self.name, self.handler = _parse_handler(handler)

        # handler validation
        _is_callable(self.handler)
        _is_coro(self.handler)

        self.__template = str(self.__class__) + '{name}</class>'
        self.__id = self.__template.format(name=self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        if type(other) is str:
            return self.id == self.__template.format(name=other)
        return False

    async def __call__(self, message, publisher, event):
        return await self.handler(message=message, publisher=publisher, event=event)

    @property
    def id(self):
        """Subscriber identification.

        :return: string ID
        :rtype: str
        """
        return self.__id


def _parse_handler(handler: Union[callable, object, Subscriber]):
    """Parse handler name and body.

    Function accept functions, callable object and instance of Subscriber.
    If Subscriber has been given, parser will extract its name and handler.

    :param handler: Function or callable object.
    :type handler: callable, object
    :return: Name and handler tuple
    :rtype: tuple
    """
    if isinstance(handler, Subscriber):
        return handler.name, handler.handler

    try:
        name = handler.__name__
    except AttributeError:
        # assume instance of callable object
        name = handler.__class__.__name__

    return name, handler


def _is_callable(handler: Union[callable, object]):
    """Check if handler is callable.

    :param handler: Function or callable object.
    :type handler: callable, object
    :raises eeee.exception.NotCallableError: Not callable error
    :return: None
    """
    if not callable(handler):
        raise exceptions.NotCallableError


def _is_coro(handler: Union[callable, object]):
    """Check if handler is coroutine.

    Class with async __call__ method is considered a coroutine.

    :param handler: Function or callable object.
    :type handler: callable, object
    :raises eeee.exceptions.NotCoroutineError: Not coroutine error
    :return: None
    """
    try:
        is_coro = iscoroutinefunction(handler) or iscoroutinefunction(handler.__call__)
    except AttributeError:
        is_coro = False

    if not is_coro:
        raise exceptions.NotCoroutineError
