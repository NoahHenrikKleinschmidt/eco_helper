"""
Defines the "convert" subcommand parser and its arguments
"""

import os
import eco_helper.convert.tabular as tabular
import eco_helper.convert.funcs as funcs
import eco_helper.convert.seurat as seurat

def setup_parser( parent ):

    descr = "This command converts between different formats. It is able to convert tabular dataformats (csv,tsv,txt) to and from mtx format. It can also extract data from a SeuratObject (stored in an RDS file) and convert the data to tabular formats."
    convert = parent.add_parser( "convert", description=descr )
    convert.add_argument( "input", help = "Input file." )
    convert.add_argument( "-o", "--output", help = "Output file. By default the same as the input with altered suffix.", default = None )
    convert.add_argument( "-r", "--recursive", action = "store_true", help = "Use this to mark the output as a directory rather than a target output file", default = False )
    convert.add_argument( "--from", dest = "fmt_in", help = "The input format in case it is not evident from the input file suffix.", default = None )
    convert.add_argument( "--to", dest = "fmt_out", help = "The output format in case it is not evident from the output file suffix.", default = None )
    convert.add_argument( "-i", "--index", help = "Use this to also save the index (rownames) to tabular output files. By default the index will NOT be written to the output files. In case of SeuratObject data this option only applies to metadata tables. The extracted data will **always** have an index.", action = "store_true", default = False )
    convert.add_argument( "-d", "--data", help = "[Used only for Seurat-RDS] The data to extract from the SeuratObject. If not specified, by default the 'counts' slot will be extracted.", default = None )
    convert.add_argument( "-m", "--metadata", help = "[Used only for Seurat-RDS] The metadata to extract from the SeuratObject. This may be any number accessible slots or attributes of the SeuratObject. If not specified, by default a 'meta.data' attribute is tried to be extracted.", default = None )
    convert.set_defaults( func=convert_func )


def convert_func( args ):
    """
    Converts the input file to the output file.

    Note
    ----
    This is the core function behind the `eco_helper convert` command.

    Parameters
    ----------
    args : Namespace
        The arguments passed to the command line.
    
    Namespace attributes
    --------------------
    input : str
        The input file.
    output : str
        The output file.
    fmt_in : str
        The input format.
    fmt_out : str
        The output format.
    data : str
        The data to extract from the SeuratObject. If not specified, by default the 'counts' slot will be extracted.
    metadata : str
        The metadata to extract from the SeuratObject. This may be any number accessible slots or attributes of the SeuratObject. If not specified, by default a 'meta.data' attribute is tried to be extracted.
    index : bool
        Use this to also save the index to tabular output files. By default the index will NOT be written. In case of a SeuratObject this attribute only applies to metadata tables, the data will always have the index.
    """
    input, output, fmt_in, fmt_out, data, metadata, index, make_dir = args.input, args.output, args.fmt_in, args.fmt_out, args.data, args.metadata, args.index, args.recursive

    # start with some error handling

    if fmt_out is None and output is None:
        raise ValueError( "An output file is required if no output format is specified. Or vice versa an output format when no output is specified." )

    elif output is None and make_dir:
        raise FileNotFoundError( "Cannot create non-specified output directory" )

    elif fmt_out is None and not make_dir:
        fmt_out,loc = _suffix( output )
        if loc == -1:
            raise ValueError( "No output format specified and no output file suffix found in output file name." )

    elif fmt_out is None and make_dir:
        raise ValueError( "An output format is required when specifying an output directory" )

    elif fmt_out is not None and make_dir:
        os.makedirs( output, exist_ok=True )
        outfile = _assemble_outfile_name(input, fmt_out)
        output = os.path.join( output, os.path.basename(outfile) )
        output = os.path.abspath( output ) 
    
    fmt_in, fmt_out = _prep_formats(input, output, fmt_in, fmt_out)
    
    print( output )
    # now the actual conversion

    if fmt_in in tabular.supported_formats:
        sep_in = tabular.separators[fmt_in]

        if fmt_out in tabular.supported_formats:
            sep_out = tabular.separators[fmt_out]
            funcs.between_tabulars( input, output, sep_in, sep_out, index = index )
        
        elif fmt_out == "mtx":
            funcs.from_tabular_to_mtx( input, output, sep_in )

        else:
            raise ValueError(f"Cannot convert from {fmt_in} to {fmt_out}")

    elif fmt_in == "mtx":
        if fmt_out in tabular.supported_formats:
            sep_out = tabular.separators[fmt_out]
            funcs.from_mtx_to_tabular( input, output, sep_out )
        else:
            raise ValueError(f"Cannot convert from {fmt_in} to {fmt_out}")
    
    elif fmt_in in seurat.supported_formats:
        if metadata is None:
            metadata = "meta.data"
        if fmt_out in tabular.supported_formats:
            sep_out = tabular.separators[fmt_out]
            funcs.from_seurat_to_tabular( input, output, sep_out, data, metadata, index )
        else:
            raise ValueError(f"Cannot convert from {fmt_in} to {fmt_out}")

def _prep_formats(input, output, fmt_in, fmt_out):
    """
    Prepares the input and output formats.
    """
    if fmt_in is None:
        fmt_in,_ = _suffix( input )
    if fmt_out is None:
        fmt_out,_ = _suffix( output )

    fmt_in = fmt_in.lower()
    fmt_out = fmt_out.lower()
    return fmt_in,fmt_out

def _assemble_outfile_name(input, fmt_out):
    """
    Assembles the output file name from the input file name and the output format.
    """
    # we find the last occurrence of a dot and assume that thereafter is the output suffix
    # we crop the filename there and add the new file suffix.
    return input[ : input.rfind( "." ) ] + f".{fmt_out}"

def _suffix( filename ) -> str: 
    """
    Returns the suffix of the filename and a location of the delimiting dot. This will be -1 if NO dots were found! (Error indication)
    """
    loc = filename.rfind( "." )
    return filename[ loc + 1 : ], loc