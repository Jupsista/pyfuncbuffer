# pyfuncbuffer
[![Build status](https://github.com/Jupsista/pyfuncbuffer/actions/workflows/pytest.yml/badge.svg?branch=master)](https://github.com/Jupsista/pyfuncbuffer/actions/workflows/pytest.yml)

A simple to use decorator to buffer function calls. Supports python versions 3.6 and up.
Works for both regular and async functions.

## Install

```bash
$ pip install pyfuncbuffer
```

## Example usage

Let's say you have a scraper, and don't want sites to timeout you.
You can use the `@buffer()` wrapper to make your function calls buffered!

```python
from pyfuncbuffer import buffer

# We specify scrape_links to always buffer at least 0.5 seconds
# and by a random delay of 0 to 0.5
@buffer(seconds=0.5, random_delay=0.5)
def scrape_links(url) -> []: ...

links = scrape_links("https://example.org")

while True:
    link = links.pop(0)
    links.append(scrape_links(link))
```

The `@buffer()` wrapper works both for regular functions, and instance methods!

## Parameters

- `seconds`: Required

Seconds to buffer. Can be an int or a float.

- `random_delay`: Optional

Seconds to define a random delay between 0 and random_delay.
Can be an int or a float. Alternativelly if a tuple is passed,
delay is chosen between `random_delay[0]` and `random_delay[1]`.

- `always_buffer`: Optional

Whether or not to always buffer. If specified, `buffer_on_same_arguments`
is ignored.

- `buffer_on_same_arguments`: Optional

Only buffer if the arguments on the buffered function are the same.
False by default.

## Testing

Testing is done using [pytest](https://github.com/pytest-dev/pytest) and [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio).

Run

```bash
$ python -m pytest tests/test_pyfuncbuffer.py
```

in the project root to run all the tests.
