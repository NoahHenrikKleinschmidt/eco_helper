"""
This module provides the functionality to perform gene-set enrichment analysis on the results of an Ecotyper run.

`eco_helper` uses the `gseapy package <https://github.com/zqfang/GSEApy>`_ to perform gene set enrichment analysis.

Usage
=====

    >>> eco_helper enrich [--prerank] [--enrichr] [--assemble] [--gene_sets <gene sets>] [--output <output>] <input>

where ``<input>`` is the path to the EcoTyper results directory, and ``<output>`` is the path to the output directory.
`eco_helper` offers by default either the `gseapy prerank` (``--prerank`` option) or the `enrichr` method (``--enrichr`` option) for gene set enrichment analysis. 
Both can be passed at the same time.
By default each cell-type will produce a separate data file for each of its cell-states. Using the ``--assemble`` option,
these individual files will be merged into one single data file for each cell type, including the enrichment results for all its cell-states.
In this case the individual files will be removed. 
The ``--gene_sets`` option can be used to specify the reference gene sets to query when performing the enrichment analysis. Multiple inputs of any format that are accepted by `gseapy` are allowed, and at least one input is required.

Full CLI
========

.. code-block:: bash

    usage: eco_helper enrich [-h] [-o OUTPUT] -g GENE_SETS [GENE_SETS ...] [-p]
                         [-e] [-a] [--organism ORGANISM] [--size SIZE SIZE]
                         [--permutations PERMUTATIONS]
                         input

    This command performs gene set enrichment analysis using `gseapy` on the
    results of an EcoTyper analysis.

    positional arguments:
    input                 The directory storing the EcoTyper results.

    options:
    -h, --help            show this help message and exit
    -o OUTPUT, --output OUTPUT
                            Output directory. By default a '<input>_gseapy_results'
                            directory within the in the same location as the input directory.
    -g GENE_SETS [GENE_SETS ...], --gene_sets GENE_SETS [GENE_SETS ...]
                            The reference gene sets to use for enrichment
                            analysis. This can be any number of accepted gene set
                            inputs for gseapy enrichr or prerank.
    -p, --prerank         Use this to perform gseapy prerank analysis.
    -e, --enrichr         Use this to perform gseapy enrichr analysis.
    -a, --assemble        By default each cell type will produce a separate file
                            for each cell state enrichment analysis. Using the
                            `--assemble` option, all cell-state files from one
                            cell type will be merged together to a single file. In
                            this case the individual files are removed.
    --organism ORGANISM   Set the reference organism. By default the organism is
                            set to 'human'.
    --size SIZE SIZE      [prerank only] Set the minimum and maximum number of
                            gene matches for the reference gene sets and the data.
                            By default 5 and 500 are used. Note, this will require
                            a two number input for min and max.
    --permutations PERMUTATIONS
                            [prerank only] Set the number of permutations to use
                            for the prerank analysis. By default 1000 is used.


Performing both ``enrichr`` and ``prerank``
===========================================

It is possible to supply both ``--prerank`` and ``--enrichr`` at the same time,
in which case both analyses are preformed. However, it is a known issue that occasionally 
the progress bar in the prerank analysis, which is performed after the enrichr analysis, gets stuck for currently unknown reasons causing the analysis to fail.
A safe option is to simply run the enrich commands separately, once with ``--prerank`` and once with ``--enrichr``.

    >>> eco_helper enrich --enrichr --prerank --gene_sets Reactome_2016 my_ecotyper_run

    In case the above command should fail, separating enrichr and prerank should fix the problem.

    >>> eco_helper enrich --enrichr --gene_sets Reactome_2016 my_ecotyper_run
    
    >>> eco_helper enrich --prerank --gene_sets Reactome_2016 my_ecotyper_run
"""

from .funcs import *
