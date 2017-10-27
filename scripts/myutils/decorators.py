# Copyright (c) 2017, Medicine Yeh

import logging
from time import time
from functools import wraps

# Third party
from logzero import logger


def timed(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        start = time()
        result = f(*args, **kwds)
        elapsed = time() - start
        logger.debug('%10s, elapsed time: %f ms', f.__name__, elapsed * 1000)
        return result

    return wrapper
