"""
This is ``eco_helper`` - a package to facilitate data handling and pre-processing for later work with the `EcoTyper framework <https://github.com/digitalcytometry/ecotyper>`_.
The tools offered by this package are all accessible via a command line interface and this is the intended way to use them. 
However, the package can be used directly as a library.

There are three primary commands offered by ``eco_helper``:

>>> eco_helper convert 

    The :ref:`convert` command is used to convert data from one format to another.
    Supported formats are tabular formats such as TSV, Matrix Transfer Archive (mtx), and 
    SeuratObjects stored in RDS files.

>>> eco_helper normalise

    The :ref:`normalise` command is used to normalise data to TPM or CPM.

>>> eco_helper format

    The :ref:`format` command is used to reformat data columns and headers from a tabular file.
    The purpose of this is to eliminate invalid characters for downstream software. For instance,
    `EcoTyper` does not accept spaces or minuses in the column headers or index. Therefore, using 
    this command one can replace automatically such characters (or any other regex pattern).
"""