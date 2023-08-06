"""
Snarky

``snarky`` is a useless package that makes it easy to add a jk (just kidding!)
keyword argument to any function. Moreover, snarky defines several default
behaviors for reacting whenever jk==True.
"""

__all__ = ['snarky',
           'snarkyvoice',
           'say_time']

from . decorators import *

from . version import __version__