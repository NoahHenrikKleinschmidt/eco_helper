"""
Defines wrapper functions to call the `_seurat_rds_to_tabular.R` script, 
to read from an RDS file storing `SeuratObject` and to write to tabular files of the data and metadata.

Note
----
While this module allows CLI use of the udnerlying Rscript, the Rscript itself also has a 
fully implemented CLI and can thus also be used as a stand-alone if desired.
"""
import os
import eco_helper.core.terminal_funcs as tfuncs

supported_formats = ( "rds", "seurat" )
"""
The supported formats (i.e. file suffixes) to interpret as storing a SeuratObject.
"""

default_metadata = [ "meta.data" ]
"""
The default metadata to extract from a SeuratObject.
"""

def to_tabular( 
                            filename : str, 
                            output : str, 
                            sep : str, 
                            which : str, 
                            metadata : list, 
                            index : bool ):
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
    seurat_conversion_script = os.path.abspath( os.path.dirname( __file__ ) ) 
    seurat_conversion_script = os.path.join( seurat_conversion_script, "_seurat_rds_to_tabular.R" )

    metadata = " ".join( metadata )
    index = f"-i " if index else ""
    
    cmd = f"Rscript {seurat_conversion_script} {filename} --output {output} --separator '{sep}' {index}--data {which} --metadata {metadata}"
    tfuncs.run( cmd )