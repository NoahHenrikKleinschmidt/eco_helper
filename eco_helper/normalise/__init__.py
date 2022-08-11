"""
Using the `normalise` subcommand, this module provides the functionality to normalise raw counts data to TPM or CPM.

Note
----
This subcommand exclusively works with ** TSV ** formatted files!

Usage
=====

>>> eco_helper normalise <norm> [--lengths <lengths>] [--gtf <gtf>] [--names] [--output <output>] <input>

where <norm> is the kind of normalisation to perform, which can be eithe ``tpm`` or ``cpm``, <input> is the input file, and <output> is the output file. By default the normalised data will be written to the same file as the input file.
In case of ``tpm`` also the lengths of the transcripts must be provided.
This can be done using the ``--lengths`` option. 
It is possible to provide a `GTF` file to the ``--gtf`` option, instead of a lengths file. In this case `eco_helper` will use ``gtftools`` to extract the lengths and use the `merged` transcript length.
Also, using the ``--names`` option the gene names (symbols) can be used instead of gene ids.

Full CLI
========

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


"""

from .funcs import *