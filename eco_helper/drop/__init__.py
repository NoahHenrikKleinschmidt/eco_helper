"""
This module provides the functionality to drop sets of entries from the annotation and expression matrix.

.. warning::

    Depending on the size of the expression matrix, this can be very memory consuming! 
    If working on a cluster, make sure to use a node with enough memory.

Usage
=====

    >>> eco_helper drop [--samples <samples>] [--celltypes <celltypes>] [--ids <ids>] <annotation> <expression>

where ``<annotation>`` and ``<expression>`` are an annotation and expression matrix file for Ecotyper. The ``--samples`` option allows to drop entries belonging to specific samples from the dataset (as given by the `Sample` column in the annotation file). 
The ``--celltypes`` option allows to drop entries belonging to specific cell types from the dataset (as given by the `CellType` column in the annotation file). The ``--ids`` option allows to drop specific entries from the dataset (as given by the `ID` column in the annotation file). The ``--samples``, ``--celltypes`` and ``--ids`` may be provided together.

Full CLI
========

.. code-block:: bash

    usage: eco_helper drop [-h] [-o OUTPUT] [-s SAMPLES [SAMPLES ...]] [-c CELLTYPES [CELLTYPES ...]] [-i IDS [IDS ...]] [-scol SAMPLECOL] [-ccol CELLTYPECOL]
                       [-idcol IDCOL]
                       annotation expression

    This command allows removal of entries from EcoTyper datasets.

    positional arguments:
    annotation            The file storing the annotations.
    expression            The file storing the expression matrix.

    options:
    -h, --help            show this help message and exit
    -o OUTPUT, --output OUTPUT
                            The output basename. This will generate a <basename>.annotation.tsv and <basename>.expression.tsv file. By default, the input filenames are
                            appended by '.drop' at the end.
    -s SAMPLES [SAMPLES ...], --samples SAMPLES [SAMPLES ...]
                            The samples whose entries to drop
    -c CELLTYPES [CELLTYPES ...], --celltypes CELLTYPES [CELLTYPES ...]
                            The cell-types whose entries to drop
    -i IDS [IDS ...], --ids IDS [IDS ...]
                            Specific entries to drop
    -scol SAMPLECOL, --samplecol SAMPLECOL
                            The column containing the sample annotations. By default EcoTyper-friendly 'Sample' is assumed.
    -ccol CELLTYPECOL, --celltypecol CELLTYPECOL
                            The column containing the cell-type annotations. By default EcoTyper-friendly 'CellType' is assumed.
    -icol IDCOL, --idcol IDCOL
                            The column containing the entry identifiers. By default EcoTyper-friendly 'ID' is assumed.
"""

from .funcs import *
