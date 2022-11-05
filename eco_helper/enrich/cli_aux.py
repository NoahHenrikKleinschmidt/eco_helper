"""
Defines auxiliary functions for the main CLI enrich_func function.
"""

import eco_helper.core as core
import eco_helper.enrich.funcs as funcs
from eco_helper.enrich import EnrichmentCollection as col
import yaml, os


def _enrich_all( gene_sets_dir, args ):
    """
    Perform enrichment analysis on all cell-types and states.

    Parameters
    ----------
    gene_sets_dir : str
        The directory containing the gene sets.
    """
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


def _enrich_ecotypes( gene_sets_dir, args ):
    """
    Perform enrichment analysis only on Ecotype-contributing cell-types and states.

    Parameters
    ----------
    gene_sets_dir : str
        The directory containing the gene sets.
    """
    
    ecotypes = core.EcotypeCollection( args.input )

    if args.enrichr:
        funcs.enrichr_ecotypes( 
                                directory = gene_sets_dir, 
                                outdir = args.output, 
                                ecotypes = ecotypes,
                                gene_sets = args.gene_sets, 
                                organism = args.organism 
                            )

    if args.prerank:
        funcs.prerank_ecotypes( 
                                directory = gene_sets_dir, 
                                outdir = args.output, 
                                ecotypes = ecotypes,
                                gene_sets = args.gene_sets, 
                                organism = args.organism,
                                min_size = args.size[0],
                                max_size = args.size[1],
                                permutations = args.permutations
                            )

def _read_from_config( config ):
    """ 
    Read the output directory from the config file. 
    
    Parameters
    ----------
    config : str
        The path to the config file.
    """
    config = yaml.load( open( config, "r" ), Loader = yaml.SafeLoader )
    
    user = os.environ.get("USER")
    parent = config["directories"].get("parent").format(user=user)
    results = config["directories"].get("results").format(parent=parent, user=user)

    name = config["directories"].get("ecotyper_dir").split("/")[-1]
    data_dir = config["directories"].get("enrichment_results").format(parent=parent, results=results, user=user)
    data_dir = os.path.join( data_dir, name )
    
    resolution = "ecotype" if config["enrichment"].get("ecotype_resolution") else "celltype"
    
    enrichr = config["enrichment"].get("enrichr")
    prerank = config["enrichment"].get("prerank")
    which = enrichr, prerank
    
    outdir = config["directories"].get("outdir").format(parent=parent, results=results, user=user)
    
    return data_dir, resolution, which, outdir

def pickle_notebook( args ):
    """
    Export a pickled collection when using Notebook mode.
    """
    data_dir, resolution, which, outdir = _read_from_config( args.notebook_config )

    if resolution != "ecotype":
        print( "Pickle export is only supported for EcoType-resolution collection" )
        return

    if args.input != "-":
        filename = args.input.replace("ipynb", "") + ".pkl" 
    else:
        filename = os.path.join( outdir, "{which}" + ".pkl" )

    if which[0]:
        collection = col( data_dir, "ecotype", "enrichr" )
        collection._compute_log( "Combined Score", "Adjusted P-value" )
        collection.save( filename.format(which = "enrichr") )
        print( "Enrichr collection saved to: {}".format( filename.format(which = "enrichr") ) )

    if which[1]:
        collection = col( data_dir, "ecotype", "prerank" )
        collection._compute_log( "NES", "FWER p-val" )
        collection.save( filename.format(which = "prerank") )
        print( "Prerank collection saved to: {}".format( filename.format(which = "prerank") ) )
   

def pickle( args ):
    """
    Export a pickled collection
    """
    if not args.ecotypes:
        print( "Pickle export is only supported for EcoType-resolution collection" )
        return

    if args.enrichr:
        collection = col( args.output, "ecotype", "enrichr" )
        collection._compute_log( "Combined Score", "Adjusted P-value" )
        collection.save( os.path.join( args.output, "enrichr.pkl" ) )
        print( "Enrichr collection saved to: {}".format( os.path.join( args.output, "enrichr.pkl" ) ) )

    if args.prerank:
        collection = col( args.output, "ecotype", "prerank" )
        collection._compute_log( "NES", "FWER p-val" )
        collection.save( os.path.join( args.output, "prerank.pkl" ) )  
        print( "Prerank collection saved to: {}".format( os.path.join( args.output, "prerank.pkl" ) ) )