"""
The main class that handles re-formatting input datafile index, columns, and headers.
"""

import os
import pandas as pd
import logging
import glob
from alive_progress import alive_bar

import eco_helper.format.formats as formats
import eco_helper.format.Pseudo as pseudo



logger = logging.getLogger( "eco_helper" )

class Formatter:
    """
    A cass to read expression matrices and annotation files in `TSV` format, and re-format 
    the `ID`, `CellType`, and `Sample` columns (in annotation files), and `index` and `column names` 
    (expression matrices) to conform with EcoTyper format requirements.

    Parameters
    ----------
    formats : dict
        A dictionary of invalid characters which must be replaced with a valid character.     
        By default the pre-set `EcoTyper` dictionary is used.
    """
    def __init__( self, formats : dict = None ):
        
        self._formats = formats.EcoTyper if not formats else formats
        
        self._matrices = {}
        self._annotations = {}

        self._matrix_filetypes = [ "*.counts", "*.countsTable", "*.tpm", "*.TPM" ]
        self._annotation_filetypes = [ "*.annotations", "*.annotation" ]

        self._annotation_index_id_was_reset = False

    def reformat( self, **kwargs ):
        """
        Reformat the expression matrix and annotation table.
        """
        logger.info( "Reformatting expression matrix and annotation table" )
        self._matrices = { k : self.reformat_expression_matrix( i ) for k,i in self._matrices.items() }
        self._annotations = { k : self.reformat_annotation_table( i, **kwargs ) for k,i in self._annotations.items() }
    
    def reformat_expression_matrix( self, matrix : pd.DataFrame, **kwargs ) -> pd.DataFrame:
        """
        Reformat the expression matrix' `index` and `column names`.
        """
        for old, new in self._formats.items():
            matrix.index = matrix.index.str.replace( old, new )
            matrix.columns = matrix.columns.str.replace( old, new )
        return matrix

    def reformat_annotation_table( self, table : pd.DataFrame, columns : list, **kwargs ) -> pd.DataFrame:
        """
        Reformat the annotation table's `ID` column, the `CellType` column, and the `Sample` column.

        Note
        ----
        All of these columns must be present in the annotation table!

        Parameters
        ----------
        table : pd.DataFrame
            The annotation table to reformat.
        columns : list
            The list of columns to reformat.
        """
        for column in columns:
            table[ column ] = table[ column ].astype( str )
            for old, new in self._formats.items():
                table[ column ] = table[ column ].str.replace( old, new )

        # table[ "ID" ] = table[ "ID" ].astype( str )
        # table[ "CellType" ] = table[ "CellType" ].astype( str )
        # table[ "Sample" ] = table[ "Sample" ].astype( str )

        # for old, new in self._formats.items():
        #     table[ "ID" ] = table[ "ID" ].str.replace( old, new )
        #     table[ "CellType" ] = table[ "CellType" ].str.replace( old, new )
        #     table[ "Sample" ] = table[ "Sample" ].str.replace( old, new )
        return table

    def memory_saving_dir_pipe( self, path : str, output : str = None, suffix : str = None, **kwargs ) -> None:
        """
        This method performs the entire pipeline on all matching files within a directory
        but goes file-wise instead of step-by-step first reading all files, then formatting all files etc.
        This is computationally more expensive but uses less memory.

        Parameters
        ----------
        path : str
            The path to the directory containing the expression matrix and/or annotation table.
        
        output : str
            The path to the directory where the reformatted files will be written.

        suffix : str
            The suffix to append to the output file names.
        """
        matrices, annotations = self._read_from_dir( path )

        # now process each file:
        with alive_bar( len(annotations + matrices), title = "Processing files" ) as bar:
            
            kwargs1 = dict( kwargs )
            kwargs1.pop( "pseudo" )
            for i in annotations:
                logger.debug( "Reading annotation table", i )
                self.read_annotation_table( i, **kwargs1 )
                logger.debug( "Table has columns: ", self._annotations[ i ].columns )

                self.reformat()
                self.save_to_dir( path = output, suffix = suffix )
                self._annotations = {}
                bar()   

            kwargs.pop( "id_is_index" )
            for i in matrices:
                self.read_expression_matrix( i, **kwargs )
                self.reformat()
                self.save_to_dir( path = output, suffix = suffix )
                self._matrices = {}
                bar()

    def read_from_dir( self, path : str, **kwargs ):
        """
        Read an expression matrix and/or annotation table from the same directory.
        When using this method, it is assumed that expression matrix either ends with `.counts`, `.countsTable`, or `.tpm` and the annotation file ends with `.annotations`.


        Parameters
        ----------
        path : str
            The path to the directory containing the expression matrix and/or annotation table.
        """
        
        matrices, annotations = self._read_from_dir( path )

        # read the datafiles
        kwargs1 = dict(kwargs)
        kwargs1.pop( "pseudo" )
        self._annotations = { i : self._read_annotation_table( i, **kwargs1 ) for i in annotations }

        kwargs.pop( "id_is_index" )
        self._matrices = { i : self._read_expression_matrix( i, **kwargs ) for i in matrices }


    def _pseudoread_expression_matrix( self, filename : str, **kwargs ) -> pseudo.PseudoDataFrame:
        """
        Only reads the first line and first column of the expression matrix.

        Parameters
        ----------
        filename : str
            The name of the expression matrix file.

        Returns
        -------
        PseudoDataFrame
            A pseudo dataframe containing the first line and first column of the expression matrix without actually reading any of the data.
            This object can still be "normally worked with" in terms of reformatting and saving.
        """
        return pseudo.PseudoDataFrame( filename, **kwargs )

    def read_expression_matrix( self, file : str, pseudo : bool = False, **kwargs ):
        """
        Read an expression matrix.

        Parameters
        ----------
        file : str
            The path to the expression matrix.
        pseudo : bool
            If True, only the column names and index will be read into PseudoDataFrame.
            This will prevent excessive memory usage for large files.
        """
        logger.info( f"(this may take a while) Reading expression matrix {file}" )
        if pseudo:
            data = self._pseudoread_expression_matrix( file, **kwargs )
        else:
            data = self._read_expression_matrix( file, **kwargs )
        self._matrices[ file ] = data
        return data

    def read_annotation_table( self, file : str, id_is_index : bool = False, **kwargs ):
        """
        Read an annotation table.

        Parameters
        ----------
        file : str
            The path to the annotation table.
        id_is_index : bool
            Set to `True` if the `ID` column is the index of the table.
        """
        logger.info( f"(this may take a while) Reading annotation table {file}" )
        
        data = self._read_annotation_table( file, id_is_index = id_is_index, **kwargs )
        self._annotations[ file ] = data
        return data

    def save_to_dir( self, path : str = None, suffix : str = None ):
        """
        Save the expression matrix and/or annotation table(s) to the same directory.
        When using this method, the same filenames as the input files will be re-used. 
        If saving to the same directory as the input files, this will overwrite the existing files!

        Parameters
        ----------
        path : str
            The path to the directory to save the expression matrix and/or annotation table.
            By default the same filenames as the input filenames will be used and the old files are overwritten.
        suffix : str
            Any suffix to add to the output filenames.
        """
        logger.info( f"(this may take a while) Saving to directory {path}" )

        make_path = self._create_make_path(path, suffix)

        for file,i in self._matrices.items():
            self.save_expression_matrix( make_path( file ), i )

        for file,i in self._annotations.items():    
            self.save_annotation_table(  make_path( file ), i )

    @staticmethod
    def _create_make_path(path : str, suffix : str = None ):
        """
        Create a lambda funtion that will create a proper 
        absolute filepath to store an output file to.

        Parameters
        ----------
        path : str
            The path to the directory to save the expression matrix and/or annotation table.
        suffix : str
            Any suffix to add to the output filenames.
        
        Returns
        -------
        make_path : lambda
            A lambda function that will create a proper absolute filepath to store an output file to.
        """
        if not suffix: suffix = ""
        if path: 
            if not os.path.exists( path ): 
                os.makedirs( path )
            if not os.path.isabs( path ):
                path = os.path.abspath( path )
            make_path = lambda x: f"{ path }/{ x }{ suffix }"
        else:
            make_path = lambda x: f"{ x }{ suffix }"
        return make_path


    @staticmethod
    def save_expression_matrix( file : str, matrix : pd.DataFrame ):
        """
        Save an expression matrix.

        Parameters
        ----------
        file : str
            The path to the expression matrix.
        matrix : pd.DataFrame
            The expression matrix to save.
        """
        logger.info( f"(this may take a while) Saving expression matrix {file}" )
        matrix.to_csv( file, sep = "\t", index = True )

    def save_annotation_table( self, file : str, table : pd.DataFrame ):
        """
        Save an annotation table.

        Parameters
        ----------
        file : str
            The path to the annotation table.
        table : pd.DataFrame
            The annotation table to save.
        """
        logger.info( f"(this may take a while) Saving annotation table {file}" )
        table.to_csv( file, sep = "\t", index = not self._annotation_index_id_was_reset )

    
    @staticmethod
    def _read_expression_matrix( file : str, **kwargs ):
        """
        Core of read_expression_matrix
        """
        data = pd.read_csv( file, sep = "\t", index_col = 0, **kwargs )
        return data


    def _read_annotation_table(self, file : str, id_is_index = False, id_colname = None, **kwargs ):
        """
        Core of read_annotation_table
        """
        self._annotation_index_id_was_reset = False
        data = pd.read_csv( file, sep = "\t", **kwargs )
        if id_is_index and id_colname is not None:
            self._annotation_index_id_was_reset = True
            data.insert( 0, id_colname, data.index )
            data = data.reset_index( drop = True )
        return data

    def _read_from_dir(self, path):
        """
        The core of read_from_dir
        """

        logger.info( f"Reading from directory {path}" )
        
        if not os.path.isabs( path ):
            path = os.path.abspath( path )

        # find matching datafiles
        pwd = os.getcwd()
        os.chdir( path )
        matrices = [ glob.glob( i ) for i in self._matrix_filetypes ]        
        annotations = [ glob.glob( i ) for i in self._annotation_filetypes ]
        os.chdir( pwd )

        # flatten the findings
        matrices = [ item for sublist in matrices for item in sublist ]
        annotations = [ item for sublist in annotations for item in sublist ]

        return matrices,annotations

    def _is_expression_matrix_file( self, path ):
        """
        Check if the file is an expression matrix file.
        """
        return any( path.endswith( i ) for i in self._matrix_filetypes )
    
    def _is_annotation_table_file( self, path ):
        """
        Check if the file is an annotation table file.
        """
        return any( path.endswith( i ) for i in self._annotation_filetypes )

    # these methods are used to get the read matrix 
    # in the main script in case only a single file is being read...
    def _last_matrix( self ):
        return list( self._matrices.values() )[-1]

    def _last_annotation( self ):
        return list( self._annotations.values() )[-1]
    
    @property
    def formats( self ):
        return self._formats

    @property
    def matrix_filetypes( self ):
        return self._matrix_filetypes
    
    @property
    def annotation_filetypes( self ):
        return self._annotation_filetypes
    
    @property
    def matrices( self ):
        return self._matrices
    
    @property
    def annotations( self ):
        return self._annotations
        
    
    def __repr__( self ):
        return f"Formatter( {self._formats} )"
    

