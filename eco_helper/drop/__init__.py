"""
This module provides the functionality to drop sets of entries from the annotation and expression matrix.


Usage
=====

    >>> eco_helper drop [--samples <samples>] [--celltypes <celltypes>] [--ids <ids>] <annotation> <expression>

where ``<annotation>`` and ``<expression>`` are an annotation and expression matrix file for Ecotyper. The ``--samples`` option allows to drop entries belonging to specific samples from the dataset (as given by the `Sample` column in the annotation file). 
The ``--celltypes`` option allows to drop entries belonging to specific cell types from the dataset (as given by the `CellType` column in the annotation file). The ``--ids`` option allows to drop specific entries from the dataset (as given by the `ID` column in the annotation file). The ``--samples``, ``--celltypes`` and ``--ids`` may be provided together.

Full CLI
========

.. code-block:: bash

     STUFF NEEDS TO BE ADDED HERE
"""

from .funcs import *
