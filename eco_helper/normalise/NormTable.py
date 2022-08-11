"""
A class to read raw counts data from an expression matrix file and normalise the data.
"""

import pandas as pd
import numpy as np
import eco_helper.normalise.funcs as funcs


class NormTable(object):
    """
    A class to read raw counts from an expression matrix file and normalise the data to either ``tpm`` or ``cpm``.

    Parameters
    ----------
    filename : str
        The input count table. By default this is assumed to be tab-delimited. 
        Pass a ``sep`` argument to specify a different separator.
    """
    def __init__( self, filename : str, **kwargs ):
        self._src = filename
        kwargs[ "index_col" ] = kwargs.get( "index_col", 0 )
        self._counts = self.read( filename, **kwargs )
        self._normalized = None
        self.cpm = None
        self.tpm = None
        self._lengths = None
        self._raw_counts = None
        self._full_counts = None
        self._memorize = False

    def memorize( self ):
        """
        Store the original (pre-filtered) and raw (unnormalised) counts.
        """
        self._memorize = True

    def to_tpm( self, digits : int = 5, log : bool = False ):
        """
        Normalise the raw counts to TPM.

        Parameters
        ----------
        digits : int, optional
            The number of digits to round to. The default is 5.
        log : bool, optional
            If True, the TPM values are logarithmically scaled. The default is False.
        """
        if not self._has_lengths:
            raise ValueError( "The table does not have lengths." )

        # store the raw counts
        if self._memorize:
            self._raw_counts = self._counts.copy()
        
        # convert to TPM
        self._normalized = funcs.array_to_tpm( self.counts, self.lengths, log )
        
        # now round to the given number of digits
        # logger.info( "Rounding values..." )
        self._normalized = self.round( digits )
        
        # and now replace the raw counts in all 
        # columns that contain counts (i.e. all but the first)
        # logger.debug( "Current values ")
        # logger.debug( str( self._counts.head() ) )
        # logger.info( "Replacing raw counts with TPM values..." )
        new_df = pd.DataFrame( 
                                    self._normalized, 
                                    columns = self._counts.columns, 
                                    index = self._counts.index 
                            )

        # logger.debug( "New values")
        # logger.debug( str( new_df.head() )  ) 
        self._normalized = new_df
        self.tpm = new_df
        return self

    def to_cpm( self, digits : int = 5, log : bool = False ):
        """
        Normalise the raw counts to CPM.

        Parameters
        ----------
        digits : int, optional
            The number of digits to round to. The default is 5.
        log : bool, optional
            If True, the CPM values are logarithmically scaled. The default is False.
        """
  
        # store the raw counts
        if self._memorize:
            self._raw_counts = self._counts.copy()
        
        # convert to CPM
        self._normalized = funcs.array_to_cpm( self.counts, log )
        
        # now round to the given number of digits
        # logger.info( "Rounding values..." )
        self._normalized = self.round( digits )
        
        # and now replace the raw counts in all 
        # columns that contain counts (i.e. all but the first)
        # logger.debug( "Current values ")
        # logger.debug( str( self._counts.head() ) )
        # logger.info( "Replacing raw counts with CPM values..." )
        new_df = pd.DataFrame( 
                                    self._normalized, 
                                    columns = self._counts.columns, 
                                    index = self._counts.index 
                            )

        # logger.debug( "New values")
        # logger.debug( str( new_df.head() )  ) 
        self._normalized = new_df
        self.cpm = new_df
        return self
    
    def round(self, digits):
        """
        Round tpm values to a given number of digits.

        Parameters
        ----------
        digits : int
            The number of digits to round to.
        """
        return funcs.round_values( self._normalized, digits )

    def set_lengths( self, filename : str, which : str = None, id_col : str = None, name_col : str = None, **kwargs ):
        """
        Sets the lengths of the features.

        Parameters
        ----------
        filename : str
            The file containing the lengths of the features.
        which : str, optional
            The column name of the lengths. The default is None (in which case the last column is used).
        id_col : str, optional
            The column name of the IDs. The default is None (in which case the first column is used).
        name_col : str, optional
            The column name of the (gene) names. The default is None (in which case the second column is used).
            Note, even if your datafile does not specify gene names a "name column" will still be extracted. 
            However, you can adjust not to include the column later for saving the TPM-converted file.
        """
        
        # store the original data
        if self._memorize:
            self._full_counts = self._counts.copy()

        # get only the relevant subset of lengths for the actually present features
        if id_col is None:
            id_col = 0
        kwargs[ "index_col" ] = kwargs.get( "index_col", id_col )

        lengths = self.read( filename, **kwargs )

        # check if we have a specified name for the index column
        # this will first check for an index name in the counts data
        # and then for a name in the lengths data. It will overwrite the 
        # current index name in both dataframes with the specified name.
        index_name = self._counts.index.name
        if not index_name:
            index_name = lengths.index.name
            if not index_name:
                # logger.warning( "No index name could be identified! Will use `gene_id` as index name." )
                index_name = "gene_id"

        # get all the currently held ids in the countTable
        # and mask the data to only those gene to which reference 
        # lengths are available, and therefore TPMs can be calculated.
        # logger.debug( "Before masking:", len( lengths ) )

        mask_lengths = lengths.index.isin( self._counts.index )
        mask_counts = self._counts.index.isin( lengths.index )

        lengths = lengths.iloc[ mask_lengths,: ]
        self._counts = self._counts.iloc[ mask_counts,: ]

        # logger.debug( "After masking:", len( lengths ) )

        # and now sort to ensure the same order is preserved
        lengths = lengths.reindex( index = self._counts.index )

        lengths.index.name = index_name
        self._counts.index.name = index_name


        # get which names to extract from the lengths dataframe
        if name_col is None:
            name_col = 0 if id_col == 0 else 1            
            name_col = lengths.columns[name_col]

        # now only get a single length column from the lengths dataframe
        if which is None:
            which = lengths.columns[-1]
        elif which not in lengths.columns:
            raise ValueError( f"The column name '{which}' is not in the file {filename}" )
        
        # and finally restrict our length data to only the name and lengths column
        # as well as the index which holds the ids...
        self._lengths = lengths.loc[ :,[name_col, which] ]
        return self
    
    def get_lengths( self ): 
        """
        Returns the lengths of the features.

        Returns
        -------
        lengths : pandas.Series or None
            The lengths of the features.
        """
        return self._lengths

    def get(self):
        """
        Returns the table of normalized values.

        Returns
        -------
        pandas.DataFrame
            The table.
        """
        return self._normalized

    def read( self, filename : str, sep : str = "\t", **kwargs ) -> pd.DataFrame: 
        """
        Reads a table from a file.

        Parameters
        ----------
        filename : str
            The input file.
        sep : str, optional
            The separator of the table. The default is "\t".

        Returns
        -------
        df : pandas.DataFrame
            The table.
        """
        # logger.info( f"Reading input file... (this may take a while)" )
        df = pd.read_csv( 
                            filename, 
                            sep = sep, 
                            comment = "#", 
                            **kwargs
                        ) 
        return df

    def save( self, filename : str, use_names : bool = False ): 
        """
        Saves the table to a file.

        Parameters
        ----------
        filename : str
            The output file.
        use_names : bool
            Save the file with gene_names instead of gene_ids in the first column.
        
        """
        # logger.info( "Saving to file... (this may take a while)" )
        if use_names:
            self.adopt_name_index()
        self._normalized.to_csv( filename, sep = "\t", index = True )
        # logger.info( f"Saved to file: {filename}" )

    def adopt_name_index( self ):
        """
        Adopts the extracted name column of the lengths dataframe as the new 
        dataframe index for both the lengths and counts data.

        Note
        ----
        This will only affect the raw and final counts (normalized),
        but it will not affect the original counts!
        """
        index = self._lengths.iloc[:,0]
        self._lengths.index = index
        if self._normalized is not None: 
            self._normalized.index = index
        if self._raw_counts is not None:
            self._raw_counts.index = index

    @property
    def raw_data( self ):
        """
        Returns the originally provided counts data.

        Note    
        -----
        This contains all the provided genes and their counts,
        including those for which no lengths are available.

        Returns
        -------
        raw_data : pandas.DataFrame
            The originally provided counts data.
        """
        return self._full_counts

    @property
    def raw_counts( self ):
        """
        Returns the raw counts.

        Note
        ----
        These are cropped to only genes that were found to have a 
        corresponding length in the lengths file and for which therefore
        TPM conversion could be performed. If you wish to access the original
        (pre filtered) data, use the raw_data attribute instead.

        Returns
        -------
        counts : np.ndarray
            The raw counts.
        """
        if self._raw_counts is None:
            return self.counts
        return self._raw_counts.to_numpy()
    
    @property
    def counts( self ):
        """
        Returns the raw or TPM counts (if normalisation was performed).

        Note
        ----
        These are cropped to only genes that were found to have a 
        corresponding length in the lengths file and for which therefore
        TPM conversion could be performed. If you wish to access the original
        (pre filtered) data, use the raw_data attribute instead.

        Returns
        -------
        counts : np.ndarray
            The raw or TPM counts.
        """
        return self._counts.to_numpy()


    @property
    def ids(self) -> np.ndarray:
        """
        Returns the IDs of the features.

        Returns
        -------
        ids : np.ndarray
            The IDs of the features.
        """
        return self._counts.index.to_numpy()

    @property
    def names(self) -> np.ndarray:
        """
        Returns the names of the features.

        Returns
        -------
        names : np.ndarray
            The names of the features.
        """
        return self._lengths.iloc[ :,0 ].to_numpy()

    @property
    def lengths( self ) -> np.ndarray:
        """
        Returns the lengths of the features.

        Returns
        -------
        lengths : numpy.ndarray or None
            The lengths of the features.
        """
        return self._lengths.iloc[ :,-1 ].to_numpy()

    @property
    def _has_lengths(self): 
        """
        Checks if the table has lengths.

        Returns
        -------
        has_lengths : bool
            True if the table has lengths.
        """
        return self._lengths is not None

    @staticmethod
    def _count_columns( df ):
        """
        Returns the names of the columns that contain counts.

        Returns
        -------
        count_columns : list
            The names of the columns that contain counts.
        """
        return df.columns[1:]

    def __repr__(self) -> str:
        return f"NormTable(file='{self._src}')"
    
    def __str__(self) -> str:
        return self._counts
    
    def __len__(self) -> int:
        return len(self._counts)