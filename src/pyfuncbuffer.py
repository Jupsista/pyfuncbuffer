"""pyfuncbuffer.py - A library for buffering function calls.

Copyright (C) 2021 TODO: Add name

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
           always_buffer: bool = False):
    """Buffer function calls by time specified in seconds and random_delay.

    Parameters:
        seconds: Seconds to buffer. Can be lower than one second with float.
        random_delay: Seconds to define random delay between 0 and
                      random_delay, or if a tuple is passed,
                      between random_delay[0] and random_delay[1].
                      Can be omitted.

    Random delay can be used or omitted to buffer functions by a random time.
    """
    class Buffer:
        # Store function calls in a dictionary where function is the key
        # and time of last call is the value
        last_called = {}
        lock = threading.Lock()

        def __init__(self, func):
            self.func = func
            self.seconds = seconds
            self.always_buffer = always_buffer
            self.random_delay_start = 0
            self.random_delay_end = random_delay
            if isinstance(random_delay, tuple):
                self.random_delay_start = random_delay[0]
                self.random_delay_end = random_delay[0]

            functools.update_wrapper(self, func)  # Transfer func attributes

        def __call__(self, *args, **kwargs):
            # A lock is required, so that if the function is called rapidly,
            # we can still buffer all the calls. Wihthout this, calls would
            # get through without being buffered.
            print(Buffer.last_called)
            Buffer.lock.acquire()
            l_random_delay = random.uniform(self.random_delay_start, self.random_delay_end)
            while True:
                if self.always_buffer:
                    time.sleep(self.seconds + l_random_delay)
                    Buffer.last_called[self.func] = (time.time() + l_random_delay)
                    Buffer.lock.release()
                    return self.func(*args, **kwargs)

                if Buffer.last_called:
                    if (time.time() - Buffer.last_called.get(self.func)) > self.seconds:
                        Buffer.last_called[self.func] = (time.time() + l_random_delay)
                        Buffer.lock.release()
                        return self.func(*args, **kwargs)
                    else:
                        time.sleep(self.seconds - (time.time() - Buffer.last_called.get(self.func)))
                else:
                    Buffer.last_called[self.func] = (time.time() + l_random_delay)
                    Buffer.lock.release()
                    return self.func(*args, **kwargs)

        # This is required for class functions to work
        def __get__(self, instance, instancetype):
            """Return original function.

            Implement the descriptor protocol to make decorating instance
            method possible.
            """
            # Return a partial function with the first argument is the instance
            #   of the class decorated.
            return functools.partial(self.__call__, instance)

    return Buffer
