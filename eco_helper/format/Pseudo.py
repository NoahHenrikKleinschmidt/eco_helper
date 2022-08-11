"""
Classes to pseudo-read large data files only by their first column (index) and their first line (column headers).
These classes are intended to work with the core `Formatter` class and imitate the file reading and workflow of a real pandas dataframe, without actually reading or storing data.
"""

import pandas as pd
import eco_helper.core.terminal_funcs as tfuncs

class Pseudo( pd.Series ):
    """
    A class to imitate the dataframe columns and indices.
    It is just pd.Series but giving them extra names will make the 
    code easier to understand...
    """
    def __init__( self, data : list, name : str ):
        super().__init__( data, name = name )

    def __repr__( self ):
        return f"{self.__class__.__name__}( name={self.name} )"

    def __str__( self ):
        return super().__str__()
        
class PseudoIndex( Pseudo ):
    def __init__( self, values, name ):
        super().__init__( data = values, name = name )

class PseudoColumns( Pseudo ):
    def __init__( self, values, name ):
        super().__init__( data = values, name = name )

# because the expression matrices can be really large and therefore take a long time to load
# this class will allow an easier shortcut by just extracting the column names and indices from
# the datafiles and offering the few methods that the Formatter class below will require to perform
# the actual reformatting. Hence, the Formatter can use this class just like it would a real pandas 
# DataFrame with all the actual data.

class PseudoDataFrame:
    """
    A class to imitate the relevant methods and attributes for re-formatting of a pandas DataFrame
    withou actually storing any of it's data.

    Parameters
    ----------
    source : str
        The data source file to read.
    sep : str
        The separator. By default tab.
    """
    def __init__( self, source : str, sep = "\t", **kwargs ):
        self.src = source
        self._sep = sep
        self.columns = None
        self.rows = None
        if self.src:
            self.read( self.src, sep = sep, **kwargs )
    
    def read( self, filename : str, index_col = 0, index_has_header = False, sep = "\t", **kwargs ) -> None:
        """
        Read a data source file and get the column (first line)
        names and the index column.

        Note
        ----
        The column names *must* be in the first line, no 
        comments may be present in the file!

        Parameters
        ----------
        filename : str
            The path to the data source file.
        index_col : int
            The index column. By default the first column.
        index_has_header : bool
            Set to True if the index column has a header.
        sep : str
            The separator. By default tab.
        """

        # get the first line which are the column names
        columns = tfuncs.stdout( f"head -n 1 {filename}" ).split( sep )

        # previous code from the stand-alone...
        # columns = subprocess.run( f"head -n 1 {filename}", shell=True, capture_output=True )
        # columns = columns.stdout.decode( "utf-8" ).strip().split( sep )
        
        # get the first column with the index values
        index = str( index_col+1 )
        index = tfuncs.stdout( f"cut -f { index } {filename}" ).split( "\n" )

        # previous code from the stand-alone...
        # index = subprocess.run( f"cut -f { index } {filename}", shell=True, capture_output=True )
        # index = index.stdout.decode( "utf-8" ).strip().split( "\n" )

        # get rid of a trailing whitespace
        if index[-1] == "":
            index = index[:-1]

        name = None
        if index_has_header:
            name = index[0]
            index = index[1:]

        self.columns = PseudoColumns( columns, None ) 
        self.index = PseudoIndex( index, name ) 
        self.replace_delims()


    def to_csv( self, filename : str = None, sep = "\t", **kwargs ):
        """
        Write the edited column names and indices to a csv file.

        Parameters
        ----------
        filename : str
            The path to the output file.
        sep : str
            The separator. By default tab.
        """
        if filename is None:
            filename = self.src

        tmpfile = f"{filename}.tmpfile"
        self._write_columns(tmpfile, sep)
        self._write_index(tmpfile)


    def _write_index(self, filename):
        """
        Write the index column to a file.
        """

        # first assemble the full column
        index_col = "\n".join( self.index )
        if self.index.name is not None:
            index_col = f"{self.index.name}\n{index_col}"
        
        # save the index col to another tmpfile
        index_file = f"{filename}.index_column"
        # subprocess.run( f"printf '{index_col}' > { index_file }", shell=True )
        with open( index_file, "w" ) as f:
            f.write( index_col )

        # and now paste the file and new index together and remove the tmpfiles...
        cmd = f"""( paste <( cut -f 1 '{index_file}' ) <( cut -f 2- '{filename}' ) ) ; rm {index_file} ; rm {filename}"""


        outfile = filename.replace( ".tmpfile", "" )
        tfuncs.stdout( cmd, file = outfile )

        # with open( outfile, "w" ) as f:
            # subprocess.run( cmd, shell = True, executable = self._get_bash(), stdout = f )

        
    def _write_columns(self, filename, sep):
        """
        Write the column names to the first line.
        """
        # now assemble the first line
        first_line = sep.join( self.columns )

        # ----------------------------------------------------------------
        # this one works in theory but apparently the lines are too long and bash is not happy...
        # ----------------------------------------------------------------
        # # if no filename is given, just do the editing in-place...
        # if filename is None:
        #     options = ( "-i ", "" )
        # else:
        #     options = ( "", " > '{filename}'" )
        # # and insert the first line
        # subprocess.run( f"""sed { options[0] }"1s/.*/{first_line}/" '{self.src}'{ options[1].format(filename = filename) }""", shell = True, executable = self._get_bash() )

        
        with open( filename, "w" ) as f:
            f.write( first_line )
            f.write( "\n" )
        
        with open( filename, "a" ) as f:
        #     subprocess.run( f"""( tail -n +2 "{self.src}" ) """, shell = True, executable = self._get_bash(), stdout = f )

            # since the file option of tfuncs.stdout would overwrite the contents, we do this instead...
            f.write( tfuncs.stdout( f"""( tail -n +2 "{self.src}" ) """ ) ) 

    # this was part of the original stand-alone but should not be necessary anymore...
    # def _get_bash(self):
    #     """
    #     Get the path to the used bash executable.
    #     """
    #     bash = subprocess.run( "which bash", shell = True, capture_output = True ).stdout.decode( "utf-8" ).strip()
    #     return bash

    def replace_delims(self):
        """
        Removes any whitespace characters used for delimintation
        from the index and columns.
        """
        to_remove = ( "\n", "\t" )
        for i in to_remove:
            self.index = self.index.str.replace( i, "" )
            self.columns = self.columns.str.replace( i, "" )

    def __repr__(self):
        return f"PseudoDataFrame({self.columns}, {self.index})"
