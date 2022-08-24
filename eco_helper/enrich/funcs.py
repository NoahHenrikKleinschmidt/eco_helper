"""
These are the main functions that are used by ``eco_helper enrich``.
"""

import glob
import os
import pandas as pd
import eco_helper.core as ec
import gseapy as gp
from alive_progress import alive_bar

def collect_gene_sets( directory : str, outdir : str, enrichr : bool = True, prerank : bool = False ):
    """
    Collect gene sets from a EcoTyper output directory for subsequent gene set enrichment analysis.

    Parameters
    ----------
    directory : str
        The path to the EcoTyper output directory.
    outdir : str
        The path to the output directory.
    enrichr : bool
        Set to True to export only gene names for subsequent `gseapy enrichr`.
    prerank : bool
        Set to True to export gene names with max. Fold Change for `pseapy prerank` analysis.
    """
    collection = ec.CellStateCollection( [directory] )
    collection.export_to_gseapy( directory = outdir, prerank = prerank, enrichr = enrichr )

def enrichr( directory : str, outdir : str, gene_sets : list or str = "KEGG_2021_Human", organism : str = "human" ):
    """
    Perform gene set enrichment using `gseapy enrichr` for each cell type and each cell-state therein.

    Parameters
    ----------
    directory : str
        The path to the directory where extracted gene sets are stored in separate text files.
        Note, if both prerank and enrichr sets were extracted, this will automatically adjust to the `gseapy_enrichr` subdirectory if necessary.
    outdir : str
        The path to the output directory.
    gene_sets : list or str
        The gene sets to use for enrichment analysis. By default the latest KEGG gene sets are used.
    organism : str
        The organism to use for enrichment analysis. By default "human" is assumed.
    """

    if isinstance( gene_sets, str ):
        gene_sets = [gene_sets]

    directory, tmpdir, outdir = _enrichr_prep_directories(directory, outdir)
    
    files = os.listdir( directory )
    with alive_bar( len( files ), title = "Performing gseapy enrichr" ) as bar:
        for file in files:
            
            # perpare the filenames for enrichment analysis
            infile = os.path.join( directory, file )
            outfile = f"{file}{ec.settings.enrichr_results_suffix}"

            # perform enrichr analysis
            gp.enrichr( 
                        gene_list = infile, 
                        outdir = tmpdir, 
                        gene_sets = gene_sets,
                        organism = organism,
                        no_plot = True,
                    )
            
            # merge the temporary files into one for each cell type and cell state
            textfiles = glob.glob( os.path.join( tmpdir, "*.txt" ) )
            textfiles = [ pd.read_csv( file, sep = "\t" ) for file in textfiles ]
            final = pd.concat( textfiles )
            final.to_csv( os.path.join( outdir, outfile ), sep = "\t", index = False )

            bar()

    # remove the temporary directory
    os.system( f"rm -r {tmpdir}" )

def prerank( directory : str, outdir : str, gene_sets : list or str = "KEGG_2021_Human", organism : str = "human", min_size : int = 5, max_size = 500, permutations : int = 1000, **kwargs ):
    """
    Perform gene set enrichment using `gseapy prerank` for each cell type and each cell-state therein.

    Parameters
    ----------
    directory : str
        The path to the directory where extracted gene sets are stored in separate text files.
        Note, if both prerank and prerank sets were extracted, this will automatically adjust to the `gseapy_prerank` subdirectory if necessary.
    outdir : str
        The path to the output directory.
    gene_sets : list or str
        The gene sets to use for enrichment analysis. By default the latest KEGG gene sets are used.
    organism : str
        The organism to use for enrichment analysis. By default "human" is assumed.
    min_size : int
        The minimum number of genes required to be found in a gene set. 
    max_size : int
        The maximum number of genes allowed to be found in a gene set.
    permutations : int
        The number of permutations to use for the permutation test.
    **kwargs
        Any additional keyword arguments to pass to `gseapy.prerank`.
    """

    if isinstance( gene_sets, str ):
        gene_sets = [gene_sets]

    directory, tmpdir, outdir = _prerank_prep_directories(directory, outdir)
    
    files = os.listdir( directory )
    with alive_bar( len( files ), title = "Performing gseapy prerank" ) as bar:
        for file in files:
            
            # perpare the filenames for enrichment analysis
            infile = os.path.join( directory, file )
            outfile = f"{file}{ec.settings.prerank_results_suffix}"

            # perform prerank analysis
            gp.prerank( 
                        rnk = infile, 
                        outdir = tmpdir, 
                        gene_sets = gene_sets,
                        organism = organism,
                        min_size = min_size,
                        max_size = max_size,
                        permutation_num = permutations,
                        no_plot = True,
                        **kwargs
                    )
            
            # merge the temporary files into one for each cell type and cell state
            # NOTE: prerank makes CSV files not TSV files!
            textfiles = glob.glob( os.path.join( tmpdir, "*.csv" ) )
            textfiles = [ pd.read_csv( file, sep = "," ) for file in textfiles ]
            final = pd.concat( textfiles )
            final.to_csv( os.path.join( outdir, outfile ), sep = "\t", index = False )

            bar()

    # remove the temporary directory
    os.system( f"rm -r {tmpdir}" )

def assemble_enrichr_results( directory : str, cell_types : ec.CellTypeCollection, outdir : str = None, remove_raw : bool = True ):
    """
    Assemble the raw per cell-type and cell-state enrichr output text files into a single file per cell-type including all respective cell states. 

    Parameters
    ----------
    directory : str
        The directory storing the raw enrichr output files for each cell type and state.
    cell_types : CellTypeCollection
        The cell types to use for assembling the results.
    outdir : str
        The output directory to store the assembled results. 
        If not specified, the results will be stored in the same directory as the raw enrichr results.
    remove_raw : bool
        If True, the raw enrichr results will be removed after assembling.
    """
    if outdir is None:
        outdir = directory
    for cell_type in cell_types:
        
        # merge the individual datafiles of cell-type and cell-states therein into one
        files, final = _merge_dataframes(directory, cell_type)
        outfile = os.path.join( outdir, f"{cell_type}{ec.settings.enrichr_results_suffix}" )
        final.to_csv( outfile, sep = "\t", index = False )

        _remove_raw_files(remove_raw, files)

def assemble_prerank_results( directory : str, cell_types : ec.CellTypeCollection, outdir : str = None, remove_raw : bool = True ):
    """
    Assemble the per-state prerank output text files into a single file per cell type. 

    Parameters
    ----------
    directory : str
        The directory storing the raw prerank output files for each cell type and state.
    cell_types : CellTypeCollection
        The cell types to use for assembling the results.
    outdir : str
        The output directory to store the assembled results. 
        If not specified, the results will be stored in the same directory as the raw prerank results.
    remove_raw : bool
        If True, the raw prerank results will be removed after assembling.
    """
    if outdir is None:
        outdir = directory
    for cell_type in cell_types:
        
        # merge the individual datafiles of cell-type and cell-states therein into one
        files, final = _merge_dataframes(directory, cell_type)
        outfile = os.path.join( outdir, f"{cell_type}{ec.settings.prerank_results_suffix}" )
        final.to_csv( outfile, sep = "\t", index = False )

        _remove_raw_files(remove_raw, files)

def _enrichr_prep_directories(directory, outdir):
    """
    Prepare the input and output directories for enrichr analysis. This will also create the tmpdir.

    Parameters
    ----------
    directory : str
        The path to the directory where extracted gene sets are stored in separate text files.
        Note, if both prerank and enrichr sets were extracted, this will automatically adjust to the `gseapy_enrichr` subdirectory if necessary.
    outdir : str
        The path to the output directory.
    """
    if ec.settings.enrichr_outdir in os.listdir( directory ):
        directory = os.path.join( directory, ec.settings.enrichr_outdir )
    
    outdir, tmpdir = _prep_out_and_tmpdir(directory, outdir)
        
    return directory, tmpdir, outdir

def _prerank_prep_directories(directory, outdir):
    """
    Prepare the input and output directories for prerank analysis. This will also create the tmpdir.

    Parameters
    ----------
    directory : str
        The path to the directory where extracted gene sets are stored in separate text files.
        Note, if both prerank and prerank sets were extracted, this will automatically adjust to the `gseapy_prerank` subdirectory if necessary.
    outdir : str
        The path to the output directory.
    """
    if ec.settings.prerank_outdir in os.listdir( directory ):
        directory = os.path.join( directory, ec.settings.prerank_outdir )
    
    outdir, tmpdir = _prep_out_and_tmpdir(directory, outdir)
        
    return directory, tmpdir, outdir

def _prep_out_and_tmpdir(directory, outdir):
    """
    Prepare the output and temporary directories for enrichr analysis. This will also create the tmpdir.
    """
    if outdir == directory: 
        outdir = os.path.join( outdir, ec.settings.gseapy_outdir )

    tmpdir = os.path.join( outdir, "__tmp" )
    if not os.path.exists( tmpdir ): 
        os.mkdir( tmpdir )
    return outdir, tmpdir

def _remove_raw_files(remove_raw, files):
    """
    Remove raw enrichment data files for cell types and cell states.

    Parameters
    ----------
    remove_raw : bool
        If True, the raw enrichment data files will be removed.
    files : list
        The list of files to remove.
    """
    if remove_raw:
        files = " ".join( files )
        os.system( f"rm {files}" )

def _merge_dataframes(directory, cell_type):
    """
    Merge the datafiles into a single dataframe.

    Parameters
    ----------
    directory : str
        The directory storing the raw enrichment output files for each cell type and state.
    cell_type : str
        The cell type whose raw files to assemble.
    
    Returns
    -------
    files : list
        The list of files contributing to the merged data (for later removal).
    final : pd.DataFrame
        The final dataframe containing the merged data.
    """
    # get the corresponding prerank or enrichr files
    files = glob.glob( os.path.join( directory, cell_type + "_*" ) )

    # get the states associated with each file by splitting through <cell_type>_<state>.txt.<prerank|enrichr>.txt
    states = [ i[ i.rfind( "_" ) + 1 : ].split(".")[0] for i in files ]

    # now read the dataframes and add the state
    dfs = [ pd.read_csv( file, sep = "\t" ) for file in files ]
    for df, state in zip(dfs, states): 
        df.insert( 0, ec.settings.state_col, state ) 
        
    # concatenate and save the final dataframe
    final = pd.concat( dfs )
    return files, final