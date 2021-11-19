"""pyfuncbuffer.py - A library for buffering function calls.

Copyright (C) 2021 Jupsista

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import time
from multiprocessing import Queue, Process
from threading import Thread
import pytest

from pyfuncbuffer.pyfuncbuffer import buffer


# A function shouldn't buffer if it is called only once
def test_buffer_on_same_arguments_once():
    @buffer(0.1, buffer_on_same_arguments=True)
    def normal_function(arg1):
        return time.time()

    now = time.time()
    time1 = normal_function("foo")
    assert(now + 0.05 > time1)


# The second function call should be buffered
def test_buffer_on_same_arguments_twice():
    @buffer(0.1, buffer_on_same_arguments=True)
    def normal_function(arg1):
        return time.time()

    time1 = normal_function("foo")
    time2 = normal_function("foo")

    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# The second function call shouldn't be buffered
def test_buffer_on_same_arguments_normal_function_with_sleep():
    @buffer(0.1, buffer_on_same_arguments=True)
    def normal_function(arg1):
        return time.time()

    normal_function("foo")
    time.sleep(0.1)
    now = time.time()
    time1 = normal_function("foo")  # This shouldn't be buffered since we slept

    assert(now + 0.05 > time1)


# Functions should have their own buffers
def test_buffer_on_same_arguments_many_functions():
    @buffer(0.1, buffer_on_same_arguments=True)
    def normal_function1(arg1):
        return time.time()

    @buffer(0.1, buffer_on_same_arguments=True)
    def normal_function2(arg1):
        return time.time()

    time1 = normal_function1("foo")
    time2 = normal_function1("foo")
    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)

    now = time.time()
    time1 = normal_function2("foo")
    # This shouldn't be buffered
    assert(now + 0.05 > time1)
    time2 = normal_function2("foo")
    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# Using different arguments shouldn't buffer
def test_buffer_on_same_arguments_different_args():
    @buffer(0.1, buffer_on_same_arguments=True)
    def normal_function(arg1):
        return time.time()

    now = time.time()
    normal_function("test_arg")
    time1 = normal_function("different_test_arg")
    assert(now + 0.05 > time1)


# Using different arguments shouldn't buffer even with
# other arguments used in between
def test_buffer_on_same_arguments_different_args_many():
    @buffer(0.1, buffer_on_same_arguments=True)
    def normal_function(arg1):
        return time.time()

    now = time.time()
    normal_function("foo")
    normal_function("bar")
    time1 = normal_function("baz")
    assert(now + 0.05 > time1)


def test_buffer_on_same_arguments_different_args_and_kwargs():
    @buffer(0.1, buffer_on_same_arguments=True)
    def normal_function(arg1, arg2):
        return time.time()

    now = time.time()
    time1 = normal_function("foo", arg2="bar")
    time2 = normal_function("foo", arg2="baz")  # Shouldn't get buffered
    assert(now + 0.05 > time2)
    time2 = normal_function("foo", arg2="bar")  # Should get buffered
    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# A class function shouldn't buffer if it is called only once
def test_buffer_on_same_arguments_class_function_once():
    class Class:
        @buffer(0.1, buffer_on_same_arguments=True)
        def class_function(self, arg1):
            return time.time()

    instance = Class()

    now = time.time()
    time1 = instance.class_function("foo")

    assert(now + 0.05 > time1)


# Classes should have their own buffers
def test_buffer_on_same_arguments_many_instance_methods():
    class Class1:
        @buffer(0.1, buffer_on_same_arguments=True)
        def instance_method(self, arg1):
            return time.time()

    class Class2:
        @buffer(0.1, buffer_on_same_arguments=True)
        def instance_method(self, arg1):
            return time.time()

    instance1 = Class1()
    instance2 = Class2()

    time1 = instance1.instance_method("foo")
    time2 = instance1.instance_method("foo")

    assert(time2 - time1 > 0.1)

    now = time.time()
    time1 = instance2.instance_method("foo")
    # This shouldn't be buffered
    assert(now + 0.05 > time1)
    time2 = instance2.instance_method("foo")
    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


def test_buffer_on_same_arguments_random_delay_twice():
    @buffer(0, random_delay=(0.1, 0.1), buffer_on_same_arguments=True)
    def normal_function(arg1):
        return time.time()

    time1 = normal_function("foo")
    time2 = normal_function("foo")
    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# A function shouldn't buffer if it is called only once
def test_normal_function_once():
    @buffer(0.1)  # Buffer by 0.1 seconds
    def normal_function():
        return time.time()

    now = time.time()
    time1 = normal_function()
    assert(now + 0.05 > time1)


# The second function call should be buffered
def test_normal_function_twice():
    @buffer(0.1)
    def normal_function():
        return time.time()

    time1 = normal_function()
    time2 = normal_function()

    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# The second function call should be buffered
def test_normal_function_with_sleep():
    @buffer(0.1)
    def normal_function():
        return time.time()

    normal_function()
    time.sleep(0.1)
    now = time.time()
    time1 = normal_function()  # This shouldn't be buffered since we slept

    assert(now + 0.05 > time1)


# Functions should have their own buffers
def test_many_normal_functions():
    @buffer(0.1)
    def normal_function1():
        return time.time()

    @buffer(0.1)
    def normal_function2():
        return time.time()

    time1 = normal_function1()
    time2 = normal_function1()
    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)

    now = time.time()
    time1 = normal_function2()
    # This shouldn't be buffered
    assert(now + 0.05 > time1)
    time2 = normal_function2()
    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# A class function shouldn't buffer if it is called only once
def test_instance_method_once():
    class Class:
        @buffer(0.1)
        def instance_method(self):
            return time.time()

    instance = Class()

    now = time.time()
    time1 = instance.instance_method()

    assert(now + 0.05 > time1)


# The second class function call should be buffered
def test_instance_method_twice():
    class Class:
        @buffer(0.1)
        def instance_method(self):
            return time.time()

    instance = Class()

    time1 = instance.instance_method()
    time2 = instance.instance_method()

    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# Classes should have their own buffers
def test_many_instance_methods():
    class Class1:
        @buffer(0.1)
        def instance_method(self):
            return time.time()

    class Class2:
        @buffer(0.1)
        def instance_method(self):
            return time.time()

    instance1 = Class1()
    instance2 = Class2()

    time1 = instance1.instance_method()
    time2 = instance1.instance_method()

    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)

    now = time.time()
    time1 = instance2.instance_method()
    # This shouldn't be buffered
    assert(now + 0.05 > time1)
    time2 = instance2.instance_method()
    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# All classfunctions should have their own buffers
def test_class_with_many_functions():
    class Class:
        @buffer(0.1)
        def instance_method1(self):
            return time.time()

        @buffer(0.1)
        def instance_method2(self):
            return time.time()

    instance = Class()

    time1 = instance.instance_method1()
    time2 = instance.instance_method2()

    assert(time1 - time2 < 0.1 and time2 - time1 < 0.15)


# Multiple instances of the same class should share buffers
def test_many_instances_off_same_class():
    class Class:
        @buffer(0.1)
        def instance_method(self):
            return time.time()

    instance1 = Class()
    instance2 = Class()

    time1 = instance1.instance_method()
    time2 = instance2.instance_method()

    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# A staticmethod should be able to be buffered
def test_staticmethod():
    class Class:
        @staticmethod
        @buffer(0.1)
        def static_method():
            return time.time()

    time1 = Class.static_method()
    time2 = Class.static_method()

    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# A classmethod should be able to be buffered
def test_classmethod():
    class Class:
        @classmethod
        @buffer(0.1)
        def class_method(cls):
            return time.time()

    instance = Class()
    time1 = Class.class_method()
    time2 = instance.class_method()

    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# Attributes should remain intact
def test_attributes():
    @buffer(0.1)
    def normal_function():
        """Example"""
        pass

    assert(normal_function.__name__ == "normal_function")
    assert(normal_function.__doc__ == "Example")
    assert(normal_function.__module__ == __name__)


# If always buffer is enabled, then the function call should always buffer
def test_always_buffer():
    @buffer(0.1, always_buffer=True)
    def normal_function1():
        return time.time()

    now = time.time()
    time1 = normal_function1()
    assert(now + 0.05 < time1)

    # Always buffer should work with buffer_on_same_arguments
    @buffer(0.1, always_buffer=True, buffer_on_same_arguments=True)
    def normal_function2(arg1):
        return time.time()

    now = time.time()
    time1 = normal_function2("foo")
    assert(now + 0.05 < time1)


# Function should be buffered both times
def test_always_buffer_twice():
    @buffer(0.1, always_buffer=True)
    def normal_function():
        return time.time()

    now = time.time()
    normal_function()
    time1 = normal_function()
    assert(time1 - now > 0.2 and time1 - now < 0.25)


# Function should be buffered both times even though we sleep
def test_random_delay_with_sleep():
    @buffer(0.1, always_buffer=True)
    def normal_function():
        return time.time()

    now = time.time()
    normal_function()
    time.sleep(0.1)
    time1 = normal_function()
    assert(time1 - now > 0.3 and time1 - now < 0.35)


def test_random_delay_once():
    @buffer(0, (0.1, 0.1), always_buffer=True)
    def normal_function():
        return time.time()

    now = time.time()
    time1 = normal_function()
    assert(now + 0.05 < time1)


def test_random_delay_twice():
    @buffer(0, (0.1, 0.1))
    def normal_function():
        return time.time()

    time1 = normal_function()
    time2 = normal_function()
    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# A function shouldn't buffer if it is called only once
@pytest.mark.asyncio
async def test_async_normal_function_once():
    @buffer(0.1)  # Buffer by 0.1 seconds
    async def normal_function():
        return time.time()

    now = time.time()
    time1 = await normal_function()
    assert(now + 0.05 > time1)


# The second function call should be buffered
@pytest.mark.asyncio
async def test_async_normal_function_twice():
    @buffer(0.1)
    async def normal_function():
        return time.time()

    time1 = await normal_function()
    time2 = await normal_function()

    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# A class function shouldn't buffer if it is called only once
@pytest.mark.asyncio
async def test_async_instance_method_once():
    class Class:
        @buffer(0.1)
        async def instance_method(self):
            return time.time()

    instance = Class()

    now = time.time()
    time1 = await instance.instance_method()

    assert(now + 0.05 > time1)


# The second class function call should be buffered
@pytest.mark.asyncio
async def test_async_instance_method_twice():
    class Class:
        @buffer(0.1)
        async def instance_method(self):
            return time.time()

    instance = Class()

    time1 = await instance.instance_method()
    time2 = await instance.instance_method()

    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# Function should be buffered both times
@pytest.mark.asyncio
async def test_async_always_buffer_twice():
    @buffer(0.1, always_buffer=True)
    async def normal_function():
        return time.time()

    now = time.time()
    await normal_function()
    time1 = await normal_function()
    assert(time1 - now > 0.2 and time1 - now < 0.25)


# No buffering should happen
def test_multiprocessing_twice():
    @buffer(0.1)
    def shared_function(q):
        q.put(time.time())

    q1 = Queue()
    q2 = Queue()
    p1 = Process(target=shared_function, args=(q1,))
    p2 = Process(target=shared_function, args=(q2,))
    now = time.time()
    p1.start()
    p2.start()
    time1 = q1.get()
    time2 = q2.get()
    p1.join()
    p2.join()
    assert(now + 0.05 > time1 and now + 0.05 > time2)


# Second process call should be buffered
def test_multiprocessing_share_buffer_twice():
    @buffer(0.1, share_buffer=True)
    def shared_function(q):
        q.put(time.time())

    q1 = Queue()
    q2 = Queue()
    p1 = Process(target=shared_function, args=(q1,))
    p2 = Process(target=shared_function, args=(q2,))
    p1.start()
    p2.start()
    time1 = q1.get()
    time2 = q2.get()
    p1.join()
    p2.join()
    # Use 0.09 instead of 0.1 since multiprocessing can be a bit unpredictable
    # Also since either of the processes can reach buffering before the other,
    # check for both outomes
    assert((time2 - time1 > 0.09 and time2 - time1 < 0.15)
           or (time1 - time2 > 0.09 and time1 - time2 < 0.15))


# Function should be buffered both times
def test_multiprocessing_always_buffer_twice():
    @buffer(0.1, always_buffer=True)
    def normal_function(q):
        q.put(time.time())

    q1 = Queue()
    q2 = Queue()
    p1 = Process(target=normal_function, args=(q1,))
    p2 = Process(target=normal_function, args=(q2,))
    now = time.time()
    p1.start()
    p2.start()
    time2 = q1.get()
    time1 = q2.get()
    p1.join()
    p2.join()
    assert((time1 - now > 0.18 and time1 - now < 0.25)
           or (time2 - now > 0.18 and time2 - now < 0.25))


# The second process method call should be buffered
def test_multiprocessing_instance_method_twice():
    class Class:
        @buffer(0.1, share_buffer=True)
        def instance_method(self, q):
            q.put(time.time())

    instance = Class()

    q1 = Queue()
    q2 = Queue()
    p1 = Process(target=instance.instance_method, args=(q1,))
    p2 = Process(target=instance.instance_method, args=(q2,))
    p1.start()
    p2.start()
    time1 = q1.get()
    time2 = q2.get()
    p1.join()
    p2.join()
    # Use 0.09 instead of 0.1 since multiprocessing can be a bit unpredictable
    assert((time2 - time1 > 0.09 and time2 - time1 < 0.15)
           or (time1 - time2 > 0.09 and time1 - time2 < 0.15))


def test_threading_twice():
    @buffer(0.1)
    def normal_function(q):
        q.put(time.time())

    q1 = Queue()
    q2 = Queue()
    p1 = Thread(target=normal_function, args=(q1,))
    p2 = Thread(target=normal_function, args=(q2,))
    p1.start()
    p2.start()
    time1 = q1.get()
    time2 = q2.get()
    p1.join()
    p2.join()
    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


def test_threading_instance_method_twice():
    class Class:
        @buffer(0.1)
        def instance_method(self, q):
            q.put(time.time())

    instance = Class()

    q1 = Queue()
    q2 = Queue()
    p1 = Thread(target=instance.instance_method, args=(q1,))
    p2 = Thread(target=instance.instance_method, args=(q2,))
    p1.start()
    p2.start()
    time1 = q1.get()
    time2 = q2.get()
    p1.join()
    p2.join()
    assert(time2 - time1 > 0.1 and time2 - time1 < 0.15)


# Function should be buffered both times
def test_threading_always_buffer_twice():
    @buffer(0.1, always_buffer=True)
    def normal_function(q):
        q.put(time.time())

    q1 = Queue()
    q2 = Queue()
    p1 = Thread(target=normal_function, args=(q1,))
    p2 = Thread(target=normal_function, args=(q2,))
    now = time.time()
    p1.start()
    p2.start()
    _ = q1.get()
    time1 = q2.get()
    p1.join()
    p2.join()
    assert(time1 - now > 0.18 and time1 - now < 0.25)
