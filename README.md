
eco_helper
==========


[![Documentation Status](https://readthedocs.org/projects/eco-helper/badge/?version=master)](https://eco-helper.readthedocs.io/en/master/?badge=master)
[![CodeFactor](https://www.codefactor.io/repository/github/noahhenrikkleinschmidt/eco_helper/badge)](https://www.codefactor.io/repository/github/noahhenrikkleinschmidt/eco_helper)


This is `eco_helper` - a package that offers various command line tools to automate data pre processing with the aim to facilitate working with the [EcoTyper framework](https://github.com/digitalcytometry/ecotyper). While the toolbox is streamlined to work specifically to accomodate the requirements of EcoTyper, the tools are usually customizable and/or perform operations that are useful in a wide field of applications. 

Basic usage
===========
`eco_helper` is primarily intended as a command line tool. However, `eco_helper` can also be used as a python package and be included in your own scripts. In fact, some few functionalities are only available throught the code API, such as passing kwargs to file-reading functions. `eco_helper`'s main command line interface offers four commands: 

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

```bash
eco_helper enrich [--prerank] [--enrichr] [--assemble] [--gene_sets <gene sets>] [--output <output>] <input>
```

to perform gene set enrichment analysis on EcoTyper results using [gseapy](https://github.com/zqfang/GSEApy).

```bash
eco_helper drop [--samples <samples>] [--celltypes <celltypes>] [--ids <ids>] <annotation> <expression>
```

to remove entries from the an EcoTyper dataset. Entries can be directly specified by their _ids_, or entire cell-types or samples can be removed.


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

`eco_helper enrich`
-------------------

```bash
usage: eco_helper enrich [-h] [-o OUTPUT] [-g GENE_SETS [GENE_SETS ...]] [-p] [-e] [-a] [-E] [-n] [--notebook_config NOTEBOOK_CONFIG] [--organism ORGANISM]
                         [--size SIZE SIZE] [--permutations PERMUTATIONS]
                         input

This command performs gene set enrichment analysis using `gseapy` on the results of an EcoTyper analysis.

positional arguments:
  input                 The directory storing the EcoTyper results.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory. By default a '<input>_gseapy_results' directory within the same location as the input directory.
  -g GENE_SETS [GENE_SETS ...], --gene_sets GENE_SETS [GENE_SETS ...]
                        The reference gene sets to use for enrichment analysis. This can be any number of accepted gene set inputs for gseapy enrichr or prerank.
  -p, --prerank         Use this to perform gseapy prerank analysis.
  -e, --enrichr         Use this to perform gseapy enrichr analysis.
  -a, --assemble        By default each cell type will produce a separate file for each cell state enrichment analysis. Using the `--assemble` option, all cell-
                        state files from one cell type will be merged together to a single file. In this case the individual files are removed.
  -E, --ecotypes        Use this to only analyse cell-types and states contributing to Ecotypes. In this case each Ecotype will receive a subdirectory with its
                        enrichment results files. Note, in this case the files will *not* be assembled, and any non-Ecotype-contributing cell-type and state will
                        not be analysed.
  -n, --notebook        Generate a jupyter notebook to analyse the enrichment results. If this option is specified, then the <intput> argument is interpreted as
                        the filename of the notebook to generate. By specifying '-' as filename a default filename with the dataset name is used.
  --notebook_config NOTEBOOK_CONFIG
                        The configuration file for notebook generation. This is required for the notebook to be generated.
  --organism ORGANISM   Set the reference organism. By default the organism is set to 'human'.
  --size SIZE SIZE      [prerank only] Set the minimum and maximum number of gene matches for the reference gene sets and the data. By default 5 and 500 are used.
                        Note, this will require a two number input for min and max.
  --permutations PERMUTATIONS
                        [prerank only] Set the number of permutations to use for the prerank analysis. By default 1000 is used.
```



`eco_helper drop`
-------------------

```bash
usage: eco_helper drop [-h] [-s SAMPLES [SAMPLES ...]] [-c CELLTYPES [CELLTYPES ...]] [-i IDS [IDS ...]] [-o OUTPUT] annotation expression

This command allows removal of entries from EcoTyper datasets.

positional arguments:
  annotation            The file storing the annotations.
  expression            The file storing the expression matrix.

options:
  -h, --help            show this help message and exit
  -s SAMPLES [SAMPLES ...], --samples SAMPLES [SAMPLES ...]
                        The samples whose entries to drop
  -c CELLTYPES [CELLTYPES ...], --celltypes CELLTYPES [CELLTYPES ...]
                        The cell-types whose entries to drop
  -i IDS [IDS ...], --ids IDS [IDS ...]
                        Specific entries to drop
  -o OUTPUT, --output OUTPUT
                        The output basename. This will generate a <basename>.annotation.tsv and <basename>.expression.tsv file. By default, the input filenames are
                        appended by '.drop' at the end.
```

