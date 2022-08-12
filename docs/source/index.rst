.. eco_helper documentation master file, created by
   sphinx-quickstart on Fri Aug 12 11:37:10 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to eco_helper's documentation!
======================================

`eco_helper` is a command line toolbox for data preprocessing to automate common tasks.
`eco_helper` was specifically designed to automate pre-processing tasks related to working
with the `EcoTyper <https://github.com/digitalcytometry/ecotyper>`_  framework for transcriptomics data.
However, the tasks performed by `eco_helper` can be used for other purposes as well.
While designed primarily as a command line tool, `eco_helper` is also a Python package and can be used directly within python scripts.
In fact, some few functionalities of `eco_helper` can only be accessed via the code API and not via command line. These are minor functions,
however, such as passing kwargs to file-reading functions, and does not impact the usability from command line in most cases.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   eco_helper.convert
   eco_helper.normalise
   eco_helper.format
   eco_helper.core


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
