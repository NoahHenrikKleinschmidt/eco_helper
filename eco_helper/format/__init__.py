"""
This module provides the functionality to re-format data columns and/or rows by regex-based substitutions.
It is the core of the ``eco_helper format`` command.

Usage
=====

    >>> eco_helper format [--index] [--names] [--columns <columns>] [--output <output>] [--pseudo] [--formats <formats>] <input>

where ``<input>`` is the input file and ``<output>`` is the output file. By default the reformatted data will be written to the same file as the input file.
Using the ``--index`` option, the data index will be re-formatted. 
Using the ``--names`` option, the data headers (column names) will be re-formatted.
``<columns>`` can be any number of specific columns present within the input file.

The ``--pseudo`` option can be used to exclusively re-format the index and column headers of a data file. 
In this case only these parts of the file will be read without loading the entire data and thus saving memory. 
This is intended for large data files that would otherwise consume large resources or time. 
Note, that when speciying ``--pseudo`` then other options such as ``--index`` or ``--columns`` are ignored.

A file specifying a python dictionary `regex` patterns can be passed to the --formats option. 
Alternatively, `eco_helper` offers the "EcoTyper" format which will simply replace "-" by "." and " " (space) by "_". 
To use this simply pass ``--format EcoTyper``.

Full CLI
========

The full command line of `eco_helper format` with all options is as follows:

.. code-block:: bash

    usage: eco_helper format [-h] [-o OUTPUT] [-f FORMAT] [-s SUFFIX] [-i]
                            [-iname INDEXNAME] [-noid] [-n]
                            [-c COLUMNS [COLUMNS ...]] [-p] [-sep SEPARATOR] [-e]
                            [-ee] [-a]
                            input

    Fix annotations in columns, index, and column names of tabular data files such
    as expression matrices and annotation files.

    positional arguments:
    input                 The input file.

    options:
    -h, --help            show this help message and exit
    -o OUTPUT, --output OUTPUT
                            The output path. By default the file is saved to the
                            same path it was read from (thereby overwriting the
                            previous one!).
    -f FORMAT, --format FORMAT
                            A file specifying a dictionary of regex patterns for
                            replacement.
    -s SUFFIX, --suffix SUFFIX
                            A suffix to add to the output file. This will not
                            affect the file format and only serves to add
                            additional information to the filename.
    -i, --index           Use this if the index should be re-formatted.
    -iname INDEXNAME, --indexname INDEXNAME
                            Use this to specify a name which the index should be
                            given a name in the output file. Since the index is
                            turned to a regular data column, the (replacement)
                            index will not be written anymore.
    -noid, --noindex      Use this if the index should not be written to the
                            output file.
    -n, --names           Use this if the column names (headers) should be re-
                            formatted.
    -c COLUMNS [COLUMNS ...], --columns COLUMNS [COLUMNS ...]
                            Specify any number of columns within the annotation
                            file to reformat values in.
    -p, --pseudo          Use this to only pseudo-read the given file. This is
                            useful when the datafiles are very large to save
                            memory.
    -sep SEPARATOR, --separator SEPARATOR
                            Use this to specify the separator to use when reading
                            the file. By default, the separator is guessed from
                            the file extension. Otherwise `tsv` (for tab), `csv`
                            (for comma), or `txt` (for space) can be specified.
    -e, --expression      A preset for expression matrices equivalent to '--
                            index --names --pseudo'
    -ee, --ecoexpression  A preset for EcoTyper expression matrices equivalent
                            to '--index --names --pseudo --format EcoTyper'
    -a, --annotation      A preset for EcoTyper annotation files corresponding
                            to '--index --indexname ID --columns CellType Sample
                            --format EcoTyper'
"""

from .funcs import *
from .Formatter import Formatter