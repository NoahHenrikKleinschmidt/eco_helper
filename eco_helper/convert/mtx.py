"""
Read and write Matrix Transfer Archive (MTX) formats.
"""

import os
import pandas as pd
from scipy.io import mmread, mmwrite


def read( filename: str ):
    """
    Reads an mtx file and returns a pandas dataframe.

    Parameters
    ----------
    filename : str
        The name of the mtx file to read.

    Returns
    -------
    pandas.DataFrame
        The dataframe containing the mtx data.
    """
    data = pd.DataFrame( mmread( filename ) )
    data = add_names( data, filename )
    return data

def write( data : pd.DataFrame, filename : str ):
    """
    Writes a dataframe to an mtx file.

    Parameters
    ----------
    data : pandas.DataFrame
        The dataframe to write.
    filename : str
        The name of the mtx file.
    """
    # write the actual array
    mmwrite( filename, data)
    
    # write the column names
    if isinstance( data.columns.values[0], str ):
        cols = filename.replace( ".mtx", ".mtx_cols" )
        with open( cols, "w" ) as f:
            f.write( "\n".join( data.columns ) )
        
    # write the row names
    if isinstance( data.index.values[0], str ):
        rows = filename.replace( ".mtx", ".mtx_rows" )
        with open( rows, "w" ) as f:
            f.write( "\n".join( data.index ) )
    
def add_names( data : pd.DataFrame, filename : str ):
    """
    Adds column and row names to a dataframe.

    Parameters
    ----------
    data : pandas.DataFrame
        The dataframe to add names to.
    filename : str
        The name of the mtx file.

    Returns
    -------
    pandas.DataFrame
        The dataframe with names.
    """

    cols = filename.replace( ".mtx", ".mtx_cols" )
    if os.path.exists( cols ):
        cols = pd.read_csv( 
                                cols, 
                                sep = "\t", header = None, names = ["name"] 
                            )
        data.columns = cols.name.values

    rows = filename.replace( ".mtx", ".mtx_rows" )
    if os.path.exists( rows ):
        rows = pd.read_csv( 
                            rows, 
                            sep = "\t", header = None, names = ["name"] 
                        )
        data.index = rows.name.values

    return data