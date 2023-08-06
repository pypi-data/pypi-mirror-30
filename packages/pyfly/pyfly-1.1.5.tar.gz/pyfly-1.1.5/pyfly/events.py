#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class EventHook(object):
    """
    Simple event class used to provide hooks for different types of events

    Here's how to use the EventHook class::

        my_event = EventHook()
        def on_my_event(a, b, **kw):
            print "Event was fired with arguments: %s, %s" % (a, b)
        my_event += on_my_event
        my_event.fire(a="foo", b="bar")
    """

    def __init__(self):
        self._handlers = []

    def __iadd__(self, handler):
        self._handlers.append(handler)
        return self

    def __isub__(self, handler):
        self._handlers.remove(handler)
        return self

    def fire(self, *args,**kwargs):
        for handler in self._handlers:
            handler(*args, **kwargs)

task_success = EventHook()
task_fail = EventHook()

    
