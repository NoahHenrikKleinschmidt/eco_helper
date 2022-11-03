"""
Auxiliary functions for the main CLI `convert_func`
"""

import eco_helper.convert.funcs as funcs

def _prep_formats(input, output, fmt_in, fmt_out):
    """
    Prepares the input and output formats.
    """
    if fmt_in is None:
        fmt_in,_ = funcs.filesuffix( input )
    if fmt_out is None:
        fmt_out,_ = funcs.filesuffix( output )

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

