"""
This class handles loading gene set enrichment results files from a source directory.
This is designed for manual use when evaluating the results of enrichment 
analyses done through `eco_helper` and is not part of the CLI.

The `EnrichmentCollection` class is a container for the results of enrichment analyses, which stores a dictionary
of pandas dataframes either on celltype level or ecotype level and can be easily iterated over to facilitate data handling.

Example

    .. code-block:: python

        from eco_helper.enrich import EnrichmentCollection

        # Load the results of enrichment analyses
        enrich_collection = EnrichmentCollection(directory = '/path/to/enrichment/results' )

    On the very basis the above code is all that is required to load the enrichment results. However, in case 
    multiple layers of results (such as both prerank and enrichr results) are present, further fine-tuning can (must be) done.

    .. code-block:: python

        # Load the results of enrichment analyses
        enrich_collection = EnrichmentCollection(   directory = '/path/to/enrichment/results',
                                                    # load ecotype level results
                                                    resolution = 'ecotype',
                                                    # load prerank results
                                                    which = 'prerank'
                                                )

    With the above segment we specified that we are interested in loading the enrichment results for each ecotype and only the prerank results.
    One `EnrichmentCollection` objects supports only one resolution and one kind of results (prerank or enrichr).

    In case of the above example, the keys in the `EnrichmentCollection` object are the ecotypes (i.e. E1, E2, etc.), while the 
    values are the respective dataframes that include all their associated cell-types and states.

    In case we specify ``resolution = 'celltye'`` then the keys will be the individual cell-type/state combinations (filenames within the source directory)
    and their individual dataframes will be the values. It is important to note that if ``eco_helper enrich`` was run with the ``--assemble`` option then 
    the each celltype will have only one merged file and the keys will indeed correspond purely to cell types. On the other hand, if the ``--assemble`` option was not used then
    each celltype and state will have their own file and the keys will correspond to each celltype and state combination that was identified by EcoTyper.

"""

import os, glob, pickle
import pandas as pd
import eco_helper.core as core

class EnrichmentCollection:
    """
    This class will load the enrichment datafiles from a source directory.

    Parameters
    ----------
    directory : str
        The directory containing the datafiles.
    resolution : str
        This can be either `"ecotype"` to load from ecotype dedicated subdirectories, or `"celltype"` to load files directly from the source directory.
        This is only required in case the source directory contains both files and ecotype subdirectories.
    which : str
        This can be either `"prerank"` or `"enrichr"`. This is only required in case 
        the source directory (or ecotype directories) contains both enrichr and prerank results.
    """

    _accepted_resolutions = [ "celltype", "ecotype" ]
    _accepted_which = [ "prerank", "enrichr" ]

    def __init__(self, directory : str, resolution : str = None , which : str = None ):
        self.directory = directory
        self.resolution = resolution
        self.which = which

        self._check_resolution()
        self._check_which()

        self.data = {}
        self.load()
    
    def keys( self ):
        """
        Returns the keys of the enrichment datafiles.
        """
        return self.data.keys()
    
    def values( self ):
        """
        Returns the enrichment dataframes.
        """
        return self.data.values()        

    def items( self ):
        """
        Returns the enrichment dataframes as a dictionary.
        """
        return self.data.items()

    def load( self ):
        """
        Loads the enrichment datafiles from the source directory.
        """
        loading_func = {
                            "celltype": self._load_celltype,
                            "ecotype": self._load_ecotype
                        }
        loading_func[ self.resolution ]()

    def save( self, filename : str ):
        """
        Save the enrichment as a pickle file.

        Parameters
        ----------
        filename : str
            The name of the pickle file.
        """
        with open( filename, "wb" ) as f:
            pickle.dump( self, f )

    def split_terms( self ):
        """
        Split the `Term` column into `Term` and `Gene_set` columns.

        Note
        ----
        This only applies to `prerank` results. In `enrichr` results, the `Term` column is already split.
        """
        if self.which == "prerank":
            for key, df in self.data.items():
                df[ "Gene_set" ] = df[ "Term" ].str.split( "__" ).str[0]
                df[ "Term" ] = df[ "Term" ].str.split( "__" ).str[1]
                self.data[ key ] = df
        else: 
            print( "In enrichr results, the `Term` column is already split..." )

    def _load_celltype( self ):
        """
        Loads the enrichment datafiles from the source directory on celltype resolution.
        """
        suffix = self._get_suffix()

        files = glob.glob( os.path.join( self.directory, f"*{suffix}" ) )
        cell_types = [ os.path.basename( i ).replace( suffix, "" ).split(".txt")[0] for i in files ]

        for cell_type, file in zip( cell_types, files ):

            df = pd.read_csv( file, sep = "\t", comment = "#" )
            df.insert( 0, core.settings.cell_type_col, cell_type )

            self.data[ cell_type ] = df

    def _load_ecotype( self ):
        """
        Loads the enrichment datafiles from the source directory on ecotype resolution.
        """
        subdirs = [ os.path.join( self.directory, i ) for i in os.listdir( self.directory ) ]
        subdirs = [ i for i in subdirs if os.path.isdir( i ) and os.path.basename( i ).startswith( "E" ) ]

        ecotypes = [ os.path.basename( i ) for i in subdirs ]

        suffix = self._get_suffix()

        for ecotype, subdir in zip( ecotypes, subdirs ):
            
            dfs = []
            files = glob.glob( os.path.join( subdir, f"*{suffix}" ) )
            for file in files:

                cell_type = os.path.basename( file ).replace( suffix, "" ).split(".txt")[0]

                df = pd.read_csv( file, sep = "\t", comment = "#" )
                df.insert( 0, core.settings.cell_type_col, cell_type )
                dfs += [df]
            
            self.data[ ecotype ] = pd.concat( dfs )

    def _get_suffix(self):
        """
        Returns the suffix for the enrichment datafiles.
        """
        suffix = {
                    "enrichr": core.settings.enrichr_results_suffix,
                    "prerank": core.settings.prerank_results_suffix
                }
        suffix = suffix[ self.which ]
        return suffix

    def _check_which( self ):
        """
        Checks if the provided results type matches the directory architecture.
        """
        if self.which is not None:

            if self.which in self._accepted_which:
                return True
            else:
                raise ValueError( f"Results type must be one of {self._accepted_which}" )
        else:
            
            contents = [ os.path.join( self.directory, i ) for i in os.listdir( self.directory ) ]
            if self.resolution == "ecotype":
                contents = [ i for i in contents if os.path.isdir( i ) and os.path.basename( i ).startswith( "E" ) ]
                contents = os.listdir( contents[0] )

            has_enrichr = any( [ core.settings.enrichr_results_suffix in i for i in contents ] )
            has_prerank = any( [ core.settings.prerank_results_suffix in i for i in contents ] )

            if has_enrichr and has_prerank:
                raise ValueError( "The directory contains both enrichr and prerank results. Please specify which results to load." )
            
            elif has_enrichr:
                self.which = "enrichr"
                return True
            
            elif has_prerank:
                self.which = "prerank"
                return True

    def _check_resolution( self ): 
        """
        Checks if the given resolution matches the directory architecture, 
        and if not automatically adjusts it or raises an error.
        """
        if self.resolution is not None:

            if self.resolution in self._accepted_resolutions: 
                return True
            else: 
                raise ValueError( f"Resolution must be one of {self._accepted_resolutions}" )

        else:

            contents = os.listdir( self.directory )

            contents = [ os.path.join( self.directory, i ) for i in contents ]

            files = [ os.path.isfile( i ) for i in contents ]
            subdirs = [ os.path.isdir( i ) and os.path.basename( i ).startswith( "E" ) for i in contents ]

            have_files = any( files )
            have_subdirs = any( subdirs )

            if have_files and have_subdirs: 
                raise ValueError( "The directory contains both files and subdirectories. Please specify the resolution." )

            elif have_files: 
                self.resolution = "celltype"
                return True

            elif have_subdirs: 
                self.resolution = "ecotype"
                return True

    def __repr__( self ):
        return f"{self.__class__.__name__}( dir={self.directory}, res={self.resolution}, which={self.which} )"

    def __getitem__( self, key ):
        return self.data[ key ]
    
    def __setitem__( self, key, value ):
        self.data[ key ] = value
    
    def __delitem__( self, key ):
        del self.data[ key ]
    
    def __len__( self ):
        return len( self.data )
    
    def __iter__( self ):
        return iter( self.data.items() )
    
    def __contains__( self, key ):
        return key in self.data