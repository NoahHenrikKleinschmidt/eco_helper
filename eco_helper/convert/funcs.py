"""
These are the main conversion functions that are used by ``eco_helper convert``.
"""

import eco_helper.convert.mtx as mtx
import eco_helper.convert.tabular as tabular
import eco_helper.convert.seurat as seurat


def from_seurat_to_tabular( 
                            filename : str, 
                            output : str, 
                            sep : str, 
                            which : str, 
                            metadata : list, 
                            index : str ):
    """
    Convert a Seurat object to tabular file(s) for the extracted data and any additional metadata.
    
    Parameters
    ----------
    filename : str
        The name of the RDS file containing a SeuratObject.
    output : str
        The name of the output filename. The actually created files will 
        use this as a base name and attach their symbols to the filenames.
    sep : str
        The separator to use.
    which : str
        The data to extract from the SeuratObject. This can be any slot that is accessible via `GetAssayData` from the SeuratObject.
    metadata : list
        The metadata to extract from the SeuratObject. This can be any number slots or attributes that is accessible from SeuratObject.
    index : bool
        Whether to include the index in the output of metadata files.
    """
    if metadata is None:
        metadata = seurat.default_metadata
    if isinstance( metadata, str ): 
        metadata = [ metadata ]
    seurat.to_tabular( filename, output, sep, which, metadata, index )


def from_mtx_to_tabular( filename : str, output : str, sep : str, **kwargs ):
    """
    Convert an mtx file to tabular file(s).
    
    Parameters
    ----------
    filename : str
        The name of the mtx file.
    output : str
        The name of the output filename. The actually created files will 
        use this as a base name and attach their symbols to the filenames.
    sep : str
        The separator to use.
    """
    data = mtx.read( filename )

    # we want to save the index in case it is not a default integer index
    index = kwargs.pop( "index", None )
    if index is None and isinstance( data.index.values[0], str ):
        index = True
   
    tabular.write( data, output, sep, index = index, **kwargs )


def from_tabular_to_mtx( filename : str, output : str, sep : str, **kwargs ):
    """
    Convert a tabular file to mtx files.
    
    Parameters
    ----------
    filename : str
        The name of the tabular file.
    output : str
        The name of the output filename. The actually created files will 
        use this as a base name and attach their symbols to the filenames.
    sep : str
        The separator to use.
    """
    data = tabular.read( filename, sep, **kwargs )
    mtx.write( data, output )

def between_tabulars( filename : str, output : str, sep_in : str, sep_out : str, **kwargs ):
    """
    Convert a tabular files to one another.
    
    Parameters
    ----------
    filename : str
        The name of the tabular file.
    output : str
        The name of the output filename. The actually created files will 
        use this as a base name and attach their symbols to the filenames.
    sep_in : str
        The separator to use for the input file.
    sep_out : str
        The separator to use for the output file.
    """
    index = kwargs.pop( "index", False )
    data = tabular.read( filename, sep_in, **kwargs )
    tabular.write( data, output, sep_out, index = index, **kwargs )


def filesuffix( filename ): 
    """
    Returns the suffix of the filename and a location of the delimiting dot. This will be -1 if NO dots were found! (Error indication)

    Parameters
    ----------
    filename : str  
        The name of the file. 

    Returns
    -------
    str
        The suffix of the file. Or the full filename if no dots were found to delimit a suffix.
    int
        The location of the dot in the filename. -1 if no dot was found.
    """
    loc = filename.rfind( "." )
    return filename[ loc + 1 : ], loc