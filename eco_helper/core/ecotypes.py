"""
This class handles EcoType assignments between different EcoTyper runs.
"""

import logging
import os
import pandas as pd
from itertools import zip_longest

import eco_helper.core.settings as settings
import eco_helper.core.cell_states as cell_states

class Ecotype:
    """
    The base class of an Ecotype holding cell types and associated states associated with the Ecotype.

    Parameters
    ----------
    cell_types : list
        List of cell types associated with the Ecotype.
    states : list
        List of cell states associated with the Ecotype.
    genes : list
        List of pandas dataframes containing the genes associated with each celltype and state.
    label : str
        An arbitrary identifier for the Ecotype.
    """
    def __init__( self, cell_types : list = None, states : list = None, genes : list = None, label : str = None ):
        self.label = label

        cell_types = list(cell_types) if cell_types is not None else []
        states = list(states) if states is not None else []
        genes = list(genes) if genes is not None else []

        self._dict = {
                        ( cell_type, state ) : genes  for 
                        cell_type, state, genes in zip_longest( cell_types, states, genes )
                    }

    def add( self, cell_type : str, state : str, genes : pd.DataFrame = None ):
        """
        Add a cell type and state to the Ecotype.

        Parameters
        ----------
        cell_type : str
            The cell type to add.
        state : str
            The cell type's cell state.
        genes : pd.DataFrame
            The genes associated with the cell state.
        """
        self._dict[ (cell_type, state) ] = genes

    def remove( self, cell_type : str, state : str = None ):
        """
        Remove a cell type and state from the Ecotype.
        If no state is given then all states associated with the cell-type are removed.
        """
        if state is None:
            for key in self._dict.keys():
                if key[0] == cell_type:
                    del self._dict[key]
        else:
            del self._dict[ (cell_type, state) ]

    def to_dict( self ):
        """
        Convert the Ecotype to a dictionary with cell types and states keys and their associated genes as values.
        """
        return dict( self._dict )

    def to_df( self ):
        """
        Convert the Ecotype to a pandas DataFrame with two columns, 
        one for cell types and one for their states (as string identifiers/labels).
        """
        return pd.DataFrame( { settings.cell_type_col : self.cell_types, settings.state_col : self.states } )

    def gene_set_filenames( self ):
        """
        Assemble a list of gene set filenames (as created by the `eco_helper.enrich.collect_gene_sets` function) for all celltypes and states contributing to the Ecotype.

        Returns
        -------
        list
            List of gene set filenames.
        """
        return [ f"{cell_type}_{state}.txt" for cell_type, state in zip( self.cell_types, self.states ) ]

    @property
    def cell_types( self ):
        return [ i[0] for i in self._dict.keys() ]
    
    @property
    def states( self ):
        return [ i[1] for i in self._dict.keys() ]
    
    @property
    def genes( self ):
        return list( self._dict.values() )

    def __setitem__( self, key, value ):
        self.add( key, value )
    
    def __getitem__( self, key ):
        if isinstance( key, int ):
            return self._dict[ list(self._dict.keys())[key] ]
        return self._dict[key]
    
    def __delitem__( self, key ):
        if isinstance( key, int ):
            self.remove( list(self._dict.keys())[key] )
        elif isinstance( key, tuple ):
            self.remove( *key )
        else:
            self.remove( key )
            
    def __iter__( self ):
        return iter( self._dict.items() )
    
    def __repr__( self ):
        return f"{self.__class__.__name__}(label={self.label})"



class EcotypeCollection( cell_states.CellStateCollection ):
    """
    This class handles Ecotype assignments between separate EcoTyper runs.

    Note
    ----
    This module is not yet implemented!

    Parameters
    ----------
    directories : list
        List of EcoTyper results (output) directories to get ecotypes from.
    """
    def __init__( self, directories : list ):
        super().__init__( directories )

        self.ecotype_assignments = {}

        for directory in self.directories:
            self._find_ecotype_assignments( directory )

    def match_genes_to_states( self ):
        """
        Get the gene sets associated with each cell type's cell state. 
        This will replace the simple string description of the cell state with the respective 
        dataframe within the ecotype_assignments dictionary.
        """
        if len( self.genes ) == 0:
            self.get_genes()
        for dir, ecotypes in self.ecotype_assignments.items():
            for ecotype in ecotypes.values():
                for entry,_ in ecotype:
                    
                    cell_type, state = entry

                    genes = self.genes[cell_type]
                    genes = genes[ genes.values == state ] 
                    
                    ecotype.add( cell_type, state, genes )

                   
    def _find_ecotype_assignments( self, directory : str ):
        """
        Find the ecotype assignments, specified through celltypes and their states contributing to an EcoType,
        from a single EcoTyper results directory.
        
        Parameters
        ----------
        directory : str
            The EcoTyper results directory to get ecotypes from.
        """
        ecotypes_dir = os.path.join( directory, settings.ecotypes_folder )
        
        if not os.path.exists( ecotypes_dir ):
            logging.warning( f"No Ecotypes found in {directory}!" )
            return
        
        ecotypes = os.path.join( ecotypes_dir, settings.ecotypes_composition_file )
        if not os.path.exists( ecotypes ):
            logging.error( f"No Ecotypes assignment file found in {directory}!" )
            return

        # read the ecotype assignments
        ecotypes = pd.read_csv( ecotypes, sep="\t" )

        # and assemble Ecotypes
        ecotype_assignments = {}
        for label, ecotype in ecotypes.groupby( settings.ecotype_col ):
            
            cell_types = ecotype[ settings.cell_type_col ]
            states = ecotype[ settings.state_col ]
            
            ecotype_assignments[label] = Ecotype( cell_types = cell_types, states = states, label = label )

        self.ecotype_assignments[directory] = ecotype_assignments
            
    def __getitem__( self, key ):

        # we make stuff a bit easier to handle with the item getting
        # by allowing direct access to the ecotypes in case only a single
        # run is stored anyway.
        if len( self.ecotype_assignments ) == 1:
            ref_dict = self.ecotype_assignments[ list(self.ecotype_assignments.keys())[0] ]
        else:
            ref_dict = self.ecotype_assignments 

        if isinstance( key, tuple ):
            return ref_dict[ key[0] ][ key[1] ]
        elif isinstance( key, int ):
            return ref_dict[ list(ref_dict.keys())[key] ]
        return ref_dict[ key ]
    
    def __iter__( self ):
        if len( self ) == 1:
            return iter( self.ecotype_assignments[ list(self.ecotype_assignments.keys())[0] ].values() )
        return iter( self.ecotype_assignments.items() )

    def __repr__( self ):
        return f"{self.__class__.__name__}(directories={self.directories})"
    
    def __len__( self ):
        return len( self.ecotype_assignments )