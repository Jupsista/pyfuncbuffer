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

import functools
import time
import threading
import random
from typing import Union, Tuple


# pylint: disable=line-too-long
def buffer(seconds: Union[float, int],
           random_delay: Union[float, int, Tuple[Union[float, int], Union[float, int]]] = 0,
           always_buffer: bool = False,
           buffer_on_same_arguments: bool = False):
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
    """
    class Buffer:
        # Store function calls in a dictionary where function is the key
        # and time of last call is the value
        last_called = {}
        # Store arguments in adictionary where function is the key
        # and the key is a dictionary where the arguments are the
        # key and the time of last call with said arguments is the value
        arguments = {}
        lock = threading.Lock()

        def __init__(self, func):
            self.func = func
            self.seconds = seconds
            self.always_buffer = always_buffer
            self.random_delay_start = 0
            self.random_delay_end = random_delay
            self.buffer_on_same_arguments = buffer_on_same_arguments
            if isinstance(random_delay, tuple):
                self.random_delay_start = random_delay[0]
                self.random_delay_end = random_delay[0]

            functools.update_wrapper(self, func)  # Transfer func attributes

        def __call__(self, *args, **kwargs):
            # A lock is required, so that if the function is called rapidly,
            # we can still buffer all the calls. Wihthout this, calls would
            # get through without being buffered.
            Buffer.lock.acquire()
            l_random_delay = random.uniform(self.random_delay_start, self.random_delay_end)
            # If always buffer is on then this is the only required thing to do
            if self.always_buffer:
                time.sleep(self.seconds + l_random_delay)
                Buffer.last_called[self.func] = (time.time() + l_random_delay)
                Buffer.lock.release()
                return self.func(*args, **kwargs)

            if self.buffer_on_same_arguments:
                return self.buffer_same_args(*args, **kwargs)
            else:
                return self.buffer_regular(*args, **kwargs)

        def buffer_same_args(self, *args, **kwargs):
            """Buffer the function only when `*args` and `**kwargs` are the same."""
            if not Buffer.arguments:
                self.add_arguments(*args, **kwargs)
                Buffer.lock.release()
                return self.func(*args, **kwargs)

            time_of_last_call = self.get_last_called_with_args(*args, **kwargs)
            print("time_of_last_call: ", time_of_last_call)
            if not time_of_last_call:
                self.add_arguments(*args, **kwargs)
                Buffer.lock.release()
                return self.func(*args, **kwargs)

            if not (time.time() - time_of_last_call) > self.seconds:
                time.sleep(self.get_sleep_time(time_of_last_call))

            self.add_arguments(*args, **kwargs)
            Buffer.lock.release()
            return self.func(*args, **kwargs)

        def buffer_regular(self, *args, **kwargs):
            """Buffer self.function depending on self.seconds and random_delay."""
            l_random_delay = random.uniform(self.random_delay_start, self.random_delay_end)
            if Buffer.last_called:
                if (time.time() - Buffer.last_called.get(self.func)) > self.seconds:
                    Buffer.last_called[self.func] = (time.time() + l_random_delay)
                    Buffer.lock.release()
                    return self.func(*args, **kwargs)
                else:
                    time.sleep(self.get_sleep_time(Buffer.last_called.get(self.func)))
                    Buffer.last_called[self.func] = (time.time() + l_random_delay)
                    Buffer.lock.release()
                    return self.func(*args, **kwargs)
            else:
                Buffer.last_called[self.func] = (time.time() + l_random_delay)
                Buffer.lock.release()
                return self.func(*args, **kwargs)

        def get_last_called_with_args(self, *args, **kwargs) -> Union[float, None]:
            """Return time of last call with *args and **kwargs."""
            return Buffer.arguments.get((self.func, args, frozenset(kwargs.items())))

        def add_arguments(self, *args, **kwargs):
            """Add arguments to Buffer.arguments object."""
            Buffer.arguments[(self.func, args, frozenset(kwargs.items()))] = time.time()

        def get_sleep_time(self, last_called):
            """Get the required amount of time to sleep depending on last_called."""
            return (self.seconds - (time.time() - last_called))

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
