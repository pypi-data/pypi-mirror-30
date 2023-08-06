[![PyPI version](https://badge.fury.io/py/TagStats.svg)](https://badge.fury.io/py/TagStats)

A concise yet efficient implementation for computing the statistics of each tag's set of key phrases over input lines in Python 3.
One of the major applications is for [sentiment analysis](https://en.wikipedia.org/wiki/Sentiment_analysis), where each tag is a sentiment with the respective key phrases describing the sentiment.

# How it Works

A trie structure is constructed to index all the key phrases. Then each line is matched towards the index to compute the respective statistics.
The time complexity is $O(m^2 \cdot n)$, where $m$ is the maximum number of words in each line and $n$ is the number of lines.

# Installation

This package is available on PyPi. Just use `pip3 install -U tagstats` to install it.

# Usage

You can simply call `compute(content, tagDict)`, where `content` is a list of lines and `tagDict` is a dictionary with each tag name as key and the respective set of key phrases as value.

``` python
from tagstats import compute

print(compute(
    [
        "a b c",
        "b c",
        "a c e"
    ],
    {
        "+": ["a b", "a c"],
        "-": ["b c"]
    }
))
```

The output is a dictionary with each tag name as key and the respective totaled frequencies for lines as value.
``` python
{'+': [1, 0, 1], '-': [1, 1, 0]}
```

You can change the default tokenizer, by specify a compiled regex as separator to `tagstats.tagstats.tokenizer`.

# Tip

I strongly encourage using PyPy instead of CPython to run the script for best performance.
