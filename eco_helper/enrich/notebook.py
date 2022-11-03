"""
The `EnrichmentNotebook` class creates a Jupyter notebook for enrichment data analysis.
This notebook is mostly auto-generated and can be used as a setup for manual final analysis.
"""
import nbformat.v4 as nbf
import eco_helper.enrich.EnrichmentCollection as EnrichmentCollection
import eco_helper.enrich.visualise as visualise
import yaml
import os
import logging 

from alive_progress import alive_bar


class EnrichmentNotebook:
    """
    Generate a new notebook for enrichment results analysis. 
    This will automatically analyse the results of the enrichment cell-type and 
    cell-state wise or ecotype and cell-state wise 
    if a reference yaml file of categories to check for is provided.

    Parameters
    ----------
    config : str
        The yaml config file containing the metainfo for building the new notebook.
    """
    def __init__(self, config : str ):
        self.config = yaml.safe_load( open(config, "r") )
        self._load_from_config()

        self._filename = None
        self._notebook = self._load_template()

        self._update_directories()
        self._set_gene_sets()

    def execute( self, filename : str = None ):
        """
        Execute the notebook.

        Parameters
        ----------
        filename : str
            The filename to save the notebook to.
        """
        filename = self._filename if not filename else filename
        if not filename:
            filename = f"enrichment_analysis_{ os.path.basename(self._ecotyper_dir) }.ipynb"
        self._filename = filename

        self.save_notebook( filename )
        cmd = f"jupyter nbconvert --execute --to notebook {filename}"
        os.system( cmd )

        # and rename the .nbconvert notebook to the actually desired filename and remove the nbconvert tmp file
        nbfile = f"{filename.replace('.ipynb', '')}.nbconvert.ipynb"
        os.system( f"mv {nbfile} {filename}" ) # ; rm {nbfile.replace( '.ipynb', '*' )}" )

    def load_notebook( self, filename : str ):
        """
        Load a jupyter notebook as template.

        Parameters
        ----------
        filename : str
            The path to the notebook to load.
        """
        with open( filename, "r" ) as template:
            self._notebook =  nbf.reads( template.read() )

        self._update_directories()
        self._set_gene_sets()

    def save_notebook( self, filename : str ):
        """
        Save the notebook to a file.

        Parameters
        ----------
        filename : str
            The filename to save the notebook to.
        """
        self._filename = filename
        with open( filename, "w" ) as output:
            output.write( nbf.writes( self._notebook ) )

    def markdown_cell( self, contents : str, index : int = None ):
        """
        Add a markdown cell to the notebook.

        Parameters
        ----------
        contents : str
            The markdown contents to add.
        index : int
            The index to add the cell at.
        """
        cell = nbf.new_markdown_cell( contents )
        if index is None:
            self._notebook.cells.append( cell )
        else:
            self._notebook.cells.insert( index, cell )

    def code_cell( self, contents : str, index : int = None ):
        """
        Add a code cell to the notebook.

        Parameters
        ----------
        contents : str
            The code contents to add.
        index : int
            The index to add the cell at.
        """
        cell = nbf.new_code_cell( contents )
        if index is None:
            self._notebook.cells.append( cell )
        else:
            self._notebook.cells.insert( index, cell )

    def analyse_results( self, which : str = "enrichr" ):
        """
        Add the cells to analyse the enrichment results.

        Parameters
        ----------
        which : str
            Which analysis to perform. Either "enrichr" or "prerank".
        """
        if self._enrichment_categories is None:
            raise ValueError( "No enrichment categories were provided. Cannot analyse results." )
        
        resolution = "ecotype" if self._ecotype_resolution else "celltype"
        collection = self._get_collection(which, resolution)
        _collection_var, x, y = self._make_prep_cells( which )

        self.markdown_cell( "> **Note**<br>\n> The following code is auto-generated by `eco_helper`" )
        
        if self._ecotype_resolution:
            self._analyse_by_ecotypes(which, collection, _collection_var, x, y)
        else: 
            self._analyse_by_celltype(which, collection, _collection_var, x, y)


    def _set_gene_sets( self ):
        """
        Set the gene sets to query against in the gene set enrichment analysis.
        """
        self[ 4 ].source = self[ 4 ].source.format( __gene_sets__ = self.gene_sets )
        
    def _load_from_config( self ):
        """
        Loads properties from the config
        """
        self._parent = self.config["directories"]["parent"]
        self._results_dir = self.config["directories"]["results"]
        self._ecotyper_dir = self.config["directories"]["ecotyper_dir"]
        self._enrichment_dir = self.config["directories"]["enrichment_results"]
        self._outdir = self.config["directories"]["outdir"]

        self._perform_enrichment = self.config["enrichment"]["perform_enrichment"]
        self._ecotype_resolution = self.config["enrichment"]["ecotype_resolution"]
        self._enrichr = self.config["enrichment"]["enrichr"]
        self._prerank = self.config["enrichment"]["prerank"]
        self.gene_sets = self.config["enrichment"]["gene_sets"]

        self._enrichment_categories = self.config["analysis"]["references"]
        self._topmost = self.config["analysis"]["top_most_fraction"]
        self._cutoff = self.config["analysis"]["cutoff"]

    def _load_template( self ):
        """
        Load the template notebook
        """
        notebook = os.path.join( os.path.dirname( __file__ ), "enrichment_template.ipynb" )
        with open( notebook, "r" ) as template:
            return nbf.reads( template.read() )
    
    def _update_directories( self ):
        """
        Update the various directories in the notebook.
        """
        self[ 2 ].source = self[ 2 ].source.replace( "__ecotyper_dir__",  self._ecotyper_dir )
        self[ 2 ].source = self[ 2 ].source.replace( "__outdir__",  self._outdir )
        self[ 2 ].source = self[ 2 ].source.replace( "__perform_enrichment__",  str(self._perform_enrichment) )

        self[ 4 ].source = self[ 4 ].source.replace( "__enrichr__",  str(self._enrichr) ) 
        self[ 4 ].source = self[ 4 ].source.replace( "__prerank__",  str(self._prerank) )
        self[ 4 ].source = self[ 4 ].source.replace( "__ecotype_resolution__",  str(self._ecotype_resolution) )
        
        self[ 9 ].source = self[ 9 ].source.replace( "__parent__", self._parent )
        self[ 9 ].source = self[ 9 ].source.replace( "__results_dir__", self._results_dir )
        self[ 9 ].source = self[ 9 ].source.replace( "__enrichment_dir__", self._enrichment_dir )

    def _get_collection(self, which, resolution):
        """
        Try to load enrichment data and if none are available yet, 
        run the notebook to generate them.
        """
        try: 
            collection = EnrichmentCollection( self.data_dir, resolution = resolution, which = which )
        
        except FileNotFoundError:
            logging.info( "No enrichment data available yet. Running the notebook to generate them." )
            # get the temporary notebook file and remove it again after running
            self.execute( ".tmpnotebook.ipynb" )
            os.remove( ".tmpnotebook.ipynb" )
        
            # now try to get the loaded data again to see if it's now available
            try:
                collection = EnrichmentCollection( self.data_dir, resolution = resolution, which = which )
            except Exception as e:
                raise e

        return collection


    def _analyse_by_celltype(self, which, collection, _collection_var, x, y):
        """
        Add the cells to analyse the enrichment results by celltype where each celltype's
        found cell states are included in full but no information about the ecotypes is available.

        Parameters
        ----------
        which : str
            Which analysis to perform. Either "enrichr" or "prerank".
        collection : EnrichmentCollection
            The collection of enrichment results to analyse.
         _collection_var : str
            The variable name of the collection (enrichr or prerank).
        x : str
            The variable name of the x-axis (for highlight cutoff in the prerun).
        y : str
            The variable name of the y-axis (for highlight cutoff in the prerun).
        """

        self.markdown_cell( f"# Enrichment results for cell-types ({which})" )
        self._celltype_res_make_get_state_df_cell( _collection_var )
        
        self._make_plotly_collection_summary( _collection_var )
        self._make_matplotlib_collection_summary( _collection_var )

        with alive_bar( len(collection), title = "Pre-running", dual_line = True ) as bar: 
            for celltype in collection.keys():
                
                # add a markdown title cell
                self.markdown_cell( f"## {celltype} \n\n-----------------" )
                    
                states = collection[ celltype ].groupby( "State" )
                for state, df in states:

                    bar.text = f"Pre-running:\t {state} ({celltype})"
                    self._celltype_res_make_celltype_analysis_cells( celltype, state, df, x, y )
                
                bar()

    def _analyse_by_ecotypes(self, which, collection, _collection_var, x, y):
        """
        Add analysis cells on ecotype resolution where ecotypes and their contributing 
        cell-types / states are included.

        Parameters
        ----------
        which : str
            Which analysis to perform. Either "enrichr" or "prerank".
        collection : EnrichmentCollection
            The collection of enrichment results to analyse.
        _collection_var : str
            The variable name of the collection (enrichr or prerank).
        x : str
            The variable name of the x-axis (for highlight cutoff in the prerun).
        y : str
            The variable name of the y-axis (for highlight cutoff in the prerun).
        """

        self.markdown_cell( f"# Enrichment results for ecotypes ({which})" )
        self._ecotype_res_make_get_celltype_df_cell( _collection_var )
        
        self._make_plotly_collection_summary( _collection_var )
        self._make_matplotlib_collection_summary( _collection_var )

        with alive_bar( len(collection), title = "Pre-running", dual_line = True ) as bar: 
            for ecotype in collection.keys():
                

                # add a markdown title cell
                self.markdown_cell( f"## {ecotype} \n\n-----------------" )
                    
                celltypes = collection[ ecotype ].groupby( "CellType" )
                for celltype, df in celltypes:

                    bar.text = f"Pre-running:\t{celltype} ({ecotype})"
                    self._ecotype_res_make_celltype_analysis_cells( ecotype, celltype, df, x, y )

                bar()

    def _celltype_res_make_celltype_analysis_cells( self, celltype, state, df, x, y ):
        """
        Make the cells for the analysis of the celltype results.
        """
        self.markdown_cell( f"### {state}" )

        # get the subsets to keep for the given state
        subsets = self._generate_subsets_to_keep(df, x, y)

        # make the setup cell
        base_varname = self._make_setup_cell(celltype, state, expand = True )
        
        # make a cell for the categories
        self.markdown_cell( f"Categories to highlight in {celltype} {state}" )
        categories = "categories = " + subsets
        self.code_cell( categories )

        # now make interactive scatterplot cells
        self._make_plotly_scatterplot( base_varname, x, state, celltype )

        # now make static scatterplot cells
        self._make_matplotlib_scatterplot( base_varname, state, celltype )

    
    def _celltype_res_make_get_state_df_cell( self, collection_var ):
        """
        Make a cell that gets the dataframe for a given ecotype and celltype.
        """
        content = """
        
# a function to get cell-type and state specific dataframes from the collection\n
def get_state_df( celltype, state ):
    max_length = 60 # just to make sure the gene names are not too long
    df = __collection_var__[ celltype ].query( f"State == '{state}'" )
    df[ "Genes" ] = df[ "Genes" ].apply( lambda x : x.replace( ";" , " " ) )
    df.loc[ :, "Genes" ] = df[ "Genes" ].apply( lambda x : x[:max_length]+"..." if len(x) > max_length else x )
    return df

""".strip().replace( "__collection_var__", collection_var )

        self.code_cell( content )


    def _ecotype_res_make_get_celltype_df_cell( self, collection_var ):
        """
        Make a cell that gets the dataframe for a given ecotype and celltype.
        """
        content = """
        
# a function to get cell-type specific dataframes from the collection\n
def get_celltype_df( ecotype, celltype ):
    max_length = 60 # just to make sure the gene names are not too long
    df = __collection_var__[ ecotype ].query( f"CellType == '{celltype}'" )
    df[ "Genes" ] = df[ "Genes" ].apply( lambda x : x.replace( ";" , " " ) )
    df.loc[ :, "Genes" ] = df[ "Genes" ].apply( lambda x : x[:max_length]+"..." if len(x) > max_length else x )
    return df

""".strip().replace( "__collection_var__", collection_var )

        self.code_cell( content )

    def _ecotype_res_make_celltype_analysis_cells( self, ecotype, celltype, df, x, y ):
            """
            Make new cells for analysis of cell-type specific 
            """
            self.markdown_cell( f"### {celltype}" )

            # get the subsets to keep for the celltype
            subsets = self._generate_subsets_to_keep(df, x, y)

            # make the setup cell
            base_varname = self._make_setup_cell(ecotype, celltype)

            # make a cell for the categories
            self.markdown_cell( f"Categories to highlight in {celltype}" )
            catecories = "categories = " + subsets
            self.code_cell( catecories )

            # now make interactive scatterplot cells
            self._make_plotly_scatterplot( base_varname, x, celltype, ecotype )
            
            # now make static scatterplot cells
            self._make_matplotlib_scatterplot( base_varname, celltype, ecotype )
        
    def _make_matplotlib_scatterplot( self, base_varname, child = None, parent = None ):
        """
        Make cells to generate a matplotlib / seaborn scatterplot

        Note
        
            These cells are by default commented out to save 
            computation time when running the notebook later.

        Parameters
        ----------
        base_varname : str
            The base variable name of the StateScatterplot object.
        child : str
            The child celltype or state.
        parent : str
            The parent ecotype or celltype.
        """
        self.markdown_cell( f"Static scatterplot" )
        title = f"{parent} {child}" if parent and child else child if child else parent

        # make the cell for the static scatterplot
        content = f"""
# visualise.backend = "matplotlib"
# fig = {base_varname}_scatter.highlight(  
#
#     ref_col = "Term", subsets = categories, 
#     xlabel = xlabel(), ylabel = ylabel(),
#     title = "{title}",
#
# )
# sns.despine()
# plt.savefig( f"__saveto__", bbox_inches = "tight", facecolor = None )
        """.strip().replace( "__saveto__", "{outdir}/" + f"{ title.replace( ' ', '_') }.png" )
        
        self.code_cell( content )

    def _make_plotly_scatterplot( self, base_varname, x, child = None, parent = None ):
        """
        Make cells to generate a plotly scatterplot

        Parameters
        ----------
        base_varname : str
            The base variable name of StateScatterplot object.
        x : str
            The variable name of the x-axis.
        child : str
            The child celltype or state.
        parent : str
            The parent ecotype or celltype.
        """
        self.markdown_cell( f"Interactive scatterplot" )
        title = f"{parent} {child}" if parent and child else child if child else parent

        # add the main cell content
        content = f"""
visualise.backend = "plotly"
fig = {base_varname}_scatter.highlight(  

    ref_col = "Term", subsets = categories, 
    xlabel = xlabel(), ylabel = ylabel(),
    title = "{title}",
    hover_data = __hover__,

)
fig.show()
        """.strip()

        # add hoverdata
        hover = "{ \"" + x + "\" : \"" + x + "\", " + "\"Genes\": \"Genes\" }"
        content = content.replace( "__hover__", hover )

        self.code_cell( content )

        # and add a cell to save the figure 
        self.code_cell( "# fig.write_html( f" + "\"{outdir}/" + f"{ title.replace(' ', '_') }.html\" )" )


    def _make_plotly_collection_summary( self, collection_varname ):
        """
        Make a cell for the plotly collection summary scatterplot figure
        """
        self.markdown_cell( f"Interactive collection summary" )

        # add the main cell content
        content = f"""
visualise.backend = "plotly"
fig = visualise.collection_scatterplot( collection = {collection_varname}, 
                                        x = x, 
                                        y = y, 
                                        hue = hue, 
                                        style = style, 
                                        xlabel = xlabel(),
                                        ylabel = ylabel(),
                                    )

fig.write_html( f"__outdir__/{collection_varname}_summary.html" )
fig.show()
""".strip().replace( "__outdir__", "{outdir}" )

        self.code_cell( content )

    def _make_matplotlib_collection_summary( self, collection_varname ):
        """
        Make a cell for the matplotlib collection summary scatterplot figure
        """
        self.markdown_cell( f"Static collection summary" )

        # add the main cell content
        content = f"""
# visualise.backend = "matplotlib"
# fig = visualise.collection_scatterplot( collection = {collection_varname}, 
#                                         x = x, 
#                                         y = y, 
#                                         hue = hue, 
#                                         style = style,
#                                         xlabel = xlabel(),   
#                                         ylabel = ylabel(),
#                                     )
#
# fig.suptitle( os.path.basename( directory ) )
# sns.despine()
# plt.tight_layout( w_pad = 10 )
#
# plt.savefig( f"__outdir__/{collection_varname}_summary.png" )
""".strip().replace( "__outdir__", "{outdir}" )

        self.code_cell( content )

    def _make_setup_cell(self, parent : str, child : str, expand : bool = False ):
        """
        Makes a setup cell to get a specific celltype's or cellstates dataframe.

        Parameters
        ----------
        parent : str
            The parent of the child, either an ecotype or a celltype.
        child : str
            The child of the parent, either a celltype or a cellstate.
        expand : bool, optional
            If True the name of the created variable will be parent_child, otherwise it will be child only.
        
        Returns
        -------
        var : str
            The variable basename created.
        """
        func = "get_celltype_df" if self._ecotype_resolution else "get_state_df"
        var = f"{parent}_{child.lower()}" if expand else child.lower()

        setup = f"""
{var}_df = {func}( "{parent}", "{child}" )
{var}_scatter = visualise.StateScatterplot( df = {var}_df, x = x, y = y, hue = hue, style = style )
""".strip()
        self.code_cell( setup )

        return var

    def _generate_subsets_to_keep(self, df, x, y, to_string : bool = True, x_ascending : bool = False, y_ascending : bool = True ):
        """
        Performs a pre-run of the enrichment highlighting and excludes all categories that 
        have not enough hit among the top-most enriched terms.

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe to analyse.
        x : str
            The variable name of the x-axis (for highlight cutoff in the prerun).
        y : str
            The variable name of the y-axis (for highlight cutoff in the prerun).
        to_string : bool, optional
            Whether to return the subsets as a string or as the raw dictionary, by default True.
        x_ascending : bool, optional
            Whether to sort the x-axis in ascending order, by default False.
        y_ascending : bool, optional
            Whether to sort the y-axis in ascending order, by default True.

        Returns
        -------
        str or dict
            The subsets to keep as a string or as a dictionary.
        """
        scatter = visualise.StateScatterplot( df = df, x = x, y = y )                 
        scatter._highlight( ref_col = "Term", subsets = self._enrichment_categories )

        # get the topmost df subset
        topmost = scatter.df.sort_values( x, ascending = x_ascending ) 
        topmost = topmost.head( int( len(topmost) * self._topmost ) )
        topmost = scatter.df.sort_values( y, ascending = y_ascending )
        topmost = topmost.head( int( len(topmost) * self._topmost ) )
        category_counts = topmost.loc[ :,"__hue__" ].value_counts()

        # now get the categories to keep for that celltype
        # we drop everything that either has too few counts among the topmost 
        # entries or that don't appear in the topmost entries at all
        to_drop = [ cat for cat in category_counts.index if category_counts[ cat ] < self._cutoff and cat != "other" ]
        to_drop += [ cat for cat in self._enrichment_categories if cat not in category_counts.index ]

        subsets = { key : value for key, value in self._enrichment_categories.items() if key not in to_drop }
        
        if to_string:
            subsets = [ f"\"{key}\" : {value}".replace( "'", "\"" ) for key, value in subsets.items() ]
            subsets = "{\n\t" + ",\n\t".join( subsets ).rstrip() + "\n\t}"

        return subsets

    def _make_prep_cells( self, which : str ):
        """
        Set the preparation cells for the analysis.

        Parameters
        ----------
        which : str
            Which analysis to perform. Either "enrichr" or "prerank".

        Returns
        -------
        collection_var : str
            The name of the collection variable (enrichr or prerank)
        ref_x : str
            The name of the reference column for the x-axis for the highlight cutoff.
        ref_y : str
            The name of the reference column for the y-axis for the highlight cutoff.
        """

        self.markdown_cell( "Prepare some data columns" )

        if which == "enrichr":

            collection, x, y, ref_x, ref_y, mpl_xlabel, mpl_ylabel, plotly_xlabel, plotly_ylabel = self._enrichr_prep_cell_vars()

            # a cell for data prep
            prepcell = f"""

# apply log2 fold change for enrichment score and -log10 for FDR
for i in enrichr.keys():
    enrichr[ i ][ "{x}" ] = np.log2( enrichr[ i ][ "{ref_x}" ] ) 
    enrichr[ i ][ "{y}" ] = -np.log10( enrichr[ i ][ "{ref_y}" ] )

""".strip()

        elif which == "prerank":

            collection, x, y, ref_x, ref_y, mpl_xlabel, mpl_ylabel, plotly_xlabel, plotly_ylabel = self._prerank_prep_cell_vars()
            
            # a cell for data prep
            prepcell = f"""

# split the Term column into GeneSet and Term
prerank.split_terms()

# apply -log10 for FDR
for i in prerank.keys():
    prerank[ i ][ "{y}" ] = -np.log10( prerank[ i ][ {ref_y} ] )

""".strip()

        self.code_cell( prepcell )

        self._make_default_plotting_params(x, y, mpl_xlabel, mpl_ylabel, plotly_xlabel, plotly_ylabel)

        return collection, ref_x, ref_y

    def _make_default_plotting_params(self, x, y, mpl_xlabel, mpl_ylabel, plotly_xlabel, plotly_ylabel):
        """
        Makes a cell for the default plotting parameters of StateScatterplots
        """
        # and add a cell for default plotting parameters
        self.markdown_cell( "Set default plotting parameters" )

        # first the main parameters
        code_defaults = f"""
x = "{x}"
y = "{y}"
hue = "CellType"
style = None
        """.strip() 

        # then the axis labels
        code_defaults += """
xlabels = {  "matplotlib" : "__mplxlabel__", 
             "plotly" : "__plotlyxlabel__" }
ylabels = {  "matplotlib" : "__mplylabel__", 
             "plotly" : "__plotlyylabel__" }

# automatically get the right labels for the respective backends
xlabel = lambda : xlabels[ visualise.backend ]
ylabel = lambda : ylabels[ visualise.backend ]
        """.rstrip() \
        .replace( "__mplxlabel__", mpl_xlabel ) \
        .replace( "__mplylabel__", mpl_ylabel ) \
        .replace( "__plotlyxlabel__", plotly_xlabel ) \
        .replace( "__plotlyylabel__", plotly_ylabel )

        self.code_cell( code_defaults )

    def _enrichr_prep_cell_vars( self ):
        """
        The setup variables to use for enrichr results.
        """
        collection = "enrichr" 

        x = "log2_score"
        ref_x = "Combined Score"

        y = "log10_qval"
        ref_y = "Adjusted P-value"

        mpl_xlabel = "$log_2$ Combined Score"
        mpl_ylabel = "$-log_{10}$ q-value"
        plotly_xlabel = "log_2 Combined Score"
        plotly_ylabel = "-log_10 q-value"

        return collection, x, y, ref_x, ref_y, mpl_xlabel, mpl_ylabel, plotly_xlabel, plotly_ylabel

    def _prerank_prep_cell_vars( self ):
        """
        The setup variables to use for prerank results.
        """
        collection = "prerank"

        x = "NES"
        ref_x = "NES"

        y = "log10_FDR_pval"
        ref_y = "FDR q-val"

        mpl_xlabel = "Normalized Enrichment Score"
        mpl_ylabel = "$-log_{10}$ FDR p-value"
        plotly_xlabel = "Normalized Enrichment Score"
        plotly_ylabel = "-log_10 FDR p-value"


        return collection, x, y, ref_x, ref_y, mpl_xlabel, mpl_ylabel, plotly_xlabel, plotly_ylabel


    @property
    def data_dir( self ):
        """
        Get the data directory storing the results of the enrichment analysis.
        """
        user = os.environ.get("USER")
        parent = self._parent.format( user = user )
        results = self._results_dir.format( parent = parent, user = user )
        enrichment_dir = self._enrichment_dir.format( parent = parent, user = user, results = results )
        enrichment_dir = f"{ enrichment_dir }/{ self._ecotyper_dir.split('/')[1] }"
        return enrichment_dir

    @property
    def cells( self ):
        return self._notebook.cells

    def __getitem__( self, key ):
        return self._notebook.cells[key]
    
    def __setitem__( self, key, value ):
        self._notebook.cells[key] = value