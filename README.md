
eco_helper
==========

This is `eco_helper` - a package that offers various command line tools to automate data pre processing with the aim to facilitate working with the [EcoTyper framework](https://github.com/digitalcytometry/ecotyper). While the toolbox is streamlined to work specifically to accomodate the requirements of EcoTyper, the tools are usually customizable and/or perform operations that are useful in a wide field of applications. 

Basic usage
===========
`eco_helper` is primarily intended as a command line tool. However, `eco_helper` can also be used as a python package and be included in your own scripts. In fact, some few functionalities are only available throught the code API, such as passing kwargs to file-reading functions. `eco_helper`'s main command line interface offers three commands: 

```bash
eco_helper convert [--from <from>] [--to <to>] [--output <output>] <input>
```

to convert one data format to another. Currently, supported are tabular formats (tsv, csv, txt), matrix transfer archives (mtx), and SeuratObjects in rds files (to tabular).


```bash
eco_helper normalise <norm> [--lengths <lengths>] [--gtf <gtf>] [--names] [--output <output>] <input>
```

to normalise raw counts data to either *TPM* or *CPM*.

```bash
eco_helper format [--index] [--names] [--columns <columns>] [--output <output>] [--pseudo] [--formats <formats>] <input>
```

to re-format data columns, data headers (column names), and or index (rownames) within data files using **regex** substitutions. This is intended to remove invalid characters such as "-" or " " (space), which EcoTyper does not allow in its input data. However, any kind of python-regex substitutions can be performed.


Command Line Interface
======================

More information about the command line interface and the underlying package is available via the documentation. Here a summary of the full command line interface of `eco_helper` and its sub-commands shall be given. 

`eco_helper convert`
--------------------

```bash
usage: eco_helper convert [-h] [-o OUTPUT] [-r] [--from FMT_IN] [--to FMT_OUT]
                            [-i] [-d DATA] [-m METADATA [METADATA ...]]
                            input

    This command converts between different formats. It is able to convert tabular
    dataformats (csv,tsv,txt) to and from mtx format. It can also extract data
    from a SeuratObject (stored in an RDS file) and convert the data to tabular
    formats.

    positional arguments:
    input                 Input file.

    options:
    -h, --help            show this help message and exit
    -o OUTPUT, --output OUTPUT
                            Output file. By default the same as the input with
                            altered suffix.
    -r, --recursive       Use this to mark the output as a directory rather than
                            a target output file.
    --from FMT_IN         The input format in case it is not evident from the
                            input file suffix.
    --to FMT_OUT          The output format in case it is not evident from the
                            output file suffix.
    -i, --index           Use this to also save the index (rownames) to tabular
                            output files. By default the index will NOT be written
                            to the output files. In case of SeuratObject data this
                            option only applies to metadata tables. The extracted
                            data will **always** have an index.
    -d DATA, --data DATA  [Used only for Seurat-RDS] The data to extract from
                            the SeuratObject. If not specified, by default the
                            'counts' slot will be extracted.
    -m METADATA [METADATA ...], --metadata METADATA [METADATA ...]
                            [Used only for Seurat-RDS] The metadata to extract
                            from the SeuratObject. This may be any number
                            accessible slots or attributes of the SeuratObject. If
                            not specified, by default a 'meta.data' attribute is
                            tried to be extracted.
```

`eco_helper normalise`
----------------------
```bash
usage: eco_helper normalise [-h] [-o OUTPUT] [-l LENGTHS] [-g GTF] [-n]
                            [-d DIGITS] [-log]
                            {tpm,cpm} input

    Normalise raw counts data to TPM or CPM.

    positional arguments:
    {tpm,cpm}             The type of normalisation to perform. Can be either
                            'tpm' or 'cpm'.
    input                 Input file.

    options:
    -h, --help            show this help message and exit
    -o OUTPUT, --output OUTPUT
                            Output file. By default the same as the input with
                            added suffix. The suffix will be either '.cpm' or
                            '.tpm'
    -l LENGTHS, --lengths LENGTHS
                            Lengths file. If not provided, the lengths will be
                            extracted from the GTF file.
    -g GTF, --gtf GTF     Reference GTF file for transcript lengths and/or gene
                            names.
    -n, --names           Use gene names instead of gene ids. This will replace
                            the gene ids (index) in the expression matrix and
                            lengths file with gene symbols from the GTF file or
                            lengths file (if provided). Note, if a length file is
                            provided then it must include gene names in the second
                            column!
    -d DIGITS, --digits DIGITS
                            The number of digits to round the values to.
    -log, --logscale      Use this to log-scale the normalised values.
```

`eco_helper format`
-------------------
```bash
usage: eco_helper format [-h] [-o OUTPUT] [-f FORMAT] [-s SUFFIX] [-i]
                            [-iname INDEXNAME] [-noid] [-n]
                            [-c COLUMNS [COLUMNS ...]] [-p] [-sep SEPARATOR] [-e]
                            [-ee] [-a]
                            input

    Fix annotations in columns, index, and column names of tabular data files such
    as expression matrices and annotation files.

    positional arguments:
    input                 The input file.

    options:
    -h, --help            show this help message and exit
    -o OUTPUT, --output OUTPUT
                            The output path. By default the file is saved to the
                            same path it was read from (thereby overwriting the
                            previous one!).
    -f FORMAT, --format FORMAT
                            A file specifying a dictionary of regex patterns for
                            replacement.
    -s SUFFIX, --suffix SUFFIX
                            A suffix to add to the output file. This will not
                            affect the file format and only serves to add
                            additional information to the filename.
    -i, --index           Use this if the index should be re-formatted.
    -iname INDEXNAME, --indexname INDEXNAME
                            Use this to specify a name which the index should be
                            given a name in the output file. Since the index is
                            turned to a regular data column, the (replacement)
                            index will not be written anymore.
    -noid, --noindex      Use this if the index should not be written to the
                            output file.
    -n, --names           Use this if the column names (headers) should be re-
                            formatted.
    -c COLUMNS [COLUMNS ...], --columns COLUMNS [COLUMNS ...]
                            Specify any number of columns within the annotation
                            file to reformat values in.
    -p, --pseudo          Use this to only pseudo-read the given file. This is
                            useful when the datafiles are very large to save
                            memory.
    -sep SEPARATOR, --separator SEPARATOR
                            Use this to specify the separator to use when reading
                            the file. By default, the separator is guessed from
                            the file extension. Otherwise `tsv` (for tab), `csv`
                            (for comma), or `txt` (for space) can be specified.
    -e, --expression      A preset for expression matrices equivalent to '--
                            index --names --pseudo'
    -ee, --ecoexpression  A preset for EcoTyper expression matrices equivalent
                            to '--index --names --pseudo --format EcoTyper'
    -a, --annotation      A preset for EcoTyper annotation files corresponding
                            to '--index --indexname ID --columns CellType Sample
                            --format EcoTyper'
```