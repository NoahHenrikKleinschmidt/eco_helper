"""
Core functions of the normalise submodule.
"""
import pandas as pd
import numpy as np
import re
from alive_progress import alive_bar

import eco_helper.core.terminal_funcs as tfuncs

def call_gtftools( filename : str, output : str,  mode : str = "l" ):
    """
    Calls gtftools from CLI to perform a computation. 
    By default to calculate lengths.

    Parameters
    ----------
    filename : str
        The input GTF file.
    output : str
        The output file.
    mode : str, optional
        The mode of the computation. The default is "l".
        Any valid gtftools mode is allowed.
    """
    cmd = f"gtftools -{mode} {output} {filename}"
    tfuncs.run( cmd )


def add_gtf_gene_names( filename : str, outfile : str, swap_ids_and_names : bool = False, **kwargs ):
    """
    Adds the gene names to the GTF file.

    Parameters
    ----------
    filename : str
        The input GTF file.
    outfile : str
        The output file.
    swap_ids_and_names : bool, optional
        Whether to swap the IDs and names. The default is False.
        If True then the Ids (1st column) and names (2nd column by default)
        will be swapped so that names are the 1st column and IDs are the 2nd column.
    """
    orig = pd.read_csv( filename, sep = "\t", header = None, comment = "#", names = ["chr", "source", "type", "start", "end", "score", "strand", "phase", "attributes"] )
    sep = kwargs.get( "sep", "\t" )
    dest = pd.read_csv( outfile, sep = sep )

    # now extract the gene names using regex and add as a data column...
    pattern = re.compile( 'gene_name "([A-Za-z0-9-.]+)"' )
    orig["gene_name"] = match_regex_pattern( pattern, orig )
    
    # and do the same for the gene_ids
    pattern = re.compile( 'gene_id "([A-Za-z0-9-.]+)"' )
    orig["gene_id"] = match_regex_pattern( pattern, orig )

    # and now merge the two dataframes
    orig = orig[ ["gene_id", "gene_name"] ]
    orig = orig.drop_duplicates()
    dest = dest.merge( orig, left_on = dest.columns[0], right_on = "gene_id" )
    dest = dest.drop( columns = ["gene_id"] )

    # now reorder to place gene_names at second position because normalisation 
    # will by default use the last column so that should be one of the length 
    # columns not the gene_names...
    cols = dest.columns.tolist()
    idx = 0 if swap_ids_and_names else 1
    cols.insert( idx, "gene_name" )
    del cols[-1]
    dest = dest[ cols ]

    # and write to files, we also save the Id to Name assignment in a separate file since it may be convenient...
    dest.to_csv( outfile, sep = sep, index = False )
    orig.to_csv( f"{filename}.names", sep = "\t", index = False )
    


def match_regex_pattern( pattern : str, df : pd.DataFrame ):
    """
    Matches a regex pattern to a dataframe using it's "attributes" column.

    Parameters
    ----------
    pattern : str
        The regex pattern.
    df : pd.DataFrame
        The dataframe.

    Returns
    -------
    list
        The matched values.
    """
    matches = map( lambda x : re.search( pattern, x ), df["attributes"] )
    matches = [ i.group(1) if i is not None else i for i in matches ]
    return matches 



def round_values( values : np.ndarray, digits : int = 5 ):
    """
    Rounds an array of values to a certain number of digits.

    Parameters
    ----------
    values : np.ndarray
        The raw values.
    digits : int, optional
        The number of digits to round to. The default is 5.

    Returns
    -------
    np.ndarray
        The rounded values.
    """
    # the for loop seems to work better than a vectorized approach, perhaps due to less memory use?
    iterations = np.arange( values.shape[1] )
    with alive_bar( values.shape[1], title = f"Rounding to {digits} digits" ) as bar:
        for i in iterations:
            col = values[:,i]
            col = np.round( col, digits )
            values[:,i] = col
            bar()
    # logger.debug( f"At the end of round_values {values.shape=}" )
    return values



def array_to_tpm( array : np.ndarray, lengths : np.ndarray, log : bool = False ):
    """
    Convert raw counts to TPM.

    Parameters
    ----------
    array : np.ndarray
        The raw counts. As a 2D ndarray.
    lengths : np.ndarray
        The lengths of the features. As a 1D ndarray.
    log : bool, optional
        Whether to use log-scale. The default is False.
    Returns
    -------
    np.ndarray
        The TPM values.
    """
    
    # first convert to log-scale
    log_length = np.log( lengths )
    tpm = np.log( array )

    # now iterate over each column and convert to TPM
    # and store the converted data
    # The for-loop is faster than a vectorised operation, possibly due to lower-memory consumption?
    factor = np.log(10**6) 
    iterations = np.arange( tpm.shape[1] )
    with alive_bar( tpm.shape[1], title = "Converting to TPM" ) as bar:
        for i in iterations:
            col = tpm[:,i]
            col = col - log_length

            colsum = np.exp( col )
            colsum = np.sum( colsum ) 
            colsum = np.log( colsum )

            tpm[:,i] = np.exp( col - colsum + factor )
            bar()
    if log: 
        tpm = np.log( tpm + 1 )
        
    # logger.debug( f"At the end of array_to_tpm {tpm.shape=}" )
    return tpm



def array_to_cpm( array : np.ndarray, log : bool = True ):
    """
    Convert raw counts to CPM.

    Parameters
    ----------
    array : np.ndarray
        The raw counts. As a 2D ndarray.
    log : bool, optional
        Whether to use log-scale. The default is True.

    Returns
    -------
    np.ndarray
        The CPM values.
    """
    
    # first convert to log-scale
    cpm = array
    total_sum = np.sum( cpm )
    cpm = cpm / total_sum
    cpm = cpm * 10 ** 6 
    if log: 
        cpm = np.log( cpm + 1 )
    
    # logger.debug( f"At the end of array_to_cpm {tpm.shape=}" )
    return cpm
