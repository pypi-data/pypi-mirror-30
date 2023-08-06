pyATS - Cisco Python Automated Test System
==========================================

pyATS is an end-to-end testing ecosystem, specializing in data-driven and 
reusable testing, and engineered to be suitable for Agile, rapid development 
iterations. Extensible by design, pyATS enables developers start with small, 
simple and linear test cases, and scale towards large, complex and asynchronous 
test suites.

pyATS is initially developed internally in Cisco, and is now available to the
general public starting late 2017 through `Cisco DevNet`_. Visit the pyATS
home page at

    https://developer.cisco.com/site/pyats/

.. _Cisco DevNet: https://developer.cisco.com/

pyATS Package
-------------

This is the top-level package of pyATS. Installing it will automatically install
all pyATS components and dependencies.

Requirements
------------

pyATS currently supports Python 3.4+ on Linux & Mac systems. Windows platforms
are not yet supported.

Quick Start
-----------

.. code-block:: console

    $ pip install pyats

    # to install alpha/beta versions, add --pre
    $ pip isntall --pre pyats

For more information on setting up your Python development environment,
such as creating virtual environment and installing ``pip`` on your system, 
please refer to `Virtual Environment and Packages`_ in Python tutorials.

.. _Virtual Environment and Packages: https://docs.python.org/3/tutorial/venv.html

Example
-------

As part of installation, examples showcasing various features & idioms of coding
in pyATS will be copied to your virtual environment under ``examples/`` folder.

In addition, you can also get a copy of these examples here:
    https://github.com/CiscoDevNet/pyats-sample-scripts

The examples are self-explanatory, and includes the necessary instructions on 
how to run them.


