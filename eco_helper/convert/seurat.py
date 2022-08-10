"""
Defines wrapper functions to call the `_seurat_rds_to_tabular.R` script.
"""
import os
import eco_helper.core.terminal_funcs as tfuncs

supported_formats = ( "rds", "seurat" )
"""
The supported formats (i.e. file suffixes) to interpret as storing a SeuratObject.
"""

def to_tabular( 
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
    """
    seurat_conversion_script = os.path.abspath( os.path.dirname( __file__ ) ) 
    seurat_conversion_script = os.path.join( seurat_conversion_script, "_seurat_rds_to_tabular.R" )
    metadata = " ".join( metadata )
    cmd = f"Rscript {seurat_conversion_script} --output {output} --separator {sep} --data {which} --metadata {metadata} --index {index} {filename}"
    tfuncs.run( cmd )