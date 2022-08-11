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
| csv    |           |
| tsv    | <tab>     |
| txt    | <space>   |

Usage
=====

    >>> eco_helper convert [--from <from>] [--to <to>] [--output <output>] <input>

    where <input> is the input file and <output> is the output file. The <from> and <to> options are only required if the format is not explicit from the file suffix.
    They are not case sensitive. If the <output> option is not specified, the output file will be the same as the input file with the new format.

Full CLI
========

.. code-block:: bash

    usage: eco_helper convert [-h] [-o OUTPUT] [-r] [--from FMT_IN] [--to FMT_OUT]
                            [-i] [-d DATA] [-m METADATA [METADATA ...]]
                            input

    This command converts between different formats. It is able to convert tabular
    dataformats (csv,tsv,txt) to and from mtx format. It can also extract data
    from a SeuratObject (stored in an RDS file) and convert the data to tabular
    formats.

    positional arguments:
    input                 Input file.

    options:
    -h, --help            show this help message and exit
    -o OUTPUT, --output OUTPUT
                            Output file. By default the same as the input with
                            altered suffix.
    -r, --recursive       Use this to mark the output as a directory rather than
                            a target output file.
    --from FMT_IN         The input format in case it is not evident from the
                            input file suffix.
    --to FMT_OUT          The output format in case it is not evident from the
                            output file suffix.
    -i, --index           Use this to also save the index (rownames) to tabular
                            output files. By default the index will NOT be written
                            to the output files. In case of SeuratObject data this
                            option only applies to metadata tables. The extracted
                            data will **always** have an index.
    -d DATA, --data DATA  [Used only for Seurat-RDS] The data to extract from
                            the SeuratObject. If not specified, by default the
                            'counts' slot will be extracted.
    -m METADATA [METADATA ...], --metadata METADATA [METADATA ...]
                            [Used only for Seurat-RDS] The metadata to extract
                            from the SeuratObject. This may be any number
                            accessible slots or attributes of the SeuratObject. If
                            not specified, by default a 'meta.data' attribute is
                            tried to be extracted.


"""

from .funcs import *