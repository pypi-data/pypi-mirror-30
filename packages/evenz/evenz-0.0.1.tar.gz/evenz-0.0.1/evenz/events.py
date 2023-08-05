#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 3/25/18
"""
.. currentmodule:: events
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Say something descriptive about the 'events' module.
"""

import inspect
from typing import Any, Callable, Iterable, List, Tuple
from functools import wraps


class Event(object):
    """
    Use events to be notified when a something happens.

    .. seealso::

        While you can instantiate an instance of this class directly, check out the
        :py:func:`event` decorator first.
    """
    def __init__(self, f: Callable):
        self._f = f
        # Grab a reference to this instance's __call__ override.
        _call = self.__call__

        # Create a new call method that wraps the original function so we get its doc string
        # and argument list.
        @wraps(f)
        def call(*args, **kwargs):
            _call(*args, **kwargs)
        self.__call__ = call
        # Create a list to hold the handlers.
        self._handlers = []

    @property
    def function(self) -> Callable:
        """
        Get the original function from which the event was created.

        :return: the original function
        """
        return self._f

    @property
    def handlers(self) -> Iterable[Callable]:
        """
        Get the handlers for this function.

        :return: an iteration of the handlers.
        """
        return iter(self._handlers)

    def subscribe(self, handler: Callable):
        """
        Subscribe a handler function to this event.

        :param handler: the handler

        .. note::

            You can also use the += operator.
        """
        self._handlers.append(handler)

    def unsubscribe(self, handler: Callable):
        """
        Unsubscribe a handler function from this event.

        :param handler: the handler

        .. note::

            You can also use the -= operator.
        """
        self._handlers.remove(handler)

    def __iadd__(self, other):
        # Append handler.
        self._handlers.append(other)
        return self

    def __isub__(self, other):
        # Remove the handler.
        self._handlers.remove(other)
        return self

    def __call__(self, *args, **kwargs):
        # Just call all the handlers.
        for h in self._handlers:
            h(*args, **kwargs)


def observable(cls):
    """
    Use this decorator to mark a class that exposes events.

    :param cls: the class
    :return: the class

    .. seealso::

        If you are using this decorator, you probably also want to use :py:func:`event` on
        some of the methods.
    """
    # For starters, we need the class' original __init__ method.
    cls_init = cls.__init__

    @wraps(cls.__init__)
    def init(self, *args, **kwargs):
        # Call the class' original __init__ method.
        cls_init(self, *args, **kwargs)
        # Retrieve all the methods marked as events.
        event_members: List[Tuple[str, Event]] = [
            member for member in inspect.getmembers(self)
            if isinstance(member[1], Event)
        ]
        for event_member in event_members:
            e = Event(event_member[1].function)
            self.__dict__[event_member[0]] = e
    # Replace the class' original __init__ method with our own.
    cls.__init__ = init
    # The caller gets back the original class.
    return cls


def event(f: Callable) -> Event:
    """
    Decorate a function or method to create an :py:class:`Event`.

    :param f: the function.
    :return: the event

    .. sealso::

        If you are decorating a method within a class, you'll need to use the
        :py:func:`observable` class decorator on the class as well.
    """
    # Create an event for the callable.
    e = Event(f)
    # That should be all we need to do.
    return e
