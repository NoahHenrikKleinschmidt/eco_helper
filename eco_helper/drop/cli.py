"""
Defines the "drop" subcommand parser and its arguments
"""



def setup_parser( parent ):

    descr = "This command allows removal of entries from EcoTyper datasets."
    drop = parent.add_parser( "drop", description=descr )
    drop.add_argument( "annotation", help = "The file storing the annotations." )
    drop.add_argument( "expression", help = "The file storing the expression matrix." )
    drop.add_argument( "-s", "--samples", help = "The samples whose entries to drop", nargs = "+", default = None )
    drop.add_argument( "-c", "--celltypes", help = "The cell-types whose entries to drop", nargs = "+", default = None )
    drop.add_argument( "-i", "--ids", help = "Specific entries to drop", nargs = "+", default = None )
    drop.add_argument( "-o", "--output", help = "The output basename. This will generate a <basename>.annotation.tsv and <basename>.expression.tsv file. By default, the input filenames are appended by '.drop' at the end.", default = None )
    drop.set_defaults( func = drop_func )

def drop_func( args ):
    """
    Performs the main entry dropping function.
    """

    import eco_helper.core.dataset as ds
    import eco_helper.drop.funcs as funcs

    # load the data
    dataset = ds.Dataset( args.annotation, args.expression )

    if args.ids is not None:
        dataset = funcs.drop_ids( dataset, args.ids )
    if args.samples is not None:
        dataset = funcs.drop_samples( dataset, args.samples )
    if args.celltypes is not None:
        dataset = funcs.drop_celltypes( dataset, args.celltypes )

    # write the output
    if args.output is None:
        annotation = args.annotation + ".drop"
        expression = args.expression + ".drop"
    else:
        annotation = args.output + ".annotation.tsv"
        expression = args.output + ".expression.tsv"
    
    dataset.write( annotation, expression )