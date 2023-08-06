========
Overview
========



A module for calculation of PCA with the NIPALS algorithm. Based on the R package
`nipals <https://cran.r-project.org/package=nipals>`_.
Tested to give same results as nipals:nipals, with some rounding errors.

Please note that the Gram-Schmidt orthogonalization has not yet been implemented.

* Free software: MIT license

Installation
============

::

    pip install nipals

Documentation
=============

https://python-nipals.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox


Changelog
=========

0.1.0 (2018-03-14)
------------------

* First release on PyPI.


