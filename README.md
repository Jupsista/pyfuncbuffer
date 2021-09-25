# pyfuncbuffer
[![Build status](https://github.com/Jupsista/pyfuncbuffer/actions/workflows/pytest.yml/badge.svg?branch=master)](https://github.com/Jupsista/pyfuncbuffer/actions/workflows/pytest.yml)

A simple to use decorator to buffer function calls.

## Install

```bash
$ pip install pyfuncbuffer
```

## Example usage

Let's say you have a scraper, and don't want sites to timeout you.
You can use the `@buffer()` wrapper to make your function calls buffered!

```python
from pyfuncbuffer import buffer

# A function you want to buffer
@buffer(seconds=0.5, random_delay=0.5)
def scrape_link(url) -> []: ...

links = scrape_link("https://example.org")

while True:
    link = links.pop(link)
    links.append(scrape_link(link))
```

The `@buffer()` wrapper works both for regular, and class functions!
