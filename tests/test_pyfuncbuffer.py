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

from src.pyfuncbuffer import buffer


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

    assert(time2 - time1 > 0.1)


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
    assert(time2 - time1 > 0.1)

    now = time.time()
    time1 = normal_function2()
    # This shouldn't be buffered
    assert(now + 0.05 > time1)
    time2 = normal_function2()
    assert(time2 - time1 > 0.1)


# A class function shouldn't buffer if it is called only once
def test_class_function_once():
    class Test:
        @buffer(0.1)
        def class_function(self):
            return time.time()

    test = Test()

    now = time.time()
    time1 = test.class_function()

    assert(now + 0.05 > time1)


# The second class function call should be buffered
def test_class_function_twice():
    class Class1:
        @buffer(0.1)
        def class_function(self):
            return time.time()

    class1 = Class1()

    time1 = class1.class_function()
    time2 = class1.class_function()

    assert(time2 - time1 > 0.1)


# Classes should have their own buffers
def test_many_class_functions():
    class Class1:
        @buffer(0.1)
        def class_function(self):
            return time.time()

    class Class2:
        @buffer(0.1)
        def class_function(self):
            return time.time()

    class1 = Class1()
    class2 = Class2()

    time1 = class1.class_function()
    time2 = class1.class_function()

    assert(time2 - time1 > 0.1)

    now = time.time()
    time1 = class2.class_function()
    # This shouldn't be buffered
    assert(now + 0.05 > time1)
    time2 = class2.class_function()
    assert(time2 - time1 > 0.1)
    assert(time2 - time1 > 0.1)


# All classfunctions should have their own buffers
def test_class_with_many_functions():
    class Class1:
        @buffer(0.1)
        def class_function1(self):
            return time.time()

        @buffer(0.1)
        def class_function2(self):
            return time.time()

    class1 = Class1()

    time1 = class1.class_function1()
    time2 = class1.class_function2()

    assert(time1 - time2 < 0.1)


# Multiple instances of the same class should share buffers
def test_many_instances_off_same_class():
    class Class1:
        @buffer(0.1)
        def class_function(self):
            return time.time()

    class1 = Class1()
    class2 = Class1()

    time1 = class1.class_function()
    time2 = class2.class_function()

    assert(time2 - time1 > 0.1)


# A staticmethod should be able to be buffered
def test_staticmethod():
    class Class1:
        @staticmethod
        @buffer(0.1)
        def class_function():
            return time.time()

    time1 = Class1.class_function()
    time2 = Class1.class_function()

    assert(time2 - time1 > 0.1)


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
    def normal_function():
        return time.time()

    now = time.time()
    time1 = normal_function()
    assert(now + 0.05 < time1)


# Function should be buffered both times
def test_always_buffer_twice():
    @buffer(0.1, always_buffer=True)
    def normal_function():
        return time.time()

    now = time.time()
    normal_function()
    time2 = normal_function()
    assert(time2 - now > 0.2)


# Function should be buffered both times even though we sleep
def test_random_delay_with_sleep():
    @buffer(0.1, always_buffer=True)
    def normal_function():
        return time.time()

    now = time.time()
    normal_function()
    time.sleep(0.1)
    time2 = normal_function()
    assert(time2 - now > 0.3)


def test_random_delay():
    @buffer(0, (0.1, 0.1), always_buffer=True)
    def normal_function():
        return time.time()

    now = time.time()
    time1 = normal_function()
    assert(now + 0.05 < time1)
