========
Overview
========



A module for calculation of PCA and PLS with the NIPALS algorithm. Based on the R packages
`nipals <https://cran.r-project.org/package=nipals>`_ and
`pcaMethods <https://doi.org/10.18129/B9.bioc.pcaMethods>` as well as the
statistical appendixes to "Introduction to Multi- and Megavariate Data Analysis
using Projection Methods (PCA & PLS)" by Eriksson et. al.
Tested to give same results as the above packages and Simca, with some rounding errors.


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

0.4.1 (2018-04-09)
------------------

* Fixed bug with cross validation of PCA

0.4.0 (2018-04-09)
------------------

* Added cross validations
* Added calculation of distance to model with plots
* Added model overview plots

0.3.0 (2018-04-05)
------------------

* Added R2X and R2Y to the PLS class
* Made plot color selectable also for scoreplots without classes

0.2.0 (2018-03-29)
------------------

* Added a PLS class
* Improved plotting
* Fixed some problems with missing/infinite values

0.1.0 (2018-03-14)
------------------

* First release on PyPI.


