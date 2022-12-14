"""
This class handles cell type sub-datasets from EcoTyper.
"""

import os
import eco_helper.core.settings as settings

class CellTypeCollection:
    """
    This class assembles the cell types from multiple EcoTyper results directories. 
    It will store for each cell type the corresponding data directory from the given EcoTyper results directories.
    This class is iterable over the cell types identified, and can be indexed by the cell type name.

    Parameters
    ----------
    directories : list or str
        A single or a list of multiple EcoTyper results (output) directories to get cell types from.
    """
    def __init__(self, directories : list ):
        self.cell_types = {}
        self.directories = directories if isinstance(directories, list) else [directories]
        
        for directory in self.directories:
            self._find_cell_types( directory )

    def _find_cell_types( self, directory : str ):
        """
        Find the cell types from a single EcoTyper results directory.

        Parameters
        ----------
        directory : str
            The EcoTyper results directory to get cell types from.
        """
        cell_types = [ i for i in os.listdir( directory ) if os.path.isdir( os.path.join( directory, i ) ) ]
        
        if settings.ecotypes_folder in cell_types: 
            cell_types.remove( settings.ecotypes_folder )

        for cell_type in cell_types:
            if cell_type not in self.cell_types:
                self.cell_types[cell_type] = [ os.path.join( directory, cell_type ) ]
            else:
                self.cell_types[cell_type] += [ os.path.join( directory, cell_type ) ]

    def __iter__( self ):
        """
        Iterate over the cell types.
        """
        return iter( self.cell_types )
    
    def __getitem__( self, key ):
        """
        Get the cell type directories.
        """
        return self.cell_types[key]
    
    def __repr__( self ):
        return f"{self.__class__.__name__}({self.directories})"
    
    def __str__( self ):
        return "Cell Types:\n" + "\n".join( list( self.cell_types.keys() ) )