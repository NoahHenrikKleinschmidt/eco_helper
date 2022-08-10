"""
Using the `convert` subcommand, this module provides the functionality to convert data from one format to another.

Specifically, suported conversions are: 

| from               | to      | backwards |
| ------------------ | ------- | --------- |
| tabular            | tabular | yes       |
| MTX                | tabular | yes       |
| RDS (SeuratObject) | tabular | no        |

    The backward column indicates whether the conversion is possible in both directions.

The tabular data formats supported are:

| format | separator |
| ------ | --------- |
| csv    | ,         |
| tsv    | <tab>     |
| txt    | <space>   |

Usage
=====

    >>> eco_helper convert [--from <from>] [--to <to>] [--output <output>] <input>

    where <input> is the input file and <output> is the output file. The <from> and <to> options are only required if the format is not explicit from the file suffix.
    They are not case sensitive. If the <output> option is not specified, the output file will be the same as the input file with the new format.
"""

from .funcs import *