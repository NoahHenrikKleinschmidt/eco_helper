"""
These are core functions to reformat datafiles.
"""

def read_formats_file( filename : str ) -> dict:
    """
    Reads a file containing a dictionary of invalid characters to valid characters.
    
    Parameters
    ----------
    filename : str
        The name of the file containing the dictionary.
    
    Returns
    -------
    dict
        A dictionary of invalid characters to valid characters.
    """
    with open( filename, "r" ) as f:
        lines = f.readlines()
    formats = {}
    for line in lines:
        line = line.strip()
        if line.startswith( "#" ) or line == "":
            continue
        key, value = line.split( ":" )
        formats[ key.strip() ] = value.strip()
    return formats
