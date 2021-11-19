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

import asyncio
import functools
from multiprocessing import current_process, Lock as mpLock, Manager, Process
from threading import current_thread, Thread, Lock as tLock
import random
import time
from typing import Union, Tuple


# pylint: disable=line-too-long, too-many-statements
def buffer(seconds: Union[float, int],
           random_delay: Union[float, int, Tuple[Union[float, int], Union[float, int]]] = 0,
           always_buffer: bool = False,
           buffer_on_same_arguments: bool = False,
           share_buffer: bool = False):
    """Simple-to-use decorator to buffer function calls.

    Parameters:
        seconds: Required
            Seconds to buffer. Can be lower than one second with float.
        random_delay: Optional
            Seconds to define random delay between 0 and
            random_delay, or if a tuple is passed,
            between `random_delay[0]` and `random_delay[1]`.
            Can be omitted.
        always_buffer: Optional
            Wether to always buffer function calls or not
        buffer_on_same_arguments: Optional
            Only buffer if the arguments on the buffered
            function are the same. If always_buffer is
            `True`, then this has no effect
        share_buffer: Optional
            Share buffer between processes. This is only useful
            when using multiprocessing, and still wanting to
            have function calls buffered even if called in seperate
            processes
    """
    # pylint: disable=missing-class-docstring
    class Buffer:
        # Store function calls in a dictionary where function is the key
        # and time of last call is the value. If `share_buffer` is enabled,
        # then we should use a manager to maintain state across processes
        if share_buffer:
            manager = Manager()
            last_called = manager.dict()
        else:
            last_called = {}
        # Store arguments in adictionary where a set containing the function,
        # args and kwargs in said order is the key and the value
        # is the time of last call
        arguments = {}

        def __init__(self, func):
            self.original_func = func
            # This is the value that will be used in `arguments` or `last_called` as a key
            self.func = id(func)
            self.seconds = seconds
            self.always_buffer = always_buffer
            self.random_delay_start = 0
            self.random_delay_end = random_delay
            self.buffer_on_same_arguments = buffer_on_same_arguments
            self._mp_lock = mpLock()
            self._t_lock = tLock()
            self.lock = None

            if asyncio.iscoroutinefunction(self.func):
                self.is_coroutine = True
            else:
                self.is_coroutine = False

            if isinstance(random_delay, tuple):
                self.random_delay_start = random_delay[0]
                self.random_delay_end = random_delay[0]

            functools.update_wrapper(self, func)  # Transfer func attributes

        def __call__(self, *args, **kwargs):
            l_random_delay = self.get_random_delay()
            # If always buffer is on then this is the only required thing to do
            self.detect_process_type()
            if self.always_buffer:
                if self.is_coroutine:
                    async def temp():
                        await asyncio.sleep(self.seconds + l_random_delay)
                        return await self.original_func(*args, **kwargs)
                    return temp()

                if self.lock:  # If true, is multiprocess or thread process
                    with self.lock:
                        time.sleep(self.seconds + l_random_delay)
                    return self.original_func(*args, **kwargs)

                time.sleep(self.seconds + l_random_delay)
                return self.original_func(*args, **kwargs)

            # pylint: disable=no-else-return
            if self.buffer_on_same_arguments:
                if self.is_coroutine:
                    # We have to make a temp function, otherwise we can't return async from a
                    # non-async function.
                    async def tmp():
                        if self.lock:
                            with self.lock:
                                return await self.buffer_same_args_async(*args, **kwargs)
                        return await self.buffer_same_args_async(*args, **kwargs)
                    return tmp()

                if self.lock:
                    with self.lock:
                        return self.buffer_same_args(*args, **kwargs)
                return self.buffer_same_args(*args, **kwargs)
            else:
                if self.is_coroutine:
                    async def tmp():
                        if self.lock:
                            with self.lock:
                                return await self.buffer_regular_async(*args, **kwargs)
                            return await self.buffer_regular_async(*args, **kwargs)
                    return tmp()

                if self.lock:
                    with self.lock:
                        return self.buffer_regular(*args, **kwargs)
                return self.buffer_regular(*args, **kwargs)

        def buffer_same_args(self, *args, **kwargs):
            """Buffer the function only when `*args` and `**kwargs` are the same."""
            if not Buffer.arguments:
                self.add_arguments(*args, **kwargs)
                return self.original_func(*args, **kwargs)

            time_of_last_call = self.get_last_called_with_args(*args, **kwargs)
            if not time_of_last_call:
                self.add_arguments(*args, **kwargs)
                return self.original_func(*args, **kwargs)

            if not (time.time() - time_of_last_call) > self.seconds:
                time.sleep(self.get_sleep_time(time_of_last_call))

            self.add_arguments(*args, **kwargs)
            return self.original_func(*args, **kwargs)

        async def buffer_same_args_async(self, *args, **kwargs):
            """Buffer the function asynchronously only when `*args` and `**kwargs` are the same."""
            if not Buffer.arguments:
                self.add_arguments(*args, **kwargs)
                return await self.original_func(*args, **kwargs)

            time_of_last_call = self.get_last_called_with_args(*args, **kwargs)
            if not time_of_last_call:
                self.add_arguments(*args, **kwargs)
                return await self.original_func(*args, **kwargs)

            if not (time.time() - time_of_last_call) > self.seconds:
                await asyncio.sleep(self.get_sleep_time(time_of_last_call))

            self.add_arguments(*args, **kwargs)
            return await self.original_func(*args, **kwargs)

        def buffer_regular(self, *args, **kwargs):
            """Buffer self.function depending on self.seconds and random_delay."""
            l_random_delay = self.get_random_delay()
            if Buffer.last_called:
                if not (time.time() - Buffer.last_called.get(self.func)) > self.seconds:
                    time.sleep(self.get_sleep_time(Buffer.last_called.get(self.func)))

            Buffer.last_called[self.func] = time.time() + l_random_delay
            return self.original_func(*args, **kwargs)

        async def buffer_regular_async(self, *args, **kwargs):
            """Buffer self.function asynchronously depending on self.seconds and random_delay."""
            l_random_delay = self.get_random_delay()
            if Buffer.last_called:
                if not (time.time() - Buffer.last_called.get(self.func)) > self.seconds:
                    await asyncio.sleep(self.get_sleep_time(Buffer.last_called.get(self.func)))

            Buffer.last_called[self.func] = time.time() + l_random_delay
            return await self.original_func(*args, **kwargs)

        def get_last_called_with_args(self, *args, **kwargs) -> Union[float, None]:
            """Return time of last call with *args and **kwargs."""
            return Buffer.arguments.get((self.func, args, frozenset(kwargs.items())))

        def add_arguments(self, *args, **kwargs):
            """Add arguments to Buffer.arguments object."""
            Buffer.arguments[(self.func, args, frozenset(kwargs.items()))] = time.time() + self.get_random_delay()

        def get_sleep_time(self, last_called) -> float:
            """Get the required amount of time to sleep depending on last_called."""
            return self.seconds - (time.time() - last_called)

        def get_random_delay(self) -> float:
            """Return random delay specified by self.random_delay_start and self.random_delay_end."""
            return random.uniform(self.random_delay_start, self.random_delay_end)

        def detect_process_type(self):
            """Detect the process type(thread or multiprocess process) and set self.lock accordingly."""
            if not self.lock:
                if type(current_process()) == Process:  # Is multiprocess process
                    self.lock = self._mp_lock
                if type(current_thread()) == Thread:  # Is thread
                    self.lock = self._t_lock

        # This is required for instance methods to work
        def __get__(self, instance, instancetype):
            """Return original function.

            Implement the descriptor protocol to make decorating instance
            method possible.
            """
            # Return a partial function with the first argument is the instance
            #   of the class decorated.
            return functools.partial(self.__call__, instance)

    return Buffer
