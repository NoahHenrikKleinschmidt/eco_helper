"""
Defines the "format" subcommand parser and its arguments
"""

import os
import eco_helper.format.formats as formats 
import eco_helper.format as core

def _apply_presets(args):
    """
    Applies the presets for expression, ecoexpression, and annotation to the arguments...
    """
    if args.expression:
        args.index = True
        args.names = True
        args.pseudo = True
    elif args.ecoexpression:
        args.index = True
        args.names = True
        args.pseudo = True
        args.format = "EcoTyper"
    elif args.annotation:
        args.index = True
        args.indexname = "ID"
        args.columns = ["CellType", "Sample"]
        args.pseudo = True
        args.format = "EcoTyper"

def _read_formats( f ):
    """
    Reads a formats file if it was passed, else just load the E
    """
    if f is not None:
        if os.path.exists( f ):
            return core.read_formats_file( f )
        else:
            _f = formats.available_formats.get( f, None )
            if _f is None:
                raise ValueError( f"The format '{f}' is not available. Try defining your own file and submitting that to --formats." )
            return _f
    else:
        raise ValueError( "No formats are specified." )