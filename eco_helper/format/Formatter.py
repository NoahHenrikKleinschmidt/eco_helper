"""
The main class that handles re-formatting input datafile index, columns, and headers.
"""

import pandas as pd
import logging


import eco_helper.format.formats as _formats
import eco_helper.format.Pseudo as Pseudo
import eco_helper.convert.tabular as tabular
import eco_helper.convert as convert

logger = logging.getLogger( "eco_helper" )

class Formatter:
    """
    A cass to read tabular data files, and re-format 
    index, column names (headers) and/or specific columns using regex substitution.

    Parameters
    ----------
    formats : dict
        A dictionary of invalid characters which must be replaced with a valid character.     
        By default the pre-set `EcoTyper` dictionary is used.
    """
    def __init__( self, formats : dict = None ):
        
        self._formats = _formats.EcoTyper if not formats else formats

        self._df = None
        self._read_sep = None
        self._index_was_set_to_column = False

    def get( self ):
        """
        Returns the dataframe (actual or pseudo).
        """
        return self._df

    def read_table( self, filename : str, sep : str = None, pseudo : bool = False, **kwargs ):
        """
        Reads a tabular data file.

        Parameters
        ----------
        filename : str
            The name of the tabular data file.
        fmt : str
            The tabular format whose separator to use. If not provided, the separator will be guessed from the file extension. Otherwise, `csv` (comma only), `tsv`, and `txt` can be used.
        pseudo : bool
            If True, the dataframe will only be read by the index and column names into a PseudoDataFrame.
            Since this will ** NOT ** store any actual data only the index and column names can be re-formated in this case!
        """
        if not sep: 
            _suffix,_ = convert.filesuffix( filename )
            if _suffix in tabular.separators:
                sep = tabular.separators[ _suffix ]
            else:
                raise ValueError( f"Could not guess the separator to use for {filename}! Specify it manually..." )
        else:
            sep = tabular.separators[ sep ]
        self._read_sep = sep 

        if pseudo:
            self._df = Pseudo.PseudoDataFrame( filename, sep = sep, **kwargs )
        else:
            self._df = pd.read_csv( filename, sep = sep, skipinitialspace = True, quotechar = '"', engine = "python", **kwargs )

    def reformat( self, index : bool, names : bool, columns : list ):
        """
        Reformats parts of the read dataframe.
        """
        if index:
            self._reformat_index()
        if names:
            self._reformat_names()
        if columns:
            self._reformat_columns( columns )

    def index_to_column( self, colname : str ):
        """
        Converts the index of the dataframe to a column.

        Parameters
        ----------  
        colname : str
            The name of the column to store the index.
        """
        self._df[ colname ] = self._df.index.values
        self._df = self._df.reset_index( drop = True )
        self._index_was_set_to_column = True 

    def write_table( self, filename : str, suffix : str = None, **kwargs ):
        """
        Writes the dataframe to a tabular data file.

        Parameters
        ----------
        filename : str
            The name of the output file.
        suffix : str
            Any suffix to add to the filename. This will ** NOT ** affect the data format in any way. 
            For instance, a ``filename = "myfile.tsv"`` and a ``suffix = ".gz"`` will result in a file named 
            ``myfile.tsv.gz``, but it will still be a regular `tsv` file, and not a compressed one! 
            It is important to either include a tabular format such as `.tsv` in the `filename` or specify 
            a `sep` argument through the `kwargs` in order to be able to save the file properly.
        """

        # get the separator to use. If it is not evident from the filename
        # or the kwargs, use the same separator that was used for file reading...
        sep = kwargs.pop( "sep", None )
        if not sep: 
            _suffix,_ = convert.filesuffix( filename )
            if _suffix in tabular.separators:
                sep = tabular.separators[ _suffix ]
            else:
                sep = self._read_sep
        
        suffix = suffix if suffix else ""
        filename = f"{ filename }{ suffix }"

        # If the index was set to a column, we don't want to write the numeric index to the file...
        write_index = kwargs.pop( "index", not self._index_was_set_to_column ) 

        self._df.to_csv( filename, sep = sep, index = write_index, **kwargs )
    
    def _reformat_index( self ):
        """
        Reformats the index of the dataframe.
        """
        self._df.index = self._df.index.astype( str )

        for old, new in self._formats.items():
            self._df.index = self._df.index.str.replace( old, new, regex = True )


    def _reformat_names( self ):
        """
        Reformats the names of the dataframe.
        """
        for old, new in self._formats.items():
            self._df.columns = self._df.columns.str.replace( old, new, regex = True )
    
    def _reformat_columns( self, columns : list ):
        """
        Reformats specific columns of the dataframe.
        """
        for column in columns:
            self._df[ column ] = self._df[ column ].astype( str )
            for old, new in self._formats.items():
                self._df[ column ] = self._df[ column ].str.replace( old, new, regex = True )

    def __repr__( self ):
        return f"Formatter( {self._formats} )"
    

