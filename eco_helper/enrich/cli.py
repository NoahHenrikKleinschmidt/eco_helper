"""
Defines the "enrich" subcommand parser and its arguments
"""

import eco_helper.core.settings as settings


def setup_parser( parent ):

    descr = "This command performs gene set enrichment analysis using `gseapy` on the results of an EcoTyper analysis."
    enrich = parent.add_parser( "enrich", description=descr )
    enrich.add_argument( "input", help = "The directory storing the EcoTyper results." )
    enrich.add_argument( "-o", "--output", help = f"Output directory. By default a '<input>_{settings.gseapy_outdir}' directory within the same location as the input directory.", default = None )
    enrich.add_argument( "-g", "--gene_sets", help = "The reference gene sets to use for enrichment analysis. This can be any number of accepted gene set inputs for gseapy enrichr or prerank.", nargs = "+")
    enrich.add_argument( "-p", "--prerank", help = "Use this to perform gseapy prerank analysis.", action = "store_true" )
    enrich.add_argument( "-e", "--enrichr", help = "Use this to perform gseapy enrichr analysis.", action = "store_true" )
    enrich.add_argument( "-a", "--assemble", help = "By default each cell type will produce a separate file for each cell state enrichment analysis. Using the `--assemble` option, all cell-state files from one cell type will be merged together to a single file. In this case the individual files are removed.", action = "store_true" )
    enrich.add_argument( "-E", "--ecotypes", help = "Use this to only analyse cell-types and states contributing to Ecotypes. In this case each Ecotype will receive a subdirectory with its enrichment results files. Note, in this case the files will *not* be assembled, and any non-Ecotype-contributing cell-type and state will not be analysed.", action = "store_true" )
    enrich.add_argument( "-n", "--notebook", help = "Generate a jupyter notebook to analyse the enrichment results. If this option is specified, then the <intput> argument is interpreted as the filename of the notebook to generate. By specifying '-' as filename a default filename with the dataset name is used.", action = "store_true", default = None )
    enrich.add_argument( "--notebook_config", help = "The configuration file for notebook generation. This is required for the notebook to be generated.", default = None )
    enrich.add_argument( "--pickle", help = "Export a pickle file of the enrichment results as an EnrichmentCollection. This can be used in the web-viewer to further inspect the enrichment results.", action = "store_true", default = None )
    enrich.add_argument( "--organism", help = "Set the reference organism. By default the organism is set to 'human'.", default = "human" )
    enrich.add_argument( "--size", help = "[prerank only] Set the minimum and maximum number of gene matches for the reference gene sets and the data. By default 5 and 500 are used. Note, this will require a two number input for min and max.", type = int, nargs = 2, default = [5, 500] )
    enrich.add_argument( "--permutations", help = "[prerank only] Set the number of permutations to use for the prerank analysis. By default 1000 is used.", type = int, default = 1000 )
    enrich.set_defaults( func = enrich_func )

def enrich_func( args ):
    """
    Perform enrichment analysis on the given Ecotyper results.

    Note
    ----
    This is the core function behind the `eco_helper enrich` command.

    Parameters
    ----------
    args : Namespace
        The arguments passed to the command line.
    """

    import os
    import eco_helper.enrich.notebook as notebook
    import eco_helper.enrich.funcs as funcs
    from eco_helper.enrich.cli_aux import _enrich_all, _enrich_ecotypes, pickle_notebook, pickle

    # Because the notebook itself can call eco_helper enrich we will not call
    # anything else but let the notebook handle everything...

    if args.notebook:
        
            
        if not args.notebook_config:
            raise ValueError( "A notebook configuration file is required for notebook generation." )

        if args.input == "-":
            args.input = None

        nb = notebook.EnrichmentNotebook( config = args.notebook_config )

        # run the notebook to ensure we get enrichment results
        print( "Pre-running notebook to ensure enrichment results are generated..." )
        nb.execute( args.input )

        if nb._enrichment_categories: 
            if nb._enrichr:
                nb.analyse_results( "enrichr" )
            if nb._prerank:
                nb.analyse_results( "prerank" )
        
        print( "Pre-running the notebook to screen enrichment results..." )
        nb.execute( args.input )

        print( f"All Done! Notebook '{nb._filename}' is ready" )

        if args.pickle:
            print( "Exporting a pickle file" )
            pickle_notebook( args )

    else:

        # now we can run the enrichment analysis
        if not args.enrichr and not args.prerank:
            print( "No analysis selected! You must specify the --prerank and/or --enrichr option." )
            return

        # make sure we have a valid output directory
        if args.output is None:
            parent = os.path.dirname( args.input )
            name = os.path.basename( args.input )
            args.output = os.path.join( parent, f"{name}_{settings.gseapy_outdir}" )


        if os.path.exists( args.output ):
            if args.pickle:
                try:
                    print( "Existing results found, exporting a pickle file and exiting" )
                    pickle( args ) 
                    return 
                except:
                    print( "Existing results found, but could not export a pickle file. Recomputing..." )

        if not args.gene_sets: 
            print( "No gene sets were specified." )
            return

        if not os.path.exists( args.output ):
            os.makedirs( args.output, exist_ok = True )

        # make a gene_sets directory in the output directory
        gene_sets_dir = os.path.join( args.output, settings.gene_sets_outdir )
        if not os.path.exists( gene_sets_dir ):
            os.makedirs( gene_sets_dir, exist_ok = True )

        # start by getting the gene sets
        funcs.collect_gene_sets( directory = args.input, outdir = gene_sets_dir, enrichr = args.enrichr, prerank = args.prerank )

        if not args.ecotypes: 
            _enrich_all( gene_sets_dir, args )
        else:
            _enrich_ecotypes( gene_sets_dir, args )    

        if args.pickle:
            print( "Exporting a pickle file" )
            pickle( args ) 
