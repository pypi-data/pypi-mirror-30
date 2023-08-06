
nr-common
=========


.. image:: https://travis-ci.org/nitred/nr-common.svg?branch=master
   :target: https://travis-ci.org/nitred/nr-common
   :alt: Build Status


Common python functionalities aimed to be at least compatible with Python3.

Current Stable Version
~~~~~~~~~~~~~~~~~~~~~~

.. code-block::

   0.1.0

Installation
============

pip
^^^

.. code-block::

   pip install nr-common

Development Installation
^^^^^^^^^^^^^^^^^^^^^^^^


* Clone the project.
* Install in Anaconda3 environment
  .. code-block::

     $ conda env create --force -f dev_environment.yml
     $ source activate nr-common
     $ pip install -e .

Test
====

To run the tests:

.. code-block::

   make test

Usage
=====

.. code-block:: python

   from nr_common.pickler import read_pickle, write_pickle
   from nr_common.mproc import mproc_func, mproc_async
   from nr_common.configreader import config_from_path, config_from_env

   from nr_common.blueprints.job_status import job_status_handler, db

Examples
========

.. code-block::

   $ python examples/simple.py

License
=======

MIT
