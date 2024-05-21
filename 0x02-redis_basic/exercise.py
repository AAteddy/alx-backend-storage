#!/usr/bin/env python3

"""Create a Cache class. In the __init__ method, store an instance
of the Redis client as a private variable named _redis
(using redis.Redis()) and flush the instance using flushdb.

Create a store method that takes a data argument and returns a string.
The method should generate a random key (e.g. using uuid),
store the input data in Redis using the random key and return the key.

Type-annotate store correctly.
Remember that data can be a str, bytes, int or float.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Counts how many times methods of the Cache class are called"""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Increments the count for that key every time the method
        is called and returns the value returned by the original method
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """Stores the history of inputs and outputs"""
    inpkey = method.__qualname__ + ":inputs"
    outpkey = method.__qualname__ + ":outputs"

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Appends the input argument and returns the output"""
        self._redis.rpush(inpkey, str(args))
        res = method(self, *args, **kwargs)
        self._redis.rpush(outpkey, str(res))
        return res

    return wrapper


def replay(method: Callable) -> None:
    """A function that displays the history of calls of a
    particular function.
    """
    input_key = "{}:inputs".format(method.__qualname__)
    output_key = "{}:outputs".format(method.__qualname__)

    inputs = method.__self__._redis.lrange(input_key, 0, -1)
    outputs = method.__self__._redis.lrange(output_key, 0, -1)

    print("{} was called {} times:".format(method.__qualname__, len(inputs)))
    for inp, out in zip(inputs, outputs):
        print(
            "{}(*{}) -> {}".format(
                method.__qualname__, inp.decode("utf-8"), out.decode("utf-8")
            )
        )


class Cache:
    """doc doc class"""

    def __init__(self):
        """Redis Client initialization"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Takes a data and a random generated key
        and returns a string.
        """
        keyx = str(uuid.uuid4())
        self._redis.set(keyx, data)
        return keyx

    def get(
        self, key: str, fn: Optional[Callable] = None
    ) -> Union[str, bytes, int, float]:
        """Reads from Redis and recovers the original type"""
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        """Parametrize Cache.get to a string conversion function"""
        return self.get(key, fn=str)

    def get_int(self, key: str) -> int:
        """Parametrize Cache.get to an integer conversion function"""
        return self.get(key, fn=int)
