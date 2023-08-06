Jaynes, A Utility for running script on AWS with docker
=======================================================

 ## Todo

-  [ ] get the initial template to work

Done
----

Installation
------------

.. code-block:: bash

    pip install jaynes

Usage (**Show me the Mo-NAY!! :moneybag::money\_with\_wings:**)
---------------------------------------------------------------

.. code-block:: python

    from jaynes import Jaynes

    J = Jaynes()  # where you add aws configurations
    J.call(fn, {some, data})

Jaynes does the following:

1. 

To Develop
----------

.. code-block:: bash

    git clone https://github.com/episodeyang/jaynes.git
    cd jaynes
    make dev

To test, run

.. code-block:: bash

    make test

This ``make dev`` command should build the wheel and install it in your
current python environment. Take a look at the
`https://github.com/episodeyang/jaynes/blob/master/Makefile <https://github.com/episodeyang/jaynes/blob/master/Makefile>`__ for details.

**To publish**, first update the version number, then do:

.. code-block:: bash

    make publish


