"""
Read and write tabular dataformats:
    - CSV (Comma Separated Values)
    - TSV (Tab Separated Values)
    - TXT (Space Separated Values)
"""

import pandas as pd

from eco_helper.core.terminal_funcs import stdout

supported_formats = ( "csv", "tsv", "txt" )
"""
The supported tabular data formats (file suffixes).
"""

separators = {
                "csv" : ",",
                "tsv" : "\\t",
                "txt" : " "
            }
"""
The separators corresponding to supported tabular data formats.
"""

def read( filename : str, sep : str, **kwargs ):
    """
    Read a file into a pandas dataframe.

    Parameters
    ----------
    filename : str
        The name of the file to read.
    sep : str
        The separator to use.
    **kwargs
        Any additional keyword arguments to pass to `pd.read_csv`.
    """
    return pd.read_csv(filename, sep = sep, **kwargs)

def read_csv(filename : str, header : int = 0, index : int = None, sep : str = None, **kwargs ):
    """
    Read a CSV file into a pandas dataframe.

    Parameters
    ----------
    filename : str
        The name of the file to read.
    header : int, optional
        The row number of the header.
    sep : str, optional
        The separator to use. By default the separator is inferred based on the first column.
        If a semicolon is found, then the semicolon is used as the separator. If both commas and 
        semicolons are found, then the comma is used.
    index : str, optional
        The column to use as the index.
    **kwargs
        Any additional keyword arguments to pass to `pd.read_csv`.
    """

    if sep is None:
        first_line = stdout( f"head -n 1 {filename}" )
        if "," in first_line:
            sep = ","
        elif ";" in first_line:
            sep = ";"
        else:
            raise ValueError( "Could not infer separator from first line of file. For a CSV file either ',' or ';' have to be used!" )

    return pd.read_csv(filename, header = header, sep = sep, comment = "#", index = index, **kwargs)

def read_tsv(filename : str, header : int = 0, index : int = None, **kwargs ):
    """
    Read a TSV file into a pandas dataframe.

    Parameters
    ----------
    filename : str
        The name of the file to read.
    header : int, optional
        The row number of the header.
    index : str, optional
        The column to use as the index.
    **kwargs
        Any additional keyword arguments to pass to `pd.read_csv`.
    """
    return pd.read_csv(filename, header = header, sep = "\t", comment = "#", index = index, **kwargs)

def read_txt(filename : str, header : int = 0, index : int = None, **kwargs ):
    """
    Read a TXT file into a pandas dataframe.

    Note
    ----
    This assumes the data is " " space separated.

    Parameters
    ----------
    filename : str
        The name of the file to read.
    header : int, optional
        The row number of the header.
    index : str, optional
        The column to use as the index.
    **kwargs
        Any additional keyword arguments to pass to `pd.read_csv`.
    """
    return pd.read_csv(filename, header = header, sep = " ", comment = "#", index = index, **kwargs)

def write_csv(filename : str, df : pd.DataFrame, index : bool = False, sep : str = ",", **kwargs ):
    """
    Write a pandas dataframe to a CSV file.

    Parameters
    ----------
    filename : str
        The name of the file to write.
    df : pd.DataFrame
        The dataframe to write.
    index : bool, optional
        Whether to write the index.
    sep : str, optional
        The separator to use.
    **kwargs
        Any additional keyword arguments to pass to `pd.to_csv`.
    """
    df.to_csv(filename, index = index, sep = sep, **kwargs)

def write_tsv(filename : str, df : pd.DataFrame, index : bool = False, **kwargs ):
    """
    Write a pandas dataframe to a TSV file.

    Parameters
    ----------
    filename : str
        The name of the file to write.
    df : pd.DataFrame
        The dataframe to write.
    index : bool, optional
        Whether to write the index.
    **kwargs
        Any additional keyword arguments to pass to `pd.to_csv`.
    """
    df.to_csv(filename, index = index, sep = "\t", **kwargs)

def write_txt(filename : str, df : pd.DataFrame, index : bool = False, **kwargs ):
    """
    Write a pandas dataframe to a TXT file.

    Note
    ----
    This will write the data as " " space separated.

    Parameters
    ----------
    filename : str
        The name of the file to write.
    df : pd.DataFrame
        The dataframe to write.
    index : bool, optional
        Whether to write the index.
    **kwargs
        Any additional keyword arguments to pass to `pd.to_csv`.
    """
    df.to_csv(filename, index = index, sep = " ", **kwargs)

def write( df : pd.DataFrame, filename : str, sep : str, **kwargs ):
    """
    Write a pandas dataframe to a file.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to write.
    filename : str
        The name of the file to write.
    sep : str
        The separator to use.
    **kwargs
        Any additional keyword arguments to pass to `pd.to_csv`.
    """
    df.to_csv(filename, sep = sep, **kwargs)