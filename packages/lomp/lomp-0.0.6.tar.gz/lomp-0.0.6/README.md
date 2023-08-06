# lowmemory-parallel

[![Build Status](https://travis-ci.org/jimrybarski/lowmem-parallel.svg?branch=master)](https://travis-ci.org/jimrybarski/lowmem-parallel)

This library provides a function to parallelize work in a way that avoids copying data when passing it to threads (when
using operating systems that have copy-on-write virtual memory, such as Linux).

It was developed to handle a scenario where many large images needed to be analyzed in parallel. When using a queue
from the `multiprocessing` module, the images would be duplicated in memory, resulting in outrageous memory usage as
well as making memory bandwidth the performance bottleneck.

## Installation

`pip install lomp`

## Usage

#### parallel_map

`parallel_map` iterates over the results returned by your function.

```python
from lomp import parallel_map

def analyze_image(image):
    # perform some analysis
    return result

big_image_list = [image1, image2, ..., image100]

# the first argument is your data, the second is a function to run on each item
for result in parallel_map(big_image_list, analyze_image):
    print(result)
```

If your function needs positional or keyword arguments, you can pass them in as tuples and dictionaries, respectively:

```python
from lomp import parallel_map

def analyze_image(image, correction_factor, palette, normalize=False, find_kittens=False):
    # perform some analysis
    return result

big_image_list = [image1, image2, ..., image100]

for result in parallel_map(big_image_list, analyze_image, args=(correction_factor, palette), kwargs={'find_kittens': True):
    print(result)
```

#### parallel_iterator

`parallel_iterator` works comparably to `parallel_map`. The critical difference is that `parallel_iterator` will work
when the number of results per item of work is unknown.

## Caveats

The memory savings only occur if the data is left unmodified, and anything that is returned from the function will be
pickled and unpickled (thus, the smaller the better). Returning large objects will result in poor performance.
If in doubt, benchmark. This library has only been tested on Linux.

Note that `parallel_map` will consume the entire iterable it is given - if this won't fit into memory, you need to
break it up into smaller chunks yourself.