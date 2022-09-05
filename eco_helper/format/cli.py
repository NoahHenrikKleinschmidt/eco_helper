"""
Defines the "format" subcommand parser and its arguments
"""

import os
import eco_helper.format.formats as formats 
import eco_helper.format as core

def setup_parser( parent ):
    """
    Sets up the command line interface
    """
    descr = "Fix annotations in columns, index, and column names of tabular data files such as expression matrices and annotation files."
    parser = parent.add_parser( "format", description = descr )
    # parser.add_argument( "input", help = "The input file or directory. Note, if a directory is given, then any annotation file(s) must end with '.annotation' and any expression file(s) must end with '.count', '.countTable', or '.tpm'." )
    parser.add_argument( "input", help = "The input file." )
    parser.add_argument( "-o", "--output", help = "The output path. By default the file is saved to the same path it was read from (thereby overwriting the previous one!).", default = None )
    parser.add_argument( "-f", "--format", help = "A file specifying a dictionary of regex patterns for replacement.", default = None )
    parser.add_argument( "-s", "--suffix", help = "A suffix to add to the output file. This will not affect the file format and only serves to add additional information to the filename.", default = None )
    parser.add_argument( "-i", "--index", help = "Use this if the index should be re-formatted.", action = "store_true" )
    parser.add_argument( "-iname", "--indexname", help = "Use this to specify a name which the index should be given a name in the output file. Since the index is turned to a regular data column, the (replacement) index will not be written anymore. ", default = None )
    parser.add_argument( "-noid", "--noindex", help = "Use this if the index should not be written to the output file.", action = "store_true", default = None )

    parser.add_argument( "-n", "--names", help = "Use this if the column names (headers) should be re-formatted.", action = "store_true" )
    parser.add_argument( "-c", "--columns", nargs = "+", help = "Specify any number of columns within the annotation file to reformat values in.", default = None )
    parser.add_argument( "-p", "--pseudo", help = "Use this to only pseudo-read the given file. This is useful when the datafiles are very large to save memory.", action = "store_true", default = False )
    parser.add_argument( "-sep", "--separator", help = "Use this to specify the separator to use when reading the file. By default, the separator is guessed from the file extension. Otherwise `tsv` (for tab), `csv` (for comma), or `txt` (for space)  can be specified.", choices = ["tsv", "csv", "txt"], default = None )

    parser.add_argument( "-e", "--expression", help = "A preset for expression matrices equivalent to '--index --names --pseudo' ", action = "store_true" )
    parser.add_argument( "-ee", "--ecoexpression", help = "A preset for EcoTyper expression matrices equivalent to '--index --names --pseudo --format EcoTyper' ", action = "store_true" )
    parser.add_argument( "-a", "--annotation", help = "A preset for EcoTyper annotation files corresponding to '--index --indexname ID --columns CellType Sample --format EcoTyper' ", action = "store_true" )
    parser.set_defaults( func=format )
    return parser

def format( args ):
    """
    The core function of the 'format' command.
    """

    if os.path.isdir( args.input ):
        raise ValueError( "The 'format' command does not support directories." )
    
    # first check for the presets we may have got:
    _apply_presets(args)
    
     # now get the formats dictionary to use
    format = _read_formats( args.format )


    # now we can actually do the formatting
    formatter = core.Formatter( formats = format )

    formatter.read_table( args.input, sep = args.separator, pseudo = args.pseudo )

    formatter.reformat( index = args.index, names = args.names, columns = args.columns )

    if args.indexname is not None:
        formatter.index_to_column( args.indexname )
        args.noindex = True

    if args.output is None:
        args.output = args.input
    
    formatter.write_table( args.output, suffix = args.suffix, index = not args.noindex )

    # # if args.annotation :
    # #         formatter.read_annotation_table( args.input, id_is_index = args.index, id_colname = args.indexname )
    # #         save_func = formatter.save_annotation_table
    # #         get_func = formatter._last_annotation

    # # elif args.expression :
    # #     formatter.read_expression_matrix( args.input, pseudo = args.pseudo )
    # #     save_func = formatter.save_expression_matrix
    # #     get_func = formatter._last_matrix

    # formatter.reformat( columns = args.columns )

    # # and now save the output
    # if args.output is None or os.path.isdir( args.output ):
    #     formatter.save_to_dir( args.output, args.suffix )
    # elif args.output is not None:
    #     suffix = "" if not args.suffix else args.suffix
    #     outfile = f"{ os.path.abspath( args.output ) }{ suffix }"        
    #     save_func( outfile, get_func() )
    # else:
    #     formatter.save_to_dir( args.output, args.suffix )

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