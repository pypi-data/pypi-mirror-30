"""Record elapsed time and number of function calls
"""

import sys
from time import time


def trek(stream=sys.stdout):
    """Elapsed time and number of calls logged at sys.stdout by default"""

    def deco(func):
        """Decorator"""

        def wrap(*args, **kwargs):
            """User function"""
            wrap.ncall += 1
            wrap.started = time() * 1000
            ret = func(*args, **kwargs)
            wrap.ms += time() * 1000 - wrap.started
            return ret

        def done():
            """Log the result"""
            stream.write(
                '[wh] {}: {} calls, {}(ms) elapsed\n'.format(
                    wrap.__name__, wrap.ncall, wrap.ms
                )
            )
            stream.flush()

        wrap.__name__ = func.__name__
        wrap.ncall = wrap.ms = 0
        wrap.done = done
        return wrap

    return deco
