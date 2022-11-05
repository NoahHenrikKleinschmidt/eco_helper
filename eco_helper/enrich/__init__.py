"""
This module provides the functionality to perform gene-set enrichment analysis on the results of an Ecotyper run.

`eco_helper` uses the `gseapy package <https://github.com/zqfang/GSEApy>`_ to perform gene set enrichment analysis.
By default `gseapy enrichr` and `gseapy prerank` analyses are offered. The former is an API to the `enrichr web service <https://maayanlab.cloud/Enrichr/>`_ that requires only gene names as inputs.
The latter requires an additional "rank" dataset associated with the respective gene names. `eco_helper` uses the associated maximum fold change from each gene within the respective cell state as rank data.


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

    usage: eco_helper enrich [-h] [-o OUTPUT]
                         [-g GENE_SETS [GENE_SETS ...]] [-p] [-e]
                         [-a] [-E] [-n]
                         [--notebook_config NOTEBOOK_CONFIG]
                         [--pickle] [--organism ORGANISM]
                         [--size SIZE SIZE]
                         [--permutations PERMUTATIONS]
                         input

    This command performs gene set enrichment analysis using `gseapy` on the results of an EcoTyper analysis.

    positional arguments:
    input                 The directory storing the EcoTyper results.

    options:
    -h, --help            show this help message and exit
    -o OUTPUT, --output OUTPUT
                            Output directory. By default a '<input>_gseapy_results' directory within the same location as the input directory.
    -g GENE_SETS [GENE_SETS ...], --gene_sets GENE_SETS [GENE_SETS ...]
                            The reference gene sets to use for enrichment analysis. This can be any number of accepted gene set inputs for gseapy enrichr or prerank.
    -p, --prerank         Use this to perform gseapy prerank analysis.
    -e, --enrichr         Use this to perform gseapy enrichr analysis.
    -a, --assemble        By default each cell type will produce a separate file for each cell state enrichment analysis. Using the `--assemble` option, all cell-
                            state files from one cell type will be merged together to a single file. In this case the individual files are removed.
    -E, --ecotypes        Use this to only analyse cell-types and states contributing to Ecotypes. In this case each Ecotype will receive a subdirectory with its
                            enrichment results files. Note, in this case the files will *not* be assembled, and any non-Ecotype-contributing cell-type and state will
                            not be analysed.
    -n, --notebook        Generate a jupyter notebook to analyse the enrichment results. If this option is specified, then the <intput> argument is interpreted as
                            the filename of the notebook to generate. By specifying '-' as filename a default filename with the dataset name is used.
    --notebook_config NOTEBOOK_CONFIG
                            The configuration file for notebook
                            generation. This is required for the
                            notebook to be generated.
    --pickle              Export a pickle file of the enrichment
                            results as an EnrichmentCollection. This
                            can be used in the web-viewer to further
                            inspect the enrichment results.
    --organism ORGANISM   Set the reference organism. By default the
                            organism is set to 'human'.
    --size SIZE SIZE      [prerank only] Set the minimum and maximum
                            number of gene matches for the reference
                            gene sets and the data. By default 5 and
                            500 are used. Note, this will require a two
                            number input for min and max.
    --permutations PERMUTATIONS
                            [prerank only] Set the number of
                            permutations to use for the prerank
                            analysis. By default 1000 is used.

Web-Viewer
==========

The `eco_helper` web-viewer can be used to further inspect the enrichment results. It is a stand-alone `streamlit` web app that can be run locally from command line or `online <https://noahhenrikkleinschmidt-eco-helper-viewer-srcmain-8ju43d.streamlit.app>`_.
It requires a `pickle file` containing an `EnrichmentCollection` object. This can be generated by passing the ``--pickle`` option to the `eco_helper enrich` command.

To run the web-viewer locally, first install `streamlit` and clone the `web-viewer repository <https://github.com/NoahHenrikKleinschmidt/eco_helper_viewer>`_ from github. Then run the following command from the root directory of the repository:

.. code-block:: bash

    streamlit run src/main.py

The web-viewer will then be available by default at `localhost:8501 <http://localhost:8501>`_.

Alternatively, the web-viewer is hosted on streamlit and can be directly accessed `here <https://noahhenrikkleinschmidt-eco-helper-viewer-srcmain-8ju43d.streamlit.app>`_.
It is possible that the app is dormant to save resources. In this case it will take a few seconds to load.


Jupyter Notebook
================

`eco_helper` can auto-generate a jupyter notebook to analyse the enrichment results. This notebook will contain a number of cells for plots to visualise the enrichment results.
To generate a notebook, the ``--notebook`` option must be passed, and a notebook config file must be provided using the ``--notebook_config`` option.

    >>> eco_helper enrich --notebook --notebook_config my_enrichment_config.yaml my_enrichment.ipynb


In this case the notebook will automatically call ``eco_helper enrich`` in case no enrichment results are present yet for the desired dataset. The notebook will also contain cells to call ``eco_helper enrich`` whenever desired - so each notebook is its own little analysis pipeline with input sections, autmated processing, and output sections.
However, certain options such as ``--size`` or ``--organism`` will be missing from the notebook-internal call to ``eco_helper enrich``. Therefore, to retain full customization of the command it is recommended to first run ``eco_helper enrich`` manually to generate the desired enrichment results, and then run again with the notebook option.
If a notebook encounters already existing results it will simply load these and perform its preset analysis without recomputing the enrichment itself (unless forced by the config). 

At the core, the preset analysis consists of highlighting subsets of enriched terms which can be supplied in the notebook config file. The notebook
will automatically pre-scan these subsets and remove any subsets that fall below a cutoff value among the highest most enriched terms for each cell-state dataset.

The notebook will then automatically generate cells to visualise plotly-based interactive scatterplots to quickly visualise the enrichment results and place the retained subsets in dedicated cells for each cell-state.
These cells can later be modified manually by the user of course to generate streamlined figures.
Cells for seaborn figures are also prepared but commented out by default.


Notebook config
---------------

In order to generate a notebook, a config file must be provided. 
This config file is a yaml file which contains the following keys:

.. code-block:: yaml

    # ----------------------------------------------------------------
    #   Main directory settings for input and output data
    # ----------------------------------------------------------------
    directories :

        # available wildcards for filepaths are:
        # - {user}    | the current username
        # - {parent}  | the project parent directory
        # - {results} | the project's raw results directory
        # - {scripts} | the project's scripts directory ( is {parent}/scripts )

        # the ecotyper results directory for which to perform or load results of
        # enrichment analysis.
        ecotyper_dir : "{results}/your_ecotyper_results"
        
        # the directory where outputs (e.g. figures) 
        # from within the notebook should be saved
        outdir : "{parent}/gsea_results/your_ecotyper_results"

        # the project directory
        parent : "/data/users/{user}/EcoTyper"

        # the directory of EcoTyper raw results
        results : "{parent}/results"

        # the directory where outputs from the notebook
        # should be saved (this is an optional 
        # variable to faciliate working with the notebook)
        outdir : "{parent}/gsea_results"

    # ----------------------------------------------------------------
    #   Enrichment analysis settings
    # ----------------------------------------------------------------
    enrichment :

        # enrichment is automatically performed when no 
        # enrichment results are found. If set to True then
        # re-computation of enrichment is forced even 
        # when results are present already.
        perform_enrichment : False

        # if True only ecotype-contributing cell states are analysed
        # and results are stored in ecotype-specific subdirectories.
        # Otherwise all cell states are analysed and stored in cell-type 
        # specific files.
        ecotype_resolution : True

        # perform GSEAPY enrichr
        enrichr : True

        # perform GSEAPY prerank
        prerank : False

        # the reference gene sets against which to query.
        # this can be any input type accepted by GSEAPY
        gene_sets : 
            - "Reactome_2016"
            - "WikiPathway_2021_Human"
            - "Panther_2016"
            - "KEGG_2021_Human"
            - "GO_Biological_Process_2021"
            - "GO_Molecular_Function_2021"
            - "GO_Cellular_Component_2021"

    # ----------------------------------------------------------------
    #   Results analysis settings for automated gene set highlighting
    # ----------------------------------------------------------------
    analysis : 

        # the topmost fraction of enriched terms to use for determining 
        # if a category might be interesting (i.e. wheter or not 
        # to keep it for a speific cell-state).
        top_most_fraction :  0.3

        # the minimum number of hits of a category among the topmost enriched terms 
        # required to keep a category for a specific cell-state.
        cutoff : 5

        # provide a dictionary of reference categories / super-terms
        # which to query within the enrichment datasets in each cell-state.
        # or set to NULL to disable.
        references : 

            # for example highlighting lipid associated terms
            "lipid associated" : 
            - "lipid"
            - "lipo(protein)?"
            - "triacyl"
            - "lipase"
            - "acylglycer"
            - "triglycer"
            - "chylomicron"
            - "fat"
            - "fatty ?-?_?acid"
            - "L( |_|-)?DL"
            - "H( |_|-)?DL"
            - "V( |_|-)?LDL" 
        
            "another category" :
                - "another pattern1"
                - "another pattern2"
"""

from .funcs import *
from .EnrichmentCollection import EnrichmentCollection
from .notebook import EnrichmentNotebook
import eco_helper.enrich.visualise as visualise