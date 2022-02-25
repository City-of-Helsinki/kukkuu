import random

from kukkuu.utils import hashids


def test_hashids():
    for x in random.sample(range(1, 99999), 10):
        assert hashids.decode(hashids.encode(x))[0] == x
