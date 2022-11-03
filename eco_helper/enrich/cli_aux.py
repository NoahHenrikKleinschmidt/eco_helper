"""
Defines auxiliary functions for the main CLI enrich_func function.
"""

import eco_helper.core as core
import eco_helper.enrich.funcs as funcs


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