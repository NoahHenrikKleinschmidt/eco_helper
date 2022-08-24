"""
Defines the "enrich" subcommand parser and its arguments
"""

import os
import eco_helper.core as core
import eco_helper.enrich.funcs as funcs
import eco_helper.core.settings as settings

def setup_parser( parent ):

    descr = "This command performs gene set enrichment analysis using `gseapy` on the results of an EcoTyper analysis."
    enrich = parent.add_parser( "enrich", description=descr )
    enrich.add_argument( "input", help = "The directory storing the EcoTyper results." )
    enrich.add_argument( "-o", "--output", help = f"Output directory. By default a '<input>_{settings.gseapy_outdir}' directory within the same location as the input directory.", default = None )
    enrich.add_argument( "-g", "--gene_sets", help = "The reference gene sets to use for enrichment analysis. This can be any number of accepted gene set inputs for gseapy enrichr or prerank.", required = True, nargs = "+")
    enrich.add_argument( "-p", "--prerank", help = "Use this to perform gseapy prerank analysis.", action = "store_true" )
    enrich.add_argument( "-e", "--enrichr", help = "Use this to perform gseapy enrichr analysis.", action = "store_true" )
    enrich.add_argument( "-a", "--assemble", help = "By default each cell type will produce a separate file for each cell state enrichment analysis. Using the `--assemble` option, all cell-state files from one cell type will be merged together to a single file. In this case the individual files are removed.", action = "store_true" )
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

    # make sure we have a valid output directory
    if args.output is None:
        parent = os.path.dirname( args.input )
        name = os.path.basename( args.input )
        args.output = os.path.join( parent, f"{name}_{settings.gseapy_outdir}" )

    if not os.path.exists( args.output ):
        os.makedirs( args.output, exist_ok = True )
    
    # make a gene_sets directory in the output directory
    gene_sets_dir = os.path.join( args.output, settings.gene_sets_outdir )
    if not os.path.exists( gene_sets_dir ):
        os.makedirs( gene_sets_dir, exist_ok = True )

    # start by getting the gene sets
    funcs.collect_gene_sets( directory = args.input, outdir = gene_sets_dir, enrichr = args.enrichr, prerank = args.prerank )

    # now we can run the enrichment analysis
    if not args.enrichr and not args.prerank:
        print( "No analysis selected! You must specify the --prerank and/or --enrichr option." )
        return

    if args.enrichr: 
        funcs.enrichr( 
                        directory = gene_sets_dir, 
                        outdir = args.output, 
                        gene_sets = args.gene_sets, 
                        organism = args.organism 
                    )
        if args.assemble:
            cell_types = core.CellTypeCollection( args.input )
            funcs.assemble_enrichr_results( directory = args.output, cell_types = cell_types, remove_raw = True )

    if args.prerank:
        funcs.prerank( 
                        directory = gene_sets_dir, 
                        outdir = args.output, 
                        gene_sets = args.gene_sets, 
                        organism = args.organism,
                        min_size = args.size[0],
                        max_size = args.size[1],
                        permutations = args.permutations
                    )
        if args.assemble:
            cell_types = core.CellTypeCollection( args.input )
            funcs.assemble_prerank_results( directory = args.output, cell_types = cell_types, remove_raw = True )
