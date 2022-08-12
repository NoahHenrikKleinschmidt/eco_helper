"""
.. _normalise:

This module provides the functionality to normalise raw counts data to TPM or CPM.
It is the core of the ``eco_helper normalise`` command.

Note
----
This subcommand exclusively works with ** TSV ** (tab-delimited) formatted files!

Usage
=====

>>> eco_helper normalise <norm> [--lengths <lengths>] [--gtf <gtf>] [--names] [--output <output>] <input>

where <norm> is the kind of normalisation to perform, which can be eithe ``tpm`` or ``cpm``, <input> is the input file, and <output> is the output file. By default the normalised data will be written to the same file as the input file.
In case of ``tpm`` also the lengths of the transcripts must be provided.
This can be done using the ``--lengths`` option. 

It is possible to provide a `GTF` file to the ``--gtf`` option, instead of a lengths file. 
In this case `eco_helper` will use ``gtftools`` to extract the lengths and use the `merged` transcript length.
Also, using the ``--names`` option the gene names (symbols) can be used instead of gene ids.

Full CLI
========

The full command line of `eco_helper normalise` with all options is as follows:

.. code-block:: bash

    usage: eco_helper normalise [-h] [-o OUTPUT] [-l LENGTHS] [-g GTF] [-n]
                            [-d DIGITS] [-log]
                            {tpm,cpm} input

    Normalise raw cuonts data to TPM or CPM.

    positional arguments:
    {tpm,cpm}             The type of normalisation to perform. Can be either
                            'tpm' or 'cpm'.
    input                 Input file.

    options:
    -h, --help            show this help message and exit
    -o OUTPUT, --output OUTPUT
                            Output file. By default the same as the input with
                            added suffix. The suffix will be either '.cpm' or
                            '.tpm'
    -l LENGTHS, --lengths LENGTHS
                            Lengths file. If not provided, the lengths will be
                            extracted from the GTF file.
    -g GTF, --gtf GTF     Reference GTF file for transcript lengths and/or gene
                            names.
    -n, --names           Use gene names instead of gene ids. This will replace
                            the gene ids (index) in the expression matrix and
                            lengths file with gene symbols from the GTF file or
                            lengths file (if provided). Note, if a length file is
                            provided then it must include gene names in the second
                            column!
    -d DIGITS, --digits DIGITS
                            The number of digits to round the values to.
    -log, --logscale      Use this to log-scale the normalised values.

Using Gene Names
----------------

A note on using gene names instead of gene ids: By default `eco_helper` assumes that your input data uses Ensemble gene Ids as primary identifiers in the first column of your expression matrix.
Therefore, it will use the gene ids as index for extracted lengths and names form a given GTF file. If your data, however, works with gene names (symbols) inistead of ids, then no (tpm) normalisation will be possible
because `eco_helper` is trying to match lengths to genes using their index. If the data works on gene names and the lengths on gene ids then no overlap will be found! To prevent this, use the ``--swap`` when computing
new lengths to swap the gene ids (first column that is used for matching when normalising) with the gene names (second column). If you wish to use the second column for your normalised output file, then use the ``--names`` option.

    Examples:

    >>> eco_helper normalise tpm --swap --gtf gencode.GTF --output my_normalised.tsv my_data.tsv

    In the above example, `my_data.tsv` uses gene names (symbols) instead of gene ids. Therefore,
    when computing new lengths from the GTF file we specify ``--swap`` to make sure the lengths file and our data
    will match. However, `my_output.tsv` will use gene ids as index in the first column.

    >>> eco_helper normalise tpm --names --gtf gencode.GTF --output my_normalised.tsv my_data.tsv

    In this second example, `my_data.tsv` uses gene ids as identifiers. Therefore, we do not need to swap the ids and names when computing the lengths.
    However, `my_output.tsv` will use gene names as index in the first column instead of the gene ids because we specified ``--names``.

    The procedure also works backwards, of course. We can use ``--swap`` and ``--names`` to start with a data file using gene names and generate one that uses gene ids.

"""

from .funcs import *
from .NormTable import NormTable