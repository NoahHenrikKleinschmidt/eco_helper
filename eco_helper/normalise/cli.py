"""
Defines the "normalise" subcommand parser and its arguments
"""

from eco_helper.convert.funcs import filesuffix
import eco_helper.normalise.funcs as funcs
import eco_helper.normalise.NormTable as norm_table

def setup_parser( parent ):

    descr = "Normalise raw cuonts data to TPM or CPM."
    parser = parent.add_parser( "normalise", description=descr )
    parser.add_argument( "norm", help = "The type of normalisation to perform. Can be either 'tpm' or 'cpm'.", choices = ["tpm", "cpm"] )
    parser.add_argument( "input", help = "Input file." )
    parser.add_argument( "-o", "--output", help = "Output file. By default the same as the input with added suffix. The suffix will be either '.cpm' or '.tpm'", default = None )
    parser.add_argument( "-l", "--lengths", help = "Lengths file. If not provided, the lengths will be extracted from the GTF file.", default = None )
    parser.add_argument( "-g", "--gtf", help = "Reference GTF file for transcript lengths and/or gene names.", default = None )
    parser.add_argument( "-s", "--swap", help = "Use this when extracting new lengths from a GTF file to use the gene names as primary identifiers and not the gene ids. This command will swap the first and second columns (usually gene_id and gene_name). This is necessary when the data uses gene names instead of ids as primary identifiers.", action = "store_true" )
    parser.add_argument( "-n", "--names", help = "Use gene names instead of gene ids. This will replace the gene ids (index) in the expression matrix and lengths file with gene symbols from the GTF file or lengths file (if provided). Note, if a length file is provided then it must include gene names in the second column! Also note, this action will be performad after normalisation and only affect the identifiers in the output file!", action = "store_true" )
    parser.add_argument( "-d", "--digits", help = "The number of digits to round the values to.", type = int, default = 5 )
    parser.add_argument( "-log", "--logscale", help = "Use this to log-scale the normalised values.", action = "store_true" )
    parser.set_defaults( func = normalise_func )

def normalise_func( args ):
    """
    The core function of the "normalise" subcommand.
    """
    if args.output is None:
        args.output = args.input.replace( filesuffix( args.input )[0], f"{args.norm}.{ filesuffix(args.input)[0] }" )
    
    tpm = args.norm == "tpm"
    cpm = args.norm == "cpm"

    if tpm and args.lengths is None and args.gtf is None:
        raise ValueError( "Lengths file or GTF file must be provided for TPM normalisation." )
    if args.names and args.lengths is None and args.gtf is None:
        raise ValueError( "Lengths file or GTF file must be provided to get gene names." )
    
    # extract lengths from the GTF file if provided
    need_lengths_for_tpm = tpm and args.lengths is None and args.gtf is not None
    need_names_for_cpm = cpm and args.lengths is None and args.names 

    if need_lengths_for_tpm or need_names_for_cpm:

        lengths_file = f"{args.gtf}.lengths"
        funcs.call_gtftools( args.gtf, lengths_file, mode = "l" )
        funcs.add_gtf_gene_names( args.gtf, lengths_file, args.swap )
        args.lengths = lengths_file
    
    # now perform the normalisation
    normaliser = norm_table.NormTable( args.input )

    if need_lengths_for_tpm or args.names or args.lengths is not None:
        normaliser.set_lengths( args.lengths ) 

    if tpm:
        normaliser.to_tpm( digits = args.digits, log = args.logscale )
    elif cpm:
        normaliser.to_cpm( digits = args.digits, log = args.logscale )
    

    normaliser.save( args.output, use_names = args.names )