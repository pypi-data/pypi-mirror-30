======
Snarky
======

Snarky is a useless Python package that makes it easy to add a ``jk`` (just kidding!) keyword argument to any function. Moreover, snarky defines several default behaviors for reacting whenever jk==True.

Quick examples
==============

Using snarky is really easy. Suppose we have a function:

.. code-block:: python

    def my_fun(a, b):
        """Sample function with arguments."""
        return a*b

Then calling our function might look like this:

.. code-block::

    >>> my_func(4, 5)
    20

    >>> my_func(a=3, b=7)
    21

    >>> my_func(a=3, b=7, jk=True)
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    <ipython-input-143-231ea24720af> in <module>()
    ----> 1 my_func(a=3, b=7, jk=True)

    TypeError: my_func() got an unexpected keyword argument 'jk'

But that's lame! What function doesn't give you the option to say 'just kidding!', right?

That's where ``snarky`` shines!

Simply add one of several default behaviors, or even define your own! Here, we will apply the default snarky behavior to our function:

.. code-block:: python

    from snarky import *

    @snarky
    def my_fun(a, b):
        """Sample function with arguments."""
        return a*b

Now calling our function might look like this:

.. code-block::

    >>> my_func(4, 5)
    20

    >>> my_func(a=3, b=7)
    21

    >>> my_func(a=3, b=7, jk=True)
    LOL! Then why are you asking me to run 'my_func'? Unbelievable!
    21

And the day is saved.

Installation
============

The easiest way to install snarky is to use ``pip``. From the terminal, run:

.. code-block:: bash

    $ pip install snarky

Alternatively, you can install the latest version of snarky by running the following commands:

.. code-block:: bash

    $ git clone https://github.com/eackermann/snarky.git
    $ cd snarky
    $ python setup.py install

License
=======

Snarky is distributed under the MIT license. See the `LICENSE <https://github.com/eackermann/snarky/blob/master/LICENSE>`_ file for details.
