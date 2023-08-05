#!/usr/bin/env python3
"""setup wh
"""

from distutils.core import setup

__VERSION__ = '1.0.0'
setup(
    name='wh',
    version=__VERSION__,
    description='Record elapsed time and number of calls of a function',
    license='MIT',
    author='AnqurVanillapy',
    author_email='anqurvanillapy@gmail.com',
    url='https://github.com/anqurvanillapy/wh',
    py_modules=['wh'],
)
