"""
Using the `format` subcommand, this module provides the functionality to re-format data columns and/or rows by regex-based substitutions.

Note
----
The `format` subcommand uses a Formatter class that specifically works with ** TSV ** files! Make sure to convert your data files to TSV format before 
reformatting them!

Usage
=====

    >>> eco_helper format [--index] [--names] [--columns <columns>] [--output <output>] [--pseudo] [--formats <formats>] <input>

    where <input> is the input file and <output> is the output file. By default the reformatted data will be written to the same file as the input file.
    Using the --index option, the data index will be re-formatted. 
    Using the --names option, the data headers (column names) will be re-formatted.
    <columns> can be any number of specific columns present within the input file.

    The --pseudo option can be used to exclusively re-format the index and column headers of a data file. 
    In this case only these parts of the file will be read without loading the entire data and thus saving memory. 
    This is intended for large data files that would otherwise consume large resources or time. 
    Note, that when speciying --pseudo then other options such as --index or --columns are ignored.

    A file specifying a python dictionary regex patterns can be passed to the --formats option. 
    Alternatively, `eco_helper` offers the "EcoTyper" format which will simply replace "-" by "." and " " by "_". 
    To use this simply pass `--format EcoTyper`.

    There are additional options available that are not shown above. The full options are:

.. code-block:: bash


"""

from .funcs import *
from .Formatter import Formatter