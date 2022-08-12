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

There are three primary commands offered by ``eco_helper``:

>>> eco_helper convert 

    The :ref:`convert <convert>` command is used to convert data from one format to another.
    Supported formats are tabular formats such as TSV, Matrix Transfer Archive (mtx), and 
    SeuratObjects stored in RDS files.

>>> eco_helper normalise

    The :ref:`normalise <normalise>` command is used to normalise data to TPM or CPM.

>>> eco_helper format

    The :ref:`format <format>` command is used to reformat data columns and headers from a tabular file.
    The purpose of this is to eliminate invalid characters for downstream software. For instance,
    `EcoTyper` does not accept spaces or minuses in the column headers or index. Therefore, using 
    this command one can replace automatically such characters (or any other regex pattern).

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


   Short disclaimer on the logo: 
   The logo is, obiously, a derivative of the original EcoTyper logo. 
   No infringement is intended, all credits go to the original designer in the EcoTyper development team. 