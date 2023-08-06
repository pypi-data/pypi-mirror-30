Jaynes, A Logging Utility for Python Debugging
==============================================

 ## Todo

-  [ ] Write examples and justify ``jaynes``'s existence
-  [ ] add pretty pictures of a ``mole`` and with a notebook.

Done
----

-  [x] rename ``ledger`` to ``jaynes``! because I couldn't get the
   names:

   -  ``ledger``: because somebody took it.
   -  ``parchment``: because somebody took it (>.<)
   -  ``vellum``: they took the calf version too (o\_O )

   So I decided on ``jaynes``! The paper just gets softer :)

Installation
------------

.. code-block:: bash

    pip install jaynes

Usage
-----

.. code-block:: python

    from jaynes import Jaynes

    M = Jaynes()

    M.log('this is a log entry!')

    # Jaynes gives really nice debug traces:
    some_variable = "test"
    M.debug(some_variable)


    # Jaynes can also be used as a code-block timer:
    import time
    M.start(silent=True)
    time.sleep(3.0)
    M.split()
    # Lap Time: 3.0084s

You can even log to a file!

.. code-block:: python

    from jaynes import Jaynes

    jaynes = Jaynes(file="https://github.com/episodeyang/jaynes/blob/master/a_log_file.log")
    jaynes.log('this is a log entry!')
    # and it prints to both std out *and* the log file!

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


