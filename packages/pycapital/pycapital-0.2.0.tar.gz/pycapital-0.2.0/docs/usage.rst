=====
Usage
=====

This program can be imported into other Python programs or run from the
commandline.


Importing pycapital
###################
To use the program as a module, import pycapitals into your code.
Call the ``pycapital.capital()`` function and pass a country to it as an argument.
The ``capital()`` function will return the capital of that country or a 0 if an invalid
country was passed to it. Capitalisation does not matter::

    >>> from pycapital.pycapital import capital
    >>> capital("Wakanda")
    0
    >>> capital("Germany")
    'Berlin'
    >>> capital("Japan")
    'Tokyo'
    >>> capital("North Korea")
    'Pyongyang'
    >>> capital("lithuania")
    'Vilnius'

Running it from the commandline.
################################

To run PyCapital from the commandline you can do::

    python pycapital.py

OR ::

    $ chmod +x pycapital.py
    $ ./pycapital.py <country name>

For detailed help information::

    $ ./pycapital.py --help

    usage: pycapital [country]

    Displays capital city of specified country.

    positional arguments:
      country     Displays the capital of country.

    optional arguments:
      -h, --help  show this help message and exit
