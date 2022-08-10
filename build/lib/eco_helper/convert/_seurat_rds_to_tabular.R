# This script allows to read an RDS file and convert it to TSV format.

library( logger )
library( argparse )
library( stringr )
library( Seurat )

get_args = function() {
    #' Setup the command line arguments parser
    #' @return args: The command line arguments
    
    descr = "Extract data from a SeuratObject in an RDS file to tabulary format."
    parser = argparse::ArgumentParser(description = descr)
    parser$add_argument( "input", help="Input RDS file" )
    parser$add_argument( "-o", "--output", help="Output file. By default the same name as the input is used.", default = NULL )
    parser$add_argument( "-d", "--data", help="The data slot to be extracted. This can be any slot accessible using GetAssayData( obj, slot = \"slot_name\" ). By default the counts slot is extracted.", default = "counts" )
    parser$add_argument( "-m", "--metadata", nargs="+", help="The metadata slot to be extracted. This can be any slot accessible using either @ or $. By default a 'meta.data' slot is tried extracted. It is also possible to extract multiple kinds of metadata when passing multiple values.", default = "meta.data" )
    parser$add_argument( "-s", "--separator", help="Separator to use in the output file. By default tabs are used.", default = "\t" )
    parser$add_argument( "-i", "--index", help="Use this to also export the index column (rownames) of extracted metadata tables.", action = "store_true" )
    args = parser$parse_args()
    return( args )
}

get.slot = function( obj, attr ){
    #' Get an attribute from an object. Using ``obj@attr`` syntax.
    #' @param obj: The object's symbol.
    #' @param attr: The attribute's name.
    #' @return result: The value or NULL.
    #' @export
    out = tryCatch( 
                    slot( obj, attr ),
                    error = function( err ){
                            return( NULL )
                    }
    
     )
    return( out )
}


get.attribute = function( obj, attr ){
    #' Get an attribute from an object. Using ``$obj[[attr]]`` syntax.
    #' @param obj: The object's symbol.
    #' @param attr: The attribute's name.
    #' @return result: The value or NULL.
    #' @export

    out = tryCatch( 
                    obj[[ attr ]],
                    error = function( err ){
                            return( NULL )
                    }
    
     )
    return( out )
}


get.from.seurat = function( obj, which = "counts", metadata = NULL ) {
    #' Extracts counts and metadata from a Seurat object and returns a list of two tables.
    #' @param obj: The Seurat object to extract data from.
    #' @param which: The type of data to extract. 
    #' This can be anything accessible via a `slot` when calling `GetAssayData` on the oject.
    #' By default `"counts"` (i.e. raw counts) are used.
    #' @param metadata: The metadata to extract. This can be a string or vector of anything that is directly gettable from the object via the `@` or `$` methods.
    #' @return data: A list of of counts and metadata as tables.
    #' @export

    # get the actual data
    # the SeuratObject contains both meta data and raw data attributes.
    
    tryCatch( 
                {
                    counts = GetAssayData( obj, slot = which )
                    counts = as.matrix( counts )
                    counts = as.data.frame( counts )
                },
        error = function( e )
                { 
                    log_debug( e$message ) 
                    log_fatal( "The given slot could not be accessed from the object!" )
                    counts = matrix( 0, nrow = 0, ncol = 0 )
                    stop( "The given slot could not be accessed from the object!" )
                }
            )

    # now try to extract any metadata from the object
    # if we only get a single metadata, assemble a vector to allow the subsequent loop
    extracted_metadata = list()
    if ( ! is.null( metadata ) ){

        for ( i in metadata ) {
            
            # first try to extract via @
            attr = get.slot( obj, i )

            # in case this fails, try to extract via $
            if ( is.null( attr ) ){
                attr = get.attribute( obj, i )  
            }

            # store if we have anything
            if ( ! is.null( attr ) ){
                extracted_metadata[[ i ]] = attr
            } else {
                log_warn( paste0( "The metadata '", i, "' could not be extracted!" ) )
            }
        }

        # if we did't get any metadata raise an error
        if ( length( extracted_metadata ) == 0 ){
            stop( "No metadata could not be accessed from the object using the given attribute(s)!" )
        }
    }

    return(
            list(  which = c( which, counts ), metadata = extracted_metadata  )
        )
}

# map the suffixes to the appropriate separator
suffixes = list(
                    "," = "csv",
                    ";" = "csv",
                    "\t" = "tsv",
                    " " = "txt"
                )

write.tabular = function( data, filename, sep, row.names = TRUE ){
    #' Write the extracted counts and metadata to TSV files.
    #' @param data: The extracted data list (containing a data (which) and metadata entry).
    #' @param filename: The filename to write the data to. 
    #' @param sep: The separator to use in the output file.
    #' @param row.names: Whether to write the row names as the first column. 
    #' Note, this will **only** affect the metadata tables, the rownames 
    #' are **always** included in the expression data. 
    #' @export
    
    # unpack the data
    name = data$which[[1]]
    which = data$which[[2]]
    metadata = data$metadata
    if ( sep == "t" ){ sep = "\t" } # just in case the backslash gets lost somewhere along the way...
    suffix = suffixes[[ sep ]]
    

    # now write the tables
    data_file = paste0( filename, ".", name, ".", suffix )
    log_info( paste("Writing", name, " to:", data_file ) )
    data_file = file.path( data_file )

    for ( i in names(metadata) ){

        metadata_file = paste0( filename, ".", i, ".", suffix )
        log_info( paste("Writing", i, " to:", metadata_file ) )
        metadata_file = file.path( metadata_file )

        write.table( metadata[[i]], metadata_file, sep = sep, row.names = row.names , quote = FALSE )

    }
    
}

main = function() {
    #' The main CLI function.
    
    args = get_args()

    log_info( paste( "Reading RDS file:", args$input ) )
    obj = readRDS( args$input )

    # get the data from the Seurat object
    log_info( paste( "Extracting data from Seurat object..." ) )
    data = get.from.seurat( obj, which = args$data, metadata = args$metadata )

    # clear the object to save memory
    rm( obj )

    # write the data to a table
    if (is.null( args$output )) {
        args$output = args$input
    }
    write.tabular( data = data, filename = args$output, sep = args$separator, row.names = args$index )

}
# run the script if called directly
if (sys.nframe() == 0){
    main()
}
